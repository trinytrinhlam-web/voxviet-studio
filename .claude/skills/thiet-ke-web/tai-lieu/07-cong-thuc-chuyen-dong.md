# Công thức chuyển động

Code ở đây đã được kiểm chứng: phần lớn lấy nguyên từ taste-skill (giấy phép MIT, xem `NGUON.md`), phần giải thích viết lại bằng tiếng Việt, một số công thức tự viết thêm cho những hiệu ứng mà bản gốc chỉ mô tả bằng lời. Tất cả dùng token trong `06-chuyen-dong.md` (`--ease-out`, `--ease-expo`, `--t-press`...).

Ba quy ước áp dụng cho mọi công thức:

1. **Nội dung luôn hiện khi JavaScript tắt.** Trạng thái ẩn chỉ áp dụng dưới lớp `html.js`, do một dòng script đặt ngay đầu trang:

```html
<script>document.documentElement.classList.add('js')</script>
```

2. **Mọi trạng thái ẩn nằm trong `@media (prefers-reduced-motion: no-preference)`.** Nhờ vậy, với người dùng bật giảm chuyển động, trang đã hoàn chỉnh ngay từ đầu.
3. **Chuyển động gắn với thanh cuộn thì dùng `linear`.** Chính thanh cuộn là đường cong. Và `animation-timeline: view()` lấy vùng cuộn gần nhất; `overflow: hidden` tạo ra một vùng cuộn mới nên ảnh bên trong sẽ không bao giờ chạy. Dùng `overflow: clip` cho khung ảnh.

## Mục lục

**Giao diện (Emil):** nút bấm và hover · menu, popover · tooltip · toast · accordion · nhấn giữ để xóa · tab đổi màu mượt · danh sách so le · làm mờ để che chỗ chuyển cảnh

**Trang quảng bá (taste-skill):** chuỗi mở trang 1,2 giây · tiêu đề trồi từ mặt nạ · lộ diện khi cuộn · ảnh mở như cửa chớp · chữ khổng lồ co giãn theo cuộn · câu chuyện ghim · danh mục có ảnh xem trước · các dòng trồi khi cuộn · cửa sổ mở rộng · ảnh đứng yên, chú thích trôi qua · thư viện ảnh trượt ngang · hero lùi xa · chuyển trang · tô mực theo cuộn · số cuộn lên

**Tự viết thêm:** footer như tấm màn · ảnh chuyển dần · băng chữ chạy · hàng kéo ngang · màu theo chương · tờ giấy phủ lên ảnh · dòng chữ bị đẩy · tĩnh lặng

Tra cứu theo mã hiệu ứng chủ đạo mà `rut-huong.mjs` đưa ra:

| Mã | Công thức |
|---|---|
| `masked-headline` | Tiêu đề trồi từ mặt nạ (kèm chuỗi mở trang) |
| `shutter-image` | Ảnh mở như cửa chớp |
| `scaling-wordmark` | Chữ khổng lồ co giãn theo cuộn |
| `pinned-story` | Câu chuyện ghim, hoặc Ảnh đứng yên, chú thích trôi qua |
| `index-preview` | Danh mục có ảnh xem trước |
| `curtain-footer` | Footer như tấm màn |
| `slow-crossfade` | Ảnh chuyển dần |
| `edge-marquee` | Băng chữ chạy |
| `drag-row` | Hàng kéo ngang |
| `colour-on-scroll` | Màu theo chương |
| `stillness` | Tĩnh lặng |
| `opening-window` | Cửa sổ mở rộng |
| `ink-fill` | Tô mực theo cuộn |
| `sheet-over` | Tờ giấy phủ lên ảnh |
| `sideways-gallery` | Thư viện ảnh trượt ngang |
| `pushed-line` | Dòng chữ bị đẩy |
| `rolling-figures` | Số cuộn lên |
| `carried-picture` | Chuyển trang |

---

# Phần A. Giao diện

## Nút bấm và hover

Nút phải "nghe" được tay người dùng: co lại 3% khi nhấn. Hover chỉ đặt sau `(hover: hover) and (pointer: fine)`, vì trên điện thoại chạm vào sẽ kích hoạt hover và để nó dính lại. Hover phải làm tăng tương phản, không làm giảm. Không đổi độ đậm chữ khi hover (dòng chữ sẽ nhảy). Không làm mọi thẻ nổi lên hay phóng to khi hover.

```css
.button { transition: transform var(--t-press) var(--ease-out), background-color var(--t-hover) ease, color var(--t-hover) ease; }
.button:active { transform: scale(0.97); }
.link { text-decoration: underline; text-decoration-color: transparent; text-underline-offset: 0.2em; text-decoration-thickness: 0.07em; transition: text-decoration-color var(--t-hover) ease; }
@media (hover: hover) and (pointer: fine) {
  .button:hover { background-color: var(--accent-strong); }
  .link:hover { text-decoration-color: currentColor; }
}
```

## Menu, popover, dialog

Mọi thứ mở ra từ chỗ nó được bấm (`transform-origin` đặt tại nút kích hoạt). Không bao giờ xuất hiện từ `scale(0)`; bắt đầu từ 0.95–0.98. Dialog ở giữa màn hình là ngoại lệ duy nhất được scale từ tâm.

```css
.menu { transform-origin: top right; transition: opacity var(--t-ui) var(--ease-out), transform var(--t-ui) var(--ease-out); }
.menu[hidden], .menu.is-closed { opacity: 0; transform: scale(0.97) translateY(-6px); pointer-events: none; }
```

Với Radix hoặc Base UI, dùng biến có sẵn: `transform-origin: var(--radix-popover-content-transform-origin)` hoặc `var(--transform-origin)`.

## Tooltip: bỏ độ trễ ở lần hover sau

Tooltip đầu tiên nên trễ một chút để tránh bật nhầm. Nhưng khi một tooltip đã mở, rê sang tooltip bên cạnh phải mở ngay, không animation. Thanh công cụ sẽ có cảm giác nhanh hơn hẳn.

