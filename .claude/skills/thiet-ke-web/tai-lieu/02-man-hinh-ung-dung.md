# Màn hình Thao tác và trang Đọc

Dashboard, admin, analytics, settings, hộp thư, hàng đợi công việc, ví, danh sách có bộ lọc, editor, công cụ; và docs, blog, bài viết, hướng dẫn, changelog. Impeccable chủ trì phần hệ thống; luật cho dashboard lấy từ nghiên cứu màn hình sản phẩm thật của taste-skill; chuyển động theo Emil.

Quy trình trang quảng bá **không** áp dụng ở đây: không rút hướng, không chuỗi mở trang, không tối thiểu tám chuyển động.

## Bài test "rập khuôn" cho sản phẩm

Ở đây sự quen thuộc thường là ưu điểm. Câu hỏi là: một người rành loại sản phẩm này có tin giao diện ngay lập tức, hay phải khựng lại ở từng thành phần hơi lệch?

Thất bại của giao diện sản phẩm không phải là sự nhạt, mà là **sự lạ không có mục đích**: nút trang trí quá mức, ô nhập lệch kiểu nhau, chuyển động thừa, font hiển thị ở chỗ cần nhãn, tự chế cách tương tác cho tác vụ tiêu chuẩn. Công cụ nên biến mất vào công việc.

Nhưng một dashboard do AI dựng là trung bình cộng mọi template: sidebar tối hoặc nhuộm màu với viên thuốc màu ở mục đang chọn, "Chào mừng trở lại" kèm bàn tay vẫy, bốn thẻ KPI mỗi thẻ có icon trong vòng tròn nhạt, "+12,5%" màu xanh và một sparkline, biểu đồ vùng gradient, bảng sọc ngựa vằn dưới tiêu đề viết hoa. Không có gì sai, và không có gì được quyết định.

## Tám điều phân biệt màn hình thật với màn hình AI

Từ nghiên cứu 23 màn hình sản phẩm thật (taste-skill), theo thứ tự mức thể hiện:

1. **Màu đặt trên dữ liệu, không trên khung.** Màn hình trung vị có khoảng 3% điểm ảnh có màu; 17/23 dưới 5%. 12/23 không có nút chính tô màu nào.
2. **KPI là chữ, không phải ô.** Không màn hình nào đặt icon trong vòng tròn màu cạnh KPI, không cái nào vẽ sparkline trên KPI.
3. **Bề mặt phẳng.** 17/23 không đổ bóng thẻ; tách bằng đường 1px hoặc một bậc tông.
4. **Không có header kiểu hero.** 9 màn hình không có tiêu đề nào trên 16px; nếu có, trung vị 24px.
5. **Biểu đồ gần như không có trang trí.** Một chuỗi dữ liệu thì không chú giải; đường lưới 3–7 đường mờ hoặc không có.
6. **Điều hướng lùi lại.** Mục đang chọn là viên thuốc xám trung tính hoặc chỉ đổi màu chữ.
7. **Bảng là đường kẻ và căn lề.** Không sọc ngựa vằn, không dải nền tiêu đề, số căn phải.
8. **Trạng thái dữ liệu trung thực.** Số không in là 0, giá trị thiếu là gạch ngang xám, section rỗng vẫn giữ khung.

**Cảnh báo học được khi thử nghiệm:** màn hình dựng theo các luật này lúc đầu sạch, yên, đúng, và thua màn hình giàu nội dung hơn. Lý do giám khảo đưa ra lần nào cũng giống nhau, và mỗi lý do giờ là một luật bên dưới: màn hình đầu mỏng; sản phẩm vắng mặt (không tên, không logo, có thể thuộc về bất kỳ ai); sự tiết chế che mất ý nghĩa (độ trễ tăng và lượt truy cập tăng cùng một màu xám); không có gì để làm; các hàng kết thúc lởm chởm. Yên tĩnh là điểm xuất phát, không phải đích.

## Quy trình

### 1. Kiểm kê dữ liệu và công việc

Liệt kê: dữ liệu thật màn hình này có (đối tượng, con số, con người, mốc thời gian), và các việc người dùng đến để làm, theo tần suất. Việc thường xuyên nhất phải cách màn hình đầu **một cú bấm**.

Nếu cần hỏi người dùng (Impeccable): tác vụ chính là gì, thông tin nào quan trọng, những trạng thái nào quan trọng, tần suất dùng, ràng buộc.

