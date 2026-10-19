# Supported input formats and the quirks found on real data

One section per reader. "Quirk" means something the files say that is not true or not what the
format documentation promises; Bosar reports each one (W-code) and never corrects it
silently. Started in v0.1.0.

## GAMMA / StaMPS export written by SNAP (`data/gamma_stamps.py`, reader `gamma`)

Layout: `rslc/<date>.rslc(.par)`, `diff0/<ref>_<sec>.diff(.par|.base)`, `geo/<ref>.lat|.lon`,
`geo/elevation_dem.rdc`, `dem/`. Big-endian FCOMPLEX / REAL*4, read through `np.memmap` windows.
Validated on the author's Indianapolis IW2 stack (29 dates, reference 20240821, 25925 × 12239).

| # | Quirk | What the file says | What is true | Bosar |
|---|---|---|---|---|
| 1 | **Nominal slant-range axis** | `range_pixel_spacing 2.0 m`; `near_range_slc` / `far_range_slc` = `center_range_slc` ∓ (N−1)/2 × 2 m (819528.6 / 871376.6 m) | spacing `c / (2 · rangeSamplingRate)` = 2.329562 m; `center_range_slc` (845452.572 m) is the **first-pixel** range of the SAFE annotation to the millimetre | W201 on the stack; `data import --annotation <SAFE>` overwrites spacing, near/mid/far range and stamps `geometry.provenance = safe-annotation:<file>` (I201) |
| 2 | **Earth radius under the sensor** | `earth_radius_below_sensor 6358256.3 m` | 6369807.5 m from the annotation orbit (WGS-84 radius at the sub-satellite latitude); the par value is 11.5 km too small and shifts every incidence angle by ≈ 1.5° and B⊥ by ≈ 8 m | same W201 / `--annotation` (both radii replaced, incidence taken from the geolocation grid) |
| 3 | **Copied reference header** | every `<date>.rslc.par` carries the reference scene's `title`, `date` (2024 8 21) and `start/center/end_time`; only the state vectors differ per scene | the scene date is the file name | W201 once per stack; `acq_utc` = file-name date at day precision (`2024-09-02`); with `--annotation` the SAFE `startTime` of every date that has a SAFE |
| 4 | **Half-seconds times** | `start_time 42612.60 s`, `center_time 42618.89 s`, `end_time 42625.18 s` (of day) | the SAFE says 23:40:25 – 23:40:52 UTC = 85225 – 85252 s of day: the par values are exactly half | not used at all (see 3); documented here, not fixed — one stack is not enough to code a rule |
| 5 | **Geo layer `.par` is a copy of the SLC par** | `geo/<ref>.lat.par` says `image_format FCOMPLEX`, `range_samples/azimuth_lines` | the layer is REAL*4 | the reader accepts `width/nlines` **or** `range_samples/azimuth_lines` and never trusts `image_format` for a geo layer; the file size check guards the dtype (E203) |
| 6 | **Malformed `.base` sidecars** | `initial_baseline(TCN)` of 20240821_20240809, _20241231, _20250524 hold 1e11 – 1e15 m | garbage (the same three dates MintPy dropped) | E205 from `parse_base`; W202 on the stack, the interferogram is kept, the pair has no baseline row until v0.2.0 recomputes B⊥ from orbits |

Baselines: B⊥ = B_C cos θ − B_N sin θ with θ the look angle at the scene-centre range (from the
radii and the range axis — hence quirks 1–2 move B⊥: 223.8 m nominal vs 216.1 m in SNAP's own
metadata for 20240821_20240704).

**MintPy's `bperp` of this stack is not a perpendicular baseline.** The author's
`ifgramStack.h5` stores, per pair, the raw C (cross-track) component of the `.base` TCN vector
(`gamma_utils.read_baseline`; 261.21 m for 20240821_20240704 where the projected B⊥ is
213.9 m). Bosar always stores the projected B⊥ above. answer 4: the MintPy
exporter writes the projected value; a `--mintpy-legacy-bperp` flag will reproduce
the raw C component when a result has to be compared with the author's existing MintPy runs.

### Deburst grid timing and height reference

Verified against SNAP's `geo/20240821.lat/.lon` with Bosar's own `rdr2geo` (probe p21, median
0.046 px, p95 0.086 px over 198 594 samples):

| quantity | where it comes from | value (IW2, 20240821) |
|---|---|---|
| first line UTC | annotation `productFirstLineUtcTime` (= SAFE `startTime`; the par's `start_time` is **half** the seconds of day, quirk 4) | 23:40:25.206955 |
| line interval | annotation `azimuthTimeInterval` (= par `azimuth_line_time`, correct) | 2.0555563 ms |
| number of lines | `(productLastLineUtcTime − productFirstLineUtcTime) / interval + 1` | 12239 = `azimuth_lines` |
| near range | annotation `slantRangeTime · c / 2` (the par's `center_range_slc`; its `near_range_slc` is centre − (N−1)/2 × a nominal 2 m) | 845 452.572 m |
| range spacing | `c / (2 · rangeSamplingRate)` (= annotation `rangePixelSpacing`) | 2.329562 m |
| `elevation_dem.rdc` | **ellipsoidal** heights (SNAP applies the geoid before writing); a ±33.5 m shift moves the solution by 11 px in range | 112–332 m over the scene |
| look side | right: nadir × velocity | — |

## Bosar crop (`data/crop.py`, reader `crop`)
`crop.json` + little-endian tiled GeoTIFFs written by `bosar data crop`. Carries the source
sha256, the window, the shifted geometry and its `provenance` (so a crop made with
`--annotation` keeps the corrected scalars). No quirks — it is our own format.

## Sentinel-1 SAFE (`data/sentinel1_safe.py`, reader `safe`)
- The author's unzipped SAFEs are VV-only and have no `annotation/calibration/` (W203); the VH
  files listed in the manifest are absent (warning, VV opens).
- The 20240704 IW1 measurement TIFF is a 1-byte placeholder → E203 naming SAFE, swath, file,
  actual and expected bytes; `--swaths IW2,IW3` opens the rest.
- Times in the annotation are UTC with microseconds; the geolocation grid holds degrees
  (converted to radians on read).

### Burst quirks (the native TOPS chain; `data/burst.py`)
- A burst's `azimuthTime` is the zero-Doppler time of its line 0 (`sensingTime` is the raw
  acquisition start); the bursts of one date share the azimuth grid, so the start differences
  are integer multiples of `azimuthTimeInterval` to ~1e-9 lines.
- The valid region is per line: `firstValidSample` / `lastValidSample` arrays with `-1` on the
  invalid lines at both ends; ISCE2's rectangle (the run of valid lines, the samples common to
  its first and last line) is what the merge and ESD use. Consecutive bursts overlap by about
  100 lines; the merged grid cuts the overlap in the middle.
- `azimuthFmRate` and `dcEstimate` are lists of polynomials in `τ − t0` with `τ = 2 r / c`;
  each burst takes the entry nearest its mid time (ISCE2). `azimuthSteeringRate` is in deg/s.
- The PRF lives in `generalAnnotation/downlinkInformationList/downlinkInformation/prf` (older
  annotations may lack it; the model keeps `prf_hz=None`) — `azimuthTimeInterval`, not the
  PRF, is the line spacing of the focused product.
- The raw pool's zips store the measurement TIFFs deflate-compressed (1.4 GB → 0.9 GB), so
  random access through the zip is not possible: `extract_safe_members` inflates manifest,
  annotation and measurement of one sub-swath into `<project>/cache/safe/<name>.SAFE/` once.
- Orbit state vectors in the annotation are seconds of day; a product near midnight gets
  vectors of the previous / next day (unwrapped by ±86400 s against the product start).

### Sentinel-1D next to Sentinel-1A, and newer processor versions

Track 121 (ascending) over Indianapolis, sub-swath IW2, as read from the products on disk:

| | S1A 2024-08-21 | S1A 2026-06-24 | S1D 2026-07-13 |
|---|---|---|---|
| IPF version | 003.80 | 004.03 | 004.03 |
| radar frequency [Hz] | 5 405 000 454.33 | same | same |
| range sampling rate [Hz] | 64 345 238.13 | same | same |
| azimuth time interval [s] | 2.0555563e-3 | same | same |
| azimuth steering rate [deg/s] | 0.97986 | same | same |
| processed range bandwidth [Hz] | 48.3e6 | same | same |
| lines x samples per burst | 1505 x 25925 | 1504 x 25389 | 1504 x 25389 |
| slant range time of sample 0 [s] | 5.6402524e-3 | 5.6406765e-3 | 5.6406747e-3 |

- **S1D is handled like S1A / S1C**: the same annotation schema, the same relative-orbit
  track (121), precise orbits named `S1D_OPER_AUX_POEORB_...` (ASF mirror, CDSE), product names
  `S1D_IW_SLC__...`. Nothing in the reader or the burst model is platform specific; the
  platform is recorded per date (`secondaries.<date>.mission` in the stack record) so that
  cross-platform interferograms can be told apart.
- **The burst size is not a constant of the track.** The 2026 products (IPF 004.03, S1A and
  S1D alike) have one line and 536 samples fewer per burst and start 63.5 m farther in slant
  range than the 2024 ones. The native chain resamples every secondary onto the reference's
  burst grid from the geometry, so the mix needs no special case; a reader that assumes one
  burst shape per stack would fail.