```css
.tooltip {
  transition: transform 125ms var(--ease-out), opacity 125ms var(--ease-out);
  transform-origin: var(--transform-origin);
}
.tooltip[data-starting-style],
.tooltip[data-ending-style] { opacity: 0; transform: scale(0.97); }
.tooltip[data-instant] { transition-duration: 0ms; }
```

## Toast (cách của Sonner)

Dùng `transition` chứ không dùng `@keyframes`: toast được thêm liên tục, keyframes bị ngắt sẽ chạy lại từ đầu, còn transition thì đổi hướng mượt. `translateY(100%)` dịch theo đúng chiều cao của chính nó, nên không cần đo. Toast vào và ra cùng một hướng để thao tác vuốt bỏ có cảm giác tự nhiên. Tạm dừng bộ đếm giờ khi tab bị ẩn.

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

Trình duyệt chưa hỗ trợ `@starting-style` thì dùng thuộc tính `data-mounted` đặt sau lần render đầu.

Nếu dự án dùng React và cần toast, dùng thư viện Sonner thay vì tự viết.

## Accordion

Animate `grid-template-rows` từ `0fr` lên `1fr` để mở đúng chiều cao nội dung mà không cần JavaScript đo. Đây là ngoại lệ được chấp nhận của luật "không animate thuộc tính bố cục", vì nó ngắn và hiếm.

```css
.acc__panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows 320ms var(--ease-out); }
.acc__panel > div { overflow: hidden; }
.acc[open] .acc__panel, .acc__item.is-open .acc__panel { grid-template-rows: 1fr; }
```

## Nhấn giữ để xóa

Thời gian không đối xứng: chậm ở chỗ người dùng đang quyết định, nhanh ở chỗ hệ thống phản hồi. Nhấn giữ 2 giây tuyến tính; thả tay thì rút về trong 200ms.

```css
.hold { position: relative; transition: transform 160ms var(--ease-out); }
.hold:active { transform: scale(0.97); }
.hold__overlay {
  position: absolute; inset: 0;
  background: var(--danger);
  clip-path: inset(0 100% 0 0);
  transition: clip-path 200ms var(--ease-out);
}
.hold:active .hold__overlay {
  clip-path: inset(0 0 0 0);
  transition: clip-path 2s linear;
}
```

Gắn hành động xóa vào sự kiện `transitionend` của lớp phủ khi nó đã phủ kín.

## Tab đổi màu mượt

Nhân đôi danh sách tab. Bản sao được tô kiểu "đang chọn" (nền và màu chữ khác), đặt chồng lên bản gốc, và dùng `clip-path: inset(...)` để chỉ lộ đúng tab đang chọn. Khi đổi tab, animate giá trị `clip-path`. Màu chữ chuyển mượt tuyệt đối mà không cần canh thời gian cho từng màu.

```css
.tabs { position: relative; }
.tabs__active {
  position: absolute; inset: 0;
  pointer-events: none;
  clip-path: inset(0 var(--right) 0 var(--left) round 999px);
  transition: clip-path 250ms var(--ease-out);
}
```

```js
function selectTab(tab, list, overlay) {
  const l = tab.offsetLeft, r = list.offsetWidth - (l + tab.offsetWidth);
  overlay.style.setProperty('--left', l + 'px');
  overlay.style.setProperty('--right', r + 'px');
}
```

## Danh sách so le

Các phần tử vào cùng lúc thì so le nhau 30–80ms (giao diện) hoặc 50–90ms (trang quảng bá). Không bao giờ chặn tương tác trong lúc so le đang chạy.

```css
@media (prefers-reduced-motion: no-preference) {
  .js .stagger > * {
    opacity: 0; transform: translateY(8px);
    animation: stagger-in 300ms var(--ease-out) forwards;
    animation-delay: calc(var(--i, 0) * 50ms);
  }
}
@keyframes stagger-in { to { opacity: 1; transform: none; } }
```

Đặt `style="--i:0"`, `--i:1`... cho từng phần tử. Tối đa 4 bước trong một chuỗi trên trang quảng bá.

## Làm mờ để che chỗ chuyển cảnh

Khi hiệu ứng mờ dần giữa hai trạng thái vẫn trông như hai vật chồng lên nhau dù đã chỉnh easing, thêm `filter: blur(2px)` trong lúc chuyển. Giữ blur dưới 20px (tốn tài nguyên, nhất là Safari); 2–5px là đủ.

```css
.button-content { transition: filter 200ms ease, opacity 200ms ease; }
.button-content.is-changing { filter: blur(2px); opacity: 0.7; }
```

---

# Phần B. Trang quảng bá

Ngân sách chuyển động cho trang Persuade nằm ở `06-chuyen-dong.md`. Nhắc lại: một hiệu ứng chủ đạo, xuất hiện theo từng phần của mỗi section, phản hồi trên mọi nút, và một hình ảnh chuyển động.

## Chuỗi mở trang trong 1,2 giây

Mọi thứ có sẵn trong HTML và hiện ngay khung hình đầu; chuỗi này chỉ thêm cảm giác "đến nơi". Không chờ sự kiện load, không animate thanh điều hướng. Tối đa bốn thứ chuyển động, xong hết trước 1,2 giây.

> **Tiếng Việt:** mặt nạ (`overflow: hidden/clip`) cắt cả phía trên lẫn phía dưới. Bản gốc chỉ chừa chỗ cho đuôi chữ (g, y, p); code dưới đây đã sửa ở hai chỗ: chừa thêm chỗ cho dấu chồng phía trên (Ế, Ỗ, Ặ, Ữ), và ở trạng thái ẩn dịch chữ xuống `calc(100% + 0.45em)` thay vì 105% để phần dấu không lơ lửng trong mặt nạ trước khi chữ trồi lên. Luôn chụp màn hình kiểm tra một tiêu đề có chữ hoa mang dấu chồng.

