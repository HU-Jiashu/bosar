# Logs and failures

Every run with its UTC-stamped records; a failure card says what, where and how.

Built in v0.1.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/logs/02_failure_dark.png"><img src="../assets/tour/logs/02_failure_light.png" width="900" alt="Logs and failures: result"></picture>

## Step by step

### 1. Logs page: every run with its records - UTC timestamps, step, level, parameters, inputs, outputs, durations.

```bash
bosar logs tour/indy_crop --tail 3
```

<img src="../assets/tour/logs/01_runs_light.png" width="900" alt="Logs and failures step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/logs/01_runs_dark.png" width="900" alt="Logs and failures step 1 (dark)">

</details>

### 2. A failed step shows a card: the error code, what was wrong, where, and the hint for fixing it.

```bash
bosar logs tour/indy_crop --level ERROR
```

<img src="../assets/tour/logs/02_failure_light.png" width="900" alt="Logs and failures step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/logs/02_failure_dark.png" width="900" alt="Logs and failures step 2 (dark)">

</details>
