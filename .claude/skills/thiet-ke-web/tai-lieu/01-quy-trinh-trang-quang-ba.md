# Quy trình dựng trang Quảng bá và Trải nghiệm

Landing page, trang marketing, trang sản phẩm, portfolio, nhà hàng, khách sạn, sự kiện, trang một màn hình. Quy trình xương sống lấy từ taste-skill; chuyển động theo Emil; kiểm tra chất lượng theo Impeccable.

## Vì sao cần quy trình này

Một trang do AI dựng thường là trung bình cộng của mọi trang nó từng thấy: tiêu đề căn giữa ba dòng, một nhãn nhỏ phía trên, một hàng thẻ có icon, một gradient nhẹ, vài đường kẻ mảnh, một chú thích monospace. Không có gì sai, và cũng không có gì được quyết định.

Quy trình này thay các mặc định đó bằng quyết định, theo bốn cách:

1. **Script rút hướng, bạn chọn.** Tự nghĩ ra phong cách thì AI luôn chọn mặc định của ngành. `rut-huong.mjs` rút ba trong hai mươi hướng đã nghiên cứu; bạn chọn hướng mang được ý tưởng của chủ thể.
2. **Ý tưởng đến từ chủ thể.** Trong nghiên cứu 247 trang, thứ phân biệt trang hay với trang dễ quên là một ý tưởng lấy từ chính chủ thể, không phải từ cách trang trí.
3. **Luật nhà không trang trí**, được soát bằng script.
4. **Bạn nhìn thứ mình làm.** Chụp ở ba độ rộng, chấm như giám khảo, sửa, nhìn lại.

**Cảnh báo học được khi thử nghiệm:** bỏ hết đồ trang trí mới là một nửa. Một trang mất nhãn, đường kẻ, thẻ mà không được bù gì sẽ trông mỏng, và giám khảo mù luôn chọn trang giàu nội dung có dấu hiệu AI hơn trang trống trơn sạch sẽ. Nửa còn lại là **thực chất**: chữ lớn hơn, cả vùng màu, ảnh thật về thế giới của chủ thể, và mọi section mang đủ nội dung. Đừng đổi thực chất lấy sự kiềm chế.

## 1. Đọc brief và dự án

Tìm hiểu cái gì là thật: chủ thể, đối tượng, **một việc** trang phải khiến người xem làm, stack, thương hiệu sẵn có (màu, font, logo), và trên hết là **ảnh nào thật sự tồn tại**: ảnh chụp của dự án, giao diện thật có thể trưng, công cụ tạo ảnh, hay không có gì. Đừng lên kế hoạch dựa trên ảnh mình không có.

Nếu cần hỏi người dùng, hỏi hai, ba câu ảnh hưởng thật (theo Impeccable): ai phải hành động, họ cần tin điều gì, bằng chứng hay nội dung thật nào giúp họ tin; điều gì không được đụng vào; điều gì sẽ khiến một bản đẹp vẫn "sai".

Rồi **kiểm kê chủ thể** trong ghi chú: tám đến mười hai thứ thuộc về khách hàng này và không đối thủ nào có. Tìm ở:
- Tên và ý nghĩa của tên.
- Địa chỉ, số nhà, con phố, khu phố, và nơi đó trông thế nào (gạch lát, biển hiệu, màu sơn, kiểu chữ trên mặt tiền, ánh sáng, thời tiết).
- Các con số trong brief (số ghế, số phòng, số phút ra biển, giá, năm thành lập).
- Ràng buộc nó sống cùng (mỗi tháng một mẻ, đóng cửa mùa mưa, chỉ nhận đặt trước).
- Chất liệu và màu sắc.
- Nghi thức và giờ giấc (lò nhóm lúc năm giờ, chuyến phà bảy giờ).
- Những món đồ in trong thế giới của nó (thời gian biểu, nhãn, vé, biển hiệu, hóa đơn).

Trong thử nghiệm mù, trang thắng mỗi brief đều dựng từ một mục trong danh sách như thế; trang thua có bố cục tốt nhưng ý tưởng của cả ngành. Danh sách này cũng là từ khóa tìm ảnh ở bước 6.

