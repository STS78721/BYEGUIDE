"""Generate original Switch 2 Expo themed icon & emblem assets for Nintendo Switch 2 Welcome Tour PC.

100% procedural vector artwork (zero copyrighted game assets).
Writes:
  - runtime/welcometour.png              (512x512 rounded tile icon)
  - runtime/welcometour_emblem.png       (512x512 floating transparent emblem)
  - runtime/welcometour.ico              (multi-size Windows icon)
  - launcher/assets/welcometour.png
  - launcher/assets/welcometour_emblem.png
  - launcher/assets/welcometour.ico
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_rgb(c0, c1, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c0, c1))


def add_radial_glow(canvas, cx, cy, radius, rgb, max_alpha):
    w, h = canvas.size
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    steps = 28
    for i in range(steps, 0, -1):
        frac = i / steps
        r = radius * frac
        a = int(max_alpha * ((1.0 - frac) ** 1.7) * 0.16)
        if a <= 0:
            continue
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*rgb, a))
    canvas.alpha_composite(glow)


def draw_star4(draw, cx, cy, rx, ry, inner, fill):
    pts = [
        (cx, cy - ry), (cx + inner, cy - inner),
        (cx + rx, cy), (cx + inner, cy + inner),
        (cx, cy + ry), (cx - inner, cy + inner),
        (cx - rx, cy), (cx - inner, cy - inner),
    ]
    draw.polygon(pts, fill=fill)


def draw_expo_console(canvas, S, scale=1.0, cy_offset=0.0):
    """Draw the Switch 2 Expo matte console + glowing cyan/coral magnetic rails + Expo compass."""
    cx = S * 0.50
    cy = S * (0.50 + cy_offset)

    # Ambient cyan (left) and coral-red (right) Expo hall glow
    add_radial_glow(canvas, cx - S * 0.20 * scale, cy, S * 0.34 * scale, (0, 208, 248), 210)
    add_radial_glow(canvas, cx + S * 0.20 * scale, cy, S * 0.34 * scale, (255, 76, 70), 205)

    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    total_w = S * 0.78 * scale
    body_h = S * 0.44 * scale
    grip_w = S * 0.165 * scale
    rail_gap = S * 0.022 * scale
    outer_r = S * 0.105 * scale

    x_left = cx - total_w * 0.5
    x_right = cx + total_w * 0.5
    y_top = cy - body_h * 0.5
    y_bot = cy + body_h * 0.5

    # Soft drop shadow under console
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle(
        (x_left + S * 0.008, y_top + S * 0.028, x_right + S * 0.008, y_bot + S * 0.036),
        radius=outer_r, fill=(4, 7, 14, 155),
    )
    sh = sh.filter(ImageFilter.GaussianBlur(radius=S * 0.024))
    canvas.alpha_composite(sh)

    # ---- Left magnetic Joy-Con 2 grip (matte graphite + glowing Cyan magnetic rail) ----
    lx0, lx1 = x_left, x_left + grip_w
    d.rounded_rectangle(
        (lx0, y_top, lx1 + outer_r * 0.5, y_bot),
        radius=outer_r, fill=(36, 44, 62, 255),
    )
    # Trim right overlap to crisp vertical edge
    d.rectangle((lx1, y_top - 4, lx1 + outer_r, y_bot + 4), fill=(0, 0, 0, 0))
    # Glowing Cyan inner magnetic rail bar
    rail_w = S * 0.026 * scale
    d.rounded_rectangle(
        (lx1 - rail_w, y_top + body_h * 0.10, lx1, y_bot - body_h * 0.10),
        radius=rail_w * 0.45, fill=(0, 214, 255, 255),
    )
    # Cyan thumbstick ring + subtle directional dots
    st_x = lx0 + grip_w * 0.46
    st_y = cy - body_h * 0.17
    st_r = S * 0.042 * scale
    d.ellipse((st_x - st_r, st_y - st_r, st_x + st_r, st_y + st_r),
              fill=(20, 26, 38, 255), outline=(0, 214, 255, 245), width=max(2, int(S * 0.009 * scale)))
    # Lower 4 directional micro-dots
    dp_y = cy + body_h * 0.19
    dp_off = S * 0.024 * scale
    dp_r = S * 0.010 * scale
    for dx, dy in ((0, -dp_off), (0, dp_off), (-dp_off, 0), (dp_off, 0)):
        d.ellipse((st_x + dx - dp_r, dp_y + dy - dp_r, st_x + dx + dp_r, dp_y + dy + dp_r),
                  fill=(165, 198, 224, 215))

    # ---- Right magnetic Joy-Con 2 grip (matte graphite + glowing Coral-Red magnetic rail) ----
    rx0, rx1 = x_right - grip_w, x_right
    d.rounded_rectangle(
        (rx0 - outer_r * 0.5, y_top, rx1, y_bot),
        radius=outer_r, fill=(36, 44, 62, 255),
    )
    d.rectangle((rx0 - outer_r, y_top - 4, rx0, y_bot + 4), fill=(0, 0, 0, 0))
    # Glowing Coral-Red inner magnetic rail bar
    d.rounded_rectangle(
        (rx0, y_top + body_h * 0.10, rx0 + rail_w, y_bot - body_h * 0.10),
        radius=rail_w * 0.45, fill=(255, 84, 78, 255),
    )
    # Upper 4 face button micro-dots
    rs_x = rx0 + grip_w * 0.54
    fb_y = cy - body_h * 0.19
    for dx, dy in ((0, -dp_off), (0, dp_off), (-dp_off, 0), (dp_off, 0)):
        d.ellipse((rs_x + dx - dp_r, fb_y + dy - dp_r, rs_x + dx + dp_r, fb_y + dy + dp_r),
                  fill=(235, 186, 184, 215))
    # Coral-Red right thumbstick ring
    rs_y = cy + body_h * 0.17
    d.ellipse((rs_x - st_r, rs_y - st_r, rs_x + st_r, rs_y + st_r),
              fill=(20, 26, 38, 255), outline=(255, 84, 78, 245), width=max(2, int(S * 0.009 * scale)))

    # Crisp rim accents on left & right grips
    d.arc((lx0, y_top, lx0 + outer_r * 2, y_top + outer_r * 2), 180, 270,
          fill=(0, 214, 255, 220), width=max(2, int(S * 0.008 * scale)))
    d.arc((lx0, y_bot - outer_r * 2, lx0 + outer_r * 2, y_bot), 90, 180,
          fill=(0, 214, 255, 220), width=max(2, int(S * 0.008 * scale)))
    d.arc((rx1 - outer_r * 2, y_top, rx1, y_top + outer_r * 2), 270, 360,
          fill=(255, 84, 78, 220), width=max(2, int(S * 0.008 * scale)))
    d.arc((rx1 - outer_r * 2, y_bot - outer_r * 2, rx1, y_bot), 0, 90,
          fill=(255, 84, 78, 220), width=max(2, int(S * 0.008 * scale)))

    # ---- Center matte glass display chassis ----
    sx0, sx1 = lx1 + rail_gap, rx0 - rail_gap
    scr_r = S * 0.032 * scale
    d.rounded_rectangle(
        (sx0, y_top, sx1, y_bot),
        radius=scr_r, fill=(14, 19, 30, 255),
        outline=(110, 132, 168, 230), width=max(2, int(S * 0.008 * scale)),
    )
    # Inner illuminated glass viewport
    pad = S * 0.022 * scale
    vx0, vy0, vx1, vy1 = sx0 + pad, y_top + pad, sx1 - pad, y_bot - pad
    d.rounded_rectangle((vx0, vy0, vx1, vy1), radius=scr_r * 0.65, fill=(20, 28, 44, 255))

    # Expo architectural floor grid inside viewport
    grid_col = (74, 108, 152, 68)
    vw, vh = vx1 - vx0, vy1 - vy0
    for k in range(1, 5):
        gy = vy0 + vh * (k / 5.0)
        d.line((vx0 + 6, gy, vx1 - 6, gy), fill=grid_col, width=max(1, int(S * 0.0025)))
    for k in range(1, 6):
        gx = vx0 + vw * (k / 6.0)
        d.line((gx, vy0 + 6, gx, vy1 - 6), fill=grid_col, width=max(1, int(S * 0.0025)))

    # Dual Cyan -> White -> Coral light strip along bottom of screen
    bar_y = vy1 - vh * 0.14
    mid_x = (vx0 + vx1) * 0.5
    bar_half = vw * 0.38
    bar_h = S * 0.011 * scale
    d.rounded_rectangle((mid_x - bar_half, bar_y, mid_x - S * 0.006, bar_y + bar_h),
                        radius=bar_h * 0.5, fill=(0, 214, 255, 240))
    d.rounded_rectangle((mid_x + S * 0.006, bar_y, mid_x + bar_half, bar_y + bar_h),
                        radius=bar_h * 0.5, fill=(255, 84, 78, 240))

    # Central Expo Showcase Compass Ring + Luminous 4-Point Star
    ccy = cy - vh * 0.04
    ring_r = min(vw, vh) * 0.30
    ring_w = max(2, int(S * 0.011 * scale))
    d.arc((cx - ring_r, ccy - ring_r, cx + ring_r, ccy + ring_r), 125, 305,
          fill=(0, 218, 255, 240), width=ring_w)
    d.arc((cx - ring_r, ccy - ring_r, cx + ring_r, ccy + ring_r), 305, 485,
          fill=(255, 92, 86, 240), width=ring_w)

    # Outer dashed blueprint arc
    orad = ring_r * 1.32
    ow = max(1, int(S * 0.005 * scale))
    for deg in range(0, 360, 45):
        d.arc((cx - orad, ccy - orad, cx + orad, ccy + orad), deg + 8, deg + 32,
              fill=(190, 216, 246, 120), width=ow)

    # Luminous Expo Star centerpiece
    sr = ring_r * 0.72
    draw_star4(d, cx, ccy, sr, sr, sr * 0.28, (250, 252, 255, 255))
    draw_star4(d, cx, ccy, sr * 0.44, sr * 0.44, sr * 0.14, (190, 238, 255, 255))

    # Subtle diagonal glass sheen across viewport
    sheen = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd2 = ImageDraw.Draw(sheen)
    sd2.polygon(
        [(vx0, vy0), (vx0 + vw * 0.52, vy0), (vx0 + vw * 0.24, vy1), (vx0, vy1)],
        fill=(255, 255, 255, 16),
    )
    layer.alpha_composite(sheen)

    # Blueprint corner reticles above/below console
    ret_col = (144, 178, 216, 145)
    ret_w = max(2, int(S * 0.007 * scale))
    rx_off = total_w * 0.46
    ry_off = body_h * 0.62
    rl = S * 0.042 * scale
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px = cx + sx * rx_off
        py = cy + sy * ry_off
        d.line((px, py, px - sx * rl, py), fill=ret_col, width=ret_w)
        d.line((px, py, px, py - sy * rl), fill=ret_col, width=ret_w)

    canvas.alpha_composite(layer)


def make_tile(out_size=512):
    S = out_size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # Rounded squircle matte graphite tile background with vertical studio gradient
    margin = int(S * 0.045)
    radius = int(S * 0.205)
    bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bg)
    top_col = (29, 36, 52)
    bot_col = (14, 18, 28)
    for y in range(margin, S - margin):
        t = (y - margin) / max(1, (S - 2 * margin - 1))
        c = lerp_rgb(top_col, bot_col, t)
        bd.line((margin, y, S - margin, y), fill=(*c, 255))

    # Subtle architectural Expo dot pattern composited with true alpha
    dots = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    dot_step = int(S * 0.065)
    for y in range(margin + dot_step, S - margin, dot_step):
        for x in range(margin + dot_step, S - margin, dot_step):
            r = max(2, int(S * 0.0028))
            dd.ellipse((x - r, y - r, x + r, y + r), fill=(140, 170, 212, 42))
    bg.alpha_composite(dots)

    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((margin, margin, S - margin, S - margin), radius=radius, fill=255)
    img.paste(bg, (0, 0), mask)

    # Top & bottom cyan/coral subtle Expo stage edge glows clipped to tile
    stage = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    add_radial_glow(stage, S * 0.22, S * 0.18, S * 0.44, (0, 200, 240), 120)
    add_radial_glow(stage, S * 0.78, S * 0.82, S * 0.44, (255, 76, 72), 120)
    stage_clipped = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    stage_clipped.paste(stage, (0, 0), mask)
    img.alpha_composite(stage_clipped)

    # Draw centerpiece console
    draw_expo_console(img, S, scale=1.02, cy_offset=0.0)

    # Crisp metallic tile border
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rounded_rectangle(
        (margin, margin, S - margin, S - margin),
        radius=radius, outline=(96, 118, 154, 210), width=max(4, int(S * 0.010)),
    )
    img.alpha_composite(rim)

    return img.resize((out_size, out_size), Image.Resampling.LANCZOS)


def make_emblem(out_size=512):
    S = out_size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw_expo_console(img, S, scale=1.18, cy_offset=0.0)
    return img.resize((out_size, out_size), Image.Resampling.LANCZOS)


def main():
    tile = make_tile(512)
    emblem = make_emblem(512)

    rt = ROOT / "runtime"
    la = ROOT / "launcher" / "assets"
    la.mkdir(parents=True, exist_ok=True)

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    for folder in (rt, la):
        tile.save(folder / "welcometour.png")
        emblem.save(folder / "welcometour_emblem.png")
        tile.save(folder / "welcometour.ico", format="ICO", sizes=ico_sizes)
        print("Wrote", folder / "welcometour.{png,ico}", "and welcometour_emblem.png")


if __name__ == "__main__":
    main()
