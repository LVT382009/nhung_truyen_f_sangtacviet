Auto Novel Embedder (Fanqie, Jjwxc, Qimao, Ciweimao -> Sangtacviet)

Tool tự động hóa quy trình nhúng truyện từ các nguồn truyện Trung Quốc phổ biến (Fanqie, Jjwxc, Qimao, Ciweimao) sang hệ thống Sangtacviet.app sử dụng Python và Selenium.

🌟 Tính năng Chính

Đa Nguồn Truyện: Hỗ trợ quét và nhúng từ 4 nguồn lớn:

🍅 Fanqie (Cà Chua): Tự động lọc truyện mới (cập nhật <= 2 ngày).

🌿 Jjwxc (Tấn Giang): Hỗ trợ quét theo danh sách tác giả hoặc bảng xếp hạng.

🐱 Qimao (Thất Miêu): Tự động nhận diện và quét danh sách truyện.

🦔 Ciweimao (Thất Vĩ Miêu/Hedgehog Cat): Hỗ trợ quét danh sách truyện.

Tự Động Phân Trang (Auto-Pagination): Tự động chuyển sang trang tiếp theo (Page 1 -> Page 2 -> ...) cho đến khi hết truyện hoặc người dùng dừng.

Bộ Lọc Thông Minh:

Tự động bỏ qua các truyện đã nhúng (Check trùng ID).

Chỉ nhúng truyện có chương mới cập nhật gần đây (với nguồn Fanqie).

Cơ Chế Chống Treo & Chặn (Anti-Crash):

Tự động reset tab trình duyệt nếu trang web load quá lâu (> 30s).

Tự động thử lại khi gặp lỗi kết nối.

Giao Diện Menu Console: Dễ dàng lựa chọn nguồn và chế độ chạy.

Điều Khiển: Nhấn phím q để dừng tool an toàn bất cứ lúc nào.

🛠️ Yêu cầu Hệ thống

Hệ điều hành: Windows (Tool sử dụng thư viện msvcrt chỉ có trên Windows).

Python 3.x đã được cài đặt.

Trình duyệt Google Chrome (Phiên bản mới nhất).

📦 Cài đặt

Cài đặt các thư viện Python cần thiết:
Mở CMD hoặc Terminal tại thư mục chứa tool và chạy lệnh:

pip install selenium webdriver-manager

Cấu hình Tài khoản:
Mở file fanqie_to_stv_bot.py bằng trình soạn thảo (Notepad, VS Code...) và tìm đến dòng cấu hình tài khoản để điền thông tin của bạn:

# --- CẤU HÌNH TÀI KHOẢN ---

STV*USERNAME = "Tên*Đăng_Nhập_Của_Bạn"
STV_PASSWORD = "Mật_Khẩu_Của_Bạn"

Cấu hình Đường dẫn lưu lịch sử (Tùy chọn):
Mặc định tool sẽ lưu file lịch sử tại D:\nhúng truyện fanqie, qidian,qimao. Bạn có thể sửa dòng HISTORY_DIR trong code nếu muốn lưu chỗ khác.

🚀 Hướng dẫn Sử dụng

Chạy tool bằng lệnh:

python fanqie_to_stv_bot.py

Menu Chức năng:

1. Mở Sangtacviet: Mở trình duyệt để bạn đăng nhập thủ công (nếu cần) hoặc kiểm tra kết nối.

2. Chạy Auto (Nguồn Fanqie): Dán link danh sách truyện Fanqie (Ví dụ: trang tìm kiếm, trang phân loại). Tool sẽ quét trang đó và các trang tiếp theo.

3. Chạy Auto (Nguồn Jjwxc): Dán link danh sách Tấn Giang (Link có chứa page=...).

4. Chạy Auto (Nguồn Qimao): Dán link thư viện Thất Miêu.

5. Chạy Auto (Nguồn Ciweimao): Dán link danh sách Thất Vĩ Miêu.

6. Xem tổng số ID đã làm: Kiểm tra số lượng truyện đã được lưu vào file da_lam_xong.txt.

7. Thoát.

Trong quá trình chạy:

Tool sẽ tự động mở trình duyệt Chrome và thực hiện các thao tác.

Để DỪNG tool: Nhấn vào cửa sổ dòng lệnh (CMD) và bấm phím q. Tool sẽ hoàn thành nốt truyện đang làm dở và dừng lại an toàn.

📝 Lưu ý

File Lịch sử (da_lam_xong.txt): File này chứa danh sách ID các truyện đã nhúng. Đừng xóa file này nếu bạn không muốn tool nhúng lại các truyện cũ.

Tốc độ mạng: Nếu mạng chậm, tool có thể báo lỗi Timeout. Nó sẽ tự động thử lại, nhưng bạn nên đảm bảo mạng ổn định để đạt tốc độ cao nhất.
