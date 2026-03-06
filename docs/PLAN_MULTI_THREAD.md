# PLAN: Multi-Threaded Download Manager & Notification System

## 1. ANALYSIS

Hiện tại, GUI được thiết kế để chỉ tải 1 video tại 1 thời điểm. Nút "Start Download" và ô nhập URL bị khoá trong suốt quá trình tải, cùng với việc dùng 1 thanh Progress Bar duy nhất ở cuối màn hình. Ngoài ra, việc dùng hộp thoại (Messagebox) bật lên sau khi tải xong gây cản trở thao tác của người dùng.

Yêu cầu mới:

1. Biến ứng dụng thành **Multi-threaded Download Manager**: Cho phép dán nhiều link và tải song song cùng lúc.
2. Xóa bỏ hoàn toàn hộp thoại `messagebox` khi hoàn thành.
3. Chuyển sang dùng các cảnh báo tích hợp trong giao diện (In-app Notification) hoặc thông báo hệ thống (System Notification - OS level).

## 2. PLANNING (Task Breakdown)

### 2.1 Cập nhật Kiến trúc Giao diện (GUI Layer - `gui/app.py`)

- **Tạo "Active Downloads" Board**:
  - Thay thế thanh Progress Bar đơn lẻ bên dưới nút "Start".
  - Chèn vào đó một `CTkScrollableFrame` đóng vai trò là danh sách các tệp đang tải.
- **Tiến trình tải độc lập (Download Item Widget)**:
  - Khi người dùng bấm "Start Download", ứng dụng KHÔNG khoá nút bấm, thay vào đó:
    - Tạo ra 1 thẻ (Frame) mới gắn vào bảng "Active Downloads". Thẻ này bao gồm: Tên Video, Progress Bar, Tốc độ, Nút Pause/Cancel (nếu có thể).
    - Reset lại trắng ô URL, Video Title để sẵn sàng đón nhận link tiếp theo.
- **Loại bỏ Messagebox**:
  - Khi hoàn thành, thẻ tải xuống đó sẽ hiển thị `✅ 100% - Finished` rồi tự động chuyển lịch sử sang cột "Download History" bên trái.
  - Tích hợp thư viện thông báo Desktop OS.

### 2.2 Nâng cấp Core (`core/downloader.py` & `gui/app.py` logic)

- Instantiation độc lập: Mỗi lần gọi `_start_download`, ta sinh ra một instance `M3U8Downloader` mới (app hiện đã làm việc này).
- Custom Hook ID: Cần truyền 1 ID hoặc object (ví dụ `download_id`) vào trong callback `progress_hook` để ứng dụng biết tín hiệu % đang báo về thuộc về cái thẻ video nào trên màn hình.
- Thêm thư viện `plyer` vào `requirements.txt` để hỗ trợ hiển thị Notification đẩy thẳng ra hệ thống Windows/Mac/Linux (VD: Bảng thông báo nhỏ hiện ở góc phải dưới màn hình).

## 3. SOLUTIONING

**Sơ đồ luồng Giao diện mới:**

- Người dùng paste link -> Bấm Start
- App lấy `url` và `title` -> Tạo 1 biến định danh UUID.
- Dựng 1 khung `DownloadTaskFrame(UUID)` thêm vào `ActiveDownloadsScrollable`.
- Gọi `M3U8Downloader.download_async(...)` truyền vào hook mới kẹp theo `UUID`.
- Trong `_progress_hook_manager(d, uuid)`: Cập nhật chỉ số lên đúng thanh Progress Bar của thẻ `UUID` đó.
- Hoàn Thành: Chuyển item đó từ `Active Downloads` sang `Download History`, gửi Desktop Notification qua `plyer.notification.notify(...)`.

## 4. IMPLEMENTATION

Phase 2 sẽ được thực hiện khi có sự chấp thuận của người dùng. Tóm tắt cài đặt:

- `pip install plyer` để dùng thông báo hệ điều hành OS.
- Xoá `messagebox.showinfo` trong `gui/app.py`.
- Tạo Component `DownloadItemWidget` lồng trong CustomTkinter.
