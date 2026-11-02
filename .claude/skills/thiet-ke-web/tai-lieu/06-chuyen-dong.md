# Chuyển động

Emil Kowalski có tiếng nói cuối cùng về chuyển động giao diện; taste-skill cung cấp ngân sách và số đo cho trang quảng bá; Impeccable thêm nguyên tắc "một khoảnh khắc có chủ đích". Ba nguồn đã được hợp nhất ở đây thành một bộ quyết định và một bộ token. Code nằm ở `07-cong-thuc-chuyen-dong.md`.

> Những chi tiết vô hình cộng dồn lại. Hầu hết chi tiết người dùng không bao giờ nhận ra một cách có ý thức. Đó chính là mục đích. (Emil)

## 1. Khung quyết định (trả lời theo thứ tự, trước khi viết code)

### Câu 1: Có nên chuyển động không?

Hỏi: người dùng thấy nó bao nhiêu lần?

| Tần suất | Quyết định |
|---|---|
| Trên 100 lần/ngày (phím tắt, bật tắt command palette) | Không animate. Không bao giờ. |
| Vài chục lần/ngày (hover, điều hướng danh sách) | Bỏ hoặc giảm mạnh |
| Thỉnh thoảng (modal, drawer, toast) | Animation tiêu chuẩn |
| Hiếm, lần đầu (onboarding, form góp ý, ăn mừng) | Có thể thêm niềm vui |

**Không bao giờ animate hành động khởi phát bằng bàn phím.** Raycast không có animation mở và đóng; đó là trải nghiệm tối ưu cho thứ dùng hàng trăm lần mỗi ngày.

Với trang quảng bá: hiệu ứng xuất hiện chỉ chạy một lần mỗi lượt xem, tức thuộc loại "hiếm", nên được phép (và bắt buộc, xem mục 4).

### Câu 2: Mục đích là gì?

Mọi chuyển động phải trả lời được "tại sao nó chuyển động?". Mục đích hợp lệ:
- **Nhất quán không gian:** toast vào và ra cùng một hướng, nên vuốt để bỏ có cảm giác tự nhiên.
- **Chỉ báo trạng thái:** nút biến hình cho thấy trạng thái thay đổi.
- **Giải thích:** animation marketing cho thấy một tính năng hoạt động thế nào.
- **Phản hồi:** nút co lại khi nhấn, xác nhận giao diện đã nghe.
- **Tránh thay đổi đột ngột:** phần tử xuất hiện hay biến mất không có chuyển tiếp trông như hỏng.

"Trông ngầu" mà người dùng thấy thường xuyên thì không animate.

### Câu 3: Easing nào?

```
Đang xuất hiện hoặc biến mất?   → ease-out (bắt đầu nhanh, thấy phản hồi ngay)
Di chuyển hoặc biến hình trên màn hình? → ease-in-out
Hover, đổi màu?                 → ease
Chuyển động liên tục (marquee, thanh tiến trình), gắn thanh cuộn? → linear
Mặc định                        → ease-out
```

- **Không bao giờ dùng `ease-in` cho giao diện.** Nó bắt đầu chậm, làm trễ đúng khoảnh khắc người dùng đang nhìn kỹ nhất. Dropdown `ease-in` 300ms *cảm giác* chậm hơn `ease-out` 300ms. Ngoại lệ duy nhất: thứ biến mất hẳn, rất ngắn, trước một lần xuất hiện chậm (`--ease-exit`).
- **Dùng đường cong tự định nghĩa.** Easing có sẵn của CSS quá yếu.
- Không nảy, không đàn hồi theo phản xạ. Spring nảy nhẹ (0.1–0.3) chỉ cho kéo thả và tương tác vui.
- Tìm đường cong mạnh hơn ở easing.dev hoặc easings.co thay vì tự chế.

### Câu 4: Nhanh cỡ nào?

| Phần tử | Thời lượng |
|---|---|
| Phản hồi khi nhấn nút | 100–160ms |
| Hover | 150–200ms |
| Tooltip, popover nhỏ | 125–200ms |
| Dropdown, select, menu | 150–250ms |
| Modal, drawer | 200–500ms |
| Lộ diện section khi cuộn (Quảng bá) | 600–1000ms |
| Mở ảnh, wipe (Quảng bá) | 1100–1600ms |
| Chuyển trang (view transition) | tối đa 480ms |
| Thoát | khoảng 60–70% thời gian vào |

