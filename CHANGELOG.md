# Changelog

## SteelTemple Welcome Tour 0.1.0 — Early Release

Initial public release of **SteelTemple Welcome Tour**, bringing *Nintendo Switch 2 Welcome Tour* (`1.0.4`) natively to Windows PC with a dedicated Setup Wizard, **WelcomeTourLauncher**, Switch 2 Expo `F1` menu, Vulkan 1.3 renderer, locked 60 FPS at 1080p / 1440p / 4K, and clean hardware-agnostic default settings.

> **Early Release Notice:** The game is booting, rendering, and running smoothly at 60 FPS across 1080p, 1440p, and native 4K, but as an early `0.1.0` release there may still be exhibit edge cases or performance variations across different GPU/CPU setups.

■ Highlights

- **Native Windows PC Recompilation (`welcometour.exe`):** Ahead-of-time ARM64-to-C lifting and local LLVM/Ninja compilation across all **43 modules** (7 static NSOs `main`, `subsdk0`–`subsdk4`, `sdk` + 36 dynamic RomFS `.nro` modules, `245,670` functions total) with C++ exception unwinding across lifted code and Switch 2 load-order symbol resolution.
- **Switch 2 Expo Setup Wizard & WelcomeTourLauncher:** Self-contained Windows installer (`SteelTemple-WelcomeTour-0.1.0-Full-Setup-Wizard.exe`) and portable archive with bundled Python 3.14, LLVM-MinGW, Ninja, and `ns2_xlate`. Supports both `.nup` containers (combined or split base + update) and direct `ExeFS`/`RomFS` dump folders, with `9/9` ExeFS SHA-256 verification, automatic 36-NRO extraction, shader pre-warming, save backup vault, and built-in GitHub release auto-updates.
- **Locked 60 FPS at 1080p, 1440p & Native 4K (`2160p`):** Live internal resolution scaling hooks preserving Welcome Tour's exact viewport crops, async Vulkan command replay, and dirty-band `R8` font/UI atlas uploads (cutting glyph re-upload time from `26.85 ms` down to `<0.3 ms`).
- **Flicker-Free Vulkan 1.3 Renderer & SM86 Shader Lowering:** Full Ampere (`SM86`) shader lowering including `RED.E`, `TLD.SCR.LZ.MS`, and `TLD4.SCR.F16`; private GPU-only color render target allocation fixing NVN pool overflows; `R32_UINT` zero-clear support; 2D-array cubemap IBL views; cumulative occlusion query counting; and `D32_SFLOAT` shadow sampler fallbacks (`0` Vulkan validation errors, `0` shader failures).
- **Verified 14-Language Locale Safety & Switch 2 Expo `F1` Menu:** Custom Switch 2 Expo `F1` overlay (plus Light and Dark themes) and Launcher Game Language selector (`auto` + all 14 verified languages). Automatically normalizes `pt` -> `pt-BR` and safely maps unsupported OS locales (such as `ru-RU`, where the game ships only an empty stub archive) to `en-US`.
- **Clean Zero-Config Default Profile:** Starts cleanly at `1920x1080` Windowed, Original internal resolution, AMD FSR, `16x` Aniso, Frame Generation Off, and `60 FPS` limit with no personal `.ini` settings bundled.

■ Known Issues (Early Release)

- As an early `0.1.0` release, some console-specific hardware exhibits or untested minigames may behave unexpectedly across different controller and GPU configurations.
- First-time traversal into new exhibits can cause brief shader translation stutters before the local shader cache warms up.
- Online features are not supported.

■ Install & Update

- **New install:** Run `SteelTemple-WelcomeTour-0.1.0-Full-Setup-Wizard.exe`, open **WelcomeTourLauncher** → **SETUP FROM DUMP**, select your *Nintendo Switch 2 Welcome Tour* `1.0.4` `.nup` container or `ExeFS`/`RomFS` folders, click **VERIFY & BUILD WELCOMETOUR.EXE**, and press **PLAY WELCOME TOUR PC**.
- **Portable:** Extract `SteelTemple-WelcomeTour-0.1.0-Portable-StandAlone.zip` anywhere and launch `WelcomeTourLauncher.exe`.
- **Update:** Future updates apply cleanly via **WelcomeTourLauncher**'s built-in updater or `Update.zip` without touching your dump, saves, or `welcometour.ini`.