## 2. Viết lập luận

Trước mọi thiết kế, liệt kê trang dưới dạng các lời khẳng định kèm bằng chứng, mỗi section một dòng (xem `09-chu-viet.md` mục 1):

```
1. Đây là ghế đẩu gỗ sồi ba chân, làm theo đơn.          → chiếc ghế, thật lớn
2. Mỗi mặt ghế cắt từ một tấm gỗ, nên vân là của riêng bạn. → ba ảnh cận cảnh
3. Mất sáu tuần, và bạn theo dõi được.                    → các công đoạn, có ảnh
4. Giá 6,2 triệu, thợ giao tận nơi.                        → giá, nút đặt
```

Các lời khẳng định quyết định section nào tồn tại và theo thứ tự nào. Section nào không có lời khẳng định thì xóa. Đây là cách thoát khỏi trình tự rập khuôn: hero, logo, ba tính năng, cảm nhận khách hàng, bảng giá, kêu gọi hành động.

## 3. Rút hướng thiết kế

```bash
node <skill>/scripts/rut-huong.mjs --nganh <ngành> --mo-ta "<một dòng về chủ thể>" \
  --phan <các vai theo thứ tự lập luận> [--giong <giọng>] [--co <tài sản>] [--giu mau,chu] --lua-chon 3
```

- `--nganh`: xem `--danh-sach nganh` (ví dụ `cafe`, `nha-hang`, `khach-san`, `phan-mem`, `ca-nhan`, `su-kien`). Chọn gần nhất; `khac` khi không có gì hợp.
- `--phan`: xem `--danh-sach phan` (ví dụ `gioi-thieu`, `tinh-nang`, `thuc-don`, `thu-vien-anh`, `bang-gia`, `hoi-dap`, `lien-he`, `chan-trang`). Hero mặc định có sẵn.
- `--giong` (tùy chọn): `yen-tinh`, `manh-me`, `am-ap`, `ky-thuat`, `vui-tuoi`, `sang-trong`, `tap-chi`. Chỉ truyền khi brief rõ ràng đòi hỏi.
- `--co`: tài sản **thật sự có**: `anh-chup` (ảnh của chính nơi chốn, con người, sản phẩm), `anh-san-pham`, `giao-dien` (ảnh chụp màn hình thật), `minh-hoa`, `video`. Không có thì bỏ trống; script sẽ tránh bố cục phụ thuộc vào chúng.
- `--giu mau,chu`: khi thương hiệu đã chốt màu hoặc font. Script chỉ rút bố cục; bạn gán màu, font của thương hiệu vào các vai.

Script in ba hướng. Đối chiếu từng hướng với danh sách kiểm kê: **cách bố cục nào mang được một thứ chỉ khách hàng này có?** Chọn hướng đó, không phải hướng quen nhất, và ghi một dòng lý do. Trong thử nghiệm, một hướng ngẫu nhiên không hợp chủ thể là nguyên nhân phổ biến nhất của trang yếu. Rồi rút phiếu đầy đủ:

```bash
node <skill>/scripts/rut-huong.mjs <cùng tham số, bỏ --lua-chon> --huong <mã đã chọn>
```

Phiếu lưu ở `.thiet-ke/huong.json`; in lại bất cứ lúc nào bằng `--xem`. Trong phiên dài, đọc lại phiếu trước mỗi section.

**Nhận lấy phiếu.** Đừng trộn với bố cục bạn vốn định làm. Thấy lạ là đúng: bố cục quen chính là thứ quy trình này tồn tại để ngăn.

Vẽ lại một ô (`--ve-lai hero | chu | mau | huong | phan:<vai>`) **chỉ khi nêu được lý do**: trái ràng buộc thương hiệu, cần tài sản không có, hoặc **font không có dấu tiếng Việt**. Không bao giờ vẽ lại để có thứ dễ chịu hơn. Ghi mọi lần vẽ lại vào báo cáo.

Khi một bản thiết kế section không chứa nổi nội dung thật (nó so ba gói giá mà chỉ có một giá; nó cần năm trích dẫn mà không có cái nào), đừng bẻ nội dung cho vừa. Xem các bản khác bằng `--thay-the <vai>` và chọn bằng `--ve-lai phan:<vai>=<mã>`.

