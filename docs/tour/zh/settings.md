# 设置

主题、语言、计算设备、凭据、数据根目录。

构建于 v0.1.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/settings/01_settings_dark.png"><img src="../../assets/tour/settings/01_settings_light.png" width="900" alt="设置: result"></picture>

## 逐步操作

### 1. 设置：主题（浅色、深色、跟随系统）、语言、计算设备、存储模式、SNAPHU 可执行文件、底图 URL、数据根目录。

```bash
bosar gui
```

<img src="../../assets/tour/settings/01_settings_light.png" width="900" alt="设置 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/settings/01_settings_dark.png" width="900" alt="设置 step 1 (dark)">

</details>

### 2. 每个服务一个引导对话框：去哪注册、在哪找密钥、填入或从文件导入。值写进系统钥匙串，绝不进日志。

```bash
bosar auth set cds
```

<img src="../../assets/tour/settings/02_credentials_light.png" width="900" alt="设置 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/settings/02_credentials_dark.png" width="900" alt="设置 step 2 (dark)">

</details>
