# Chữ viết

Chữ viết là quyết định thiết kế đầu tiên. Một tiêu đề cần bốn dòng thì typography không cứu được; một trang toàn khẩu hiệu thì bố cục không cứu được. Viết cả trang thành văn bản thường trước khi viết markup. Theo taste-skill, cộng phần tiếng Việt và phần chữ trong giao diện của Impeccable.

## 1. Viết lập luận trước

Trả lời mỗi câu một dòng, trong ghi chú nháp:

- Ai đang đọc, và họ đã biết gì?
- Đây là gì, nói theo cách người làm ra nó kể với bạn bè?
- Sau một màn hình, người đọc nên tin điều gì?
- Điều gì khiến họ tin (ảnh của món đồ, một con số, một cái tên, một màn trình diễn)?
- Họ làm gì tiếp?

Rồi liệt kê trang thành các lời khẳng định, mỗi section một cái, kèm bằng chứng:

```
1. Cà phê rang mỗi sáng thứ Ba, trong một xưởng ở dốc Nhà Làng.  → lò rang, thật lớn
2. Mỗi mẻ chỉ 12 ký, nên hết là hết.                             → bảng mẻ tuần này
3. Hạt từ ba nông hộ ở Cầu Đất, có tên từng hộ.                  → ba chân dung, ba vườn
4. 180 nghìn một túi 250g, giao trong ngày ở Đà Lạt.               → giá, nút đặt
```

Section không có lời khẳng định là chữ độn; xóa nó. Thứ tự lập luận là thứ tự trang.

## 2. Tiêu đề hai dòng

Tiêu đề là một cái tên, nắm được trong một cái liếc. Trên các trang đoạt giải, tiêu đề hero trung vị 5 từ (tiếng Anh) và 32 ký tự; 70% nằm trên một hoặc hai dòng ở desktop. Mọi tiêu đề, ở mọi độ rộng, **tối đa hai dòng**.

Giới hạn này là phép tính, nên làm trước khi mê một câu:

```
ký tự mỗi dòng ≈ độ rộng dòng (px) ÷ (cỡ chữ (px) × k)
k ≈ 0.40  font đặc hẹp (condensed)
k ≈ 0.50  đa số grotesk và serif ở cỡ hiển thị, tracking chặt
k ≈ 0.58  font rộng (extended), viết hoa toàn bộ
```

| Ở đâu | Độ rộng dòng | Cỡ | Mỗi dòng | Ngân sách hai dòng |
|---|---|---|---|---|
| Điện thoại 390, lề 20px | 350px | 44px | ~16 | **~32 ký tự** |
| Điện thoại 390, lề 20px | 350px | 34px | ~21 | ~42 ký tự |
| Tablet 768 | 690px | 64px | ~22 | ~44 ký tự |
| Desktop, cột 12 | 1100px | 104px | ~21 | ~42 ký tự |
| Desktop, nửa chiều rộng | 620px | 72px | ~17 | ~34 ký tự |

Vậy tiêu đề hero **khoảng 32 ký tự trở xuống** sống được ở mọi nơi ở cỡ tự tin. Đến khoảng 42 được nếu cỡ trên điện thoại giảm xuống giữa 30. Quá đó là đang viết một câu; chuyển phần còn lại xuống câu phụ.

**Tiếng Việt tính theo ký tự, không theo từ.** "Rang mỗi sáng thứ Ba" là 5 từ, 20 ký tự. Tiếng Việt nhiều từ một âm tiết nên năm, sáu từ thường vẫn trong ngân sách; nhưng tám từ thì đếm lại. Ký tự có dấu chiếm cùng chiều rộng như ký tự không dấu, nhưng cần thêm khoảng dòng (xem `03-chu.md`).

Kiểm soát chỗ ngắt:
- Đặt `max-width` theo `ch` cho tiêu đề để nó ngắt ở chỗ bạn muốn, và `text-wrap: balance` để hai dòng đều nhau.
- Chỗ ngắt quan trọng (thường là vậy) thì tự đặt: `Rang mỗi sáng<br> thứ Ba`. Kiểm tra ảnh điện thoại; nếu dòng tự đặt lại xuống dòng, ẩn `<br>` dưới một breakpoint hoặc rút ngắn.
- **Không ngắt giữa một từ ghép hay cụm từ** tiếng Việt ("cà / phê", "Đà / Lạt", "thứ / Ba"). Dùng `&nbsp;` giữa các âm tiết của một từ ghép khi cần giữ chúng cùng dòng.
- Không bao giờ sửa tiêu đề dài chỉ bằng cách thu nhỏ. Chín từ rụt rè ở 28px tệ hơn năm từ ở 64px.
- Tránh một từ mồ côi ở dòng hai. Cân lại bằng cách cắt một từ, không bằng cách xê dịch độ rộng.

