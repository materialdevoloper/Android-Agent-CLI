# Android Agent Actuation CLI (A³ CLI)

[English](README.md) | [中文](README_zh.md)

A deterministic, lightweight, and robust UI automation framework for Android, designed specifically as the **Actuation Layer** for Large Language Model (LLM) GUI Agents. 

## 🚀 Why this exists? (The LLM AppAgent Dilemma)
Currently, popular GitHub projects like Tencent's `AppAgent` or Alibaba's `Mobile-Agent` rely entirely on sending screenshots to Multimodal LLMs (like GPT-4V) for *every single interaction* (e.g., "Scroll down", "Is this the bottom?"). 
This is **slow**, **expensive**, and **error-prone**.

**A³ CLI** solves this by providing a deterministic CLI toolkit that handles the heavy lifting of physical Android interactions locally:
- Physical Tap/Swipe (Native Input Events)
- Smart Auto-Scrolling & Image Stitching
- Instant UI XML DOM Extraction

Your LLM only needs to issue high-level commands (`python cli.py maps scrape-details`), and this framework will autonomously scroll, stitch, and return the final aggregated data back to the LLM. 

**Zero Root Required.** All operations run on native ADB (Android Debug Bridge).

## 🛠️ Toolchain Structure
The matrix currently supports plug-and-play CLI modules for various apps:

- **`utils_cli`**: The core vision engine. Includes `auto_scroller.py` for infinite pixel-comparison scrolling and vertical image stitching.
- **`adb_core.py`**: The central nervous system for ADB commands (`screencap`, `dump_ui`, `swipe`, `tap`).
- **`maps_cli`**: Automates Google Maps. Perform searches, sort by distance/ratings, and extract specific place details into a single stitched infographic.
- **`grab_cli`**: Automates food delivery menus. Deep-links into merchant pages and autonomously scans the entire menu.
- **`play_cli`**: Automates the Google Play Store for autonomous app installation and intent resolution.

## ⚙️ Quick Start

### Prerequisites
1. Android Device or Emulator connected via USB/WiFi.
2. Developer Options -> **USB Debugging** Enabled.
3. Python 3.10+ and `Pillow` library.

### Example: Scraping a Bar on Google Maps
```bash
# 1. Search for a specific place
python maps_cli/cli.py search --query "cocktail bar"

# 2. Sort by highest rated
python maps_cli/cli.py sort --by top_rated

# 3. Enter the venue and extract the entire review/photo timeline into one image!
python maps_cli/cli.py scrape-details --auto
```

## 🛡️ Anti-Ban Architecture
Because A³ CLI utilizes system-level Android events instead of API scraping or HTTP interception, it is completely immune to traditional network-level anti-bot protections (like Cloudflare or SSL Pinning). To the server, the traffic looks identical to a real human thumb.

## 🤝 Contributing
Feel free to build new modules (`tinder_cli`, `tiktok_cli`, etc.) by extending the `adb_core.py` and submitting a Pull Request!
