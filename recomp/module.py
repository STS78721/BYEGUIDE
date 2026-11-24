"""One loaded NSO module as the generator and its analyses see it: image at a guest base, .text as words,
function seeds, and bounded-cache instruction lifting.

The function seeds and the .eh_frame_hdr reader are adapted from LAS Recomp tools/analyze.py and tools/gen.py
@ da35b83 (MIT, Copyright (c) 2026 Peiikai).
"""
import struct
from collections import OrderedDict

import numpy as np

from lifter import Insn, Lifter, Unsupported, hx
from nso import Nso, R_AARCH64_RELATIVE

LIFT_CACHE = 1 << 16  # lifted instructions kept per module; analyses revisit nearby addresses only


def _uleb(img, off):
    v = s = 0
    while True:
        b = img[off]; off += 1
        v |= (b & 0x7F) << s
        if not (b & 0x80):
            return v, off
        s += 7


def _sleb(img, off):
    v = s = 0
    while True:
        b = img[off]; off += 1
        v |= (b & 0x7F) << s
        s += 7
        if not (b & 0x80):
            if b & 0x40:
                v -= 1 << s
            return v, off


def _read_encoded_ex(img, off, enc, pc_base):
    if enc == 0xFF:
        return 0, off
    fmt, app = enc & 0x0F, enc & 0x70
    start = off
    if fmt == 0x01:
        v, off = _uleb(img, off)
    elif fmt == 0x09:
        v, off = _sleb(img, off)
    elif fmt == 0x02:
        v = struct.unpack_from('<H', img, off)[0]; off += 2
    elif fmt == 0x03:
        v = struct.unpack_from('<I', img, off)[0]; off += 4
    elif fmt in (0x00, 0x04):
        v = struct.unpack_from('<Q', img, off)[0]; off += 8
    elif fmt == 0x0A:
        v = struct.unpack_from('<h', img, off)[0]; off += 2
    elif fmt == 0x0B:
        v = struct.unpack_from('<i', img, off)[0]; off += 4
    elif fmt == 0x0C:
        v = struct.unpack_from('<q', img, off)[0]; off += 8
    else:
        raise ValueError(f'unsupported pointer encoding {enc:#x}')
    if v != 0:
        if app == 0x10:
            v += start
        elif app == 0x30:
            v += pc_base
    return v, off


def _read_encoded(img, off, enc, pc_base):
    fmt, app = enc & 0x0F, enc & 0x70
    if fmt == 0x0B:  # sdata4
        v, size = struct.unpack_from('<i', img, off)[0], 4
    elif fmt == 0x03:  # udata4
        v, size = struct.unpack_from('<I', img, off)[0], 4
    elif fmt in (0x0C, 0x04):  # sdata8, udata8
        v, size = struct.unpack_from('<q' if fmt == 0x0C else '<Q', img, off)[0], 8
    else:
        raise ValueError(f'unsupported pointer encoding {enc:#x}')
    if app == 0x10:  # pcrel
        v += off
    elif app == 0x30:  # datarel
        v += pc_base
    return v, size


