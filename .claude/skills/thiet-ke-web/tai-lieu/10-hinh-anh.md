# Hình ảnh

Theo taste-skill (nghiên cứu ảnh trên các trang đoạt giải) và Impeccable ("chứng minh, đừng tuyên bố"). Bộ gốc có script tự tìm ảnh qua mạng; bộ này không có, nên việc tìm ảnh làm bằng tay hoặc bằng công cụ web mà Claude Code đang có, **luôn hỏi người dùng trước khi tải bất kỳ file nào về**.

## 1. Quyết định ảnh nào có thật

Trước khi lên kế hoạch, xác định chính xác dự án có gì:
- Ảnh chụp của chính dự án (nơi chốn, con người, sản phẩm, quy trình).
- Ảnh chụp màn hình phần mềm thật.
- Một công cụ tạo ảnh có thể gọi.
- Video thật.
- Hoặc không có gì.

Đừng lên kế hoạch dựa trên ảnh mình không có. "Không có gì của riêng mình" hiếm khi là không có gì: thành phố, con phố, chất liệu và lịch sử của chủ thể đều nằm trong kho ảnh mở, dùng miễn phí khi ghi nguồn.

## 2. Thứ tự ưu tiên

1. **Ảnh của chính dự án.**
2. **Ảnh tạo bằng công cụ,** nếu có công cụ tạo ảnh.
3. **Ảnh thật về thế giới của chủ thể từ kho ảnh mở** (mục 3), bất cứ khi nào có một ảnh trung thực.
4. **Hình tự vẽ bằng code từ chính chủ thể,** cho thứ không có ảnh trung thực nào (mục 6).
5. **Chỉ chữ và màu** (mục 7).

Không bao giờ: ảnh stock người cười trước laptop, ảnh giả làm sản phẩm của khách, ô xám, "Ảnh ở đây".

**Một ảnh tìm được cho thấy thế giới quanh khách hàng, không bao giờ được trình bày như sản phẩm, căn phòng, món ăn, con người hay đội ngũ của khách.**

## 3. Kho ảnh mở

| Kho | Có gì |
|---|---|
| **Wikimedia Commons** (commons.wikimedia.org) | Ảnh tư liệu, bản đồ cũ, bản quét tranh in và sách, địa điểm như hiện nay |
| **Openverse** (openverse.org) | Một chỉ mục chung cho Flickr, Wikimedia, bảo tàng và thư viện |
| **The Metropolitan Museum of Art** (metmuseum.org, Open Access) | Tranh, bản in, ảnh, vải, đồ vật thuộc phạm vi công cộng, bản quét lớn |
| **Art Institute of Chicago** (artic.edu, Public Domain) | Như trên |

**Giấy phép dùng được cho mục đích thương mại:** CC0 và phạm vi công cộng (không cần ghi nguồn, nhưng nên ghi), CC BY (bắt buộc ghi tác giả), CC BY-SA (ghi tác giả, và bản chỉnh sửa phải cùng giấy phép). **Không dùng** NC (phi thương mại) hay ND (không phái sinh) cho trang của doanh nghiệp. Luôn kiểm tra giấy phép trên trang nguồn, không đoán.

**Tìm gì: tìm theo danh sách kiểm kê, không theo ngành.** "Quán cà phê" tìm ra quán của người khác. Thế giới của chủ thể thì cụ thể:
- **Nơi chốn:** thành phố, con phố, bến cảng, thung lũng trong bưu thiếp và ảnh cũ ("Dalat 1930 postcard", "Hội An old town 1960") và như hiện nay.
- **Bản đồ cũ** của khu phố, tuyến đường.
- **Chất liệu cận cảnh:** gỗ thông, đá ong, gốm Bát Tràng, lá chuối.
- **Nghề của nó trong tranh khắc, ảnh tư liệu:** thợ rang, người hái chè, thợ mộc.
- **Hiện vật bảo tàng cùng loại:** một chiếc ấm, một tấm vải, một bản thực vật học, một bản đồ sao.

Từ khóa tiếng Anh thường cho nhiều kết quả hơn ở các kho quốc tế; thử cả tiếng Việt cho ảnh về Việt Nam trên Wikimedia.

**Quy trình:** tìm, xem kỹ từng ảnh trước khi chọn, ghi lại tiêu đề, tác giả, giấy phép, trang nguồn; **hỏi người dùng trước khi tải**, kèm tên file, nguồn và dung lượng; tải vào thư mục ảnh của dự án (không hotlink); ghi nguồn trên trang.

**Ghi nguồn:** một dòng nhỏ ở chân trang hoặc trang "Nguồn ảnh": "Ảnh: [tiêu đề], [tác giả], [giấy phép], qua [kho]". Không bao giờ viết câu trên trang về chuyện ảnh không phải của khách ("ảnh này không phải quán chúng tôi"): chú thích nói ảnh là gì, dòng nguồn nằm nhỏ ở chân trang.