```html
<header class="hero">
  <h1 class="display lines">
    <span class="line"><span data-line style="--i:0">Stools for</span></span>
    <span class="line"><span data-line style="--i:1">small kitchens</span></span>
  </h1>
  <p class="lead" data-load style="--d:420ms">…</p>
  <a class="button" data-load style="--d:480ms" href="#stools">See the stools</a>
  <figure class="hero__picture" data-open><img src="stool.jpg" alt="…" fetchpriority="high"></figure>
</header>
```

```css
.hero__picture { overflow: clip; margin: 0; }
@media (prefers-reduced-motion: no-preference) {
  .js .hero [data-line] { transform: translateY(calc(100% + 0.45em)); animation: load-line 800ms var(--ease-expo) forwards; animation-delay: calc(100ms + var(--i) * var(--stagger-line)); }
  .js .hero [data-load] { opacity: 0; transform: translateY(12px); animation: load-rise 500ms var(--ease-out) forwards; animation-delay: var(--d); }
  .js .hero [data-open] { clip-path: inset(0 0 100% 0); animation: load-open 1000ms var(--ease-in-out) 150ms forwards; }
  .js .hero [data-open] img { transform: scale(1.08); animation: load-settle 1100ms var(--ease-expo) 100ms forwards; }
}
@keyframes load-line { to { transform: none; } }
@keyframes load-rise { to { opacity: 1; transform: none; } }
@keyframes load-open { to { clip-path: inset(0); } }
@keyframes load-settle { to { transform: none; } }
```

Dòng tiêu đề trồi từ 100 đến 990ms, ảnh mở từ 150 đến 1150ms, câu phụ và nút đến từ 420 đến 980ms. Preload font tiêu đề (`<link rel="preload" as="font" type="font/woff2" crossorigin>`) để chữ trồi lên đúng mặt chữ thật. Đặt `fetchpriority="high"` cho ảnh hero và cho khung ảnh một màu nền lấy từ chính ảnh, để ảnh tải chậm mở ra trên màu của nó thay vì một ô trắng.

## Tiêu đề trồi từ mặt nạ (`masked-headline`)

Mỗi dòng trồi lên từ sau đường chân chữ của nó. Vì tiêu đề tối đa hai dòng, bạn tự ngắt dòng và bọc từng dòng.

> **Tiếng Việt:** mặt nạ (`overflow: hidden/clip`) cắt cả phía trên lẫn phía dưới. Bản gốc chỉ chừa chỗ cho đuôi chữ (g, y, p); code dưới đây đã sửa ở hai chỗ: chừa thêm chỗ cho dấu chồng phía trên (Ế, Ỗ, Ặ, Ữ), và ở trạng thái ẩn dịch chữ xuống `calc(100% + 0.45em)` thay vì 105% để phần dấu không lơ lửng trong mặt nạ trước khi chữ trồi lên. Luôn chụp màn hình kiểm tra một tiêu đề có chữ hoa mang dấu chồng.

```html
<h1 class="lines">
  <span class="line"><span data-line style="--i:0">Stools for</span></span>
  <span class="line"><span data-line style="--i:1">small kitchens</span></span>
</h1>
```

```css
.lines .line { display: block; overflow: hidden; padding-block: 0.18em 0.1em; margin-block: -0.18em -0.1em; }
.lines [data-line] { display: block; }
@media (prefers-reduced-motion: no-preference) {
  .js .lines [data-line] {
    transform: translateY(calc(100% + 0.45em));
    animation: line-up 900ms var(--ease-out) forwards;
    animation-delay: calc(var(--i) * 110ms + 150ms);
  }
}
@keyframes line-up { to { transform: none; } }
```

Trên điện thoại hẹp, hai dòng tự ngắt có thể lại xuống dòng. Kiểm tra ảnh chụp màn hình điện thoại; nếu bị, dùng `<br class="chi-man-rong">` ẩn đi dưới một breakpoint, hoặc rút ngắn tiêu đề.

## Lộ diện khi cuộn (một lần)

Chỉ cho hai, ba section thực sự đáng, không phải mọi khối.

```css
@media (prefers-reduced-motion: no-preference) {
  .js [data-reveal] { opacity: 0; transform: translateY(24px); transition: opacity 700ms var(--ease-out), transform 900ms var(--ease-out); }
  .js [data-reveal].is-in { opacity: 1; transform: none; }
}
```

```js
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
}, { rootMargin: '0px 0px -12% 0px', threshold: 0.1 });
document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el));
```

Không bao giờ gắn lộ diện vào sự kiện `scroll`, không chạy lại khi phần tử quay vào màn hình, và không để thứ gì kẹt ở `opacity: 0` nếu observer không chạy (lớp `html.js` lo trường hợp tắt JS; `unobserve` lo việc chạy lại).

## Ảnh mở như cửa chớp (`shutter-image`)

Ảnh mở ra từ một cạnh trong khi bên trong thu nhẹ về kích thước thật. Chỉ dùng cho một ảnh quan trọng nhất (hero hoặc showcase).

```css
.shutter { overflow: hidden; }
@media (prefers-reduced-motion: no-preference) {
  .js .shutter { clip-path: inset(0 0 100% 0); transition: clip-path 1100ms var(--ease-in-out); }
  .js .shutter img { transform: scale(1.12); transition: transform 1500ms var(--ease-soft); }
  .js .shutter.is-in { clip-path: inset(0); }
  .js .shutter.is-in img { transform: none; }
}
```

## Chữ khổng lồ co giãn theo cuộn (`scaling-wordmark`) và chuyển động gắn thanh cuộn