class Module:
    def __init__(self, name, path, base, simd='c', image_patches=()):
        """image_patches: [(module offset, bytes)] the enabled code mods write into the image before it is read
        (patches.load_image, gen.py --image)."""
        self.name = name
        self.nso = Nso(str(path))
        self.base = base
        n = self.nso
        img = bytearray(n.image)
        for off, data in image_patches:
            img[off:off + len(data)] = data
        self.image = bytes(img)
        self.lo = base + n.text[0]
        self.hi = self.lo + n.text[1]
        self.words = np.frombuffer(self.image, dtype='<u4', count=n.text[1] // 4, offset=n.text[0])
        self.lifter = Lifter(base, simd)
        self._cache = OrderedDict()

    # ---- memory

    def in_text(self, a):
        return self.lo <= a < self.hi and a % 4 == 0

    def in_image(self, a, n=1):
        return self.base <= a and a + n <= self.base + len(self.image)

    def word(self, a):
        return int(self.words[(a - self.lo) >> 2])

    def read(self, a, n, signed=False):
        """Little-endian integer of n bytes at guest address a (unrelocated image)."""
        o = a - self.base
        return int.from_bytes(self.image[o:o + n], 'little', signed=signed)

    # ---- lifting

    def lift(self, a):
        """Lifted instruction at a; Unsupported becomes an rt_udf trap."""
        ins = self._cache.get(a)
        if ins is not None:
            self._cache.move_to_end(a)
            return ins
        try:
            ins = self.lifter.lift(self.word(a), a)
        except Unsupported as e:
            ins = Insn('trap', f'rt_udf(c, {hx(a)}); /* {e} */')
        self._cache[a] = ins
        if len(self._cache) > LIFT_CACHE:
            self._cache.popitem(last=False)
        return ins

    # ---- function seeds

    def eh_frame_functions(self):
        """Function starts from .eh_frame_hdr's binary search table (absolute addresses)."""
        img, hdr = self.image, self.nso.eh_start
        if not hdr or hdr >= len(img):
            return []
        _, ptr_enc, cnt_enc, tbl_enc = img[hdr:hdr + 4]
        off = hdr + 4
        _, sz = _read_encoded(img, off, ptr_enc, hdr)
        off += sz
        count, sz = _read_encoded(img, off, cnt_enc, hdr)
        off += sz
        starts = []
        for _ in range(count):
            loc, sz = _read_encoded(img, off, tbl_enc, hdr)
            off += sz
            _, sz = _read_encoded(img, off, tbl_enc, hdr)
            off += sz
            starts.append(self.base + loc)
        return starts

    def eh_landing_pads(self):
        """All C++ exception landing-pad addresses (absolute) from .eh_frame_hdr -> FDE -> GCC LSDA."""
        img, hdr = self.image, self.nso.eh_start
        if not hdr or hdr >= len(img):
            return []
        _, ptr_enc, cnt_enc, tbl_enc = img[hdr:hdr + 4]
        off = hdr + 4
        _, off = _read_encoded_ex(img, off, ptr_enc, hdr)
        count, off = _read_encoded_ex(img, off, cnt_enc, hdr)
        cies = {}
        lps = set()
        for _ in range(count):
            _, off = _read_encoded_ex(img, off, tbl_enc, hdr)
            fde_off, off = _read_encoded_ex(img, off, tbl_enc, hdr)
            if fde_off <= 0 or fde_off + 8 > len(img):
                continue
            length = struct.unpack_from('<I', img, fde_off)[0]
            if length == 0:
                continue
            cie_ptr_pos = fde_off + 4
            cie_delta = struct.unpack_from('<I', img, cie_ptr_pos)[0]
            cie_off = cie_ptr_pos - cie_delta
            if cie_off not in cies:
                co = cie_off + 8
                co += 1  # version
                aug_end = img.index(0, co)
                aug = img[co:aug_end].decode('ascii', 'ignore')
                co = aug_end + 1
                _, co = _uleb(img, co)
                _, co = _sleb(img, co)
                _, co = _uleb(img, co)
                fde_enc, lsda_enc = 0, 0xFF
                if aug.startswith('z'):
                    _, co = _uleb(img, co)
                    for ch in aug[1:]:
                        if ch == 'R':
                            fde_enc = img[co]; co += 1
                        elif ch == 'L':
                            lsda_enc = img[co]; co += 1
                        elif ch == 'P':
                            pe = img[co]; co += 1
                            _, co = _read_encoded_ex(img, co, pe, hdr)
                cies[cie_off] = (aug, fde_enc, lsda_enc)
            aug, fde_enc, lsda_enc = cies[cie_off]
            if lsda_enc == 0xFF or not aug.startswith('z'):
                continue
            fo = fde_off + 8
            pc_begin, fo = _read_encoded_ex(img, fo, fde_enc, hdr)
            _, fo = _read_encoded_ex(img, fo, fde_enc & 0x0F, hdr)
            aug_len, fo = _uleb(img, fo)
            if aug_len == 0:
                continue
            lsda_off, _ = _read_encoded_ex(img, fo, lsda_enc, hdr)
            if lsda_off <= 0 or lsda_off >= len(img):
                continue
            lo = lsda_off
            lpstart_enc = img[lo]; lo += 1
            lpstart = pc_begin
            if lpstart_enc != 0xFF:
                lpstart, lo = _read_encoded_ex(img, lo, lpstart_enc, hdr)
            ttype_enc = img[lo]; lo += 1
            if ttype_enc != 0xFF:
                _, lo = _uleb(img, lo)
            cs_enc = img[lo]; lo += 1
            cs_len, lo = _uleb(img, lo)
            cs_end = lo + cs_len
            while lo < cs_end:
                _, lo = _read_encoded_ex(img, lo, cs_enc & 0x0F, hdr)
                _, lo = _read_encoded_ex(img, lo, cs_enc & 0x0F, hdr)
                lp, lo = _read_encoded_ex(img, lo, cs_enc & 0x0F, hdr)
                _, lo = _uleb(img, lo)
                if lp != 0:
                    addr = self.base + lpstart + lp
                    if self.in_text(addr):
                        lps.add(addr)
        return sorted(lps)

    def seeds(self):
        """Known function starts: .eh_frame_hdr, exported FUNC symbols, R_AARCH64_RELATIVE targets in .text."""
        starts = set(self.eh_frame_functions())
        for _, info, shndx, value, _ in self.nso.syms:
            if shndx and (info & 0xF) == 2:
                starts.add(self.base + value)
        for _, typ, _, add in self.nso.relocs:
            if typ == R_AARCH64_RELATIVE:
                starts.add(self.base + add)
        return sorted(a for a in starts if self.in_text(a))
