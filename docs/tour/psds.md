# PS / DS time series

Phase linking of distributed scatterers plus persistent scatterers: several times the coverage of multilooked SBAS, with a quality verdict.

Built in v0.3.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/psds/04_result_dark.png"><img src="../assets/tour/psds/04_result_light.png" width="900" alt="PS / DS time series: result"></picture>

## Step by step

### 1. PS / DS time series: flattened SLC stack, statistically homogeneous pixels, phase linking (EMI), PS selection, then the SBAS unwrapping and inversion on the hybrid stack. A partially empty date is found and left out.

```bash
bosar pipeline psds tour/indy_crop --stack crop_indy_downtown_ts --workers 6
```

<img src="../assets/tour/psds/01_run_light.png" width="900" alt="PS / DS time series step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/psds/01_run_dark.png" width="900" alt="PS / DS time series step 1 (dark)">

</details>

### 2. Phase linking in radar geometry: the temporal coherence of the fit (left; pure noise stays below 0.36 for this stack, a DS needs 0.6) and the number of statistically homogeneous pixels (right).

```bash
bosar pipeline psds tour/indy_crop --stack crop_indy_downtown_ts --workers 6
```

<img src="../assets/tour/psds/02_linking_light.png" width="900" alt="PS / DS time series step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/psds/02_linking_dark.png" width="900" alt="PS / DS time series step 2 (dark)">

</details>

### 3. Pixel type (0 none, 1 persistent scatterer, 2 distributed scatterer) and the amplitude dispersion that selects the PS.

```bash
bosar pipeline psds tour/indy_crop --stack crop_indy_downtown_ts --workers 6
```

<img src="../assets/tour/psds/03_types_light.png" width="900" alt="PS / DS time series step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/psds/03_types_dark.png" width="900" alt="PS / DS time series step 3 (dark)">

</details>

### 4. LOS velocity of the hybrid stack over the map with the persistent scatterers as points (colour = velocity, size = quality), the quality verdict above the map and the history of the clicked pixels.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/psds/04_result_light.png" width="900" alt="PS / DS time series step 4">

<details><summary>dark theme</summary>

<img src="../assets/tour/psds/04_result_dark.png" width="900" alt="PS / DS time series step 4 (dark)">

</details>