Cho tên thương hiệu cỡ lớn co nhẹ khi hero rời màn hình, một ảnh trôi vài phần trăm, hoặc thanh tiến trình. Bọc trong `@supports` để trình duyệt không hỗ trợ giữ nguyên trạng thái tĩnh. Quãng di chuyển dưới 8% kích thước phần tử; tỉ lệ scale trong khoảng 0.94–1.15.

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .drift { animation: drift linear both; animation-timeline: view(); animation-range: entry 0% exit 100%; }
    @keyframes drift { from { transform: translateY(-4%); } to { transform: translateY(4%); } }
  }
}
```

Với chữ khổng lồ, thay keyframes bằng `from { transform: scale(1); } to { transform: scale(0.94); }` và đặt `transform-origin: bottom left`.

## Câu chuyện ghim (`pinned-story`)

Tiêu đề giữ nguyên chỗ trong khi các mục trôi qua. Dùng `position: sticky`; không chiếm quyền cuộn. Khoảng một màn hình mỗi bước, tối đa ba màn hình.

```css
.story { display: grid; grid-template-columns: 5fr 7fr; gap: var(--gutter); align-items: start; }
.story__title { position: sticky; top: 18vh; }
@media (max-width: 800px) { .story { grid-template-columns: 1fr; } .story__title { position: static; } }
```

## Ảnh đứng yên, chú thích trôi qua

Phiên bản câu chuyện ghim dành cho ảnh: ảnh giữ một bên, các chú thích ngắn trôi qua bên kia; chú thích ở giữa màn hình được làm sáng và ảnh tương ứng hiện ra. Mục không hoạt động mờ đi nhưng không dưới 40% (thấp hơn trông như chữ bị thiếu). Có dãy hơn hai bước thì hiện số đếm bằng chữ thường ("2 trên 4"), không dùng số có số 0 đứng đầu.

```html
<section class="steps">
  <figure class="steps__media">
    <div class="steps__pictures">
      <img src="seasoning.jpg" alt="Ash boards stacked to season" class="is-on">
      <img src="turning.jpg" alt="A leg being turned on the lathe">
      <img src="finish.jpg" alt="Oil rubbed into a finished seat">
    </div>
    <figcaption class="steps__count" aria-hidden="true"></figcaption>
  </figure>
  <ol class="steps__list">
    <li class="steps__item"><h3>Seasoned for a year</h3><p>…</p></li>
    <li class="steps__item"><h3>Turned by hand</h3><p>…</p></li>
    <li class="steps__item"><h3>Finished with oil</h3><p>…</p></li>
  </ol>
</section>
```

```css
.steps { display: grid; grid-template-columns: 7fr 5fr; column-gap: var(--gutter); }
.steps__media { margin: 0; align-self: start; }           /* a stretched grid item cannot stick */
.steps__pictures img { display: block; width: 100%; height: auto; }
.steps__list { list-style: none; margin: 0; padding: 0; }
.steps__item { min-height: 80svh; display: flex; flex-direction: column; justify-content: center; }
.js .steps__media { position: sticky; top: 0; height: 100svh; display: flex; flex-direction: column; justify-content: center; gap: 0.75rem; }
.js .steps__pictures { position: relative; aspect-ratio: 4 / 5; max-height: 80svh; }
.js .steps__pictures img { position: absolute; inset: 0; height: 100%; object-fit: cover; opacity: 0; transition: opacity 500ms ease; }
.js .steps__pictures img.is-on { opacity: 1; }
.js .steps__item { opacity: 0.4; transition: opacity var(--t-ui) ease; }
.js .steps__item.is-active { opacity: 1; }
@media (max-width: 800px) {
  .steps { display: block; }                               /* the section, not a grid area, contains the sticky picture */
  .js .steps__media { height: auto; z-index: 1; background: var(--bg); padding-block: 0.5rem; }
  .js .steps__pictures { aspect-ratio: 3 / 2; max-height: 42svh; }
  .steps__item { min-height: 60svh; }
}
@media (prefers-reduced-motion: reduce) { .js .steps__pictures img, .js .steps__item { transition: none; } }
```

```js
(() => {
  const root = document.querySelector('.steps');
  if (!root || !('IntersectionObserver' in window)) return;
  const items = [...root.querySelectorAll('.steps__item')];
  const pictures = [...root.querySelectorAll('.steps__pictures img')];
  const count = root.querySelector('.steps__count');
  const show = (i) => {
    items.forEach((el, k) => el.classList.toggle('is-active', k === i));
    pictures.forEach((el, k) => el.classList.toggle('is-on', k === i));
    if (count) count.textContent = `${i + 1} of ${items.length}`;
  };
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) show(items.indexOf(e.target));
  }, { rootMargin: '-45% 0px -45% 0px' });                 // a band across the middle of the screen
  items.forEach((el) => io.observe(el));
  show(0);
})();
```

## Danh mục có ảnh xem trước (`index-preview`)

Các dòng tên là lối điều hướng qua tác phẩm. Rê chuột hoặc Tab vào một dòng thì mở một khung ảnh ngang hàng với dòng đó. Khung đi theo dòng, không đi theo con trỏ. Trên màn hình cảm ứng, mỗi dòng hiện ảnh của nó ngay phía trên tên.

```html
<section class="index">
  <ul class="index__list">
    <li><a class="index__row" href="/work/harbour-house" data-preview="/img/harbour-house.jpg">
      <span class="index__name">Harbour House</span><span class="index__year">2025</span>
      <img class="index__thumb" src="/img/harbour-house-small.jpg" alt="" loading="lazy" width="640" height="400">
    </a></li>
    <!-- … -->
  </ul>
  <div class="index__frame" aria-hidden="true"><img alt=""></div>
