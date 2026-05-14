# Android Agent Actuation CLI (A³ CLI)

[English](README.md) | [中文](README_zh.md)

这是一个确定性、轻量级且极具鲁棒性的 Android 自动化框架，专门设计作为大语言模型（LLM）GUI Agent 的**底层执行器 (Actuation Layer)**。

## 🚀 为什么要有这个项目？
目前 GitHub 上流行的大模型 Agent 项目（如腾讯的 `AppAgent` 或阿里的 `Mobile-Agent`）通常严重依赖多模态大模型（如 GPT-4V）来处理**每一次交互**。大模型不仅需要判断“我现在应该点哪里”，甚至连“页面滑到底了吗？”都要通过截图去问模型。
这导致整个流程**极度缓慢**、**极其昂贵**，且**容易出错**。

**A³ CLI** 解决这个问题的思路是：把物理设备交互的“脏活累活”在本地完全确定性地解决掉。
- 物理级的精准触控与滑动
- 智能防抖长图无缝拼接（利用纯像素比对探底，0 Token 消耗）
- 零延迟的 UI XML 树结构提取

你的 LLM 只需要下达极具抽象度的高层指令（例如：`python cli.py maps scrape-details`），A³ CLI 就能完全自动地执行滚动、缝合截图，并把最终的高清超长数据喂回给 LLM。

**完全免 Root (Zero Root Required)。** 所有的操作完全基于原生的 ADB (Android Debug Bridge)。

## 🛠️ 工具链架构
本矩阵目前支持多个即插即用的 CLI 模块：

- **`utils_cli`**: 核心视觉引擎，包含 `auto_scroller.py`，用于无限像素比对滚动和图片缝合。
- **`adb_core.py`**: ADB 中枢神经系统，用于发送截图、获取节点、滑动、点击指令。
- **`maps_cli`**: 谷歌地图自动化模块。支持自动搜索、自动按评分/距离进行排序筛选，并能一键抓取某家店铺所有的评价和图片生成超长图。
- **`grab_cli`**: 外卖自动化模块。支持深度链接直达店铺并全自动扫描捕获菜单长图。
- **`play_cli`**: 谷歌商店自动化模块。

## ⚙️ 快速开始

### 环境依赖
1. 连上 USB 或通过局域网无线连接的安卓手机/模拟器。
2. 手机设置中开启了**开发者模式**与**USB 调试**。
3. Python 3.10+ 和 `Pillow` 库。

*(如果连接了多台设备，请设置环境变量 `ADB_DEVICE_ID` 来指定操作设备)*

### 示例代码：在 Google Maps 抓取酒吧信息
```bash
# 1. 自动输入并搜索
python maps_cli/cli.py search --query "cocktail bar"

# 2. 自动点击页面排序按钮，筛选出评价最高的店
python maps_cli/cli.py sort --by top_rated

# 3. 自动向下滑动抓取该店所有详情，并拼接为一张完整长图！
python maps_cli/cli.py scrape-details --auto
```

## 🛡️ 反风控架构
因为 A³ CLI 直接利用安卓系统底层的输入事件，而非逆向 API 或挂载中间人抓包（HTTP Interception），因此它完全免疫传统的网络层反爬虫保护（如 Cloudflare 验证码、SSL Pinning 证书绑定）。在服务器看来，这完全是一个真实人类的手指在滑动屏幕。

## 🤝 贡献代码
欢迎基于 `adb_core.py` 扩展编写出你自己的新模块（如 `tinder_cli`, `tiktok_cli` 等等），并提交 Pull Request！
