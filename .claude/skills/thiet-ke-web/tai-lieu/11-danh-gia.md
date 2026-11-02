# Đánh giá

Ba phần: **phê bình bằng mắt** (taste-skill, cho trang Quảng bá / Trải nghiệm), **chấm khả dụng** (Impeccable, cho Thao tác / Đọc), và **kiểm tra kỹ thuật và đánh bóng** (Impeccable, mọi chế độ). Review code thì trình bày bằng bảng **Trước | Sau | Lý do** (Emil).

Soát lỗi sạch chỉ nghĩa là không đo thấy thứ bị cấm. Nó không nói gì về chuyện trang có hay không. File này là cách biết.

**Phán xét qua ảnh, không qua code.** Bạn viết code nên sẽ đọc ý định của mình vào đó. Ảnh chỉ cho thấy những gì thật sự có. Chụp bằng:

```bash
node <skill>/scripts/chup-man-hinh.mjs <url hoặc file> vong-1
```

Script đã cuộn qua cả trang để kích hoạt mọi hiệu ứng lộ diện trước khi chụp, và chờ chuỗi mở trang chạy xong. Nếu vẫn thấy một dải trống hay một tiêu đề thiếu, chạy lại một lần; còn thấy thì đó là lỗi thật. Một phần tử bị ẩn vì thời gian animation sẽ trông như thiếu, và "sửa" nó sẽ tạo ra lỗi.

---

# Phần A. Phê bình trang Quảng bá / Trải nghiệm

## A1. Cách nhìn: mười bốn lượt

Mở `1440-01.png` (màn hình đầu desktop), rồi lần lượt `1440-02`, `1440-03`... theo thứ tự cuộn, rồi `768-*` và `390-*` (điện thoại). Đọc cả phần "Báo cáo nhanh" script in ra (cuộn ngang, font đã tải, phần tử còn ẩn). Mỗi lượt làm riêng, đừng trộn.

1. **Một giây, rồi năm giây.** Liếc rồi quay đi. Bạn thấy gì? Phải có đúng một câu trả lời: một từ, một hình, một vật. Nếu câu trả lời là "một trang web", không có tiêu điểm. Rồi nhìn màn hình đầu năm giây như người lạ: nói được đây là gì, cho ai, làm gì tiếp không? Tiêu đề chỉ có nghĩa sau khi cuộn thì không phải tiêu đề.
2. **Nheo mắt.** Làm mờ đến khi chữ thành thanh xám. Trang phải còn hai, ba khối lớn với chênh lệch kích thước rõ. Nhiều khối nhỏ giống nhau nghĩa là mọi thứ đều vừa và không gì dẫn dắt.
3. **Che logo.** Màn hình đầu này có thể thuộc về đối thủ, hay một ngành khác? Đổi tên và danh từ trong tiêu đề mà trang vẫn đúng thì trang không có ý tưởng. Rồi cuộn: ý tưởng có đến được bảng giá, hỏi đáp, chân trang, hay trang biến thành các khối rập khuôn sau màn hình đầu?
4. **Các cạnh.** Lần theo cạnh trái của mọi khối chữ xuống trang. Đếm số vị trí ngang khác nhau. Trang có bố cục có hai hoặc ba, dùng lại có chủ đích. Sáu là các thứ được đặt từng cái một.
5. **Khoảng trống và khung.** Thứ liên quan gần nhau, thứ không liên quan xa nhau? Khoảng giữa section rõ ràng lớn hơn mọi khoảng bên trong? Có vùng nào trống do tình cờ (lỗ hổng) chứ không do quyết định (chỗ nghỉ)? Lề trái phải bằng nhau? Có section nào để chữ một nửa và nửa kia trống? Có đoạn nào trống cao hơn nửa màn hình? Người xem nêu những lỗi này đầu tiên ("dồn hết sang trái", "khoảng trống vô lý").
6. **Chữ.** Bước từ thân bài lên tiêu đề có dứt khoát (gấp ba trở lên)? Có hơn năm cỡ? Tiêu đề nào có từ mồ côi ở dòng cuối? Đoạn văn nào rộng hơn khoảng 75 ký tự hoặc căn giữa quá ba dòng? Với tiếng Việt: dấu nào bị cắt, chạm dòng trên, hay lệch kiểu vì font dự phòng?
7. **Màu.** Gọi tên tỉ lệ: màu nào giữ phần lớn bề mặt, màu nào hỗ trợ, nhấn ở đâu? Màu nhấn ở mười chỗ thì chẳng nghĩa gì.
8. **Ảnh.** Đếm ảnh thật: ít nhất bốn? Có một hình ảnh chuyển động? Mỗi ảnh có làm việc (cho thấy món đồ, dựng nơi chốn, chứng minh lời khẳng định)? Tỉ lệ cắt có thống nhất? Có ô xám, ảnh bị kéo giãn, màn hình giả bằng thanh xám? Ảnh có chung một ánh sáng và một tông?
9. **Sự giống nhau.** Viết một từ cho bố cục mỗi section (chia đôi, danh sách, tràn viền, lưới, tuyên ngôn, mục lục...). Cùng từ hai lần liền nhau, hay ba lần trên trang, là template đang lộ.
10. **Điện thoại.** Màn hình điện thoại là một bố cục riêng, với khung cắt và ngắt dòng riêng, hay desktop bị bóp? Màn hình đầu vẫn là một thứ rõ ràng?
11. **Độ đầy.** Đi qua từng màn hình desktop. Mỗi màn hình là một tấm áp phích có bố cục, hay một cột chữ nhỏ hẹp với nền chết hai bên? Trang khắc khổ không phải trang kiềm chế: nếu có thể nhầm với wireframe chưa xong (khối xám, chữ xám, một cột nhỏ), nó dựng thiếu. Một họa tiết phóng to lấp đầy cả màn hình mà không có gì để đọc cũng là lỗ hổng.
12. **Thực chất.** Mọi section brief yêu cầu có đưa đủ thông tin ở cỡ đọc được (cả thực đơn, từng phòng, mọi diễn giả, giá và những gì bao gồm)? Người xem rời đi có biết điều họ đến để tìm? Hành động chính có là nút thật trên màn hình đầu?
13. **Va chạm.** Có gì đè lên tiêu đề, câu tuyên ngôn hay nút ở bất kỳ vị trí cuộn nào? Có gì chạy ra khỏi mép màn hình điện thoại? Một hàng cuộn ngang trên điện thoại trông như bị cắt; cho xuống dòng trừ khi việc cắt rõ ràng có chủ đích.
14. **Đối thủ và thứ sống động.** Đặt tên đối thủ gần nhất lên trang: ý tưởng còn đúng không? Rồi gọi tên thứ sống động duy nhất. Một trong hai câu trả lời yếu thì đó là vấn đề đầu tiên của vòng này, trước mọi chi tiết.

