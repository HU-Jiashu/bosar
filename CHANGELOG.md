# Changelog

What changed for users, release by release. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Pre-releases are marked as such on
the [Releases](https://github.com/HU-Jiashu/bosar/releases) page.

## [0.4.0-beta] — 2026-10-17

**The first installable Bosar.** Windows (`.exe`, per-user) and macOS (`.dmg`) installers,
built and smoke-tested on every platform; the GPU as a plug-in (`bosar gpu install`);
`bosar demo` runs a synthetic DInSAR pair on any installed build. Validated on real data: the
16-scene ALOS-1 PALSAR series of Mexico City (2007–2011) reproduces the pattern and the rates
of Chaussard et al. (2014) — Nezahualcóyotl −223 mm/yr along the line of sight, the airport
−192, the volcanic outcrops still — and is judged USABLE by the new deforming-area verdict; the
three-year Sentinel-1 series of Indianapolis (89 dates) stays USABLE in both the PS / DS and
the classic PSI chain; ENVISAT ASAR and ERS-1/2 pairs and the first NISAR granule read through
the stripmap chain.

### Added
- Installers: a one-folder application with the `bosar` command line and the `bosar-gui`
  desktop application, SNAPHU (built without the CS2 solver), GDAL / PROJ, the licence texts
  and a build record; a Windows per-user `.exe` (no administrator rights, Start-menu entries,
  optional PATH and `project.json` association) and a macOS `.dmg` (unsigned; right-click →
  Open once). `bosar version` names the build; `bosar preflight` reports the build record
  (P305) and the GPU plug-in (P202).
- The GPU plug-in: `bosar gpu status | install [--no-ctk] | remove` fetches CuPy and the CUDA 12
  runtime from PyPI into the user's plug-in folder (no pip needed); the next run uses the GPU.
- `bosar demo <folder>`: a synthetic stack, a project, one DInSAR pair — the smoke test of an
  installed build, no data and no network needed.
- The deforming-area mode of the time-series verdict: `--area stable | deforming | auto` on
  `pipeline sbas | psds` and `sbas quality --area`. In `deforming` mode the velocity spread is
  judged about a smooth field (`--smooth-km`, 1 km) and whole-cycle steps relative to each
  pixel's fitted line; the reference, when the chain chose it, moves to the most coherent cell
  of the stable quintile (`--stable-end max | min`); `auto` picks `deforming` when the raw
  spread exceeds three times a stable area's expectation. The Run page offers the choice.
- Outlier dates in two levels: a date with more than 20 % outlier pixels is noted (`(info)`),
  one at 35 % or more is marginal, and the verdict drops only when two or more dates are
  marginal. `sbas quality` re-judges stored results with the current thresholds and takes
  `--step` and `--area`.
- `sbas_invert --link-coherence-min`: the good mask of a PS / DS product gated by the phase
  linking's per-pixel temporal coherence — the default (0.7) of `--method sequential`.
- ALOS-1 PALSAR: 16-scene series through the strided stripmap chain (ground cells of 14 m for
  the linking grid and 28 m for the pairs SNAPHU unwraps) — 17 times faster than at full
  resolution with the same product.
- `fetch dem --timeout-s` and a direct download of the missing Copernicus GLO-30 tiles when the
  stitcher is slow or fails; `fetch slc` verifies a present file once by MD5 and afterwards by
  a tail hash; stacks that mix Sentinel-1A and 1D are labelled so.
- NISAR: `open_nisar(frequency="auto")` takes frequency A when present, else the one there;
  the first provisional RSLC granule opens.
- Online basemaps are off until enabled in Settings; a custom XYZ template takes an API key;
  every provider's attribution is drawn on the map.
- The Settings page shows the licence (an About card with the licence, notice and third-party
  texts).
- Documentation: the feature tour at 1080p in the pages and at 4K in `bosar-tour-4k.zip`
  (with the where-to-click animations and the DInSAR recording), the tour in Chinese, the
  walkthrough's installed-build chapter, the documentation site with the API reference, the
  sensor download plan.
- `scripts/gacos_vs_era5.py`: the per-date comparison of the two zenith-delay fields.

### Changed
- Licence: PolyForm Noncommercial License 1.0.0; every commercial right reserved by the author,
  commercial licences available. The source is not published; the installers and this
  documentation are.
- Sequential phase linking (`--method sequential`) is gated by the linking coherence; `auto`
  stays the default for every stack length.
- Unwrapping on an installed build initialises with MST (the SNAPHU inside has no CS2 solver);
  the step summary records the initialisation and warning W503 says so.
- The quality report labels informational findings `(info)`.

### Fixed
- The newest run log is taken by name, not by modification time (a 2-second file-system
  resolution could pick the wrong log).
- An excluded date the network no longer holds is noted, not refused.
- The per-pair range bandwidth of the ionosphere estimate comes from the scene records (the
  Sentinel-1 default exceeded the ALOS sampling rate).

## [0.3.0-alpha] — 2026-10-07

- PS / DS time series (phase linking of distributed scatterers plus persistent scatterers, a
  hybrid stack through the SBAS inversion) and classic PS-InSAR (periodogram, arcs, APS) as an
  independent chain; a quality verdict on every time series.
- Native Sentinel-1 processing from the raw zips (bursts, deramp, geometric coregistration,
  enhanced spectral diversity, calibration, sub-swath merge) — no SNAP needed.
- Sentinel-1 SLC search and resumable, verified download from ASF; the SNAP bridge.
- Offset tracking, six speckle filters, thermal-noise removal, the ionosphere split-spectrum
  estimate as a diagnostic, the common-mode time reference and outlier dates.
- The first readers of ALOS-1 PALSAR, ENVISAT ASAR, ERS-1/2 and NISAR; the stripmap
  coregistration chain.
- The feature tour at 4K; the GUI shows the sensor, band and quality profile of a stack.

## [0.2.0-alpha] — 2026-09-30

- SBAS time series: network design, derived pairs, batch unwrapping, triplet closure and
  closure-based correction, inversion, temporal coherence, velocity and displacement series,
  GACOS and ERA5 corrections, MintPy export.
- The result viewer with basemaps, layers, opacity and masks, linked views, time-series plots
  and figure export; the feature tour; the Chinese walkthrough.
- Flattening from orbits and DEM; the auxiliary-data page (orbits, DEM, GACOS).

## [0.1.0-alpha.2] — 2026-09-25

- Renamed to Bosar. Two-pass DInSAR, coherence change detection with damage-proxy maps,
  amplitude change; the SNAPHU unwrapper bundled for Windows; the desktop application
  (project, data, system check, runs, logs, settings).

## [0.1.0-alpha.1] — 2026-09-24

- The foundation: project files, the step runner with tiled NumPy / CuPy kernels, the
  pre-flight check, JSON Lines run logs with microsecond UTC timestamps, precise failure
  screens, readers for the SNAP → GAMMA/StaMPS export and Sentinel-1 SAFE.
