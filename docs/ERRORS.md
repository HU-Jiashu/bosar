# Error, warning and preflight codes

Every failure in Bosar answers five questions on one screen: **what** (message + code), **where**
(project → run → step → function → tile window → file/dataset → parameter), **why** (expected vs
actual), **next** (hint + link to this page) and **where to look** (run-log path + record `#seq`).

Codes are stable across versions: once a code is published here it is never reused for a different
meaning. `tests/test_errors_catalogue.py` keeps this file, `src/bosar/errors.py`, the warning
and preflight registries and the exit-code table in sync.

## How a code appears

| Place | Form |
|---|---|
| Exception text | `window_coherence(): argument 'cpx_sec' has shape (512, 500), expected (512, 512) [E301]` |
| Run log (JSONL) | `step_failed` record → `error.code`; `warning` records → `code`; every preflight check → `code` |
| Human mirror (`.log`) | `#000057 … ERROR step_failed step=dummy_001 code=E301 ShapeError …` |
| CLI | header line, WHERE table, HINT line, `→ docs/ERRORS.md#e301` |
| `project.json` | `steps[].error = {type, code, msg, where, hint, log_seq}` |
| Run report (`logs/run_<id>.md`) | section `## Failure — E301 ShapeError (record #57)` |

## Exit codes

| Exit | Meaning | Error codes |
|---|---|---|
| 0 | success | — |
| 1 | unexpected error outside a step | E000, E001 |
| 2 | usage error (click) or invalid CLI parameter / unknown step kind | E101, E102 |
| 3 | preflight blocked the run | E701 |
| 4 | step failed; the failure record was written | E801, E802 |
| 5 | project, configuration or input file error before the run started | E103, E104, E105, E107, E200, E201, E203, E204, E205 |
| 130 | cancelled (Ctrl-C); record written, status cancelled | E803 |

## Families

`E0xx` internal · `E1xx` configuration / project file · `E2xx` inputs · `E3xx` array / kernel entry ·
`E4xx` backend / memory · `E5xx` external tools · `E6xx` storage · `E7xx` preflight · `E8xx` runner ·
`E9xx` numerical · `Wxxx` warnings (same hundreds) · `Pgnn` preflight checks (`g` = group).

Foreign exceptions are classified by `errors.classify()` in this order: package error →
Windows `winerror` (206 → E604, 3/2 → E201, 5 → E602, 32 → E605, 112 → E603) → `errno`
(ENOSPC → E603, ENAMETOOLONG → E604, EACCES/EPERM → E602) → exception module (`pydantic` → E101,
`cupy` → E401/E402/E403, `numpy.linalg` → E901, `subprocess` → E501/E503) → `MemoryError` → E404 →
`KeyboardInterrupt` → E803 → builtin `FileNotFoundError` → E201, `PermissionError` → E602 → E000.
Python folds WinError 206 and 3 into `FileNotFoundError` and 5 and 32 into `PermissionError`, and the
`strerror` text is localised, which is why the number is checked first.

## Error codes (E)

### E000 BosarError
Raised by: the base class, and the code given to any foreign exception that no rule matches.
Meaning: unclassified failure. Hint: re-run with `-v`; attach the run log when reporting.

### E001 InternalError
Raised by: library code in place of a bare `assert`. Meaning: an invariant the package guarantees was violated — a bug.

### E100 ConfigError
Family base for configuration and project-file problems.

### E101 ParamError
Raised by: step parameter validation (pydantic) and CLI option parsing. Meaning: one parameter is wrong; `where.param` is the dotted field path, `param.expected` the validator message, `extra.errors` the full list. Guards against unit mistakes. Also raised by the ALOS-1 / ALOS-2 PALSAR L1.1 reader (`data/ceos_alos.py`) for several L1.1 products in one folder or zip (two products extracted into one folder, or a zip holding two): the members of different products are never mixed, so the folder or zip itself is refused (`where.param` = `path`, the message lists the products); name one of the product's files (its `LED-` or `IMG-` file), which opens that product, or extract every product into a folder of its own. Also raised by `pipeline stripmap-coregister` (without `--force`) when its step - `stripmap_coregister_<tag>`, `stripmap_coregister_native` without `--tag` - is already `done` at the current step version with its products on disk but was recorded with other products, another reader, another crop window or (only when `--pol` is given) another polarisation: the Runner would skip such a step (W101) and the command would import the old stack again, under a new `--id` too, so it refuses instead. `where.param` names the first differing parameter with its recorded (`expected`) and requested (`actual`) value, `extra.changed` lists all of them; `--tag <name>` keeps both results (step `stripmap_coregister_<name>`), `--force` re-runs the step with the new parameters. The same parameters pass (the step is skipped and its stack re-imported). The `stripmap_coregister` step itself raises it when the opened scenes do not share one polarisation (`where.param` = `products`, the message names every date with its polarisation: a stack is coregistered in one polarisation - list products of one polarisation, or name one that every product holds with `--pol`), and when `--pol` names a polarisation that the scene of a single-polarisation reader does not hold (`where.param` = `pol`).

### E102 UnknownStepError
Raised by: `pipeline.registry.get_step`. Meaning: the step kind is not registered; the message lists the known kinds.

### E103 ProjectFileError
Raised by: `project.store` and `Project.step()`. Meaning: project directory or step id problem (e.g. unknown step id, listing the known ids).

### E104 ProjectCorruptError
Raised by: `project.store.load_project`. Meaning: `project.json` is not valid JSON; `extra.line/column/snippet` locate the damage; restore from `project.json.bak`.

### E105 ProjectSchemaError
Raised by: `project.store.load_project`. Meaning: the file does not match the schema (every failing field is listed) or its `schema_version` is newer than the software.

### E107 DependencyError
Raised by: the Runner while resolving `requires`. Meaning: a required product kind is not available from a `done` step.