- **Azimuth timing of S1D against S1A.** ESD on the two S1D dates coregistered to the S1A
  reference converged to +0.0455 and +0.0468 lines (94 microseconds, about 0.65 m along track),
  against 0.0001 ... 0.009 lines (absolute) for the 49 converged S1A dates of the same stack: a constant
  along-track timing offset between the platforms, removed by ESD. Without ESD (geometry only)
  a cross-platform interferogram would carry a burst-edge phase jump of about
  `2 pi * 0.046 * dt * 4.5 kHz = 2.7 rad`.
- Range: the cross-correlation check gives -0.063 and -0.048 px for the S1D dates, inside the
  scatter of the S1A dates (-0.19 ... +0.12 px).
- S1D phases 7 days after S1A on this track in mid 2026 (S1A 2026-06-24, S1D 2026-07-13 =
  +19 days = 12 + 7): cross-platform pairs have temporal baselines of 7 + 12 k days.

### Range shift of a date by IPF version, and what it really is

The amplitude cross-correlation of every date against the reference (20240821) on the
downtown crop of track 121, IW2 bursts 6–8, 88 secondaries 2023-07-10 … 2026-09-23
(`scripts/range_shift_by_ipf.py`):

| IPF | platform | dates | first – last | median shift [px] | min / max [px] | max burst spread [px] | applied | > 0.1 px (W209) |
|---|---|---|---|---|---|---|---|---|
| 003.61 | S1A | 9 | 20230710 – 20231014 | +0.013 | −0.067 / +0.048 | 0.014 | 4 | 0 |
| 003.71 | S1A | 20 | 20231026 – 20240610 | −0.027 | −0.195 / +0.087 | 0.014 | 13 | 5 |
| 003.80 | S1A | 12 | 20240622 – 20241113 | +0.036 | −0.064 / +0.122 | 0.018 | 10 | 2 |
| 003.90 | S1A | 8 | 20241125 – 20250217 | −0.100 | −0.128 / +0.018 | 0.020 | 3 | 4 |
| 003.91 | S1A | 9 | 20250301 – 20250605 | +0.018 | −0.103 / +0.100 | 0.012 | 3 | 2 |
| 003.92 | S1A | 10 | 20250617 – 20251003 | −0.002 | −0.102 / +0.076 | 0.013 | 4 | 1 |
| 004.00 | S1A | 5 | 20251015 – 20251202 | −0.078 | −0.173 / +0.007 | 0.022 | 2 | 1 |
| 004.01 | S1A | 1 | 20251214 | −0.188 | — | 0.007 | 1 | 1 |
| 004.02 | S1A | 1 | 20260107 | −0.129 | — | 0.004 | 1 | 1 |
| 004.03 | S1A, S1D | 13 | 20260224 – 20260923 | −0.063 | −0.155 / +0.030 | 0.024 | 7 | 2 |

**The shifts do not cluster by IPF version** — within almost every version they span ±0.1 px.
They are **propagation delays** (`scripts/range_shift_vs_era5.py`): the change of the
tropospheric delay (ERA5 zenith total delay at the crop centre, 1 / cos θ) and of the
ionospheric **group** delay (40.31 TEC / f², 1.38 cm per TECU at 5.405 GHz; slant TEC from the
CODE rapid GIM at the pierce point) between the date and the reference:

| predictor (87 dates) | r | R² | residual std |
|---|---|---|---|
| troposphere only | 0.36 | 0.13 | 0.064 px |
| ionosphere only | 0.70 | 0.49 | 0.049 px |
| troposphere + ionosphere | **0.87** | **0.76** | **0.034 px (7.8 cm)** |
| both with free coefficients | — | 0.77 | 0.033 px; coefficients 0.94 and 0.83 |

The ionosphere dominates (±0.18 px: slant TEC differences of up to ±30 TECU between dates near
the 2024–2025 solar maximum; the reference date has 46 TECU). The coregistration geometry has no
atmosphere, so the envelope of a secondary sits where its group delay puts it; the range
correction moves the envelope back and leaves the carrier phase alone (verified with the two
versions of one date: 0.005 rad across the crop). The measured shift is thus also an
independent, if coarse, estimate of the TEC difference of each date (0.03 px ≈ 5 TECU).

**v0.4.0: the implied ΔSTEC per date is a product.** `bosar aux range-shift <project>
--stack <id> [--era5-dir] [--ionex-dir] --write` (`pipeline/auxdata/rangeshift.py`, which
supersedes the v0.3.0 script) computes per secondary date the ERA5 zenith delay at the crop
centre on the date and on the reference (the two hourly files around the acquisition, no
download), `tropo_px = Δztd / cos θ / Δr`, `residual_px = measured − tropo`, and
`implied_dstec_tecu = residual_px × Δr f₀² / (40.31 × 10¹⁶)` (168.8 TECU per pixel at 2.33 m and
5.405 GHz); with IONEX maps on disk the GIM slant-TEC difference at the pierce point stands next
to it (`gim_dstec_tecu`), and the summary carries the regressions of v0.3.0 plus
`implied_vs_gim`. `--write` stores the values in every date's `coreg.json`
(`record.range_cc.delay`, with the sign convention) and in the coregistration step's summary
(`range_shift_delay`, `range_shift_delay_fit`); `bosar sbas quality` then prints the
`shift[px]`, `dSTEC[TECU]` and `GIM[TECU]` columns in its per-date table. Sign: a positive shift
is a later echo (more delay on the date than on the reference); ΔSTEC = STEC(date) −
STEC(reference).

### Thermal-noise annotation and IPF versions (`data/noise.py`)

`annotation/calibration/noise-<mission>-<swath>-<product>-<pol>-<start>-...xml`, one per
sub-swath and polarisation, named like the calibration XML; read from the zip without
extraction. Values are noise power in DN^2 (the unit of `|DN|^2`), linear. Two layouts:

| IPF | elements | noise power |
|---|---|---|
| 2.90 and later (from March 2018) | `noiseRangeVectorList/noiseRangeVector`: `azimuthTime`, `line`, `pixel` (list), `noiseRangeLut` (list); `noiseAzimuthVectorList/noiseAzimuthVector`: `swath`, `firstAzimuthLine`, `firstRangeSample`, `lastAzimuthLine`, `lastRangeSample` (inclusive), `line` (list), `noiseAzimuthLut` (list) | range(line, sample) x azimuth(line) inside each block |
| before 2.90 | `noiseVectorList/noiseVector`: `azimuthTime`, `line`, `pixel`, `noiseLut` | range only |

- The IPF version is in `manifest.safe`: `<safe:software name="Sentinel-1 IPF"
  version="003.80"/>` under the `processing` metadata object (the annotation XML does not
  carry it). The Indianapolis products are 003.80 (2024) and 004.03 (2026).
- IW SLC (xarray-sentinel's S1B 2021-04-01 test product, IPF 003.31, IW1, 9 bursts of 1501
  lines, 21632 samples): one range vector per burst, 542 pixels every 40 samples ending at
  21631, plus one vector at the product stop time; one azimuth block over the whole sub-swath
  (lines 0-13508, samples 0-21631) with a value every 10 lines that follows the TOPS
  scalloping (about 1.16 at a burst edge).
- **Quirk: the range vectors' `line` is one burst early in TOPS SLC.** The vector whose
  `azimuthTime` equals burst k's `azimuthTime` has `line` = first line of burst k-1 (-1501 for
  burst 0; the calibration vectors of the same product map time to line correctly). Bosar picks
  each burst's range vector by azimuth time, as SNAP does; interpolating by `line` would give
  every burst its successor's vector (a few percent of noise power, tenths of a dB near the
  noise floor).
- The azimuth `line` list and the block bounds are image lines of the sub-swath (burst k
  starts at `k x linesPerBurst`), the same frame as the calibration LUT.
- `tests/synthetic/safe.py` writes `<noise/>` placeholders with `with_calibration=True`: an
  unusable annotation (E205 when read; `thermal_noise=auto` then skips the subtraction).

## SNAP BEAM-DIMAP (`data/beam_dimap.py`, reader `dimap`) — synthetic fixtures only so far
- `Abstracted_Metadata/radar_frequency` is in **MHz**; `.img` bands are big-endian ENVI.

## ISCE2 topsStack (`data/isce_stack.py`, reader `isce`) — synthetic fixtures only so far
- `los.rdr` band 0 is the incidence angle in degrees, band 1 the azimuth angle; `reference/IW*.xml`
  is needed for the wavelength and the slant-range axis.
- Bosar's native TOPS chain (`s1_coregister`) writes this layout itself, with the
  addition `DATA_TYPE = CINT16` (int16 I/Q pairs, BIP; half the bytes of CFLOAT) when asked
  for; the reader returns complex64 either way.
