# 日志与失败

每次运行及其 UTC 时间戳记录；失败卡片说明出了什么、在哪里、怎么办。

构建于 v0.1.0。[返回导览](README.md)

4K 截图、点击位置动画和 DInSAR 录屏在 [Releases](https://github.com/HU-Jiashu/bosar/releases) 的 `bosar-tour-4k.zip` 里；页面上是同一批截图的 1080p 版本。

## 结果

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tour/logs/02_failure_dark.png"><img src="../../assets/tour/logs/02_failure_light.png" width="900" alt="日志与失败: result"></picture>

## 逐步操作

### 1. 日志页：每次运行及其记录——UTC 时间戳、步骤、级别、参数、输入、输出、耗时。

```bash
bosar logs tour/indy_crop --tail 3
```

<img src="../../assets/tour/logs/01_runs_light.png" width="900" alt="日志与失败 step 1">

<details><summary>深色主题</summary>

<img src="../../assets/tour/logs/01_runs_dark.png" width="900" alt="日志与失败 step 1 (dark)">

</details>

### 2. 失败的步骤显示一张卡片：错误码、哪里错了、在哪里，以及修复提示。

```bash
bosar logs tour/indy_crop --level ERROR
```

<img src="../../assets/tour/logs/02_failure_light.png" width="900" alt="日志与失败 step 2">

<details><summary>深色主题</summary>

<img src="../../assets/tour/logs/02_failure_dark.png" width="900" alt="日志与失败 step 2 (dark)">

</details>