### E310 ChainUndeclaredError
Raised by: the Runner before a time-series step (`psds_link`, `psds_pairs`, `pair_batch`, `closure`, `unw_correct`, `sbas_invert`, `ts_correct`, `psi_classic`) in a `storage_mode=minimal` project that no declared plan names. Meaning: the step belongs to a multi-command chain whose intermediates minimal storage would collect too early. Remedy: `bosar project new --storage-mode full`, or the chain command (`sbas prep`, `pipeline sbas | psds | psi`), which declares its steps.

### E200 InputError
Family base for input problems.

### E201 MissingInputError
Raised by: the Runner, `core._check.check_path`, readers. Meaning: a file or directory named in WHERE does not exist.

### E203 UnreadableInputError
Raised by: `data.raster` (rasterio/GDAL failures). Meaning: the file exists but cannot be read; the GDAL message is the cause.

### E204 ImplausibleMetadataError
Raised by: `data.model.check_plausible` at every reader exit when a parsed value is outside the physical range: wavelength ∉ [0.02, 0.35] m (unit slips: SNAP MHz, GAMMA GHz), incidence ∉ [15°, 65°], slant range ∉ [500, 1500] km, |B⊥| ≥ 5 km, or a scene shape that differs from the stack geometry. WHERE names the file, the field, the expected range and the actual value. Also raised by the ENVISAT / ERS reader (`data/asar.py`) when a precise orbit file is more than 1 km from the product's own state vectors at mid scene - not this product's orbit (see W223) - and by the ALOS reader for an ALOS-2 observation-mode code it does not know.

### E205 MetadataError
Raised by: readers. Meaning: a required metadata key is absent (`where.dataset` names the key). Guards against metadata unit and sign traps. Since: v0.1.0 (class), raised from v0.1.0. Also raised by the ALOS PALSAR L1.1 reader (`data/ceos_alos.py`) for an ALOS-2 PALSAR-2 product it does not serve, named by its product id: a processing level other than 1.1 (`where.param` = `product_level`), a spotlight (SBS) or ScanSAR (WBS / WBD / WWS / WWD / VBS / VBD) product, and a product with one image file per scan whatever its product id says (`where.param` = `mode`). The message names the mode and its kind; these are not stripmap scenes, and the hint lists the stripmap modes the reader takes (UBS / UBD, HBS / HBD / HBQ, FBS / FBD / FBQ). An observation-mode code the reader does not know at all is E204.

### E300 ArrayError
Family base for kernel-entry checks (`core._check`).

### E301 ShapeError
Raised by: `check_array`, `check_shapes_match`, `apply_tiled`. Meaning: the named argument has the wrong shape; the message names the partner argument it must match.

### E302 DTypeError
Raised by: `check_array`, `data.raster.RasterWriter`. Meaning: wrong dtype (complex64 for phasors, float32 for phase/coherence — `np.angle` on a float array is silent).

### E303 NDimError
Raised by: `check_array`. Meaning: wrong number of dimensions.

### E304 ValueRangeError
Raised by: `check_array(finite=True, min_value, max_value)`, `check_scalar`. Meaning: non-finite values or a value outside the allowed range/choices.

### E305 EmptyArrayError
Raised by: `check_array`, `data.raster.array_stats` consumers. Meaning: zero-size array or no valid pixel.

### E306 WindowSpecError
Raised by: `core.tiling.Tiler`, `check_pair`. Meaning: invalid `(rows, cols)` tile/halo/window.

### E400 BackendError
Family base for CPU/GPU backend problems.

### E401 GpuOutOfMemoryError
Raised by: classification of CuPy `OutOfMemoryError` (and `apply_tiled`). Meaning: the GPU allocation failed; the hint carries the current tile and free memory.

### E402 KernelCompileError
Raised by: classification of CuPy `CompileException`. Meaning: NVRTC could not compile a kernel — usually the CUDA headers are missing (`pip install "cupy-cuda12x[ctk]"`).

### E403 CudaRuntimeError
Raised by: classification of CuPy runtime/driver errors. Meaning: driver/runtime mismatch or device error.

### E404 HostOutOfMemoryError
Raised by: classification of `MemoryError` (host). Meaning: RAM allocation failed; retry with a smaller tile.

### E500 ExternalToolError
Family base for subprocess tools (SNAPHU).

### E502 ToolNotFoundError
Raised by: binary discovery (preflight `binaries`). Meaning: no usable binary found in the discovery order `BOSAR_<NAME>_EXE` → bundled → PATH → package → fallback.

### E510 SnapNotFoundError
Raised by: the SNAP bridge (`external/snap`) and preflight P402 when no `gpt` is found (`BOSAR_SNAP_GPT` → PATH → typical installs).

### E511 SnapRunError
Raised by: `external/snap/run.py` when `gpt` exits non-zero, is cancelled or times out; `extra` carries the argv, exit code, duration and the last Java exception; the hint is matched on that exception (heap, orbit, DEM, unknown operator, missing file).

### E512 SnapOutputError
Raised by: the SNAP Steps when `gpt` exited 0 but the expected BEAM-DIMAP product is absent or empty.

### E600 StorageError
Family base for filesystem problems.

### E601 WriteError
Raised by: writers. Meaning: a file could not be written.

### E602 PermissionDeniedError
Raised by: classification of WinError 5 / EACCES / EPERM, `safe_unlink`. Meaning: permission denied.

### E603 DiskFullError
Raised by: classification of WinError 112 / ENOSPC, preflight disk check. Meaning: no space left.

### E604 PathTooLongError
Raised by: classification of WinError 206 / ENAMETOOLONG, preflight path check. Meaning: the path exceeds the platform limit.

### E605 FileLockedError
Raised by: `utils.fs.replace_with_retry`, `safe_unlink`. Meaning: another process holds the file (WinError 32, or 5 on some volumes); the message counts the attempts.