Tiêu đề section theo cùng luật và ngắn hơn: hai đến năm từ.

**Câu tuyên ngôn không phải tiêu đề.** Một câu giới thiệu hay trích dẫn đặt lớn là đoạn văn: markup bằng `<p>` hoặc `<blockquote>`, khoảng 25 từ, ở cỡ tuyên ngôn (36px trở xuống trên desktop, 24px trên điện thoại), được chạy đến ba dòng (bốn trên điện thoại). Lớn hơn thế, hoặc markup thành heading, hoặc đặt làm dòng chính của màn hình đầu, thì nó là tiêu đề và chịu luật hai dòng.

## 3. Các dạng tiêu đề hiệu quả

Chọn dạng giản dị nhất mà vẫn đúng:

- **Cái tên.** Tên thương hiệu hay người, đặt rất lớn, mô tả một dòng ở chỗ khác. Mạnh nhất khi tên ngắn và chủ thể giàu hình ảnh (studio, nhà hàng, khách sạn, cá nhân).
- **Nó là gì.** "Kệ đĩa than trong túi áo." "Nội thất cho căn hộ nhỏ." Tên loại, kèm một từ cụ thể.
- **Lời khẳng định.** "Ngân hàng của bạn không làm được điều này." Một câu đối thủ không ký được.
- **Lời mời làm.** "Hiểu tiền của bạn." Động từ đứng đầu, ngắn.
- **Nơi chốn hoặc khoảnh khắc.** "Côn Đảo." "Hội An, từ 1984." Cho du lịch, sự kiện, lưu trú.

Các dạng cần tránh, vì là trung bình cộng của mọi landing page:

- Điền vào chỗ trống: "Nền tảng ứng dụng AI cho đội ngũ hiện đại".
- Bộ ba: "Nhanh. Đơn giản. An toàn." hoặc "Lên kế hoạch. Xây dựng. Ra mắt."
- Câu sửa sai: "Không chỉ là công cụ, mà là cả một quy trình". Cũng như "Hơn cả một…".
- "X, theo cách mới", "Định nghĩa lại X", "Chào mừng đến với…", "Giới thiệu…" cho thứ chưa ai biết.
- Câu hỏi người đọc không hỏi.
- Tiêu đề cần dấu hai chấm: "Sổ Xanh: hóa đơn cho người làm tự do". Bỏ tên đi, nó đã ở thanh điều hướng.
- Một từ của tiêu đề được tô khác (nghiêng, serif, màu, gạch chân, đặt trong viên thuốc).

Viết thường đầu câu (chỉ hoa chữ đầu và tên riêng). Không dấu chấm cuối, trừ khi giọng của hướng thiết kế dùng dấu chấm ở mọi nơi.

## 4. Câu phụ, thân bài, nút

**Câu phụ.** Một câu, tối đa khoảng 22 từ, nói cụ thể đây là gì và cho ai. Là chỗ chứa chi tiết bị cắt khỏi tiêu đề. Không bao giờ nhắc lại tiêu đề bằng từ khác.

**Thân bài.** Đoạn ngắn, câu khẳng định đơn giản. Ưu tiên danh từ cụ thể và con số thật: "giao trong tuần" hơn "giao hàng nhanh"; "38 chỗ ngồi" hơn "không gian ấm cúng". Đọc từng câu và hỏi: một công ty khác có in nguyên câu này được không? Được thì làm sắc lại hoặc cắt.

**Nút.** Gọi tên hành động hay đồ vật: "Đặt bàn", "Xem bảng giá", "Tải cho Mac". Một đến ba từ. Hành động chính giữ một tên ở mọi chỗ trên trang. Một nút chính mỗi màn hình; hành động thứ hai là link chữ. Không mũi tên trên mọi link và nút; tối đa một mũi tên, trên hành động chính, nếu hướng thiết kế có dùng mũi tên.

**Điều hướng.** Tên thương hiệu, tối đa năm link, một hành động. Nhãn link là danh từ đơn ("Thực đơn", "Phòng", "Liên hệ").

**Chữ trong giao diện (Impeccable):**
- Điều khiển gọi tên hành động của nó ("Lưu thay đổi", không phải "OK").
- Lỗi gọi tên vấn đề và cách khắc phục ("Số điện thoại thiếu một chữ số", không phải "Dữ liệu không hợp lệ").
- Trạng thái rỗng dạy cách dùng ("Chưa có đơn nào. Đơn mới sẽ hiện ở đây ngay khi khách đặt.").
- Dùng ngôn ngữ của chính sản phẩm và người dùng; tránh thuật ngữ nội bộ.
- Nhất quán thuật ngữ, viết hoa và dấu câu trong cả sản phẩm.
- Hỏi trước khi thay câu chữ mang tính sự thật hoặc thêm lời khẳng định.

