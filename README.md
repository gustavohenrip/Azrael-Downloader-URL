# Professional Video Downloader Pro

A modern, cross-platform video downloader application built with Python and tkinter. Download videos and audio from multiple platforms with high-quality output, professional interface, and advanced format selection capabilities.

## Features

- **Multi-Platform Support**: Download videos from YouTube, Vimeo, and hundreds of other video platforms
- **High-Quality Downloads**: Support for multiple video qualities (1080p, 720p, 480p, 360p, 240p)
- **Audio-Only Downloads**: Extract audio in MP3, M4A, WAV, and FLAC formats
- **Modern UI**: Professional dark theme with rounded corners and smooth animations
- **Real-Time Progress**: Live download progress tracking with percentage display
- **Video Information**: Display video details including title, duration, views, and thumbnail
- **Format Selection**: Choose from multiple video and audio formats or select specific format IDs
- **Smart Quality Detection**: Only show available qualities for each video
- **Download Cancellation**: Cancel downloads in progress with dedicated cancel button
- **Automatic Dependency Management**: Auto-installs required components with fallback options

## System Requirements

- Python 3.7 or higher
- 4GB RAM recommended for processing large videos
- Internet connection for downloading videos
- Minimum 100MB free disk space

## Installation and Usage

### Windows

1. **Install Python 3.7+** from python.org
2. **Clone or download this repository**
3. **Open Command Prompt** and navigate to the project folder
4. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```
5. **Run the application**:
   ```cmd
   python main.py
   ```

### macOS

1. **Install Python 3.7+** via Homebrew or python.org:
   ```bash
   brew install python
   ```
2. **Clone or download this repository**
3. **Open Terminal** and navigate to the project folder
4. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```
5. **Run the application**:
   ```bash
   python3 main.py
   ```

### Linux (Ubuntu/Debian)

1. **Install Python and pip**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-tkinter
   ```
2. **Clone or download this repository**
3. **Open Terminal** and navigate to the project folder
4. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```
5. **Run the application**:
   ```bash
   python3 main.py
   ```

### Linux (CentOS/RHEL/Fedora)

1. **Install Python and pip**:
   ```bash
   sudo dnf install python3 python3-pip python3-tkinter
   ```
2. **Follow steps 2-5 from Ubuntu/Debian instructions**

## How to Use

1. **Launch the application** using the appropriate command for your system
2. **Enter a video URL** in the input field (YouTube, Vimeo, etc.)
3. **Click "Analyze"** to fetch video information and available formats
4. **Select quality and format** from the dropdown menus or click on a specific format in the list
5. **Choose download location** using the Browse button
6. **Click "Download Video"** to start the download
7. **Monitor progress** in real-time with the progress bar and log
8. **Cancel if needed** using the Cancel Download button

## Supported Formats

### Video Formats
- MP4 (recommended for compatibility)
- WebM
- MKV

### Audio Formats
- MP3 (most compatible)
- M4A (high quality)
- WAV (uncompressed)
- FLAC (lossless)

## Supported Platforms

The application supports downloading from hundreds of video platforms including:
- YouTube
- Vimeo
- Facebook
- Instagram
- TikTok
- Twitter
- Dailymotion
- And many more

## Building Executable

To create a standalone executable:

### Windows
```cmd
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico main.py
```

### macOS/Linux
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```

The executable will be created in the `dist` folder.

## Troubleshooting

### Common Issues

**Installation Problems**: Ensure Python 3.7+ is installed and pip is updated
**Download Failures**: Check internet connection and verify the video URL is accessible
**Quality Issues**: Some platforms may limit available qualities
**Permission Errors**: Try installing dependencies with `--user` flag
**FFmpeg Missing**: Install FFmpeg manually for format conversion support

### Error Messages

If you encounter dependency errors:
```bash
pip install --upgrade yt-dlp requests pillow
```

For FFmpeg installation:
- **Windows**: Download from ffmpeg.org
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`

## Technical Details

Built with:
- Python tkinter for the GUI framework
- yt-dlp for video downloading capabilities
- PIL/Pillow for image processing
- Custom UI components with Canvas-based rounded designs
- Robust error handling and progress tracking
- Multi-threading for responsive interface

## License

This project is for educational and personal use only. Respect copyright laws and platform terms of service when downloading content.

## Contributing

Contributions are welcome. Please ensure code follows the existing style and includes appropriate error handling.