### E606 AtomicSaveError
Raised by: `utils.fs.atomic_write_text`. Meaning: the temp-file/replace sequence failed; the previous file is intact.

### E607 OutputMissingError
Raised by: the Runner after `Step.run`. Meaning: a declared product was not written.

### E701 PreflightError
Raised by: the Runner / CLI when a blocking preflight check fails (`extra.checks` lists the P-codes).

### E801 StepFailedError
Raised by: `Runner.run` after persisting the failure record (`__cause__` is the original exception).

### E802 StepInterruptedError
Recorded by: the Runner when a step is found `running` without a `run_end` in its log (process killed, drive unplugged); the step becomes `failed` and is re-executed.

### E803 StepCancelledError
Raised by: the Runner on `KeyboardInterrupt`; status `cancelled`.

## Reserved error codes (documented, not yet raised)

### E501 ToolExitError (reserved)
External tool exited with an error; `extra.returncode/argv/stderr_tail`. Classification of `subprocess.CalledProcessError` already yields this code. Planned for the unwrapping step.

### E503 ToolTimeoutError (reserved)
External tool exceeded its time limit. Planned for the unwrapping step.

### E804 WorkerCrashedError (reserved)
A worker process died (`BrokenProcessPool`). Planned for multi-process execution.

### E900 NumericalError (reserved)
Family base for numerical failures.

### E901 SingularMatrixError (reserved)
`numpy.linalg.LinAlgError`; the network/design matrix is singular. Planned for the SBAS inversion.

### E902 NonFiniteResultError (reserved)
A kernel produced NaN/Inf where finite values were required. Planned for the DInSAR kernels.

### E904 NoCandidatesError (reserved)
Zero PS candidates after thresholds. Planned for the PS chain.

## Warning codes (W)

Emitted as `warning` records in the run log; they never stop a run.

### W000 CapturedPythonWarning
A Python `warnings` message raised inside `Step.run`. Warnings whose file lies inside this package or a `tests/` tree are recorded one by one (`category`, `filename`, `lineno`) and counted in `step_end.summary.n_warnings`. Third-party warnings (site-packages: CuPy `compiler.py` EncodingWarnings, NumPy deprecations) are not recorded individually: they are counted per module into one W000 record (`detail.third_party = {module: count}`) and into `step_end.summary.n_warnings_third_party`.

### W101 StepSkipped
The step was `done` with existing outputs and the same version; nothing was re-run (`--force` overrides). The parameters are compared but do not decide: when the requested parameters differ from the recorded ones, the message names the differing keys and the record carries them in `detail.changed_params` (null when nothing differs); the recorded result is still kept and the step is still skipped. Re-run with `--force`, or give the step another id to keep both results. `pipeline stripmap-coregister` refuses such a skip instead (E101): its old stack would be imported again.

### W102 ParamDefaulted
A parameter fell back to its default because the given value was empty.

### W103 VersionUnknown
The package version is the fallback `0.0.0` (installed without git history); set `SETUPTOOLS_SCM_PRETEND_VERSION` or install from a checkout.

### W104 InterruptedStepMarkedFailed
A `running` step from a crashed run was diagnosed (E802) and marked `failed` before this run continued.

### W105 LegacyNameDeprecated
A name from before the rename to Bosar was read: an environment variable with the
old prefix (read only while the `BOSAR_*` variable of the same suffix is unset), raster tags in the
old GDAL metadata namespace, or a product reference / `crop.json` whose `format` carries the old
name. The old names are listed in `src/bosar/_legacy.py`; nothing is written under them. Rename the
variable or re-run the step that wrote the file; `bosar preflight` lists old-prefix variables
(check `system.legacy_env`). Support ends in 0.2.0.

### W106 CcdOnSlcBoxCoherence
The `ccd` step read a coherence product whose `estimator` tag is `slc-box` (the author's MintPy
recipe: a full-resolution box larger than the looks, then the block mean). Neighbouring looked
pixels then share samples, so `ccd_z` is spatially correlated (null-case Moran's I ≈ 0.37 instead
of < 0.1) and detections reach about one looked pixel beyond a real change (precision ≈ 0.72 on
the injected patch, recall 1). `pipeline ccd` therefore defaults to `--recipe looks`; the warning names the pairs. Re-run the coherence steps with `--recipe looks` (a
`--tag`) when the statistics must be pixel-independent.

### W107 SbasNetworkSplit
`sbas_invert` found that the pairs left after the pair-level rules (empty, weak and unreliable pairs) no longer connect all the dates: the network has two or more parts and the offset between them is unknown for every pixel. The time series is still written (zero velocity across the gap, the minimum-norm solution), the velocity is fitted with one common rate and one offset per part, and `ts_mask` counts a pixel as connected when its network is connected inside every part. To bridge the gap, keep more pairs: design the network with more links across the period (`sbas network --k`, `--max-dt`), lower `sbas prep --min-coherent-fraction`, raise `unw_correct --pair-max-error`, or name the pairs to exclude yourself with `sbas_invert --exclude-pairs`.

### W108 LowUsableFraction
The **quality verdict** of a time-series chain (`core/sbas/quality.py`). `sbas_invert`, `ts_correct` and the PS/DS chain judge what they measured and write `summary.quality = {verdict, findings, indicators}`; every finding is logged under its code with the measured value, the threshold and a remedy, the CLI prints the verdict after the chain and the Results page shows it above the map. Verdicts: `usable` (no finding), `marginal` (read the result only with the stated limits), `not_usable` (do not interpret as deformation).