</section>
```

```css
.index { position: relative; }
.index__list { list-style: none; margin: 0; padding: 0; }
.index__row { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 0 var(--gutter); padding-block: 0.3em; font-size: var(--step-head); color: inherit; text-decoration: none; transition: opacity var(--t-hover) ease; }
.index__thumb { order: -1; flex-basis: 100%; width: 100%; height: auto; margin-bottom: 0.4rem; }
.index__frame { display: none; }
@media (hover: hover) and (pointer: fine) {
  .index__list { max-width: 62%; }
  .index__thumb { display: none; }
  .index__list:has(.index__row:hover, .index__row:focus-visible) .index__row:not(:hover, :focus-visible) { opacity: 0.4; }
  .index__frame { display: block; position: absolute; top: 0; right: var(--margin); width: 30%; aspect-ratio: 4 / 3; z-index: 1; pointer-events: none; clip-path: inset(100% 0 0 0); transition: clip-path 320ms var(--ease-out), transform 360ms var(--ease-out); }
  .index__frame.is-open { clip-path: inset(0); }
  .index__frame img { width: 100%; height: 100%; object-fit: cover; }
}
@media (prefers-reduced-motion: reduce) { .index__frame { transition: none; } }
```

```js
(() => {
  const root = document.querySelector('.index');
  if (!root) return;
  const frame = root.querySelector('.index__frame');
  const picture = frame.querySelector('img');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  let warmed = false;
  const show = (row) => {
    if (!fine.matches) return;
    if (!warmed) { warmed = true; root.querySelectorAll('[data-preview]').forEach((a) => { new Image().src = a.dataset.preview; }); }
    picture.src = row.dataset.preview;
    const y = row.offsetTop + row.offsetHeight / 2 - frame.offsetHeight / 2;
    const max = root.offsetHeight - frame.offsetHeight;
    const opening = !frame.classList.contains('is-open');
    if (opening) frame.style.transitionProperty = 'clip-path';   // open in place, do not slide in from the top
    frame.style.transform = `translateY(${Math.min(max, Math.max(0, y))}px)`;
    if (opening) { frame.getBoundingClientRect(); frame.style.transitionProperty = ''; }
    frame.classList.add('is-open');
  };
  const hide = () => frame.classList.remove('is-open');
  root.querySelectorAll('.index__row').forEach((row) => {
    row.addEventListener('pointerenter', () => show(row));
    row.addEventListener('focus', () => show(row));
  });
  root.addEventListener('pointerleave', hide);
  root.addEventListener('focusout', (e) => { if (!root.contains(e.relatedTarget)) hide(); });
})();
```

## Các dòng trồi khi cuộn

Cho tiêu đề section hoặc câu tuyên ngôn mà bạn không kiểm soát được chỗ ngắt dòng. Tách dòng sau khi font tải xong, lộ diện một lần, rồi trả lại chữ nguyên gốc để nó tự xuống dòng bình thường. Chỉ dùng cho chữ thuần (không có link hay nhấn mạnh bên trong).

> **Tiếng Việt:** mặt nạ (`overflow: hidden/clip`) cắt cả phía trên lẫn phía dưới. Bản gốc chỉ chừa chỗ cho đuôi chữ (g, y, p); code dưới đây đã sửa ở hai chỗ: chừa thêm chỗ cho dấu chồng phía trên (Ế, Ỗ, Ặ, Ữ), và ở trạng thái ẩn dịch chữ xuống `calc(100% + 0.45em)` thay vì 105% để phần dấu không lơ lửng trong mặt nạ trước khi chữ trồi lên. Luôn chụp màn hình kiểm tra một tiêu đề có chữ hoa mang dấu chồng.

```html
<h2 class="head" data-lines>Turned by hand in one small workshop</h2>
```

```css
[data-lines] .line { display: block; overflow: clip; padding-block: 0.18em 0.12em; margin-block: -0.18em -0.12em; }
[data-lines] .line > span { display: block; }
@media (prefers-reduced-motion: no-preference) {
  .is-split .line > span { transform: translateY(calc(100% + 0.45em)); }
  .is-split.is-in .line > span { transform: none; transition: transform 900ms var(--ease-expo) calc(var(--i) * var(--stagger-line)); }
}
```

```js
(() => {
  const els = [...document.querySelectorAll('[data-lines]')];
  if (!els.length || !('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const restore = (el) => { el.textContent = el.dataset.text; el.classList.remove('is-split', 'is-in'); };
  const split = (el) => {
    const text = el.textContent.trim().replace(/\s+/g, ' ');
    el.dataset.text = text;
    el.textContent = '';
    const words = text.split(' ').map((word) => {
      const s = document.createElement('span');
      s.style.display = 'inline-block';
      s.textContent = word;
      el.append(s, ' ');
      return s;
    });
    const lines = [];                                   // group the words by the line they landed on
    for (const w of words) {
      const last = lines.at(-1);
      if (last && Math.abs(last.top - w.offsetTop) < 4) last.words.push(w.textContent);
      else lines.push({ top: w.offsetTop, words: [w.textContent] });
    }
    el.textContent = '';
    lines.forEach((line, i) => {
      const mask = document.createElement('span');
      const inner = document.createElement('span');
      mask.className = 'line';
      inner.style.setProperty('--i', i);
      inner.textContent = line.words.join(' ');
      mask.append(inner);
      el.append(mask, ' ');
    });
    el.classList.add('is-split');
  };
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      io.unobserve(e.target);
      e.target.classList.add('is-in');
      e.target.querySelector('.line:last-of-type > span')
        .addEventListener('transitionend', () => restore(e.target), { once: true });
    }
  }, { rootMargin: '0px 0px -12% 0px' });
  document.fonts.ready.then(() => els.forEach((el) => { split(el); io.observe(el); }));
  let width = innerWidth;                               // a width change before the reveal: give the text back
  addEventListener('resize', () => {
    if (innerWidth === width) return;
    width = innerWidth;
    els.filter((el) => el.matches('.is-split:not(.is-in)')).forEach((el) => { io.unobserve(el); restore(el); });
  });
})();
```

## Cửa sổ mở rộng (`opening-window`)

Chuyển giao từ một màn hình toàn chữ sang bức ảnh lớn: ảnh ban đầu hiện như một ô cửa sổ giữa sân khấu được giữ, rồi mở ra tràn viền trong khoảng một màn hình cuộn.

```html
<section class="opening">
  <div class="opening__stage">
    <img src="workshop-wide.jpg" alt="The workshop at first light, benches cleared" width="2400" height="1500">
  </div>