**Kiểm tra bảng màu với chủ thể.** Bảng màu được rút là một bộ **tỉ lệ** (một nền, một mực, một nhấn, các vùng màu) cũng như một bộ màu. Nếu màu đánh nhau với chất liệu của chủ thể (pastel kẹo ngọt cho rượu whisky khói, neon cho nhà gỗ trên núi), vẽ lại bảng màu một lần. Nếu chủ thể có màu riêng không thể nhầm (chất liệu, màu sơn con phố, phong cảnh ngoài cửa sổ), giữ tỉ lệ đã rút nhưng lấy màu từ chủ thể, và nói rõ trong báo cáo.

**Kiểm tra font tiếng Việt ngay lúc này** nếu nội dung tiếng Việt (cách làm trong `03-chu.md`). Font thiếu dấu thì `--ve-lai chu` cho đến khi được font có dấu.

Phiếu giữ phần mô tả chi tiết bằng tiếng Anh vì đó là dữ liệu đo đạc gốc (cột, tỉ lệ, cỡ chữ); đọc như thông số kỹ thuật.

## 4. Tìm ý tưởng

Hướng là một cách bố cục. Ý tưởng là thứ khiến trang thuộc về chủ thể này và không ai khác. Viết câu này vào ghi chú và chưa dựng cho đến khi điền đủ hai chỗ trống từ chính chủ thể:

> **Trên trang này, [một thứ thuộc về chủ thể] trở thành [thiết bị mà hướng gọi đến].**

Chỗ tìm cho ô đầu:
- **Sản phẩm đầu ra.** Nó tạo ra gì? Đặt đầu ra thật lên trang làm chất liệu.
- **Hình dạng của nó.** Nhìn mặt cắt, bóng dáng. Phóng to, cắt xén, biến nó thành khung hoặc họa tiết duy nhất.
- **Cái tên.** Chữ cái có thể chứa ảnh, xếp thành tường, tách về hai góc?
- **Nơi chốn.** Có một khung cảnh khiến người ta muốn có mặt ở đó?
- **Nghi thức.** Có một trình tự trang có thể diễn lại khi cuộn?
- **Món đồ in.** Vật in nào đã tồn tại trong thế giới của nó: vé, thực đơn, nhãn, hóa đơn, thiệp, bìa hồ sơ, sách hướng dẫn?
- **Cái đối lập.** Ngành nào sở hữu cảm xúc mà ngành này thiếu?

**Bài test đối thủ:** đặt đối thủ gần nhất vào câu (tiệm bánh cách hai con phố, xưởng gỗ sồi khác, homestay khác trên cùng con dốc). Nếu câu vẫn đúng, ý tưởng là của cả ngành: một ổ bánh mì là mọi tiệm bánh; bảy cánh cửa của con phố mà tiệm này lấy tên thì chỉ tiệm này có. "Sạch sẽ và hiện đại" không phải ý tưởng.

**Bài test trí nhớ (Impeccable):** nếu ai đó rời đi sau màn hình đầu, một giờ sau họ sẽ kể lại gì? Nếu câu trả lời thật lòng là một "cảm giác", ý tưởng chưa thành hình.

**Một thứ sống động.** Cho trang một thứ người xem làm được, hoặc khác đi mỗi lần ghé, làm từ ý tưởng: chọn loại gỗ và thấy ghế bằng gỗ đó; gõ tên và thấy nó được cắt bằng chữ của xưởng in; kéo số tiền vay và đọc ngay số trả hàng tháng thật; xem bếp lò của nhà trên núi đang đỏ lửa không và còn bao lâu đến chuyến phà cuối. Trong thử nghiệm mù, mọi trang thắng đều có một thứ như vậy và giám khảo nhắc đến nó đầu tiên. Luật: dùng nội dung thật của chủ thể, dùng được bằng ngón cái trên điện thoại, có phương án thường khi không có script, không chặn việc đọc, và chỉ **một** thứ, không phải sân chơi. Dựng ở bước 6 như một phần của trang, không thêm vào như hiệu ứng ở bước 9.