- The stripmap chain (`stripmap_coregister`) writes the same
  layout with `reference/<MODE>.xml` (`FBS.xml`, `IMS.xml`, ...; the reader takes any
  `reference/*.xml`, `IW*` first) carrying `dopplerCentroid` (the JSON of the slant-range Doppler
  polynomial, `{"r0_m", "coeffs_hz"}`; absent = zero-Doppler), `azimuthPixelSize`, `prf`,
  `lookSide`, `mission`; `orbits/<date>.json` (each date's state vectors, so `slc_flatten` and the
  baselines need no project orbit file) and a `coreg.json` next to every SLC with that date's own
  centroid, offsets and refinement.

## IONEX 1.0 global ionosphere maps (`data/ionex.py`) - synthetic fixtures only so far

Read for the order-of-magnitude test of the split-spectrum ionosphere (`docs/design/ionosphere.md`
section 4). Format description: Schaer, Gurtner & Feltens (1998), "IONEX: The IONosphere Map
EXchange Format Version 1".

- **Fixed columns.** Every header and map record carries its label in columns 61-80. Header
  records read: `EPOCH OF FIRST MAP` / `EPOCH OF LAST MAP` (6I6, UTC), `INTERVAL` (I6, s),
  `# OF MAPS IN FILE`, `MAPPING FUNCTION` (COSZ / QFAC / NONE), `BASE RADIUS` (F8.1, km),
  `MAP DIMENSION` (only 2 is supported: a single layer), `HGT1 / HGT2 / DHGT`,
  `LAT1 / LAT2 / DLAT`, `LON1 / LON2 / DLON` (2X,3F6.1; km, degrees), `EXPONENT` (I6, default
  -1). `START OF AUX DATA` ... `END OF AUX DATA` blocks (differential code biases) are skipped.
- **Maps.** `START OF TEC MAP` (I6 index), `EPOCH OF CURRENT MAP`, then per latitude band a
  `LAT/LON1/LON2/DLON/H` record (2X,5F6.1) followed by the band's values, 16 per line (I5); `END
  OF TEC MAP`. RMS maps the same (`START OF RMS MAP`); height maps (3-D files) are skipped.
  Values are in `10**EXPONENT` TECU - an `EXPONENT` record inside a map overrides the header's
  for that map; `9999` = no value (NaN). Latitudes usually run north to south (`DLAT < 0`); a
  global grid repeats -180 as +180.
- **End of day.** CODE writes the last map of a daily file as hour 24 of that day
  (`2024 12  3 24  0  0`); the reader accepts hour 24. An acquisition after the last map is
  served by merging the next day's file (`merge_maps`).
- **Interpolation** (`IonexMaps.vtec_at`): bilinear between the four nodes; between two maps
  linear in time with the maps rotated by 360 deg/day (the "rotated maps" of the format
  description: a point keeps its local solar time); NaN off the grid or next to a missing node.
- **Single layer.** Shell height = `HGT1` (450 km for CODE / IGS), radius = `BASE RADIUS`
  (6371 km); `sin z' = R / (R + H) sin z`, slant TEC = VTEC(pierce point) / cos z', the pierce
  point `z - z'` of earth-central angle from the ground point toward the sensor.
- **Files.** CODE final GIMs at `http://ftp.aiub.unibe.ch/CODE/YYYY/`:
  `COD0OPSFIN_YYYYDDD0000_01D_01H_GIM.INX.gz` (25 hourly maps, 00:00-24:00 UTC) since GPS week
  2238 (2022-11-27), `CODGDDD0.YYI.Z` before (`code_gim_candidates`). Plain and gzip files are
  read; Unix-compress `.Z` files are refused with a hint (decompress them first). The library
  never downloads; `scripts/validate_iono_winter.py` does, into its default `data/aux/ionex` (another
  folder only with `--download`).

## NISAR L1 RSLC (`data/nisar.py`, reader `nisar`) - real granules opened, a real pair through the stripmap chain

One HDF5 granule -> one `StripmapScene` per polarisation and frequency sub-band
(`open_stripmap(path, polarisation="HH", frequency="A", band="L")`; `frequency` defaults to
`auto` - A when the granule holds it, else the frequency it holds; `polarisation` to the first
of the frequency's `listOfPolarizations`; `band` to the band the file holds, L before S).
Registered as `nisar`; the sniffer accepts an HDF5 file (signature at offset 0 or after a
power-of-two user block of 512 B to 64 KiB) that holds `/science/LSAR/RSLC/swaths` (or `SSAR`).

### The real granules (provisional L1 RSLC, `NISAR_L1_RSLC_PROVISIONAL_V1`)

| granule (cycle, track, frame, date) | mode / pol code | content | size |
|---|---|---|---|
| cycle 33, track 40, frame 50, 2026-10-14 | `0005` / `NASV` | frequency B alone: VV, 5 MHz, 13680 x 6393 | 0.38 GB |
| cycle 23, track 58, frame 53, 2026-06-18 | `0505` / `SHSV` | frequency A: HH, 5 MHz; frequency B: VV, 5 MHz; 41040 x 6381 each | 2.19 GB |
| cycle 24, track 58, frame 53, 2026-06-30 | `0505` / `SHSV` | as above (the 12-day repeat of the same frame) | 2.19 GB |

What the reader found in them:

- **L band, left-looking, descending** (`lookDirection` = `Left`, `orbitPassDirection` =
  `Descending`). The track 58 / frame 53 granules hold 41040 lines x 6381 samples per
  frequency, at a slant-range spacing of 24.98 m (25 m range pixels; the derived range
  sampling rate `c / (2 dr)` is 6.0 MHz for the 5 MHz processed bandwidth).
- **A zero-Doppler grid with its own line rate**: `zeroDopplerTimeSpacing` is 1/1520 s
  (0.658 ms) while `nominalAcquisitionPRF` is 1911.1 Hz - the RSLC lines are not the radar
  pulses. The reader takes the line interval from `zeroDopplerTimeSpacing`
  (`azimuth_time_interval_s`) and keeps the PRF as `prf_hz`.
- **The mode and polarisation codes of the file name**, read from these two kinds of granule
  (not from a specification): two digits of processed bandwidth in MHz per frequency, A then
  B (`0005`: no frequency A, 5 MHz on B; `0505`: 5 MHz on both), and two letters per
  frequency (`NA`: not acquired; `SH` / `SV`: single polarisation HH / VV).
- **The centre frequency belongs to the frequency group**, not to the letter: 1221.5 MHz on
  frequency A and 1236.5 MHz on frequency B of the `0505` granules, 1221.5 MHz on the
  frequency B of the `0005` granule. The wavelength is each scene's own
  (`processedCenterFrequency` of the frequency opened). The stripmap chain does not compare
  the scenes' wavelengths: pair granules of one mode (with `frequency="auto"`, a granule that
  holds frequency A and one that holds frequency B alone open different sub-bands).
- **Orbit**: `orbitType` = `MOE` (medium-precision) in all three.

`fetch slc` has no NISAR mission: the track 58 / frame 53 pair was found with `asf_search` and
downloaded by Bosar's download loop (`bosar.fetch.slc`, resumable, the size and MD5 of the ASF record
checked) with the Earthdata login. Two things of the ASF records were new: a NISAR record
lists `bytes` **per file of the granule** (a dictionary - the HDF5's entry is the scene's
size), and the scene name keeps its `.h5` extension.

### The first pair through the stripmap chain

Track 58 / frame 53, 2026-06-18 / 2026-06-30 (12 days), frequency A HH, cropped to
69.05-69.30 N, 131.3-130.7 W (tundra, lakes and channels; 8186 lines x 957 samples after the crop),
GLO-30 DEM: `pipeline stripmap-coregister --reader nisar` on the CPU in 308 s. Geometric offsets +556.5
lines / +1.66 samples; the amplitude refinement adds a constant of +0.35 / -0.24 px (azimuth
rms 0.96 px over 258 patches - the lakes and channels decorrelate; range rms 0.03 px).
`B_perp` 60 m. The interferogram: coherence median 0.51 (67 % of the pixels >= 0.4) at 12 days
of L band in summer.

**Left-looking geometry (fixed).** The first interferogram showed about 28 fringes of
flat-earth phase across 24 km of range (an unwrapped std of 49.8 rad): the imported stack's
geometry carried no look side, so the flattening steps (`slc_flatten`, `ifg_flatten`), the
stack's orbit geometry and the orbit baselines solved the ground point on the right of the
track - the reader and the coregistration had the scene's side right. The stack geometry now
carries the look side of its reference scene and every ground-point solution of a stack uses
it. Re-flattened, the range ramp is gone (unwrapped std 5.2 rad). What remains is a smooth
azimuth gradient of about 17 rad over 28 km (2.7 cycles); the ionosphere at 69 N in June or
the medium-precision orbit are the candidates - not corrected.

### Reachability probe (2026-10-16, `asf_search` 14.0.3, metadata only, no login, nothing downloaded)

- `asf.search(platform="NISAR", processingLevel="RSLC", maxResults=25)` **does return L1 RSLC
  products**: dataset `NISAR_L1_RSLC_PROVISIONAL_V1`, files at
  `https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L1_RSLC_PROVISIONAL_V1/<granule>/<granule>.h5`
  (the search was marked incomplete at 25, i.e. the archive holds more). `platform="NISAR"` alone
  also lists `NISAR_L0B_RRSD_PROVISIONAL_V1` (L0B raw, 43 MB samples). A download needs an
  Earthdata login (`bosar auth`), as for Sentinel-1; the pair above came through Bosar's
  download loop that way.
