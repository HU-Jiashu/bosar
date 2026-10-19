# 项目与数据

新建项目、导入影像栈，查看日期、基线和相干预览。

构建于 v0.1.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/project_data/03_preview_dark.png"><img src="../../assets/tour/project_data/03_preview_light.png" width="900" alt="项目与数据: result"></picture>

## 逐步操作

### 1. 打开或新建项目：项目文件夹存放产品、日志和 project.json。

```bash
bosar project new tour/indy_crop --name indy_crop
```

<img src="../../assets/tour/project_data/01_project_light.png" width="900" alt="项目与数据 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/project_data/01_project_dark.png" width="900" alt="项目与数据 step 1 (dark)">

</details>

### 2. 导入影像栈（GAMMA/StaMPS 导出、SAFE、BEAM-DIMAP 或裁剪）：日期、几何和基线图。

```bash
bosar data import tour/indy_crop data/indy_downtown_crop
```

<img src="../../assets/tour/project_data/02_stack_light.png" width="900" alt="项目与数据 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/project_data/02_stack_dark.png" width="900" alt="项目与数据 step 2 (dark)">

</details>

### 3. 一对影像的相干快速预览告诉你值不值得处理。

```bash
bosar data preview tour/indy_crop --pair 20240821_20240914
```

<img src="../../assets/tour/project_data/03_preview_light.png" width="900" alt="项目与数据 step 3">

<details><summary>深色主题</summary>

<img src="../../assets/tour/project_data/03_preview_dark.png" width="900" alt="项目与数据 step 3 (dark)">

</details>
