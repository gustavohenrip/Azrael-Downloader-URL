import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import subprocess
import requests
from urllib.parse import urlparse
import json
import re
from PIL import Image, ImageTk
import io
import glob
import time
from button_styles import ModernButton, RoundedEntry, RoundedProgressBar, RoundedCombobox

class VideoDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Professional Video Downloader Pro")
        self.root.geometry("1100x1000")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(True, True)
        
        self.download_path = os.path.expanduser("~/Downloads")
        self.is_downloading = False
        self.video_info = None
        self.thumbnail_image = None
        self.selected_format_id = None
        self.download_process = None
        
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a', 
            'bg_tertiary': '#2a2a2a',
            'accent': '#0078d4',
            'accent_hover': '#106ebe',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'border': '#333333'
        }
        
        self.setup_styles()
        self.setup_ui()
        self.check_dependencies()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TCombobox', 
                       fieldbackground=self.colors['bg_tertiary'],
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       arrowcolor=self.colors['accent'],
                       borderwidth=1,
                       relief='flat',
                       insertcolor=self.colors['text_primary'])
        
        style.map('Modern.TCombobox',
                 fieldbackground=[('readonly', self.colors['bg_tertiary'])],
                 selectbackground=[('readonly', self.colors['accent'])],
                 selectforeground=[('readonly', self.colors['text_primary'])],
                 bordercolor=[('focus', self.colors['accent'])])
        
        style.configure('Modern.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        style.configure('Modern.TFrame',
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       relief='solid')
    
    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        header_frame.pack(fill="x", pady=(0, 30))
        
        title_label = tk.Label(header_frame, text="Professional Video Downloader Pro", 
                              font=("Segoe UI", 24, "bold"), fg=self.colors['accent'], 
                              bg=self.colors['bg_primary'])
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Download videos from any platform with premium quality", 
                                 font=("Segoe UI", 11), fg=self.colors['text_secondary'], 
                                 bg=self.colors['bg_primary'])
        subtitle_label.pack(pady=(8, 0))
        
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill="both", expand=True)
        
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_secondary'], 
                             relief="flat", bd=0)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_secondary'], 
                              relief="flat", bd=0)
        right_panel.pack(side="right", fill="y", padx=(15, 0))
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
    
    def setup_left_panel(self, parent):
        inner_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        inner_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        url_section = self.create_modern_section(inner_frame, "Video URL")
        
        url_input_frame = tk.Frame(url_section, bg=self.colors['bg_secondary'])
        url_input_frame.pack(fill="x", padx=15, pady=15)
        
        self.url_entry = RoundedEntry(url_input_frame, bg_color=self.colors['bg_tertiary'], 
                                     fg_color=self.colors['text_primary'], width=400, height=44)
        self.url_entry.pack(side="left", fill="x", expand=True)
        
        analyze_btn = ModernButton(url_input_frame, text="Analyze", command=self.get_video_info,
                                  bg_color=self.colors['accent'], hover_color=self.colors['accent_hover'],
                                  width=100, height=44)
        analyze_btn.pack(side="right", padx=(15, 0))
        
        settings_section = self.create_modern_section(inner_frame, "Download Settings")
        
        settings_inner = tk.Frame(settings_section, bg=self.colors['bg_secondary'])
        settings_inner.pack(fill="x", padx=15, pady=15)
        
        path_frame = tk.Frame(settings_inner, bg=self.colors['bg_secondary'])
        path_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(path_frame, text="Download Path:", font=("Segoe UI", 11), 
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(anchor="w")
        
        path_input_frame = tk.Frame(path_frame, bg=self.colors['bg_secondary'])
        path_input_frame.pack(fill="x", pady=(8, 0))
        
        self.path_entry = RoundedEntry(path_input_frame, bg_color=self.colors['bg_tertiary'], 
                                      fg_color=self.colors['text_primary'], width=350, height=36)
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.path_entry.insert(0, self.download_path)
        
        browse_btn = ModernButton(path_input_frame, text="Browse", command=self.browse_folder,
                                 bg_color=self.colors['accent'], hover_color=self.colors['accent_hover'],
                                 width=80, height=36)
        browse_btn.pack(side="right", padx=(15, 0))
        
        quality_format_frame = tk.Frame(settings_inner, bg=self.colors['bg_secondary'])
        quality_format_frame.pack(fill="x", pady=(0, 15))
        
        quality_frame = tk.Frame(quality_format_frame, bg=self.colors['bg_secondary'])
        quality_frame.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        tk.Label(quality_frame, text="Quality:", font=("Segoe UI", 11), 
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(anchor="w")
        
        self.quality_combo = RoundedCombobox(quality_frame, 
                                           values=["1080p", "720p", "480p", "360p", "240p", "audio-only"],
                                           bg_color=self.colors['bg_tertiary'], fg_color=self.colors['text_primary'],
                                           width=150, height=36)
        self.quality_combo.set("720p")
        self.quality_combo.pack(fill="x", pady=(8, 0))
        
        format_frame = tk.Frame(quality_format_frame, bg=self.colors['bg_secondary'])
        format_frame.pack(side="right", fill="x", expand=True, padx=(15, 0))
        
        tk.Label(format_frame, text="Format:", font=("Segoe UI", 11), 
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(anchor="w")
        
        self.format_combo = RoundedCombobox(format_frame, 
                                          values=["mp4", "webm", "mkv", "mp3", "m4a", "wav", "flac"],
                                          bg_color=self.colors['bg_tertiary'], fg_color=self.colors['text_primary'],
                                          width=150, height=36)
        self.format_combo.set("mp4")
        self.format_combo.pack(fill="x", pady=(8, 0))
        
        download_section = tk.Frame(inner_frame, bg=self.colors['bg_secondary'])
        download_section.pack(fill="x", pady=(20, 15))
        
        self.download_btn = ModernButton(download_section, text="Download Video", 
                                        command=self.start_download, bg_color=self.colors['accent'], 
                                        hover_color=self.colors['accent_hover'], width=400, height=50,
                                        font=("Segoe UI", 14, "bold"))
        self.download_btn.pack(fill="x")
        
        self.cancel_btn = ModernButton(download_section, text="Cancel Download", 
                                      command=self.cancel_download, bg_color='#dc3545', 
                                      hover_color='#c82333', width=400, height=50,
                                      font=("Segoe UI", 14, "bold"))
        self.cancel_btn.pack(fill="x", pady=(10, 0))
        self.cancel_btn.pack_forget()
        
        progress_section = self.create_modern_section(inner_frame, "Download Progress")
        
        progress_inner = tk.Frame(progress_section, bg=self.colors['bg_secondary'])
        progress_inner.pack(fill="x", padx=15, pady=15)
        
        self.progress_bar = RoundedProgressBar(progress_inner, width=400, height=24,
                                             bg_color=self.colors['bg_tertiary'], 
                                             fill_color=self.colors['accent'])
        self.progress_bar.pack(fill="x", pady=(0, 8))
        
        self.status_label = tk.Label(progress_inner, text="Ready to download", 
                                    font=("Segoe UI", 11), fg=self.colors['text_secondary'], 
                                    bg=self.colors['bg_secondary'])
        self.status_label.pack(anchor="w")
        
        log_section = self.create_modern_section(inner_frame, "Download Log")
        
        log_inner = tk.Frame(log_section, bg=self.colors['bg_secondary'])
        log_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.log_text = tk.Text(log_inner, bg=self.colors['bg_primary'], fg=self.colors['text_secondary'], 
                               font=("Consolas", 10), insertbackground=self.colors['text_primary'],
                               bd=0, relief="flat", selectbackground=self.colors['accent'])
        self.log_text.pack(side="left", fill="both", expand=True)
        
        log_scrollbar = tk.Scrollbar(log_inner, bg=self.colors['bg_tertiary'], 
                                    troughcolor=self.colors['bg_secondary'],
                                    activebackground=self.colors['accent'])
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
    
    def create_modern_section(self, parent, title):
        section_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        section_frame.pack(fill="x", pady=(0, 20))
        
        title_frame = tk.Frame(section_frame, bg=self.colors['accent'], height=3)
        title_frame.pack(fill="x")
        
        title_label = tk.Label(section_frame, text=title, font=("Segoe UI", 12, "bold"),
                              fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
        title_label.pack(anchor="w", padx=15, pady=(10, 0))
        
        content_frame = tk.Frame(section_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill="both", expand=True)
        
        return content_frame
    
    def setup_right_panel(self, parent):
        inner_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        inner_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        info_section = self.create_modern_section(inner_frame, "Video Information")
        
        info_inner = tk.Frame(info_section, bg=self.colors['bg_secondary'])
        info_inner.pack(fill="x", padx=15, pady=15)
        
        self.thumbnail_label = tk.Label(info_inner, bg=self.colors['bg_tertiary'], width=30, height=20,
                                       text="No thumbnail", fg=self.colors['text_secondary'],
                                       font=("Segoe UI", 11), relief="flat")
        self.thumbnail_label.pack(pady=(0, 15))
        
        self.title_label = tk.Label(info_inner, text="No video selected", 
                                   font=("Segoe UI", 12, "bold"), fg=self.colors['text_primary'], 
                                   bg=self.colors['bg_secondary'], wraplength=250, justify="left")
        self.title_label.pack(anchor="w", pady=(0, 8))
        
        self.duration_label = tk.Label(info_inner, text="Duration: --", 
                                      font=("Segoe UI", 10), fg=self.colors['text_secondary'], 
                                      bg=self.colors['bg_secondary'])
        self.duration_label.pack(anchor="w", pady=(0, 4))
        
        self.views_label = tk.Label(info_inner, text="Views: --", 
                                   font=("Segoe UI", 10), fg=self.colors['text_secondary'], 
                                   bg=self.colors['bg_secondary'])
        self.views_label.pack(anchor="w", pady=(0, 4))
        
        self.uploader_label = tk.Label(info_inner, text="Uploader: --", 
                                      font=("Segoe UI", 10), fg=self.colors['text_secondary'], 
                                      bg=self.colors['bg_secondary'])
        self.uploader_label.pack(anchor="w", pady=(0, 4))
        
        formats_section = self.create_modern_section(inner_frame, "Available Formats")
        
        formats_inner = tk.Frame(formats_section, bg=self.colors['bg_secondary'])
        formats_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.formats_listbox = tk.Listbox(formats_inner, bg=self.colors['bg_primary'], 
                                         fg=self.colors['text_secondary'], font=("Consolas", 9), 
                                         selectbackground=self.colors['accent'], bd=0, relief="flat",
                                         activestyle='none', highlightthickness=0)
        self.formats_listbox.pack(side="left", fill="both", expand=True)
        
        formats_scrollbar = tk.Scrollbar(formats_inner, bg=self.colors['bg_tertiary'], 
                                        troughcolor=self.colors['bg_secondary'],
                                        activebackground=self.colors['accent'])
        formats_scrollbar.pack(side="right", fill="y")
        self.formats_listbox.config(yscrollcommand=formats_scrollbar.set)
        formats_scrollbar.config(command=self.formats_listbox.yview)
        
        self.formats_listbox.bind('<<ListboxSelect>>', self.on_format_select)
    
    def check_dependencies(self):
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            self.log("yt-dlp is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("Installing yt-dlp...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "yt-dlp"])
                self.log("yt-dlp installed successfully")
            except subprocess.CalledProcessError:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                    self.log("yt-dlp installed successfully")
                except subprocess.CalledProcessError:
                    self.log("Failed to install yt-dlp. Please install manually.")
        
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            self.log("ffmpeg is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("Installing ffmpeg...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "ffmpeg-python"])
                self.log("ffmpeg-python installed. Download ffmpeg manually for full functionality.")
            except subprocess.CalledProcessError:
                self.log("Warning: ffmpeg not found. Some conversions may fail.")
    
    def on_format_select(self, event):
        selection = self.formats_listbox.curselection()
        if selection and self.video_info:
            index = selection[0]
            selected_format = self.video_info['formats'][index]
            
            self.selected_format_id = selected_format.get('format_id')
            
            quality = selected_format.get('height', 'audio-only')
            ext = selected_format.get('ext', 'unknown')
            
            if quality != 'audio-only':
                self.quality_combo.set(f"{quality}p")
            else:
                self.quality_combo.set("audio-only")
            
            self.format_combo.set(ext)
    
    def load_thumbnail(self, thumbnail_url):
        try:
            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            image = image.resize((320, 240), Image.Resampling.LANCZOS)
            
            self.thumbnail_image = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.thumbnail_image, text="", 
                                       width=320, height=240)
            
        except Exception as e:
            self.log(f"Failed to load thumbnail: {str(e)}")
            self.thumbnail_label.config(image="", text="No thumbnail",
                                       width=30, height=20)
    
    def update_format_options(self):
        if not self.video_info or 'formats' not in self.video_info:
            return
        
        formats = self.video_info['formats']
        quality_options = set()
        format_options = set()
        
        for fmt in formats:
            height = fmt.get('height')
            ext = fmt.get('ext', 'unknown')
            
            if height:
                quality_options.add(f"{height}p")
            else:
                quality_options.add("audio-only")
            
            format_options.add(ext)
        
        available_qualities = []
        standard_qualities = ["1080p", "720p", "480p", "360p", "240p"]
        
        for quality in standard_qualities:
            if quality in quality_options:
                available_qualities.append(quality)
        
        if "audio-only" in quality_options:
            available_qualities.append("audio-only")
        
        if not available_qualities:
            available_qualities = sorted([q for q in quality_options if q != "audio-only"], 
                                       key=lambda x: int(x.replace('p', '')), reverse=True)
            if "audio-only" in quality_options:
                available_qualities.append("audio-only")
        
        self.quality_combo.values = available_qualities
        self.format_combo.values = sorted(list(format_options))
        
        current_quality = self.quality_combo.get()
        if current_quality not in available_qualities and available_qualities:
            self.quality_combo.set(available_qualities[0])
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def browse_folder(self, ):
        folder = filedialog.askdirectory(initialdir=self.path_entry.get())
        if folder:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, folder)
            self.download_path = folder
    
    def get_video_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
        
        self.log(f"Analyzing video: {url}")
        self.status_label.config(text="Analyzing video...")
        threading.Thread(target=self._get_video_info_thread, args=(url,), daemon=True).start()
    
    def _get_video_info_thread(self, url):
        try:
            cmd = ["yt-dlp", "--dump-json", "--no-download", url]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.video_info = json.loads(result.stdout)
            
            self.root.after(0, self._update_video_info_ui)
            
        except subprocess.CalledProcessError as e:
            self.log(f"Error getting video info: {e.stderr}")
            self.status_label.config(text="Analysis failed")
        except json.JSONDecodeError:
            self.log("Error parsing video information")
            self.status_label.config(text="Analysis failed")
        except Exception as e:
            self.log(f"Unexpected error: {str(e)}")
            self.status_label.config(text="Analysis failed")
    
    def _update_video_info_ui(self):
        if not self.video_info:
            return
        
        title = self.video_info.get('title', 'Unknown Title')
        duration = self.video_info.get('duration', 0)
        view_count = self.video_info.get('view_count', 0)
        uploader = self.video_info.get('uploader', 'Unknown')
        thumbnail_url = self.video_info.get('thumbnail', '')
        
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
        view_count_str = f"{view_count:,}" if view_count else "Unknown"
        
        self.title_label.config(text=title)
        self.duration_label.config(text=f"Duration: {duration_str}")
        self.views_label.config(text=f"Views: {view_count_str}")
        self.uploader_label.config(text=f"Uploader: {uploader}")
        
        if thumbnail_url:
            threading.Thread(target=self.load_thumbnail, args=(thumbnail_url,), daemon=True).start()
        
        self.formats_listbox.delete(0, tk.END)
        if 'formats' in self.video_info:
            for fmt in self.video_info['formats']:
                height = fmt.get('height', 'audio')
                ext = fmt.get('ext', 'unknown')
                filesize = fmt.get('filesize', 0)
                
                if height == 'audio':
                    quality_str = "Audio only"
                else:
                    quality_str = f"{height}p"
                
                if filesize:
                    size_mb = filesize / (1024 * 1024)
                    size_str = f" ({size_mb:.1f} MB)"
                else:
                    size_str = ""
                
                format_str = f"{quality_str} - {ext}{size_str}"
                self.formats_listbox.insert(tk.END, format_str)
        
        self.update_format_options()
        self.status_label.config(text="Video analyzed successfully")
        self.log("Video analysis completed successfully")
    
    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
        
        download_path = self.path_entry.get().strip()
        if not os.path.exists(download_path):
            messagebox.showerror("Error", "Download path does not exist")
            return
        
        self.is_downloading = True
        self.download_btn.pack_forget()
        self.cancel_btn.pack(fill="x")
        self.status_label.config(text="Starting download...")
        
        threading.Thread(target=self._download_thread, args=(url, download_path), daemon=True).start()
    
    def cancel_download(self):
        if self.download_process:
            self.download_process.terminate()
            self.log("Download cancelled by user")
            self.status_label.config(text="Download cancelled")
            self.progress_bar.set_progress(0)
        self.is_downloading = False
        self.cancel_btn.pack_forget()
        self.download_btn.pack(fill="x")
    
    def _download_thread(self, url, download_path):
        try:
            if self.selected_format_id:
                format_selector = self.selected_format_id
                cmd_extra = []
                self.log(f"Using selected format ID: {format_selector}")
            else:
                quality = self.quality_combo.get()
                format_ext = self.format_combo.get()
                
                audio_formats = ["mp3", "m4a", "wav", "flac"]
                video_formats = ["mp4", "webm", "mkv"]
                
                if quality == "audio-only":
                    if format_ext in audio_formats:
                        if format_ext == "mp3":
                            format_selector = "bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best"
                            cmd_extra = ["--extract-audio", "--audio-format", "mp3"]
                        elif format_ext == "m4a":
                            format_selector = "bestaudio[ext=m4a]/bestaudio/best"
                            cmd_extra = ["--extract-audio", "--audio-format", "m4a"]
                        elif format_ext == "wav":
                            format_selector = "bestaudio/best"
                            cmd_extra = ["--extract-audio", "--audio-format", "wav"]
                        elif format_ext == "flac":
                            format_selector = "bestaudio/best"
                            cmd_extra = ["--extract-audio", "--audio-format", "flac"]
                        else:
                            format_selector = "bestaudio/best"
                            cmd_extra = []
                    else:
                        format_selector = "bestaudio/best"
                        cmd_extra = ["--extract-audio", "--audio-format", "mp3"]
                        self.log("Warning: Video format selected for audio-only. Converting to MP3.")
                else:
                    height = quality.replace('p', '')
                    if format_ext in video_formats:
                        if format_ext == "mp4":
                            format_selector = f"best[height<={height}][ext=mp4]/best[height<={height}][vcodec^=avc]/best[height<={height}]/best"
                        elif format_ext == "webm":
                            format_selector = f"best[height<={height}][ext=webm]/best[height<={height}]/best"
                        elif format_ext == "mkv":
                            format_selector = f"best[height<={height}][ext=mkv]/best[height<={height}]/best"
                        else:
                            format_selector = f"best[height<={height}]/best"
                        cmd_extra = ["--recode-video", format_ext] if format_ext != "webm" else []
                    else:
                        format_selector = f"best[height<={height}][ext=mp4]/best[height<={height}]/best"
                        cmd_extra = ["--recode-video", "mp4"]
                        self.log("Warning: Audio format selected for video. Converting to MP4.")
            
            cmd = [
                "yt-dlp",
                "--format", format_selector,
                "--output", os.path.join(download_path, "%(title)s.%(ext)s"),
                "--newline",
                url
            ]
            
            cmd.extend(cmd_extra)
            
            self.log(f"Starting download: {url}")
            self.log(f"Command: {' '.join(cmd)}")
            
            self.download_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                                   text=True, universal_newlines=True)
            
            while True:
                output = self.download_process.stdout.readline()
                if output == '' and self.download_process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
                    if "[download]" in output and "%" in output:
                        match = re.search(r'(\d+(?:\.\d+)?)%', output)
                        if match:
                            percent = float(match.group(1))
                            self.root.after(0, lambda p=percent: self.progress_bar.set_progress(p))
                            self.root.after(0, lambda p=percent: self.status_label.config(text=f"Downloading... {p:.1f}%"))
            
            stderr = self.download_process.stderr.read()
            if stderr:
                self.log(f"Errors: {stderr}")
            
            if self.download_process.returncode == 0:
                self.log("Download completed successfully!")
                self.root.after(0, lambda: self.status_label.config(text="Download completed"))
                self.root.after(0, lambda: self.progress_bar.set_progress(100))
            else:
                search_pattern = os.path.join(download_path, "*")
                files_after = glob.glob(search_pattern)
                
                if any(f for f in files_after if os.path.getmtime(f) > time.time() - 300):
                    self.log("Download completed with warnings (file was created)")
                    self.root.after(0, lambda: self.status_label.config(text="Download completed"))
                    self.root.after(0, lambda: self.progress_bar.set_progress(100))
                else:
                    self.log("Download failed!")
                    self.root.after(0, lambda: self.status_label.config(text="Download failed"))
        
        except Exception as e:
            self.log(f"Error during download: {str(e)}")
            self.root.after(0, lambda: self.status_label.config(text="Error occurred"))
        
        finally:
            self.is_downloading = False
            self.download_process = None
            self.selected_format_id = None
            self.root.after(0, self._reset_download_state)
    
    def _reset_download_state(self):
        self.cancel_btn.pack_forget()
        self.download_btn.pack(fill="x")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoDownloader()
    app.run()
