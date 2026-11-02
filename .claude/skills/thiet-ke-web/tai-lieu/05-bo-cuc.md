# Bố cục và khoảng cách

Bố cục biến thứ tự ưu tiên của sản phẩm thành thứ tự đọc, nhóm, nhịp và không gian dùng được. Chẩn đoán vấn đề cấu trúc trước khi di chuyển các hộp. Tổng hợp từ Impeccable (hệ thống, kiểm tra) và taste-skill (số đo trên trang đoạt giải, khung trang).

## 1. Những gì trang mạnh làm (Quảng bá)

Từ 114 trang đoạt giải:

- **Lề hẹp, nội dung chạm mép.** Khoảng 45 trang dùng lề ngoài từ 32px trở xuống.
- **Chữ treo từ một đường lệch tâm.** Khoảng 22 trang neo chữ vào một đường cố định không phải lề trái cũng không phải giữa.
- **Hai, ba cỡ chữ, không có gì ở giữa.**
- **Mỗi màn hình một thứ:** một câu, một vật, một dự án.
- **Các section phân biệt bằng nền,** đổi cả màu nền ở mỗi section.
- **Section được bố cục lại, không lặp lại.**
- **Phá hệ thống một lần, có chủ đích:** một dòng căn giữa trên trang chia đôi.
- **Thường không có thanh điều hướng,** và phần kết là một cảnh được thiết kế chứ không phải danh sách link.
- **Ít chữ.** Trung vị 575 từ cả trang; vài trang hay nhất dưới 200.

## 2. Lưới và lề

- Một cặp lề và một lưới cho cả trang. Mọi cạnh trái là một đường cột.
- Đừng bọc trang trong `max-width: 1200px; margin: auto` theo phản xạ. Để thứ lớn chạy đến mép.
- Màn hình rất rộng: giới hạn bố cục khoảng 1760–1920px, hoặc dừng chữ cỡ `vw` khỏi tiếp tục lớn.
- Lề thường hẹp: trung vị khoảng 28px ở 1440px, nửa số trang từ 18 đến 45px. Hướng thiết kế đòi lề rộng (ảnh so le, nhạc cụ trầm lặng) sẽ ghi trong phiếu.
- Thanh điều hướng nằm trên cùng lề với nội dung. Lỗi nhỏ phổ biến nhất là thanh điều hướng lệch lề.
- **Không bao giờ vẽ lưới.** Đường cột, dấu thập, đường gióng là đồ trang trí bị cấm.
- Thang khoảng cách gốc 4 đơn vị (4, 8, 12, 16, 24, 32, 48, 64, 96, 128...). Nó cho những bậc giữa hữu ích mà thang chỉ có 8 bỏ lỡ. Đặt tên token theo vai trò, không theo giá trị.
- Dùng `gap` cho nhịp giữa các phần tử anh em khi nó diễn đạt quan hệ trực tiếp hơn margin.

## 3. Chữ đặt ở đâu

- **Chọn một đường neo và dùng lại.** Tiêu đề hero bắt đầu ở cột 5 thì tiêu đề section cũng bắt đầu ở đó hoặc ở lề.
- **Lệch tâm thắng căn giữa.** Tiêu đề ở một phần ba trái, đoạn văn ở phía phải xa.
- **Hai đầu đối diện.** Hai đoạn chữ ngắn ở hai đầu của cùng một đường chân chữ (tên bên trái, mô tả một dòng bên phải).
- **Căn giữa là một quyết định.** Khi trang mạnh căn giữa, nó dùng một trục với hai bên trống rộng bằng nhau và chỉ một thứ trên trục. Căn giữa tối đa một khoảnh khắc mỗi trang.
- **Hàng cho chữ dài:** tiêu đề ở một phần ba trái, thân bài ở hai phần ba phải, cùng một tỉ lệ chia cho mọi section dạng này.
- Toàn trang có hai hoặc ba cạnh trái cho các khối chữ. Đếm được sáu là các thứ được đặt từng cái một.

## 4. Khoảng trống

Phân biệt **chỗ nghỉ** (có chủ đích) với **lỗ hổng** (tình cờ). Cách trang hỏng:

1. Khoảng giữa section bị kéo quá xa: những dải 250–760px nền trơn.
2. Chữ ở một nửa section, nửa kia không có gì.
3. Nội dung đến muộn: hiệu ứng lộ diện chưa chạy nên người xem cuộn vào nền trống.
4. Khối ngắn bị kéo thành cả màn hình: footer đệm bằng chiều cao màn hình.
5. Cảnh được ghim mà gần như không chứa gì trong nhiều màn hình.
6. Ảnh khác chiều cao canh đỉnh trong một hàng, để lại lỗ dưới ảnh ngắn.

Luật:
- Quyết định khoảng trống nằm ở đâu và gọi tên thứ khép nó lại: chính ảnh (bầu trời, mặt đất, vật thể) với chữ cập mép; một ảnh ở phía xa của dải trống; chữ đủ lớn để trải hết khoảng; hai đoạn chữ ngắn ở hai đầu một đường chân chữ. Không có gì khép thì đó là lỗ hổng.
- Giữ khoảng trống sạch: không chú thích lạc, không hình trang trí, không watermark mờ, không đường lưới.
- Các section cách nhau 120–240px trên desktop. Khoảng giữa section rõ ràng lớn hơn mọi khoảng bên trong section. Thứ liên quan ngồi gần nhau.
- Không đoạn nào cao hơn khoảng nửa màn hình mà trống trơn.
- Nội dung có mặt ngay lần vẽ đầu. Hiệu ứng xuất hiện chỉ di chuyển thứ đã ở đó.
- Kích thước section theo nội dung. `min-height: 100svh` chỉ cho section thật sự lấp đầy màn hình.
- Ảnh khác chiều cao trong một hàng: canh đáy, hoặc đặt gì đó dưới ảnh ngắn.
- Chỗ nghỉ là một thứ trên một màn hình: một dòng, một vật, một ảnh, hoặc một vùng màu. Tối đa một lần mỗi trang.
- Khi section trông trống, câu trả lời gần như không bao giờ là "thêm gì đó". Làm thứ chính lớn hơn.

