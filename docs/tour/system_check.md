# System check

Preflight table: Python, GPU, SNAPHU, SNAP, credentials, read-only data roots.

Built in v0.1.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/system_check/01_preflight_dark.png"><img src="../assets/tour/system_check/01_preflight_light.png" width="900" alt="System check: result"></picture>

## Step by step

### 1. The preflight runs before every job: interpreter, packages, GPU, SNAPHU, SNAP, disk space, project.

```bash
bosar preflight --offline
```

<img src="../assets/tour/system_check/01_preflight_light.png" width="900" alt="System check step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/system_check/01_preflight_dark.png" width="900" alt="System check step 1 (dark)">

</details>

### 2. Credentials are stored in the system keyring and shown as present / missing only; read-only data roots are searched first for orbits, DEM tiles and GACOS grids.

```bash
bosar auth status
```

<img src="../assets/tour/system_check/02_settings_light.png" width="900" alt="System check step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/system_check/02_settings_dark.png" width="900" alt="System check step 2 (dark)">

</details>
