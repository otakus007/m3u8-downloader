# M3U8 Downloader Plan

## Goal

A Desktop GUI and CLI application in Python for downloading and merging M3U8 (HLS) streams into MP4 files using `yt-dlp`. It must support multiple OS environments (Windows, Linux).

## Architecture

We are building a **Monolithic Python Application** using a 3-layer architecture:

- **Core Layer (`core/`)**: Handles the business logic of downloading, merging, and progress reporting. Wraps `yt-dlp` to execute downloads, capture progress hooks, and manage the download lifecycle asynchronously.
- **CLI Layer (`cli/`)**: Uses Python's built-in `argparse`. Parses command-line arguments and invokes the Core Layer directly.
- **GUI Layer (`gui/`)**: Built with `customtkinter` (for modern, dark-mode styling). Provides an input field for the URL, a directory picker for the output path, a start button, and a progress bar. It runs the Core Layer in a background thread to prevent UI freezing and uses a thread-safe callback system to update the UI with progress data.

## Data Flow

1. **Input**: User provides URL & Output Path (via CLI args or GUI).
2. **Initialization**: Input is passed to `core.downloader.M3U8Downloader`.
3. **Configuration**: `M3U8Downloader` configures `yt-dlp` with the correct output template and a progress hook function.
4. **Execution**: `yt-dlp` downloads the `.ts` chunks. The progress hook is called periodically with speed, ETA, and progress percentage.
5. **State Update**: If in GUI mode, the progress hook updates the progress bar on the main UI thread via `window.after` safely. If CLI, it prints to stdout.
6. **Merge Phase**: Once all chunks are downloaded, `yt-dlp` uses `ffmpeg` to merge them into a single `.mp4` file.
7. **Completion**: Completion callback is fired, updating UI status to "Completed".

## Tasks

- [ ] Task 1: **Setup Environmental Scaffolding**
  - Action: Create `requirements.txt` with `yt-dlp` and `customtkinter`. Setup base folder structure.
  - Verify: `pip install -r requirements.txt` succeeds and project folders exist.
- [ ] Task 2: **Implement Core Logic (`core/downloader.py`)**
  - Action: Create `M3U8Downloader` class wrapping `yt-dlp` with a `progress_hook` callback param.
  - Verify: Python shell can run a test download with a printed callback.
- [ ] Task 3: **Implement CLI Layer (`cli/parser.py`)**
  - Action: Setup `argparse` for url and output folder arguments. Link to `M3U8Downloader`.
  - Verify: `python main.py <url> -o ./` starts download with terminal output.
- [ ] Task 4: **Implement GUI Layout (`gui/app.py`)**
  - Action: Create `customtkinter` main window with inputs (URL, path), button, and progress bar layout.
  - Verify: `python main.py` opens the GUI correctly without functionality.
- [ ] Task 5: **Integrate GUI with Core (`gui/app.py`)**
  - Action: Bind the download button to start a background `threading.Thread` that calls `M3U8Downloader` and update progress bar via the callback using `after()`.
  - Verify: Clicking download in GUI downloads a file and updates the progress bar smoothly.
- [ ] Task 6: **Implement Application Routing (`main.py`)**
  - Action: Detect if sys arguments are passed (>1) to run CLI mode, else run GUI mode.
  - Verify: App runs in CLI mode when args provided, GUI mode when not.

## Done When

- [ ] M3U8 videos can be downloaded via CLI and GUI cleanly.
- [ ] Progress is visually reported in both modes (Console logs vs GUI Progress bar).
- [ ] Final output is a playable `.mp4` file.
- [ ] Application does not freeze in GUI mode during download.
