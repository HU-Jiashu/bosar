# GACOS 对流层改正

缺什么、带 --tropo gacos 的运行、改正前后的形变。

构建于 v0.2.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/gacos/04_before_after_dark.png"><img src="../../assets/tour/gacos/04_before_after_light.png" width="900" alt="GACOS 对流层改正: result"></picture>

## 逐步操作

### 1. 辅助数据页：项目已有什么——轨道、DEM、GACOS 格网——以及各自来自哪里。

```bash
bosar aux status tour/indy_crop
```

<img src="../../assets/tour/gacos/01_aux_light.png" width="900" alt="GACOS 对流层改正 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/gacos/01_aux_dark.png" width="900" alt="GACOS 对流层改正 step 1 (dark)">

</details>

### 2. 运行前助手只列出这次运行需要的：哪些自动、哪些需要你（GACOS 申请）。

```bash
bosar aux status tour/indy_crop --for dinsar+gacos
```

<img src="../../assets/tour/gacos/02_assistant_light.png" width="900" alt="GACOS 对流层改正 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/gacos/02_assistant_dark.png" width="900" alt="GACOS 对流层改正 step 2 (dark)">

</details>

### 3. 勾选 GACOS 改正：tropo_gacos 步骤在形变之前加入链路。

```bash
bosar pipeline dinsar tour/indy_crop --stack crop_indy_downtown_crop --pair 20240821_20240914 --tropo gacos --tag gacos
```

<img src="../../assets/tour/gacos/03_run_light.png" width="900" alt="GACOS 对流层改正 step 3">

<details><summary>深色主题</summary>

<img src="../../assets/tour/gacos/03_run_dark.png" width="900" alt="GACOS 对流层改正 step 3 (dark)">

</details>

### 4. 左侧未改正，右侧 GACOS 改正后，两个视图联动。

```bash
bosar gui tour/indy_crop
```

<img src="../../assets/tour/gacos/04_before_after_light.png" width="900" alt="GACOS 对流层改正 step 4">

<details><summary>深色主题</summary>

<img src="../../assets/tour/gacos/04_before_after_dark.png" width="900" alt="GACOS 对流层改正 step 4 (dark)">

</details>