## 5. Viết chữ

Viết toàn bộ trang thành bản thảo chữ (văn bản thường) trước khi viết markup, theo `09-chu-viet.md`:

- **Mọi tiêu đề vừa hai dòng hoặc ít hơn ở mọi độ rộng.** Làm phép tính ở `09-chu-viet.md` mục 2 trước khi chốt câu. Khoảng 32 ký tự là an toàn ở cỡ tự tin.
- Một câu phụ, ngay dưới tiêu đề (cách 32–48px), hiện cùng tiêu đề, không bị animation giữ lại. Khi tiêu đề là một cái tên hay một hình ảnh tu từ, câu này nói rõ đây là gì.
- Một hành động chính, đặt tên theo việc nó làm, là **nút thật** trên màn hình đầu.
- **Màn hình đầu trả lời câu hỏi đầu tiên của người xem bằng chữ lớn.** Sự kiện: là gì, khi nào, ở đâu (ngày tháng nằm trong tiêu đề hoặc ở cỡ thứ hai, không chỉ ở chữ nhỏ). Sản phẩm: là gì và giá bao nhiêu hoặc làm được gì. Con người: là ai và làm gì. Mỗi section người xem đến để tìm (thực đơn, phòng, giá) có tiêu đề riêng và chỗ riêng trong thanh điều hướng.
- **Viết đủ nội dung.** Cả thực đơn kèm giá, từng phòng với chi tiết riêng, từng diễn giả và bài nói, giá kèm những gì bao gồm, câu trả lời cho từng câu hỏi thật. Section mỏng là lý do phổ biến nhất khiến trang sạch thua trang rối.
- Chi tiết mẫu được phép ở chỗ brief bỏ trống (tên món, tên phòng, giá phòng) để thấy thiết kế ở đúng mật độ; liệt kê chúng trong báo cáo để khách xác nhận. **Bằng chứng thì không bao giờ bịa.**

## 6. Dựng, khi vẫn còn tĩnh

Dựng trang với chuyển động "tắt" trong đầu; trang cần animation mới trông xong thì chưa xong. Thứ tự:

1. **Token.** Vai trò màu và chữ từ phiếu thành biến CSS. Mọi thứ phía sau chỉ tham chiếu token. Thêm luôn bộ token chuyển động trong `06-chuyen-dong.md`.
2. **Hero, đúng như bản thiết kế mô tả,** ở desktop và điện thoại. Làm thứ lớn thật lớn, thứ nhỏ thật nhỏ trước khi có gì khác.
3. **Từng section theo bản thiết kế của nó,** với nội dung dự án. Giữ hình học, đổi chủ thể. Hai section kề nhau không cùng bố cục. **Mang ý tưởng vào mọi section**, kể cả bảng giá, hỏi đáp, chân trang: lỗi phổ biến nhất trong nghiên cứu, kể cả ở trang tốt, là màn hình đầu độc đáo rồi các khối rập khuôn.
4. **Hình ảnh**, theo thứ tự ưu tiên trong `10-hinh-anh.md`: ảnh của dự án → ảnh tạo bằng công cụ (nếu có) → ảnh thật về thế giới của chủ thể từ kho mở → hình tự vẽ bằng code từ chủ thể → chỉ chữ và màu. **Mức sàn:** ít nhất bốn ảnh thật, thường sáu đến mười hai; SVG tự vẽ không tính. Có dự án có video hay ảnh thật về quy trình, sản phẩm thì màn hình đầu cho thấy nó, lớn (khoảng 40% màn hình trở lên). Không bao giờ viết câu trên trang về nguồn gốc ảnh ("ảnh không phải quán chúng tôi"); chú thích nói ảnh là gì, dòng ghi nguồn nhỏ ở chân trang.
5. **Thứ sống động** từ bước 4, đặt ở section nó chứng minh lời khẳng định (thường là hero hoặc phần đặt chỗ), với nội dung thật, bản điện thoại vừa ngón cái, và phương án thường.
6. **Độ đầy.** Nhìn mỗi màn hình desktop như một tấm áp phích: một thứ chủ đạo và nội dung nó mang. Màn hình gần như toàn nền trống là section dựng thiếu, không phải chỗ nghỉ; mỗi trang tối đa một chỗ nghỉ có chủ đích. Chữ chạy dài màu mực đầy đủ, từ 16px; màu xám chỉ cho ghi chú phụ.
7. **Khung trang.** Một cặp lề ngoài bằng nhau ở mọi độ rộng; mọi section dùng hết chiều rộng trang đã dựng: chữ ở nửa trái thì nửa phải có ảnh, cột thứ hai, danh sách hoặc hình, không bao giờ bỏ trống. Bất đối xứng nằm trong lưới, không ở khung trang. Không đoạn nào cao hơn nửa màn hình mà trống trơn; các section cách nhau 120–240px trên desktop. Mỗi section người xem đến tìm mở bằng một tiêu đề gọi tên nó; màn hình đầu mang tên trang trong một `h1`.
8. **Trạng thái và ngữ nghĩa.** Link và nút thật, focus nhìn thấy được, alt cho ảnh, bố cục điện thoại là một bố cục riêng chứ không phải desktop bị bóp. Áp dụng nền tảng di động trong `08-hieu-nang-va-di-dong.md`.

