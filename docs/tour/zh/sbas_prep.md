# SBAS 准备

网络设计器、派生像对、批量解缠、闭合图。

构建于 v0.2.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/sbas_prep/03_closure_dark.png"><img src="../../assets/tour/sbas_prep/03_closure_light.png" width="900" alt="SBAS 准备: result"></picture>

## 逐步操作

### 1. SBAS 准备：设计网络（时间和垂直基线限制加顺序连接）或导入 CSV；图上显示选中的像对。

```bash
bosar sbas network tour/indy_crop --stack crop_indy_downtown_ts --name ts --max-dt 36 --max-bperp 200 --k 3
```

<img src="../../assets/tour/sbas_prep/01_network_light.png" width="900" alt="SBAS 准备 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_prep/01_network_dark.png" width="900" alt="SBAS 准备 step 1 (dark)">

</details>

### 2. 一条命令从星形栈派生每个像对、多视、估计相干、选公共参考像元、解缠并检查三元组闭合——可续跑，多进程并行。

```bash
bosar sbas prep tour/indy_crop --network ts --looks 2,10 --backend snaphu --workers 6
```

<img src="../../assets/tour/sbas_prep/02_prep_light.png" width="900" alt="SBAS 准备 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_prep/02_prep_dark.png" width="900" alt="SBAS 准备 step 2 (dark)">

</details>

### 3. 闭合图：缠绕闭合的 RMS（相位偏差）和不闭合的三元组数（解缠误差）。

```bash
bosar sbas prep tour/indy_crop --network ts --looks 2,10 --backend snaphu --workers 6
```

<img src="../../assets/tour/sbas_prep/03_closure_light.png" width="900" alt="SBAS 准备 step 3">

<details><summary>深色主题</summary>

<img src="../../assets/tour/sbas_prep/03_closure_dark.png" width="900" alt="SBAS 准备 step 3 (dark)">

</details>