## 5. Bằng chứng mà không bịa

Không bao giờ bịa khách hàng, trích dẫn của người có tên, logo báo chí, số người dùng, đánh giá sao hay số liệu so sánh. Bằng chứng bịa vừa không trung thực vừa là dấu hiệu AI.

Khi brief không có bằng chứng, dùng thứ đúng sẵn:
- Cho thấy chính món đồ, thật lớn. Một màn trình diễn thật hơn mọi trích dẫn.
- Nói cụ thể nó hoạt động thế nào.
- Dùng sự thật trong brief (giá, địa điểm, năm, chất liệu, những gì bao gồm).
- Nếu brief yêu cầu rõ section cảm nhận khách hàng hay logo mà không có cái thật, dựng section với nội dung mẫu rõ ràng là hư cấu và nói trong báo cáo để thay trước khi ra mắt. Không dùng tên công ty thật hay người thật.

**Chi tiết mẫu khác với bằng chứng, và được kỳ vọng.** Khi brief cho hình dạng nội dung mà không đủ chi tiết (sáu phòng "từ 1,2 triệu", "thực đơn ngắn", mười hai diễn giả), viết đầy đủ chi tiết hợp lý: mỗi phòng có tên, giường, hướng nhìn và giá riêng; mỗi món có giá; mỗi diễn giả có tên bài nói. Thiết kế chỉ đánh giá được ở mật độ thật. Liệt kê mọi chi tiết mẫu trong báo cáo để khách xác nhận hoặc thay.

## 6. Những thứ đọc lên như máy viết

`soat-loi.mjs` bắt được phần lớn.

**Tiếng Việt:** giải pháp toàn diện, đột phá, hàng đầu, nâng tầm, tối ưu hóa trải nghiệm, trải nghiệm tuyệt vời, liền mạch, vượt trội, đỉnh cao, cách mạng hóa, mọi lúc mọi nơi, chất lượng hàng đầu, uy tín số 1; nút "Khám phá ngay", "Tìm hiểu thêm", "Bắt đầu ngay"; mở đầu "Chào mừng bạn đến với…"; câu "không chỉ là X mà còn là Y".

**Tiếng Anh:** unlock, unleash, supercharge, elevate, empower, streamline, seamless, effortless, robust, cutting-edge, next-generation, world-class, all-in-one, blazing fast; "Get started", "Learn more".

**Mọi ngôn ngữ:**
- Nhãn giả làm tạp chí: "Ghi chép thực địa", "Triết lý của chúng tôi", "Được tin dùng một cách lặng lẽ". Tiêu đề section có thể đơn giản là "Bảng giá".
- Chữ trang trí: dải giờ địa phương, "Est. 2024", tọa độ, số phiên bản, "Cuộn xuống", tín dụng ảnh giả, dòng trạng thái "Đang nhận dự án" kèm chấm xanh, chuỗi từ ngăn bằng chấm giữa hoặc gạch chéo.
- Gạch ngang dài (—) thành thói quen. Một, hai cái trên trang đọc như người viết; mười cái đọc như máy. Dùng dấu chấm.
- Chú thích kể lể thiết kế: "Một bố cục tối giản, sạch sẽ cho…".
- Nhãn bước trùng với số: "Bước 1", "Giai đoạn 02".
- Bộ ba ở khắp nơi: ba tính năng, ba số liệu, ba bước. Dùng đúng số lượng nội dung có.

## 7. Vi chữ

- Dấu ngoặc kép cong (“ ” ‘ ’), dấu ba chấm thật (…), gạch ngang ngắn cho khoảng (9–17 giờ).
- Khoảng trắng không ngắt (`&nbsp;`) giữa số và đơn vị (250&nbsp;g, 180&nbsp;nghìn), và giữa các âm tiết của từ ghép ở cuối tiêu đề khi không thì nó bị mồ côi.
- Tiền Việt: "180.000&nbsp;đ" hoặc "180 nghìn", nhất quán cả trang. Dùng `Intl.NumberFormat('vi-VN')` cho số do code sinh ra.
- Ngày: "Thứ Ba, 22/10" hoặc "22 tháng 10", nhất quán.
- `tabular-nums` cho số xếp cột.
- Không viết hoa toàn bộ thứ gì dài hơn ba từ; viết hoa thì thêm tracking 0.02–0.06em.
- Không chữ dưới 13px. Không căn giữa đoạn hơn ba dòng. Không căn đều hai bên.