Đọc `03-chu.md`, `04-mau.md`, `05-bo-cuc.md` khi cần chi tiết cho một quyết định.

## 7. Soát

```bash
node <skill>/scripts/soat-loi.mjs <thư mục mã nguồn> --che-do quang-ba
```

Sửa mọi LỖI. Mỗi CẢNH BÁO coi là sai trừ khi bảo vệ được trong một câu trước một nhà thiết kế. Thương hiệu bắt buộc dùng một thứ bị cấm (logo nằm trong gradient, màu chủ đạo là tím): giữ tài sản thương hiệu, nói rõ trong báo cáo, và bỏ qua đúng luật đó bằng `--bo-qua <mã>`.

## 8. Nhìn

Qua được bước soát chỉ có nghĩa là không đo thấy thứ bị cấm. Không có nghĩa là trang đẹp.

```bash
node <skill>/scripts/chup-man-hinh.mjs <url hoặc file> vong-1
```

Mở **mọi** ảnh (mọi độ rộng) và phê bình theo `11-danh-gia.md`: mười bốn lượt nhìn, điểm theo trọng số Awwwards, các mức trần. Viết phê bình ra theo đúng mẫu, sửa ba vấn đề lớn nhất, chụp lại, nhìn lại. Tối đa ba vòng.

Chỉ phán xét qua ảnh. Một vấn đề thấy được trong ảnh là vấn đề thật, bất kể code nói gì.

## 9. Chuyển động

Giờ mới dựng lớp chuyển động. Nó là bắt buộc, và nhiều hơn một hiệu ứng mờ dần. Bốn phần (chi tiết trong `06-chuyen-dong.md`, code trong `07-cong-thuc-chuyen-dong.md`):

1. **Hiệu ứng chủ đạo** ghi trong phiếu: một, làm thật tốt.
2. **Xuất hiện theo từng phần ở mỗi section:** tiêu đề, rồi chữ, rồi ảnh, so le 60–90ms, nâng 16–32px kèm opacity, kích hoạt một lần khi section vào màn hình. Không phải một hiệu ứng mờ cho cả khối, không phải cùng một hiệu ứng y hệt cho mọi section, và không bao giờ để nội dung ẩn mãi nếu script lỗi.
3. **Phản hồi trên mọi điều khiển:** nhấn, hover, focus trên nút, link, thẻ và thứ sống động. Thời lượng và easing theo Emil.
4. **Một hình ảnh chuyển động:** video thật làm vòng lặp tắt tiếng, ảnh trôi hay phóng chậm, hoặc ảnh hero chuyển động theo cuộn.

Tổng cộng ít nhất tám phần tử thật sự chuyển động khi trang tải và cuộn (ngoại lệ: hướng `stillness`). Chỉ `transform`, `opacity` (và `clip-path` cho mở ảnh); mọi chuyển động có phương án `prefers-reduced-motion` giữ nội dung và bỏ di chuyển. Chuyển động đổi màu hay bố cục cả màn hình (màu theo chương, câu chuyện ghim) là một phần bố cục: dựng ở bước 6.

