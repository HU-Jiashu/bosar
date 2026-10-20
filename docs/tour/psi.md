# Classic PS-InSAR

The periodogram chain (amplitude dispersion, arcs, APS) as a workflow of the Run page; its GeoPackage is a point layer of the Results page.

Built in v0.3.0. [Back to the tour](README.md)

The screenshots at 4K, the where-to-click animations and the DInSAR recording are in `bosar-tour-4k.zip` under [Releases](https://github.com/HU-Jiashu/bosar/releases); the pages show the same screenshots at 1080p.

## Result

<picture><source media="(prefers-color-scheme: dark)" srcset="../assets/tour/psi/01_run_dark.png"><img src="../assets/tour/psi/01_run_light.png" width="900" alt="Classic PS-InSAR: result"></picture>

## Step by step

### 1. Classic PS-InSAR as a workflow: persistent-scatterer candidates by amplitude dispersion, a Delaunay network, the periodogram on every arc (height error and rate at once), integration from a reference point, the atmospheric screen - an independent check of the PS / DS chain on the same flattened stack.

```bash
bosar pipeline psi tour/indy_crop --stack crop_indy_downtown_ts
```

<img src="../assets/tour/psi/01_run_light.png" width="900" alt="Classic PS-InSAR step 1">

<details><summary>dark theme</summary>

<img src="../assets/tour/psi/01_run_dark.png" width="900" alt="Classic PS-InSAR step 1 (dark)">

</details>
