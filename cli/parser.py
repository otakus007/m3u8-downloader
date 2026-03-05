import argparse
import sys
from core.downloader import M3U8Downloader

def print_progress(d):
    """
    Callback function to print download progress to the terminal.
    """
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        sys.stdout.write(f"\rDownloading... {percent} at {speed} ETA: {eta}")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\nDownload chunks finished. Merging files into an MP4...")

def run_cli():
    parser = argparse.ArgumentParser(description="M3U8 Downloader CLI tool")
    parser.add_argument("url", help="M3U8 stream URL to download")
    parser.add_argument("-o", "--output", default=".", help="Output directory path (default: current directory)")
    parser.add_argument("--referer", default="", help="Referer HTTP header to bypass 403 Forbidden")
    parser.add_argument("--cookie", default="", help="Raw Cookie string to bypass 403 Forbidden")
    
    args = parser.parse_args()
    
    print(f"Starting download for URL: {args.url}")
    print(f"Output directory: {args.output}")
    if args.referer: print(f"Referer: {args.referer}")
    if args.cookie: print(f"Cookies provided")
    print(f"Press Ctrl+C to cancel.")
    print("-" * 50)
    
    headers = {"Referer": args.referer} if args.referer else None

    downloader = M3U8Downloader(progress_hook=print_progress)
    try:
        downloader.download(args.url, args.output, headers=headers, cookies=args.cookie)
        print("Download successfully completed!")
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during download: {e}")
        sys.exit(1)
