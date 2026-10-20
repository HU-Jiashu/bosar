# Bosar walkthrough: from a fresh clone to the downtown displacement map and damage proxy map

> **Using an installed build?** This walkthrough was written on a source checkout. The steps that use the source tree (`git clone`, `pip install -e`, `scripts/...`, `pytest`) need the source code, which is not published and is available only under a source licence from the author (see [Licensing](LICENSING.md)). With the installers, start at [Install](install.md) and at step 50 (the installed version); the `bosar` commands of the other steps are the commands of the installed build.

This is the English edition of the Chinese walkthrough `WALKTHROUGH_zh.md`; the screenshots are
shared between the two editions.

Applies to: `v0.1.0-alpha.1` (end of phase 1). This manual answers "how far does the
software go right now": every command was run verbatim while the manual was written, and the full
output is in the release notes. There is no graphical
interface yet; everything is done in PowerShell.

Goal: on a 7.2 × 10.8 km crop of downtown Indianapolis, starting from a GAMMA/StaMPS stack
exported by SNAP, obtain the geocoded line-of-sight displacement map `geo_disp`, the
coherence-change damage proxy map `geo_dpm`, the amplitude log-ratio and RGB composite, then clip
them to 500 m either side of the highways and export them as COG + GeoPackage. The whole process
takes about 8 minutes on the CPU, most of it the pip install of step 2; the processing itself is
under 2 minutes.

---

## Step 0: Edit these three variables for your machine (the only place that needs changing)

```powershell
$DATA = "<data-root>"                  # read-only data pool (this walkthrough only reads from it, never writes)
$MAIN = "<repo>"       # the main working copy, where SNAPHU is already built
$WORK = "<repo>\data\walkthrough_bosar"   # where the fresh clone goes
```

Files used under `$DATA`: the GAMMA stack `01_Preprocessed\01_IW2\`, the original zip
`00_RawData\S1A_IW_SLC__1SDV_20240821T..._E05B.zip` (only the geometry annotation is read, nothing
is extracted), the highway lines `04_GIS\indianapolis_highways.geojson`, and the GACOS folder
`05_Auxiliary\00_GACOS\`.

## Step 1: Clone the code

```powershell
New-Item -ItemType Directory -Force $WORK | Out-Null
Set-Location $WORK
git -c safe.directory=* clone --quiet $MAIN bosar_walk
Set-Location bosar_walk
git -c safe.directory=* log --oneline -1
```

The clone comes from the main working copy of step 0 (`$MAIN`); the public repository on
GitHub carries the documentation and the installers, not the source. Readers who were given
the address of the source repository put it in place of `$MAIN`. On a disk that does not record file ownership, git
reports "dubious ownership" (exit code 128) on a fresh clone; the command above allows it for this
one call only and does not touch your global configuration. To allow it permanently, run
`git config --global --add safe.directory <clone directory>` yourself.

## Step 2: Create the Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --quiet -e ".[dev,unwrap,viz]"
python --version
```

- `unwrap` installs scikit-image (the unwrapping fallback when SNAPHU is absent), `viz` installs
  matplotlib (quick-look figures).
- With an NVIDIA GPU, also run `python -m pip install -e ".[gpu]"` and the software uses CuPy
  automatically; this manual does not install it and runs everything on the CPU (`preflight`
  reports W401, which is normal).

## Step 3: Development environment variables

```powershell
. .\scripts\dev_env.ps1
```

Puts the ruff / pytest / CuPy caches inside the repository's `.cache\` and reminds you that only
one process should use the GPU at a time (do not run the full test suite while a pipeline is
running).

## Step 4: Self-check with `preflight`

```powershell
bosar version
bosar preflight
```

Checks Python, dependencies, GPU, disk, SNAPHU and so on item by item; `OK` passes, `WARN` lets you
continue, `FAIL` blocks the run. A fresh clone has no SNAPHU executable yet, so P401 shows `WARN`
(W501: it will fall back to scikit-image).

## Step 5: Put SNAPHU in place

```powershell
New-Item -ItemType Directory -Force packaging\bin\win-x64 | Out-Null
Copy-Item "$MAIN\packaging\bin\win-x64\snaphu.exe" packaging\bin\win-x64\
bosar preflight | Select-String "P401"
```

SNAPHU 2.0.6 is compiled by `packaging\snaphu\build.ps1` with MinGW-w64; on the same input it gives pixel-identical
results to the SNAPHU the author runs in WSL. The binary is not in git (licence and platform
reasons), so a fresh clone copies it from the main directory or compiles it. After the copy, P401
is `OK`.

## Step 6: Create a project

```powershell
bosar project new walk --name walk_demo --storage-mode full
```

