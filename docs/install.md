# Install

Bosar installs like any other program; nothing else is needed — Python, the numerical stack,
GDAL / PROJ, the SNAPHU unwrapper and the licence texts are inside the installer.

## Windows 10 / 11 (x64)

1. Download `bosar-<version>-win-x64-setup.exe` from
   [Releases](https://github.com/HU-Jiashu/bosar/releases).
2. Run it. The installer is per-user (no administrator rights; it installs under
   `Programs\Bosar` in your local application-data folder). Tick **Add the bosar command line to the user PATH** to
   type `bosar` in any terminal; tick **Open project.json files with Bosar** if you like.
3. Open a new terminal (the PATH takes effect in new windows) and check:

```text
bosar version                  # the version and the build id
bosar preflight --offline      # the environment table; the SNAPHU row says "no CS2 solver (MST init)"
```

Windows SmartScreen may show "Windows protected your PC" on the first run of an unsigned
installer: *More info* → *Run anyway*. The `.zip` next to the installer is the same folder
without an installer (unpack anywhere; `bosar.exe` and `bosar-gui.exe` are at its top).

## macOS 12+ (Apple silicon and Intel)

1. Download `bosar-<version>-mac-arm64.dmg` (Apple silicon) or `bosar-<version>-mac-x64.dmg`
   (Intel) from [Releases](https://github.com/HU-Jiashu/bosar/releases).
2. Open the image and drag **Bosar.app** to *Applications*.
3. The application is not signed with an Apple developer certificate. On the first start macOS
   says it cannot verify the developer: **right-click (or control-click) Bosar.app → Open**, and
   confirm once. Or, in a terminal:

```text
xattr -dr com.apple.quarantine /Applications/Bosar.app
```

4. The command line lives inside the bundle:

```text
/Applications/Bosar.app/Contents/MacOS/bosar version
```

   Add that folder to your PATH, or make an alias. Apple-silicon Macs have no CUDA; Bosar
   runs on the CPU there.

## First steps on an installed build

```text
bosar demo my_demo             # a synthetic pair through the whole DInSAR chain (about a minute)
bosar-gui my_demo/project      # the desktop application on that project (or open it from the Start menu / Applications)
```

`bosar demo` writes a small synthetic stack, creates a project, imports it and runs one pair
through multilooking, coherence, filtering, unwrapping, geocoding and displacement — the proof
that the installation works, with no data and no network. From there the
[walkthrough](WALKTHROUGH.md) ([中文](WALKTHROUGH_zh.md)) continues with real data.

## The GPU (NVIDIA, CUDA 12)

The installers run on NumPy. A machine with an NVIDIA GPU adds the GPU afterwards:

```text
bosar gpu install              # CuPy and the CUDA 12 runtime from PyPI into the plug-in folder (about 1.5 GB)
bosar gpu install --no-ctk     # CuPy only, when a CUDA 12 toolkit is installed system-wide
bosar preflight --offline      # the GPU row shows the device; the plug-in row says "ok"
bosar gpu status / remove
```

No pip is needed: Bosar resolves the wheels itself, checks their SHA-256 and unpacks them under
your user data folder. `BOSAR_FORCE_CPU=1` runs on the CPU even with the plug-in present.

## Where things live

| What | Where |
|---|---|
| Settings | an INI file under your user config folder (shown at the bottom of the Settings page) |
| Credentials (Earthdata, Copernicus, OpenTopography, CDS) | the operating system's credential store; Bosar never shows, logs or copies them |
| Projects | wherever you create them (`bosar project new <folder>`) — products, logs and `project.json` inside |
| The GPU plug-in | `<user data folder>/bosar/plugins/cupy` |
| Licence texts | `_internal/licenses/` inside the installation; the About card of the Settings page |

## Uninstall

Windows: *Settings → Apps → Bosar → Uninstall* (or the Start-menu entry). macOS: drag
`Bosar.app` to the bin. Projects, settings and the GPU plug-in are left in place; delete them
yourself if you no longer need them.
