# Install

Bosar installs like any other program; nothing else is needed — Python, the numerical stack,
GDAL / PROJ, the SNAPHU unwrapper and the licence texts are inside the installer.

## What the machine needs

Bosar runs on an ordinary workstation; what you plan to process decides how much of it you
need. The figures below are what the chains used on real data (peak resident memory of the
run, measured by the program itself and written to its log), rounded up.

| | Minimum | Recommended |
|---|---|---|
| Operating system | Windows 10 / 11 x64, macOS 12 on Apple silicon (M1 and later; no Intel build) | Windows 11, macOS 14 |
| CPU | 4 cores | 8-16 cores (the SBAS and PS / DS chains run one pair per worker process, `--workers`) |
| RAM | 16 GB | 32 GB for crops and pairs; 64 GB for a full-sub-swath Sentinel-1 time series or when SNAP runs beside Bosar |
| Disk | 20 GB free for the demo and one Sentinel-1 pair (the download guard of `fetch slc` defaults to 150 GB free; lower it with `--min-free-gb`) | an SSD with 300-500 GB free for a series (raw scenes 4-8 GB each, the stack about the same again) |
| GPU | none (every chain runs on NumPy) | NVIDIA with 8 GB or more, CUDA 12 driver, `bosar gpu install` (the linking and coregistration kernels measured 18-65 x faster; unwrapping stays on the CPU) |
| Network | only to fetch data (scenes, orbits, the DEM, weather and ionosphere models) and the GPU plug-in; nothing phones home | |

What this means in practice:

- A **two-scene DInSAR pair** of Sentinel-1 (one sub-swath, a city-sized crop) needs about
  2 GB of memory and runs in minutes on the CPU.
- A **Sentinel-1 time series** (tens of dates, a full sub-swath) peaks at 30-45 GB of memory
  in the inversion and takes hours on the CPU; the GPU takes the linking and the inversion
  down to minutes, the unwrapping stays on the CPU (an hour or more for a full sub-swath).
  Keep `storage_mode: minimal` (the default) so that intermediate products are deleted as
  the chain goes, or budget two to three times the raw data for `full`.
- **Stripmap stacks** (ALOS, ASAR, ERS, NISAR crops of 10-20 km) stay under 4 GB of memory
  and run on a laptop (the measured peaks are being collected; the figure is an upper bound
  from the stack sizes).
- **SNAP** (optional, for the SNAP bridge) takes whatever Java heap it is given; Bosar gives
  it half the RAM (at most 64 GB), so 64 GB machines are comfortable there, 16 GB machines
  are not.
- Free disk: a download that would breach the free-space guard is refused (`fetch slc
  --min-free-gb`); a run warns in its pre-flight table when the project drive is under
  10 GiB.

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

## macOS 12+ (Apple silicon)

1. Download `bosar-<version>-mac-arm64.dmg` from
   [Releases](https://github.com/HU-Jiashu/bosar/releases). Bosar is built for Apple silicon
   (M1 and later); there is no Intel build.
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
