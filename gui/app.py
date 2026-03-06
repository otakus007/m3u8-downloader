import os
import re
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path
import customtkinter as ctk
from core.downloader import M3U8Downloader

class M3U8DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings (Task 4: Native Window Controls & Resizing)
        self.title("M3U8 Downloader Pro")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Apply global appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configuration Path
        self.config_file = Path.home() / ".m3u8_downloader_config.json"
        saved_dir = self._load_saved_directory()

        # Core State Variables
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=saved_dir)
        self.referer_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to download.")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.video_title_var = tk.StringVar(value="")

        # Download History (Task 5: Download Management)
        self.download_history = []

        self._build_interface()

    def _build_interface(self):
        """Constructs the elegant UI components with grid layout for sidebar support."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # SIDEBAR (History / Manager)
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, text="Download History", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.history_scrollable = ctk.CTkScrollableFrame(self.sidebar_frame)
        self.history_scrollable.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)


        # ==========================================
        # MAIN CONTENT AREA
        # ==========================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)

        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="Video Downloader", 
            font=ctk.CTkFont(family="Inter", size=36, weight="bold")
        )
        self.header_label.pack(anchor="w", pady=(0, 4))
        
        self.sub_label = ctk.CTkLabel(
            self.main_frame, 
            text="Download HLS/M3U8 streams to MP4. Options to bypass 403.", 
            font=ctk.CTkFont(size=18), text_color="#94A3B8"
        )
        self.sub_label.pack(anchor="w", pady=(0, 24))

        # URL Input
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(fill="x", pady=(0, 16))

        self.url_entry = ctk.CTkEntry(
            self.url_frame, textvariable=self.url_var,
            placeholder_text="Paste M3U8 URL here...",
            height=54, font=ctk.CTkFont(size=18),
            border_width=1, border_color="#334155", fg_color="#0F172A",
            corner_radius=8
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.sniff_btn = ctk.CTkButton(
            self.url_frame, text="🌐 Auto-Capture Browser", command=self._open_sniffer,
            width=220, height=54, corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#059669", hover_color="#047857" # emerald-600
        )
        self.sniff_btn.pack(side="right")

        # Directory Picker
        self.dir_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dir_frame.pack(fill="x", pady=(0, 16))

        self.dir_btn = ctk.CTkButton(
            self.dir_frame, text="Choose Output Folder", command=self._select_directory,
            width=180, height=48, corner_radius=8,
            font=ctk.CTkFont(size=16, weight="normal"),
            fg_color="#334155", hover_color="#475569", text_color="#F8FAFC"
        )
        self.dir_btn.pack(side="left")

        self.dir_label = ctk.CTkLabel(
            self.dir_frame, textvariable=self.output_dir_var,
            font=ctk.CTkFont(size=16), text_color="#64748B"
        )
        self.dir_label.pack(side="left", padx=(12, 0))

        # ==========================================
        # Authentication Section (Expandable/Optional)
        # ==========================================
        self.auth_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E293B", corner_radius=8)
        self.auth_frame.pack(fill="x", pady=(0, 24), ipadx=10, ipady=10)
        
        self.auth_label = ctk.CTkLabel(
            self.auth_frame, text="Authentication (Optional)", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.auth_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.referer_entry = ctk.CTkEntry(
            self.auth_frame, textvariable=self.referer_var,
            placeholder_text="Referer URL (e.g. https://example.com)",
            height=48, font=ctk.CTkFont(size=16), corner_radius=6, border_color="#475569"
        )
        self.referer_entry.pack(fill="x", padx=10, pady=(0, 10))

        self.cookie_text = ctk.CTkTextbox(
            self.auth_frame, height=90, font=ctk.CTkFont(size=16), corner_radius=6, border_color="#475569", border_width=1
        )
        self.cookie_text.insert("0.0", "Paste raw cookies here if required...")
        self.cookie_text.bind("<FocusIn>", self._clear_cookie_placeholder)
        self.cookie_text.pack(fill="x", padx=10, pady=(0, 10))

        # ==========================================
        # Action & Active Downloads
        # ==========================================
        self.dl_btn = ctk.CTkButton(
            self.main_frame, text="Start Download (Multi-Thread Supported)", command=self._start_download,
            height=54, corner_radius=8, font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8"
        )
        self.dl_btn.pack(fill="x", pady=(0, 16))

        # Replace single progress bar with a Scrollable Frame for Multi-downloads
        self.active_dl_label = ctk.CTkLabel(
            self.main_frame, text="Active Downloads", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.active_dl_label.pack(anchor="w", pady=(10, 5))
        
        self.active_scrollable = ctk.CTkScrollableFrame(self.main_frame, fg_color="#0F172A", corner_radius=8)
        self.active_scrollable.pack(fill="both", expand=True, pady=(0, 8))
        
        # State mapping for Active Downloads
        self.active_downloads = {} # dict[uuid] = {'frame': widget, 'progress_var': DoubleVar, 'status_var': StringVar}

    def _send_notification(self, title: str, message: str, timeout: int = 3):
        """Cross-platform notification with guaranteed timeout on Linux."""
        try:
            if sys.platform.startswith('linux'):
                # On Linux (Hyprland/GNOME/etc), 'notify-send' timeout is much more reliable
                # than plyer's dbus implementation which drops the expire-time.
                subprocess.Popen([
                    'notify-send', 
                    '-a', 'M3U8 Downloader',
                    '-t', str(timeout * 1000),
                    '-e', # Transient (auto-dismiss)
                    title, 
                    message
                ])
            else:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="M3U8 Downloader",
                    timeout=timeout
                )
        except Exception as e:
            print(f"Notification error: {e}")

    # ==========================================================================
    # LOGIC HANDLERS
    # ==========================================================================
    def _open_sniffer(self):
        from browser.sniffer import WebSniffer
        self.sniff_btn.configure(state="disabled", text="Opening...")
        
        sniffer = WebSniffer(
            on_found_callback=self._on_sniffer_found,
            on_error_callback=self._on_sniffer_error
        )
        sniffer.start_sniffing()

    def _on_sniffer_found(self, url: str, cookies: str, referer: str, title: str):
        self.after(0, self._update_ui_from_sniffer, url, cookies, referer, title)

    def _update_ui_from_sniffer(self, url: str, cookies: str, referer: str, title: str):
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        self.url_var.set(url)
        self.referer_var.set(referer)
        self.video_title_var.set(safe_title)
        
        self.cookie_text.delete("0.0", "end")
        self.cookie_text.insert("0.0", cookies)
        
        print(f"Auto-Captured M3U8 for: {title}")
        self._send_notification(title="Link Captured ✨", message=f"Ready to download: {safe_title}", timeout=3)

    def _on_sniffer_error(self, e: Exception):
        self.after(0, self._handle_sniffer_error, str(e))

    def _handle_sniffer_error(self, err: str):
        self.sniff_btn.configure(state="normal", text="🌐 Auto-Capture Browser")
        print(f"Sniffer error/close: {err}")

    def _clear_cookie_placeholder(self, event):
        if "Paste raw cookies" in self.cookie_text.get("0.0", "end"):
            self.cookie_text.delete("0.0", "end")

    def _load_saved_directory(self) -> str:
        """Loads the last used directory from the config file, fallback to CWD."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_path = config.get("output_dir", "")
                    if saved_path and os.path.isdir(saved_path):
                        return saved_path
        except Exception as e:
            print(f"Failed to load config: {e}")
        return os.getcwd()

    def _save_directory_to_config(self, path: str):
        """Saves the current directory to the config file."""
        try:
            config = {}
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config["output_dir"] = path
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def _select_directory(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if folder:
            self.output_dir_var.set(folder)
            self._save_directory_to_config(folder)

    def _progress_hook(self, d: dict, dl_id: str):
        if dl_id not in self.active_downloads:
            return
            
        widgets = self.active_downloads[dl_id]
        
        if d['status'] == 'downloading':
            try:
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                percent_str = str(d.get('_percent_str', '0%')).replace('%', '').strip()
                percent_clean = ansi_escape.sub('', percent_str)
                percent = float(percent_clean) / 100.0
                speed_str = str(d.get('_speed_str', 'N/A'))
                speed_clean = ansi_escape.sub('', speed_str).strip()
                eta_str = str(d.get('_eta_str', 'N/A'))
                eta_clean = ansi_escape.sub('', eta_str).strip()
                
                info_dict = d.get('info_dict', {})
                playlist_index = info_dict.get('playlist_index')
                playlist_count = info_dict.get('playlist_count')
                prefix = f"[Vid {playlist_index}/{playlist_count}] " if playlist_index and playlist_count else ""
                
                status_text = f"{prefix}Dl: {percent*100:.1f}% | Spd: {speed_clean} | ETA: {eta_clean}"
                self.after(0, self._update_progress_ui, dl_id, percent, status_text)
            except Exception:
                pass
        
        elif d['status'] == 'finished':
            self.after(0, self._update_progress_ui, dl_id, 1.0, "Merging MP4... Please wait.")

    def _update_progress_ui(self, dl_id: str, percent: float, text: str):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id]['progress_var'].set(percent)
            self.active_downloads[dl_id]['status_var'].set(text)

    def _on_download_complete(self, final_file_path: str, dl_id: str):
        self.after(0, self._reset_ui_after_success, final_file_path, dl_id)

    def _reset_ui_after_success(self, final_file_path: str, dl_id: str):
        filename = os.path.basename(final_file_path)
        self._send_notification(title="Download Complete", message=f"Successfully downloaded: {filename}", timeout=4)
            
        # Clean up Active Download Frame
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id]['frame'].destroy()
            del self.active_downloads[dl_id]
            
        # Add to history sidebar
        self._add_to_history(final_file_path)

    def _add_to_history(self, final_file_path: str):
        filename = os.path.basename(final_file_path)
        display_name = f"📁 [Playlist] {filename}" if os.path.isdir(final_file_path) else f"🎬 {filename}"
        
        history_item_frame = ctk.CTkFrame(self.history_scrollable, fg_color="#334155", corner_radius=6)
        history_item_frame.pack(fill="x", pady=(0, 8), ipady=4)
        
        name_label = ctk.CTkLabel(
            history_item_frame, text=display_name, 
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w", justify="left"
        )
        name_label.pack(side="top", fill="x", padx=10, pady=(6, 2))
        
        open_btn = ctk.CTkButton(
            history_item_frame, text="Open Folder", height=24, width=100,
            command=lambda path=final_file_path: self._open_file_location(path),
            fg_color="#334155", hover_color="#475569"
        )
        open_btn.pack(anchor="w", padx=8, pady=6)

    def _open_file_location(self, file_path: str):
        try:
            folder = os.path.dirname(file_path)
            if sys.platform == 'win32': os.startfile(folder)
            elif sys.platform == 'darwin': subprocess.Popen(['open', folder])
            else: subprocess.Popen(['xdg-open', folder])
        except Exception:
            pass

    def _on_download_error(self, e: Exception, dl_id: str):
        self.after(0, self._handle_error_ui, str(e), dl_id)

    def _handle_error_ui(self, error_msg: str, dl_id: str):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id]['status_var'].set("Error! See terminal.")
            self.active_downloads[dl_id]['progress_var'].set(0)
        
        self._send_notification(title="Download Failed", message="An error occurred during download.", timeout=5)
        print(f"Download Error for {dl_id}: {error_msg}")

    def _start_download(self):
        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        referer = self.referer_var.get().strip()
        
        cookie_data = self.cookie_text.get("0.0", "end").strip()
        if "Paste raw cookies" in cookie_data:
            cookie_data = ""

        if not url:
            self._send_notification(title="Missing URL", message="Please enter a valid URL.", timeout=3)
            return

        # Prepare Multi-Thread GUI Slot
        import uuid
        dl_id = str(uuid.uuid4())
        
        custom_name = self.video_title_var.get()
        display_title = custom_name if custom_name else "Video Stream"

        # Create Active Item Frame
        item_frame = ctk.CTkFrame(self.active_scrollable, fg_color="#1E293B", corner_radius=6)
        item_frame.pack(fill="x", pady=(0, 8), padx=5, ipady=4)
        
        lbl_title = ctk.CTkLabel(item_frame, text=display_title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        lbl_title.pack(fill="x", padx=10, pady=(4, 0))
        
        prg_var = tk.DoubleVar(value=0)
        prg_bar = ctk.CTkProgressBar(item_frame, variable=prg_var, height=6, progress_color="#10B981")
        prg_bar.pack(fill="x", padx=10, pady=(6, 4))
        
        stat_var = tk.StringVar(value="Connecting...")
        lbl_stat = ctk.CTkLabel(item_frame, textvariable=stat_var, font=ctk.CTkFont(size=12), text_color="#94A3B8", anchor="w")
        lbl_stat.pack(fill="x", padx=10, pady=(0, 4))
        
        self.active_downloads[dl_id] = {
            'frame': item_frame,
            'progress_var': prg_var,
            'status_var': stat_var
        }

        # Clear Input fields for next download
        self.url_var.set("")
        self.video_title_var.set("")
        
        # Fire background thread
        headers = {"Referer": referer} if referer else None
        
        # We wrap the hook to inject our dl_id
        def hook_wrapper(d):
            self._progress_hook(d, dl_id)

        downloader = M3U8Downloader(progress_hook=hook_wrapper)
        downloader.download_async(
            url=url, 
            output_path=output_dir,
            headers=headers,
            cookies=cookie_data,
            custom_name=custom_name,
            completion_callback=lambda f: self._on_download_complete(f, dl_id),
            error_callback=lambda e: self._on_download_error(e, dl_id)
        )
