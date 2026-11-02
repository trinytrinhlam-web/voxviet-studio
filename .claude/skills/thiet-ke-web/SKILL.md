---
name: thiet-ke-web
description: Bộ skill thiết kế website riêng, tự chứa, tổng hợp từ ba nguồn - Emil Kowalski (chuyển động, độ mượt giao diện), Paul Bakaus/Impeccable (chữ, màu, khoảng cách, kiểm tra chất lượng) và taste-skill (ý tưởng, bố cục chống rập khuôn) - có bổ sung riêng cho tiếng Việt. Dùng skill này mỗi khi người dùng muốn thiết kế, làm mới, chỉnh sửa, review hay đánh bóng bất kỳ giao diện web nào, dù nói tiếng Việt hay tiếng Anh - thiết kế website, landing page, trang giới thiệu, trang bán hàng, portfolio, dashboard, trang admin, docs, blog, hero section, chọn font, phối màu, khoảng cách, bố cục, thêm animation, hiệu ứng chuyển động, làm web đẹp hơn, sang hơn, bớt giống AI, bớt rập khuôn, review UI, design, redesign, restyle, polish, frontend, UI, UX - kể cả khi họ chỉ nói "làm cái trang này đẹp lên".
---

# Thiết kế web

Bộ skill này chắt lọc từ ba "thầy" và hợp nhất thành một hệ luật duy nhất, đã phân xử sẵn những chỗ họ mâu thuẫn:

| Thầy | Phần đóng góp |
|---|---|
| **taste-skill** (Leonxlnx) | Ý tưởng lấy từ chủ thể, hướng nghệ thuật rút ngẫu nhiên từ thư viện 247 website đoạt giải, bố cục, hình ảnh, chữ viết. Chống kiểu "landing page trung bình". |
| **Impeccable** (Paul Bakaus) | Bốn chế độ bề mặt, hệ thống chữ, màu, khoảng cách, kiểm tra chất lượng (trợ năng, hiệu năng, responsive), độ hoàn thiện. |
| **Emil Kowalski** | Có nên chuyển động không, easing, thời lượng, độ "nghe tay" của giao diện, hiệu năng animation, thử dữ liệu xấu. |

Không cần cài gì thêm. Mọi thứ nằm trong thư mục này; các script chỉ đọc file cục bộ và cần Node.js 18 trở lên (riêng script chụp màn hình cần Node 22 trở lên và Chrome, Chromium hoặc Edge đã có trên máy).

**Luôn trả lời người dùng bằng tiếng Việt.** Tên thuộc tính CSS, mã lệnh và tên thư viện giữ nguyên tiếng Anh.

## Công cụ đi kèm

Chạy từ thư mục gốc của dự án. `<skill>` là thư mục chứa file này.

| Script | Việc nó làm |
|---|---|
| `node <skill>/scripts/rut-huong.mjs` | Rút ngẫu nhiên hướng thiết kế (ý tưởng, hero, font, bảng màu, từng section, chuyển động chủ đạo) từ thư viện. Chỉ dùng cho trang quảng bá. Xem `tai-lieu/01-quy-trinh-trang-quang-ba.md`. |
| `node <skill>/scripts/soat-loi.mjs <thư mục> --che-do <chế độ>` | Soát code tìm dấu hiệu "AI làm", lỗi chuyển động, lỗi trợ năng, lỗi tiếng Việt. Thoát mã 1 nếu còn LỖI. |
| `node <skill>/scripts/chup-man-hinh.mjs <url hoặc file> <tên>` | Giả lập đúng màn hình 1440, 768 và 390px, cuộn qua trang để kích hoạt hiệu ứng, chụp từng màn hình, cộng một bản giảm chuyển động; báo cuộn ngang, font thực sự đã tải, phần tử còn ẩn. Dùng Chrome/Edge có sẵn trên máy. Ảnh vào `.thiet-ke/anh/<tên>/`. Node cũ hơn 22: dùng `bash <skill>/scripts/chup-man-hinh.sh` (ảnh điện thoại kém chính xác, vì Chrome headless không thu hẹp dưới 500px). |

Thư mục `.thiet-ke/` trong dự án là chỗ làm việc của skill (phiếu hướng, ảnh chụp, ghi chú). Nhắc người dùng thêm nó vào `.gitignore` nếu họ không muốn commit.

## Bước 1. Xác định chế độ bề mặt

Chế độ đặt theo **bề mặt đang làm**, không theo sản phẩm. Trang landing của một phần mềm vẫn là Quảng bá; tài liệu của một hãng thời trang vẫn là Đọc.

