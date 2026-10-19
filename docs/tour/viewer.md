# Result viewer

Basemaps, layer opacity and masks, stretch, linked views, figure export, two chains compared.

Built in v0.2.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/viewer/02_satellite_mask_dark.png"><img src="../assets/tour/viewer/02_satellite_mask_light.png" width="900" alt="Result viewer: result"></picture>

## Step by step

### 1. The Layers panel: basemap, and per layer visibility, opacity 0-100 %, order and an optional coherence mask.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/viewer/01_layers_light.png" width="900" alt="Result viewer step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/viewer/01_layers_dark.png" width="900" alt="Result viewer step 1 (dark)">

</details>

### 2. Sentinel-2 cloudless basemap, the displacement at 50 % and hidden where the coherence is below 0.4.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/viewer/02_satellite_mask_light.png" width="900" alt="Result viewer step 2">

<details><summary>dark theme</summary>

<img src="../assets/tour/viewer/02_satellite_mask_dark.png" width="900" alt="Result viewer step 2 (dark)">

</details>

### 3. Any geocoded product can be laid over the map as a further layer and moved up or down.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/viewer/03_overlay_light.png" width="900" alt="Result viewer step 3">

<details><summary>dark theme</summary>

<img src="../assets/tour/viewer/03_overlay_dark.png" width="900" alt="Result viewer step 3 (dark)">

</details>

### 4. Stretch per view (percentile, min-max, manual, gamma), remembered per product kind; the two views pan and zoom together.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/viewer/04_stretch_linked_light.png" width="900" alt="Result viewer step 4">

<details><summary>dark theme</summary>

<img src="../assets/tour/viewer/04_stretch_linked_dark.png" width="900" alt="Result viewer step 4 (dark)">

</details>

### 5. "Export view" writes a PNG or PDF at the chosen DPI with legend, scale bar, north arrow and attribution; the CLI commands of the layers are in the file's metadata.

<img src="../assets/tour/viewer/05_figure_light.png" width="900" alt="Result viewer step 5">

<details><summary>dark theme</summary>

<img src="../assets/tour/viewer/05_figure_dark.png" width="900" alt="Result viewer step 5 (dark)">

</details>

### 6. Compare two chains: classic PSI points against the PS / DS velocity of the same stack - every point samples the cell that contains it; the difference in mm/yr on the map (diverging, centred at 0), the scatter with the 1:1 line, n, correlation, median difference (the two reference points) and MAD-std.

```bash
bosar gui tour/indy_crop
```

<img src="../assets/tour/viewer/06_compare_light.png" width="900" alt="Result viewer step 6">

<details><summary>dark theme</summary>

<img src="../assets/tour/viewer/06_compare_dark.png" width="900" alt="Result viewer step 6 (dark)">

</details>
