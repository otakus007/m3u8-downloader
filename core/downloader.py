import os
import yt_dlp
import threading
from typing import Callable, Optional

class M3U8Downloader:
    def __init__(self, progress_hook: Optional[Callable[[dict], None]] = None):
        """
        Initialize the downloader wrapper.
        :param progress_hook: A function that takes a dict containing progress information.
        """
        self.progress_hook = progress_hook

    def _internal_hook(self, d):
        if self.progress_hook:
            self.progress_hook(d)

    def download(self, url: str, output_path: str, headers: Optional[dict] = None, cookies: str = "", custom_name: str = "", is_playlist: bool = False, playlist_title: str = ""):
        """
        Blocking call to download an M3U8 stream or YouTube playlist.
        """
        # Determine output template structure
        if is_playlist:
            # Create a folder for the playlist
            playlist_folder = os.path.join(output_path, playlist_title)
            if not os.path.exists(playlist_folder):
                os.makedirs(playlist_folder, exist_ok=True)
            # yt-dlp native playlist formatting
            filename_template = '%(playlist_index)s - %(title)s.%(ext)s'
            download_dir = playlist_folder
        else:
            if not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)
            # Use custom name if provided for single video
            filename_template = f"{custom_name}.%(ext)s" if custom_name else '%(title)s.%(ext)s'
            download_dir = output_path
            
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(download_dir, filename_template),
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self._internal_hook],
        }

        if headers:
            ydl_opts['http_headers'] = headers
        if cookies:
            if headers is None:
                ydl_opts['http_headers'] = {}
            ydl_opts['http_headers']['Cookie'] = cookies

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_async(self, url: str, output_path: str, headers: Optional[dict] = None, cookies: str = "", custom_name: str = "",
                       completion_callback: Optional[Callable[[str], None]] = None, 
                       error_callback: Optional[Callable[[Exception], None]] = None):
        """
        Non-blocking call to download. Executes in a daemon thread.
        Detects if URL is a playlist or single video and routes appropriately.
        """
        def _run():
            final_path = None # Initialize final_path
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': 'in_playlist'}
                if headers: ydl_opts['http_headers'] = headers
                if cookies: 
                    if 'http_headers' not in ydl_opts: ydl_opts['http_headers'] = {}
                    ydl_opts['http_headers']['Cookie'] = cookies

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    # Check if the result is a playlist
                    is_playlist = info.get('_type') == 'playlist'
                    
                    if is_playlist:
                        playlist_title = info.get('title', 'Unknown_Playlist')
                        # Sanitize playlist folder name
                        playlist_title = re.sub(r'[\\/*?:"<>|]', "", playlist_title)
                        final_path = os.path.join(output_path, playlist_title)
                        # Perform actual download for playlist
                        self.download(url, output_path, headers, cookies, is_playlist=True, playlist_title=playlist_title)
                    else:
                        title = custom_name if custom_name else info.get('title', 'Unknown_Video')
                        final_path = os.path.join(output_path, f"{title}.mp4")
                        # Perform actual download for single video
                        self.download(url, output_path, headers, cookies, custom_name=custom_name, is_playlist=False)

            except Exception as e:
                if error_callback:
                    error_callback(e)
                return # Exit _run on error

            if completion_callback and final_path: # Ensure final_path is set before calling
                completion_callback(final_path)
                    
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return thread