</section>
```

```css
.opening__stage { height: 100svh; overflow: clip; }
.opening__stage img { display: block; width: 100%; height: 100%; object-fit: cover; }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .opening { height: 200svh; view-timeline-name: --opening; --inset-y: 20%; --inset-x: 28%; }
    .opening__stage { position: sticky; top: 0; animation: opening-window linear both; animation-timeline: --opening; animation-range: contain 0% contain 75%; }
    .opening__stage img { animation: opening-settle linear both; animation-timeline: --opening; animation-range: contain 0% contain 75%; }
  }
}
@media (max-width: 700px) { .opening { --inset-y: 18%; --inset-x: 8%; } }
@keyframes opening-window { from { clip-path: inset(var(--inset-y) var(--inset-x)); } to { clip-path: inset(0); } }
@keyframes opening-settle { from { transform: scale(1.15); } to { transform: none; } }
```

Section cao hai màn hình; sân khấu được giữ một màn hình và cửa sổ mở hết ở ba phần tư quãng đó, để ảnh tràn viền dừng lại một chút trước khi trang đi tiếp. Không hỗ trợ scroll timeline hoặc khi giảm chuyển động: ảnh là một màn hình tràn viền bình thường.

## Thư viện ảnh trượt ngang (`sideways-gallery`)

Một hàng ảnh ngắn (tối đa tám) trượt ngang trong khi cuộn dọc giữ sân khấu. Nền tảng là hàng kéo ngang gốc của trình duyệt; bản ghim chỉ thêm trên màn hình rộng, khi cho phép chuyển động, và khi hàng ngắn hơn ba màn hình.

```html
<section class="gallery">
  <div class="gallery__stage">
    <h2 class="head">Eight kitchens, one stool</h2>
    <ul class="gallery__track">
      <li class="gallery__item"><a href="/kitchens/leith"><img src="leith.jpg" alt="A narrow galley kitchen in Leith" width="1200" height="1500"><span>Leith</span></a></li>
      <!-- … -->
    </ul>
  </div>
</section>
```

```css
.gallery__track { display: flex; gap: var(--gutter); list-style: none; margin: 0; padding: 0 var(--margin); overflow-x: auto; scroll-snap-type: x mandatory; scroll-padding-inline: var(--margin); }
.gallery__item { flex: 0 0 min(72vw, 28rem); scroll-snap-align: start; }
.gallery__item img { display: block; width: 100%; height: auto; aspect-ratio: 4 / 5; object-fit: cover; }
.gallery.is-pinned .gallery__stage { position: sticky; top: 0; height: 100svh; display: flex; flex-direction: column; justify-content: center; gap: 2rem; overflow: clip; }
.gallery.is-pinned .gallery__track { overflow: visible; scroll-snap-type: none; }
.gallery.is-pinned .gallery__item { flex-basis: calc(62svh * 0.8); }
```

```js
(() => {
  const root = document.querySelector('.gallery');
  if (!root) return;
  const track = root.querySelector('.gallery__track');
  const wide = matchMedia('(min-width: 900px) and (prefers-reduced-motion: no-preference)');
  let dx = 0, queued = false;
  const place = () => {
    queued = false;
    if (!root.classList.contains('is-pinned')) return;
    const p = Math.min(1, Math.max(0, -root.getBoundingClientRect().top / dx));
    track.style.transform = `translate3d(${(-p * dx).toFixed(1)}px, 0, 0)`;
  };
  const measure = () => {
    root.classList.add('is-pinned');                     // measure the row as it would be when pinned
    track.style.transform = '';
    dx = track.scrollWidth - track.clientWidth;
    const pin = wide.matches && dx > 0 && dx < innerHeight * 3;
    root.classList.toggle('is-pinned', pin);
    root.style.height = pin ? `${innerHeight + dx}px` : ''; // one pixel of scroll moves the row one pixel
    place();
  };
  track.addEventListener('focusin', (e) => {             // keyboard: bring the focused item into view
    if (!root.classList.contains('is-pinned')) return;
    const item = e.target.closest('.gallery__item');
    const x = Math.min(dx, Math.max(0, item.offsetLeft - parseFloat(getComputedStyle(track).paddingLeft)));
    scrollTo({ top: root.getBoundingClientRect().top + scrollY + x, behavior: 'instant' });
  });
  addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(place); } }, { passive: true });
  addEventListener('resize', measure);
  addEventListener('load', measure);
  wide.addEventListener('change', measure);
  measure();
})();
```

## Hero lùi xa

Khi màn hình đầu rời đi, ảnh chìm xuống và tối đi một chút trong khi chữ nâng lên nhanh hơn, để hero lùi xa thay vì chỉ cuộn mất.

```html
<header class="hero">
  <img class="hero__picture" src="kitchen.jpg" alt="…" width="2400" height="1600" fetchpriority="high">
  <div class="hero__copy"><h1 class="display">…</h1><p class="lead">…</p></div>
