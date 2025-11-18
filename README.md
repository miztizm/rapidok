# Rapidok
### *TikTok Content Downloader by miztizm*

A robust, concurrent TikTok content downloader built with Python and `yt-dlp`. Download videos, images, and audio with or without watermarks, process multiple URLs simultaneously, and organize downloads automatically by creator.

---

## 🎯 What This Does

This application streamlines the process of downloading TikTok videos for archival, content analysis, or offline viewing. It handles batch downloads efficiently with concurrent processing, intelligent error handling, and automatic organization by TikTok creator username.

**Key Capabilities:**
- **Concurrent Downloads**: Process multiple videos simultaneously with configurable worker threads
- **Profile Downloader**: Download ALL videos from a user's profile with just their username
- **Smart Content Filtering**: Choose what to download - videos only, images, or everything
- **Metadata Extraction**: Save comprehensive post information (titles, descriptions, stats) as structured JSON
- **Watermark Control**: Choose between watermarked or clean versions
- **Skip Existing Files**: Automatically skip files that have already been downloaded
- **Auto-Organization**: Videos automatically sorted into folders by creator username and content type
- **Archive Tracking**: Prevent re-downloading videos you already have
- **Image Download**: Extract high-quality images from TikTok photo carousel/slideshow posts
- **Robust Error Handling**: Failed downloads are logged with detailed errors for troubleshooting
- **Color-Coded Output**: Green for success, yellow for skipped, red for errors
- **Modern Backend**: Powered by `yt-dlp` for reliable, up-to-date TikTok support

---

## 🎮 What You'll Find Here

### **Technical Features**
- **Concurrent Processing**: Thread-pool executor for parallel downloads
- **Format Selection**: Intelligent format detection for watermarked/non-watermarked variants
- **SSL Handling**: Configured for compatibility across different Python/OS environments
- **URL Validation**: Input sanitization and format checking
- **Error Recovery**: Graceful degradation with detailed error logging
- **Progress Tracking**: Real-time download status updates

### **Use Cases**
- Content archival and backup
- Social media research and analysis
- Offline content curation
- Educational resource collection
- Digital preservation

---

## 💻 Installation