| code | indicator | marginal | not usable | usual remedy |
|---|---|---|---|---|
| W108 | fraction of the image that is connected with temporal coherence above the threshold | < 20 % | < 2 % | PS / DS chain, Goldstein filter before unwrapping, fewer looks, a smaller area |
| W109 | share of the designed pairs left out (empty, weak, unreliable), or a date without pairs | > 30 % or any lost date | - | `bosar sbas quality` per-date table; drop or re-coregister the date; shorter links or a season rule |
| W110 | standard deviation of the velocity over the good pixels | > 4 mm/yr | > 10 mm/yr | longer series, tropospheric correction, deramp, an independent chain |
| W111 | pair-pixels in triplets that do not close after the correction | > 15 % | - | filter, more looks, mask before unwrapping, shorter baselines |
| W112 | median velocity of the good pixels, when larger than 3 mm/yr and than the spread | yes | - | before deramping: `--deramp`, a reference inside the area (`--ref-latlon`); after deramping the reference pixel itself is off: another reference |
| — | `sbas quality --area deforming`: W110 judges the spread of the velocity residual about a smooth field (`smooth_km`, 1 km) and W113 the whole-cycle steps relative to each pixel's fitted line; `--area auto` picks it when the raw spread exceeds three times a stable area's expectation; the reference moves to the most coherent cell of the stable quintile when the chain chose it | — | — | — |
| W117 | a date whose residual to the fitted line exceeds 3 robust standard deviations at more than 20 % of the sampled good pixels; marginal at 35 % and more; the verdict drops when two or more dates are marginal | yes | - | `--exclude-dates`, `--fit huber`, `--tropo gacos|era5` |

The thresholds are judgement values for C-band 12-day stacks (`quality.THRESHOLDS`), not physical limits.

### W109 PairsExcluded
Quality verdict: see the table under W108.

### W110 VelocityNoise
Quality verdict: see the table under W108.

### W111 UnclosedTriplets
Quality verdict: see the table under W108.

### W112 SceneTrend
Quality verdict: see the table under W108.

### W113 TimeSeriesJumps
Quality verdict: after the step common to all pixels is removed (see W114), more than 3 % of the good pixels have a step larger than three quarters of a cycle (0.75 × λ/2 in range, 21 mm at C band) that is still there one date later (a single noisy date steps out and back and is not counted) between two consecutive dates of one network part. Deformation of that size in one revisit is rare; a unwrapping error in time or a date with missing / corrupted data is the usual cause. The message names the dates at which most jumps occur (`summary.jumps_by_date`). Found on the downtown test area: 20250430 holds a zero-filled strip, and one cycle of error starts at that date in patches of the image.

### W114 ReferenceUnstable
Quality verdict: between consecutive dates the good pixels move together against the reference pixel by more than 5 mm (standard deviation over the dates of their median step, `summary.reference_step_std_mm`). The reference itself is unstable - on the downtown test area the automatic choice fell on a strong scatterer on a tall building, whose uncompensated height error changes phase with every baseline. Velocities are little affected (a common offset), single dates are. W113 counts jumps after this common step is removed.

### W117 DateOutlier
Quality verdict: the inversion keeps a sample of the good pixels (every n-th, about 200 000 at most) and the residual of their series to the fitted velocity line (one intercept per network part; the median offset for a Huber fit). One robust scale is taken over the whole sample (1.4826 × MAD, `summary.date_outliers.scale_mm`; the test needs six dates or more, a shorter series has degenerate residuals); a date at which more than 20 % of the sampled pixels lie further than 3 scales from the sample median is an outlier - its atmosphere (or bad data) has moved the whole scene, which deformation does not do in one revisit. `summary.date_outliers` lists the flagged dates and the fraction of every date; `bosar sbas quality` prints them. The message says whether the least-squares velocity leans on the date or the Huber fit (`--fit huber`) has down-weighted it; either way the series at that date stays biased - leave the date out with `--exclude-dates` or correct the troposphere. The temporal reference is never such a date: with no `--ref-date`, the reference is the date whose common mode (the scene-wide median) lies closest to the median over the dates (`summary.ref_date_rule = common_mode_median`, the common modes in `summary.common_mode_mm`). Found on the three-year Indianapolis product: the first date, 2023-07-10, sat 4 mm below the rest and one 2026-06 date 14 mm above at three landmarks. Two levels since v0.4.0: a date beyond 20 % is *noted* (the finding is informational, printed with `(info)`, the verdict stands); a date at 35 % or more is *marginal* and named as such; the verdict drops to MARGINAL only when two or more dates are marginal - one atmospheric date is tolerated because `--fit huber` or `--exclude-dates` handles it and the per-date fractions ship with the product (`summary.date_outliers`) either way.

### W115 ClosureBudgetUnreached
Closure correction (`unw_correct`): the exact L1 programs run under a wall-clock budget (`--correct-budget-s`, 900 s by default), the closure patterns covering most pixels first; the patterns not reached stay uncorrected and the warning carries their share of the pixels with errors. A longer budget or more workers reaches them.

