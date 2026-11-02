# Dấu hiệu "AI làm"

Một dấu hiệu là một thiết bị khiến trang bị đọc như do máy tạo ra. Bản thân chúng không xấu; đa số bắt đầu là ý hay trên trang hay. Chúng thành dấu hiệu vì được sinh ra theo mặc định, ở khắp nơi, không lý do. Vì vậy danh sách này có ghi thời điểm, và **không bao giờ nêu tên font, màu hay component thay thế**: mọi danh sách "dùng cái này thay" từng được công bố đều trở thành làn sóng dấu hiệu tiếp theo trong vài tháng. Thứ thay thế ở đây là **quy trình** (rút từ thư viện, lấy từ chủ thể), không phải sản phẩm.

Cột "Script" cho biết `soat-loi.mjs` có bắt được không (mã luật trong ngoặc).

## 1. Đợt một (2023–2024)

| Dấu hiệu | Script | Làm thay |
|---|---|---|
| Gradient tím, indigo ở hero, nút, ánh sáng | có (`gradient`, `ai-palette`) | Bảng màu được rút; màu phẳng |
| Chữ tiêu đề tô gradient | có (`gradient-text`) | Mực đặc |
| Panel kính: backdrop blur, thẻ trong suốt | có (`glass`) | Bề mặt đục, một bậc tông so với nền |
| Nút "Bắt đầu" phát sáng hay gradient | có (`gradient`) | Nút phẳng gọi tên hành động |
| Bóng xám nhạt dưới mọi thẻ | có (`shadow-rest`) | Bậc tông, hoặc không có hộp |
| Ba thẻ tính năng giống hệt, mỗi thẻ icon trong ô vuông bo góc | không | Bản thiết kế section được rút |
| Emoji làm icon hay gạch đầu dòng | có (`emoji`) | Chữ, hoặc ảnh thật |
| Tiêu đề căn giữa, câu phụ, hai nút, ảnh màn hình bên dưới | không | Hero được rút |
| Cùng một font trên mọi trang | có (`default-font`) | Hệ chữ được rút |

## 2. Đợt hai (2025)

| Dấu hiệu | Script | Làm thay |
|---|---|---|
| Eyebrow: nhãn nhỏ viết hoa giãn chữ trên mọi tiêu đề | có với Tailwind (`eyebrow-tw`) | Gộp vào tiêu đề, hoặc xóa |
| Badge viên thuốc trên tiêu đề hero ("Mới", "Beta", "Giới thiệu") | không | Nói trong câu phụ |
| Một từ của tiêu đề nghiêng serif, khác màu hay gạch chân | không | Một font, một màu |
| Lưới bento ô bo tròn làm section tính năng | không | Section có bố cục; ô chỉ trong hướng `dense-tiles`, đầy nội dung, kích thước nghiêm ngặt |
| Nền gần đen với một màu neon và ánh phát sáng | một phần (`shadow-rest`, `gradient`) | Bảng màu tối được rút, không phát sáng |
| Thanh điều hướng viên thuốc nổi có blur | có (`pill-nav`, `glass`) | Một thanh phẳng |
| Hero là dashboard giả bằng thanh xám và biểu đồ tròn | không | Mảnh giao diện thật, hoặc không có ảnh |
| Chấm trạng thái trang trí ("Đang nhận dự án", chấm "live" nhấp nháy) | một phần (`bounce`) | Xóa |
| Mờ dần trồi lên ở mọi section | không | Một hiệu ứng chủ đạo; xuất hiện theo từng phần, đổi cách theo nội dung |

## 3. Đợt ba (2025–2026): "cách sửa" trở thành vẻ ngoài

Lời khuyên được công bố cho hai đợt đầu là "làm ấm lên và làm cho có chất tạp chí". Mô hình áp dụng nguyên xi, và giờ đó là vẻ ngoài AI dễ nhận ra nhất.

| Dấu hiệu | Script | Làm thay |
|---|---|---|
| Nền kem vàng + nhấn đất nung, gỉ sét, đất sét | có (`ai-palette`) | Bảng màu được rút. Ấm từ một tông đá ít bão hòa, một màu mực sâu, một bức ảnh, hoặc một vùng màu ấm đầy đủ |
| Serif tương phản cao hay serif mềm làm lối tắt đến "cao cấp" | một phần (`training-font`) | Hệ chữ được rút, dù là loại gì |
| Tiêu đề serif nghiêng cỡ lớn | không | Như được rút |
| Nhại báo giấy: đường kẻ mảnh khắp nơi, không bo góc, cột dày đặc | có (`hairline`) | Cấu trúc từ khoảng trống và bậc tông |
| Nhãn trình diễn: "Ghi chép thực địa", "Được tin dùng một cách lặng lẽ", "Trên bàn làm việc của chúng tôi" | không | Tên section giản dị |

## 4. Mốt của phòng tranh, bị cấm làm phong cách nhà

Đang phổ biến trên các trang đoạt giải. Trong nghiên cứu, chúng xuất hiện ở trang điểm cao **nhiều hơn** trang yếu (nhãn monospace 44% so với 24%, đánh số 38% so với 21%, đường kẻ mảnh 61% so với 52%). Ở đây chúng vẫn bị cấm, theo quyết định của chủ bộ gốc: chúng là thứ đầu tiên máy sao chép từ phòng tranh, không mang thông tin, và một trang không có chúng phải tự tìm cấu trúc thật.