Ghi chú từ thử nghiệm: trong so sánh mù, trang giàu nội dung đầy thiết bị template luôn thắng trang sạch hơn nhưng mỏng. Luật nhà gỡ thiết bị; lượt 11–13 đảm bảo trang không mất thực chất cùng chúng.

## A2. Chấm điểm

Chấm như giám khảo Awwwards: bốn tiêu chí, mỗi tiêu chí 1–10, trọng số **thiết kế 40%, khả dụng 30%, sáng tạo 20%, nội dung 10%**.

**Thiết kế (40%):** bố cục, chữ, màu, ảnh, độ tinh xảo.
- 9–10: mọi màn hình đứng vững như áp phích. Không gì bỏ đi hay dời đi được.
- 8: tự tin và mạch lạc; một, hai điểm mềm mà nhà thiết kế sẽ nhận ra.
- 7: sạch và chuyên nghiệp, hệ thống rõ, ít độ căng.
- 6: gọn nhưng vô danh. Trông như một bộ kit.
- 5 trở xuống: thứ bậc yếu, khoảng cách tình cờ, chữ mặc định, ảnh lệch nhau.

**Khả dụng (30%):** định hướng trong ba giây, chữ đọc được, hành động rõ, điện thoại trung thực.
- 9–10: biết đây là gì, cho ai, làm gì mà không cần cuộn; hoàn hảo trên điện thoại.
- 8: rõ ràng, dễ chịu; ma sát nhỏ (một section dài, một vùng chạm nhỏ).
- 7: dùng được, có một vấn đề thật (tương phản yếu đâu đó, bố cục điện thoại chật).
- 6 trở xuống: phải đi tìm, hoặc có gì đó hỏng.

**Sáng tạo (20%):** một ý tưởng nói được trong một câu, mang suốt trang.
- 9–10: một khái niệm riêng cho chủ thể này chưa từng thấy áp dụng như vậy.
- 8: ý tưởng rõ với một khoảnh khắc đáng nhớ.
- 7: thực hiện tinh tế một cách tiếp cận đã biết.
- 6 trở xuống: mặc định của ngành.

**Nội dung (10%):** chữ và ảnh cụ thể, nghe như thật, được biên tập.
- 9–10: mọi dòng chỉ có thể nói về chủ thể này; ảnh chính là chủ thể.
- 7–8: rõ và cụ thể, vài dòng chung chung.
- 6 trở xuống: khẩu hiệu, chữ độn, ảnh stock.

