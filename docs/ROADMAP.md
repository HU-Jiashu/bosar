# Roadmap

What Bosar does today, what comes next, and what is further out — by capability. Dates are not
promised; each release's [changelog](https://github.com/HU-Jiashu/bosar/blob/main/CHANGELOG.md)
says what actually landed.

## Available (0.4.1-beta)

- **Installers** for Windows (`.exe`, per-user) and macOS (`.dmg`); the GPU as a plug-in
  (`bosar gpu install`); `bosar demo` as the smoke test of an installed build.
- **Sentinel-1 IW**: the native TOPS chain from the raw zips (coregistration, ESD, calibration,
  sub-swath merge) and the SNAP bridge; SLC search and download from ASF; orbits, DEM, GACOS
  and ERA5 fetched or found locally.
- **Two-pass DInSAR**, **coherence change detection** with damage-proxy maps, **amplitude
  change** with speckle filters and thermal-noise removal, **offset tracking**.
- **Time series**: SBAS with closure-based correction; PS / DS by phase linking with a hybrid
  stack; classic PS-InSAR; a quality verdict with a stable-area and a deforming-area mode;
  tropospheric corrections (GACOS, ERA5); ionosphere split-spectrum diagnostics with opt-in
  models.
- **Stripmap sensors**: ALOS-1 PALSAR (a 16-scene series validated), ENVISAT ASAR, ERS-1/2;
  the first NISAR granule opens.
- **Desktop application**: every workflow as one command shown in the window, a result viewer
  with basemaps (off until enabled), layers, masks, time-series plots and figure export, logs
  with failure cards, the licence in the About card.
- **Documentation**: the feature tour (English and Chinese, 4K bundle), the Chinese
  walkthrough, the API reference.

## Next

- The installers' second iteration from the first field reports: a smaller bundle (the DEM
  through the direct tile download only), macOS notarisation when a developer certificate is
  available, the installer's own pages in the tour.
- The ionosphere per-pair plausibility gate before any model is subtracted (span and gradient
  against the band's physical bound and the GIM, triplet closure as a veto).
- ALOS-2 PALSAR-2 (CEOS L1.1 reader, the L-band profile reused) and the first NISAR
  interferogram when a repeat granule exists.
- DORIS precise orbits for ENVISAT / ERS and the orbital ramp they remove.
- An English walkthrough.

## Later

- SAOCOM, RADARSAT Constellation, Gaofen-3 (stripmap readers); the X-band commercial formats
  (TerraSAR-X, COSMO-SkyMed, ICEYE, Capella) from sample data; Sentinel-1 EW and SM modes.
- A Level-0 focusing study.
- Multi-track fusion and LOS-to-vertical decomposition; corridor and asset reports.

The sensor-by-sensor status, with archives and sample scenes, is kept in the
[sensor download plan](data/sensor_download_plan.md).
