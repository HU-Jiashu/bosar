# SLC 下载

按影像栈的轨道和帧或 AOI 在 ASF 搜索 Sentinel-1 景；先试运行，再做可续传、带校验、会话结束后仍继续的下载。

构建于 v0.3.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/fetch_slc/01_card_dark.png"><img src="../../assets/tour/fetch_slc/01_card_light.png" width="900" alt="SLC 下载: result"></picture>

## 逐步操作

### 1. Sentinel-1 SLC 景（ASF）：影像栈的相对轨道、帧和足迹选出各日期范围的景；试运行列出它们和大小，下载可续传、校验大小和 MD5、为每景写来源文件、低于剩余空间阈值时停下、会话结束后仍继续（`bosar fetch status`）。

```bash
bosar fetch slc tour/indy_crop --range 2025-08-01:2026-09-30 --range 2023-07-01:2024-06-30 --dest data/raw/s1 --dry-run
```

<img src="../../assets/tour/fetch_slc/01_card_light.png" width="900" alt="SLC 下载 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/fetch_slc/01_card_dark.png" width="900" alt="SLC 下载 step 1 (dark)">

</details>