### 2. Gọi tên câu hỏi duy nhất của màn hình

Mỗi màn hình trả lời một câu hỏi trước tiên: "Doanh thu hôm nay về chưa?", "Lần deploy nào làm hỏng?", "Ai đang chờ trả lời?", "Ngân sách tháng này còn bao nhiêu?". Viết nó thành một dòng. Nó quyết định:
- **Cái gì lớn nhất.** Khối lớn nhất luôn là khối mang câu hỏi của màn hình. Con số lớn nhất trả lời câu hỏi mà dòng tiêu đề nói.
- **Cái gì đọc trước.**
- **Cái gì bỏ đi.** Trang settings có thể chỉ hiện ba con số sử dụng và link sang trang analytics thay vì vẽ biểu đồ.

Rồi gọi tên **phát hiện duy nhất**: sự thật trong dữ liệu hôm nay cần chú ý nhất ("9 khách không đến trong khi 8 người đang chờ chỗ", "lần deploy 23:28 làm tỉ lệ lỗi tăng gấp đôi"). Đặt nó ở chỗ đọc đầu tiên, dưới tiêu đề hoặc dưới con số chính, cạnh hành động nó dẫn đến.

Trên màn hình 1440×900, **mọi khối mà brief nhắc đến đều hiện tiêu đề và vài hàng đầu**.

### 3. Cho sản phẩm một gương mặt

