import yt_dlp
from concurrent import futures
from tqdm import tqdm
import argparse
import os
import json
import requests
import time
import random
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import urllib3

# Rich library imports for enhanced terminal output
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, DownloadColumn, TransferSpeedColumn
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

# Disable SSL warnings for image downloads (TikTok CDN certificate issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize rich console
console = Console()


class SuppressLogger:
    """Custom logger to suppress yt-dlp error messages during metadata extraction"""
    def debug(self, msg):
        pass
    
    def info(self, msg):
        pass
    
    def warning(self, msg):
        pass
    
    def error(self, msg):
        # Suppress "No video formats found" errors - these are benign
        if "No video formats found" not in msg:
            pass  # Could log other errors if needed


# User-Agent rotation for anti-detection
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def get_random_user_agent() -> str:
    """Return a random User-Agent string to avoid bot detection"""
    return random.choice(USER_AGENTS)


def sanitize_username(username: str) -> str:
    """Remove @ prefix and whitespace from username"""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")
    return username.strip().lstrip('@')


def detect_post_type(entry: Dict[str, Any]) -> str:
    """
    Detect the type of TikTok post based on available formats
    
    Args:
        entry: Video entry from yt-dlp extraction
        
    Returns:
        One of: 'video', 'audio_only', 'images', 'unknown'
    """
    formats = entry.get('formats', [])
    
    if not formats:
        return 'unknown'
    
    # Check if any format has a video codec
    has_video = any(
        f.get('vcodec') and f.get('vcodec') != 'none' 
        for f in formats
    )
    
    # Check if any format has an audio codec
    has_audio = any(
        f.get('acodec') and f.get('acodec') != 'none'
        for f in formats
    )
    
    # Check for slideshow posts (have thumbnails but no video)
    # TikTok slideshows/photo carousels only provide audio track via yt-dlp
    thumbnails = entry.get('thumbnails', [])
    has_thumbnails = len(thumbnails) > 0
    
    if has_video:
        return 'video'
    elif has_audio and not has_video and has_thumbnails:
        # Slideshow post (photo carousel) - has audio + thumbnails but no video
        return 'images'
    elif has_audio and not has_video:
        # Pure audio post (rare)
        return 'audio_only'
    else:
        return 'unknown'


def extract_metadata(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant metadata from a TikTok post

    Args:
        entry: Video entry from yt-dlp extraction

    Returns:
        Dictionary with post metadata
    """
    return {
        'id': entry.get('id'),
        'title': entry.get('title'),
        'description': entry.get('description'),
        'duration': entry.get('duration'),
        'view_count': entry.get('view_count'),
        'like_count': entry.get('like_count'),
        'comment_count': entry.get('comment_count'),
        'timestamp': entry.get('timestamp'),
        'upload_date': entry.get('upload_date'),
        'uploader': entry.get('uploader'),
        'uploader_id': entry.get('uploader_id'),
        'webpage_url': entry.get('webpage_url'),
        'post_type': detect_post_type(entry),
        'thumbnails': [
            {
                'url': t.get('url'),
                'width': t.get('width'),
                'height': t.get('height')
            }
            for t in entry.get('thumbnails', [])
        ]
    }


def should_download_post(post_type: str, content_filter: str) -> bool:
    """
    Determine if a post should be downloaded based on content filter

    Args:
        post_type: Type of post ('video', 'audio_only', 'images', 'unknown')
        content_filter: Content type filter ('all', 'video-only', 'audio-only', 'images-only', 'metadata-only')

    Returns:
        True if post should be downloaded
    """
    if content_filter == 'all':
        return True
    elif content_filter == 'video-only':
        return post_type == 'video'
    elif content_filter == 'audio-only':
        return post_type == 'audio_only'
    elif content_filter == 'images-only':
        return post_type == 'images'
    elif content_filter == 'metadata-only':
        return False  # Don't download any media
    return False


def download_image_from_url(url: str, output_path: str) -> bool:
    """
    Download an image from a URL and save it to the specified path

    Args:
        url: Image URL to download
        output_path: Full path where the image should be saved

    Returns:
        True if download successful, False otherwise
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True, verify=False)
        response.raise_for_status()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        console.print(f"    [red]✗[/red] Error downloading image: {e}")
        return False


def apply_rate_limit(args, delay_min, delay_max):
    """Apply rate limiting delay with random jitter"""
    if args.no_rate_limit:
        return

    delay = random.uniform(delay_min, delay_max)
    time.sleep(delay)