**Luật: animation giao diện dưới 300ms.** Dropdown 180ms cảm giác nhạy hơn 400ms. Spinner quay nhanh làm việc tải có vẻ nhanh hơn dù thời gian thật như nhau. Tooltip hiện ngay lập tức sau cái đầu tiên làm cả thanh công cụ có vẻ nhanh hơn. Thời lượng dài chỉ dành cho nội dung marketing và giải thích.

## 2. Bộ token thống nhất

Dùng bộ này cho cả dự án, để mọi thứ có chung một "cảm giác tay":

```css
:root {
  /* Easing */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);          /* Emil: mọi tương tác UI, phần tử xuất hiện dưới 600ms */
  --ease-expo: cubic-bezier(0.16, 1, 0.3, 1);          /* lộ diện dài từ 600ms, dòng chữ trồi, mở ảnh */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);      /* Emil: vật di chuyển khi đang hiển thị, wipe */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);       /* Emil: drawer, sheet kiểu iOS */
  --ease-soft: cubic-bezier(0.33, 1, 0.68, 1);         /* ảnh trôi, phóng chậm */
  --ease-exit: cubic-bezier(0.55, 0.055, 0.675, 0.19); /* thứ biến mất hẳn, rất ngắn */

  /* Thời lượng tương tác */
  --t-press: 140ms;
  --t-hover: 180ms;
  --t-tooltip: 160ms;
  --t-ui: 240ms;
  --t-modal: 300ms;

  /* Thời lượng trang quảng bá */
  --t-reveal: 800ms;
  --t-open: 1200ms;
  --stagger-item: 70ms;
  --stagger-line: 90ms;
}
```

## 3. Quy tắc vật lý (Emil, mọi chế độ)

- **Không bao giờ xuất hiện từ `scale(0)`.** Không gì ngoài đời xuất hiện từ hư không. Bắt đầu từ `scale(0.9–0.97)` kèm `opacity: 0`, như quả bóng xẹp vẫn có hình dáng.
- **Nút phải "nghe" tay:** `transform: scale(0.97)` khi `:active`, chuyển tiếp 140–160ms. Áp dụng cho mọi thứ bấm được; mức co nhẹ (0.95–0.98).
- **Popover mở từ nút kích hoạt:** `transform-origin` tại nút (Radix, Base UI có biến sẵn). **Modal là ngoại lệ:** giữ ở giữa.
- **Transition, không keyframes, cho giao diện động.** Transition bị ngắt sẽ đổi hướng mượt; keyframes chạy lại từ đầu. Mọi thứ có thể bị kích hoạt liên tục (thêm toast, bật tắt) dùng transition.
- **Thời gian không đối xứng:** chậm ở chỗ người dùng đang quyết định (nhấn giữ để xóa: 2 giây tuyến tính), nhanh ở chỗ hệ thống phản hồi (thả ra: 200ms ease-out).
- **Thoát nhanh hơn vào.**
- **`@starting-style`** để animate lúc phần tử xuất hiện mà không cần JavaScript.
- **`translateY(100%)` dịch theo chính kích thước phần tử,** nên không cần đo. Ưu tiên phần trăm hơn pixel cứng.
- **`clip-path: inset(...)`** là công cụ animation mạnh: lộ diện ảnh, nhấn giữ để xóa, tab đổi màu mượt, thanh so sánh hai ảnh.
- **Làm mờ 2–5px** để che một chuyển cảnh mờ dần trông như hai vật chồng nhau. Dưới 20px.
- **Spring** cho kéo có quán tính, cử chỉ có thể bị ngắt, thứ cần "sống". Cấu hình kiểu Apple dễ hiểu hơn: `{ type: "spring", duration: 0.5, bounce: 0.2 }`. Spring giữ vận tốc khi bị ngắt.
- **Chuyển động theo chuột** nội suy bằng spring (`useSpring`) thay vì gắn thẳng giá trị, nhưng chỉ khi chuyển động mang tính trang trí. Biểu đồ chức năng trong app ngân hàng thì không animate là tốt nhất.
- **Hover chỉ sau `@media (hover: hover) and (pointer: fine)`.**
- **So le 30–80ms** giữa các phần tử (giao diện), 50–90ms (trang quảng bá). Không bao giờ chặn tương tác trong lúc so le chạy.