- The newest 25 RSLC granules were all of 2026-10-14, cycle 033, tracks 032 and 033, ascending and
  descending, frames 013-155, **0.76-30.4 GB per `.h5`**, each with a `_LATLON.png` quick-look,
  `_LATLON` / `_NATIVE` / `_NATIVE_A_<pol>` KMLs, an `.iso.xml`, a QA report (PDF), QA stats
  (HDF5), a `_QA_SUMMARY.csv` and an `.rc.yaml` run configuration. Example (3.6 GB):
  `NISAR_L1_PR_RSLC_033_033_A_045_0505_SVSH_A_20261014T114317_20261014T114401_P05023_N_F_J_001.h5`.
  Name fields as observed: `<cycle>_<track>_<A|D>_<frame>_<mode 0005|0505|2005|4005>_<pol code
  NASV|NADV|SVSH|DHDH>_<A|M>_<start>_<stop>_P<orbit>_N_<F|P>_J_<version>` - the meaning of the mode
  and polarisation codes is not in a specification on disk; what the granules opened since
  show is in the section above.
- A later search listed more than 600 RSLC granules, and one frame repeats every 12 days:
  the pair above is such a repeat.

### Layout: what was verified against which source

The product specification (JPL D-102274) is not on disk; the paths in the reader's docstring
table were reconstructed from the open ISCE3 sources (Apache-2.0; read, nothing copied):

| item | source | status |
|---|---|---|
| dataset names, dtypes and `units` strings under `RSLC/swaths/`, `RSLC/swaths/frequencyA/`, `RSLC/metadata/orbit/`, `metadata/processingInformation/parameters/frequencyA/`, `metadata/calibrationInformation/` | ISCE3 writer `python/packages/nisar/products/writers/SLC.py` | verified in source |
| which datasets the ISCE3 swath / metadata loader reads (`zeroDopplerTime`, `zeroDopplerTimeSpacing` in the swaths group; `slantRange`, `processedCenterFrequency`, `nominalAcquisitionPRF`, `processedRangeBandwidth`, `processedAzimuthBandwidth`, `numberOfSubSwaths`, `validSamplesSubSwathN` in the frequency group) | `cxx/isce3/product/Serialization.h` | verified in source |
| identification datasets (`zeroDopplerStartTime`, `zeroDopplerEndTime`, `lookDirection`, `orbitPassDirection`, `absoluteOrbitNumber`, `listOfFrequencies`, `boundingPolygon`, `missionId`, `productType`; bytes scalars) | `python/packages/nisar/products/readers/Base/Identification.py` | verified in source; `trackNumber` (uint32) and `frameNumber` (uint16) from the writer |
| reference epoch of every time axis: attribute `units` = `seconds since YYYY-MM-DDTHH:MM:SS` (integer seconds) or `...:SS.fffffffff` | `cxx/isce3/io/Serialization.h` (`setRefEpoch` / `getRefEpoch`) | verified in source; the reader accepts both, and a space instead of the `T` |
| orbit group: `time`, `position` (meters), `velocity` (meters / second), `orbitType` (FOE / NOE / MOE / POE / Custom, default `Undefined`), `interpMethod` (Hermite / Legendre) | `cxx/isce3/core/Serialization.h` | verified in source |
| image dtype `complex32` = compound `('r', float16), ('i', float16)`; `complex64` also possible | `python/packages/isce3/core/types.py`; probe with h5py 3.16 (`.dtype` returns the compound, no `c4` error; `ds.astype(complex32)[window]` slices lazily) | verified |
| `lookDirection` / `orbitPassDirection` spellings | writer asserts `Ascending` / `Descending`; `lookDirection` is copied from the L0B | seen on the real granules: `Left`, `Descending`; the reader compares case-insensitively |
| the image grid is zero-Doppler (`doppler` = zero polynomial); the `dopplerCentroid` LUT under `processingInformation/parameters/frequencyA/` is the raw-data Doppler used in focusing | ISCE3 focusing design | **assumed**; consistent with the real pair (the geometric coregistration from the zero-Doppler grid is within 0.35 lines of the amplitude refinement); the LUT's max |value| is kept in `extra["doppler_centroid_lut_max_abs_hz"]` |
| SLC phase sign = ISCE's `-4 pi R / lambda` (Bosar's convention), no conjugation | - | **assumed**; consistent with the real pair (its flat-earth phase cancels on flattening, where the opposite sign would double it); the reader still sets `extra["phase_sign_verified"] = False` |
| range sampling rate: the product has none; `range_sampling_rate_hz = c / (2 slantRangeSpacing)` | - | derivation, noted in `extra["range_sampling_rate_source"]` |
| `calibration_db`: none - the RSLC carries linear `scaleFactor` / `differentialDelay` / `differentialPhase` per polarisation | writer | `scaleFactor` kept in `extra["calibration_scale_factor"]` |

Checks the reader makes (all E205 / E204 with the HDF5 path in `dataset`): every required path
present; `zeroDopplerTime` and `slantRange` uniform at their stated spacings (1e-6 of the step
plus 16 ulp of the stored values, so a reference epoch months before the scene passes);
`processedCenterFrequency` between 0.1 and 100 GHz; image shape equal to the axes; the orbit
usable (>= 4 vectors, increasing times); the polarisation listed and present; the frequency in
`listOfFrequencies`. Times are converted from the product's reference epochs (one per time axis)
to seconds after midnight UTC of the `zeroDopplerStartTime` date; the orbit is rebased to the
same epoch. Non-finite samples are read as `0 + 0j`.

Fixture: `tests/synthetic/nisar.py` writes the layout above from a `synthetic_scene` (complex32
or complex64 images, several polarisations, frequency A or B, distinct reference epochs for the
time axis and the orbit, `omit=` for the missing-path tests). The quirks of the real granules
(frequency B alone, the line rate below the PRF, the left look side, the per-file sizes of the
ASF records) are in the sections above; the fixture writes one frequency per granule, so a
`0505`-style granule with two frequencies at different centre frequencies exists only as real
data.

## ENVISAT ASAR IMS and ERS IMS in the Envisat format (`data/asar.py`, readers `asar` / `ers_envisat`)

The author's 26 products over Mexico City (track 255, descending, frame 3213; catalogue in
`mexico_city_esa_products.md`): 20 `ASA_IMS_1P...N1` (ENVISAT ASAR, IS2, VV, 2003-03-07 ...
2010-06-18) and 6 `SAR_IMS_1P...E1/.E2` (ERS-1 1996-05-16, ERS-2 1996-05-17 ... 2000-03-17).
All were produced by ESA's on-the-fly service in October 2026 with `SOFTWARE_VER="ASAR/7.00"`:
the ERS scenes come from the ASAR processor in the ASAR product format, so one parser serves
both flavours, with a sensor table (`asar.SENSORS`) for the nominal constants that are only
checked (W223), never substituted. The ESA specification (PO-RS-MDA-GS-2009 vol. 8) was not on
disk: ISCE2's `EnviSAT_SLC.py` gave the MPH / SPH / DSD scheme and the first offsets of three
records, the rest of the layout was reconstructed on the products (the `data/asar.py` module
docstring lists every offset read; big-endian throughout). Opened through
`bosar.data.stripmap.open_stripmap` as a `StripmapScene`; `scripts/validate_asar_products.py`
prints the report below for a folder.

### What the products say

| | ASAR IMS (IS2, VV) | ERS-1 IMS | ERS-2 IMS |
|---|---|---|---|
| radar frequency [Hz] (MPP 987) | 5 331 004 416 (float32 of 5.331004416 GHz) | 5 299 999 744 (float32 of 5.3 GHz) | same |
| range sampling rate [Hz] (MPP 983) | 19 207 680 | 18 962 468 | same |
| chirp / processed range bandwidth [Hz] (MPP 743 / 1024) | 16.0e6 / 16.0e6 | 15.55e6 / 15.55e6 | same |
| PRF [Hz] (MPP 703) = 1 / `line_time_interval` | 1652.4156 (6.0517463e-4 s) | 1679.9023 (5.9527281e-4 s) | same |
| processed azimuth bandwidth [Hz] (MPP 1274) | 1316 | 1378 | 1378 |
| lines x samples; MDS record | 30 334-30 377 x 5168, 20 689 B (20090911: 29 431 x 5160) | 30 940 x 4992, 19 985 B | 29 114-30 940 x 4991-4992 |
| first-pixel two-way time [ns] (grid) / slant range [m] | 5 502 445.0 / 824 795.8 | 5 522 634.5 / 827 822.1 | same |
| range spreading-loss reference `range_ref` [m] (MPP 979) | 800 000 | 847 000 | 847 000 |
| external calibration constant K (MPP 1381) | 32 284.94 | 65 026.0 | 93 325.3 |
| processing scaling factor (MPP 1377) | 120 000 | 403 597.7 | same |
| filters, looks | HAMMING 0.75 range and azimuth, 1 x 1 | same | same |
| scene height of the geolocation grid [m] (MPP 1541) | 2527.35 (20090911: 0.0) | 0.0 | 0.0 |
| state vectors (MPP 1765 + 36 k) | 5, first to last line, 4.59 s apart, 1e-2 m / 1e-5 m/s, Earth-fixed | same | same |
| `VECTOR_SOURCE`; `ORBIT STATE VECTOR 1` DSD | `DP`; `DOR_VOR_AXVF-P...` | `PC`; `DOR_VOR_AXVF-P1996...` | `PC`; `DOR_VOR_...` |
| mid-swath Doppler centroid [Hz] (DOP ADS) | -15 ... -143 (confidence 0.99) | +133 | -91 ... -349 (0.97-0.98) |

