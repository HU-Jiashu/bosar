# GACOS correction

What is missing, the run with --tropo gacos, displacement before and after.

Built in v0.2.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/gacos/04_before_after_dark.png"><img src="../assets/tour/gacos/04_before_after_light.png" width="900" alt="GACOS correction: result"></picture>

## Step by step

### 1. Aux page: what the project has - orbits, DEM, GACOS grids - and where each came from.

```bash
bosar aux status tour/indy_crop
```

<img src="../assets/tour/gacos/01_aux_light.png" width="900" alt="GACOS correction step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/gacos/01_aux_dark.png" width="900" alt="GACOS correction step 1 (dark)">

</details>

### 2. Before a run the assistant lists only what this run needs, what is automatic and what needs you (the GACOS request).

```bash
bosar aux status tour/indy_crop --for dinsar+gacos
```

<img src="../assets/tour/gacos/02_assistant_light.png" width="900" alt="GACOS correction step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/gacos/02_assistant_dark.png" width="900" alt="GACOS correction step 2 (dark)">

</details>

### 3. Tick the GACOS correction: the tropo_gacos step joins the chain before the displacement.

```bash
bosar pipeline dinsar tour/indy_crop --stack crop_indy_downtown_crop --pair 20240821_20240914 --tropo gacos --tag gacos
```

<img src="../assets/tour/gacos/03_run_light.png" width="900" alt="GACOS correction step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/gacos/03_run_dark.png" width="900" alt="GACOS correction step 3 (dark)">

</details>

### 4. Left without, right with the GACOS correction, the two views linked.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/gacos/04_before_after_light.png" width="900" alt="GACOS correction step 4">

<details><summary>dark theme</summary>

<img src="../assets/tour/gacos/04_before_after_dark.png" width="900" alt="GACOS correction step 4 (dark)">

</details>