def download_from_url(link: str, watermark: bool, args, delay_min, delay_max) -> None:
    """Download a single TikTok video from URL with enhanced error handling and rate limiting"""
    link = link.strip()
    if not link or not link.startswith("http"):
        return

    # Apply rate limiting before download
    apply_rate_limit(args, delay_min, delay_max)

    try:
        # Extract username and video ID from URL
        parts = link.split("/")
        username = parts[-3].replace("@", "")
        video_id = parts[-1].split("?")[0]  # Remove query parameters

        # Create folder for user in output directory
        folder_name = os.path.join(args.output_dir, username)
        os.makedirs(folder_name, exist_ok=True)

        # Check if file already exists (skip-existing feature)
        if args.skip_existing:
            for ext in ['mp4', 'webm', 'mkv', 'm4a', 'mp3', 'jpg', 'jpeg']:
                potential_file = os.path.join(folder_name, f"{video_id}.{ext}")
                if os.path.exists(potential_file):
                    console.print(f"[yellow]⊘[/yellow] Skipping: {username}/{video_id} (already exists)")
                    return

        # Configure yt-dlp options with rate limiting and anti-detection
        ydl_opts = {
            'nocheckcertificate': True,
            'quiet': False,
            'no_warnings': True,  # Suppress impersonation warnings
            'outtmpl': os.path.join(folder_name, f'{video_id}.%(ext)s'),
            # Retry and error handling
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            # HTTP options for anti-detection
            'http_headers': {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
        }

        # Add rate limiting options only if enabled (prevents type comparison errors)
        if not args.no_rate_limit:
            ydl_opts['sleep_interval'] = 1
            ydl_opts['max_sleep_interval'] = 3
            ydl_opts['sleep_interval_requests'] = 1

        # Add throttle rate if specified
        if args.throttle_rate and not args.no_rate_limit:
            ydl_opts['ratelimit'] = args.throttle_rate

        # Format selection: prefer video formats, download audio if that's all available
        if watermark:
            ydl_opts['format'] = 'download/best'
        else:
            # Prefer video formats (mp4 with video codec), fallback to best available
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            title = info.get('title', 'Unknown')
            console.print(f"[green]✓[/green] Downloaded: {username}/{video_id} - {title}")

            # Save metadata if requested
            if args.save_metadata:
                metadata_dir = os.path.join(folder_name, "metadata")
                os.makedirs(metadata_dir, exist_ok=True)
                metadata_file = os.path.join(metadata_dir, f"{video_id}.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'id': info.get('id'),
                        'title': info.get('title'),
                        'description': info.get('description'),
                        'duration': info.get('duration'),
                        'view_count': info.get('view_count'),
                        'like_count': info.get('like_count'),
                        'comment_count': info.get('comment_count'),
                        'upload_date': info.get('upload_date'),
                        'uploader': info.get('uploader'),
                        'uploader_id': info.get('uploader_id'),
                        'webpage_url': info.get('webpage_url'),
                        'ext': info.get('ext'),
                        'format': info.get('format'),
                        'resolution': f"{info.get('width')}x{info.get('height')}" if info.get('width') else None,
                        'filesize': info.get('filesize'),
                    }, f, indent=4, ensure_ascii=False)

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {link} - {str(e)}")
        error_log = os.path.join("logs", "errors.txt")
        os.makedirs("logs", exist_ok=True)
        with open(error_log, 'a', encoding='utf-8') as error:
            error.write(f"{link} - {str(e)}\n")