A project is just a folder: `project.json` (steps, parameters, product inventory), `products\`,
`logs\`, `scratch\`. `full` keeps every intermediate product (handy for inspection); the default
`minimal` deletes the regenerable intermediate files when the chain finishes.

## Step 7: Crop downtown out of the full stack

```powershell
bosar data crop "$DATA\01_Preprocessed\01_IW2" --window 7904,8672,2590,5662 --dates 20240704,20240821,20240902,20240914,20250723 --annotation "$DATA\00_RawData\S1A_IW_SLC__1SDV_20240821T234025_20240821T234052_055318_06BEBA_E05B.zip" --out data\indy_downtown_crop
```

Reads a 768 × 3072 pixel window for 5 dates out of the 12239 × 25925 IW2 stack (read-only,
windowed reads, the full scene is never loaded) and writes GeoTIFFs + `crop.json` under this
repository's `data\`. `--annotation` reads the SAFE annotation straight from the original zip and
replaces the nominal geometry of the SNAP export (2 m range spacing, Earth radius 11.5 km too
small) with the real values (2.33 m and so on); `crop.json` records I201.

## Step 8: Import the crop and the full stack

```powershell
bosar data import walk data\indy_downtown_crop
bosar data import walk "$DATA\01_Preprocessed\01_IW2" --annotation "$DATA\00_RawData\S1A_IW_SLC__1SDV_20240821T234025_20240821T234052_055318_06BEBA_E05B.zip"
bosar project info walk
```

Import only registers metadata (dates, geometry, baselines, footprint); the raw data stays where
it is. The full stack has 29 scenes; the B⊥ of 20240821_20240704 is corrected from the nominal
geometry's 223.8 m to 213.9 m (SNAP itself gives 216.1 m). The project now holds two stacks, and
the pipelines below name one with `--stack`.

## Step 9: DInSAR pipeline → `geo_disp`

```powershell
bosar pipeline dinsar walk --stack crop_indy_downtown_crop --all-pairs --looks 2,10 --backend snaphu --geocode-coh
```

Each interferogram pair runs in turn: `ifg_import` (references the differential interferogram in
the stack) → `multilook` (2 × 10 looks, 28 × 23 m) → `coherence` (since v0.1.0 DInSAR defaults
to the `slc-box` recipe: a 5 × 5 window at full resolution, then averaged inside the 2 × 10
block, consistent with MintPy's coherence; `--recipe looks` is the standard estimator with 20
samples per multilook block. CCD defaults to `looks`, see step 11) → `goldstein` (filtering) →
`unwrap` (SNAPHU, single tile) → `geocode_unw` → `displacement` (`d = −λφ/4π`, metres, **positive
toward the satellite**, 0 at the reference point) → `geocode_disp` → `geocode_coh`. One line per
step on screen; the last line is the location of the run log. Four pairs make 36 steps, about 25
seconds on the CPU (results agree with the GPU to 1e-6).

## Step 10: Look at the quick-looks

```powershell
Get-ChildItem walk\products\figure -Name | Select-Object -First 12
```

- `*_coherence.png`: coherence (black 0 → white 1); river channels and vegetation are dark,
  buildings and roads bright.
- `*_unwrapped.png`: unwrapped phase (radians, symmetric red-blue).
- `*_displacement.png`: line-of-sight displacement (millimetres, red = toward the satellite,
  blue = away from the satellite, colour scale symmetric over the 2–98 % range); on 12–48 day
  short pairs this is mostly atmosphere (centimetre level), not ground subsidence.
- The `geo_*` products (`walk\products\geo_disp\` and so on) are EPSG:4326 GeoTIFFs that can be
  dragged straight into QGIS.

## Step 11: Coherence change detection → `geo_dpm`

```powershell
bosar pipeline ccd walk --pre 20240821_20240902 20240821_20240914 --co 20240821_20240704
bosar pipeline ccd walk --pre 20240821_20240902 20240821_20240914 --co 20240821_20250723
```

`--pre` gives the two pre-event pairs (summer, 12/24 days), `--co` the "event" pair. There is no
real destructive event, so: the first command is a **null test** (another pair of the same season);
the second is a **seasonal pseudo-event** (336 days, across winter). Measured results (with the standard estimator `looks`, details in the release notes): 2 % exceed the
quantile threshold, about 0.36 % remain on the map after despeckling; but in both cases the map
concentrates on coherent urban targets rather than vegetation: in C-band 12/24 day summer pairs,
fields and woodland are already decorrelated before the event, there is no coherence left to lose,
so the land-cover-map failure mode the review expected does not appear on this data. The null test
is not pure noise either: the 48 day event pair is itself more decorrelated than the 12/24 day
pre-event pairs, and a fixed threshold z ≥ 3 flags about 5 %. Products: `ccd_delta` (coherence
drop), `ccd_z` (standardised by the spread between the pre-event pairs, positive = drop), `dpm`
(1 = significant drop, 0 = none, 255 = masked where pre-event coherence < 0.3), and the geocoded
`geo_ccd`, `geo_dpm`. An artificially injected 200 m damage block is detected (test
`tests/test_ccd.py`, precision and recall ≥ 0.9 under `looks`).
The trade-off between the two coherence recipes: the 5-row azimuth window
of `slc-box` is larger than 2 looks, neighbouring multilook pixels share samples, `ccd_z` is
spatially correlated (Moran's I about 0.37 in the null test, < 0.1 under `looks`), and the edge of
the damage block gets an extra ring of flagged pixels (recall still 1, precision about 0.72):
small bias but blurred boundaries; `looks` pixels are independent of each other with crisp
boundaries, slightly more bias at low coherence. For damage mapping localisation matters more than
bias, so **`pipeline ccd` and the GUI's CCD workflow default to `looks`** (DInSAR still defaults
to `slc-box`). If CCD reads `slc-box` coherence, the log records a W106 note; to use it anyway, add
`--recipe slc-box` explicitly (a freshly computed coherence step should get a `--tag` so the two
sets of results coexist).

## Step 12: Amplitude change (log-ratio and RGB)

```powershell
bosar run walk amplitude --step-id amplitude_crop --stack crop_indy_downtown_crop --looks 2,10
bosar run walk log_ratio --step-id log_ratio_20240821_20250723 --requires amplitude_crop --pre 20240821 --post 20250723
bosar run walk rgb_composite --step-id rgb_20240821_20250723 --requires amplitude_crop --pre 20240821 --post 20250723
bosar run walk geocode --step-id geocode_log_ratio_20240821_20250723 --requires amplitude_crop --requires log_ratio_20240821_20250723 --source log_ratio
```

The GAMMA stack has no radiometric calibration, so amplitude change is **relative**: each date is
first normalised on "stable scatterers" (the 95 % of pixels with the lowest amplitude dispersion),
then `10·log10(I_post/I_pre)` is computed (positive = brighter). In the RGB composite red = pre,
green and blue = post: red means darkening, cyan brightening, grey unchanged. The calibration
look-up tables (σ⁰) can already be read straight from the original zips (all 33 zips readable) and
are used in the native SAFE workflow of v0.2.0.

## Step 13: Export (clipped to 500 m either side of the highways)

```powershell
bosar export walk all --aoi "$DATA\04_GIS\indianapolis_highways.geojson" --buffer-m 500 --out walk\export
Get-Content walk\export\README.txt -TotalCount 25
```

Each geocoded product is written as a cloud-optimised GeoTIFF (COG) with nodata beyond 500 m from
the highways; the vectors (product extent, reference point, AOI, stack footprint) go into one
GeoPackage; `README.txt` and `export.json` state each file's units, sign convention, reference
point, date pair and run id.

## Step 14: Where the logs are and how to read them

```powershell
bosar logs walk --tail 3
Get-ChildItem walk\logs -Name | Select-Object -Last 3
```

Each run writes one `logs\run_*.jsonl` (one JSON record per line, UTC time to the microsecond, with
parameters, inputs, outputs, duration, peak memory), next to a human-readable `.log` and a Markdown
report `.md`. `bosar logs walk --failure` shows the cause and hint of the most recent failure.

## Step 15: GACOS request card and validation of existing files

```powershell
bosar aux gacos-request walk --stack gamma_01_IW2
bosar aux gacos-check walk --stack gamma_01_IW2 --dir "$DATA\05_Auxiliary\00_GACOS"
```

GACOS has no API: the software computes from the project what to type into the gacos.net form,
the extent (N/W/E/S), the time (23:40 UTC, from the SAFE startTime, not the halved 11:50 in the
SNAP-exported par), the dates (at most 20 per request, so the 29 go in two batches); you submit the
form, and once the e-mail arrives you put the `.ztd/.rsc` files into `walk\aux\gacos\` and validate
them with `gacos-check`. All 29 dates already present in `<data-root>` pass (time difference 0.4 min,
edge margin 0.10°, no missing values). The tropospheric correction itself is added in v0.2.0.

## Step 16: The graphical interface

Start the GUI from the same PowerShell window (the virtual environment and `dev_env.ps1` are both
in effect):

```text
bosar gui walk
```

You can also run `bosar-gui walk` directly (the launcher without a console window). This step is
**not executed** by the automated check above, because the window stays open; closing the window
ends it. The interface settings (theme, recent projects, SNAPHU path, and so on) live in the INI
file pointed to by `$env:BOSAR_CONFIG_DIR` (in the development environment that is `.cache\config`
inside the repository); nothing is written to the registry.

The GUI does no computation of its own: **every action is one `bosar …` command**, shown in the
command bar at the bottom of the window, which can be copied to PowerShell with one click; the
results are exactly those of steps 6–15 above. Processing runs in a separate process, and the
interface reads the same `project.json` and `logs\run_*.jsonl`.

- **Project**: create / open a project; the summary card lists the data stacks, step status and the
  disk usage of each product level.
- **Check**: the `preflight` of step 4, grouped by system / GPU / dependencies / programs /
  credentials / network / project, in green, yellow and red.
- **Data**: dataset table, baseline table (Δt and B⊥ coloured by threshold), baseline network plot,
  stack footprints on a Natural Earth basemap, and the amplitude image of a date when it is
  selected; drag a stack folder in to import it (step 8).
- **Run**: pick a workflow (DInSAR / CCD / amplitude change) and the pairs; the parameter form is
  generated automatically from each step's parameter definition (common items on top, the rest
  under "Advanced"); the command about to run is shown live on the right. **Run** starts it,
  **Stop** first requests cancellation (the current step is recorded as cancelled) and, if nothing
  has stopped within 5 seconds, ends the whole process tree (including SNAPHU).

![Running](assets/tour/dinsar/03_running_light.png)

- **View**: the product tree on the left, two linked image views on the right; colour tables are
  fixed per product type (coherence grey 0–1, displacement symmetric red-blue in mm, red = toward
  the satellite); the full-resolution value, unit and lat/lon are shown under the mouse; the damage
  proxy map can be overlaid, and export is available (the `bosar export` of step 13).

![Result](assets/tour/dinsar/04_result_dark.png)

- **Logs**: one row per run; the record table can be filtered by level / event / step / text; a
  failed run shows a failure card: WHAT (error code and message), WHERE (step, code location,
  file), HINT (what to do), LOG (log file and line number).

![Failure card](assets/tour/logs/02_failure_dark.png)

- **Aux**: the GACOS request card of step 15, with a copy button on every field; "Copy request k"
  copies one batch of dates in the order of the website form; the folder holding the files is
  re-validated automatically whenever it changes. The orbit and DEM cards are enabled in v0.2.0.
- **Settings** (gear icon, top right): theme (dark / light / follow system), compute device
  (auto / CPU / GPU), SNAPHU path, storage mode for new projects, read-only data directory;
  credentials **only show whether they exist**, never their content.

---

## Step 17: Account credentials

Credentials enter by two routes only: `bosar auth set <service>` in the terminal (hidden input, or
`--from-file yourfile.txt`, the file is read once and not copied), or in the GUI
**Settings → Credentials → Set…** (which first prompts you to register, explains where to find
the key, then lets you type it or "import from file"). The value is stored in the system
credential store (Windows Credential Manager / macOS Keychain) and never appears on the command
line, in logs or in release packages. To see the status:

```powershell
bosar auth status
bosar auth services
```

None of the downloads used in these steps need an account: orbits come from local folders and the
SNAP cache, with the ASF public mirror for what is missing; the DEM comes from the AWS public
bucket. A `cdse` (Copernicus Data Space) account is an optional faster source.

## Step 18: Orbit files: local first, then download

```powershell
bosar fetch orbits walk --stack crop_indy_downtown_crop --local-dir <data-root>/05_Auxiliary/03_Orbits --no-download
```

For each date one POEORB covering the acquisition time (±60 s) is chosen (RESORB only when there
is none), looked up first in `--local-dir` (recorded in `project.json`), `BOSAR_ORBIT_DIRS` and the
SNAP cache `~/.snap/auxdata/Orbits/Sentinel-1`; a file found there is referenced in place with its
sha256 recorded; drop `--no-download` and the missing dates are downloaded to `walk/aux/orbits/`.
The project has two stacks (the crop and the full frame), so `--stack` is required; all 5 dates of
this crop are hits locally, 0 downloads.

## Step 19: DEM: local tile mosaic, ellipsoidal height by default

```powershell
bosar fetch dem walk --stack crop_indy_downtown_crop --tile-dir <data-root>/05_Auxiliary/02_DEM/tiles --no-download
```

Finds the 1°×1° GLO-30 tiles for the stack footprint plus 0.1°; when all are present locally they
are mosaicked directly (no network) and written to `walk/aux/dem/glo30_<W>_<S>_<E>_<N>.tif` with a
`.json` of the same name (which tiles were used, sha256, geoid model). The default is
**ellipsoidal height** (GLO-30 is EGM2008 orthometric; the program adds the geoid undulation, here
about −33 m); `--height orthometric` keeps the orthometric height.

## Step 20: Quick coherence preview and baselines from orbits

```powershell
bosar data preview walk --pair 20240821_20240914
bosar data baselines walk --stack crop_indy_downtown_crop --from-orbits
```

The preview gives a coarse coherence map of one pair in a few seconds
(`walk/preview/coh_<pair>.tif`, with Δt and B⊥); in the GUI, select a pair on the Data page and
press **Preview coherence**. `--from-orbits` uses the orbits of step 18 to compute B⊥/B∥ on a
10×10 grid of targets, compares them pair by pair with the TCN values in `.base`, and fills in the
pairs that have no `.base` (method `orbit`). The 4 pairs of the crop all differ by less than 3 m;
the same command on the full stack `gamma_01_IW2` (29 epochs) gives 21 of 25 pairs within 1 m.

## Step 21: GACOS atmospheric correction (`--tropo gacos`)

```powershell
bosar pipeline dinsar walk --stack crop_indy_downtown_crop --pair 20240821_20240914 --looks 2,10 --backend snaphu --tropo gacos --gacos-dir <data-root>/05_Auxiliary/00_GACOS --tag gacos
```

One extra step `tropo_gacos` after `unwrap`: each pixel is sampled bilinearly on the ZTD grids of
the two dates, divided by the cosine of that pixel's incidence angle to give the slant delay,
`φ_tropo = 4π/λ (S_sec − S_ref)` (a larger delay on the secondary = longer range = positive
phase), `unw_tropo = unw − φ_tropo` (the reference point stays 0), and `displacement` switches to
`unw_tropo`. The step summary gives the displacement RMS on coherent pixels before and after the
correction (this pair 6.25 → 5.09 mm; the same pair on the full IW2 30.2 → 22.3 mm). If a date's
file is missing, the time does not match or the grid does not cover the scene, the step raises
E201/E204 naming the date and the file. `bosar aux status walk --for dinsar+gacos` lists in
advance what is missing, what can be fetched automatically (with the command) and what you have to
do by hand.

## Step 22: SBAS network design

```powershell
bosar sbas network walk --stack crop_indy_downtown_crop --max-dt 400 --max-bperp 300 --k 2 --name crop
```

Selects pairs by the Δt / |B⊥| thresholds, then adds for each date the `--k` nearest connections
in time (so gaps stay connected), and reports the connected components, the redundancy (pairs /
dates) and the number of triplets; rejected pairs are recorded with their reason in
`project.json` (`aux.sbas.networks`). Your own `network_design.csv` can be imported with
`--from-csv` (B⊥ taken from the stack's orbital baselines). The 5 dates of the crop: 9 pairs, 1
rejected (|B⊥| 392 m but kept as a sequential connection), 7 triplets, connected. In the GUI,
choose **SBAS prep** on the Run page to design the network and view the network plot (selected
pairs solid, rejected pairs dashed).

## Step 23: Derive the small-baseline interferograms, common reference point, batch unwrapping

```powershell
bosar sbas prep walk --stack crop_indy_downtown_crop --network crop --looks 2,10 --backend snaphu --workers 3 --nproc 2 --tag sbas
```

Step ids carry the network name (`coherence_<pair>_crop_sbas`), so the networks of the two stacks
in one project do not interfere. Four resumable phases: **prepare**: for each pair
`ifg_derive → multilook → coherence` (`ifg_derive` computes the flattened (i, j) pair from the
star-stack `diff(ref,i)`, `diff(ref,j)` and the reference image power; the coherence uses the same
numerator and the two SLC powers); **reference**: among the pixels coherent (≥ 0.3) in every pair,
the one with the highest mean coherence becomes the common reference point (written into the
network record); **unwrap**: SNAPHU for each pair (`smooth` cost), unified reference;
**closure**: see the next step. `--workers 3` runs three pairs in parallel (subprocesses, CPU), and
the concurrent writes to `project.json` are merged by revision number. The 9 pairs of the crop:
prepare about 1 minute per pair, unwrap 1–3 seconds per pair, reference pixel (20, 167).

## Step 24: Triplet closure (B4)

The last phase of `sbas prep` is `closure`; it can also be run on its own:

```powershell
bosar sbas prep walk --stack crop_indy_downtown_crop --network crop --phase closure --looks 2,10 --tag sbas
```

Each closed triangle gets two quantities: the wrapped-phase closure `arg(c_ij c_jk conj(c_ik))`
(phase bias) and the integer closure of the unwrapped phase `round((u_ij + u_jk − u_ik − w)/2π)`
(unwrapping errors); products `closure/wrapped_rms`, `closure/integer_count`; the summary has
per-triplet, per-pair (with a "systematic error" flag) and coherent-pixels-only statistics. The 7
triplets of the crop: median wrapped closure RMS 0.94 rad (0.43–0.52 rad on pixels coherent in all
three pairs), 9–24 % of pixels with non-zero integer closure (2–11 % on coherent pixels; the summer
triplet 20240821-0902-0914 is best, 2.2 %).

## Step 25: Preprocessing with SNAP (requires an installed ESA SNAP)

```powershell
bosar preflight --offline
bosar pipeline preprocess walk --engine snap --product "$DATA\00_RawData\S1A_IW_SLC__1SDV_20240821T234025_20240821T234052_055318_06BEBA_E05B.zip" --product "$DATA\00_RawData\S1A_IW_SLC__1SDV_20240902T234025_20240902T234052_055493_06C53E_B90F.zip" --product "$DATA\00_RawData\S1A_IW_SLC__1SDV_20240914T234026_20240914T234052_055668_06CC28_B2FF.zip" --subswath IW2 --aoi-wkt "POLYGON((-86.30 39.65,-86.00 39.65,-86.00 39.90,-86.30 39.90,-86.30 39.65))" --threads 8 --cache-mb 8192 --tag subset
```

Preflight's P402 reports SNAP's `gpt`, toolboxes and heap memory. The command calls SNAP as a
separate program (no SNAP code is copied or imported): TOPSAR-Split (bursts chosen by the AOI) →
Apply-Orbit-File (the local orbits found in step 18, copied to `walk/snap/userdir`) →
Back-Geocoding (external DEM = the ellipsoidal mosaic of step 19, `walk/aux/dem`) → ESD →
Interferogram (flat-earth + topographic phase, coherence, elevation, lat/lon) → Deburst; the
product is BEAM-DIMAP and is then imported automatically (`data import --reader dimap --ifg-dim`)
as the stack `snap_subset`, which every command from step 8 onward can use. Everything SNAP writes
is under `walk/snap/` and `walk/products/dimap/`; not one file in `~/.snap` is touched. On this
machine: stack 90 s, interferogram 344 s, gpt peak memory 45 GB (the -Xmx132G in `gpt.vmoptions`
allows it). Note: the DEM is mosaicked only for the AOI box, and Back-Geocoding blanks every pixel
without elevation, so the subset has data only inside the AOI box.

## Step 26: Which pairs and pixels are dropped when coherence is insufficient

How good an SBAS result is depends mostly on how trustworthy the unwrapped phase fed into it is.
Bosar makes "dropping" a set of explicit rules, each leaving a record in the command output and in
`project.json`, and each can be loosened or tightened individually:

| Level | Rule | Where to adjust | Where it is recorded |
|---|---|---|---|
| Whole pair | **Empty pair**: coherence is 0 everywhere (the interferogram or SLC of that date is all zeros in the export; W206 at import) | not adjustable | network record `empty_pairs` |
| Whole pair | **Weak pair**: fewer than 5 % of pixels with coherence ≥ 0.4; but each date keeps its best forward and backward connection | `sbas prep --min-coherent-fraction 0.05` (0 = do not drop) | `weak_pairs`, `weak_pairs_kept`, `pair_quality` |
| Whole pair | **Unreliable pair**: in every triplet it takes part in, more than 30 % of coherent pixels have non-zero integer closure (a scene-wide decorrelated or badly coregistered date) | `unw_correct --pair-max-error 0.3` | `unreliable_pairs` in the `unw_correct` summary |
| Pixel | the pair's coherence at this pixel is below the threshold | `pipeline sbas --coh-min 0.3` | `sbas_invert` summary `pair_pixels_dropped.coherence` |
| Pixel | the pixel is not in the unwrapping connected component that holds the reference point | `--any-component` disables this rule | `pair_pixels_dropped.component` |
| Pixel | after closure correction the triplet containing this pair still does not close | `--keep-unclosed` disables this rule | `pair_pixels_dropped.unclosed_triplet` |

A pixel needs at least 2 remaining pairs to get a time series (`--min-pairs`); only when its
network connects all dates into one piece and its temporal coherence is ≥ 0.7 does it enter the
default mask (product `ts_mask`). If the whole-pair rules break the network into several segments
(as happens when all the winter pairs are unreliable), `sbas_invert` reports **W107**: the offsets
between segments are unknown, and the velocity is fitted as "one rate + one intercept per
segment"; to bridge the break, keep more pairs across it (raise `sbas network --k`, lower
`--min-coherent-fraction`, or choose yourself with `sbas_invert --exclude-pairs`). Network design
has two more options: `--sequential-only` (only the k nearest connections in time for each date)
and `--season-months 5-10` (reject pairs that cross seasons, sequential connections excepted).

## Step 27: SBAS time series (`pipeline sbas`)

```powershell
bosar pipeline sbas walk --network crop --tag sbas --tropo gacos --gacos-dir <data-root>/05_Auxiliary/00_GACOS
```

On the network prepared in step 23, in turn: `unw_correct` (corrects 2π unwrapping errors from
closure loops, the phase-closure method of Yunjun et al. 2019, deduplicated by "closure pattern"
so each pattern is solved once) → `sbas_invert` (weighted least squares / minimum-norm solution
of the per-pixel network, Berardino et al. 2002; weights from coherence and the number of looks;
outputs `ts_los` (one band per date, metres, positive toward the satellite), `velocity` (m/yr)
with its standard deviation, `temporal_coherence`, `n_pairs_used`, `ts_rank`, `ts_mask`) →
`ts_correct` (the GACOS slant delay of each date, referenced to the reference point and reference
date; `--deramp` additionally removes a plane per date; `--tropo era5` uses ERA5 pressure-level
data and needs a CDS key) → geocoding (velocity, temporal coherence, time series). Inside the
products everything is metres and metres per year; only the GUI, CSV and summaries switch to
millimetres. The correction method is written into the step id (`ts_correct_crop_sbas_gacos`), so
uncorrected, GACOS and ERA5 results can coexist for comparison. This 5-scene crop has only 9
pairs, and the result only demonstrates the workflow; the 26-scene crop (`data/indy_downtown_ts`,
see the release notes) is where a proper time series appears.

## Step 28: Export for comparison with MintPy (optional)

```powershell
bosar sbas export-mintpy walk --network crop --tag sbas --out walk\mintpy
```

Writes `inputs/ifgramStack.h5`, `inputs/geometryRadar.h5` and a minimal `smallbaselineApp.cfg`
(file formats follow the MintPy manual; no MintPy code is used). MintPy, run as a separate program
on these files (`ifgram_inversion.py inputs/ifgramStack.h5 -w var`), can then be compared with
Bosar on exactly the same input; `--mintpy-legacy-bperp` writes the baselines as the `.base`
values of the export, consistent with your earlier MintPy data set.

## Step 29: Viewing time series, stacking layers and exporting figures in the GUI

`bosar gui walk` → Results page:

- Select `geo_velocity` (the velocity map): in the **Layers** panel at the bottom left choose a
  basemap (default "none"; since v0.4.0 the release no longer connects to any tile server by
  default; the 2016 Sentinel-2 cloudless mosaic is CC BY and can be used directly, OpenStreetMap
  and Esri each have terms of use, and a custom XYZ takes its template, key and attribution in
  Settings); the basemap can be dimmed; each layer has a visibility switch, 0–100 % opacity
  (70 % by default over a basemap), stacking order and a "transparent where coherence / temporal
  coherence is below the threshold" mask; "Add selected as layer" stacks another geocoded product
  selected in the tree. Radar-geometry products are never silently reprojected; instead a
  "Geocode for the map" button runs the `geocode` step.
- Click a pixel on the velocity map: the LOS displacement time series of that pixel (millimetres)
  appears below with its linear fit and rate (mm/yr); several pixels can be clicked, different
  corrections ticked (uncorrected / GACOS / ERA5) and a CSV exported; in the radar-geometry view
  the reference point is marked with a star.
- "Export view…" saves the current view as PNG or PDF: with colour bar, one legend row per layer,
  scale bar, north arrow and basemap attribution; the commands that produced each layer are
  written into the file metadata.

## Step 30: Is the result usable? Quality verdict and data health check

```powershell
bosar sbas quality walk --network crop --tag sbas
```

Every time-series chain (`pipeline sbas`, `pipeline psds`) prints a **quality verdict** when it
finishes: `USABLE` / `MARGINAL` (readable only within the stated limits) / `NOT USABLE` (must not
be interpreted as deformation). The verdict comes from measured metrics, each with a warning code,
the measured value, the threshold and a **concrete remedy**:

| Code | Metric | Marginal | Not usable |
|---|---|---|---|
| W108 | fraction of pixels connected and meeting the temporal-coherence threshold | < 20 % | < 2 % |
| W109 | fraction of dropped interferogram pairs, or dates lost entirely | > 30 % or a date lost | — |
| W107 | network broken into segments | yes | — |
| W110 | velocity spread of the usable pixels | > 4 mm/yr | > 10 mm/yr |
| W111 | fraction of triplets still unclosed after correction | > 15 % | — |
| W112 | median velocity clearly offset from the reference point (a scene-wide ramp or a bad reference point) | yes | — |
| W113 | fraction of pixels with a jump of nearly half a wavelength between adjacent epochs (and from which date it starts) | > 3 % | — |

`bosar sbas quality` also prints a **per-date data health table**: how many pairs each date has,
how many are empty (all zeros), how many too weak, how many judged unreliable by the closure
check, the mean coherent-pixel fraction. A date whose pairs are all empty is a data problem (that
scene is empty in the export; tuning parameters will not help, only re-coregistration or
exclusion); a date whose pairs all fail was decorrelated that day (snow, rain, leaf fall). In the
GUI, the Results page shows the same verdict in a banner above the map.

## Step 31: PS / DS time series (`pipeline psds`)

```powershell
bosar pipeline psds walk --stack crop_indy_downtown_crop --strides 2,10 --workers 3 --backend snaphu
```

Where vegetation is dense, multilooked SBAS keeps few pixels. This chain uses two kinds of
scatterers instead: **distributed scatterers (DS)**: around each pixel, find statistically
homogeneous neighbours (SHP, a GLRT test on amplitude), estimate the N×N coherence matrix over
those neighbours, and estimate the phases of all N dates at once by **phase linking** (EMI);
**persistent scatterers (PS)**: points with amplitude dispersion D_A ≤ 0.25 keep their own phase.
The two are merged into one "hybrid stack", which then goes through the same unwrapping, closure
and inversion as steps 23–27. In order: `slc_flatten` (flattens each SLC with Bosar's own
flat-earth phase; it also scans every date, and **a date with a missing band is detected and
dropped by default**, W207) → `psds_link` (SHP, phase linking, PS selection; 26 scenes of 768×3072
take only a dozen seconds on the GPU) → the interferogram of each pair → unwrapping → closure
correction → inversion → geocoding → quality verdict. Common options: `--shp glrt|ks`,
`--method emi|evd`, `--ps-da 0.25`, `--strides azimuth,range` (decimation of the output grid),
`--ds-tcoh 0.6` (the phase-linking temporal coherence a DS needs; pure noise reaches at most 0.36
on this stack), `--keep-partial-dates`. The 5-scene crop only demonstrates the workflow (with so
few dates phase linking means little); results on the 26-scene test area are in
the release notes.

## Step 32: Classic PS-InSAR as an independent cross-check (`pipeline psi`)

```powershell
bosar pipeline psi walk --stack crop_indy_downtown_crop --name psds --max-arc-m 3000
```

Classic PSI re-implemented after Ferretti et al. 2001 / Kampes 2006, with neither phase linking
nor spatial unwrapping: PS candidates (D_A) → the edges of a Delaunay triangulation → each edge
estimates height error and rate jointly with a periodogram (batched in one matrix multiplication)
→ integration from the reference point along the most coherent path → atmospheric phase screen
estimated from the residuals and removed → final estimate per point. The result is a GeoPackage
point layer (`products/psi_points/`): LOS velocity (positive toward the satellite), height error,
temporal coherence and the displacement of each date. The acceptance threshold is raised
automatically above the "99th percentile of pure noise" for this stack's number of dates (with
few dates, noise alone can produce a high temporal coherence). It reuses the flattened stack
`slc_flatten_psds` of the previous step.

## Step 33: Viewing PS/DS results in the GUI

`bosar gui walk` → choose **PS / DS time series** on the Run page to run the command above
directly; on the Results page, with a PS/DS velocity map selected, tick **PS points** to draw the
persistent scatterers as points (colour = velocity, size = quality) and click one to see its time
series; the quality maps `psds_temporal_coherence`, `shp_count`, `psds_type`, `amp_dispersion` can
be viewed directly. When the network is broken into segments, the time series is drawn as one line
per segment with one offset each (the displacement between segments is unknown).

## Step 34: Downloading raw SLCs from ASF (`fetch slc`)

```powershell
bosar fetch slc --project demo_dinsar --stack gamma_01_IW2 --range 2025-08-01:2026-09-30 --dry-run
bosar fetch slc --project demo_dinsar --stack gamma_01_IW2 --range 2025-08-01:2026-09-30 --range 2023-07-01:2024-06-30 --dest data/raw/s1 --detach
bosar fetch status --dest data/raw/s1
bosar fetch stop --dest data/raw/s1
```

Searches ASF for scenes by the stack's relative orbit, frame and footprint (or
`--aoi "POINT(lon lat)"` + `--relative-orbit`); `--dry-run` only lists the scenes and sizes; the
real download is Bosar's own loop: resumable (Range), verified by size and MD5, one `<name>.json`
provenance record per scene, stops when free space falls below `--min-free-gb` (default 150 GB),
and the second batch starts only when free space exceeds `--continue-if-free-gb`. `--detach` runs
it in the background and continues across sessions; the progress file `fetch_slc_progress.json`
and `fetch_slc.log` are in the destination directory. Earthdata credentials go through `~/.netrc`
or the keychain, never through chat. The Aux page has the same card. The destination refuses a
read-only data root.

## Step 35: Native TOPS coregistration: from zip to stack without SNAP (`pipeline s1-coregister`)

```text
bosar project new demo_native
bosar fetch dem demo_native --bbox -86.52,39.27,-85.06,40.28 --margin-deg 0
bosar pipeline s1-coregister demo_native --product <zip1> --product <zip2> --product <zip3> --subswath IW2 --pol VV --aoi-wkt "POLYGON((-86.30 39.65,-86.00 39.65,-86.00 39.90,-86.30 39.90,-86.30 39.65))" --tag r11
bosar fetch orbits demo_native --stack native_r11 --no-download
bosar run demo_native slc_flatten --step-id slc_flatten_r11 --stack native_r11
```

The first zip is the reference. One step does it all: extract the sub-swath's annotation and image
from the zip into `cache/safe/` (once), build the burst model from the annotation, precise orbits
(those recorded in the project, else the data root / SNAP cache, else the annotation ephemeris with
W301), topo on a grid with the DEM for each reference burst, deramp of each secondary burst →
Knab-window sinc resampling by the orbit + DEM offsets → reramp, ESD in the burst overlaps
iterated to within 0.001 lines, stitching along the overlap mid-lines (deburst), written in the
ISCE `merged/` layout (`--output cint16` halves the space) and imported automatically as the stack
`native_<tag>`. On an RTX 3090 one 1500 × 25000 burst takes under 1 second (CPU 55 seconds).
`products/native/stack/<step>.json` records the burst parameters, the stitching plan, the ESD
table and offsets of each date, and the timings. The comparison with SNAP on the same three scenes
(`scripts/validate_native_tops.py`, `scripts/validate_native_flat.py`) is in
the release notes.

## Step 36: Empty-scene health check at import and per-band quality thresholds

`bosar data import` now scans each date by sampling (16 rows out of every 128): an all-zero date
gets W206, a date whose zero fraction exceeds the "common floor" (the region that is zero on every
date, scene edges and burst gaps; the minimum zero fraction across dates, W208) by more than 2
percentage points gets W207, recorded in the stack record's warnings and in each date record's
`zero_fraction` / `partially_empty` / `empty`; the time-series chains still drop W207 dates by
default. The quality verdict picks thresholds by band: C-band is the default, L-band is a draft
(the millimetre-scale thresholds scaled by the wavelength ratio), and the second output line says
`thresholds: C-band (default)`.

## Step 37: Classic PSI and the point layer in the GUI

`bosar gui walk` → the Run page gains **Classic PS-InSAR (periodogram)** (the command of step 32,
with D_A, point count, longest edge and temporal coherence as basic parameters; in the plan it is
`slc_flatten_psi` + `psi_classic_psi`); on the Results page, with a PSI result selected, tick
**PS points** and the points in the GeoPackage are drawn coloured by velocity and sized by
temporal coherence, by the same mechanism as the PS/DS point layer.

## Step 38: Multi-year native stack: every zip in a directory, cropped to the AOI, resumable

```text
bosar project new demo_multi
bosar fetch dem demo_multi --bbox -86.52,39.27,-85.06,40.28 --margin-deg 0
bosar fetch orbits demo_multi --product <reference zip> --product <other zips…>
bosar pipeline s1-coregister demo_multi --product <reference zip> --products-from <data-root>/00_RawData --products-from data/raw/s1 --subswath IW2 --aoi-wkt "POLYGON((-86.30 39.65,-86.00 39.65,-86.00 39.90,-86.30 39.90,-86.30 39.65))" --crop-wkt "POLYGON((-86.245 39.692,-86.078 39.692,-86.078 39.813,-86.245 39.813,-86.245 39.692))" --drop-cache --tag multi
bosar pipeline psds demo_multi --stack native_multi --workers 6 --tropo era5 --ref-latlon 39.7684,-86.1581 --no-correct --keep-unclosed
bosar pipeline psi demo_multi --stack native_multi --name psds --max-arc-m 3000
```

`--products-from` takes every `S1?_IW_SLC__*.zip` in the folder sorted by date (S1A and S1D alike); bursts are selected by the **intersection** of the AOI polygon with each burst footprint;
`--crop-wkt` writes only the bounding box of the polygon to disk (bursts are still coregistered
whole). One date is processed at a time: open → deramp → geometric offsets → range
cross-correlation check → ESD → stitch → write → close, so memory does not grow with the number of
dates; each date writes a `merged/SLC/<date>/coreg.json` (the signature of the settings), and
**running the same command again processes only the newly downloaded dates** (`n_reused` in the
summary). The default output is CINT16 (`--output cfloat` switches back). `fetch orbits --product`
fetches precise orbits by product name before any stack exists. 53 dates (2024-07 to 2026-07,
including 2 S1D scenes) take about 53 seconds per scene on an RTX 3090. The third line of the
quality verdict gives "measured velocity spread vs the spread expected from the number of dates
and the time span": `sigma_v = sigma_d * sqrt(12 (N-1) / (N (N+1))) / T`.
On long stacks (two years, nearly 200 pairs) add `--no-correct --keep-unclosed`: the closure
correction step corrupts the unwrapped result on a network this large (to be
fixed), and the unclosed pairs are kept and judged by temporal coherence. With that, on two years
of data PS/DS is USABLE (26.5 % of pixels reliable, velocity spread 1.45 mm/yr, expected 1.1),
classic PSI is USABLE too (1.26 mm/yr), and the two chains differ by 0.4–0.6 mm/yr on reliable
pixels. Do not read relative velocities across coherence gaps (for example the two banks of a
river). Time-series projects are best created with `bosar project new --storage-mode full`.

## Step 39: Calibration and terrain flattening (`--calibration`, `--terrain-flatten`)

```text
bosar pipeline s1-coregister demo_native --product <zip1> --product <zip2> --subswath IW2 --bursts 6,8 --output cfloat --calibration sigma0 --terrain-flatten --tag cal
bosar pipeline amplitude demo_native --stack native_cal --pre 20240821 --post 20240902
```

The SLC keeps its DN unchanged; `merged/calibrated/<date>/<date>.sigma0.rdr` (or beta0 / gamma0)
is linear power computed with the SAFE calibration LUT, `gamma0_flat.rdr` = beta0 × area factor
(Small 2011; the factor is computed in radar geometry from DEM facets, equals tan(incidence angle)
on flat ground, and is NaN in layover and shadow), and the factor itself is in
`geom_reference/gamma_flat_factor.rdr`. When a native stack carries calibration layers, the
amplitude-change chain switches automatically to absolute backscatter (`dB (sigma0)`, no more
relative normalisation). The comparison with SNAP's Calibration / Terrain-Flattening:
`scripts/validate_native_cal.py`.

## Step 40: Three sub-swaths and swath merging (`--subswath IW1,IW2,IW3`)

```text
bosar project new demo_full
bosar fetch dem demo_full --bbox -87.65,38.40,-84.001,40.75 --margin-deg 0
bosar pipeline s1-coregister demo_full --product <zip1> --product <zip2> --subswath IW1,IW2,IW3 --tag full --id native_full
```

Each sub-swath is coregistered once (steps `s1_coregister_full_iw1…3`; without `--bursts` /
`--aoi-wkt` that means all bursts), then `s1_swath_merge_full` merges the three stacks onto one
range / azimuth grid: whole-pixel placement (as in ISCE2), cut along the overlap mid-line, no
interpolation at all; the geometry layers are merged the same way, so every pixel carries its own
lat/lon. The `seams` in the summary give the phase, coherence and amplitude step of each seam for
each date. The DEM mosaic is read by window, so even a full scene is never loaded whole into
memory.

## Step 41: Split-spectrum ionosphere estimation (`iono_split`)

```powershell
bosar run demo_full slc_flatten --step-id slc_flatten_full --stack native_full
bosar run demo_full iono_split --step-id iono_full --requires slc_flatten_full --pair 20240821_20240902
```

On the **flattened** SLC stack: the upper and lower thirds of the range spectrum are each
extracted to form sub-band interferograms, the full band is unwrapped only once, the dispersive
term is computed from the two sub-band phases (Gomba 2016), and a coherence-weighted Gaussian
low-pass is applied. The output is `iono_phase/<pair>` (the ionospheric phase at the carrier
frequency, radians, multilook grid); the summary has the plane slope of the unwrapped phase before
and after correction. Noise is amplified about 120 times, hence the default 64 × 256 looks. The
constant term cannot be determined (like every interferometric phase, it is relative).

## Step 42: GUI: the Coregister workflow and download batches

`bosar gui demo_multi` → **Coregister (Bosar)** on the Run page: Engine `bosar` (the native chain,
the command of step 38) or `snap` (the SNAP bridge of step 25); ticking "all three sub-swaths"
gives step 40; the form has output type, calibration and terrain flattening. The
**Sentinel-1 SLC scenes (ASF)** card on the Aux page now lists the progress of each batch, the
file being transferred and the remaining time estimated from the rate of the last minute;
`bosar fetch slc --parallel 3` downloads in parallel, and scenes interrupted by the network are
retried automatically on a later attempt.

## Step 43: Temporal reference date and outlier dates

```powershell
bosar pipeline sbas demo_multi --network psds --no-correct --ref-latlon 39.7684,-86.1581 --tropo era5
bosar pipeline sbas demo_multi --network psds --tag ex5 --no-correct --ref-latlon 39.7684,-86.1581 --fit huber --exclude-dates 20230803,20240330,20240622,20250325,20250816
```

Without `--ref-date`, the zero date of the series is no longer the first scene but follows the
"common-mode median" rule: for each date take the spatial median of the good pixels (the amount by
which the whole scene moves relative to the reference pixel, mostly atmosphere) and pick the date
closest to the median of those medians, which is never an outlier day. The summary records
`ref_date_rule`, `common_mode_mm`. W117 names the dates that "deviate from the fitted line by more
than 3 robust standard deviations on more than 20 % of pixels"; `--exclude-dates` removes them with
all their pairs, `--fit huber` estimates the velocity with a Huber estimator, and the quality
report prints both the least-squares and the Huber spread. `--tag` can now name a variant of the
time-series part only, with the pair products reusing the network's own.

## Step 44: ΔSTEC implied by the range shifts

```powershell
bosar aux range-shift demo_multi --stack native_multi --ionex-dir data/aux/ionex --write
bosar sbas quality demo_multi --network psds
```

For each date: the shift predicted by the ERA5 troposphere, the residual, and the slant TEC
difference obtained by treating the residual as ionospheric group delay (one 2.33 m pixel
≈ 169 TECU); when IONEX maps are present the GIM value is given alongside. `--write` writes them
into each date's `coreg.json` and the coregistration step summary, and the per-date table of
`sbas quality` gains three columns `shift[px]`, `dSTEC[TECU]`, `GIM[TECU]`.

## Step 45: Ionospheric model correction (optional)

```powershell
bosar pipeline sbas demo_multi --network psds --iono --iono-model plane
bosar pipeline psds demo_alos --stack alos_mx --network l --iono --iono-looks 32,32
```

Without `--iono` nothing happens. With it, each interferogram pair gets one split-spectrum
estimate and a model fit (C-band defaults to `plane`, L-band to `filtered`), and the model is
subtracted at the read-in stage of the inversion; at the end of the chain it prints the model
span, the number of W220 pairs and the triplet closure. Every model passes a plausibility gate
first (span, gradient, triplet closure; `--no-iono-gate` switches it off): a model that fails
is skipped and counted (W227), so a bad estimate never enters the inversion.

What the correction is worth, measured on real stacks (0.4.1): at C band (Sentinel-1,
Indianapolis, 88 winter dates) no measurable benefit - the gate passes a handful of pairs and
the velocities change by less than their own noise; at L band (ALOS-1, Mexico City) the gate
keeps about half of the models and the product is unchanged within 0.01 mm/yr. The gate is
on by default because a `filtered` model can follow the deformation it sits on, and that is
what the gate's span and closure rules catch. Use `--iono` with the gate, compare the velocity
map with and without it, and keep the run whose residuals and landmark series you can defend;
it stays opt-in.

NISAR records two frequency bands in one granule (mode `0505`: 1221.5 MHz on frequency A,
1236.5 MHz on B, 5 MHz each, one grid). Coregister the second band as its own stack
(`pipeline stripmap-coregister … --reader nisar --frequency B --tag b`) and name it:

```text
bosar pipeline sbas demo_nisar --network l --iono --iono-band-stack stripmap_b
```

The ionosphere then comes from the two full bands instead of the outer thirds of one (the
`bands` source of the `iono_split` step): 15 MHz between the carriers against 3.3 MHz, a
noise gain of 58 instead of 259 - four to five times less noise for the same looks. The two
stacks may carry different polarisations (HH on A, VV on B in that mode); each band's
interferogram is formed within itself. The estimator is verified on synthetic bands; on the
provisional `0505` granules of 2026 (track 58, frame 53) frequency B held no signal, so look
at `band.coherence_median` in the `iono_split` summary before trusting a run.

## Step 46: Sequential phase linking for long series and the star-unwrapping experiment

```powershell
bosar pipeline psds demo_multi --stack native_multi --network psds_seq --method sequential --ministack 15
bosar pipeline psds demo_multi --unwrap star
```

`sequential`: one ministack of 15 scenes at a time, each linked on its own, with compressed SLCs
chaining the datums together; the matrix never exceeds "ministack + number of earlier ministacks"
dates (N/L drops from 0.9 to 0.2); the summary reports `n_over_l_median`. `--unwrap star`: only the
star pairs with the first scene are measurements, the remaining pairs are derived from the star
(closure identically zero), and independently unwrapped adjacent pairs are used only to vote on
integer-cycle errors.

Measured on 88 scenes: `sequential` links 7 times faster and selects 68 % more DS,
doubling the product coverage (73 % vs 37 %), but the velocity spread goes from 0.54 to
0.80 mm/yr and 6 % of pixels show integer-cycle jumps: interferogram pairs derived from linked
phases close by construction, so the inversion's temporal coherence is identically 1.0 for them
and cannot act as a gate. The default remains `auto`; `sequential` is an option, to be re-evaluated
in v0.4.0 once the linking coherence is used as the mask.
`--unwrap star` is also a negative result on 88 scenes: the star pairs centred on the first scene
span up to 1171 days, the far pairs carry whole-scene integer-cycle errors, and the vote of three
adjacent pairs per scene cannot hold them (five dates had 91–98 % of pixels changed), velocity
spread 3.6 mm/yr. The default remains `pairs`.

## Step 47: ALOS-1 / ENVISAT / ERS / NISAR readers and the stripmap coregistration chain

```text
bosar fetch slc --mission alos --path 186 --frame 370 --flight-direction ascending --range 2007-01-01:2011-12-31 --dry-run
bosar project new demo_alos --storage-mode full
bosar fetch dem demo_alos --bbox -99.30,19.15,-98.85,19.60 --tile-dir data/aux/dem_tiles
bosar pipeline stripmap-coregister demo_alos --product A.zip --product B.zip --reader alos --crop-wkt "POLYGON((...))" --id alos_pair
bosar sbas network demo_alos --stack alos_pair --name pair --max-dt 400 --max-bperp 5000
bosar run demo_alos slc_flatten --step-id slc_flatten_alos_pair --stack alos_pair --mode orbits
bosar sbas prep demo_alos --stack alos_pair --network pair --flat-step slc_flatten_alos_pair
```

ALOS-1 PALSAR L1.1 (CEOS, ASF's zip read directly), ENVISAT ASAR IMS and ERS IMS (Envisat format,
`--reader asar` / `ers_envisat`), and NISAR RSLC (HDF5, no real data seen yet) are all read into
the same `StripmapScene`; the stripmap coregistration chain carries the Doppler centroid (the
geometry uses the Doppler term of `rdr2geo`/`geo2rdr`, resampling demodulates first and
remodulates after) and writes the same ISCE directory as the TOPS chain. A native stack has no
stored interferograms, so pairs must be flattened first and derived with `--flat-step`; with three
or more scenes go straight to `pipeline psds`. One pair of each of the three sensors was run over
Mexico City; the 16-scene ALOS series
(`pipeline psds demo_alos --stack alos_mx --network l --k 3`, then `pipeline sbas --tag ex --ref-latlon 19.342,-99.088
--exclude-dates 20100522 --fit huber`) gives Nezahualcóyotl −223 mm/yr (LOS, roughly −290
vertical), the airport −192, the volcanic-rock reference point −4 ± 3, consistent in pattern and
magnitude with Chaussard 2014. Two cautions: the default reference pixel (the best DS) lands in
the subsidence basin, so point `--ref-latlon` at stable ground; and the W110/W113 of the quality
verdict are designed for stable areas and will judge the deformation itself NOT USABLE on a
30 cm/yr basin.

## Step 48: Comparing two chains, the 4K tour

```powershell
bosar compare demo_multi --list
bosar compare demo_multi products/geo_velocity/geocode_velocity_psds_era5.tif ps:psds_link_psds --out compare_out
python scripts/gui_tour.py --project tour/indy_crop --size 1920x1080 --scale 2
```

`bosar compare` is the command-line version of "Compare two chains" on the Results page; the tour
screenshots are rendered at 2× scale to 3840 × 2160, each step gains one animated "where to click"
hint, and the DInSAR demo is additionally saved as a 4K MP4.

## Current limitations and what comes next

- Input can be a GAMMA/StaMPS stack exported by SNAP, SNAP-bridged preprocessing (step 25), or,
  since v0.3.0, Bosar's own native TOPS coregistration (steps 35, 38–40: multi-year stacks,
  calibration, three-swath merging).
- There are three time-series chains: SBAS (steps 22–27), the PS/DS hybrid stack (step 31) and
  classic PSI (step 32). On this vegetated C-band area the velocity noise is of the order of
  2–5 mm/yr, and one year of data cannot resolve millimetre-level deformation; the quality verdict
  tells you so explicitly.
- Split-spectrum ionosphere estimation is wired into the time-series chains (step 45, optional);
  the ALOS-1, ENVISAT and ERS readers and the stripmap coregistration chain ran on real data in
  v0.4.0 (step 47), NISAR only on synthetic data; offset tracking and speckle filtering are in
  v0.3.0; the installers in v0.4.0.

## Step 49: Quality verdict for deforming areas, linking-coherence gate, two safeguards on downloads

```powershell
bosar pipeline sbas demo_alos --network l --tag ex2 --area deforming --exclude-dates 20100522 --fit huber --no-geocode
bosar sbas quality demo_alos --network l --tag ex2
bosar sbas quality demo_multi --network psds --step ts_correct_psds_era5 --area deforming
bosar pipeline sbas demo_multi --network psds_seq --tag gate --link-coherence-min 0.7 --tropo era5 --no-geocode
bosar fetch dem demo_alos --bbox -99.30,19.15,-98.85,19.60 --timeout-s 120
```

- `--area stable | deforming | auto`: the stable-area rules (the default) judge a 30 cm/yr
  subsidence basin NOT USABLE, because the velocity spread is itself deformation and so are the
  integer-cycle steps between adjacent dates. In `deforming` mode W110 looks at the residual
  spread after subtracting a 1 km smoothed field from the velocity, W113 at cycle slips relative
  to each pixel's fitted line, W114 at the detrended common-mode steps, and W112 is no longer
  reported; when no reference point is given, it moves automatically to the cell with the densest
  coherent neighbourhood inside the "most stable quintile" of the velocity field
  (`--stable-end max` for subsidence scenes, `min` for uplift). `auto` switches to `deforming`
  when the spread exceeds 3 times the stable-area expectation. The 16-scene Mexico City series is
  thereby judged USABLE, with the reference point landing automatically on the volcanic rock of
  Cerro de la Estrella.
- Two levels of W117: a date with more than 20 % outlier pixels is only recorded (marked
  `(info)` in the report), ≥ 35 % is marginal, and only more than two marginal dates lower the
  verdict; `sbas quality` now re-judges the stored metrics against the current thresholds,
  `--step` names the step to report on, and `--area` applies a different rule set to the same
  product.
- `--link-coherence-min 0.7`: the reliable mask of PS/DS products is gated once more by the
  temporal coherence of phase linking; a sequentially linked stack has an inversion coherence
  identically 1, so this gate is mandatory, and `pipeline psds --method sequential` therefore
  carries 0.7 by default (`--link-coherence-min 0` turns it off). On the three-year stack the
  gate keeps 82.5 % of pixels, the verdict is still marginal, and the landmark velocities differ
  from the ungated product by less than 0.15 mm/yr: the gate replaces the definition of
  "reliable", not the product.
- `fetch dem --timeout-s` (the only path since v0.4.0): downloads the missing GLO-30
  tiles straight from the Copernicus public bucket into `<project>/aux/dem/tiles/` and then
  mosaics them; `fetch slc` checks an existing file by MD5 once and afterwards by a tail hash (the
  last 1 MiB) for a quick check, no longer by size alone.

## Step 50: The installed version: starting from .exe / .dmg without the source

Since v0.4.0 Bosar has installers; the commands below run on the **installed version** (not this
development checkout), so they are written as plain text blocks and `check_walkthrough.py` does
not execute them.

1. Download from [Releases](https://github.com/HU-Jiashu/bosar/releases): on Windows
   `bosar-<version>-win-x64-setup.exe` (per-user install, no administrator needed; tick "Add the
   bosar command line to the user PATH" in the wizard), on macOS `bosar-<version>-mac-arm64.dmg`
   (Apple silicon only; on first launch right-click → Open, or
   `xattr -dr com.apple.quarantine /Applications/Bosar.app`).
2. Open a new terminal (so PATH takes effect) and check the version and environment:

```text
bosar version                      # with the build id: bosar 0.4.0b0 (build 2026…-win-x64 …)
bosar preflight --offline          # P305 shows the build record; P401 reports SNAPHU as "no CS2 solver (MST init)"
```

3. With no data at all, run the demo first (a synthetic pair of images, project creation, import,
   the full DInSAR chain, about a minute):

```text
bosar demo my_demo                 # 8 steps done; my_demo/project is an ordinary project that opens in the GUI
bosar-gui my_demo/project          # or open Bosar from the Start menu / Applications
```

4. Machines with an NVIDIA GPU: the GPU is a plug-in, installed once (about 1.5 GB, CuPy and the
   CUDA 12 runtime libraries from PyPI, no pip needed):

```text
bosar gpu install                  # or --no-ctk (when a CUDA 12 toolkit is already installed)
bosar preflight --offline          # P202 gpu.plugin ok, P201 gpu.backend shows the graphics card
```

   Apple-silicon Macs have no CUDA; Bosar runs on the CPU (NumPy).
5. From there, the workflow of steps 1–10 is exactly the same on the installed version
   (`bosar project new`, `bosar data import`, `bosar pipeline dinsar …`); PS-InSAR (the
   `pipeline psi` of step 32) and two-scene differential interferometry are included as well. The
   installed version's SNAPHU has no CS2 solver; unwrapping uses the MST initialisation, which
   is the default everywhere since 0.4.1 (`init: mst` in the step summary) and the same
   optimisation problem started from a different point; if you need MCF initialisation, use the
   CS2 build from the source checkout (`packaging/snaphu/build.ps1`) with `unwrap.init=mcf`.
6. Licence: the "About Bosar" card on the Settings page shows the licence line (PolyForm
   Noncommercial 1.0.0; contact the author for a commercial licence) and three files
   (Licence… / Notice… / Third-party licences…); the same texts are in `_internal/licenses/` in
   the installation directory.

## Step 51: ALOS-2 PALSAR-2 reader and JAXA's free samples

```powershell
bosar fetch slc --mission alos2 --sample list
bosar fetch slc --mission alos2 --sample 730_greenland
bosar project new demo_alos2 --storage-mode full
bosar fetch dem demo_alos2 --bbox -71.5,77.4,-67.0,78.5 --tile-dir data/aux/dem_tiles
bosar pipeline stripmap-coregister demo_alos2 --product data/raw/alos2/ALOS2150521570-170307 --product data/raw/alos2/ALOS2152591570-170321 --reader alos2 --crop-wkt "POLYGON((-70.1 77.85,-69.1 77.85,-69.1 78.05,-70.1 78.05,-70.1 77.85))" --id alos2_pair
```

ALOS-2 L1.1 CEOS products are read by the same `ceos_alos` reader (told apart by the scene id
`ALOS2…`): the mode comes from the product id (the FBS/FBD/FBQ, HBS/HBD/HBQ and UBS/UBD stripmap
modes are readable; spotlight SBS and ScanSAR are recognised and refused by name), the 544-byte
line prefix carries microsecond time stamps, and the starting slant range is taken from the line
headers rather than the leader's range gate (which on ALOS-2 is not the delay to the first
sample). JAXA's 22 free sample sets can be fetched by anonymous FTP (`--sample list` lists them);
ASF's ALOS-2 collection currently holds only ScanSAR (30–60 GB per scene). The result of the
Greenland FBS pair (2017-03-07 / 03-21, 14 days) through the stripmap coregistration chain is in
the v0.4.0 release notes.