`tổng = 0.4·thiết kế + 0.3·khả dụng + 0.2·sáng tạo + 0.1·nội dung`

Hiệu chỉnh: trang Site of the Day thật được giám khảo chấm khoảng 7.5–8.0. Một 8.5 trung thực là hiếm. Nếu điểm đầu tiên bạn cho chính mình là 9, chấm lại như một giám khảo không dựng nó.

## A3. Mức trần

Các mức trần đè lên phép tính:

- Còn LỖI trong `soat-loi.mjs`: tổng tối đa **6.0**.
- Tiêu đề ba dòng trở lên ở bất kỳ độ rộng nào, eyebrow, nhãn monospace, đánh số 01/02/03, gradient trang trí, bóng trên vật đứng yên, hoặc đường kẻ mảnh trang trí thấy được trong ảnh: tổng tối đa **6.5**.
- Lượt 3 thất bại (trang có thể thuộc về bất kỳ ai): sáng tạo tối đa **6**.
- Ý tưởng vẫn đúng với đối thủ gần nhất: sáng tạo tối đa **7**.
- Dưới bốn ảnh thật (ảnh chụp, ảnh tư liệu, video; hình vẽ không tính): thiết kế tối đa **6.5**.
- Trang gần như không chuyển động, hoặc cùng một hiệu ứng mờ cho mọi khối: thiết kế tối đa **7**.
- Không có thứ sống động: sáng tạo tối đa **7.5**.
- Có nội dung giữ chỗ (ô xám, lorem, "Ảnh ở đây"): nội dung tối đa **5**.
- Hai màn hình desktop trở lên gần như toàn nền trống, hoặc chữ chạy dài nhỏ và xám: thiết kế tối đa **6.5**.
- Một section brief yêu cầu bị thiếu hoặc chỉ còn vài chữ: nội dung tối đa **6**.
- Không có nút thật cho hành động chính trên màn hình đầu: khả dụng tối đa **7**.
- Lượt năm giây thất bại (màn hình đầu không có tiêu đề rõ đây là gì): khả dụng tối đa **6**.
- Lề không đều, section dồn một bên với nửa kia trống, hoặc đoạn trống cao hơn nửa màn hình: thiết kế tối đa **6.5**.
- Một section chữ chạy dài không có tiêu đề gọi tên nó: khả dụng tối đa **7**.
- Bất cứ thứ gì đè lên tiêu đề ở bất kỳ vị trí cuộn nào: khả dụng tối đa **6**.
- Một dải trống do hiệu ứng lộ diện không chạy, hoặc nội dung bị cắt khỏi màn hình: khả dụng tối đa **5**.
- **Tiếng Việt:** dấu bị cắt hoặc chữ có dấu hiển thị bằng font dự phòng trong một tiêu đề: thiết kế tối đa **6**.

## A4. Viết phê bình

Viết ra, đừng chỉ nghĩ. Dùng đúng mẫu này để so sánh các vòng:

```
VÒNG n
Thấy trong một giây: …
Ý tưởng (một câu): …
Thứ sống động: …
Bố cục theo section: hero=… / …=… / …
Điểm: thiết kế _ · khả dụng _ · sáng tạo _ · nội dung _ → tổng _._
Mức trần đã áp: …
Ba vấn đề lớn nhất (dễ thấy nhất trước), mỗi vấn đề kèm ảnh chụp thấy nó và cách sửa:
1. …
2. …
3. …
```

Gọi tên vấn đề như nhà thiết kế nói với đồng nghiệp: "đoạn phụ bắt đầu lệch trái 40px so với cạnh tiêu đề", "section cảm nhận là bố cục chia đôi thứ ba liên tiếp", "hero trên điện thoại cắt mất cái chai". "Có thể trau chuốt hơn" không phải là một phát hiện.

## A5. Sửa gì trước

Theo thứ tự; thứ sau không cứu được thứ trước:

1. **Ý tưởng.** Lượt 3 thất bại thì đổi khái niệm hero, không sửa chi tiết.
2. **Thứ bậc.** Một phần tử chủ đạo mỗi màn hình. Làm thứ lớn lớn hơn, thứ nhỏ ít đi, trước khi đụng gì khác.
3. **Bố cục.** Cạnh chung, khoảng cách section, đa dạng bố cục giữa các section, lỗ hổng.
4. **Chữ.** Tương phản cỡ, ngắt dòng, độ dài dòng, leading, dấu tiếng Việt.
5. **Ảnh.** Thay ảnh yếu, thống nhất khung cắt và tông.
6. **Màu.** Tỉ lệ và kỷ luật màu nhấn.
7. **Chi tiết.** Trạng thái, focus, căn lề nhỏ, tinh chỉnh điện thoại.
8. **Chuyển động.** Cuối cùng.

