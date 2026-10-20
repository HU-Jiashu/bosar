# Licensing

*What Bosar is licensed under, what it ships with, what each component obliges, and what
would change if Bosar were ever commercialised. An engineering record, not legal advice.*

## 1. The licence of Bosar

- **Code and installers: PolyForm Noncommercial License 1.0.0**, verbatim in `LICENSE`, with
  one line above it: commercial licences are available from the author. Anyone may use,
  modify and redistribute Bosar for non-commercial purposes (research, teaching, personal and
  non-profit work); every commercial right is reserved by the copyright holder. The licence is
  not "open source" by the OSI definition — intended.
- **Copyright holder: Jiashu Hu**, sole author. Contact: oswaldmurphy66@gmail.com.
- **Publication model**: the source is not published; this repository holds the user
  documentation and the releases (installers, the 4K tour bundle). Zenodo archives the public
  releases; `CITATION.cff` names the author.
- Outside contributions, if ever accepted, come with a contributor licence agreement assigning
  the rights to the author.

## 2. Independence

Bosar was developed independently and self-funded: the hardware, the cloud and data-service
accounts (ASF / Earthdata, ESA, Copernicus CDS, GACOS requests) and the working time are the
author's own; no grant, assistantship task or institutional resource was used, and no
institution is named anywhere in the software or its documentation.

## 3. What ships, and what each component obliges

| Component | Licence | Obligation met by |
|---|---|---|
| Bosar | PolyForm NC 1.0.0, the author's copyright | `LICENSE`, `NOTICE`, the headers, the About dialog |
| Adapted code: ISCE2 / ISCE3 (Caltech) fragments in the ALOS, Envisat, DORIS and NISAR readers | Apache-2.0 (with a US export notice, EAR99) | the adaptation headers, the Apache text and the export notice in `THIRD_PARTY_NOTICES.md` |
| Adapted code: dolphin (Caltech) in the phase-linking kernels | BSD-3-Clause OR Apache-2.0 | same |
| Python packages in the installer (numpy, scipy, rasterio, pyproj, pydantic, typer, click, rich, psutil, keyring, platformdirs, scikit-image, pyqtgraph, matplotlib, asf_search, cdsapi, sentineleof, h5py and their dependencies) | BSD / MIT / Apache / PSF | the per-package table in `THIRD_PARTY_NOTICES.md` |
| Qt / PySide6 | LGPL-3.0 | one-folder builds only (the Qt libraries stay separate and replaceable), the LGPL text and the Qt source pointer shipped, the About dialog says so |
| SNAPHU 2.0.7 binary | Stanford terms: any use, no fee for redistribution; the CS2 solver is non-commercial only | the installers carry the build without the CS2 solver (MST initialisation); SNAPHU is included free of charge; its copyright notice is in `THIRD_PARTY_NOTICES.md` |
| ffmpeg (through imageio-ffmpeg) | GPL | a tool of the documentation build only; never part of an installer |
| IBM Plex fonts, Carbon icons and themes, Natural Earth | OFL 1.1, Apache-2.0, public domain | bundled with their licence files |
| Online basemaps (OpenStreetMap, EOX Sentinel-2 cloudless, Esri World Imagery, a user's XYZ server) | ODbL + OSMF tile policy; CC BY 4.0 (2016) / CC BY-NC-SA 4.0 (later years); Esri terms | none on by default; the attribution drawn on the map; the user chooses a provider in Settings |
| Data the user fetches (Sentinel-1, ALOS, ERS / ENVISAT, ERA5, Copernicus DEM, orbits, IONEX, GACOS) | each provider's terms; GACOS is for research use | not bundled; the user's own accounts and acceptance of the terms |
| Reference-only projects (MintPy, ESA SNAP, PyAPS, pypsi) | GPL / MIT | no code copied; SNAP runs as a separate program |

## 4. If Bosar goes commercial

Nothing in the present choice prevents a commercial licence, a dual licence, a source-available
licence or full open source later: the author holds every right. What would have to change on
that day:

- **SNAPHU**: keep it free and separate (a downloadable add-on, never part of a paid artefact),
  or replace it with an unwrapper under the author's control; the CS2 solver stays out.
- **Qt**: stay LGPL-compliant (one-folder, replaceable libraries, notices) or buy a Qt
  commercial licence.
- **EOX basemap**: only the 2016 mosaic (CC BY); the later years are non-commercial.
- **Esri World Imagery**: an ArcGIS licence or drop the provider.
- **GACOS**: research-only data — a commercial service must obtain permission from Newcastle
  University or use ERA5 only (the recommended correction anyway).
- **Adapted Apache / BSD code**: no change — the notices keep shipping.

## 5. Record

| Date | Change |
|---|---|
| 2026-09-16 | Project started (private, Apache-2.0; no copy ever distributed) |
| 2026-10-16 | Licence changed to PolyForm Noncommercial 1.0.0, commercial rights reserved; binaries-only publication; the notices generated and shipped; basemaps off by default; the licence shown in the application |
