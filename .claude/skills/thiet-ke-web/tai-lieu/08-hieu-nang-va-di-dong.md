# Hiệu năng và di động

Phần A theo skill `animation-performance` của Emil; phần B theo `mobile-native` của Emil; phần C là kiểm tra hiệu năng chung theo Impeccable.

---

# Phần A. Hiệu năng animation

Hãy tưởng tượng Sonner chạy ở 30 khung hình mỗi giây. Cùng easing, cùng thời lượng, cùng code. Sẽ chẳng ai quan tâm. Hiệu năng không phải bước đánh bóng sau cùng; nó là thứ cho phép chuyển động tốt được cảm nhận.

## Luật cứng

1. **`transform` và `opacity` là mặc định.** Mọi thứ khác cần lý do.
2. **Gọi tên nguyên nhân trước khi sửa code.** "Thêm `will-change`, có vẻ mượt hơn" không phải chẩn đoán.
3. **Không bao giờ kết luận "ổn rồi" từ một máy nhanh.** Chuẩn là điện thoại tầm trung, và trên màn hình 120Hz ngân sách chỉ còn một nửa. Nói rõ phát hiện nào kiểm tra từ code, phát hiện nào cần ghi hình trên thiết bị thật.
4. **Không bao giờ `transition: all`.**
5. **Đừng đổi tính đúng lấy một tối ưu may rủi.** Tăng tốc phần cứng là thứ trình duyệt *có thể* cho. Thuộc tính nào được animate là thứ bạn kiểm soát.

## Bảng triệu chứng

| Vấn đề | Cách sửa |
|---|---|
| Animation giật | Animate `transform`/`opacity`, không `width`/`height`/`top`/`margin` |
| Animate bóng bị khựng | Dùng `filter: drop-shadow()` thay `box-shadow` |
| Chỉ giật khi chuyển trang hoặc đang tải | Chuyển animation sang CSS hoặc WAAPI để chạy ngoài luồng chính |
| Motion `x`/`y` rớt khung | Animate chuỗi `transform` đầy đủ |
| Animation tự viết rớt khung trong React | Ghi vào `ref.current.style`, không qua state |
| Kéo càng chậm khi danh sách càng dài | Ngừng animate biến CSS được kế thừa; đặt `transform` trực tiếp |
| Hiệu ứng blur lag (nhất là Safari) | Giữ `blur()` được animate dưới 20px |
| Thuộc tính không mong muốn cũng chuyển động | Thay `transition: all` bằng thuộc tính cụ thể |
| Phần tử lệch 1px khi bắt đầu hoặc kết thúc | `will-change: transform`, chỉ khi đã thấy lỗi |

## Ngân sách khung hình

60 khung/giây cho trình duyệt **16,7ms** mỗi khung. Trên màn hình 120Hz (đa số điện thoại hiện nay) chỉ còn **8ms**. Thiết kế theo con số nhỏ hơn. Một lần tính lại bố cục trên trang phức tạp có thể mất hơn 100ms: không phải rớt một khung mà là cả chục.

## Animate cái gì

Trình duyệt chạy tối đa ba bước: **Layout** (tính kích thước, vị trí), **Paint** (vẽ thành lớp), **Composite** (ghép lớp lên màn hình).

| Bậc | Thuộc tính | Chi phí |
|---|---|---|
| Chỉ composite | `transform`, `opacity`; ở Chrome/Firefox hiện tại cả `filter`, `clip-path`, `background-color` | Rẻ nhất |
| Paint + composite | `box-shadow`, `border-radius`, `color` | Vẽ lại mỗi khung |
| Layout + paint + composite | `width`, `height`, `padding`, `margin`, `top`, `left`, `border-width` | Đắt nhất; một phần tử lớn lên đẩy mọi thứ xung quanh |

Hạ bậc:

| Thay vì | Animate |
|---|---|
| `width`/`height`/`padding` để to nhỏ | `scale()` |
| `top`/`left`/`margin` để di chuyển | `translate()` |
| Đổi `display`/`visibility` | `opacity` |
| `box-shadow` | `filter: drop-shadow(…)` |

