# SBAS 时间序列

速度与时间相干；点一个像元看它的形变历史。

构建于 v0.2.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/sbas_ts/03_time_series_dark.png"><img src="../../assets/tour/sbas_ts/03_time_series_light.png" width="900" alt="SBAS 时间序列: result"></picture>

## 逐步操作

### 1. 已准备网络的 SBAS 时间序列：基于闭合的解缠改正、逐像元反演、对流层改正、地理编码。

```bash
bosar pipeline sbas tour/indy_crop --network ts --tropo gacos
```

<img src="../../assets/tour/sbas_ts/01_run_light.png" width="900" alt="SBAS 时间序列 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_ts/01_run_dark.png" width="900" alt="SBAS 时间序列 step 1 (dark)">

</details>

### 2. 视线向速度 mm/yr（左，时间相干低于 0.7 处隐藏）和时间相干（右）。

```bash
bosar pipeline sbas tour/indy_crop --network ts --tropo gacos
```

<img src="../../assets/tour/sbas_ts/02_velocity_light.png" width="900" alt="SBAS 时间序列 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_ts/02_velocity_dark.png" width="900" alt="SBAS 时间序列 step 2 (dark)">

</details>

### 3. 点击像元：它们的视线向形变历史（mm）带线性拟合和速率；切换改正项，把曲线导出为 CSV。

```bash
bosar gui tour/indy_crop
```

<img src="../../assets/tour/sbas_ts/03_time_series_light.png" width="900" alt="SBAS 时间序列 step 3">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_ts/03_time_series_dark.png" width="900" alt="SBAS 时间序列 step 3 (dark)">

</details>

### 4. 雷达几何下的质量图层：网络连通且时间相干良好的像元掩膜，以及经过相干、连通分量和闭合规则后每个像元用到的像对数。

```bash
bosar pipeline sbas tour/indy_crop --network ts --tropo gacos
```

<img src="../../assets/tour/sbas_ts/04_quality_light.png" width="900" alt="SBAS 时间序列 step 4">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_ts/04_quality_dark.png" width="900" alt="SBAS 时间序列 step 4 (dark)">

</details>
