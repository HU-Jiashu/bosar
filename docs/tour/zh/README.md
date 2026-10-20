# Bosar 功能导览与教程

今天能用的每个模块：先看结果，再从头看每一步。截图由 `scripts/gui_tour.py` 在每次发布时从真实程序生成（印第安纳波利斯市中心的一小块裁剪），所以它们始终与代码一致。浅色 / 深色跟随你的 GitHub 主题。[English](../README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## [项目与数据](project_data.md)

新建项目、导入影像栈，查看日期、基线和相干预览。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/project_data/03_preview_dark.png"><img src="../../assets/tour/project_data/03_preview_light.png" width="560" alt="项目与数据"></picture>](project_data.md)

## [系统检查](system_check.md)

预检表：Python、GPU、SNAPHU、SNAP、凭据、只读数据根目录。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/system_check/01_preflight_dark.png"><img src="../../assets/tour/system_check/01_preflight_light.png" width="560" alt="系统检查"></picture>](system_check.md)

## [DInSAR 差分干涉](dinsar.md)

选一对影像、设参数、运行，在地图上读视线向形变。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/dinsar/04_result_dark.png"><img src="../../assets/tour/dinsar/04_result_light.png" width="560" alt="DInSAR 差分干涉"></picture>](dinsar.md)

## [GACOS 对流层改正](gacos.md)

缺什么、带 --tropo gacos 的运行、改正前后的形变。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/gacos/04_before_after_dark.png"><img src="../../assets/tour/gacos/04_before_after_light.png" width="560" alt="GACOS 对流层改正"></picture>](gacos.md)

## [相干变化检测](ccd.md)

事件前与跨事件像对、运行、叠在卫星影像上的损毁代理图。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/ccd/03_dpm_dark.png"><img src="../../assets/tour/ccd/03_dpm_light.png" width="560" alt="相干变化检测"></picture>](ccd.md)

## [幅度变化](amplitude.md)

对数比值和前后 RGB 合成，叠在底图上。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/amplitude/03_rgb_dark.png"><img src="../../assets/tour/amplitude/03_rgb_light.png" width="560" alt="幅度变化"></picture>](amplitude.md)

## [结果查看器](viewer.md)

底图、图层透明度与掩膜、拉伸、联动视图、出图，两条链路对比。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/viewer/02_satellite_mask_dark.png"><img src="../../assets/tour/viewer/02_satellite_mask_light.png" width="560" alt="结果查看器"></picture>](viewer.md)

## [SBAS 准备](sbas_prep.md)

网络设计器、派生像对、批量解缠、闭合图。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/sbas_prep/03_closure_dark.png"><img src="../../assets/tour/sbas_prep/03_closure_light.png" width="560" alt="SBAS 准备"></picture>](sbas_prep.md)

## [SBAS 时间序列](sbas_ts.md)

速度与时间相干；点一个像元看它的形变历史。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/sbas_ts/03_time_series_dark.png"><img src="../../assets/tour/sbas_ts/03_time_series_light.png" width="560" alt="SBAS 时间序列"></picture>](sbas_ts.md)

## [PS / DS 时间序列](psds.md)

分布式散射体相位连接加永久散射体：覆盖是多视 SBAS 的数倍，并给出质量判定。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/psds/04_result_dark.png"><img src="../../assets/tour/psds/04_result_light.png" width="560" alt="PS / DS 时间序列"></picture>](psds.md)

## [经典 PS-InSAR](psi.md)

周期图链路（幅度离差、弧段、APS）作为运行页的一个工作流；它的 GeoPackage 是结果页的点图层。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/psi/01_run_dark.png"><img src="../../assets/tour/psi/01_run_light.png" width="560" alt="经典 PS-InSAR"></picture>](psi.md)

## [SNAP 桥接](snap_bridge.md)

用 SNAP 作引擎预处理原始 Sentinel-1 zip，导入，处理。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/snap_bridge/03_result_dark.png"><img src="../../assets/tour/snap_bridge/03_result_light.png" width="560" alt="SNAP 桥接"></picture>](snap_bridge.md)

## [SLC 下载](fetch_slc.md)

按影像栈的轨道和帧或 AOI 在 ASF 搜索 Sentinel-1 景；先试运行，再做可续传、带校验、会话结束后仍继续的下载。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/fetch_slc/01_card_dark.png"><img src="../../assets/tour/fetch_slc/01_card_light.png" width="560" alt="SLC 下载"></picture>](fetch_slc.md)

## [日志与失败](logs.md)

每次运行及其 UTC 时间戳记录；失败卡片说明出了什么、在哪里、怎么办。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/logs/02_failure_dark.png"><img src="../../assets/tour/logs/02_failure_light.png" width="560" alt="日志与失败"></picture>](logs.md)

## [设置](settings.md)

主题、语言、计算设备、凭据、数据根目录。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/settings/01_settings_dark.png"><img src="../../assets/tour/settings/01_settings_light.png" width="560" alt="设置"></picture>](settings.md)

## [原生 Sentinel-1 处理](native_s1.md)

不用 SNAP，从原始 Sentinel-1 zip 到配准影像栈——burst、去斜、几何配准、ESD、定标、子条带拼接——再在其上做多年 PS / DS 时间序列。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/native_s1/04_multi_year_dark.png"><img src="../../assets/tour/native_s1/04_multi_year_light.png" width="560" alt="原生 Sentinel-1 处理"></picture>](native_s1.md)

## [更多传感器](sensors.md)

ALOS-1 PALSAR（L 波段）、ENVISAT ASAR 和 ERS-1/2 走条带链路：带传感器信息的影像栈、L 波段质量配置、各一幅墨西哥城干涉图。

[<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/sensors/03_alos_pair_dark.png"><img src="../../assets/tour/sensors/03_alos_pair_light.png" width="560" alt="更多传感器"></picture>](sensors.md)

## 安装程序 

Releases 页面上的 Windows .exe 与 macOS .dmg 安装程序；GPU 以插件方式加入。