Animate `margin-left` của sidebar đẩy nội dung bên cạnh mỗi khung; `translateX` thì không.

## Chạy ở đâu

JavaScript luôn chạy trên luồng chính. Animation dùng `requestAnimationFrame` (GSAP, component `motion/react`) cạnh tranh với mọi thứ khác trình duyệt đang làm. CSS transition, keyframes và Web Animations API (`element.animate()`) có thể chạy ngoài luồng chính.

Chú ý **chuyển động chạy trong lúc trang làm việc nặng**: chuyển trang, chỉ báo tab khi điều hướng, thứ gì chạy cùng lúc tải dữ liệu hay hydration. Ở Vercel, chỉ báo tab của dashboard dùng Shared Layout Animation và rớt khung khi tải trang; chuyển sang CSS thì hết.

```jsx
<motion.div animate={{ x: 100 }} />                          // luồng chính, có thể giật
<motion.div animate={{ transform: "translateX(100px)" }} />  // có thể tăng tốc phần cứng
```

```js
// WAAPI: điều khiển bằng JS, hiệu năng như CSS, không cần thư viện
element.animate([{ clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0 0)' }],
  { duration: 1000, fill: 'forwards', easing: 'cubic-bezier(0.77, 0, 0.175, 1)' });
```

**Chia việc:** CSS cho chuyển động đơn giản và mọi thứ chạy khi trang đang bận; Motion (Framer Motion) cho chuyển động phức tạp, ngắt được, theo cử chỉ (spring thật, layout animation, animation khi unmount).

## Hai cái bẫy trông có vẻ đúng

**Biến CSS kế thừa.** Thao tác kéo của Vaul chậm dần khi drawer có hơn khoảng 20 mục, dù không re-render. Khoảng cách kéo được ghi vào một biến CSS mà `translateY()` đọc. Biến CSS kế thừa, nên đổi nó trên cha làm tính lại style cho mọi con.

```js
element.style.setProperty('--swipe-amount', `${d}px`); // tính lại cho mọi phần tử con
element.style.transform = `translateY(${d}px)`;        // chỉ phần tử này
```

**Blur.** `filter: blur()` đắt rất nhanh, nhất là Safari. Dưới 20px; 2–5px là đủ làm mềm chuyển cảnh.

## React: đừng animate qua state

```jsx
setY(nextY);                                          // một lần re-render mỗi khung: rớt khung
ref.current.style.transform = `translateY(${nextY}px)`; // không re-render
```

Tìm cập nhật state bên trong `requestAnimationFrame`, `pointermove`, `scroll` hay handler kéo.

## `will-change`

Bước cuối cùng, không phải bước đầu. Chỉ thêm khi đã thấy lệch pixel hoặc đo được rớt khung, chỉ trên phần tử đang animate, gỡ ra sau đó. Mỗi lớp được nâng tốn bộ nhớ GPU.

## Quy trình chẩn đoán

1. Liệt kê mọi animation trong phạm vi: phần tử, công cụ chạy, thuộc tính, chạy lúc nào. Khai triển `transition: all` và shorthand của Motion thành thuộc tính thật.
2. Đi xuống danh sách theo tần suất là nguyên nhân: thuộc tính nào được animate → có trùng lúc trang bận không → React có re-render mỗi khung không → có tệ hơn khi nội dung tăng không → có animate biến CSS không → có blur trên 20px không → vẫn lệch thì mới `will-change`.
3. Xác nhận bằng ghi hình (bảng Performance của DevTools), không bằng cảm giác. Profile trên điện thoại tầm trung qua remote debugging.
4. Báo cáo mỗi phát hiện: phần tử và vị trí file, nguyên nhân, trước, sau, đã kiểm tra từ code hay cần ghi hình thiết bị.

---

# Phần B. Cảm giác "ứng dụng thật" trên điện thoại

