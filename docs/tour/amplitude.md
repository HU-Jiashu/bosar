# Amplitude change

Log-ratio and pre/post RGB composite over the basemap.

Built in v0.1.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/amplitude/03_rgb_dark.png"><img src="../assets/tour/amplitude/03_rgb_light.png" width="900" alt="Amplitude change: result"></picture>

## Step by step

### 1. Amplitude change: a pre- and a post-event date; the stack is normalised to its temporal median first.

```bash
bosar pipeline amplitude tour/indy_crop --stack crop_indy_downtown_crop --pre 20240821 --post 20250723
```

<img src="../assets/tour/amplitude/01_dates_light.png" width="900" alt="Amplitude change step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/amplitude/01_dates_dark.png" width="900" alt="Amplitude change step 1 (dark)">

</details>

### 2. Log ratio in dB over the basemap: red brighter, blue darker than before.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/amplitude/02_log_ratio_light.png" width="900" alt="Amplitude change step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/amplitude/02_log_ratio_dark.png" width="900" alt="Amplitude change step 2 (dark)">

</details>

### 3. Pre/post RGB composite (R = before, G and B = after): new bright targets are cyan, vanished ones red.

```bash
bosar pipeline amplitude tour/indy_crop --stack crop_indy_downtown_crop --pre 20240821 --post 20250723
```

<img src="../assets/tour/amplitude/03_rgb_light.png" width="900" alt="Amplitude change step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/amplitude/03_rgb_dark.png" width="900" alt="Amplitude change step 3 (dark)">

</details>