### W116 IntermediatesRematerialized
Chains in `storage_mode=minimal`: a step of the chain is done, but the tier-2 products it made were collected after the chain that declared them had finished (the producer's `summary.collected` lists the kinds), and a later step of this chain requires them - e.g. `pipeline psi` after a completed `pipeline psds` needs the flattened stack again. The chain re-runs that step with the same parameters instead of failing with E107; the record gets `summary.rematerialized_for`, and the re-made products are collected again when their new dependents are done. Declaring both chains before the first one runs avoids the re-run, as does `storage_mode=full`.

### W201 MetadataSuspicious
Recorded on a dataset (and in the run log when imported) when a reader detects metadata that is nominal rather than measured — e.g. the SNAP StaMPS export writes `near_range_slc`/`far_range_slc` as centre ∓ (N−1)/2 × the nominal 2 m spacing, so the slant-range axis and every incidence angle derived from it are approximate; or every `.rslc.par` carries the reference scene's date/time header (then `acq_utc` is the file-name date). Never corrected silently; the warning text says what to verify. `bosar data import --annotation <SAFE>` resolves the range-axis case from the Sentinel-1 annotation and records **I201** instead (see *Info records* below and `docs/data/formats.md`).

### I201 GeometryCorrected (info, not a warning)
Appended to a stack's `info` list (and to the `StackRecord`) when `data import --annotation` or `data crop --annotation` overwrote the nominal GAMMA/StaMPS geometry from the matching Sentinel-1 swath annotation: range spacing, near/mid/far range, azimuth spacing, both radii, incidence angles, the re-projected B⊥ of every pair (first pair before → after in the text) and `acq_utc` from the SAFE `startTime`. `geometry.provenance` becomes `safe-annotation:<file>`.

### W202 SidecarMalformed
Recorded on a stack when one metadata sidecar cannot be parsed or holds a non-physical value while the rest of the stack is fine — e.g. the author's `diff0/20240821_20240809.base` carries TCN components of ~1e11 m (the same pair MintPy reported as B⊥ = −1.3e11). The affected pair keeps its interferogram but has no baseline row; the warning names the file and the value. A stack whose *reference* metadata is broken still fails hard (E204/E205).

### W203 CalibrationAbsent
Recorded on a Sentinel-1 SAFE product whose `annotation/calibration/` folder (σ⁰/β⁰/γ⁰ LUTs and noise vectors) is absent — the author's VV-only unzips are like this. Interferometry proceeds; radiometric calibration steps will refuse the product until the full SAFE (or the zip) is supplied.

### W204 ProductSpacingMismatch
Reported by `bosar info <product.tif>` when a Step product's per-look pixel spacing (tags `pixel_spacing_*_m` / `looks_*`) differs by more than 0.1 % from the project stack that has the same `geometry_provenance`. This is the v0.1.0 regression (Steps re-opened the raw export and wrote the nominal 2 × 14 m grid although the stack had been corrected with `--annotation`); it is fixed by `reapply_from_provenance` and the check keeps it from returning. `info` also prints a W201 line when a product carries the reader's nominal geometry (`geometry_provenance = reader`).

### W205 AuxDataMarginal
Reported by `bosar aux gacos-check` when a delivered file is usable but not clean: the GACOS grid leaves less than 0.05 deg between the stack footprint and its edge, more than 1 % of the grid inside the area is NaN or zero, the grid steps differ between dates, grids exist for dates outside the stack, or the acquisition time is unknown so `TIME_OF_DAY` could not be checked. The same check reports hard problems with the input codes: **E201** a date's `.ztd` or `.ztd.rsc` is missing, **E204** wrong file size, `TIME_OF_DAY` more than `--time-tolerance-h` (1 h) from the acquisition, grid not covering the footprint or a median delay outside 1-3 m, **E205** unreadable `.rsc` header; any E makes the folder unusable (exit 5).

### W206 EmptyInterferogram
Reported by `bosar data import` (GAMMA/StaMPS reader) when a `<ref>_<date>.diff` or a `<date>.rslc` holds only zeros in 25 small windows sampled across the raster: the export wrote an empty interferogram for that date (seen for three dates of the author's SNAP export, the same dates whose `.base` is malformed). The stack still imports; `bosar sbas prep` drops every pair derived from such an interferogram (`empty_pairs`) and `ifg_flatten` can rebuild an empty `.diff` from the SLCs when those are valid; an empty `.rslc` cannot be rebuilt from the stack - re-export that date or preprocess it again.

### W207 PartiallyEmptyDate
`slc_flatten` scans every date of the stack and reports the fraction of zero pixels (`summary.missing_fraction_by_date`). A date with more than 0.1 % zero pixels inside the stack's common area is partially empty: a strip the export did not fill, a burst that failed. `bosar pipeline psds` leaves such dates out by default and says so (`--keep-partial-dates` keeps them: every pixel of the empty area is then lost for all dates). Re-coregister the date from the raw product to get it back.

### W208 CommonZeroFloor
`slc_flatten` (v3) and `bosar data import` (every reader) measure the zero pixels of every date against the common floor: the median zero fraction of the non-empty dates, which is the scene edge / burst-gap area the export leaves empty on every date (6.5 % on the full 9-burst IW2 swath). W208 reports that floor once; W207 is then raised only for a date lacking more than two percentage points beyond it. Nothing is left out because of W208 alone.

### W209 RangeShiftLarge
`s1_coregister`: the amplitude cross-correlation of a date against the reference reads a range shift above 0.1 px. The shift is still applied only under the gate (above `range_cc_min_px` = 0.02 px and the bursts agreeing within `range_cc_max_spread_px` = 0.01 px); W209 says that a shift this large is a change of the propagation delay between the date and the reference rather than a coregistration error: on the Indianapolis stack the ionospheric group delay (GIM slant TEC) and the ERA5 tropospheric delay explain the per-date shifts with r 0.87 and a 0.034-px residual, while the IPF version does not (table and regression in `docs/data/formats.md`). The carrier phase is baseband after deramping, so the correction moves the envelope only.

### W210 OffsetFieldSparse
`offset_tracking` found that fewer than half of the patches with data carry a valid offset: the rest have an SNR below `snr_min`, a correlation peak on the edge of the search area, or deviate from the 3 × 3 median of the field by more than `mad_k` MAD. The products are written as usual (rejected patches are NaN, the classes are in `offset_mask`) and the summary counts every class, but the field is dominated by decorrelation and its median / std are not representative. It is also raised when no patch of the area has data (every class 255). Use a larger `window`, a shorter time span, or restrict the run to the coherent area (`region`, `bbox`).

### W211 OffsetSpacingNominal
`offset_tracking` ran on a stack without lat / lon layers (`--geocode false`): the azimuth offsets are converted to metres with the stack's nominal azimuth pixel spacing (14.0 m for an ISCE-layout stack, whose `reference/IW*.xml` carries no azimuth spacing) instead of the along-track spacing measured from the layers, and nothing is geocoded. Range offsets use the slant-range spacing of the metadata and are exact.

### W213 SpeckleEnlNotEstimated
The `amplitude` step was asked for a speckle filter that uses the ENL (`--speckle` lee, refined_lee, gamma_map or nlmeans; boxcar and frost do not use it and never raise W213) without an ENL (`enl`), and the automatic estimate on the reference date found no 32 × 32 block (or, on a small image, no block of the image's size) with at least 90 % valid pixels - the image is smaller than 8 × 8 multilooked pixels or mostly no-data (layover, shadow, zero fill). The filter ran with the nominal number of looks (azimuth × range looks) as the ENL, an upper bound (neighbouring looked pixels are correlated): the filter then takes the speckle for weaker than it is and keeps more of it. Pass the ENL with `--set amplitude.enl=<looks>` (measured with `bosar.core.speckle.enl_window` on a homogeneous area) to silence it.

### W215 ThermalNoiseIncomplete
`s1_coregister` with calibrated layers: thermal-noise removal was requested - `thermal_noise=on`, or `auto` on an IPF 2.90 or later product - but the SAFE cannot provide it as asked. Either the noise annotation (`annotation/calibration/noise-*.xml`) is missing or unusable: the calibrated layers of that date are written without noise subtraction; or it holds range vectors only (IPF before 2.90, `noiseVectorList`; or a new-style file without azimuth vectors): the range noise is subtracted and the azimuth component (the TOPS scalloping) is not. The message names the date and the reason; the date's record (`written.<date>.calibrated.thermal_noise`) carries the decision, the IPF version and the clamped fraction.

### W216 ThermalNoiseMixed
`s1_coregister`: the calibrated layers of some dates of the stack have the thermal noise removed and those of others do not - typically `thermal_noise=auto` on a stack that spans IPF 2.90 (March 2018), or a date without a usable noise annotation (W215). Areas near the noise floor (water, shadow) then step between the two groups of dates. The message lists the dates without removal; re-run with `--thermal-noise off` (none) or `on` (range-only noise for the older products) for one rule across the stack.

### W219 IonoNoSnaphuComponents
`iono_split` (version 2, `components=snaphu`) found no SNAPHU executable (or the unwrapping backend was set to scikit-image): the full band was unwrapped with scikit-image, which unwraps every 4-connected region of coherent cells on its own (probe: two regions split by a masked band came out 2 cycles apart). Those regions are taken as the components; each one's weighted median is removed before the low-pass, as with SNAPHU's connected components. The estimate is usable; SNAPHU decides better which cells belong together (it grows components by cost, across thin decorrelated gaps). Install or point to the binary (`BOSAR_SNAPHU_EXE`, `packaging/bin/<platform>/`) and re-run the step.

### W220 IonoFragmentedComponents
`iono_split`: the estimate rests on more than one connected component and the largest holds less than half of the used cells. Each component's median was removed (regions unwrapped independently differ by `k` half-cycles of dispersive phase, `core.iono.ambiguity_step_rad`), so the ionosphere *between* components - its long wavelengths across the scene - is not measured; `summary.component_list` gives each component's constant split into whole ambiguity steps and a remainder. Prefer a pair with more coherent area (winter, short temporal baseline), more looks, or a lower `coh_min`.

### W227 IonoModelSkipped
The plausibility gate of `sbas_invert --iono` refused one or more ionospheric models: a model's span (`max - min` of the model grid that is subtracted) exceeded what a plausible TEC difference makes at the carrier (`rad_per_tecu(f) x max(floor, k x |GIM difference|)`), its gradient per 100 km of ground (the range slope taken from slant to ground range with the stack's mid-swath incidence) exceeded the ionosphere's (a fixed `iono_gate_gradient`, 2 TECU per 100 km by default; the GIM enters only the span bound), or the triplet closure vetoed it: a triplet whose three models do not close (the span of `m_ab + m_bc - m_ac` above the larger of `iono_gate_closure_factor` - 3 by default - times the median over the triplets and the phase of 1 TECU, `rad_per_tecu(f)`) names its pair of the largest span as the suspect, and a pair named so by failing triplets in at least half of all the triplets it belongs to (those whose three models are defined) is vetoed. A model that is undefined (its fit could not be made) is skipped as `span`. Nothing is subtracted for those pairs; the inversion runs on; the summary's `iono.gate` names them with the reasons and the bounds. `--no-iono-gate` subtracts every model without judging it and fails the step (E201) on a pair whose model is undefined. A GIM term of the span bounds that was lost before any model was judged is W228.

### W228 IonexGimUnavailable
`sbas_invert --iono` with the plausibility gate on: the GIM term of the span bounds (W227) was lost for some pairs before any model was judged - the IONEX folder named by `--ionex-dir` (or found at `<project>/aux/ionex`) is not a folder, the stack has no footprint centre, or some dates have no usable map (no file for the day, the acquisition time outside the maps, an unreadable file, no VTEC at the centre of a regional map). The message names the folder and a date with its reason; the detail carries `gim_pairs` (pairs with a finite GIM difference at both dates), `ionex_dir`, `gim_error` and up to 20 `dates_without_map`, and the summary's `iono.gate` keeps `gim_error`, `gim_dates_without_map` and `ionex_dir_source`. Those pairs' span bounds rest on the floor (`iono_gate_tec_floor`, 10 TECU by default): the gate is stricter for them, never looser, so a model of a strongly ionised date may be skipped that its map would have let through. Put the daily IONEX file of every date into the folder (or name the right one) and re-run the inversion with `--force`. Without any IONEX folder, named or found, the floor applies silently.

### W223 EnvisatMetadataInconsistent
`data/asar.py`: a metadata check of an ENVISAT ASAR IMS or ERS-1/2 IMS product in the Envisat format failed - the SPH disagrees with the annotation data sets (`FIRST_LINE_TIME`, `LINE_LENGTH`, `PASS` against the sign of the orbit's vertical velocity), the annotated `line_time_interval` does not match the stamped first-to-last-line span, the PRF is not the line rate, the radar frequency or the range sampling rate is off the sensor's nominal value by more than 0.1 %, the processed range bandwidth is off the chirp by more than 5 %, the geolocation grid is off the uniform range axis (0.05 samples) or the line timing (0.5 lines), the data type is not `SWORD`, the CHIRP PARAMS ADS is missing, or fewer than four product state vectors are usable (the orbit is then extended by two-body + J2 propagation). The message names the field and both values; the annotation data set wins over the SPH and nothing is corrected silently. The strings sit in `extra["warnings"]` of the `StripmapScene`; the chain logs them. None of the author's 26 products raises it. The same code checks an external precise orbit (a DORIS `DOR_VOR_AX` / `DOR_POR_AX` or ERS PRC file given as `orbit_file`, or the one `open_asar(orbit_dir=...)` - the stripmap chain's `--orbits <folder>` - takes from a folder) against the product's own state vectors at mid scene: more than 100 m apart (`ORBIT_FILE_WARN_M`) is a W223 naming the file and the distance; more than 1 km (`ORBIT_FILE_REFUSE_M`) is not this product's orbit - a file named as `orbit_file` is refused (E204), a folder's file is skipped for the next covering one with a W223 naming it, and E204 follows when every covering file is that far. On real products the matching precise orbit is about 10 m from the product's vectors (ERS PRC) or a few centimetres (ENVISAT DORIS); the other ERS satellite's PRC file of a tandem day is about 11 950 km away. A product without a usable state vector of its own raises a W223 saying that the orbit file is not checked.

### W224 Ers2GyroDoppler
`data/asar.py`: an ERS-2 scene dated 2001-01-01 or later. ERS-2 lost its gyroscopes in January 2001 and flew in zero-gyro / degraded attitude modes afterwards: the Doppler centroid can be several PRF ambiguities large and the processor's annotation (`DOP CENTROID COEFFS ADS`, `extra["processed_doppler_centroid"]`) less reliable; a pair with such a scene needs its Doppler checked before the azimuth spectra are trusted. The message carries the mid-swath value and the confidence. The author's ERS-2 scenes on disk (1996-05 ... 2000-03) all predate that date; note that the 2000-03-17 scene, acquired after the February 2000 switch to one-gyro piloting, already shows a mid-swath Doppler of -349 Hz (0.21 PRF, the other ERS-2 scenes -91 ... -148 Hz) and is not flagged by the date rule.

### W221 AlosPrfVaries
`data/ceos_alos.py`: the ALOS-1 PALSAR L1.1 reader reads the PRF field of every line header (an integer in mHz) and compares the lines with each other and with the leader's PRF (`Pulse Repetition Frequency in mHz`, with decimals). A variation across the lines above `PRF_TOLERANCE` = 1e-6 relative is **E205** (one `StripmapScene` has one PRF; such a file is not one scene). A smaller variation, or a difference between the lines and the leader, is W221: the leader's PRF is used for the azimuth time interval and the line times. On the real products the field is constant and 1e-7 from the leader (the millihertz rounding). The warning is kept in `scene.extra["warnings"]`. v0.4.0 (ALOS-2): the same code reports the microsecond line stamps' own clock when its rate differs from the leader's PRF by more than the tolerance on a scene spanning at least one second (the Greenland scenes: 8.8e-6 fast, ±44 µs at the ends); the leader's PRF and the centre-weighted fit are used.

### W222 AlosLeaderPrefixMismatch
`data/ceos_alos.py`: the leader and the image file's line headers describe the same scene twice and the reader checks them against each other. Scene centre time: the least-squares fit of the per-line millisecond stamps puts the scene centre line more than 2 ms from the leader's `Scene centre time` (E205 above 1 s) - the line times are used. Slant range to the first sample: the leader's range gate delay times c/2 differs by more than 1 m from the integer-metre field of the line headers (E205 above 100 m) - the leader's value is used. On the real products both agree within the quantisation of the header fields (0.5 ms, 0.5 m). v0.4.0 (ALOS-2): the same code reports the leader's `Doppler center frequency` fields (`a + b R`) disagreeing with its cross-track polynomial at the first sample by more than 5 Hz, and the millisecond and microsecond stamps disagreeing on the first line by more than 2 ms (the polynomial and the microseconds are used); the ALOS-2 range gate delay is not checked at all - it is not the delay to the first sample. v0.4.0 review (ALOS-2 range bandwidth): the reader takes the range bandwidth from the leader, not from the mode's nominal table - the chirp's `|rate| x pulse length` and the `total processor bandwidth in range` field are each plausible when positive, not above the range sampling rate and within `ALOS2_BANDWIDTH_TOLERANCE` (25 %) of the mode's nominal bandwidth. The same code reports a chirp that is blank or implausible (the total processor bandwidth is used when it is plausible, else the nominal value), and a chirp and a total processor bandwidth that are both plausible but differ by more than `BANDWIDTH_CHECK_REL` (2 % of the chirp): the smaller of the two is used, since the image's range spectrum is no wider than either. A plausible chirp next to a total that differs from it by more than 2 % but is not plausible itself is reported too, and the chirp is kept. `scene.extra` records `chirp_bandwidth_hz`, `total_bandwidth_range_leader_hz`, `nominal_bandwidth_hz` and `range_bandwidth_source`. The Greenland FBS products give 24.9 MHz from both fields (nominal 28 MHz) and raise nothing; ALOS-1 keeps its nominal 28 / 14 MHz without a check.

### W225 StripmapRefineNotApplied
`stripmap_coregister`: the amplitude cross-correlation refinement of a date (`core.offsets.track` between the reference and the geometrically coregistered secondary on a coarse patch grid, then `core.stripmap.fit_offset_plane`) was not applied - fewer than `refine_min_patches` valid patches survived the SNR / edge / MAD culling (water, snow, a decorrelated pair, an empty scene), the written window holds no patch at all (a crop smaller than `refine_window + 2 refine_search`), or the fitted constant exceeded the search radius minus one pixel (the correlation peak sits against the search border: the geometric offsets are off by more than `refine_search` pixels, which points at a timing or orbit problem of that product rather than at a sub-pixel residual). The geometric offsets alone are used for that date; the record keeps the rejected fit (`refinement.reason`). Inspect `refinement.n_valid` / `rms_px` in the stack record; a larger `--refine-search`, or `--no-refine`, is the way round a product with a known timing error. Since v0.4.0 a third reason: the residual rms of the kept patches exceeds `refine_max_rms_px` (2 px by default) in azimuth or range - the patches found no correlation peak (the VV band of a NISAR river-delta scene scattered by 9 px on 250 patches), and the plane fitted through noise would misregister the date; the geometric offsets alone are kept.

### W226 StripmapMetadataIncomplete
`stripmap_coregister`: a scene's metadata does not fully determine the chain's inputs and an assumption was made. (a) The products mix range samplings - ALOS FBD (14 MHz) with FBS (28 MHz) - and the reader of the FBD scene took no `oversample_to_fbs` flag, so the pair is coregistered at different range samplings: the geometry is right (the offsets are in each scene's own pixels) but the range spectra overlap by half, which costs coherence; a reader that oversamples silences it. (b) A zero-Doppler product (ASAR / ERS IMS, NISAR RSLC) carries no processed Doppler centroid (`extra["processed_doppler_centroid"]`), so the secondary is interpolated without demodulation: with the azimuth spectrum off centre by the processor's centroid, the sinc kernel aliases part of it (a few per cent of coherence at ASAR's typical few hundred hertz; more for a yaw-steering-free ERS-1 scene).

### W301 OrbitFromAnnotation
The native TOPS chain (`s1_coregister`) found no precise orbit file for a date in the project, the data roots or SNAP's cache and used the annotation's state vectors (10 s spacing, metre-level). Run `bosar fetch orbits` for the products and re-run the step.

### W302 EsdNoCoherentOverlap
Enhanced spectral diversity found no burst-overlap pixel above the coherence threshold (`esd_coherence`) for a date; the geometric coregistration (orbits + DEM) stands without the azimuth correction. Lower the threshold, widen the looks, or check the date (an empty or decorrelated scene).

### W401 GpuUnavailable
CuPy or a CUDA device was not usable; the run continues on NumPy (`reason` carries the exception text).

### W501 SnaphuUnavailable
No SNAPHU binary/package; unwrapping falls back to scikit-image.

### W503 SnaphuNoCs2
Retired: `mst` is the default initialisation of the `unwrap` step since v0.4.0 (every bundled SNAPHU is a NO_CS2 build, and on a real Sentinel-1 pair the two initialisations differed by one cycle on 4 of 117 888 pixels), so the substitution this warning announced no longer happens by default. An `init: mcf` asked of a binary without the solver still runs as MST; the step summary records `init` (applied) and `init_requested`, without a warning. The code is never reused. The text it carried in v0.4.0: the `unwrap` step asked SNAPHU for an initialisation the binary cannot run: it was built without the CS2 minimum-cost-flow solver (the solver has its own non-commercial licence), so `INITMETHOD MCF` is unavailable and the unwrap ran with the MST initialisation; the step summary records `init` (applied) and `init_requested`. The installers carry that SNAPHU, and so does a source checkout that uses the bundled binary or builds its own with `-NoCs2` / `--no-cs2` (`bosar preflight` reports it as "no CS2 solver (MST init)") - so with the step's default `init=mcf` this warning comes with every SNAPHU unwrap there: it records the substitution, not a fault. The result is the same optimisation from a different starting flow; on a real Sentinel-1 pair (117 888 unwrapped pixels) the two initialisations differed by one cycle on 4 pixels and nowhere by more. An unwrap step whose parameters ask for `init: mst` runs without the warning; a SNAPHU of your own that carries the solver, named with `BOSAR_SNAPHU_EXE`, runs MCF.

### W502 SnapHeapFromInstall
A `snap_*` Step ran with `heap_mb = 0`, i.e. with the `-Xmx` of the install's `gpt.vmoptions`, and that default is larger than the heap Bosar gives a job when `heap_mb` is unset (half of the RAM, at least 2 GB and at most 64 GB). SNAP fills whatever heap it is given (41-45 GB peak RSS for a three-scene subset under `-Xmx132G`), so parallel work on the machine may starve. Pass `heap_mb` / `--snap-heap <MB>` or leave the parameter unset.

### W601 Tier2Kept
`storage_mode=full` kept intermediate products that `minimal` would have deleted.

### W602 GcDeleteFailed
Garbage collection could not delete a file (locked by another process or permission denied); the file is listed under `kept` with the reason and the step status is unaffected.

### W802 PostFailureActionFailed
A bookkeeping action after a failure (save, gc, report) failed itself; the original failure is preserved.

### W803 HookFailed
A client-registered hook raised; the step status is unaffected.

## Preflight check codes (P)

`P1xx` system · `P2xx` gpu · `P3xx` dependencies · `P4xx` binaries · `P5xx` credentials · `P6xx` network · `P7xx` project.
Version 0.4.0 added `P202 gpu.plugin` (the GPU plug-in of an installed build: present, absent with an NVIDIA driver seen, or not needed) and `P305 deps.build` (the build record of an installed build: id, platform, time, commit, SNAPHU solver); `P401` now says whether the SNAPHU binary carries the CS2 solver.
The full list with the check ids lives in `src/bosar/preflight/model.py` (`CHECK_CODES`) and is
printed by `bosar preflight`; blocking failures raise E701.