Lời phàn nàn hàng đầu của giám khảo sau bốn vòng: "một bộ kit áp dụng tốt, không phải một sản phẩm có bản sắc" (Geist hoặc Inter mặc định, nền #f8f8f8, thẻ trắng 12px, xanh chanh trên đen). Token làm màn hình đúng; những thứ sau làm nó là của sản phẩm này:

- **Một nét nhận diện, chọn trước khi dựng:** nền nhuộm nhẹ từ thế giới sản phẩm, một font số có cá tính, hoặc màu thương hiệu trên phần tử dữ liệu chính. Chọn một, ghi vào ghi chú cạnh câu hỏi của màn hình, kiểm tra nó hiện ra trong ảnh chụp đầu tiên.
- **Logo và tên sản phẩm** ở đầu khung, vẽ riêng cho sản phẩm (chữ lồng hay biểu tượng đơn giản từ tên hoặc vật thể của nó, màu nhấn), không bao giờ là ô vuông đen với một chữ cái.
- **Một phần tử chỉ sản phẩm này có,** dựng từ chính các thứ của nó: luồng điện của một nhà dùng năng lượng mặt trời, dải "món đã hết" của tiệm bánh, độ phủ nhân sự so với mức tối thiểu của lịch nghỉ phép.
- **Một màu biểu đồ trên phần tử dữ liệu chính:** đường của hôm nay, cột đã đặt, kỳ hiện tại.
- **Con người và đồ vật là chính chúng:** mỗi người một chữ cái đầu cố định và một màu nhạt riêng (các người cạnh nhau lệch nhau ít nhất 60 độ sắc độ); sản phẩm hiện ảnh nhỏ, bìa đĩa hiện bìa.

**Đừng dựng lại một màn hình quen thuộc.** Khi sản phẩm giống một loại phổ biến (trang chủ tài chính, tổng quan deploy), bố cục quen chính là cái bẫy. Lấy cấu trúc từ chính các thứ của sản phẩm.

### 4. Dựng khung

Năm kiểu khung phổ biến: sidebar + nội dung; thanh trên + nội dung; sidebar + nội dung + cột phải; danh sách + chi tiết (hộp thư); canvas toàn màn hình (editor). Chọn theo công việc, không theo thói quen.

- **Sidebar:** tên sản phẩm và phạm vi (workspace) ở trên; mục đang chọn là nền xám nhạt hoặc chữ đậm hơn; một thanh màu bên trái tối đa một lần trong cả sản phẩm.
- **Canvas:** một lề trái và một lề phải cho mọi khối; các hàng kết thúc thẳng hàng (không lởm chởm).
- **Tiêu đề trang:** 20–28px, kèm dòng phát hiện; bộ lọc, tab và khoảng thời gian nằm cùng một hàng gần tiêu đề.

### 5. Đặt dữ liệu vào

Dữ liệu thật hoặc dữ liệu mẫu **cộng lại khớp** (tổng bằng tổng các phần, phần trăm cộng lại 100). Dữ liệu mẫu được dán nhãn là dữ liệu mẫu trong báo cáo.

### 6. Dựng các trạng thái

Mọi thành phần tương tác có: mặc định, hover, focus, active, disabled, loading, lỗi (và thành công khi có nghĩa). Đừng ship với một nửa.
- Loading: skeleton đúng hình nội dung, không phải spinner giữa nội dung.
- Rỗng: trạng thái rỗng **dạy cách dùng** giao diện, không phải "Không có gì ở đây". Section rỗng vẫn giữ khung.
- Lỗi: gọi tên vấn đề và cách khắc phục.

### 7. Kiểm tra

```bash
node <skill>/scripts/soat-loi.mjs <thư mục> --che-do thao-tac   # hoặc --che-do doc
node <skill>/scripts/chup-man-hinh.mjs <url> vong-1
```

Phê bình theo `11-danh-gia.md` (phần Thao tác dùng thang Nielsen), rồi `12-du-lieu-xau.md`.

## Luật chi tiết

### Chữ

- **Một font thường là đúng.** Giao diện sản phẩm không cần cặp font tiêu đề và thân bài. Một font sans tốt mang được tiêu đề, nút, nhãn, thân bài, dữ liệu. Font hệ thống được phép.
- **Thang cố định theo rem, không fluid.** Người dùng xem ở mật độ điểm ảnh ổn định; tiêu đề co giãn trong sidebar trông tệ hơn.
- **Tỉ lệ giữa các bậc 1.125–1.2.** Ở đây có nhiều loại chữ hơn trang quảng bá; tương phản cường điệu tạo nhiễu.
- Độ dài dòng cho văn xuôi vẫn 65–75 ký tự; dữ liệu và giao diện dày có thể dày hơn; bảng 120 ký tự trở lên vẫn ổn.
- Số trong bảng, giá, ngày theo cột: `font-variant-numeric: tabular-nums`.
- Không font hiển thị cho nhãn, nút, dữ liệu.

### Màu

- Mặc định **Tiết chế**: các màu trung tính nhuộm nhẹ từ thế giới sản phẩm, cộng một màu nhấn. Một màn hình riêng có thể **Cam kết** (một màu danh mục chở cả báo cáo; màn hình chào mừng phủ màu), nhưng Tiết chế là sàn.
- Bộ từ vựng trạng thái đầy đủ và nhất quán: hover, focus, active, disabled, selected, loading, error, warning, success, info.
- Màu nhấn chỉ cho hành động chính, mục đang chọn và chỉ báo trạng thái; không để trang trí.
- Một lớp trung tính thứ hai cho sidebar, toolbar, panel (ấm hơn hoặc lạnh hơn bề mặt nội dung một chút).
- **Màu nói tốt hay xấu, không nói lên hay xuống.** Mỗi chỉ số có một hướng tốt: chi phí tăng là xấu (màu tiêu cực), doanh thu tăng là tốt. Thay đổi bằng không hoặc không xác định thì màu xám.

### KPI

- Đa số là chữ trần, không có ô riêng; 1–6 mỗi hàng, số KPI khớp với lưới (bốn KPI, bốn cột).
- Giá trị 16–40px, trung vị 26px. Nhãn ở trên giá trị, màu xám, viết thường đầu câu.
- Không icon trong vòng tròn màu, không sparkline, không ô nhuộm màu.
- **Con số trả lời câu hỏi đứng đầu** và lớn nhất.
- Delta (tùy chọn) 10–15px, không lớn hơn nhãn, có khoảng thời gian bằng chữ ("so với 30 ngày trước"); chỉ tô màu con số, hoặc để cả delta màu xám.

### Biểu đồ

| Câu hỏi | Dạng |
|---|---|
| Có thay đổi theo thời gian không? | Một đường; vùng tô chỉ khi độ phủ 15% trở xuống |
| Mỗi kỳ bao nhiêu? | Cột góc vuông |
| Phân bố thế nào? | Histogram, các khoảng bằng nhau |
| Ai xếp hạng? | Danh sách thanh ngang đã sắp xếp |
| Chiếm bao nhiêu phần? | Vòng mỏng hoặc thanh xếp chồng 100%; tối đa năm phần |
| Còn bao xa tới mục tiêu? | Thanh tiến độ, ghi nhãn cả hai đầu, phần tô đúng tỉ lệ thật |
| Ở đâu? | Bản đồ kèm danh sách; danh sách mang độ lớn |

- Một màu cho mỗi biểu đồ; màu nhấn chỉ chạm vào dữ liệu.
- Không chú giải khi chỉ có một chuỗi; tiêu đề đã gọi tên nó.
- Đường lưới ngang 3–7 đường mờ hoặc không có; không đường trục y; đường đáy là đường đậm nhất.
- 4–7 mốc trục y, 4–8 nhãn trục x, không bao giờ xoay nghiêng nhãn. Chữ trục không lớn hơn chữ dữ liệu.
- Đường 1–3px, đoạn thẳng (không làm mượt). Cột góc vuông hoặc bo tối đa 4px phía trên.
- Dự báo không phải sự thật: sau hôm nay đường nét đứt.
- Chú thích sự kiện quan trọng (bước nhảy lớn gấp ba lần thay đổi thường) ngay trên biểu đồ.
- Lịch sử ngắn hay rỗng vẽ trung thực: đường không bằng phẳng với một đỉnh, không bịa thêm.
- Tooltip là chữ trần hoặc hộp đơn giản không mũi tên.

### Bảng và danh sách

- Hàng một dòng 36–53px (trung vị 45); hàng hai dòng có ảnh 56–92px.
- Tiêu đề cột 11–14px, thường, xám, viết thường đầu câu; không dải nền, đa số không đường kẻ dưới.
- Không sọc ngựa vằn. Tách hàng bằng đường mảnh nhạt hoặc chỉ bằng khoảng trống.
- Số căn phải, dùng tabular-nums; chữ căn trái.
- Danh sách tổng quan hiện 2–5 hàng rồi link "Xem tất cả".
- Viên thuốc trạng thái: nền nhạt, chữ đậm hơn cùng sắc độ, ít loại; không dùng cho mọi thứ.

### Form và settings

- Nhãn luôn hiện (không chỉ dùng placeholder); ô nhập 16px trở lên để điện thoại không tự phóng to.
- Lỗi nằm ngay dưới ô, gọi tên vấn đề và cách sửa, không chỉ đổi viền đỏ.
- Nhóm theo ý nghĩa, dùng khoảng trống trước khi thêm khung.
- Lưu: rõ ràng là tự động lưu hay cần bấm Lưu; nhất quán trong cả sản phẩm.

### Thành phần

- Nhất quán: cùng hình nút, cùng bộ ô nhập, cùng kiểu icon ở mọi màn hình. Nút "Lưu" trông khác nhau ở hai chỗ thì một chỗ sai.
- **Modal không phải lựa chọn đầu tiên.** Thử hết phương án tại chỗ và mở dần trước.
- Lớp phủ thoát khỏi khung chứa: dropdown định vị tuyệt đối trong tổ tiên `overflow: hidden/auto` sẽ bị cắt; dùng `<dialog>`, popover API, `position: fixed` hoặc portal.
- Được phép: điều hướng chuẩn (thanh trên + sidebar, breadcrumb, tab, command palette), mật độ cao, sự nhất quán thay vì bất ngờ.

### Chuyển động

- 150–250ms cho đa số chuyển tiếp. Người dùng đang trong dòng chảy công việc; đừng bắt họ chờ vũ đạo.
- Chuyển động truyền đạt trạng thái, không trang trí: thay đổi trạng thái, phản hồi, loading, lộ ra.
- Không chuỗi mở trang. Sản phẩm tải vào thẳng tác vụ.
- **Thang tần suất của Emil áp dụng nghiêm ngặt** (`06-chuyen-dong.md`): command palette, phím tắt, chuyển tab bằng bàn phím: không animate. Hover trên danh sách dùng hàng chục lần mỗi ngày: bỏ hoặc giảm mạnh.

## Trang Đọc

Docs, blog, bài viết, hướng dẫn:

- Cấu trúc vì sự hiểu trước, rồi mới làm trải nghiệm đọc đáng ở lại.
- Cột chữ 60–75 ký tự; thân bài 17–20px, leading 1.5–1.7 (tiếng Việt nghiêng về 1.6–1.7 vì dấu).
- Mục lục và điều hướng giữa các trang rõ ràng; tiêu đề có link neo; vị trí hiện tại được đánh dấu.
- Code block dùng monospace (đây là chỗ đúng của nó), có nút sao chép, cuộn ngang trong khối chứ không làm cả trang cuộn ngang.
- Chuyển động gần như bằng không.
