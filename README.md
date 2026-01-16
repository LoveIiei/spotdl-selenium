# Spotify to MP3 Downloader

A Python automation script that mimics `spotdl` functionality without using the Spotify API. This tool scrapes song names from a Spotify playlist URL using Selenium and downloads high-quality audio from YouTube using `yt-dlp`.

**⚠️ Disclaimer: This project is for educational and study purposes only.**

## Key Features
* **No API Keys Required:** Uses Web Scraping (Selenium) to fetch playlist data.
* **High Efficiency:** Use `yt-dlp` for fast, reliable downloads.
* **Smart Metadata:** Automatically embeds thumbnails, artist, and title tags into the MP3s.
* **Clean UI:** Uses `tqdm` for a professional progress bar and redirects internal warnings to a log file.

## Prerequisites

* **Python 3.8+**
* **Firefox driver** (The script automatically manages the driver version)
* **FFmpeg** (Must be installed and added to your system PATH for audio conversion)

## Installation

1.  **Clone the repository** (or create a new folder).
2.  **Install dependencies**:
    ```bash
    pip install requirements.txt
    ```
3.  **Verify FFmpeg**:
    Type `ffmpeg -version` in your terminal. If it's not recognized, install it manually.
4.  **Download a browser driver as per selenium webpage**
    ***This must be DONE*** Please download firefox driver at [driver](https://github.com/mozilla/geckodriver)