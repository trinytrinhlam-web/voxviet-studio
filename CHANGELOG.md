# Nhật ký thay đổi — VoxViet Studio

Mỗi phiên bản một mục `## <phiên bản> — <ngày>`, mỗi thay đổi một dòng `- …`.
Trang **Cập nhật** trong phần mềm đọc file này để cho bạn biết bản mới có gì.

## 0.7.0 — 2026-11-02
- Trình cài đặt .exe: cài vào E:\VoxViet Studio, biểu tượng trên Desktop và menu Start, tự chuyển kho giọng + mô hình từ bản cũ
- Mở như phần mềm thường: không còn cửa sổ dòng lệnh, chỉ một phiên, đóng cửa sổ là tắt hẳn
- Màn hình chào lần đầu: tải lõi giọng có báo dung lượng ngay trong cửa sổ, tải xong tự mở lại
- Bỏ gradio và pillow khỏi bản cài (không dùng tới, nhiều lỗ hổng đã công bố)
- Biểu tượng VoxViet cho phần mềm

## 0.6.2 — 2026-11-02
- Sửa lỗi quét virus 0x80508023 trong kiem_tra_bao_mat.bat; thêm cách quét dự phòng bằng PowerShell

## 0.6.1 — 2026-11-02
- Bảo mật: chặn trang web lạ điều khiển phần mềm (DNS rebinding), thêm khoá phiên cho cửa sổ phần mềm
- Bảo mật: chặn chèn mã và đọc/xoá file qua dữ liệu kho giọng đồng bộ từ máy khác
- Bảo mật: kiểm tra mã câu ở Phòng thu, giới hạn dung lượng tải lên 200 MB, chính sách bảo mật nội dung (CSP)
- Không ghi tên máy tính vào lịch sử GitHub khi đồng bộ; cửa sổ phần mềm không tự kết nối ra ngoài
- Ghim phiên bản thư viện đã kiểm tra; bộ fine-tune ghim đúng bản đã rà soát
- Thêm kiem_tra_bao_mat.bat: tự quét mã mô hình, file trọng số, thư viện lõi và quét virus
- Báo cáo rà soát bảo mật: BAO-CAO-BAO-MAT.md

## 0.6.0 — 2026-11-02
- Thêm trang Cập nhật: kiểm tra, xem có gì mới, cập nhật bằng một nút ngay trong phần mềm
- Tự kiểm tra bản mới mỗi ngày và hiện dấu báo ở thanh bên
- Bản vá lỗi khi chạy thử sẽ tự quay lại phiên bản cũ; có nút "Quay lại phiên bản trước"
- Tự cài thêm thư viện khi bản vá cần
- Đồng bộ kho giọng, bản thu, từ điển với GitHub ngay trong phần mềm (thay cho sync_github.bat)

## 0.5.0 — 2026-11-02
- Ảnh đại diện 3D cho các giọng; chọn nhân vật đại diện cho giọng của bạn

## 0.4.1 — 2026-11-02
- Ảnh đại diện theo giới tính, icon giới tính và nhãn phong cách đọc có icon

## 0.4.0 — 2026-11-02
- Đổi thương hiệu toàn bộ: lõi giọng VoxViet, 25 giọng có sẵn mang tên địa danh
- Giao diện mới "phòng thu tối", mở trong cửa sổ riêng, băng câu bấm để nghe từng câu
- Thu âm ngay trong Kho giọng và Phòng thu

## 0.3.0 — 2026-11-02
- Giảm vang và khử nhiễu AI; mức Trong giảm đục mạnh hơn

## 0.2.0 — 2026-11-02
- Làm trong giọng (hậu kỳ), nghe lại bản vừa đọc ở các mức khác nhau

## 0.1.0 — 2026-11-02
- Phiên bản đầu tiên
