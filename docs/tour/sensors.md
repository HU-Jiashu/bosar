# More sensors

ALOS-1 PALSAR (L band), ENVISAT ASAR and ERS-1/2 through the stripmap chain: the stack with its sensor, the L-band quality profile, a Mexico City interferogram of each.

Built in v0.4.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/sensors/03_alos_pair_dark.png"><img src="../assets/tour/sensors/03_alos_pair_light.png" width="900" alt="More sensors: result"></picture>

## Step by step

### 1. ALOS-1 PALSAR L1.1 (CEOS, straight from the ASF zips) through the stripmap chain - Doppler-aware geometric coregistration on the DEM, FBD oversampled onto the FBS range grid, calibration - and imported like any other stack: the sensor, the 23.6 cm wavelength and the baselines come with it. The same chain reads ENVISAT ASAR and ERS-1/2 (.N1 / .E1 / .E2 with DORIS orbits) and NISAR RSLC.

```bash
bosar pipeline stripmap-coregister <project> --product <ALPSRP zip> … --reader alos --dem bosar --crop-wkt "POLYGON((…))" --id alos_pair
```

<img src="../assets/tour/sensors/01_stack_light.png" width="900" alt="More sensors step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/sensors/01_stack_dark.png" width="900" alt="More sensors step 1 (dark)">

</details>

### 2. Next to the stack the Run page names the sensor, the band and the quality profile the verdict will use: at L band the coherence floors, the tolerated spread and the ionospheric model (filtered rather than a plane) are the L-band set - the same thresholds in radians, scaled by the wavelength. --iono adds the split-spectrum ionosphere of every pair.

```bash
bosar pipeline psds <project> --stack alos_mx --network l --k 3 --iono
```

<img src="../assets/tour/sensors/02_profile_light.png" width="900" alt="More sensors step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/sensors/02_profile_dark.png" width="900" alt="More sensors step 2 (dark)">

</details>

### 3. Mexico City, 20080214 - 20080331 (46 days, B⊥ −111 m): the unwrapped L-band phase of the pair in radar geometry. Positive phase is motion away from the sensor: Iztapalapa in the south-east subsides by about 4 rad = 7.5 cm of LOS in 46 days - the order of the published 20-40 cm/yr - with the ionosphere still in it (the split-spectrum model of this pair is a 1.1 rad range gradient).

```bash
bosar sbas prep <project> --stack alos_pair --network pair --flat-step slc_flatten_alos_pair
```

<img src="../assets/tour/sensors/03_alos_pair_light.png" width="900" alt="More sensors step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/sensors/03_alos_pair_dark.png" width="900" alt="More sensors step 3 (dark)">

</details>

### 4. ENVISAT ASAR IS2, 20091225 - 20100305 (70 days), the same crop and route: the unwrapped C-band phase spans −12 … +10 rad, most of the basin 5 cm of LOS away from the north-west corner in 70 days - the Iztapalapa order of magnitude again, from a sensor that stopped in 2012. The ERS-1 / ERS-2 tandem day (1996) is in the same project: a turbulent ±6 rad atmosphere and nothing else.

```bash
bosar pipeline stripmap-coregister <project> --product <ASA_IMS .N1> … --reader asar --dem bosar --crop-wkt "POLYGON((…))" --id asar_pair
```

<img src="../assets/tour/sensors/04_asar_pair_light.png" width="900" alt="More sensors step 4">

<details><summary>dark theme</summary>

<img src="../assets/tour/sensors/04_asar_pair_dark.png" width="900" alt="More sensors step 4 (dark)">

</details>