### Quirks and decisions

| # | Quirk | What the file says | What is true / what Bosar does |
|---|---|---|---|
| 1 | **Signed MJD days** | MJD fields are `days, seconds, microseconds` since 2000-01-01 | the day is a signed i32 (`-1325` for 1996-05-16); ISCE2 unpacks `>3L` and would date the ERS scenes in 2117. Bosar reads `>iII` |
| 2 | **Scene height of the geolocation grid** | the ASAR grids' lat / lon (and the SPH corners) sit at `avg_scene_height_ellpsoid` = 2527.35 m (MPP offset 1541; ISCE2 reads 1537, four bytes early, as it reads the state vectors at 1761 instead of 1765) | with h = 0 the ASAR tie points are 6.0 km off cross-track (6050 m on the ground = 2300 m along the line of sight at 23 deg); ERS grids and ASA 20090911 are at 0 m. `tie_point_agreement` and the chain's geocoding must use `extra["geolocation_grid"]["height_m"]` |
| 3 | **ERS products labelled `SWATH="IS2"`** | SPH `SWATH="IS2"` on ERS too (processor label) | `mode="IM"` from the flavour, the swath string kept in `extra["swath"]` |
| 4 | **State vectors span exactly the frame** | five vectors at the first, last and three intermediate line times | no margin for the geometry kernels: the reader extends them by `orbit_margin_s` (10 s) on both sides with two-body + J2 propagation in the Earth-fixed frame (`core.orbit.extend_orbit`); the model reproduces vector 4 from vector 0 (18.4 s) to 0.01-0.03 m on ASAR and 0.17-0.24 m on ERS (two-body alone: 1.5-1.8 m), and the MPH vector 20-60 s earlier to 0.01-0.35 m, which also confirms the Earth-fixed frame |
| 5 | **Doppler polynomial units** | `DOP CENTROID COEFFS ADS`: origin `slant_range_time` in ns, five coefficients | the coefficients are Hz, Hz/s, Hz/s^2, ... of `tau - tau0` in **seconds** (c1 = -8.5e5 Hz/s on ASAR, -230 Hz across the swath); the origin is 5 samples past the first-sample time. Converted to slant range into `extra["processed_doppler_centroid"]`; the scene's own `doppler` is zero (zero-Doppler product) |
| 6 | **Line timing** | `line_time_interval` float32 6.0517463e-4 s; every MDS line carries its own MJD stamp | the stamps follow the interval to < 1 us over the frame; the reader takes `(last - first) / (lines - 1)` (double precision, consistent with both ends) and reports the ADS value in `extra["line_time_interval_ads_s"]`; a disagreement above the stamp resolution is W223 |
| 7 | **Zero-filled edges** | first lines and last samples hold 0 + 0j (`quality_flag` 0 everywhere) | no-data stays 0 + 0j as the contract says; the chain's valid mask comes from the samples |
| 8 | **Frame sizes vary** | 30 334-30 377 lines; 20090911 has 29 431 x 5160 and a 0 m grid; ERS 20000317 has 4991 samples, 19960517 29 114 lines | every product carries its own geometry; nothing is assumed per track |
| 9 | **Float32 constants** | radar frequency 5 299 999 744 Hz on ERS | the product value is used as read (5e-8 relative to 5.3 GHz); the nominal table only checks it |

### Geometry convention and the measured agreement

The products are focused to zero Doppler (`ALGORITHM="RAN/DOP"`, lines stamped with zero-Doppler
times): line `row` is at `first_zero_doppler_time + row * dt`, sample `col` at the two-way time
of the first grid sample plus `col / range_samp_rate`. Acceptance test
(`tests/test_integration_asar_real.py`, `asar.tie_point_agreement`): `rdr2geo` of all 286 tie
points (13 records x first and last line x 11 samples; 264 on the two short frames) from the
product state vectors, at the grid's scene height, against the tie points' own lat / lon:

| products | max [m] | median [m] | along-track mean [m] | cross-track mean [m] |
|---|---|---|---|---|
| 20 ASAR | 0.35 ... 0.53 | 0.14 ... 0.28 | -0.01 ... +0.09 | -0.23 ... -0.07 |
| 6 ERS | 0.90 ... 1.25 | 0.18 ... 0.28 | 0.00 ... +0.07 | -0.09 ... -0.06 |

(2026-10-16, all 26 products; the quantisation of the vectors and of the float32 range times is
~0.1 m.) The zero-Doppler claim, the signed MJD, the 1-based lines and samples, the Earth-fixed
frame and the scene height are all settled by this number; before the height was found the
ASAR products were 7.4 km off.

### Calibration

`calibration_db = -10 log10(K)` with `K = ext_cal_fact` (MPP 1381). The ESA convention for
single-look complex ASAR products (Rosich & Meadows 2004, ENVI-CLVL-EOPG-TN-03-0010) is
`sigma0 = |z|^2 / K * (R / range_ref)^3 * sin(incidence)`; the per-pixel range and incidence
terms are the caller's (`extra["calibration"]` carries K and `range_ref`). With it the mid-image
`|z|^2` of 20030307 (mean |z| 66) gives -10.8 dB and that of ERS-1 19960516 (mean |z| 57) gives
-15.4 dB for the same lake-bed area; the 4.6 dB gap is close to the 4.1 dB of `1 / sin 23 deg`
of the ERS convention (reference incidence 23 deg, Laur et al. 2004), so the ERS constant may
follow the ERS formula. Not verified on a target: an open point for the data report.

### ERS caveats

- ERS-2 lost its gyroscopes in January 2001; scenes from 2001-01-01 on get W224 (the Doppler
  centroid may be ambiguities large; the annotation less reliable). All six ERS scenes on disk
  predate that date. ERS-2 had already switched to one-gyro piloting in February 2000, and the
  one scene after that switch, 2000-03-17, carries a mid-swath Doppler of -349 Hz (0.21 PRF)
  against -91 ... -148 Hz on the 1996-2000-01 scenes (its tie points still agree to 1.25 m):
  W224 follows the January 2001 rule of the task, so that scene is *not* flagged - check its
  Doppler against its pair partner before trusting the azimuth spectra (the common-band filter
  reads `extra["processed_doppler_centroid"]["mid_swath_hz"]` of both scenes).
- The 1996 tandem pair (ERS-1 1996-05-16, ERS-2 1996-05-17, 1 day): B_perp +128 m at the scene
  centre from the product orbits; the two satellites share the 5.3 GHz carrier but carry
  different calibration constants (65 026 / 93 325).
- Doppler centroids of -91 ... -349 Hz (ERS-2) and +133 Hz (ERS-1): the azimuth spectra of a
  pair are offset by up to 0.3 PRF; the common-band filter of the chain needs the processed
  Doppler of both scenes (`extra["processed_doppler_centroid"]`).
- ESA's reprocessed ERS orbits come as `DOR_VOR_AX` files (the ERS products' `ORBIT STATE VECTOR
  1` DSD names `DOR_VOR_AXVF-P1996...`): the DORIS reader below serves ERS too; PRC is the legacy
  D-PAF format, and the one the public mirror serves for ERS (`fetch orbits --mission ers`,
  below).

### Pairs for the stripmap chain (from the product orbits, `scripts/validate_asar_products.py`)

| pair | days | B_perp [m] | B_par [m] | note |
|---|---|---|---|---|
| 20100514 / 20100618 | 35 | +168 | -73 | the only 35-day ASAR pair on disk: first ASAR pair |
| 20091225 / 20100305 | 70 | +37 | +20 | smallest ASAR baseline with a short span |
| 20050624 / 20051111 | 140 | +13 | +17 | smallest baseline overall |
| 19960516 / 19960517 | 1 | +128 | -69 | ERS-1 / ERS-2 tandem pair |
| 20000107 / 20000317 | 70 | -88 | +37 | ERS-2 / ERS-2 |

`B_perp` is the component of the secondary-minus-reference satellite vector along
`v_hat x los_hat` at the reference scene centre (signed); the critical baseline at C band with
16 MHz is about 1.1 km.

## DORIS and PRC precise orbits (`data/doris.py`, `pipeline/auxdata/esa_orbits.py`) - real files read

The readers were written against synthetic files (`tests/synthetic/envisat.py`, still the
fixtures of the tests); the real files now come from ESA's public mirror and have been read
for the ASAR and ERS pairs of the stripmap chain.

**Where the files come from.** ESA's own orbit servers need an EO Sign In account and FTP over
TLS; the SNAP auxdata mirror (`step.esa.int`) serves the same files without a login, one zip
per year:

- ENVISAT DORIS: `https://step.esa.int/auxdata/orbits/Doris/vor/<YYYY>.zip` (`DOR_VOR_AX`,
  2002-2012). Inside: `<YYYYMM>/DOR_VOR_AX..._<start>_<stop>.zip`, one inner zip per file;
  each file spans about 26.5 h (one state vector every 60 s) and is filed under the year and
  month of its **stop** date, so a file starting on 30 or 31 December sits in the next year's
  archive.
- ERS PRC: `https://step.esa.int/auxdata/orbits/ers_precise_orb/ERS<1|2>/<YYYY>.zip` (1991-2011).
  Inside: `<YYYY>/PRC_<yymmdd>_<orbit>_rev2.zip`, one inner zip per file; each file is named by
  the day of its first state vector, spans four to eight days (one vector every 30 s) and is
  filed under the year of its **start**, so the last file of a year runs into January.

`bosar fetch orbits <project> --mission envisat|ers --product <IMS product>` (or `--date
YYYYMMDD`, with `--satellite ERS1|ERS2` for ERS) downloads the year archives once into
`<project>/aux/orbits/esa/<mission>/` (the neighbouring year's archive too for a date next to
the year boundary; a short or corrupt download is not cached, a cached archive that no longer
opens is downloaded again), extracts the inner files that may cover each date into
`<project>/aux/orbits/esa/<mission>/files/`, reads them back and keeps those that touch the
date. A row is `ok` when one file covers a product's sensing window (the files together the
whole day of a bare date), `partial` when files touch the day but leave a gap, `missing` when
none does. That `files` folder is what the stripmap chain takes as `--orbits <folder>`.

**The formats.**

- **DORIS** `DOR_VOR_AX...` (precise) / `DOR_POR_AX...` (preliminary): Envisat format (MPH,
  SPH, one `DS_TYPE=M` data set named `DORIS PRECISE ORBIT` / `DORIS PRELIMINARY ORBIT`) of
  ASCII records `dd-MMM-yyyy hh:mm:ss.ffffff  delta-UT1  abs-orbit  X Y Z  VX VY VZ  quality`,
  one state vector per record (60 s apart in the real files), read by whitespace splitting
  (tokens 0-1, 4-6, 7-9, 10) as ISCE2's `DOR` class does. Earth-fixed frame, UTC.
- **PRC** (D-PAF / DLR, "DGM-E04"): 130-byte ASCII records. The real files open with a
  `DSIDP` record before the `STATE ` record (`DSIDP ERS1.ORB.PRC` / `DSIDP ERS2.ORB.PRC`): the
  sniffer accepts a file that starts with either. `STATE ` carries the arc's first / last
  epoch (0.1 days since J2000) and the TDT - UTC offset in ms at bytes 47-52; `STTERR`
  records carry the day (bytes 14-20, 0.1 days since J2000 noon, + 0.5 day), the TDT seconds of
  day in microseconds (20-31), x / y / z in mm (31-67) and vx / vy / vz in micrometres per second
  (67-100), the quality character at byte 127; `STTINE` (inertial) records are skipped. Columns
  and the J2000 / TDT bookkeeping reconstructed from ISCE2's `Orbit/PRC.py`; the real files
  bear the day convention (ISCE2's `+ 0.5`) out - their vectors agree with the products' own
  to about 10 m at mid scene. `.Z` files are refused with a hint.
- **The satellite** of every file is recorded (`OrbitRecords.satellite`: `ENVISAT`, `ERS1`,
  `ERS2`, or none when the file does not say): PRC from the `DSIDP` record, else from the
  COSPAR id of the state-vector records (`9105001` ERS-1, `9502101` ERS-2); DORIS from the
  SPH descriptor (`ORBITE POE_REST SAT ENV1` on the mirror's files). It matters for ERS: the
  ERS-1 and ERS-2 files of a year share one `files` folder and cover the same times in the
  tandem months.

**How a product takes its orbit.**

- `open_asar(path, orbit_file=...)` replaces the product's five vectors by the file's, windowed
  to the scene +- 60 s with four extra vectors on each side (`orbit_source = "VOR:<name>"` /
  `"POR:..."` / `"PRC:..."`); a file that does not cover the scene is E205.
- `open_asar(path, orbit_dir=...)` - the stripmap chain's `--orbits <folder>` - takes the
  file of the folder that covers the scene with 60 s to spare: VOR before POR before PRC, the
  longer span first within a kind; files that name another satellite than the product's are
  left out (files that name none are kept); none covering the scene is E201, with the
  `fetch orbits` command as the hint.
- The chosen file is checked against the product's own state vectors at mid scene: more than
  100 m apart is a W223; more than 1 km is not this product's orbit - a named `orbit_file` is
  refused (E204), a folder's file is skipped for the next covering one (W223), and E204
  follows when none is left.

On the real pairs: the DORIS VOR files of the ASAR pair 2009-12-25 / 2010-03-05 are 3-7 cm
from the products' own vectors at mid scene (the Envisat products carry DORIS-derived
vectors); the PRC files of the ERS-1 / ERS-2 tandem pair 1996-05-16 / 05-17 are 9.6-9.7 m
from them (9.1-9.2 m along track, the same on both dates), and `B_perp` moves from -141.54 m
(product vectors) to -141.58 m. The other ERS satellite's PRC file of the tandem day covers
the same times about 11 950 km away - the case the satellite match and the 1-km check exist
for.
## ALOS-2 PALSAR-2 L1.1 (CEOS) (`data/ceos_alos.py`, the same reader)

JAXA's L1.1 product is the ALOS-1 CEOS product with the PALSAR-2 layout
(`PALSAR-2_xx_Format_CEOS_E.pdf`); the reader tells the missions apart by the scene id and
reads both. Validated on JAXA's free Greenland sample pair (`730_greenland`: FBS, right-looking,
ascending, 2017-03-07 and 2017-03-21, 18265 × 9990 samples, 1.4 GB zips, every member
deflated - the chain extracts them once; `bosar fetch slc --mission alos2 --sample 730_greenland`
fetches them, `--sample list` names the 22 sets; ASF's ALOS-2 collection, searched with
`--mission alos2` without `--sample`, held ScanSAR WBD / WBS L1.1 only (30-60 GB a scene) in
October 2026).

**Names.** Scene id `ALOS2<orbit 5><frame 4>-<YYMMDD>`, then the product id
`<mode><L|R><level><option><projection><A|D>` (`ALOS2150521570-170307-FBSR1.1__A`; JAXA's zips
are `<order 10>_<item 6>_<scene id>.zip`, the folder holds `VOL- / LED- / IMG-HH- / TRL-`, a
`BRS-` quick-look and `summary.txt`). The **mode** comes from the product id (`ALOS2_MODES`):
stripmap UBS / UBD (nominal 84 MHz, 104.79 MHz sampling), HBS / HBD / HBQ (42 MHz, 52.40 MHz),
FBS / FBD / FBQ (28 MHz, 34.93 MHz) are read; the spotlight (SBS) and the ScanSAR products
(WBS / WBD / WWS / WWD / VBS / VBD, one image file per scan and polarisation:
`IMG-<pol>-<scene id>-<product id>-F<n>` next to the plain `VOL- / LED- / TRL-<scene
id>-<product id>`, as ISCE2's `contrib/stack/alosStack/read_data.py` globs them) are recognised
and refused with E205 naming the mode - they are not stripmap scenes; image files named per
scan are refused as ScanSAR (E205) whatever the product id says. A level other than 1.1 is
refused the same way. The leader's sensor id (`ALOS2 -L -0315-`: operation mode `03` = fine, calibration mode
`15` = during observation) is kept in `extra`. The quad modes are given their single-pol
bandwidths (assumption: no quad product seen).

**Records.** Data set summary, platform position (28 ECR vectors 60 s apart, `high
precision`), attitude (16384 B), radiometric (CF at 20/16, −83.0 dB) and the image descriptor
have the ALOS-1 offsets; five facility records of 3-728 kB are skipped by length. The signal
data record's prefix is **544 bytes** (descriptor field `prefix bytes`): the ALOS-1 fields to
byte 216 plus the **microseconds of day** (uint64 at 84) and the ALOS-2 frame number at 284;
the samples (`COMPLEX*8`, two big-endian float32) follow at 544. `_prefix_dtype(prefix_bytes)`
builds either layout from the descriptor; nothing is assumed from the mission.

**What differs from ALOS-1 and how the reader takes it:**

- *Time.* The microsecond stamps give the line times directly (`stamp_unit = "us"` in
  `extra["line_time_fit"]`); the millisecond field is the truncated microsecond value (ALOS-1's
  is rounded). On both Greenland scenes the stamps' own clock runs **8.8e-6 faster** than the
  leader's PRF (1826.4173 against 1826.4012 Hz: the line steps are 547 / 548 µs where
  1 / PRF is 547.53 µs; ±44 µs at the scene ends over 10 s) - **W221** reports it; the leader's
  PRF is used (the per-line PRF field agrees with it to the millihertz) with the centre-weighted
  fit of the stamps, so the scene centre matches the leader's centre time to the microsecond
  and the ends are off by 0.08 lines, which the coregistration's refinement absorbs. The check
  runs only on scenes spanning ≥ 1 s (`STAMP_CLOCK_MIN_SPAN_S`): below that the microsecond
  rounding alone exceeds the tolerance.