Rồi soát và chụp lại lần nữa, kiểm tra mọi ảnh xem có nội dung nào không hiện ra, và mở riêng ảnh `1440-giam-chuyen-dong.png`.

## 10. Báo cáo

Chưa báo cáo cho đến khi tất cả đều đúng; mỗi điều từng bị bỏ qua trong một lần thử ra kết quả tệ:

- `soat-loi.mjs` không còn LỖI trên phiên bản cuối.
- Đã mở mọi ảnh chụp sau thay đổi cuối cùng, không chỉ màn hình đầu.
- Một người lạ đọc màn hình đầu năm giây nói được đây là gì và phải làm gì.
- Mọi section có tiêu đề; lề hai bên bằng nhau; không đoạn nào trống trơn.
- Phê bình vòng cuối đã được viết ra theo mẫu trong `11-danh-gia.md`.

Rồi báo cáo theo mục "Bước 5" của SKILL.md.

## Trường hợp đặc biệt

**Có sẵn thương hiệu hoặc hệ thiết kế.** Dùng `--giu mau,chu`, gán màu và font thương hiệu vào các vai, chỉ lấy bố cục từ phiếu. Luật nhà vẫn áp dụng.

**Review, restyle hoặc làm lại một trang có sẵn.**
1. Ghi lại trạng thái trước: chạy trang, `chup-man-hinh.mjs <url> truoc`, `soat-loi.mjs`. Đọc code: framework, cách viết style, component, và thứ phải giữ (route, form, dữ liệu, hành vi, tài sản thương hiệu).
2. **Review thì dừng ở đây.** Phê bình ảnh "trước" theo `11-danh-gia.md`, liệt kê phát hiện kèm kết quả soát, và gọi tên ba thay đổi có tác động lớn nhất.
3. Giữ stack, nội dung và những gì đang tốt. Không chuyển framework hay thư viện style; kiểm tra file phụ thuộc trước khi thêm gì. **Restyle** giữ bố cục, lấy chữ, màu và thành phần từ phiếu (`--giu` những gì thương hiệu đã chốt); **làm lại** rút hướng đầy đủ và dựng lại section từ bản thiết kế bên trong component có sẵn. Cả hai đi tiếp từ bước 2 với nội dung thật.
4. Thứ tự làm, tác động lớn nhất với rủi ro nhỏ nhất: chữ (font và thang cỡ) → màu (một nền, một mực, một nhấn) → khung trang (lề, nhịp section, tiêu đề màn hình đầu, tiêu đề mỗi section) → trạng thái (hover, focus, loading, rỗng, lỗi) → thay các thành phần rập khuôn (thẻ icon, badge viên thuốc, đốm gradient, lưới thẻ) bằng bản thiết kế được rút.
5. Chứng minh: chụp lại vào `sau`, so trước và sau ở mọi độ rộng, bấm thử mọi link, form, menu từng chạy được, và báo cáo số liệu trước và sau cạnh nhau.

**Không có hệ thống thanh toán hay backend cho form.** Nút chính dẫn đến đích thật nếu brief có. Không thì mở email (`mailto:` có tiêu đề và nội dung soạn sẵn kèm lựa chọn của người xem), hoặc với cửa hàng thì trỏ tới `#thanh-toan` và báo cáo rằng phải nối trước khi ra mắt. Không bao giờ làm form thanh toán giả.

**Trang có giao diện phần mềm.** Các mảnh giao diện hiển thị trên trang (màn hình sống ở hero, phần cắt của một tính năng, một biểu đồ) dựng như một phần thật của ứng dụng đó, theo luật trong `02-man-hinh-ung-dung.md`, với dữ liệu thật cộng lại khớp. Một mảnh trông như sản phẩm đang chạy là bức ảnh mạnh nhất mà trang phần mềm có thể có; thanh xám và số giả là yếu nhất. Gắn thuộc tính `data-ui` vào gốc mảnh đó: bên trong nó được giữ viền và menu của sản phẩm.
