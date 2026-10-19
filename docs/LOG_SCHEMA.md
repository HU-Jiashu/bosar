# Run log schema (`log_schema_version = 1`)

Every processing run writes three files under `<project>/logs/`:

| File | Content |
|---|---|
| `run_<run_id>.jsonl` | one JSON object per line, the machine-readable record of the run |
| `run_<run_id>.log` | the same records, one human-readable line each (`#seq ts LEVEL event …`), with a WHERE/HINT/TRACEBACK block for failures |
| `run_<run_id>.md` | the run report: environment, preflight, steps table, failure block, warnings, storage, files — rewritten atomically at every transition |

`run_id` = `r_<YYYYMMDDTHHMMSSZ>_<4 hex>` (`logging/records.py::new_run_id`), unique for two runs
in the same second. Files are UTF-8 with LF line endings on every platform.

## Record keys

Every record carries: `ts` (UTC, `YYYY-MM-DDTHH:MM:SS.ffffffZ`), `seq` (1-based, strictly
increasing per run — the order key, because on Windows 87 % of `datetime.now()` stamps repeat within
20 000 calls), `run_id`, `level` (`INFO|WARNING|ERROR`), `event`, `step` (step id or `null`),
`msg`, `pid` (worker records carry the child pid).

| event | additional keys |
|---|---|
| `run_start` | `app_version`, `argv`, `env` (allow-listed, redacted environment digest), `env_sha256`, `log_schema_version`, `reproduce` |
| `preflight` | `report` (`counts`, `blocking`, `checks[]` with `code`, `id`, `group`, `status`, `detail`, `hint`, `duration_s`) |
| `step_start` | `kind`, `version`, `params` (validated, as run), `inputs[]` (`path`, `bytes`, `sha256`), `device`, `reproduce` |
| `step_progress` | `done`, `total`, `tile` (throttled: first, last, every ≥ 1 s or ≥ 5 %) |
| `step_end` | `outputs{kind: path}`, `figures[]`, `summary` (per-product stats and step summary), `duration_s` |
| `step_failed` | `error` (`errors.describe()`: `type`, `code`, `title`, `msg`, `where`, `param`, `hint`, `doc`, `traceback`, `frames`, `notes`, `cause_chain`), `duration_s`, `params`, `inputs[]`, `outputs_partial[]`, `tile`, `progress` |
| `gc` | `deleted[]`, `kept[]` (with reasons), `freed_bytes` |
| `warning` | `code` (`Wxxx`, see `docs/ERRORS.md`), `detail` |
| `run_end` | `status` (`done|failed|cancelled|blocked`), `n_steps`, `n_failed`, `duration_s`, `report` |

Deviation from the project rules ("preflight results are the first records of every run"): the first
record is `run_start` — a header carrying the environment digest and `log_schema_version` — and
the preflight records follow immediately.

## Environment digest and redaction

`run_start.env` records the package version, Python and platform, the versions of the declared
dependencies, the git HEAD of the checkout (when present), the backend `device_info()` and only the
environment variables whose names start with `BOSAR_`, `PROJ_`, `GDAL_`, `CUDA_` or `PYTHON`;
`PATH` is stored as a SHA-256 only. Every mapping passes through `utils.redact.redact()`: keys
matching `token|secret|passw|pwd|api_key|auth|cookie|netrc|credential` become `***` and
`user:password@` in URLs is masked. The same redaction applies to the `.log` mirror, the report and
the CLI output, because logs travel inside release packages and issue reports.

## Worker processes

Workers (Windows `spawn`) are initialised with `logging.queue.worker_init(queue, run_id)` and emit
records with `worker_event(...)`; the records travel through a `QueueHandler` → `QueueListener` in
the parent and receive their `seq` from the same `RecordSink` as the main process, so `seq` stays
strictly increasing across producers while `ts` is only guaranteed non-decreasing per producer.

## Reading logs

`bosar logs <project> --tail N | --failure | --report | --validate`; the reader
(`logging/reader.py`) reports a damaged line as E104 with the file, line and column.

## Warnings captured inside a step

`warning` records with `code = "W000"` come in two forms. A warning raised in this package or in
a `tests/` tree is one record per warning with `detail.category`, `detail.filename`,
`detail.lineno`. Warnings raised in third-party code (any path under `site-packages`) are
summarised: one W000 record per step with `detail.third_party = {"<module>": <count>, ...}` and
a message listing the modules. `step_end.summary.n_warnings` counts the individually recorded
warnings; `step_end.summary.n_warnings_third_party` counts the summarised ones.

`run_start.reproduce` lists only the parameters that differ from the step defaults (the full
resolved set is in `step_start.params`). Run ids carry microseconds
(`r_<YYYYMMDDTHHMMSSffffff>Z_<4 hex>`) so log file names sort by start time; readers pick the
latest run by `run_start.ts`, not by name.
