# Changelog - Rapidok

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-11-16 - miztizm Fork

### Added
- Complete migration to `yt-dlp` for robust video downloading
- SSL certificate handling for compatibility across environments
- Enhanced error messages and logging
- Comprehensive documentation and usage examples
- Technical architecture documentation
- Credits and attribution section
- MIT License file
- This CHANGELOG

### Changed
- **BREAKING**: Replaced tmate.cc web scraping with yt-dlp library
- Improved code structure and readability
- Enhanced command-line help text with attribution
- Updated all dependencies in requirements.txt
- Rewrote README.md with detailed technical information

### Fixed
- SSL certificate verification errors on Windows/Python 3.14
- Broken tmate.cc API dependencies (service no longer functional)
- Error handling to be more graceful and informative
- URL validation to skip empty/invalid lines

### Removed
- Dependencies on `beautifulsoup4` and `requests`
- Dependencies on `urllib3`
- Web scraping logic for tmate.cc

---

## [1.0.0] - Original - xsrazy

### Original Features
- Concurrent TikTok video downloads
- Watermark/no-watermark options
- Batch processing from text file
- Automatic folder organization by username
- Error logging to errors.txt
- Multi-threaded downloads with configurable workers

### Original Implementation
- Used tmate.cc web service for video extraction
- BeautifulSoup for HTML parsing
- Requests library for HTTP operations
- tqdm for progress bars

---

## Attribution

- **Original Author**: xsrazy (https://github.com/xsrazy)
- **Original Repository**: https://github.com/xsrazy/Download-All-Tiktok-Videos
- **Fork Maintainer**: miztizm
- **Fork Repository**: https://github.com/miztizm/rapidok
