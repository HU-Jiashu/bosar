# Bosar

**Open, install-and-run SAR interferometry for Windows and macOS.** Two-pass DInSAR, coherence
and coherence-change detection, amplitude change, PS-InSAR and PS/DS time series, SBAS, offset
tracking — on Sentinel-1 (native TOPS processing), ALOS-1 PALSAR, ENVISAT ASAR, ERS-1/2 and the
first NISAR granules — with automatic data, orbit, DEM and weather-model fetching, a desktop GUI,
optional CUDA acceleration and a full UTC-stamped processing log.

<p align="center"><img src="assets/tour/dinsar_run.gif" width="760" alt="A DInSAR run on the downtown Indianapolis crop"></p>

## Install

| Platform | Download | Notes |
|---|---|---|
| Windows 10/11 x64 | `bosar-<version>-win-x64-setup.exe` from [Releases](https://github.com/HU-Jiashu/bosar/releases) | per-user, no administrator rights; the GUI in the Start menu, `bosar` on the command line |
| macOS 12+ (Apple silicon, Intel) | `bosar-<version>-mac-arm64.dmg` / `-mac-x64.dmg` | unsigned: right-click → Open once (the README in the image) |
| GPU | `bosar gpu install` after installing | CuPy and the CUDA 12 runtime as a plug-in (about 1.5 GB) on an NVIDIA machine |

The installers carry everything else: Python, the numerical stack, GDAL/PROJ, the SNAPHU
unwrapper (built without the CS2 solver), the licence texts. See [Install](install.md).

## Where to go

- [Walkthrough](WALKTHROUGH.md) ([中文](WALKTHROUGH_zh.md)) — every step from an empty
  folder to a validated time series, with the commands.
- [Feature tour](tour/README.md) — every module, screenshots from the real application.
- Numerical conventions, held everywhere: positive LOS = toward the sensor; metres, seconds, radians; dates in UTC.
- [Errors, warnings and preflight codes](ERRORS.md) — what a code means and what to do.
- [Sensor download plan](data/sensor_download_plan.md) — every sensor the readers could
  handle, where its data come from, what is verified.
- [Licensing](LICENSING.md) — free for non-commercial use (PolyForm Noncommercial 1.0.0);
  commercial licences from the author; the third-party notices.

## Validated on

| Sensor | Site | Yardstick | Result |
|---|---|---|---|
| Sentinel-1 IW (native TOPS) | Indianapolis, 89 dates, 2023–2026 | the SNAP/StaMPS route, PSI against PS/DS, landmark series | PS/DS velocities within 1 mm/yr of the route-A product; verdict USABLE |
| ALOS-1 PALSAR | Mexico City, 16 scenes, 2007–2011 | Chaussard et al. (2014) | Nezahualcóyotl −223 mm/yr LOS, the airport −192, the volcanic hill −4 ± 3; USABLE in the deforming-area mode |
| ENVISAT ASAR, ERS-1/2 | Mexico City | the ESA pairs' documented fringe rate | real pairs form, unwrap and geocode |
| NISAR L-band | track 33 (provisional RSLC, October 2026) | the granule's own metadata | opens; a pair follows when a repeat exists |

Maintainer: Jiashu Hu — oswaldmurphy66@gmail.com.