## 4. Bao nhiêu ảnh, đặt ở đâu (Quảng bá)

1. **Khoảng một phần ba trang là ảnh.** Trên toàn bộ các màn hình cuộn, ảnh chiếm 30–40% diện tích, và ít nhất một màn hình trên bốn không có ảnh.
2. **Ảnh dẫn màn hình của nó, hoặc giữ nhỏ.** Ảnh dẫn chiếm ít nhất 60% màn hình; ảnh điểm xuyết dưới 10%. Tránh màn hình này nối màn hình kia toàn ảnh chiếm 20–40%.
3. **Ba đến năm kiểu đặt ảnh mỗi trang,** hai section kề nhau không cùng kiểu.
4. **Sáu đến mười hai ảnh, không bao giờ dưới bốn.** Hình SVG tự vẽ không tính vào con số này.
5. **Hai tỉ lệ cho ít nhất 75% số ảnh,** tỉ lệ thứ ba chỉ cho một ngoại lệ có chủ đích. Mặc định 4:5 cho ảnh dọc, 16:9 hoặc 3:2 cho ảnh ngang.
6. **Góc vuông cho mọi ảnh** (94% trang nghiên cứu). Nếu hướng thiết kế bo góc, một bán kính 4px cho tất cả.
7. **Ảnh chia đôi** chiếm 42–50% chiều rộng, hoặc hai phần ba, cao bằng section và chạm mép màn hình ở cạnh ngoài; trên điện thoại ảnh đi trước, toàn chiều rộng.
8. **Dải tràn viền** rộng 100%, cao 100–150vh, một dải mỗi ba, bốn màn hình; chữ chỉ ở một góc, cách mép ít nhất 32px. Trên điện thoại cắt lại thành ảnh dọc toàn màn hình.
9. **Thư viện ngang** hiện ba thẻ và một thẻ thứ tư bị cắt.
10. **Một ảnh lớn thắng sáu ảnh nhỏ.** Trên các trang điểm cao, ảnh hero phủ ít nhất nửa màn hình đầu 68% số lần.

Có video thật hoặc ảnh thật về quy trình, sản phẩm của dự án: màn hình đầu cho thấy nó, lớn (khoảng 40% màn hình trở lên). Thêm một hình ảnh chuyển động ở chỗ có video trung thực: vòng lặp tắt tiếng, có ảnh poster (`<video autoplay muted loop playsinline poster="...">`), dừng khi ra khỏi màn hình.

## 5. Cắt, đặt và xử lý

- **Cắt có chủ đích:** `object-fit: cover` với `object-position` chọn riêng cho từng ảnh để chủ thể nằm đúng chỗ bố cục cần.
- **Để ảnh chạm mép.** Tràn viền, hoặc tràn một bên, trông như được thiết kế. Ảnh trôi giữa với lề đều bốn phía trông như đặt mặc định.
- **Chồng lấn ít và có chủ đích:** dòng cuối tiêu đề chạy đè lên mép trên ảnh, hoặc ảnh nhỏ đè ảnh lớn một khoảng cố định 40–80px. Tối đa một chỗ chồng mỗi màn hình. **Không gì đè lên tiêu đề hay câu tuyên ngôn.**
- **Không khung:** không viền, không bóng, không khung thiết bị, không khung trình duyệt quanh ảnh.
- **Chú thích** một dòng ngắn cỡ nhỏ, mực nhạt, dưới ảnh, canh trái theo mép ảnh. Đa số ảnh không cần.
- **Một cách xử lý cho cả trang:**
  - Để nguyên (mặc định); chọn ảnh có ánh sáng vốn đã hợp nhau.
  - Đen trắng: `filter: grayscale(1) contrast(1.05)`, cho mọi ảnh hoặc không ảnh nào. Thống nhất ngay một bộ ảnh lẫn lộn.
  - Nhân trên nền màu: `mix-blend-mode: multiply` trên nền sáng phẳng làm nền trắng của ảnh sản phẩm biến mất.
  - Làm tối cho trang tối: `filter: brightness(0.85) contrast(1.05)`.
- **Không phải cách xử lý:** phủ màu lên ảnh, duotone phủ, làm mờ, phủ hạt, vignette, khung polaroid nghiêng có bóng.

