# Nguồn gốc và giấy phép

Bộ skill `thiet-ke-web` là bản chắt lọc, viết lại bằng tiếng Việt và hợp nhất từ ba dự án mã nguồn mở. Nội dung được đọc trực tiếp từ mã nguồn gốc trên GitHub ngày 22/10/2026.

| Dự án | Tác giả | Phiên bản đã đọc | Giấy phép |
|---|---|---|---|
| [taste-skill](https://github.com/Leonxlnx/taste-skill) | Leonxlnx | commit `6010f91` (20/10/2026), tasteskill v2 | MIT |
| [skills](https://github.com/emilkowalski/skills) | Emil Kowalski | commit `2d22863` (11/10/2026) | MIT |
| [impeccable](https://github.com/pbakaus/impeccable) | Paul Bakaus | commit `4281ac2` (21/10/2026), v4.7.0 | Apache 2.0 |

Nguyên văn giấy phép nằm trong thư mục `giay-phep/`.

## Phần nào lấy từ đâu

**Sao chép nguyên văn (dữ liệu và code):**
- `thu-vien/*.json`: dữ liệu thư viện của taste-skill (hướng thiết kế, hero, section, bảng màu, bộ font, hiệu ứng chủ đạo). Đã bỏ các trường `seenIn` và `links`, bỏ bộ font Newsreader (thuộc danh sách font cần tránh của Impeccable), và sửa các tham chiếu tới công cụ của bộ gốc. Nội dung mô tả giữ nguyên tiếng Anh.
- Các khối code trong `tai-lieu/07-cong-thuc-chuyen-dong.md` phần B: từ `references/motion.md` của taste-skill. Đã sửa CSS mặt nạ chữ để không cắt dấu tiếng Việt.

**Viết lại bằng tiếng Việt, có điều chỉnh:**
- Quy trình trang quảng bá, luật nhà, chấm điểm và mức trần, dấu hiệu AI, hình ảnh, chữ viết, bố cục, màu: chủ yếu từ taste-skill.
- Bốn chế độ bề mặt, chiến lược màu, font cần tránh, luật màn hình sản phẩm, kiểm tra kỹ thuật, đánh bóng, làm chắc, thang Nielsen: từ Impeccable.
- Khung quyết định chuyển động, easing, thời lượng, quy tắc vật lý, hiệu năng animation, trải nghiệm di động, dữ liệu xấu, công thức giao diện ở phần A của file 07: từ bộ skill của Emil Kowalski.

**Mới, không có trong bộ gốc:**
- Mọi phần về tiếng Việt (font có dấu, leading, mặt nạ, dữ liệu xấu cho tên Việt, câu sáo tiếng Việt, định dạng số và ngày).
- Bảng phân xử những chỗ ba bộ mâu thuẫn nhau.
- Bốn script trong `scripts/` (viết mới hoàn toàn; `rut-huong.mjs` theo thuật toán rút hướng của `draw.mjs` trong taste-skill; `chup-man-hinh.mjs` điều khiển Chrome qua giao thức DevTools theo cách tương tự trình kiểm tra của taste-skill).
- Code cho các hiệu ứng mà bộ gốc chỉ mô tả bằng lời (phần C của file 07).

## Những gì cố ý bỏ ra

- Engine nhị phân, hook tự động, trình duyệt sống và subagent của Impeccable.
- Script tìm ảnh qua mạng, trình kiểm tra trong Chrome, cảnh cuộn dùng GSAP và bộ ảnh mẫu của taste-skill.
- Các skill về Swift, React Native/Expo và Sonner của Emil (ngoài phạm vi thiết kế web).

Bộ skill này không liên kết với, không được bảo trợ bởi các tác giả trên.