| Chế độ | Mã cho script | Người xem thành công khi | Ví dụ |
|---|---|---|---|
| **Quảng bá** (Persuade) | `quang-ba` | quyết định và hành động | landing page, trang marketing, bảng giá, nhà hàng, sự kiện, khách sạn |
| **Trải nghiệm** (Experience) | `trai-nghiem` | đắm chìm trong tác phẩm | portfolio, gallery, showcase |
| **Thao tác** (Operate) | `thao-tac` | hoàn thành tác vụ | dashboard, admin, settings, editor, công cụ |
| **Đọc** (Read) | `doc` | hiểu nội dung | docs, blog, bài viết, hướng dẫn, changelog |

Quảng bá và Trải nghiệm được táo bạo hết mức: ý tưởng riêng, chữ cực lớn, màu phủ cả vùng. Thao tác và Đọc thể hiện tham vọng bằng **độ chính xác và sự kiềm chế**: những khuôn mẫu người dùng đã quen là ưu điểm, không phải lỗi.

Yêu cầu gồm nhiều bề mặt (landing page và dashboard phía sau) thì làm từng cái theo chế độ của nó, dùng chung một bảng màu và kiểu chữ.

## Bước 2. Đọc bối cảnh dự án

Trước khi sửa hay dựng, đọc:

- `SAN-PHAM.md` (hoặc `PRODUCT.md`) nếu có: sự thật về sản phẩm (đối tượng, mục đích, giọng văn, ràng buộc, bằng chứng thật).
- `THIET-KE.md` (hoặc `DESIGN.md`) nếu có: hệ thiết kế đã chốt (token, font, màu, thành phần).
- Code thật: stack, cách viết style (Tailwind v3/v4, CSS module, CSS thường...), token, component, tài sản thương hiệu.

Dự án chưa có `SAN-PHAM.md` và đây là bề mặt mới: hỏi người dùng hai, ba câu ảnh hưởng thật đến thiết kế (theo chế độ, xem tài liệu quy trình), rồi ghi câu trả lời vào `SAN-PHAM.md`. Không hỏi giá trị CSS. Yêu cầu mơ hồ thì tự quyết, nói rõ cách hiểu của mình trong một dòng, chỉ hỏi khi thiếu một sự thật chặn việc (ví dụ chưa có tên sản phẩm).

Phân biệt **làm tinh** và **làm lại**:
- **Làm tinh** giữ bản sắc, hành vi, nội dung và mọi thứ ngoài phạm vi. Hỏi trước khi thay câu chữ mang tính sự thật.
- **Làm lại** giữ sự thật sản phẩm, nội dung, chức năng và ràng buộc, nhưng coi giao diện cũ là bằng chứng chứ không phải khuôn mẫu.
- Một section hay component mới bên trong một trang đã có hệ thiết kế thì **thừa hưởng** hệ đó. Không biến việc nhỏ thành bài tập bản sắc mới.

## Bước 3. Chọn quy trình

| Việc | Đọc và làm theo |
|---|---|
| Trang Quảng bá hoặc Trải nghiệm mới, hoặc làm lại | `tai-lieu/01-quy-trinh-trang-quang-ba.md` (đọc trọn) |
| Màn hình Thao tác hoặc trang Đọc | `tai-lieu/02-man-hinh-ung-dung.md` (đọc trọn) |
| Chỉ làm chuyển động | `tai-lieu/06-chuyen-dong.md`, rồi `07-cong-thuc-chuyen-dong.md` |
| Animation bị giật, hoặc trang chậm | `tai-lieu/08-hieu-nang-va-di-dong.md` |
| Review, phê bình, kiểm tra chất lượng | `tai-lieu/11-danh-gia.md` |
| Thử UI với dữ liệu xấu, làm chắc trước khi ra mắt | `tai-lieu/12-du-lieu-xau.md` |
| Một component hay section nhỏ | Không rút hướng mới. Bám thiết kế xung quanh, áp dụng luật nhà bên dưới, rồi soát lỗi và chụp màn hình. |
| Chỉ sửa chữ, màu hoặc bố cục | `03-chu.md`, `04-mau.md` hoặc `05-bo-cuc.md`, giữ nguyên hệ hiện có |

## Luật nhà

Luôn áp dụng, trừ khi brief hoặc thương hiệu của người dùng nói khác.

### Thứ tự ưu tiên khi có mâu thuẫn

1. **Brief và thương hiệu của người dùng.** Họ chỉ định font, màu, phong cách nào thì làm theo, kể cả khi trái luật bên dưới; ghi chú trong báo cáo. Đừng bẻ một brief rõ ràng theo gu của mình.
2. **Trợ năng.** Tương phản WCAG AA, `prefers-reduced-motion`, focus nhìn thấy được, chữ thân bài từ 16px, vùng chạm từ 44px.
3. **Luật theo chế độ** (bảng bên dưới).
4. **Phiếu hướng thiết kế** (nếu đã rút): hướng → hệ chữ và màu → bản thiết kế hero → bản thiết kế section.