**Chữ trên ảnh:** chỉ chữ hiển thị, một dòng ngắn và một nút, đặt trên phần yên của ảnh (bầu trời, bức tường tối, phía bóng), cập vào một góc hoặc một cạnh. Thân bài, chú thích, nhãn đặt bên cạnh hoặc bên dưới. Đo tương phản tại đúng vị trí chữ (4.5:1, hoặc 3:1 từ 24px). Không đạt thì: dời chữ sang chỗ yên hơn, đặt lên một thẻ đặc màu nền, hoặc phủ một lớp trung tính chỉ dưới vùng chữ (khối đen 40–55%, hoặc mờ dần từ 55% đen về trong suốt ở một phần ba dưới). Không bao giờ phủ màu. Thanh điều hướng cố định chạy qua ảnh thì có dải nền đặc, hoặc ẩn khi cuộn xuống.

Kỹ thuật: luôn có `width`, `height`, `alt`; `loading="lazy"` trừ ảnh hero; ảnh hero có `fetchpriority="high"` và màu nền lấy từ chính ảnh; định dạng AVIF/WebP với `srcset`.

## 6. Cho thấy phần mềm

- Dựng một **mảnh giao diện thật** bằng HTML ở kích thước thật, nội dung đáng tin, thay vì ảnh chụp thu nhỏ hay mock-up trang trí. Cắt đến phần làm rõ ý: một điều khiển, một hàng, một panel.
- Đáng tin nghĩa là: nhãn thật, số thật cộng lại khớp, một mục đang hover hoặc đang chọn, căn lề chuẩn. Thanh xám thay chữ tệ hơn không có ảnh.
- Đặt mảnh trực tiếp trên trang hoặc trên một màu sân khấu phẳng. Không laptop, không khung điện thoại (trừ khi là app điện thoại và khung là hình chữ nhật bo góc đơn giản).
- Bên trong mảnh, quy ước giao diện của sản phẩm được áp dụng (bo góc nhỏ, viền 1px của điều khiển, bóng trên menu đang mở). Gắn `data-ui` vào gốc mảnh và viết CSS của nó dưới `[data-ui]`. `data-ui` chỉ cho mảnh đã cắt, không bọc cả tiêu đề hay section.
- Người dùng cung cấp ảnh chụp màn hình thật thì cho thấy lớn và không cắt ít nhất một lần.

## 7. Vẽ chủ thể

Khi không có gì thật để chụp và kho mở không có ảnh trung thực, vẽ nó, và vẽ cho tốt. SVG nội tuyến và CSS là đủ. Hình vẽ và ảnh tìm được có thể chung một trang: ảnh tìm được cho thấy thế giới quanh khách hàng, hình vẽ cho thấy đồ vật của chính khách hàng.

- **Vẽ đồ vật của chủ thể,** không phải đồ trang trí: ba chân ghế và vân gỗ mặt ghế, tấm biển men trên cửa tiệm bánh, hai cửa sổ và ống khói của căn nhà gỗ, sơ đồ con phố, tờ hóa đơn mà công cụ tạo ra. Không gọi tên được hình vẽ đó là gì trong thế giới của chủ thể thì nó là đồ trang trí.
- **Một ngôn ngữ đồ họa cho cả trang:** hình đặc phẳng, không viền hoặc một độ dày nét nhất quán, cùng bộ góc và đường cong, tô bằng màu thật của bảng màu ở độ bão hòa đầy đủ (không phải xám).
- **Màu là chất liệu.** Sản phẩm bán bằng lớp hoàn thiện thì vẽ bằng màu lớp hoàn thiện đó.
- **Ba mức chi tiết.** Giám khảo luôn gọi hình vẽ đơn giản là "sơ sài". Mỗi hình có khối lớn đọc được ngay, khối vừa mô tả đồ vật (tay cầm, khung cửa, bậc thềm), và chi tiết nhỏ thưởng cho cái nhìn thứ hai (dấu của người làm, số nhà, viên gạch mẻ, bản lề, con chim trên mái). Tạo sáng tối bằng các bậc tông phẳng, không gradient. Hình vẽ trông như icon giữ chỗ khi phóng to là chưa xong.
- **Vẽ lớn và cho nó làm việc:** là phần tử chủ đạo của hero, một dải toàn chiều rộng, một bộ ô, dấu ở chân trang. Hình vẽ nhỏ rải rác trông như đồ độn.

## 8. Chỉ chữ và màu

Câu trả lời trung thực khi chủ thể không có gì đáng chụp và cũng không có ảnh thế giới nào hợp: hướng `type-only-statement`, hoặc `colour-chapters`. Đặt những gì cần nói tốt nhất có thể: chữ thật lớn, một màu cam kết, khoảng trống có chủ đích. Vẫn cố đưa vào vài ảnh thật ở phần sau, lớn và ít.

## 9. Báo cáo

Liệt kê mọi ảnh và video tìm được: tiêu đề, tác giả, giấy phép, trang nguồn, chỗ ghi nguồn trên trang. Liệt kê những hình vẽ đang đứng thay cho ảnh chụp, để có thể thay khi khách có ảnh thật.
