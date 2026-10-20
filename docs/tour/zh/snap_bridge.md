# SNAP 桥接

用 SNAP 作引擎预处理原始 Sentinel-1 zip，导入，处理。

构建于 v0.2.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/snap_bridge/03_result_dark.png"><img src="../../assets/tour/snap_bridge/03_result_light.png" width="900" alt="SNAP 桥接: result"></picture>

## 逐步操作

### 1. 引擎设为 snap 的配准：原始 Sentinel-1 zip、子条带和选 burst 的 AOI。SNAP 的 gpt 作为独立程序运行，用 Bosar 的轨道和 DEM；它写的一切都留在项目里。

```bash
bosar pipeline preprocess <project> --engine snap --product <S1 zip> … --subswath IW2 --aoi-wkt "POLYGON((…))"
```

<img src="../../assets/tour/snap_bridge/01_form_light.png" width="900" alt="SNAP 桥接 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/snap_bridge/01_form_dark.png" width="900" alt="SNAP 桥接 step 1 (dark)">

</details>

### 2. 配准后的栈及其干涉图作为 BEAM-DIMAP 栈导入；之后每个工作流都在它上面运行。

```bash
bosar data import <project> <stack.dim> --reader dimap --ifg-dim <ifg.dim>
```

<img src="../../assets/tour/snap_bridge/02_imported_light.png" width="900" alt="SNAP 桥接 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/snap_bridge/02_imported_dark.png" width="900" alt="SNAP 桥接 step 2 (dark)">

</details>

### 3. SNAP 预处理子集上的 DInSAR：DEM 框内的解缠相位和相干。

```bash
bosar pipeline dinsar <project> --stack snap_subset --pair 20240821_20240914
```

<img src="../../assets/tour/snap_bridge/03_result_light.png" width="900" alt="SNAP 桥接 step 3">

<details><summary>深色主题</summary>

<img src="../../assets/tour/snap_bridge/03_result_dark.png" width="900" alt="SNAP 桥接 step 3 (dark)">

</details>