Bỏ một thứ để lại khoảng trống thì đừng lấp bằng đồ trang trí. Thu khoảng trống, phóng to thứ còn lại, hoặc để một ảnh hay một vùng màu chiếm chỗ.

## A6. Khi nào dừng

Tối đa ba vòng: phê bình → sửa ba vấn đề lớn nhất → chụp lại → phê bình. Dừng sớm khi một vòng không tìm thấy vấn đề nào người lạ sẽ nhận ra. Vòng ba vẫn dưới 7.5 thì nói thẳng trong báo cáo, kèm các vấn đề còn lại; không làm tròn lên.

---

# Phần B. Chấm khả dụng cho Thao tác / Đọc

## B1. Mười nguyên tắc Nielsen

Chấm mỗi nguyên tắc 0–4 (0 = vi phạm nghiêm trọng, 4 = xuất sắc thật sự). Đa số giao diện thật đạt 20–32/40. Nguyên tắc không áp dụng thì ghi `n/a` và tính lại thang tối đa (8 nguyên tắc thì /32, không in /40).

| # | Nguyên tắc | Hỏi |
|---|---|---|
| 1 | Hiển thị trạng thái hệ thống | Người dùng luôn biết chuyện gì đang xảy ra (đang tải, đã lưu, lỗi)? |
| 2 | Khớp với thế giới thật | Dùng từ ngữ, khái niệm của người dùng, không thuật ngữ nội bộ? |
| 3 | Kiểm soát và tự do | Có lối thoát rõ ràng, hoàn tác, hủy? |
| 4 | Nhất quán và chuẩn mực | Cùng thứ thì cùng tên, cùng hình, cùng chỗ? Theo quy ước nền tảng? |
| 5 | Phòng lỗi | Thiết kế ngăn lỗi trước khi xảy ra (xác nhận thao tác nguy hiểm, giới hạn đầu vào)? |
| 6 | Nhận ra hơn nhớ lại | Lựa chọn và thông tin hiện sẵn thay vì bắt người dùng nhớ? |
| 7 | Linh hoạt và hiệu quả | Có lối tắt cho người dùng thạo (phím tắt, thao tác hàng loạt)? |
| 8 | Thẩm mỹ và tối giản | Mỗi phần tử đều có ích; không có thông tin thừa cạnh tranh? |
| 9 | Nhận biết, chẩn đoán, khắc phục lỗi | Lỗi nói rõ vấn đề và cách sửa bằng ngôn ngữ thường? |
| 10 | Trợ giúp và tài liệu | Có trợ giúp đúng ngữ cảnh khi cần? |

## B2. Mức độ vấn đề

| Mức | Tên | Mô tả |
|---|---|---|
| **P0** | Chặn | Không hoàn thành được tác vụ. Sửa ngay. |
| **P1** | Lớn | Gây khó khăn hay nhầm lẫn đáng kể. Sửa trước khi ra mắt. |
| **P2** | Nhỏ | Phiền nhưng có cách vượt qua. Sửa đợt sau. |
| **P3** | Đánh bóng | Nên sửa, không ảnh hưởng thật. |

Phân vân giữa hai mức: "người dùng có liên hệ hỗ trợ vì chuyện này không?" Có thì ít nhất P1.

## B3. Năm nhân vật thử nghiệm

Đi qua giao diện dưới góc nhìn của những người dùng có khả năng gặp nó nhất:

- **An, người dùng thạo và thiếu kiên nhẫn:** muốn làm nhanh, dùng bàn phím, ghét animation và bước thừa. Có phím tắt không? Thao tác hàng loạt?
- **Bình, người dùng lần đầu bối rối:** không biết thuật ngữ, không biết bắt đầu từ đâu. Trạng thái rỗng có dẫn dắt? Nhãn có rõ?
- **Châu, người dùng cần trợ năng:** dùng trình đọc màn hình hoặc chỉ dùng bàn phím, phóng to 200%. Thứ tự focus? Nhãn? Tương phản?
- **Dũng, người cố tình làm hỏng:** nhập dữ liệu lạ, bấm hai lần, mất mạng giữa chừng. Xem `12-du-lieu-xau.md`.
- **Giang, người dùng điện thoại bị phân tâm:** một tay, nắng gắt, bị gián đoạn liên tục. Vùng chạm? Trạng thái được giữ khi quay lại?

