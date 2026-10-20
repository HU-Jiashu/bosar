# Project and data

Create a project, import a stack, look at dates, baselines and a coherence preview.

Built in v0.1.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/project_data/03_preview_dark.png"><img src="../assets/tour/project_data/03_preview_light.png" width="900" alt="Project and data: result"></picture>

## Step by step

### 1. Open or create a project: its folder holds the products, the logs and project.json.

```bash
bosar project new tour/indy_crop --name indy_crop
```

<img src="../assets/tour/project_data/01_project_light.png" width="900" alt="Project and data step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/project_data/01_project_dark.png" width="900" alt="Project and data step 1 (dark)">

</details>

### 2. Import a stack (GAMMA/StaMPS export, SAFE, BEAM-DIMAP or a crop): dates, geometry and the baseline plot.

```bash
bosar data import tour/indy_crop data/indy_downtown_crop
```

<img src="../assets/tour/project_data/02_stack_light.png" width="900" alt="Project and data step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/project_data/02_stack_dark.png" width="900" alt="Project and data step 2 (dark)">

</details>

### 3. A quick coherence preview of a pair tells whether it is worth processing.

```bash
bosar data preview tour/indy_crop --pair 20240821_20240914
```

<img src="../assets/tour/project_data/03_preview_light.png" width="900" alt="Project and data step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/project_data/03_preview_dark.png" width="900" alt="Project and data step 3 (dark)">

</details>
