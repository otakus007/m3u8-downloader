# M3U8 Downloader Authentication Plan

## Goal

To handle `403 Forbidden` errors by allowing users to pass necessary HTTP Headers (like `Referer`, `User-Agent`) or `Cookies` which the source website requires for downloading the M3U8 stream.

## Architecture & Data Flow Update

The application will be updated across all 3 layers:

1. **GUI Layer (`gui/app.py`)**:
   - Add a "Headers/Cookies" text area or entry fields.
   - Users can paste their raw cookie string (e.g. `session_id=123; user=abc`) or a specific `Referer` URL.
   - Pass this string to `downloader.download_async()`.
   - **[NEW] Window Controls**: Remove `self.resizable(False, False)` constraints to allow resizing, maximizing, and native OS window handling.
   - **[NEW] Download Management**: Add a "History" or "Downloads" section (e.g. using a `CTkScrollableFrame`). When a download finishes, log the file path and add an "Open Folder" button to quickly navigate to the downloaded file.

2. **CLI Layer (`cli/parser.py`)**:
   - Add arguments `--cookies` and `--referer`.

3. **Core Layer (`core/downloader.py`)**:
   - Update `M3U8Downloader.download()` to accept `headers` and `cookie` parameters.
   - Inject these into `yt-dlp`'s `ydl_opts` using the `http_headers` and `cookiefile` or `cookie` fields.

## Tasks

- [ ] Task 1: **Update Core Logic (`core/downloader.py`)**
  - Action: Add `headers: dict` and `cookies: str` to `download()` and pass them to `yt_dlp` options.
  - Verify: yt-dlp receives the headers correctly.
- [ ] Task 2: **Update CLI Parser (`cli/parser.py`)**
  - Action: Add `--referer` and `--cookie` flags. Link to Core.
- [ ] Task 3: **Update GUI (`gui/app.py`)**
  - Action: Add a new section in the GUI for "Authentication" with a text entry for `Referer` and `Cookies`. Make it blend with the `ui-ux-pro-max` styling.
  - Verify: App layout accommodates the new fields and passes data to Core.

## Done When

- A user can copy their Cookies/Referer from the browser's Network Tab and paste it into the Go-live GUI to bypass the 403 Forbidden error.
