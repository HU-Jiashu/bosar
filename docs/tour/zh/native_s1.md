# 原生 Sentinel-1 处理

不用 SNAP，从原始 Sentinel-1 zip 到配准影像栈——burst、去斜、几何配准、ESD、定标、子条带拼接——再在其上做多年 PS / DS 时间序列。

构建于 v0.3.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/native_s1/04_multi_year_dark.png"><img src="../../assets/tour/native_s1/04_multi_year_light.png" width="900" alt="原生 Sentinel-1 处理: result"></picture>

## 逐步操作

### 1. 配准（Bosar）：从原始 zip 开始的原生链路——由注记建 burst 模型、精密轨道和 DEM 算偏移、去斜、sinc 重采样、加斜、距离向检查、增强谱分集、去 burst。定标后的 sigma nought 和地形平坦化的 gamma nought 作为额外图层写出；加入更多 zip 重跑只配准新日期。

```bash
bosar pipeline s1-coregister <project> --product <S1 zip> … --subswath IW2 --aoi-wkt "POLYGON((…))" --calibration sigma0 --terrain-flatten
```

<img src="../../assets/tour/native_s1/01_form_light.png" width="900" alt="原生 Sentinel-1 处理 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/native_s1/01_form_dark.png" width="900" alt="原生 Sentinel-1 处理 step 1 (dark)">

</details>

### 2. 三个子条带：各自配准，再拼到同一个距离 / 方位格网上，切口在每段重叠的中间；接缝检查报告每条切口两侧的相位和幅度跳变。

```bash
bosar pipeline s1-coregister <project> --product <S1 zip> … --subswath IW1,IW2,IW3 --tag full
```

<img src="../../assets/tour/native_s1/02_merge_light.png" width="900" alt="原生 Sentinel-1 处理 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/native_s1/02_merge_dark.png" width="900" alt="原生 Sentinel-1 处理 step 2 (dark)">

</details>

### 3. 原生链路写出的多年栈（CINT16，ISCE 布局），像其他栈一样导入：Sentinel-1A 和 Sentinel-1D 的日期在同一参考格网上。

```bash
bosar pipeline s1-coregister <project> --products-from <folder> --crop-wkt "POLYGON((…))" --tag multi
```

<img src="../../assets/tour/native_s1/03_stack_light.png" width="900" alt="原生 Sentinel-1 处理 step 3">

<details><summary>深色主题</summary>

<img src="../../assets/tour/native_s1/03_stack_dark.png" width="900" alt="原生 Sentinel-1 处理 step 3 (dark)">

</details>

### 4. 原生栈上两年的印第安纳波利斯市中心（52 个日期，Sentinel-1A 和 1D）：PS / DS 速度，永久散射体为点，以及点击像元的形变历史。没有超出噪声的运动（离散 1.4 mm/yr，按时间跨度预期 1.1）；河西的红色块是跨相干间隙的解缠伪影——经典 PSI 链路里没有它。

```bash
bosar pipeline psds <project> --stack native_multi --tropo era5 --no-correct --keep-unclosed
```

<img src="../../assets/tour/native_s1/04_multi_year_light.png" width="900" alt="原生 Sentinel-1 处理 step 4">

<details><summary>深色主题</summary>

<img src="../../assets/tour/native_s1/04_multi_year_dark.png" width="900" alt="原生 Sentinel-1 处理 step 4 (dark)">

</details>
