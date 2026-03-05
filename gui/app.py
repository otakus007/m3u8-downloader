import os
import re
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from core.downloader import M3U8Downloader

class M3U8DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings (Task 4: Native Window Controls & Resizing)
        self.title("M3U8 Downloader Pro")
        self.geometry("900x550")
        self.minsize(800, 500)
        
        # Apply global appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Core State Variables
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=os.getcwd())
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
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, text="Download History", 
            font=ctk.CTkFont(size=18, weight="bold")
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
            font=ctk.CTkFont(family="Inter", size=30, weight="bold")
        )
        self.header_label.pack(anchor="w", pady=(0, 4))
        
        self.sub_label = ctk.CTkLabel(
            self.main_frame, 
            text="Download HLS/M3U8 streams to MP4. Options to bypass 403 Forbidden.", 
            font=ctk.CTkFont(size=16), text_color="#94A3B8"
        )
        self.sub_label.pack(anchor="w", pady=(0, 24))

        # URL Input
        self.url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.url_frame.pack(fill="x", pady=(0, 16))

        self.url_entry = ctk.CTkEntry(
            self.url_frame, textvariable=self.url_var,
            placeholder_text="Paste M3U8 URL here...",
            height=50, font=ctk.CTkFont(size=16),
            border_width=1, border_color="#334155", fg_color="#0F172A",
            corner_radius=8
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.sniff_btn = ctk.CTkButton(
            self.url_frame, text="🌐 Auto-Capture Browser", command=self._open_sniffer,
            width=200, height=50, corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#059669", hover_color="#047857" # emerald-600
        )
        self.sniff_btn.pack(side="right")

        # Directory Picker
        self.dir_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dir_frame.pack(fill="x", pady=(0, 16))

        self.dir_btn = ctk.CTkButton(
            self.dir_frame, text="Choose Output Folder", command=self._select_directory,
            width=160, height=44, corner_radius=8,
            font=ctk.CTkFont(size=15, weight="normal"),
            fg_color="#334155", hover_color="#475569", text_color="#F8FAFC"
        )
        self.dir_btn.pack(side="left")

        self.dir_label = ctk.CTkLabel(
            self.dir_frame, textvariable=self.output_dir_var,
            font=ctk.CTkFont(size=14), text_color="#64748B"
        )
        self.dir_label.pack(side="left", padx=(12, 0))

        # ==========================================
        # Authentication Section (Expandable/Optional)
        # ==========================================
        self.auth_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E293B", corner_radius=8)
        self.auth_frame.pack(fill="x", pady=(0, 24), ipadx=10, ipady=10)
        
        self.auth_label = ctk.CTkLabel(
            self.auth_frame, text="Authentication (Optional)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.auth_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.referer_entry = ctk.CTkEntry(
            self.auth_frame, textvariable=self.referer_var,
            placeholder_text="Referer URL (e.g. https://example.com/video-page)",
            height=44, font=ctk.CTkFont(size=16), corner_radius=6, border_color="#475569"
        )
        self.referer_entry.pack(fill="x", padx=10, pady=(0, 10))

        self.cookie_text = ctk.CTkTextbox(
            self.auth_frame, height=80, font=ctk.CTkFont(size=15), corner_radius=6, border_color="#475569", border_width=1
        )
        self.cookie_text.insert("0.0", "Paste raw cookies here if required...")
        self.cookie_text.bind("<FocusIn>", self._clear_cookie_placeholder)
        self.cookie_text.pack(fill="x", padx=10, pady=(0, 10))

        # ==========================================
        # Action & Progress
        # ==========================================
        self.dl_btn = ctk.CTkButton(
            self.main_frame, text="Start Download", command=self._start_download,
            height=54, corner_radius=8, font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8"
        )
        self.dl_btn.pack(fill="x", pady=(0, 16))

        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame, variable=self.progress_var, height=10,
            corner_radius=4, progress_color="#3B82F6", fg_color="#1E293B"
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0) 

        self.status_label = ctk.CTkLabel(
            self.main_frame, textvariable=self.status_var,
            font=ctk.CTkFont(size=14), text_color="#94A3B8"
        )
        self.status_label.pack(anchor="w")

    # ==========================================================================
    # LOGIC HANDLERS
    # ==========================================================================
    def _open_sniffer(self):
        from browser.sniffer import WebSniffer
        self.status_var.set("Starting Web Browser for Sniffing...")
        self.sniff_btn.configure(state="disabled", text="Opening...")
        
        sniffer = WebSniffer(
            on_found_callback=self._on_sniffer_found,
            on_error_callback=self._on_sniffer_error
        )
        sniffer.start_sniffing()

    def _on_sniffer_found(self, url: str, cookies: str, referer: str, title: str):
        # Force thread safety transition back to tkinter Main Thread
        self.after(0, self._update_ui_from_sniffer, url, cookies, referer, title)

    def _update_ui_from_sniffer(self, url: str, cookies: str, referer: str, title: str):
        # Strip illegal characters for filenames
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        
        self.url_var.set(url)
        self.referer_var.set(referer)
        self.video_title_var.set(safe_title)
        
        self.cookie_text.delete("0.0", "end")
        self.cookie_text.insert("0.0", cookies)
        
        self.status_var.set(f"Captured: {safe_title} (Ready to download)")
        # Do not re-enable the Sniff button because the browser is STILL open.
        # We will re-enable it on error/close
        # Remove messagebox to avoid interrupting the user while they are clicking around in the browser
        print(f"Auto-Captured M3U8 for: {title}")

    def _on_sniffer_error(self, e: Exception):
        self.after(0, self._handle_sniffer_error, str(e))

    def _handle_sniffer_error(self, err: str):
        self.status_var.set("Browser sniffer closed or errored.")
        self.sniff_btn.configure(state="normal", text="🌐 Auto-Capture Browser")
        print(f"Sniffer error/close: {err}")

    def _clear_cookie_placeholder(self, event):
        if "Paste raw cookies" in self.cookie_text.get("0.0", "end"):
            self.cookie_text.delete("0.0", "end")

    def _select_directory(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if folder:
            self.output_dir_var.set(folder)

    def _progress_hook(self, d: dict):
        if d['status'] == 'downloading':
            try:
                # Cleanup ALL ANSI formatting artifacts from all output fields
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                
                percent_str = str(d.get('_percent_str', '0%')).replace('%', '').strip()
                percent_clean = ansi_escape.sub('', percent_str)
                percent = float(percent_clean) / 100.0
                
                speed_str = str(d.get('_speed_str', 'N/A'))
                speed_clean = ansi_escape.sub('', speed_str).strip()
                
                eta_str = str(d.get('_eta_str', 'N/A'))
                eta_clean = ansi_escape.sub('', eta_str).strip()
                
                # Check for playlist metadata
                info_dict = d.get('info_dict', {})
                playlist_index = info_dict.get('playlist_index')
                playlist_count = info_dict.get('playlist_count')
                
                if playlist_index and playlist_count:
                    prefix = f"[Video {playlist_index}/{playlist_count}] "
                else:
                    prefix = ""
                
                status_text = f"{prefix}Downloading... {percent*100:.1f}%  |  Speed: {speed_clean}  |  ETA: {eta_clean}"
                self.after(0, self._update_progress_ui, percent, status_text)
            except Exception:
                pass
        
        elif d['status'] == 'finished':
            self.after(0, self._update_progress_ui, 1.0, "Merging and finalizing MP4 file... Please wait.")

    def _update_progress_ui(self, percent: float, text: str):
        self.progress_var.set(percent)
        self.status_var.set(text)

    def _on_download_complete(self, final_file_path: str):
        self.after(0, self._reset_ui_after_success, final_file_path)

    def _reset_ui_after_success(self, final_file_path: str):
        self.status_var.set("Download completed successfully!")
        self.progress_var.set(1.0)
        self.dl_btn.configure(state="normal", text="Start Download")
        self.url_entry.configure(state="normal")
        
        # Add to history sidebar
        self._add_to_history(final_file_path)
        messagebox.showinfo("Download Complete", "The video was downloaded successfully!", parent=self)

    def _add_to_history(self, final_file_path: str):
        filename = os.path.basename(final_file_path)
        
        # Check if the returned path is a directory (Playlist) or a file (Single Video)
        if os.path.isdir(final_file_path):
            display_name = f"📁 [Playlist] {filename}"
        else:
            display_name = f"🎬 {filename}"
        
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
        """Cross-platform method to open file explorer and select the file."""
        try:
            folder = os.path.dirname(file_path)
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            print(f"Cannot open folder: {e}")

    def _on_download_error(self, e: Exception):
        self.after(0, self._handle_error_ui, str(e))

    def _handle_error_ui(self, error_msg: str):
        self.status_var.set("Error occurred during download.")
        self.progress_var.set(0)
        self.dl_btn.configure(state="normal", text="Start Download")
        self.url_entry.configure(state="normal")
        messagebox.showerror("Download Error", f"An error occurred:\n\n{error_msg}", parent=self)

    def _start_download(self):
        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        referer = self.referer_var.get().strip()
        
        cookie_data = self.cookie_text.get("0.0", "end").strip()
        if "Paste raw cookies" in cookie_data:
            cookie_data = ""

        if not url:
            messagebox.showwarning("Missing URL", "Please enter a valid M3U8 URL to proceed.", parent=self)
            return

        self.dl_btn.configure(state="disabled", text="Initializing...")
        self.url_entry.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Connecting to stream...")

        headers = {"Referer": referer} if referer else None
        custom_name = self.video_title_var.get()

        downloader = M3U8Downloader(progress_hook=self._progress_hook)
        downloader.download_async(
            url=url, 
            output_path=output_dir,
            headers=headers,
            cookies=cookie_data,
            custom_name=custom_name,
            completion_callback=self._on_download_complete,
            error_callback=self._on_download_error
        )