</header>
```

```css
.hero { position: relative; min-height: 100svh; overflow: clip; display: grid; align-items: end; view-timeline-name: --hero; }
.hero__picture { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.hero::after { content: ''; position: absolute; inset: 0; background: var(--ink); opacity: 0; pointer-events: none; }
.hero__copy { position: relative; z-index: 1; padding: var(--margin); }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .hero__picture { animation: hero-sink linear both; animation-timeline: --hero; animation-range: exit 0% exit 100%; }
    .hero::after { animation: hero-dim linear both; animation-timeline: --hero; animation-range: exit 0% exit 100%; }
    .hero__copy { animation: hero-lift linear both; animation-timeline: --hero; animation-range: exit 0% exit 70%; }
  }
}
@keyframes hero-sink { to { transform: translateY(8%) scale(1.06); } }
@keyframes hero-dim { to { opacity: 0.35; } }
@keyframes hero-lift { to { transform: translateY(-6%); opacity: 0; } }
```

## Chuyển trang (`carried-picture`)

Chuyển giữa các trang của site bằng view transitions của chính trình duyệt: trang cũ mờ nhanh, trang mới trồi lên, và bức ảnh vừa được bấm bay vào chỗ làm hero của trang mới. Không thư viện, không tấm màn toàn màn hình. Tối đa 480ms, tắt khi giảm chuyển động.

```css
/* on every page */
@view-transition { navigation: auto; }
@media (prefers-reduced-motion: reduce) { @view-transition { navigation: none; } }
::view-transition-old(root) { animation: vt-leave 200ms var(--ease-exit) both; }
::view-transition-new(root) { animation: vt-arrive 380ms var(--ease-out) 60ms both; }
::view-transition-group(*) { animation-duration: 480ms; animation-timing-function: var(--ease-in-out); }
::view-transition-image-pair(*.picture) { overflow: clip; }
::view-transition-old(*.picture), ::view-transition-new(*.picture) { height: 100%; object-fit: cover; }
@keyframes vt-leave { to { opacity: 0; } }
@keyframes vt-arrive { from { opacity: 0; transform: translateY(16px); } }
```

```html
<!-- on the index: the card picture of one project -->
<img src="/img/leith.jpg" alt="…" style="view-transition-name: kitchen-leith; view-transition-class: picture">
<!-- on that project's page: its hero picture -->
<img src="/img/leith-wide.jpg" alt="…" style="view-transition-name: kitchen-leith; view-transition-class: picture">
```

## Tô mực theo cuộn (`ink-fill`)

Một câu tuyên ngôn chuyển từ 45% mực lên đủ mực khi nó trôi lên qua màn hình. Đọc được ngay từ đầu; việc tô chỉ đặt nhịp đọc. Một câu mỗi trang, ba đến năm dòng, cỡ 32px trở lên.

```html
<p class="statement head" data-fill>Nine people, one workshop, no catalogue: every stool is made for the kitchen it goes to.</p>
```

```css
[data-fill] { --fill: var(--ink); color: var(--fill); }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .is-filling > span { display: inline-block; color: color-mix(in oklab, var(--fill) 45%, transparent); animation: ink-fill linear both; animation-timeline: view(); animation-range: cover 20% cover 45%; }
  }
}
@keyframes ink-fill { to { color: var(--fill); } }
```

```js
(() => {
  if (!CSS.supports('animation-timeline: view()') || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('[data-fill]').forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    words.forEach((word, i) => {
      const s = document.createElement('span');
      s.textContent = word;
      el.append(s, i < words.length - 1 ? ' ' : '');
    });
    el.classList.add('is-filling');
  });
})();
```

## Số cuộn lên (`rolling-figures`)

Cho trang mà luận điểm là vài con số (báo cáo, quỹ, năm thành lập): mỗi chữ số cuộn lên giá trị của nó một lần. Con số thật vẫn nằm trong văn bản cho trình đọc màn hình và công cụ tìm kiếm.

```html
<p class="figure"><span class="display" data-roll>1987</span> the year the first stool was sold</p>
```

```css
.roll__digits { display: inline-flex; font-variant-numeric: tabular-nums; line-height: 1; }
.roll__col { display: inline-block; height: 1em; overflow: clip; }
.roll__strip { display: flex; flex-direction: column; transform: translateY(calc(var(--d) * -1em)); }
.roll__strip > span { height: 1em; }
@media (prefers-reduced-motion: no-preference) {
  .roll:not(.is-in) .roll__strip { transform: none; }
  .roll.is-in .roll__strip { transition: transform 1100ms var(--ease-expo) calc(var(--i) * var(--stagger-item)); }
}
```

```js
(() => {
  const els = [...document.querySelectorAll('[data-roll]')];
  if (!els.length) return;
  els.forEach((el) => {
    const value = el.textContent.trim();
    const said = Object.assign(document.createElement('span'), { className: 'sr-only', textContent: value });
    const shown = Object.assign(document.createElement('span'), { className: 'roll__digits' });
    shown.setAttribute('aria-hidden', 'true');
    let i = 0;
    for (const ch of value) {
      if (!/\d/.test(ch)) { shown.append(ch); continue; }
      const col = Object.assign(document.createElement('span'), { className: 'roll__col' });
      const strip = Object.assign(document.createElement('span'), { className: 'roll__strip' });
      strip.style.setProperty('--d', ch);
      strip.style.setProperty('--i', i++);
      for (let n = 0; n < 10; n++) strip.append(Object.assign(document.createElement('span'), { textContent: n }));
      col.append(strip);
      shown.append(col);
    }
    el.classList.add('roll');
    el.replaceChildren(said, shown);
  });
  if (!('IntersectionObserver' in window)) { els.forEach((el) => el.classList.add('is-in')); return; }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
  }, { rootMargin: '0px 0px -15% 0px' });
  els.forEach((el) => io.observe(el));
})();
```

---

# Phần C. Tự viết thêm

Các hiệu ứng dưới đây bản gốc chỉ mô tả bằng lời; code do bộ skill này viết theo đúng mô tả đó.

## Footer như tấm màn (`curtain-footer`)

Nội dung trang trượt lên như một tấm màn để lộ footer đang chờ bên dưới. Không cần JavaScript.

```css
main { position: relative; z-index: 1; background: var(--bg); }
.site-footer { position: sticky; bottom: 0; z-index: 0; }
```

Footer phải ngắn hơn chiều cao màn hình, nếu không phần dưới của nó sẽ không bao giờ lộ ra.

## Ảnh chuyển dần (`slow-crossfade`)

Ba, bốn ảnh cùng khung hình chuyển dần qua nhau trong khoảng 1,6 giây, mỗi ảnh giữ 5–6 giây. Cảm giác như ánh sáng thay đổi trong phòng. Dừng khi tab bị ẩn; khi giảm chuyển động thì chỉ hiện ảnh đầu.

```html
<figure class="crossfade" aria-label="Quán lúc sáng, trưa và tối">
  <img src="sang.jpg" alt="" class="is-on">
  <img src="trua.jpg" alt="">
  <img src="toi.jpg" alt="">