| Vấn đề | Cách sửa |
|---|---|
| Hover dính lại sau khi chạm | Bọc trong `@media (hover: hover) and (pointer: fine)` |
| Nháy xám/xanh khi chạm | `-webkit-tap-highlight-color: transparent` |
| Chiều cao bố cục sai | `100dvh` (khung ứng dụng) hoặc `100svh` (hero) |
| Trang tự phóng to khi gõ vào ô nhập | Ô nhập tối thiểu 16px |
| Chạm có cảm giác trễ | Phản hồi ngay lúc `pointerdown`/`:active` + `touch-action: manipulation` |
| Kéo để làm mới cướp mất thao tác cuộn | `overscroll-behavior: none` trên `html, body` |
| Nội dung bị tai thỏ che | `viewport-fit=cover` + `env(safe-area-inset-*)` |
| Nhấn giữ bôi đen chữ trên nút | `user-select: none` chỉ trên điều khiển |
| Carousel cuộn theo chiều dọc | `touch-action: pan-y` trên vùng cử chỉ |
| Màu thanh trạng thái không khớp | `theme-color` cho từng chế độ màu |
| Đúng trên Chrome, sai trên điện thoại | Thử trên thiết bị thật |

## Nền tảng

Đặt trước component đầu tiên của mọi trang hướng tới điện thoại:

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content" />
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#ffffff" />
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0a0a0a" />
```

```css
html {
  -webkit-tap-highlight-color: transparent;
  -webkit-text-size-adjust: 100%;
  overscroll-behavior: none; /* bỏ dòng này nếu là trang tài liệu cuộn dài, nơi kéo để làm mới là bình thường */
}
input, textarea, select { font-size: 16px; }
button, a, [role="button"] {
  touch-action: manipulation;
  user-select: none;
  -webkit-user-select: none;
}
@media (hover: hover) and (pointer: fine) {
  /* mọi quy tắc :hover nằm ở đây */
}
```

Đổi `theme-color` theo màu nền thật của trang. `interactive-widget=resizes-content` làm bàn phím ảo co vùng nhìn trên Chrome Android, để `100dvh` và ô nhập ghim đáy phản ứng giống iOS.

## Không bao giờ ship

| Không bao giờ | Thay bằng |
|---|---|
| `user-scalable=no` hoặc `maximum-scale=1` | Ô nhập 16px, sửa đúng nguyên nhân |
| `:hover` không bọc media query | `@media (hover: hover) and (pointer: fine)` |
| `100vh` cho khung ứng dụng hay UI ghim đáy | `100dvh` |
| `100dvh` cho hero trang marketing | `100svh` (không nhảy khi cuộn) |
| Phản hồi nhấn chỉ ở sự kiện `click` | `:active` / `pointerdown` |
| `touchmove` + `preventDefault()` để chặn kéo quá | `overscroll-behavior` |
| `user-select: none` trên `body` | Chỉ trên điều khiển |
| `touch-action: none` trên thứ người dùng cần cuộn qua | `pan-x` / `pan-y` |
| `env(safe-area-inset-*)` thiếu `viewport-fit=cover` | Thêm thẻ meta, nếu không giá trị bằng 0 |
| Một `theme-color` cho cả hai chế độ | Mỗi chế độ một cái |
| Đoán thiết bị cảm ứng từ user-agent | Media query `(hover)` / `(pointer)` |
| Tuyên bố đã sửa chỉ từ giả lập thiết bị | Thiết bị thật |

Thử trên thiết bị thật: kết nối điện thoại cùng mạng, mở dev server bằng địa chỉ IP của máy, dùng Safari remote devtools hoặc `chrome://inspect`.

---

# Phần C. Hiệu năng chung (kiểm tra)

- Ảnh có `width`, `height`, `loading="lazy"` (trừ ảnh hero, ảnh hero có `fetchpriority="high"`), định dạng hiện đại (AVIF/WebP) và kích thước phù hợp (`srcset`).
- Không đọc rồi ghi thuộc tính bố cục xen kẽ trong vòng lặp.
- Không nhập thư viện cả gói cho một hàm; không phụ thuộc thừa.
- Font: chỉ độ đậm đang dùng, `font-display: swap`, preload font tiêu đề.
- Vòng lặp và video dừng khi ra khỏi màn hình hoặc tab ẩn.
- Không preloader. Trang đọc được ngay.