## 5. Khung trang: lề, cân bằng, tiêu đề

- Lề trái và phải bằng nhau ở mọi độ rộng.
- Phần tràn mép là có chủ đích và bắt đầu từ lề: một hàng ảnh chạy ra khỏi mép phải.
- Bất đối xứng nằm trong khung: một đường neo lệch tâm (một phần ba, 42%, đường giữa), và một tiêu đề lệch tâm được trả lời bằng thứ gì đó ở phía xa của lưới.
- Chữ chiếm một bên thì ảnh, cột thứ hai, danh sách hoặc con số lớn chiếm bên kia.
- Phần giữa cũng tính: một thẻ ở mép trái và một nút lẻ ở mép phải với một phần ba giữa trống là lỗi.
- Màn hình đầu có một `h1` ở cỡ hiển thị (từ 32px trên desktop), có mặt ngay lần vẽ đầu.
- 82% section chữ trên trang nghiên cứu mở bằng tiêu đề. Section không tiêu đề thường dùng nhãn nhỏ thay thế (chữ hoa, mono, số), thứ bị cấm ở đây. Một câu tuyên ngôn chỉ được mở section khi nó gọi tên thứ section chứa.
- **Ý tưởng sống đến pixel cuối cùng.** Hỏi mỗi section, kể cả bảng giá và hỏi đáp: section này mang ý tưởng của trang thế nào?

## 6. Section: mang ý tưởng, đổi cách sắp

- Mỗi section có bố cục khác section kề nó. Viết một từ cho bố cục mỗi section (chia đôi, danh sách, tràn viền, lưới, tuyên ngôn, mục lục...). Cùng một từ hai lần liền nhau, hoặc ba lần trên trang, là template đang lộ ra.
- Không section nào là lưới thẻ.
- Lặp lại phục vụ nhận diện; chỉ phá khi nội dung hoặc thứ ưu tiên thay đổi. Biến đổi không phải là mục tiêu tự thân.

## 7. Điều hướng

- Tên thương hiệu, ba đến năm link chữ đơn giản, một nút hành động. Không khung thanh, không viên thuốc nổi, không kính mờ.
- Nhãn link là danh từ đơn.
- Trang một màn hình có thể không cần thanh điều hướng: tên, vài link và một thông tin ở các góc, như viền tranh.

## 8. Phần kết

Footer là một đoạn kết được thiết kế, không phải sơ đồ trang: trên đa số trang mạnh, cái tên trở lại ở toàn chiều rộng. Thông tin liên hệ, giờ mở cửa, địa chỉ thật nằm ở đây, rõ ràng.

## 9. Điện thoại là một bố cục thứ hai

- Bố cục điện thoại có khung cắt ảnh riêng, chỗ ngắt dòng riêng, thứ tự riêng; không phải desktop bị bóp.
- Màn hình đầu trên điện thoại vẫn là một thứ rõ ràng.
- Không hàng nào cuộn ngang ngoài ý muốn: trong ảnh chụp nó trông như bị cắt. Chỉ để cuộn ngang khi cắt rõ ràng có chủ đích (thẻ cuối lộ một phần ở mép).
- Thứ tự DOM và thứ tự focus vẫn khớp thứ tự nhìn thấy.
- Responsive là cấu trúc: sắp lại, thu gọn, dàn lại, hoặc hiện ra dựa trên cái gì còn quan trọng. Ưu tiên component phản ứng theo container (`@container`) khi cùng một component xuất hiện ở nhiều ngữ cảnh.
- Vùng chạm từ 44×44px, kể cả khi dấu nhìn thấy nhỏ hơn.

## 10. Kiểm tra bố cục

Trên ảnh chụp đã render (Impeccable):

- **Bài test nheo mắt:** làm mờ chi tiết; vẫn phải nhận ra phần chính, phần phụ và các nhóm lớn theo đúng thứ tự.
- **Nhóm:** thứ liên quan có gần nhau, các nhóm khác nhau có tách xa, hay khung đang bù cho sự gần kém?
- **Nhịp:** khoảng chặt và khoảng rộng có tạo nhịp có chủ đích, hay một giá trị lặp lại đến khi mọi thứ ngang nhau?
- **Cấu trúc:** bố cục có khớp nội dung và tác vụ? Các thẻ, cột, section lặp lại có thật sự tương đương, hay chỉ là mặc định của framework?
- **Mật độ:** lượng thông tin mỗi vùng có hợp tần suất dùng, độ phức tạp quyết định và chế độ?
- **Thích ứng:** ở hẹp, vừa, rộng, phóng to, bản dịch dài: cái gì sắp lại, thu gọn, xuống dòng, cuộn, hay cố định?
- **Cực đoan:** nội dung dài, trạng thái rỗng, lớp phủ, phần tử dính, vùng an toàn, vùng chạm nhỏ có làm lộ lỗi cấu trúc?

Chỉnh quang học chỉ sau khi nhìn kết quả render. Một bản soát sạch không chứng minh được thứ bậc hay nhịp.
