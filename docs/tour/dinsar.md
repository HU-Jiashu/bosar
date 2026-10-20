# DInSAR

Choose a pair, set the parameters, run, read the LOS displacement on the map.

Built in v0.1.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/dinsar/04_result_dark.png"><img src="../assets/tour/dinsar/04_result_light.png" width="900" alt="DInSAR: result"></picture>

## Step by step

### 1. Run page, DInSAR: pick the stack and the pair. The command box shows the one command the button will run.

```bash
bosar pipeline dinsar tour/indy_crop --stack crop_indy_downtown_crop --pair 20240821_20240914
```

<img src="../assets/tour/dinsar/01_pair_light.png" width="900" alt="DInSAR step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/dinsar/01_pair_dark.png" width="900" alt="DInSAR step 1 (dark)">

</details>

### 2. Parameters per step; an unset field shows the value that will be chosen ("auto (…)"). Only what differs from the default is written into the command.

```bash
bosar pipeline dinsar tour/indy_crop --stack crop_indy_downtown_crop --pair 20240821_20240914 --looks 2,10 --backend snaphu
```

<img src="../assets/tour/dinsar/02_parameters_light.png" width="900" alt="DInSAR step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/dinsar/02_parameters_dark.png" width="900" alt="DInSAR step 2 (dark)">

</details>

### 3. While it runs: steps with their state and duration, the live log, progress in the status bar, Stop cancels cleanly.

```bash
bosar pipeline dinsar tour/indy_crop --stack crop_indy_downtown_crop --pair 20240821_20240914
```

<img src="../assets/tour/dinsar/03_running_light.png" width="900" alt="DInSAR step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/dinsar/03_running_dark.png" width="900" alt="DInSAR step 3 (dark)">

</details>

### 4. Results page: the LOS displacement (positive toward the satellite) over OpenStreetMap; hover for value, unit and lat/lon.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/dinsar/04_result_light.png" width="900" alt="DInSAR step 4">

<details><summary>dark theme</summary>

<img src="../assets/tour/dinsar/04_result_dark.png" width="900" alt="DInSAR step 4 (dark)">

</details>