- *Range.* The leader's `range gate delay` (132.53 µs) is **not** the two-way delay to the
  first sample (757 926 m = 5055.8 µs): it is counted inside a pulse interval (547.5 µs) and
  does not even equal the delay modulo the interval (128.0 µs). The line headers' integer
  metres are the starting range (as ISCE2's `MultiMode/ALOS2.py` reads it); the leader's value
  is kept in `extra["range_gate_leader_us"]` and not checked. Spacing `c / (2 × 34.93 MHz)` =
  4.2913 m; the two Greenland scenes share the PRF, the starting range and the width (the
  lines differ by one).
- *Doppler.* The cross-track centroid polynomial (1478, 3 × F16.7) is in **Hz per pixel** as
  on ALOS-1 (−35.36 Hz, −1.1e-4 Hz/px on the first scene) and, unlike ALOS-1, the `Doppler
  center frequency` fields at 1734 / 1750 (`f = a + b R[km]`: −19.49 Hz, −0.02096 Hz/km) agree
  with it at the first sample to 0.01 Hz; the reader checks that (**W222** beyond
  `DOPPLER_CHECK_HZ` = 5 Hz) and uses the polynomial.
- *Pass and side.* Clock angle +90 = right as on ALOS-1; the product id's `A` / `D` must agree
  with the orbit's vertical velocity at mid scene (E204 otherwise); the first line's centre
  geolocation must lie on the clock angle's side of the track (E204, as on ALOS-1).
- *Calibration.* σ⁰ [dB] = 10 log10 |DN|² + CF − 32.0 with the leader's CF = −83.0 dB, as
  JAXA's format document states for L1.1 (`calibration_db = −115.0`; −11.3 dB on the Greenland
  ice at 36° incidence).
- *Bandwidth.* `range_bandwidth_hz` is the leader's chirp |rate| × pulse length (24.9 MHz
  on both Greenland FBS scenes: 693.97 GHz/s × 35.88 µs), **not** the mode's nominal 28 MHz:
  the leader's total processor bandwidth in range (1254, 24900 kHz) and bandwidth per look say
  the same, and the measured range spectrum of the SLC is flat to ±12.45 MHz (−3 dB width
  24.89 MHz) and 32-35 dB down at ±13 MHz (ISCE2's `MultiMode/ALOS2.py`
  takes the chirp too). The chirp is taken when it is plausible: positive, not above the
  sampling rate and within `ALOS2_BANDWIDTH_TOLERANCE` = 25 % of the mode's nominal value;
  else the leader's total processor bandwidth when it is plausible, else the nominal value,
  each fallback with a **W222**. The total processor bandwidth cross-checks a plausible chirp:
  more than `BANDWIDTH_CHECK_REL` = 2 % apart is a W222, and when both are plausible the
  **narrower** of the two is used, min(chirp, total) - the processed range spectrum is no
  wider than either (`range_bandwidth_source` = `total_bandwidth_range` when the total is the
  narrower; an implausible total leaves the chirp). In short:

    | chirp | total (leader) | used | W222 |
    |---|---|---|---|
    | plausible | blank, or within 2 % | chirp | no |
    | plausible | plausible, > 2 % apart | min(chirp, total) | yes |
    | plausible | implausible, > 2 % apart | chirp | yes |
    | implausible / blank | plausible | total | yes |
    | implausible / blank | implausible / blank | the mode's nominal value | yes |

    `extra` keeps `chirp_bandwidth_hz`, `total_bandwidth_range_leader_hz`, `nominal_bandwidth_hz`
    and `range_bandwidth_source` (`chirp` / `total_bandwidth_range` / `nominal`); the warning is
    in `extra["warnings"]`. The value reaches `coreg.json` and so the ionosphere step's
    sub-bands and the coregistration's interpolation kernel. `oversample_to_fbs` does nothing
    on an ALOS-2 scene (its FBD shares the FBS sampling). The ionosphere step's
    nominal-bandwidth table (`NOMINAL_RANGE_BANDWIDTH_HZ`, a fallback for `coreg.json` records
    written without a bandwidth) carries the ALOS-2 stripmap modes under mission `ALOS-2`: the
    fine modes FBS / FBD / FBQ take the 24.9 MHz measured on the JAXA fine-mode product (FBD /
    FBQ assumed the same, no such product seen), the ultra-fine and high-sensitive modes their
    nominal 84 / 42 MHz.

- *Polarisation.* PALSAR-2 stripmap products may be VV or VV + VH (single HH / HV / VH / VV,
  dual HH + HV / VV + VH): without `pol` the reader opens HH, else VV, else the first
  polarisation listed (`default_polarisation`, `extra["polarisation_source"]` = `default` or
  `requested`), so `open_stripmap` and the stripmap chain open a VV product as they open an HH
  one. The stripmap chain refuses a product list whose scenes do not share one polarisation
  (E101, the dates and polarisations named: an HH product next to a VV-only one); its `pol`
  parameter opens one named polarisation of every product (handed to the reader as
  `polarisation=`, which the CEOS reader takes for `pol`).
- *One product per listing.* `list_product` groups the files of a zip or a folder by their
  name tail (scene id + product id, `ALOS2150521570-170307-FBSR1.1__A`); a per-scan image
  `IMG-<pol>-<tail>-F<n>` joins the `LED-<tail>` product (so a ScanSAR product is **one**
  product, refused as ScanSAR, not 1 + N products). Only a tail with a `LED-` **and** an
  `IMG-` file is a product: a GDAL sidecar (`IMG-HH-<tail>.aux.xml`, written when QGIS
  computes statistics) or a stray file of an incomplete product is not one and is left out.
  Exactly one product per listing is opened: a folder or zip holding two products is E101
  (naming them), a member file (`LED-` / `IMG-` / `VOL-` / `TRL-`) opens its own product (see
  "One product at a time" in the ALOS-1 section, which shares the rule).
- *Mission check.* The file names say which mission; the leader's mission id (`ALOS2`) must
  agree (E205). The scene is `mission="ALOS-2"`, `sensor="PALSAR-2"`, wavelength 0.2424525 m,
  so the L-band quality profile applies as for ALOS-1.

## ALOS-1 PALSAR L1.1 (CEOS) (`data/ceos_alos.py`, stripmap reader `ceos_alos`)

ASF's L1.1 products: the zip `ALPSRP<orbit 5><frame 4>-H1.1__A.zip` (FBD: members
`VOL- / LED- / IMG-HH- / IMG-HV- / TRL-<id>-H1.1__A`, a quick-look and `summary.txt`, all
**stored**) or `ALPSRP<id>-L1.1.zip` (FBS: the same files inside a folder `<id>-L1.1/` with the
processor's `workreport` and logs, all **deflated**), or the extracted folder. Opened with
`open_stripmap(path)` / `open_alos(path, pol=None)` (HH, else VV, else the first polarisation
of the product; ALOS-2 shares the rule); `open_alos_scenes` gives every polarisation.
Validated on seven Mexico City scenes (frame 370, ascending, 2007-2011).

**One product at a time** (both missions). The product files are grouped by
their name tail (scene id + product id: `ALPSRP082730370-H1.1__A`,
`ALOS2150521570-170307-FBSR1.1__A`). ASF's H1.1 zips and JAXA's ALOS-2 zips are flat, so two
of them unzipped into one folder put two products side by side: a member file (`LED-` /
`IMG-` / `VOL-` / `TRL-`) opens its own product - the scene's `path` is then that file, which
re-opens the same product -, the folder itself is **E101** naming the products, and so is a zip
holding two products. Before the review the folder's files were merged by kind (the last
product's files under the first one's scene id: a silent wrong scene on ALOS-1, a misleading
E205 on ALOS-2). `extract_product` puts every zip into a folder of its own
(`<dest>/<zip stem>/`). Only a name tail with a `LED-` and at least one `IMG-` file counts as
a product (second fix of the review): a GDAL `.aux.xml` sidecar or the stray image file of an
incomplete product next to a product is left out instead of making the folder E101, and a
folder with no such pair is E201 listing the files found. ALOS-2 ScanSAR per-scan images
(`-F<n>`) join their `LED-` product (ALOS-2 section).

**Record layout relied on** (offsets in bytes from the record start; ISCE2 `alos_slc/*.xml`,
every binary field big-endian, every number in a text field Fortran-style):