### Ba thầy đều đồng ý (mọi chế độ)

- Không "eyebrow": nhãn nhỏ viết hoa giãn chữ phía trên tiêu đề, chip "Mới ·", badge viên thuốc trên headline. Đưa thông tin vào tiêu đề hoặc bỏ.
- Không đánh số section 01 / 02 / 03, trừ khi thứ tự là thông tin người đọc cần.
- Không monospace làm "trang phục kỹ thuật"; chỉ cho code, dữ liệu, số đo.
- Không emoji hay ký tự Unicode thay bộ icon. Icon từ một thư viện thật hoặc SVG tự vẽ, cùng nét, cùng độ đậm.
- Không hàng thẻ giống hệt nhau (icon + tiêu đề + đoạn văn) làm khung trang. Không lồng thẻ trong thẻ.
- Không chữ xám nhạt trên nền màu; chữ phụ lấy sắc độ từ màu nền hoặc màu chữ chính.
- Không chữ gradient.
- Không viền màu dày một bên (trên 1px) cho thẻ, callout, cảnh báo.
- Không `ease-in` cho thứ xuất hiện. Không easing nảy theo phản xạ. Không xuất hiện từ `scale(0)`. Không `transition: all`. Không animate `width`, `height`, `top`, `left`, `margin`.
- Nội dung luôn hiện khi JavaScript lỗi; mọi chuyển động có phương án `prefers-reduced-motion`.
- Không bịa bằng chứng: không logo khách hàng, trích dẫn, đánh giá sao, "10.000+ người dùng" giả.
- Trạng thái mặc định của trình duyệt cũng phải được thiết kế: màu bôi đen chữ, vòng focus, thanh cuộn, khoảng gạch chân, số dạng bảng.
- Phải nhìn kết quả đã render ở nhiều độ rộng. Code đúng không có nghĩa là trang đẹp.

### Theo chế độ

| Chủ đề | Quảng bá / Trải nghiệm | Thao tác / Đọc |
|---|---|---|
| Ai chủ trì | taste-skill: ý tưởng, bố cục, hình ảnh | Impeccable: hệ thống, sự quen thuộc có chủ đích |
| Gradient | Cấm, trừ lớp phủ trung tính dưới chữ trên ảnh | Hạn chế; chỉ khi brief yêu cầu |
| Đổ bóng | Không cho vật đứng yên. Chỉ menu, dialog đang nổi; bóng có độ lệch và blur mềm | Được dùng khi làm rõ trạng thái hoặc thứ bậc |
| Đường kẻ mảnh, viền 1px | Cấm (trừ trong bảng, form). Tách bằng khoảng trống hoặc bậc tông nền | Được dùng khi giúp quét thông tin |
| Kính mờ | Cấm | Chỉ khi có chức năng cụ thể |
| Font | Tối đa 2, thường 1, có cá tính; rút từ thư viện | Thường 1 font làm việc tốt; font hệ thống được phép |
| Cỡ chữ | Ít cỡ, cách xa nhau (tiêu đề gấp ≥4 lần thân bài); tối đa 5 cỡ | Thang cố định theo rem, tỉ lệ 1.125–1.2 |
| Chữ hiển thị lớn | Được phép rất lớn (đến 16–24vw); tracking đến -0.06em ở cỡ tượng đài | Tối đa 6rem; tracking không chặt hơn -0.04em |
| Số lượng chuyển động | Một hiệu ứng chủ đạo + xuất hiện theo từng phần mỗi section + phản hồi mọi nút + một hình ảnh động; tổng ít nhất 8 phần tử chuyển động (trừ hướng `stillness`) | Thang tần suất của Emil thắng; không có số tối thiểu; không chuỗi mở trang |
| Thời lượng | Tương tác theo Emil (dưới 300ms); lộ diện khi cuộn 600–1000ms; mở ảnh 1100–1600ms | Tất cả dưới 300ms, trừ modal và drawer (đến 500ms) |
| Thuộc tính animate | `transform`, `opacity`; `clip-path` cho mở ảnh và hiệu ứng chủ đạo | `transform`, `opacity` |

Chi tiết từng chủ đề nằm trong `tai-lieu/03` đến `tai-lieu/10`.

### Riêng cho tiếng Việt

Ba bộ gốc không xử lý tiếng Việt. Khi nội dung có tiếng Việt:

- **Font phải có đủ dấu.** Phần lớn font Fontshare không có; kiểm tra trước khi dựng (cách kiểm tra trong `03-chu.md`). Font thiếu dấu khiến trình duyệt ghép chữ có dấu bằng font khác, nhìn lởm chởm.
- **Leading dưới 1.0 dễ cắt hoặc chồng dấu** trên chữ hoa (Ế, Ỗ, Ặ, Ữ). Với tiêu đề tiếng Việt viết hoa, thường cần 1.05–1.15.
- **Mặt nạ `overflow: hidden` cắt dấu phía trên.** Công thức trong `07-cong-thuc-chuyen-dong.md` đã sửa sẵn; tự viết thì chừa `padding-block` ở cả hai phía.
- **Không cắt phần trên của chữ** bằng mép màn hình hay mặt nạ: mất dấu là mất nghĩa ("ĐÁ" thành "ĐA").
- `<html lang="vi">`.
- Ngân sách ký tự cho tiêu đề tính theo ký tự, không theo từ: tiếng Việt nhiều từ ngắn nên năm từ tiếng Việt thường ngắn hơn năm từ tiếng Anh, nhưng chữ có dấu chồng cần thêm khoảng dòng.

## Bước 4. Kiểm tra trước khi báo xong

1. `node <skill>/scripts/soat-loi.mjs <thư mục mã nguồn> --che-do <chế độ>`: sửa mọi LỖI. Mỗi CẢNH BÁO coi là sai trừ khi bảo vệ được nó trong một câu.
2. Chạy trang (dev server hoặc file), `node <skill>/scripts/chup-man-hinh.mjs <url> vong-1`, rồi **mở từng ảnh** và phê bình theo `tai-lieu/11-danh-gia.md`. Sửa ba vấn đề lớn nhất, chụp lại, tối đa ba vòng.
3. Không có Chrome/Edge: dùng công cụ trình duyệt đang có để chụp; không có gì để chụp được thì nói rõ trong báo cáo là chưa kiểm tra bằng mắt.

Không khai báo một bước kiểm tra chưa chạy.

## Bước 5. Báo cáo cho người dùng

Ngắn gọn, bằng tiếng Việt:

- Chế độ bề mặt và quy trình đã dùng.
- Với trang Quảng bá: hướng đã rút (tên và seed), các ô đã vẽ lại kèm lý do, câu ý tưởng, "một thứ sống động" trên trang.
- Điểm phê bình vòng cuối và những gì còn chưa đạt.
- Ảnh tìm từ kho mở: tên, tác giả, giấy phép, nguồn, chỗ ghi nguồn trên trang.
- Nội dung mẫu cần thay trước khi ra mắt.
- Những luật đã cố ý không theo, và vì sao.

Khi review code giao diện, trình bày phát hiện bằng **một bảng duy nhất** ba cột **Trước | Sau | Lý do** (định dạng của Emil), xếp theo mức ảnh hưởng.

## Danh mục tài liệu

| File | Đọc khi |
|---|---|
| `tai-lieu/01-quy-trinh-trang-quang-ba.md` | Dựng hoặc làm lại trang Quảng bá / Trải nghiệm. Quy trình 10 bước. |
| `tai-lieu/02-man-hinh-ung-dung.md` | Dashboard, admin, settings, công cụ, docs, blog. |
| `tai-lieu/03-chu.md` | Chọn và dựng chữ; kiểm tra font tiếng Việt. |
| `tai-lieu/04-mau.md` | Bảng màu, vai trò màu, tương phản, chế độ tối. |
| `tai-lieu/05-bo-cuc.md` | Lưới, lề, khoảng cách, nhịp, khoảng trống, điện thoại. |
| `tai-lieu/06-chuyen-dong.md` | Mọi quyết định chuyển động: có nên không, easing, thời lượng, token. |
| `tai-lieu/07-cong-thuc-chuyen-dong.md` | Code mẫu cho từng hiệu ứng (tra theo mã trong phiếu hướng). |
| `tai-lieu/08-hieu-nang-va-di-dong.md` | Animation giật; trang chạy trên điện thoại cho "ra chất" ứng dụng. |
| `tai-lieu/09-chu-viet.md` | Viết tiêu đề, câu phụ, nút, nội dung; tránh câu sáo. |
| `tai-lieu/10-hinh-anh.md` | Chọn, tìm, ghi nguồn, cắt, xử lý ảnh; khi không có ảnh. |
| `tai-lieu/11-danh-gia.md` | Phê bình qua ảnh chụp, chấm điểm, kiểm tra kỹ thuật, đánh bóng. |
| `tai-lieu/12-du-lieu-xau.md` | Tên dài, danh sách rỗng, số lớn, lỗi mạng, dịch thuật. |
| `tai-lieu/13-dau-hieu-ai.md` | Danh sách các dấu hiệu "AI làm" theo từng đợt và thứ thay thế. |
| `thu-vien/*.json` | Dữ liệu cho `rut-huong.mjs`. Không đọc trọn; dùng script. |
| `NGUON.md` | Nguồn gốc và giấy phép. |