| Dấu hiệu | Script | Làm thay |
|---|---|---|
| Nhãn monospace nhỏ, mono làm giọng "kỹ thuật", chú thích mono | có (`mono`) | Font thân bài; số dạng bảng cho dữ liệu |
| Đánh số: 01 / 02 / 03, (001), "Bước 02", số đánh dấu section | có (`numbering`) | Thứ tự bằng vị trí, cỡ, hoặc chữ; `<ol>` khi thật sự là danh sách |
| Đường kẻ mảnh: đường chia, lưới kẻ, hộp viền 1px | có (`hairline`) | Khoảng trống, bậc tông, hình đặc, một thanh dày nếu thanh là ý tưởng |
| Đồ nghề công cụ thiết kế làm trang trí: dấu thập, dấu cắt, tay cầm chọn, đường gióng nét đứt, thước | một phần | Xóa |
| Siêu dữ liệu kiểu agency: giờ địa phương, tọa độ, thời tiết, số phiên bản, "©2026 · Cuộn", chuỗi chấm giữa | không | Xóa |
| Chữ hoa nhỏ giãn chữ rải quanh màn hình | có với Tailwind (`eyebrow-tw`) | Viết thường đầu câu ở cỡ đọc được, đặt cạnh nội dung nó mô tả |

Chữ hoa nhỏ giãn chữ là mục duy nhất trong nhóm mà dữ liệu cũng lên án: 16% trang điểm cao so với 57% trang yếu.

## 5. Dấu hiệu cấu trúc

| Dấu hiệu | Script | Làm thay |
|---|---|---|
| Tiêu đề là cả một câu ở cỡ hiển thị, ba bốn dòng | không (nhìn ảnh chụp) | Tiêu đề khoảng năm từ; phần còn lại xuống dưới |
| Thứ tự section rập khuôn: hero, logo, tính năng, cảm nhận, bảng giá, CTA | không | Thứ tự của lập luận (`09-chu-viet.md`) |
| Mọi section cùng một họ bố cục | không | Bố cục khác nhau mỗi section, từ phiếu |
| Mọi thứ căn giữa | không | Neo trái, một khoảnh khắc căn giữa |
| Một bo góc vừa (12–16px) cho mọi thứ | không | Vuông hoặc tròn hẳn, chọn một lần |
| Chín cỡ chữ gần bằng nhau | không | Năm cỡ, cách xa nhau |
| Bằng chứng bịa: logo, trích dẫn, hàng sao, "10.000+ đội ngũ" | không | Bằng chứng thật, hoặc không có |
| Chữ hay hộp CSS ở chỗ lẽ ra là ảnh | không | Ảnh thật, hoặc thiết kế không cần ảnh |
| Viền màu dày một bên trên thẻ, callout | có (`side-stripe`) | Bỏ; nền tông khác nếu cần |
| Bóng lệch cứng không blur ngoài thế giới neobrutalist | có (`hard-shadow`) | Bậc tông |

## 6. Dấu hiệu chữ viết

Bắt bởi `copy-vi`, `copy-en`, `lorem`. Chi tiết trong `09-chu-viet.md` mục 6: động từ và tính từ của thể loại (đột phá, nâng tầm, liền mạch, giải pháp toàn diện; unlock, seamless, elevate); câu sửa sai ("không chỉ là X mà còn là Y"); tiêu đề bộ ba; nút "Tìm hiểu thêm", "Bắt đầu ngay"; quá nhiều gạch ngang dài; lorem ipsum.

## 7. Dấu hiệu chuyển động

Cùng một hiệu ứng mờ trồi cho mọi khối; một tá hiệu ứng so le trong hero; mọi thẻ nổi lên khi hover; easing nảy (`overshoot`, `bounce`); vòng lặp vô nghĩa; hiệu ứng lộ diện không chạy để lại dải trống; preloader; con trỏ tùy chỉnh; chữ xáo trộn kiểu giải mã. Xem `06-chuyen-dong.md` mục 6.

## 8. Dấu hiệu riêng cho trang tiếng Việt

| Dấu hiệu | Script | Làm thay |
|---|---|---|
| Chữ có dấu lệch kiểu vì font thiếu tiếng Việt | một phần (`vi-fontshare`) | Font có subset tiếng Việt (`03-chu.md`) |
| Dấu bị cắt trong tiêu đề leading chặt hay hiệu ứng mặt nạ | một phần (`vi-leading`) | Leading 1.05–1.15, padding hai phía cho mặt nạ |
| `<html lang="en">` trên trang tiếng Việt | có (`vi-lang`) | `lang="vi"` |
| Văn phong dịch máy từ tiếng Anh ("Hãy bắt đầu hành trình của bạn", "Mở khóa tiềm năng") | một phần (`copy-vi`) | Viết như người Việt nói với nhau, cụ thể |
| Định dạng số, ngày kiểu Mỹ (1,250,000; 10/22/2026) | không | `Intl.NumberFormat('vi-VN')`, ngày/tháng/năm |

## 9. Vì sao gỡ bỏ thôi là chưa đủ

Một trang gỡ hết dấu hiệu mà không đặt gì vào chỗ đó là một trang trống có phép lịch sự, và đó cũng là một dấu hiệu ("thẩm mỹ né tránh": ai cũng đoán được nó từ tên ngành cộng danh sách điều cần tránh). Các dấu hiệu từng lấp chỗ mà lẽ ra ý tưởng phải đứng. Thứ tự làm trong `01-quy-trinh-trang-quang-ba.md` tồn tại để lấp chỗ đó bằng thực chất: chữ lớn hơn, vùng màu đầy đủ, ảnh thật của thế giới chủ thể, và nội dung đầy đủ.