## B4. Tải nhận thức

Kiểm tra: bức tường lựa chọn (quá nhiều lựa chọn cùng lúc); bắt người dùng nhớ thông tin từ màn hình trước; điều hướng ẩn; rào cản thuật ngữ; nhiễu thị giác; khuôn mẫu không nhất quán; đòi làm nhiều việc cùng lúc; chuyển ngữ cảnh liên tục. Bộ nhớ làm việc chứa khoảng bốn mục; nhóm thông tin cho vừa.

---

# Phần C. Kiểm tra kỹ thuật (mọi chế độ)

Chấm mỗi chiều 0–4:

1. **Trợ năng.** Tương phản dưới 4.5:1; `prefers-reduced-motion` có phương án có chủ đích (không phải lệnh giết toàn cục); phần tử tương tác thiếu vai trò, nhãn, trạng thái; điều hướng bàn phím (focus thấy được, thứ tự hợp lý, không bẫy bàn phím); HTML ngữ nghĩa (thứ bậc heading, landmark, `<button>` thay vì `<div>`); alt cho ảnh; form có nhãn, thông báo lỗi tốt, đánh dấu ô bắt buộc.
2. **Hiệu năng.** Đọc ghi bố cục xen kẽ trong vòng lặp; animation thuộc tính bố cục; blur, filter, bóng không giới hạn; ảnh không lazy-load, không tối ưu; `will-change` rải khắp; gói JavaScript thừa; re-render không cần thiết. Xem `08-hieu-nang-va-di-dong.md`.
3. **Theme.** Màu viết cứng không qua token; chế độ tối hỏng hoặc thiếu; token dùng sai vai trò; giá trị không cập nhật khi đổi theme.
4. **Responsive.** Độ rộng cố định vỡ trên điện thoại; vùng chạm dưới 44×44px; cử chỉ chạm hỏng (thanh trượt, vùng kéo nuốt mất thao tác cuộn trang); cuộn ngang ngoài ý muốn; bố cục vỡ khi tăng cỡ chữ; thiếu breakpoint.
5. **Độ toàn vẹn.** Lối tắt lặp đi lặp lại, hệ thiết kế bị trôi, nội dung gây hiểu lầm hay trang trí, cấu trúc có thể hoán đổi với một sản phẩm không liên quan. Chạy `soat-loi.mjs` và kiểm tra từng phát hiện trong ngữ cảnh; tách phát hiện máy khỏi nhận định thị giác; ghi rõ báo nhầm.

---

# Phần D. Đánh bóng trước khi ra mắt

Đi qua toàn bộ hành trình, không chỉ màn hình hiện tại (Impeccable):

- **Luồng và thứ bậc:** tác vụ chính và trạng thái hiện tại rõ ràng mà không san phẳng mọi thứ; đường đến, chuyển tiếp, rỗng và khôi phục nối với nhau thay vì là các màn hình rời rạc.
- **Bố cục và chữ:** căn theo lưới và thang khoảng cách, cả căn quang học lẫn toán học; cùng vai trò thì cùng kiểu chữ; thử độ dài dòng, xuống dòng, bản dịch dài, phóng to, tải font; kiểm tra mọi độ rộng được hỗ trợ.
- **Màu, ảnh, icon:** token ngữ nghĩa, ý nghĩa màu ổn định qua các theme; tương phản chữ, điều khiển, focus ở mọi trạng thái; bộ icon cùng nét, cùng cỡ, căn quang học; ảnh không gây nhảy bố cục.
- **Tương tác và trạng thái:** mọi điều khiển có mặc định, hover, focus, active, disabled, loading, lỗi, thành công; focus bàn phím thấy được, thứ tự Tab hợp lý, vùng chạm đúng nền tảng; chuyển động mạch lạc, ngắt được, hiệu năng tốt. **Đừng thêm animation chỉ để thấy là đã đánh bóng.**
- **Nội dung và code:** thuật ngữ, viết hoa, dấu câu, câu chữ sự thật nhất quán; xóa debug, code chết, import thừa, style cũ; thay phần tự chế bằng component dùng chung khi hệ thống đã có; đưa giá trị thật sự dùng lại vào token, đừng trừu tượng hóa cho một ngoại lệ.
- **Bề mặt trình duyệt:** màu bôi đen chữ, con trỏ nhập, thanh cuộn, vòng focus, khoảng gạch chân, số trong bảng: đều theo bảng màu. Đây là tín hiệu rẻ nhất cho thấy trang được dựng chứ không phải lắp ráp, và là thứ AI bỏ qua thường nhất.
