# M3U8 Downloader Pro

A powerful, modern, multi-threaded GUI application for downloading video streams, HLS (m3u8), and YouTube playlists at maximum resolution. Built with Python, `customtkinter`, `yt-dlp`, and `playwright`.

![M3U8 Downloader Pro Showcase](https://img.shields.io/badge/Status-Active-brightgreen) ![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![License MIT](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **Modern & Responsive UI**: Clean dark mode interface built with `customtkinter`. Dynamically expands to show up to 20-30 concurrent downloads beautifully.
- **Multi-threaded Downloading**: Download multiple video streams simultaneously without freezing the UI.
- **Auto-Capture Web Sniffer**: Built-in persistent Chromium browser powered by Playwright. Browse websites and the app automatically captures hidden `.m3u8` video streams in the background. Continuously listens for links when navigating through playlists!
- **Highest Resolution Priority**: Intelligently searches and merges the _best_ available video (up to 4K) and audio streams using `ffmpeg`.
- **Intelligent Overwrites**: Automatically replaces old low-res files with new high-res versions without throwing errors.
- **Smart Directory Persistence**: Remembers your designated download folder between sessions.
- **OS Notifications**: Get native system alerts when a stream is sniffed or a download completes.
- **Cross-Platform**: Designed and tested specifically for Linux (Ubuntu/GNOME, Hyprland), but fully cross-platform for Windows and Mac.

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have Python 3.10+ and `ffmpeg` installed on your system.

```bash
# On Debian/Ubuntu
sudo apt install ffmpeg python3 python3-pip python3-venv

# On Arch/Hyprland
sudo pacman -S ffmpeg python python-pip
```

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/otakus007/m3u8-downloader.git
cd m3u8-downloader

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Browser Sniffer

To use the auto-capture feature, you must install Playwright browsers:

```bash
playwright install chromium
```

### 4. Run the App

Start the GUI:

```bash
python main.py
```

## 🎮 How to Use

1. **Direct Download**: Paste a `.m3u8` URL or a YouTube playlist URL into the address bar, enter an optional name, and click **Download**.
2. **Auto-Capture Mode**: Click **🌐 Auto-Capture Browser**. A clean browser window will open. Navigate to the website hosting the target video. As soon as the video player requests the stream, the app will instantly snatch the URL and notify you. Close the browser anytime and click Download!
3. **Track Progress**: Multi-threaded progress bars will show percentage, ETA, and speed for each concurrent download.

## 🛠️ Configuration

The application automatically creates a lightweight configuration file at `~/.m3u8_downloader_config.json` to persist your last-used download directory.

## 🏗️ Architecture

- **GUI Layer**: `customtkinter` for smooth UI rendering.
- **Core Downloader**: `yt-dlp` running on daemon threads.
- **Browser Sniffer**: `playwright` with ad-blocker configurations and continuous networking interception.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
