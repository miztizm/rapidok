# CLAUDE.md — Rapidok

> ⚡ Concurrent TikTok downloader — videos, images, audio, organized by creator.

Rapidok is a Python CLI that downloads TikTok content (with or without watermark) using `yt-dlp`, processing many URLs or whole profiles concurrently and auto-organizing output by creator and content type, with a Rich terminal UI. See [README.md](README.md).

## Future Vision

Rapidok becomes the reliable, no-nonsense archival tool for TikTok — point it at a username or a list of URLs and get a clean, deduplicated, metadata-rich local library that survives TikTok's constant format changes. It stays fast through concurrency, forgiving through robust error recovery, and honest through detailed logs, so archival and research never stall on a broken download.

**How we build it:** resilience over cleverness — keep pace with TikTok changes by leaning on `yt-dlp`, degrade gracefully and log failures with detail, skip what's already downloaded, and keep the concurrent pipeline and Rich output fast and legible; clean, broadly-compatible Python (3.6+) — in code we trust.

## Stack & structure

- Python 3.6+, packaged as `rapidok` on PyPI; entry point `rapidok = rapidok.main:main`.
- Deps: `yt-dlp`, `tqdm`, `urllib3`, `requests`, `rich`.
- Source in `rapidok/` (`main.py`); tests in `tests/`; batch input via `urls.txt`; downloads land in `downloads/`.
- Formatting/lint: black + pylint (line-length 100).