### Cử chỉ và kéo

- **Bỏ bằng quán tính:** không bắt kéo qua một ngưỡng khoảng cách. Tính vận tốc `|khoảng cách| / thời gian`; vượt khoảng 0.11 thì bỏ, bất kể khoảng cách. Một cú vuốt nhanh là đủ.
- **Giảm chấn ở biên:** kéo quá biên tự nhiên thì càng kéo càng đi ít.
- **Pointer capture** khi bắt đầu kéo, để vẫn kéo được khi con trỏ rời phần tử.
- **Chống đa chạm:** bỏ qua các điểm chạm thêm sau khi đã bắt đầu kéo.
- **Ma sát thay vì tường cứng.**

## 4. Ngân sách chuyển động theo chế độ

### Quảng bá / Trải nghiệm

Trang không chuyển động trông như bản mock-up. Lớp chuyển động gồm:

1. **Một hiệu ứng chủ đạo** (ghi trong phiếu hướng): thứ người xem kể lại sau một giờ. Chỉ nó được phép ồn ào. Đây chính là "một khoảnh khắc có chủ đích" của Impeccable.
2. **Xuất hiện theo từng phần ở mỗi section:** tiêu đề, chữ, ảnh, chi tiết đến theo thứ tự đọc, so le 60–90ms, nâng 16–32px kèm opacity, một lần. **Đổi cách theo nội dung** thay vì đóng cùng một hiệu ứng mọi nơi: danh sách đến từng hàng, ảnh mở từ mặt nạ hoặc lắng từ scale nhẹ, con số cuộn lên một lần, câu tuyên ngôn trồi từng dòng.
3. **Phản hồi dưới tay:** nút co khi nhấn, link đáp lại con trỏ, ảnh và thẻ phản hồi hover, menu mở từ chỗ được bấm.
4. **Một hình ảnh chuyển động:** video thật làm vòng lặp tắt tiếng có ảnh poster, ảnh lớn trôi hay phóng chậm, hoặc ảnh hero chuyển động theo cuộn.

Tổng cộng ít nhất **tám phần tử thật sự chuyển động** khi tải và cuộn. Ngoại lệ: hướng `stillness`.

Luật cho trang quảng bá:
- **Khung hình đầu:** tiêu đề, câu phụ, ảnh có sẵn trong HTML và hiện ngay. Chuỗi mở trang không chờ sự kiện load, xong trước 1,2 giây, tối đa bốn phần tử.
- **Không preloader, không bộ đếm, không cổng "bấm để vào", không con trỏ tùy chỉnh, không chiếm quyền cuộn.** Trong nghiên cứu, một phần ba số trang vẫn không đọc được gì sau 4,5 giây vì preloader.
- **Lộ diện:** kích hoạt một lần khi đỉnh phần tử ở 85–90% chiều cao màn hình; không thứ gì trong tầm nhìn bị ẩn quá 900ms; không thứ gì trên màn hình đầu phải chờ cuộn.
- **Chuyển động gắn thanh cuộn** thì tuyến tính, quãng di chuyển dưới 8% phần tử, scale trong 0.94–1.15, dựng bằng scroll timeline trong `@supports`, đứng yên khi không hỗ trợ.
- **Sân khấu ghim:** `position: sticky`, khoảng một màn hình mỗi bước, tối đa ba màn hình, mỗi màn hình được giữ có một dòng chữ.
- **Mỗi thứ một cái:** một hiệu ứng chủ đạo, một hình ảnh chuyển động, tối đa một băng chữ chạy.
- **Chữ luôn đọc được:** hiệu ứng tô mực bắt đầu từ 45%; mục mờ không dưới 40%; blur tối đa 8px và biến mất khi đã lắng; không gì chạy ngang qua chữ đang được đọc.
- **Màu theo chương** đổi cứng ở mép section; màu chữ của header theo trong 300ms.
- **Chuyển động ngang:** hàng kéo ngang gốc trước; thư viện trượt ngang được ghim chỉ cho hàng ngắn hơn ba màn hình, có hỗ trợ bàn phím.
- **Chuyển trang** bằng view transitions, tối đa 480ms, tắt khi giảm chuyển động.
- Không thư viện cuộn mượt mặc định: chúng tạo độ trễ giữa tay và trang. Nếu thật sự cần, lerp 0.1–0.14 và tắt cho cảm ứng và giảm chuyển động.