| record | identified by | fields read |
|---|---|---|
| any record | bytes 0-12: record number (uint32), subtype (uint8), **type code** (uint8), two subtypes, record **length** (uint32) | the leader is walked record by record on these headers |
| volume descriptor (`VOL-`, 360-byte records) | first record; the records of the file are told apart by the **first subtype** byte (192 descriptor, 219 file pointer, 18 text), every one of them with type code 192 on the real products (the text record is not type 63) | specification (16/12), ids; then one file pointer record per product file (file id at 20/16, record count 100/8, length 108/8) and the text record (product type at 16/40, `PRODUCT:H1.1__A`) |
| leader file descriptor (`LED-`, 720) | type 192 | the record counts and lengths at 180-360 (6+6 each: data set summary, map projection, platform position, attitude, radiometric, ..., GCP) and the five facility records at 420-490 |
| data set summary | type 10 (4096) | scene id 20/16, scene centre time 68/32 (`YYYYMMDDhhmmssmmm`), pass flag 100/16 (blank on the real products), centre lat / lon 116, 132 (blank on the real products), centre line / pixel 324, 332 (8 each), channels 388/4, mission 396/16, orbit 444/8, clock angle 476/8 (+90 = right), incidence 484/8, **wavelength** 500/16, chirp amplitude coefficients 534 (3 × 16: constant [Hz], **rate [Hz/s]**), **range sampling rate [MHz]** 710/16, **range gate delay [µs]** 726/16, pulse length [µs] 742/16, baseband / range-compressed flags 758, 762, **PRF [mHz]** 934/16, processing facility / system / version 1046, 1062, 1070, product level 1094/16, looks 1174, 1190, bandwidth per look 1206, 1222, total bandwidth 1238, 1254 (azimuth [Hz], range [kHz]), **cross-track Doppler centroid** 1478 (3 × 16), time direction 1526, 1534 (the real products carry `ASCEND` / `DESCEND` in the second), cross-track FM rate 1606 (3 × 16), line / pixel spacing 1686, 1702 |
| platform position | type 30 (4680) | designator 12/32, elements 44 (6 × 16), **count** 140/4, year / month / day / day-of-year 144-160 (4 each), **seconds of day** 160/22, **interval** 182/22, frame 204/64 (`ECR`), then per point six F22 fields from 386 (x, y, z [m], vx, vy, vz [m/s]) |
| attitude | type 40 (8192) | count 12/4, per point from 16 (120 bytes): day 0/4, ms 4/8, flags, pitch / roll / yaw 24, 38, 52 (14 each, deg), rates |
| radiometric | type 50 (9860) | **calibration factor [dB]** 20/16 (the distortion matrices are blank) |
| data quality, facility (types 60, 200) | skipped by length | - |
| image file descriptor (`IMG-`, 720) | type 192 | records 180/6, **record length** 186/6, **bits per sample** 216/4, **samples per group** 220/4, **bytes per group** 224/4, lines 236/8, pixels 248/8, **prefix bytes** 276/4, data bytes 280/8, suffix 288/4, format type 400/28, **code** 428/4 |
| signal data record (one per line) | type 10, prefix of 412 bytes | line number 12, year 36, day-of-year 40, **milliseconds of day** 44 (uint32), channel 48, tx / rx polarisation 52, 54 (uint16: 0 = H, 1 = V), **PRF [mHz]** 56, chirp length [ns] 68, receiver gain 92, invalid-line flag 96, **slant range to first sample [m]** 116, lat / lon of the first / centre / last pixel 192-216 (int32, micro-degrees); the samples follow at 412 |

**Sample format, decided from the descriptor** (never assumed): `32` bits per sample, `2`
samples per group, `8` bytes per group, format `COMPLEX*8` / `C*8` → two big-endian IEEE
float32 per complex sample (I, Q). A product declaring 16 bits / 4 bytes would be read as
int16 pairs; anything else is E204. The amplitudes are of order 1e5 (|DN|² ≈ 6e10).

**Conventions and checks:**

- *Time.* Every line carries its UTC stamp as integer milliseconds of day (half a line of
  quantisation at 2160 Hz); `sensing_start_s` is the least-squares intercept of the stamps
  against `line / PRF` (residuals uniform in ±0.5 ms, std 0.289 ms on the real product, which
  says the stamps are rounded, not truncated - a truncation would bias the start by 0.5 ms,
  one line; both the `floor` and the `round` writer modes are tested). The leader's scene
  centre time must agree (W222 beyond 2 ms, E205 beyond 1 s; the real products agree within
  the millisecond). The epoch is the midnight of the first line's day.
- *PRF.* The leader's `Pulse Repetition Frequency in mHz` with decimals (2159.8272138 Hz) is
  used; the per-line field is the same number rounded to the millihertz (1e-7 relative). A
  variation across the lines above 1e-6 is E205 (one scene has one PRF), below it W221.
  ALOS-1 changed its PRF between scenes (2159.8 Hz on all seven Mexico City scenes, 1900-2200
  Hz in general): pairs of different PRFs are the chain's business.
- *Range.* `starting_range_m` is the leader's range gate delay × c/2 (845 217.56 m); the
  per-line field is the same in integer metres (W222 beyond 1 m, E205 beyond 100 m; constant
  across the lines or E205). Spacing `c / (2 fs)`: 9.3685 m (FBD, 16 MHz) and 4.6843 m (FBS,
  32 MHz). The FBS frame 370 scenes have 9344 samples where the FBD ones have 4640 (9280
  oversampled) and start 300 m nearer: the grids coincide only after coregistration.
- *Doppler.* The leader's cross-track Doppler centroid polynomial is in **Hz per range pixel**
  (`f = c0 + c1 p + c2 p²`, `p` the 0-based sample; the quadratic term is 0 and the linear one
  has four significant digits in the F16.7 field). Checked on the real product: the correlation
  Doppler estimator on 4096 × 256 blocks gives +89.0 / +87.7 / +86.8 Hz at near / mid / far
  range against the leader's +76.4 / +75.0 / +73.6 Hz - the slope −2.8 Hz across the swath is
  the per-pixel reading (per metre it would be −26 Hz); the 12 Hz offset is the scene's
  spectral centroid (antenna pattern × backscatter), not the processor's reference. The
  leader's `Doppler center frequency` fields at 1734 / 1750 are a different quantity (136.3 Hz
  and −0.0707 Hz/km) and are not used. The scene stores the polynomial in slant range
  (`p = (r − r0) / Δr`), unchanged by the FBD oversampling. The L1.1 image is **not**
  zero-Doppler: `rdr2geo` of the scene-centre line at zero Doppler lands 0.8-1.2 km from the
  prefix's centre geolocation on every scene, and `geo2rdr` of that geolocation lands
  `−f_dc / f_rate` = 0.11-0.17 s (250-370 lines) later and within 1-2 samples in range, i.e.
  a target on line `l` has its zero-Doppler time at `t_l − f_dc(r) / f_rate` (the FM rate is
  the leader's cross-track rate, −518.9 Hz/s at the first pixel).
- *Orbit.* The platform position record: 28 ECR state vectors 60 s apart, metres and m/s,
  `high precision` designator, covering 27 min around the scene; rebased to the scene epoch
  and densified to 10 s by 8th-order Lagrange so that the chain's cubic Hermite stays below a
  millimetre (0.3 m at 60 s). `pass_direction` from the vertical velocity at mid scene (the
  leader's pass flag is blank; its time-direction field says `ASCEND` and is kept as a hint).
- *Look side.* Clock angle +90 → right (ISCE2's reading), confirmed geometrically: the first
  line's centre-pixel geolocation lies on the right of the ground track (E204 otherwise).
- *Calibration.* σ⁰ [dB] = 10 log10 |DN|² + CF − A with the leader's CF = −83.0 dB (products
  processed after 2009-04-09; Shimada et al. 2009, IEEE TGRS 47(12)) and the L1.1 conversion
  A = 32.0 dB: `calibration_db = −115.0`, CF and A in `extra`. With −83 dB alone the Mexico
  City scenes would read +25 dB; with −115 dB a 256 × 256 centre window reads −6.0 to −7.8 dB
  (HH, urban / agricultural), which is the published range.
- *Mode.* From the sampling rate (32 MHz FBS, 16 MHz FBD; four polarisations at 16 MHz would
  be PLR); `range_bandwidth_hz` is the mode's nominal 28 / 14 MHz (`range_bandwidth_source`
  `nominal`): the chirp bandwidth |rate × pulse length| (28.0 / 14.0 MHz on the real leaders,
  in `extra` with the leader's total processor bandwidth in range) agrees with it.
  `oversample_to_fbs=True` serves an FBD scene on the 32 MHz grid by zero-padding the range
  spectrum of whole lines (`core/range_oversample.py`; original samples kept, the band
  centred, the Nyquist bin split; the last block of lines is cached so column tiles do not
  re-read): `n_samples`, `range_pixel_spacing_m` and `range_sampling_rate_hz` are the
  oversampled grid's, `range_bandwidth_hz` stays 14 MHz. On the real FBD scene the
  oversampled spectrum holds 1.4 % of the in-band power between 7 and 8 MHz (the chirp's
  roll-off) and 0.04 % above 8 MHz (the split Nyquist bin).
- *Reading.* One seek per line, the prefix skipped, only the requested samples; a stored zip
  is read in place through the member's absolute offset (2 ms for a 256 × 256 window), the
  deflated FBS zips through `zipfile`'s seekable stream, which inflates the member from its
  start for every window (1.5 s at the scene centre, 2.5 s to open): `extract_product` puts
  the four files into a cache folder once (the chain does this, as for SAFE zips), and
  `extra["deflated_members"]` names the members concerned.

Quirks found on the real products (frame 370, 2007-2011, processor `EOC-ALOS-DPS 1.00`):
the data set summary leaves the pass flag and the centre latitude / longitude blank (the
reader takes the centre line's prefix geolocation); the FBS zips are packaged differently
from the FBD ones (folder inside, deflated, extra files); the chirp phase coefficients and
the distortion matrices are blank; the volume directory's record count and product id fields
are blank.