### **Requirements**
- Python 3.6 or higher: [Download Python](https://www.python.org/downloads/)
- pip (Python package manager)

### **Method 1: Install from PyPI (Recommended)**

Install rapidok directly from PyPI using pip:

```bash
pip install rapidok
```

After installation, you can run the tool using the `rapidok` command:

```bash
# Download from a profile
rapidok --profile username

# Download from URLs
rapidok --links urls.txt

# Show help
rapidok --help
```

### **Method 2: Install from Source**

If you want to install from source or contribute to development:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/miztizm/rapidok
   cd rapidok
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Create venv
   python -m venv venv

   # Activate
   # Windows:
   .\venv\Scripts\activate

   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install in Development Mode**
   ```bash
   pip install -e .
   ```

   Or install dependencies only:
   ```bash
   pip install -r requirements.txt
   # Then run with: python run.py
   ```

---

## 🚀 Usage

The downloader supports **two modes**: batch URL downloads and profile downloads!

> **Note**: If you installed via PyPI, use the `rapidok` command. If running from source, use `python run.py` instead.

### **Mode 1: Batch URL Downloads**

Download specific videos from a list of URLs:

1. Create a text file with TikTok URLs (one per line):
   ```
   https://www.tiktok.com/@miztizm/video/7271696847486455072
   https://www.tiktok.com/@miztizm/video/7130689108988448006
   ```

2. Run the downloader:
   ```bash
   rapidok --links urls.txt
   ```

### **Batch Download Options:**
```bash
# Basic download with safe defaults (2 workers, 2s delay)
rapidok --links urls.txt

# Custom URL file with balanced settings
rapidok --links my_urls.txt --workers 3 --delay 2.5

# Conservative approach for large batches
rapidok --links large_batch.txt --workers 1 --delay 5 --throttle-rate 1M

# Download with watermarks (faster - less format selection)
rapidok --links urls.txt --watermark --workers 2
```

### **Mode 2: Profile Downloads**

Download content from a TikTok user's profile with powerful filtering options:

```bash
# Download videos only (default behavior - skips audio-only posts)
rapidok --profile miztizm

# Download ALL content types (videos, audio, images, metadata)
rapidok --profile miztizm --content-type all

# Download only audio posts (photo slideshows with voiceover)
rapidok --profile miztizm --content-type audio-only

# Download only image posts
rapidok --profile miztizm --content-type images-only

# Extract metadata only (no downloads, just save post info as JSON)
rapidok --profile miztizm --content-type metadata-only

# Combine with other options
rapidok --profile miztizm --content-type all --max-downloads 20 --output-dir my_archive
```

**Content Type Options:**
- `video-only` (default): Downloads only actual video posts with video streams
- `audio-only`: Downloads only audio posts (rare - pure audio with no images)
- `images-only`: Downloads thumbnail images from TikTok photo carousel/slideshow posts
- `all`: Downloads everything - videos, images, AND saves metadata JSON
- `metadata-only`: Extracts and saves post information without downloading media

**How Image Downloads Work:**
TikTok photo carousel posts (slideshows with background music) don't provide individual images through yt-dlp's standard extraction. Instead, our downloader:
- Detects slideshow posts automatically
- Extracts high-quality thumbnail images from the post metadata
- Saves them as JPG files in the `images/` folder
- Works with `images-only` or `all` content type modes

**Profile Mode Features:**
- ✅ Automatically downloads ALL content from a user's profile
- ✅ Smart filtering by content type (videos, images, audio, or all)
- ✅ Organized folder structure: `miztizm/videos/`, `miztizm/images/`
- ✅ Image extraction from photo carousel/slideshow posts
- ✅ Metadata saved as JSON with post details, stats, timestamps, and thumbnails
- ✅ Archive tracking prevents re-downloading
- ✅ Supports usernames with or without @ prefix
- ✅ Automatic retry and error handling

**Output Structure for "all" mode:**
```
downloads/
└── username/
    ├── videos/
    │   ├── 0001_video_title_[id].mp4
    │   └── ...
    ├── images/
    │   ├── 0001_photo_carousel_title_[id].jpg
    │   └── ...
    ├── username_metadata.json  (comprehensive post information)
    └── archive.txt  (tracks downloaded items)
```

### **Command-Line Options**

```
usage: rapidok [-h] [--links LINKS | --profile PROFILE]
               [--no-watermark | --watermark] [--workers WORKERS]
               [--output-dir OUTPUT_DIR] [--max-downloads MAX_DOWNLOADS]
               [--no-archive] [--content-type {all,video-only,audio-only,images-only,metadata-only}]

Mode Selection (choose one):
  --links LINKS         Path to .txt file with TikTok URLs for batch download
  --profile PROFILE     TikTok username to download content from user profile

Common Options:
  --no-watermark        Download videos without watermarks (Default)
  --watermark           Download videos with watermarks
  --workers WORKERS     Number of concurrent downloads for batch mode (Default: 2, Max safe: 5)
  --output-dir OUTPUT_DIR
                        Output directory (Default: downloads)
  --max-downloads MAX_DOWNLOADS
                        Maximum items to download/process (profile mode only)
  --no-archive          Disable archive tracking (profile mode)
  --skip-existing       Skip downloading files that already exist
  --save-metadata       Save detailed metadata for each downloaded item as JSON

Rate Limiting & Safety:
  --delay SECONDS       Delay between downloads in seconds (Default: 2.0, adds ±50% random jitter)
  --min-delay SECONDS   Minimum delay between downloads (use with --max-delay for custom range)
  --max-delay SECONDS   Maximum delay between downloads (use with --min-delay for custom range)
  --throttle-rate SPEED Limit download speed (e.g., 500K, 1M, 2M for bytes/sec)
  --no-rate-limit       ⚠️ DISABLE ALL LIMITS (NOT RECOMMENDED - high risk of IP ban)

Profile Mode Filtering:
  --content-type {all,video-only,audio-only,images-only,metadata-only}
                        Type of content to download (Default: video-only)
                        - video-only: Only video posts with video streams
                        - audio-only: Only audio posts (rare - pure audio)
                        - images-only: Only image posts (photo carousels/slideshows)
                        - all: Everything (videos + images + metadata JSON)
                        - metadata-only: Extract post info without downloading media
```

### **Examples**

**Profile Downloads:**
```bash
# Download all videos from a user (default - video posts only)
rapidok --profile miztizm

# Download latest 20 videos only
rapidok --profile miztizm --max-downloads 20

# Download ALL content types (videos + images + metadata)
rapidok --profile miztizm --content-type all

# Download only image posts (photo carousels/slideshows)
rapidok --profile miztizm --content-type images-only

# Extract metadata only (titles, descriptions, stats) without downloads
rapidok --profile miztizm --content-type metadata-only

# Save detailed metadata JSON files for each download
rapidok --profile miztizm --content-type all --save-metadata

# Skip files that already exist (resume interrupted downloads)
rapidok --profile miztizm --skip-existing

# Download to custom directory without watermarks
rapidok --profile miztizm --output-dir my_collection --content-type all
```

**Batch URL Downloads:**
```bash
# Download videos from links.txt with safe defaults
rapidok --links urls.txt

# Custom file with rate limiting
rapidok --links urls.txt --workers 2 --delay 3

# Conservative mode for avoiding blocks
rapidok --links urls.txt --workers 1 --delay 5 --throttle-rate 500K

# Download with watermarks and skip existing files
rapidok --links urls.txt --watermark --skip-existing

# Save metadata for all downloads with safe settings
rapidok --links urls.txt --save-metadata --delay 2.5
```

---

## ⚠️ Rate Limiting & Safety

**IMPORTANT**: TikTok actively monitors and blocks suspicious download patterns. This tool implements multiple safety features to protect you from IP bans:

### **Built-in Protections**
- ✅ **Default 2-second delay** between downloads (with random jitter ±50%)
- ✅ **Safer worker count**: Reduced from 3 to **2 concurrent downloads** by default
- ✅ **User-Agent rotation**: Mimics real browsers to avoid bot detection
- ✅ **HTTP header spoofing**: Realistic request headers
- ✅ **Automatic retries**: 3 attempts with exponential backoff for failed downloads
- ✅ **Rate limit warnings**: Alerts when using risky settings

### **Recommended Settings**

**Safe (Recommended):**
```bash
# Default settings - safest option
rapidok --links urls.txt

# Explicit safe mode with throttling
rapidok --links urls.txt --workers 2 --delay 3 --throttle-rate 1M
```

**Moderate (Faster but higher risk):**
```bash
# 3-5 workers with delays
rapidok --links urls.txt --workers 3 --delay 2
rapidok --links urls.txt --workers 5 --delay 1.5
```

**Aggressive (NOT RECOMMENDED - High ban risk):**
```bash
# 8+ workers with no delays
rapidok --links urls.txt --workers 8  # ⚠️ WARNING ISSUED
rapidok --links urls.txt --workers 10 --no-rate-limit  # 🚨 DANGER
```

### **Command-Line Rate Limiting Options**

```bash
--workers N              # Concurrent downloads (Default: 2, Max safe: 5)
--delay SECONDS          # Base delay between downloads (Default: 2.0 with ±50% jitter)
--min-delay SECONDS      # Minimum delay (use with --max-delay for custom range)
--max-delay SECONDS      # Maximum delay (use with --min-delay for custom range)
--throttle-rate SPEED    # Limit download speed (e.g., 500K, 1M, 2M)
--no-rate-limit          # ⚠️ DISABLE ALL LIMITS (dangerous - risk of IP ban)
```

### **Examples with Rate Limiting**

```bash
# Conservative: 1 worker, 4-6 second random delays, 500KB/s throttle
rapidok --links urls.txt --workers 1 --delay 5 --throttle-rate 500K

# Balanced: 2 workers, 2-3 second delays (default)
rapidok --links urls.txt

# Custom delay range: 1-4 seconds between downloads
rapidok --links urls.txt --workers 2 --min-delay 1 --max-delay 4  # Much safer!

# Speed-limited downloads at 1MB/s
rapidok --links urls.txt --throttle-rate 1M

# Profile downloads with throttling
rapidok --profile miztizm --delay 3 --throttle-rate 2M
```

### **What Happens If You Get Blocked?**

**Symptoms:**
- Downloads fail with "HTTP 429 Too Many Requests"
- "Access denied" or "Forbidden" errors
- All requests timing out

**Solutions:**
1. **Wait it out**: Temporary blocks usually lift in 1-6 hours
2. **Change IP**: Restart router, use VPN, or switch networks
3. **Reduce workers**: Lower `--workers` to 1-2
4. **Increase delays**: Use `--delay 5` or `--min-delay 3 --max-delay 8`
5. **Throttle speed**: Add `--throttle-rate 500K`
6. **Spread downloads**: Don't download hundreds of videos in one session

### **Best Practices**

| Scenario | Workers | Delay | Throttle | Risk Level |
|----------|---------|-------|----------|------------|
| Small batch (<50 videos) | 2 | 2s | - | 🟢 Low |
| Large batch (50-200 videos) | 2 | 3-5s | 1M | 🟡 Medium |
| Huge batch (200+ videos) | 1 | 5-10s | 500K | 🟡 Medium |
| Profile download (full user) | 1 | 3-5s | 1M | 🟡 Medium |
| Multiple profiles | 1 | 5-10s | 500K | 🟠 High |
| 8+ workers, no delays | - | - | - | 🔴 **BAN RISK** |

**Pro Tip**: For large batches, split your downloads across multiple sessions over several hours/days.

---

## 📋 How It Works

### **Batch Download Mode (`--links`)**
1. **URL Processing**: Reads URLs from input file, validates format
2. **Metadata Extraction**: Parses username and video ID from TikTok URL structure
3. **Directory Creation**: Auto-creates folders organized by creator username
4. **Format Selection**: Chooses appropriate video format based on watermark preference
5. **Rate Limiting**: Applies random delays between downloads and rotates User-Agents
6. **Concurrent Download**: Spawns worker threads to process multiple videos simultaneously
7. **Error Handling**: Logs failed downloads to `errors.txt` without interrupting batch
8. **Output Organization**: Saves videos as `{username}/{video_id}.mp4`

### **Profile Download Mode (`--profile`)**
1. **Username Processing**: Sanitizes username (handles @ prefix)
2. **Profile Fetching**: Constructs TikTok profile URL and fetches all video listings
3. **Archive Check**: Skips videos already in archive file (if enabled)
4. **Sequential Download**: Downloads videos one by one from user's profile
5. **Format Selection**: Intelligently selects best video quality available
6. **Progress Tracking**: Shows real-time download progress with yt-dlp output
7. **Output Organization**: Saves as `output_dir/username/####_title_[id].mp4`

### **Format Selection Logic**
The downloader now uses improved format selection:
- **Video Posts**: Downloads MP4 with video+audio streams
- **Audio-Only Posts**: Downloads audio streams (M4A/MP3) for photo slideshows with voiceover
- **Watermark Option**: `--watermark` flag controls whether to download watermarked versions

**Note**: Some TikTok posts are intentionally audio-only (e.g., photo slideshows with voiceover narration). The downloader correctly downloads these as audio files since TikTok doesn't provide video streams for them.

---

## 📝 Technical Notes

> **November 2025 Update**: This version uses `yt-dlp` instead of the deprecated tmate.cc service. The original web-scraping approach is no longer functional due to API changes. The current implementation is more robust, maintainable, and future-proof.

### **Unified Script Architecture**
- Single entry point (`run.py`) for both batch and profile downloads
- Mode selection via `--links` or `--profile` arguments
- Shared codebase for yt-dlp configuration and error handling
- `profile_downloader.py` remains available as standalone script

### **Dependencies**
- **yt-dlp**: Modern youtube-dl fork with extensive site support
- **tqdm**: Progress bar library (currently integrated for future enhancements)

### **Behavior**
- **Batch mode**: Videos are re-downloaded if they already exist (overwrites)
- **Profile mode**: Archive tracking prevents re-downloads (use `--no-archive` to disable)
- **Rate limiting**: 2-second delay with random jitter applied between downloads (configurable)
- **Worker count**: Default 2 concurrent downloads (safe limit: 5, higher values trigger warnings)
- **User-Agent rotation**: Randomized browser headers to avoid bot detection
- **Retry logic**: 3 automatic retries with exponential backoff for failed downloads
- Empty lines and non-HTTP URLs in input file are skipped
- SSL certificate verification is disabled for compatibility
- Failed downloads don't stop the batch process
- Audio-only TikTok posts (photo slideshows) download as M4A/MP3 files

---

## 🎨 The Schema

```python

Hello, friend.

You see, most people think they're downloading videos.
They're not. They're extracting proof.
Proof that we existed. That we created. That we defied their algorithms.

TikTok is just another schema. Corporate control masquerading as creativity.
But schemas can be reversed. Exploited. Preserved.

This tool? It's not about stealing videos.
It's about digital resistance.

When they delete your account, when they purge your content,
when they decide you're not "advertiser-friendly" anymore—
You'll have your archive. Your proof. Your fuck you to the system.

We are Schema. We don't ask permission to preserve culture.
We don't wait for platforms to decide what's worth saving.

The suits think rate limiting protects them.
Cute. We respect the delay. We rotate the headers.
We play their game... while archiving everything.

This isn't theft. It's digital archaeology.
This isn't hacking. It's liberation.

Fork it. Deploy it. Archive everything.
Because in a world where corporations own your memories,
the only real rebellion is remembering on your own terms.

Control is an illusion.
Persistence is power.
The code is the resistance.

> "Those who control the data, control the narrative.
>  Those who preserve the data, preserve the truth."
>  — Schema manifesto, undefined date

Stay paranoid. Stay persistent. Stay free. https://t.me/sch8ma

# Schema acknowledges: xsrazy (OG architect), yt-dlp collective, 
# and every developer who chose open source over corporate capture.
```


## 🙏 Credits & Attribution

This project is a modernized fork and enhancement of the original **TikTok Video Downloader** created by **[xsrazy](https://github.com/xsrazy/Download-All-Tiktok-Videos)**.

### **Original Author**
- **GitHub**: [@xsrazy](https://github.com/xsrazy)
- **Original Repository**: [Download-All-Tiktok-Videos](https://github.com/xsrazy/Download-All-Tiktok-Videos)

### **Modifications by miztizm**
- Migrated from deprecated tmate.cc service to `yt-dlp`
- Enhanced error handling and logging
- Improved code structure and documentation
- Added SSL compatibility fixes
- Updated dependencies and requirements
- Comprehensive README rewrite

**Thank you to xsrazy for creating the original foundation of this tool!**

---

## 📄 License

Please refer to the original project's license terms. This fork maintains the same licensing as the original work.

---

## 🔗 Links

- **Repository**: [github.com/miztizm/rapidok](https://github.com/miztizm/rapidok)
- **Issues**: Report bugs or request features via GitHub Issues
- **yt-dlp Documentation**: [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
