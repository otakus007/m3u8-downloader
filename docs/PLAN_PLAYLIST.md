# PLAN: YouTube Playlist Management

## 1. ANALYSIS

Hiện tại phần mềm sử dụng `yt-dlp` làm core, bản thân `yt-dlp` đã hỗ trợ tải playlist mặc định. Tuy nhiên, kiến trúc hiện tại của `core/downloader.py` và `gui/app.py` đang mặc định xử lý luồng (1 URL = 1 Video).
Các vấn đề xảy ra nếu tải Playlist với code hiện tại:

1. `extract_info` sẽ trả về 1 mảng `entries` (các video) thay vì thông tin 1 video đơn lẻ. Việc gọi `info.get('title')` sẽ lấy tên của Playlist, dẫn đến lỗi đặt tên file.
2. Tham số `custom_name` nếu áp dụng cho Playlist sẽ gây lỗi ghi đè (tất cả video trong list bị lưu cùng 1 tên) hoặc sai định dạng.
3. Hook tiến trình (`progress_hook`) hiện chỉ hiển thị `%` của video hiện tại, người dùng không biết đang tải video thứ mấy trên tổng số bao nhiêu video trong playlist.
4. Lịch sử tải xuống (Download History) cần nhận dạng được là tải playlist để hiện tên Thư mục Playlist, thay vì chỉ hiện tên 1 video.

## 2. PLANNING (Task Breakdown)

Cần thực hiện các thay đổi tại 2 Layer: Core và GUI.

### 2.1. Cập nhật Core Downloader (`core/downloader.py`)

- **Detect Playlist**: Trong `download_async`, khi gọi `extract_info(download=False)`, kiểm tra key `_type`. Nếu `_type == 'playlist'`, xử lý luồng Playlist.
- **Output Template (`outtmpl`)**:
  - Nếu là Single Video: Giữ nguyên logic cũ (`custom_name` hoặc `title`).
  - Nếu là Playlist: Sử dụng cấu trúc thư mục `output_path / %(playlist_title)s / %(playlist_index)s - %(title)s.%(ext)s`.
- **Callback**: Sửa đổi `completion_callback` để truyền về tên Thư mục của Playlist (nếu là playlist) hoặc file mp4 (nếu là single video).

### 2.2. Cập nhật GUI (`gui/app.py`)

- **Bắt Hook Playlist Progress**: Nâng cấp hàm `_progress_hook`. `yt-dlp` cung cấp các biến trong custom output hook, ví dụ thông tin playlist. Tuy nhiên, cách dễ nhất là thay đổi `status_text` thành: `[Video 1/15] Downloading... 50% | Speed...`.
- Để lấy index, ta có thể phải parse output hoặc lấy từ d dict của `yt-dlp` chứa key `info_dict` -> `playlist_index` và `playlist_count`.
- **Download History**: Khi nhận callback thành công, hiển thị lên History là `📁 [Playlist] Tên Playlist`. Nút `Open` sẽ mở thư mục chứa toàn bộ video đó.

## 3. SOLUTIONING

**Luồng hoạt động mới:**

1. Khi ấn "Start", `download_async` chạy ngầm.
2. Chạy `extract_info`.
3. Kẻ nhánh ngã ba:
   - `if info.get('_type') == 'playlist':` -> Tạo thư mục trùng tên Playlist. Cấu hình `ydl_opts['outtmpl']` cho Playlist.
   - `else:` -> Xử lý như Single Video cũ.
4. Truyền thông tin `is_playlist` và tổng số video vào một callback phụ (nếu cần) hoặc xử lý trực tiếp qua `progress_hook`.
5. Kết thúc: Báo GUI.

## 4. IMPLEMENTATION

Sẽ được thực hiện bởi `backend-specialist` và `frontend-specialist` sau khi có sự đồng ý của User.