def download_user_profile(
    username: str,
    output_dir: str = "downloads",
    max_downloads: Optional[int] = None,
    use_archive: bool = True,
    watermark: bool = False,
    content_type: str = "video-only",
    args = None,
    delay_min: float = 1.0,
    delay_max: float = 3.0
) -> Dict[str, Any]:
    """
    Download content from a TikTok user's profile with filtering options

    Args:
        username: TikTok username
        output_dir: Base output directory
        max_downloads: Maximum items to process
        use_archive: Enable archive tracking
        watermark: Download watermarked versions
        content_type: Type of content to download (all, video-only, audio-only, images-only, metadata-only)
        args: Argument namespace with configuration
        delay_min: Minimum delay between downloads
        delay_max: Maximum delay between downloads

    Returns:
        Dictionary with download results
    """

    clean_username = sanitize_username(username)
    profile_url = f"https://www.tiktok.com/@{clean_username}"
    user_output_dir = os.path.join(output_dir, clean_username)
    os.makedirs(user_output_dir, exist_ok=True)

    # Create subdirectories for organized storage
    videos_dir = os.path.join(user_output_dir, "videos")
    audio_dir = os.path.join(user_output_dir, "audio")
    images_dir = os.path.join(user_output_dir, "images")

    if content_type in ['all', 'video-only']:
        os.makedirs(videos_dir, exist_ok=True)
    if content_type in ['all', 'audio-only']:
        os.makedirs(audio_dir, exist_ok=True)
    if content_type in ['all', 'images-only']:
        os.makedirs(images_dir, exist_ok=True)

    # Display profile download configuration in a panel
    config_text = f"""[cyan]Profile:[/cyan] @{clean_username}
[cyan]URL:[/cyan] {profile_url}
[cyan]Output:[/cyan] {user_output_dir}
[cyan]Content Type:[/cyan] {content_type}
[cyan]Archive:[/cyan] {'Enabled' if use_archive else 'Disabled'}"""

    if max_downloads:
        config_text += f"\n[cyan]Max Downloads:[/cyan] {max_downloads}"

    console.print(Panel(config_text, title="[bold blue]Profile Download Configuration[/bold blue]", border_style="blue", box=box.ROUNDED))
    console.print()

    # First pass: Extract metadata for all posts
    console.print("[bold cyan]Fetching profile information...[/bold cyan]")

    ydl_opts_extract = {
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'ignoreerrors': True,
        'skip_download': True,  # Don't download, just extract info
        'logger': SuppressLogger(),  # Use custom logger to suppress benign errors
        # Anti-detection headers
        'http_headers': {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        },
    }

    all_metadata = []
    posts_to_download = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts_extract) as ydl:
            info = ydl.extract_info(profile_url, download=False)

            if not info or 'entries' not in info:
                console.print("[red]✗[/red] No posts found in profile")
                return {'success': False, 'error': 'No posts found'}

            entries = [e for e in info['entries'] if e is not None]
            total_posts = len(entries)

            console.print(f"[green]✓[/green] Found {total_posts} posts in profile\n")

            for entry in entries[:max_downloads] if max_downloads else entries:
                metadata = extract_metadata(entry)
                all_metadata.append(metadata)

                post_type = metadata['post_type']

                # Determine if we should download this post
                if should_download_post(post_type, content_type):
                    posts_to_download.append(entry)

        # Save metadata if requested
        if content_type in ['all', 'metadata-only']:
            metadata_file = os.path.join(user_output_dir, f"{clean_username}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'profile_username': clean_username,
                    'extraction_date': datetime.now().isoformat(),
                    'total_posts': len(all_metadata),
                    'posts': all_metadata
                }, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✓[/green] Saved metadata for {len(all_metadata)} posts to {metadata_file}\n")

        # If metadata-only, we're done
        if content_type == 'metadata-only':
            return {
                'success': True,
                'username': clean_username,
                'posts_processed': len(all_metadata),
                'metadata_saved': True
            }

        # Download filtered posts
        if not posts_to_download:
            console.print(f"[yellow]⚠[/yellow] No posts match filter '{content_type}'\n")
            return {
                'success': True,
                'username': clean_username,
                'posts_downloaded': 0,
                'message': f'No {content_type} posts found'
            }

        console.print(f"[bold cyan]Downloading {len(posts_to_download)} posts matching '{content_type}' filter...[/bold cyan]\n")

        downloads_completed = 0

        for idx, entry in enumerate(posts_to_download, 1):
            post_type = detect_post_type(entry)
            post_id = entry.get('id', 'unknown')
            title = entry.get('title', 'Untitled')[:50]

            # Handle image posts (slideshows) differently
            if post_type == 'images':
                # Download thumbnail images from slideshow posts
                thumbnails = entry.get('thumbnails', [])
                if thumbnails:
                    # Use the first thumbnail (usually the highest quality)
                    thumbnail_url = thumbnails[0].get('url')
                    if thumbnail_url:
                        # Generate filename
                        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50].strip()
                        filename = f"{idx:04d}_{safe_title}_{post_id}.jpg"
                        output_path = os.path.join(images_dir, filename)

                        # Skip if file already exists
                        if args and args.skip_existing and os.path.exists(output_path):
                            console.print(f"  [{idx}/{len(posts_to_download)}] [yellow]⊘[/yellow] Skipping: {title}... (already exists)")
                            downloads_completed += 1
                            continue

                        if download_image_from_url(thumbnail_url, output_path):
                            downloads_completed += 1
                            console.print(f"  [{idx}/{len(posts_to_download)}] [green]✓[/green] Downloaded image: {title}... ({post_type})")

                            # Mark in archive if enabled
                            if use_archive:
                                archive_path = os.path.join(user_output_dir, "archive.txt")
                                with open(archive_path, 'a', encoding='utf-8') as f:
                                    f.write(f"tiktok {post_id}\n")
                        else:
                            console.print(f"  [{idx}/{len(posts_to_download)}] [red]✗[/red] Failed to download image: {title}")
                else:
                    console.print(f"  [{idx}/{len(posts_to_download)}] [yellow]⚠[/yellow] No thumbnails available for: {title}")
                continue

            # Handle video and audio posts with yt-dlp
            # Determine output directory based on post type
            if post_type == 'video':
                target_dir = videos_dir
            elif post_type == 'audio_only':
                target_dir = audio_dir
            else:
                target_dir = images_dir

            # Check if file already exists (skip-existing feature)
            if args and args.skip_existing:
                potential_files = [
                    f for f in os.listdir(target_dir) if f.endswith((f'[{post_id}].mp4', f'[{post_id}].m4a', f'[{post_id}].webm'))
                ] if os.path.exists(target_dir) else []
                if potential_files:
                    console.print(f"  [{idx}/{len(posts_to_download)}] [yellow]⊘[/yellow] Skipping: {title}... (already exists)")
                    downloads_completed += 1
                    continue

            # Apply rate limiting between downloads in profile mode
            if idx > 1:  # Skip delay for first download
                apply_rate_limit(args, delay_min, delay_max)

            # Configure download options for this specific post
            ydl_opts_download = {
                'outtmpl': f"{target_dir}/%(autonumber)04d_%(title)s_[%(id)s].%(ext)s",
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'quiet': False,
                'no_warnings': True,  # Suppress impersonation warnings
                # Retry and error handling
                'retries': 3,
                'fragment_retries': 3,
                # Anti-detection
                'http_headers': {
                    'User-Agent': get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
            }

            # Add rate limiting options only if enabled (prevents type comparison errors)
            if args and not args.no_rate_limit:
                ydl_opts_download['sleep_interval'] = 1
                ydl_opts_download['max_sleep_interval'] = 3

            # Add throttle rate if specified
            if args and args.throttle_rate and not args.no_rate_limit:
                ydl_opts_download['ratelimit'] = args.throttle_rate

            # Format selection based on post type and watermark preference
            if watermark:
                ydl_opts_download['format'] = 'download/best'
            else:
                if post_type == 'video':
                    ydl_opts_download['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif post_type == 'audio_only':
                    ydl_opts_download['format'] = 'bestaudio/best'
                else:  # images
                    ydl_opts_download['format'] = 'best'

            if use_archive:
                archive_path = os.path.join(user_output_dir, "archive.txt")
                ydl_opts_download['download_archive'] = archive_path

            try:
                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([entry.get('webpage_url', entry.get('url'))])
                    downloads_completed += 1
                    console.print(f"  [{idx}/{len(posts_to_download)}] [green]✓[/green] Downloaded: {title}... ({post_type})")
            except Exception as e:
                console.print(f"  [{idx}/{len(posts_to_download)}] [red]✗[/red] Error downloading {post_id}: {e}")
                continue

        # Create summary table
        summary_table = Table(title="Download Summary", box=box.ROUNDED, border_style="green")
        summary_table.add_column("Metric", style="cyan", no_wrap=True)
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Username", f"@{clean_username}")
        summary_table.add_row("Posts Downloaded", f"{downloads_completed}/{len(posts_to_download)}")
        summary_table.add_row("Content Type", content_type)
        summary_table.add_row("Output Directory", user_output_dir)

        console.print()
        console.print(summary_table)
        console.print()

        return {
            'success': True,
            'username': clean_username,
            'posts_downloaded': downloads_completed,
            'posts_total': len(all_metadata),
            'content_type': content_type
        }

    except Exception as e:
        error_str = str(e)
        if "Maximum number of downloads reached" in error_str or "max-downloads" in error_str:
            console.print()
            console.print(Panel(f"[green]✓[/green] Reached maximum download limit: {max_downloads}",
                              title="[bold green]Download Limit Reached[/bold green]",
                              border_style="green",
                              box=box.ROUNDED))
            console.print()
            return {'success': True, 'posts_downloaded': max_downloads}

        console.print()
        console.print(f"[red]✗[/red] Error downloading profile: {e}\n")
        return {'success': False, 'error': str(e)}


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Rapidok - TikTok Content Downloader by miztizm - Download videos, images, and audio from URLs or entire user profiles",
        epilog="Original concept by xsrazy | Enhanced and maintained by miztizm"
    )

    # Mode selection: URL batch or profile download
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--links", help="Path to .txt file with TikTok URLs for batch download")
    mode_group.add_argument("--profile", help="TikTok username to download all videos from user profile")

    # Common options
    watermark_group = parser.add_mutually_exclusive_group()
    watermark_group.add_argument("--no-watermark", action="store_true", help="Download videos without watermarks (Default)")
    watermark_group.add_argument("--watermark", action="store_true", help="Download videos with watermarks")

    parser.add_argument("--workers", default=2, type=int, help="Number of concurrent downloads for batch mode (Default: 2, Max recommended: 5)")
    parser.add_argument("--output-dir", default="downloads", help="Output directory (Default: downloads)")
    parser.add_argument("--max-downloads", type=int, help="Maximum videos to download (profile mode only)")
    parser.add_argument("--no-archive", action="store_true", help="Disable archive tracking (profile mode)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip downloading files that already exist")
    parser.add_argument("--save-metadata", action="store_true", help="Save detailed metadata for each downloaded item")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between downloads in seconds (Default: 2.0, adds random jitter)")
    parser.add_argument("--min-delay", type=float, help="Minimum delay between downloads (overrides --delay for range)")
    parser.add_argument("--max-delay", type=float, help="Maximum delay between downloads (overrides --delay for range)")
    parser.add_argument("--throttle-rate", help="Limit download speed (e.g., 500K, 1M, 2M for bytes/sec)")
    parser.add_argument("--no-rate-limit", action="store_true", help="Disable all rate limiting (NOT RECOMMENDED - risk of IP ban)")
    parser.add_argument(
        "--content-type",
        choices=["all", "video-only", "audio-only", "images-only", "metadata-only"],
        default="video-only",
        help="Type of content to download from profile (Default: video-only)"
    )

    args = parser.parse_args()

    # Default to links.txt if no mode specified
    if not args.links and not args.profile:
        args.links = "links.txt"

    # Validate and warn about rate limiting
    if args.workers > 5:
        console.print()
        console.print(Panel(
            "[yellow]⚠[/yellow]  WARNING: Using >5 concurrent workers increases risk of IP blocking!\n"
            "   Recommended: 2-5 workers with delays enabled.\n"
            "   Proceed at your own risk.",
            title="[bold yellow]High Worker Count Warning[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
        time.sleep(2)  # Give user time to read warning

    if args.no_rate_limit:
        console.print()
        console.print(Panel(
            "[red]⚠[/red]  DANGER: Rate limiting disabled! High risk of TikTok blocking your IP.\n"
            "   This is NOT recommended for batch downloads.",
            title="[bold red]Rate Limiting Disabled[/bold red]",
            border_style="red",
            box=box.ROUNDED
        ))
        console.print()
        time.sleep(2)

    # Calculate delay range
    if args.min_delay and args.max_delay:
        delay_min = args.min_delay
        delay_max = args.max_delay
    elif args.min_delay or args.max_delay:
        console.print("[red]✗[/red] Error: --min-delay and --max-delay must be used together")
        exit(1)
    else:
        # Add +/- 50% jitter to base delay
        delay_min = args.delay * 0.5
        delay_max = args.delay * 1.5

    # Execute based on mode
    if args.profile:
        # Profile download mode
        result = download_user_profile(
            username=args.profile,
            output_dir=args.output_dir,
            max_downloads=args.max_downloads,
            use_archive=not args.no_archive,
            watermark=args.watermark,
            content_type=args.content_type,
            args=args,
            delay_min=delay_min,
            delay_max=delay_max
        )
        exit(0 if result['success'] else 1)

    elif args.links:
        # Batch URL download mode
        with open(args.links, "r") as links:
            tiktok_links = links.read().split("\n")

        valid_links = [l for l in tiktok_links if l.strip()]

        console.print()
        console.print(Panel(
            f"[cyan]Links File:[/cyan] {args.links}\n"
            f"[cyan]Total URLs:[/cyan] {len(valid_links)}\n"
            f"[cyan]Workers:[/cyan] {args.workers}\n"
            f"[cyan]Output:[/cyan] {args.output_dir}",
            title="[bold blue]Batch Download Configuration[/bold blue]",
            border_style="blue",
            box=box.ROUNDED
        ))
        console.print()

        with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            executor.map(lambda link: download_from_url(link, args.watermark, args, delay_min, delay_max), tiktok_links)

        console.print()
        console.print(Panel(
            "[green]✓[/green] All downloads completed!",
            title="[bold green]Batch Download Complete[/bold green]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print()


if __name__ == "__main__":
    main()