</figure>
```

```css
.crossfade { display: grid; margin: 0; overflow: clip; }
.crossfade img { grid-area: 1 / 1; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 1600ms ease; }
.crossfade img.is-on { opacity: 1; }
```

```js
(() => {
  const root = document.querySelector('.crossfade');
  if (!root || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const imgs = [...root.querySelectorAll('img')];
  let i = 0, timer;
  const next = () => { imgs[i].classList.remove('is-on'); i = (i + 1) % imgs.length; imgs[i].classList.add('is-on'); };
  const start = () => { clearInterval(timer); timer = setInterval(next, 5500); };
  document.addEventListener('visibilitychange', () => document.hidden ? clearInterval(timer) : start());
  start();
})();
```

## Băng chữ chạy (`edge-marquee`)

Một dòng chữ rất lớn chạy ngang toàn chiều rộng với tốc độ chậm, đều. Nhân đôi nội dung để vòng lặp liền mạch, dừng khi hover và khi giảm chuyển động. Một băng chữ mỗi trang, mang chữ thật (tên, lời khẳng định).

```html
<div class="marquee" aria-label="Rang mỗi sáng thứ Ba ở Đà Lạt">
  <div class="marquee__track" aria-hidden="true">
    <span>Rang mỗi sáng thứ Ba ở Đà Lạt ·</span><span>Rang mỗi sáng thứ Ba ở Đà Lạt ·</span>
  </div>
</div>
```

```css
.marquee { overflow: clip; }
.marquee__track { display: flex; width: max-content; font-size: clamp(48px, 9vw, 160px); white-space: nowrap; }
.marquee__track span { padding-right: 0.5em; }
@media (prefers-reduced-motion: no-preference) {
  .marquee__track { animation: marquee 40s linear infinite; }
  .marquee:hover .marquee__track { animation-play-state: paused; }
}
@keyframes marquee { to { transform: translateX(-50%); } }
```

## Hàng kéo ngang (`drag-row`)

Một hàng phần tử lớn rộng hơn màn hình mà người xem kéo ngang: cuộn ngang gốc của trình duyệt có scroll snap, phần tử đầu thẳng lề trang, phần tử cuối được phép chạy ra khỏi mép để thấy hàng còn tiếp. Không thư viện carousel, không mũi tên, không chấm.

```css
.drag-row { display: flex; gap: var(--gutter); overflow-x: auto; scroll-snap-type: x mandatory; scroll-padding-inline: var(--margin); padding-inline: var(--margin); scrollbar-width: none; overscroll-behavior-x: contain; }
.drag-row::-webkit-scrollbar { display: none; }
.drag-row > * { flex: 0 0 min(78vw, 32rem); scroll-snap-align: start; }
```

Ẩn thanh cuộn chỉ khi phần tử cuối bị cắt rõ ở mép phải (đó là tín hiệu "còn nữa").

## Màu theo chương (`colour-on-scroll`)

Mỗi chương là một khối màu tràn viền, nền đổi đúng tại mép section. Thứ duy nhất chuyển động: thanh header cố định đổi màu chữ theo chương bên dưới, trong 300ms. Không bao giờ tô lại toàn trang từ observer.

```html
<section class="chapter" data-ink="#f4efe6" style="background:#1d3b2a;color:#f4efe6">…</section>
```

```css
.site-header { color: var(--header-ink, var(--ink)); transition: color 300ms ease; }
```

```js
(() => {
  const header = document.querySelector('.site-header');
  const chapters = document.querySelectorAll('[data-ink]');
  if (!header || !chapters.length) return;
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) if (e.isIntersecting) header.style.setProperty('--header-ink', e.target.dataset.ink);
  }, { rootMargin: '0px 0px -95% 0px' }); // chương đang nằm dưới header
  chapters.forEach((c) => io.observe(c));
})();
```

## Tờ giấy phủ lên ảnh (`sheet-over`)

Một ảnh tràn viền giữ chỗ trong một màn hình, rồi chương tiếp theo (một tờ đục mang tiêu đề ở mép trên) trượt lên phủ lên nó như lật trang. Không script.

```css
.held-photo { position: sticky; top: 0; height: 100svh; margin: 0; }
.held-photo img { width: 100%; height: 100%; object-fit: cover; }
.held-photo + .sheet { position: relative; z-index: 1; background: var(--bg); }
```

## Dòng chữ bị đẩy (`pushed-line`)

Một dòng chữ rất lớn bị thanh cuộn đẩy ngang (không phải đồng hồ): đi từ lệch phải 12% sang lệch trái 12% khi nó băng qua màn hình, và đọc được trọn vẹn ở giữa hành trình. Một dòng mỗi trang, không bao giờ chạy ngang qua đoạn văn đang đọc.

```css
.pushed { white-space: nowrap; font-size: clamp(56px, 11vw, 200px); }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .pushed { animation: pushed linear both; animation-timeline: view(); animation-range: cover 0% cover 100%; }
    @keyframes pushed { from { transform: translateX(12%); } to { transform: translateX(-12%); } }
  }
}
```

Bọc dòng chữ trong một khung `overflow: clip` (không phải `hidden`).

## Tĩnh lặng (`stillness`)

Không có màn trình diễn. Trang có mặt ngay lập tức, sự kỷ luật chính là thông điệp. Chuyển động chỉ giới hạn ở phản hồi chính xác: nhấn nút 140ms, đổi màu link 180ms, vòng focus hiện không trễ. Không thêm hiệu ứng mở trang hay lộ diện khi cuộn cho hướng này. Đây cũng là ngoại lệ duy nhất của yêu cầu "ít nhất 8 phần tử chuyển động" trên trang quảng bá.
