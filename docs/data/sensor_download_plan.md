# Sensor download plan — every sensor Bosar could process, and how to get its data

*One row per sensor the readers handle today or could handle
with a reader of the same kind; for each: where the data come from, what registration it takes,
the product and format, a sample scene to verify with, what Bosar does with it today, and when
it is planned. The plan is a checklist: verify one sensor at a time, mark the row.*

Status key: ✅ reads and processes on real data · 🧪 reader on real data, no time series yet ·
🔬 reader on synthetic data only · 📋 no reader (a reader of the stripmap kind would do) ·
⛔ out of scope.

## 1. Free and open archives

| Sensor | Band · mode | Archive · access | Product · format | Sample to verify (site · ids) | Bosar today | Planned |
|---|---|---|---|---|---|---|
| Sentinel-1A/B/C/D | C · IW TOPS (also EW, SM) | ASF DAAC / Copernicus Data Space; Earthdata login (free) | L1 SLC `.SAFE` zip | Indianapolis path 121 (the three-year stack, 89 dates); Mexico City for a cross-sensor site | ✅ IW through the native TOPS chain and SNAP; EW/SM not read | SM (stripmap mode) 📋 next: the stripmap chain + a SAFE stripmap reader |
| ALOS-1 PALSAR | L · FBS / FBD / PLR | ASF DAAC (L1.1 CEOS); Earthdata login; `bosar fetch slc --mission alos` | L1.1 CEOS zip | Mexico City path 186 frame 370 (16 scenes 2007–2011) | ✅ pair and 16-scene series | done (0.4.0) |
| ENVISAT ASAR | C · IMS (IS1–IS7) | ESA EO-CAT / the author's order (free, registration); DORIS precise orbits (`DOR_VOR_AX`) from ESA's public STEP mirror without a login: `bosar fetch orbits --mission envisat` | `ASA_IMS_1P` `.N1`; orbits: Envisat-format DORIS files | Mexico City track 255 (20 scenes) | ✅ real pair, with the product's own vectors or a DORIS file (`--orbits <folder>`) | done (0.4.0) |
| ERS-1/2 | C · IM | ESA EO-CAT (free, registration); on-the-fly processing to the Envisat format; PRC precise orbits from ESA's public STEP mirror without a login: `bosar fetch orbits --mission ers` | `SAR_IMS_1P` `.E1` / `.E2`; orbits: D-PAF PRC files (130-byte records) | the 1996 tandem pair, Mexico City | ✅ real pair, with the product's own vectors or the PRC files of each satellite (`--orbits <folder>`) | done (0.4.0) |
| NISAR | L (+ S) · stripmap-like RSLC | ASF DAAC (provisional L1 RSLC, `NISAR_L1_RSLC_PROVISIONAL_V1`, 600+ granules in October 2026; a frame repeats every 12 days); Earthdata login; no `fetch slc` mission yet (found with `asf_search`, downloaded by Bosar's download loop) | L1 RSLC HDF5 (ISCE3 layout) | track 58 frame 53, descending (2026-06-18 / 06-30, 12 days, 2.19 GB each; mode `0505`: HH on frequency A, VV on B); the frequency-B-only granule of track 40 frame 50 (2026-10-14, 0.38 GB) | ✅ real pair: the granules open (left-looking, descending) and the pair goes through the stripmap chain to an interferogram (coherence median 0.51 at 12 days, frequency A HH) | next: a series of the frame |
| Sentinel-1 EW | C · EW TOPS (5 sub-swaths, 40 m) | as IW | L1 SLC | polar / coastal sites | 📋 the IW chain with EW burst parameters | next or later (low priority) |
| SAOCOM-1A/B | L · stripmap / TOPSAR | CONAE (free for research after registration; slow approval) | L1A SLC GeoTIFF + XEMT xml | Argentina / a CONAE-covered test site | 📋 a stripmap reader (GeoTIFF SLC + xml) | next |
| ALOS-2 PALSAR-2 | L · stripmap (UBS/UBD, HBS/HBD/HBQ, FBS/FBD/FBQ); spotlight and ScanSAR recognised and refused | JAXA's free sample sets (anonymous FTP `ftp.eorc.jaxa.jp/pub/ALOS-2/1501sample`, 22 sets; `bosar fetch slc --mission alos2 --sample <set>`); ASF's ALOS-2 collection (`--mission alos2`): ScanSAR WBD/WBS L1.1 only, 30-60 GB a scene (2026-10); JAXA G-Portal otherwise (registration) | L1.1 CEOS | JAXA `730_greenland` FBS pair (2017-03-07 / 03-21, 14 days) | ✅ reader (`data/ceos_alos.py`) on the real pair; the pair through the stripmap chain | done |
| RADARSAT Constellation (RCM) | C · stripmap, ScanSAR | NRCan EODMS (free open data, registration) | SLC `product.xml` + GeoTIFF/NITF | Canadian sites (open data areas) | 📋 a stripmap reader (product.xml) | later |
| Gaofen-3 | C · stripmap (FSI/FSII), others | China Centre for Resources Satellite Data (registration; access varies) | L1A SLC GeoTIFF + xml | a Chinese test site | 📋 a stripmap reader | later |
| LuTan-1 (LT-1A/B) | L · stripmap, bistatic | China (CASC); access limited | L1 SLC | — | 📋 | when data are reachable |

## 2. Commercial and sample data (free samples exist)

| Sensor | Band · mode | Access | Product · format | Sample to verify | Bosar today | Planned |
|---|---|---|---|---|---|---|
| TerraSAR-X / TanDEM-X / PAZ | X · stripmap, spotlight, ScanSAR | DLR science proposal (free for research), Airbus sample data (free download) | SSC (COSAR `.cos` + xml) | the Airbus sample scenes (various cities) | 📋 a COSAR reader | later |
| COSMO-SkyMed (first and second generation) | X · stripmap HIMAGE, spotlight | ASI science proposals; e-GEOS sample data | SCS HDF5 | the ASI sample set | 📋 an HDF5 reader | later |
| ICEYE | X · stripmap, spotlight | ICEYE sample data (free download) | SLC GeoTIFF + JSON (or HDF5) | ICEYE sample scenes | 📋 a stripmap reader | later |
| Capella | X · stripmap, spotlight | Capella Open Data (free, S3) | SLC GeoTIFF + JSON | Capella open scenes | 📋 a stripmap reader | later |
| RADARSAT-2 | C · stripmap, others | MDA (commercial); some sample products | SLC `product.xml` + GeoTIFF | a sample product | 📋 shares the RCM reader | later |
| Umbra | X · spotlight | Umbra Open Data (free) | SICD / GeoTIFF | Umbra open scenes | 📋 | later (spotlight needs a different geometry) |

## 3. What each verification takes

1. Fetch two scenes of one frame (a short temporal baseline) into `data/raw/<sensor>/`.
2. `bosar pipeline stripmap-coregister <project> --product A --product B --reader <name> --dem bosar --crop-wkt "…" --id <stack>` (or the TOPS chain for Sentinel-1).
3. `bosar sbas network … --name pair`, `bosar run … slc_flatten`, `bosar sbas prep … --flat-step …` → the coherence, the filtered and the unwrapped phase; the quick-looks go into the verification record.
4. With ≥ 3 dates: `bosar pipeline psds` (and `pipeline psi`) with `--area auto`; the quality verdict and a landmark table against a published rate.
5. The row above is marked ✅ with the ids used and the date.

## 4. Order proposed

Done: ALOS-2 (the same CEOS family, L band) and a NISAR pair, each a real pair through the
stripmap chain. Next: a NISAR series (a frame repeats every 12 days) → SAOCOM (L band, free for
research) → RCM (open data) → the X-band samples (TerraSAR-X, ICEYE, Capella) → Sentinel-1
SM / EW → Gaofen-3 and LuTan-1 when reachable.

The readers share one contract (`data/stripmap.py`: a `StripmapScene`), so each new sensor is a
reader and a fixture test, not a chain.
