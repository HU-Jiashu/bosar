# Coherence change detection

Pre- and co-event pairs, the run, the damage proxy map over satellite imagery.

Built in v0.1.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/ccd/03_dpm_dark.png"><img src="../assets/tour/ccd/03_dpm_light.png" width="900" alt="Coherence change detection: result"></picture>

## Step by step

### 1. Coherence change: tick the pre-event pairs and the co-event pair; the planned steps list what will run and what is reused.

```bash
bosar pipeline ccd tour/indy_crop --stack crop_indy_downtown_crop --pre 20240821_20240902 20240821_20240914 --co 20240821_20250723
```

<img src="../assets/tour/ccd/01_pairs_light.png" width="900" alt="Coherence change detection step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/ccd/01_pairs_dark.png" width="900" alt="Coherence change detection step 1 (dark)">

</details>

### 2. The coherence-change z map over the Sentinel-2 cloudless mosaic, 75 % opaque.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/ccd/02_z_map_light.png" width="900" alt="Coherence change detection step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/ccd/02_z_map_dark.png" width="900" alt="Coherence change detection step 2 (dark)">

</details>

### 3. The damage proxy map: connected groups above the threshold. Here the "event" is one year of urban change.

```bash
bosar pipeline ccd tour/indy_crop --stack crop_indy_downtown_crop --pre 20240821_20240902 20240821_20240914 --co 20240821_20250723
```

<img src="../assets/tour/ccd/03_dpm_light.png" width="900" alt="Coherence change detection step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/ccd/03_dpm_dark.png" width="900" alt="Coherence change detection step 3 (dark)">

</details>