### Thao tác / Đọc

- Thang tần suất ở mục 1 áp dụng nghiêm ngặt. Không số tối thiểu.
- 150–250ms cho đa số chuyển tiếp. Chuyển động truyền đạt trạng thái, không trang trí.
- Không chuỗi mở trang.
- Chỉ `transform` và `opacity`.

## 5. Giảm chuyển động

`prefers-reduced-motion: reduce` nghĩa là **ít hơn và nhẹ hơn, không phải không có gì.** Giữ đổi opacity và màu giúp hiểu trạng thái; bỏ di chuyển, scale, parallax và tự chạy.

- Viết mọi trạng thái ẩn bên trong `@media (prefers-reduced-motion: no-preference)`, để với người giảm chuyển động trang đã hoàn chỉnh sẵn.
- Không dùng lệnh "giết" toàn cục kiểu `* { animation-duration: 0.01ms !important }`: nó phá cả những phản hồi có ích (Impeccable).
- Vòng lặp dừng khi giảm chuyển động, khi ra khỏi màn hình, và khi tab bị ẩn.
- React: `useReducedMotion()` của Motion.

## 6. Thứ gì làm lộ chuyển động do AI tạo

- Cùng một hiệu ứng mờ dần trồi lên cho mọi khối.
- Một tá hiệu ứng so le trong hero.
- Mọi thẻ và ảnh nổi lên hay phóng to khi hover.
- Easing nảy, đàn hồi trên phần tử giao diện.
- Vòng lặp vô nghĩa: chấm nhấp nháy, hình trôi nổi, chữ lấp lánh, huy hiệu xoay.
- Chữ xáo trộn kiểu "giải mã" hay đánh máy, khiến tiêu đề không đọc được trong vài giây.
- Hiệu ứng lộ diện không chạy, để lại một dải trống trên trang.

## 7. Gỡ lỗi chuyển động

- **Quay chậm:** tạm tăng thời lượng 2–5 lần, hoặc dùng bảng Animations của DevTools để làm chậm. Tìm: màu chuyển mượt hay thấy hai trạng thái chồng nhau? Easing bắt đầu, dừng có đột ngột? `transform-origin` đúng chưa? Các thuộc tính (opacity, transform, màu) có đồng bộ?
- **Từng khung hình:** bảng Animations của Chrome cho phép bước từng khung.
- **Thử trên thiết bị thật** cho cử chỉ chạm (drawer, vuốt). Laptop nhanh che giấu gần hết vấn đề.
- **Xem lại hôm sau** với đôi mắt mới.

## 8. Khi review chuyển động

Dùng bảng một cột **Trước | Sau | Lý do**. Danh sách kiểm tra:

| Vấn đề | Sửa |
|---|---|
| `transition: all` | Ghi rõ thuộc tính: `transition: transform 200ms var(--ease-out)` |
| Xuất hiện từ `scale(0)` | Từ `scale(0.95)` kèm `opacity: 0` |
| `ease-in` trên phần tử giao diện | `ease-out` hoặc đường cong tự định nghĩa |
| `transform-origin: center` trên popover | Đặt tại nút kích hoạt (modal được miễn) |
| Animation trên hành động bàn phím | Bỏ hẳn |
| Thời lượng trên 300ms cho phần tử giao diện | Giảm còn 150–250ms |
| Hover không có media query | Thêm `@media (hover: hover) and (pointer: fine)` |
| Keyframes trên phần tử bị kích hoạt liên tục | Dùng transition để ngắt được |
| Motion `x`/`y` khi trang đang bận | Dùng chuỗi `transform` đầy đủ |
| Vào và ra cùng tốc độ | Ra nhanh hơn vào |
| Mọi thứ hiện cùng lúc | So le 30–80ms |
| Không có `prefers-reduced-motion` | Bọc trạng thái ẩn trong `no-preference` |
