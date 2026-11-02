# Chữ

Chữ mang thông tin, thứ bậc và giọng nói. Tổng hợp từ taste-skill (số liệu đo trên các trang đoạt giải) và Impeccable (hệ thống, đọc, kỹ thuật), cộng phần tiếng Việt.

## Mục lục

1. Số liệu từ các trang đoạt giải
2. Thang cỡ: ít cỡ, cách xa nhau
3. Dựng chữ hiển thị (tiêu đề lớn)
4. Dựng chữ thân bài
5. Một font hay hai
6. Font cần tránh
7. Tiếng Việt
8. Tải font đúng cách
9. Chi tiết phân biệt chữ được dàn với chữ được gõ
10. Lỗi script không thấy được

## 1. Số liệu từ các trang đoạt giải

| | Trung vị | Nửa giữa | Ghi chú |
|---|---|---|---|
| Tiêu đề hero | 72px (5vw) | 43–109px | Trang điểm cao: 6vw |
| Chữ lớn nhất trang | 6.4vw | đến 10.4vw | Trang điểm cao 8.4vw, trang yếu 5vw |
| Tiêu đề hero trên điện thoại | 40px | 32–59px | |
| Tracking hero | -0.01em | -0.03 đến 0 | Càng to càng chặt |
| Leading hero | 1.0 | 0.95–1.1 | Tiếng Việt: xem mục 7 |
| Thân bài | 16px | 14–18px | Nhà mình: từ 16px |
| Tiêu đề ÷ thân bài | 4.3 | | Trang điểm cao 4.7 |
| Số font thực dùng | 2 | 31% dùng một, 45% hai | |
| Độ đậm hero | thường 48%, vừa 18%, đậm 22% | | Chữ to không cần đậm |
| Hero căn giữa | 39% | | Trang yếu: 52% |

## 2. Thang cỡ: ít cỡ, cách xa nhau

**Quảng bá / Trải nghiệm:**
- Hai hoặc ba cỡ làm hết việc nhìn thấy được: một cực lớn, một nhỏ, gần như không có gì ở giữa.
- Cỡ hiển thị gấp ít nhất bốn lần thân bài trên desktop.
- Tối đa năm cỡ trên trang. Đừng tạo cỡ "tiêu đề phụ" cho mỗi thẻ, mỗi nhãn; hai cỡ trông gần giống nhau thì gộp làm một hoặc kéo xa ra.
- Một cỡ thống trị mỗi màn hình. Hero tự tin rồi tiêu đề section gần to bằng là lỗi.
- Dùng `clamp()` cho cỡ hiển thị; cỡ hiển thị thuộc về hướng thiết kế (tượng đài 16–24vw, nhạc cụ trầm lặng 5–7vw).

```css
:root {
  --step-small: clamp(0.8125rem, 0.79rem + 0.1vw, 0.875rem); /* từ 13px */
  --step-body: clamp(1rem, 0.96rem + 0.2vw, 1.125rem);      /* 16–18px */
  --step-lead: clamp(1.25rem, 1.1rem + 0.7vw, 1.625rem);
  --step-head: clamp(2rem, 1.4rem + 2.6vw, 3.5rem);
  --step-display: clamp(3rem, 1rem + 8vw, 9rem);
}
```

**Thao tác / Đọc:** thang cố định theo rem, tỉ lệ 1.125–1.2, không fluid. Xem `02-man-hinh-ung-dung.md`.

## 3. Dựng chữ hiển thị

- **Tracking theo cỡ.** Càng to càng chặt. Sàn: -0.04em cho tiêu đề đến khoảng 6rem; chữ tượng đài (từ 10vw) có thể đến -0.06em. Chữ không được chạm nhau.
- **Leading dưới 1.0 phải kiểm tra** va chạm giữa phần đuôi dòng trên và phần đầu dòng dưới. Với tiếng Việt, xem mục 7.
- **Chữ hoa toàn bộ** cần tracking hơi mở (0 đến +0.03em) kể cả ở cỡ lớn.
- **Căn lề quang học.** Chữ lớn có cạnh trái tròn hoặc chéo (O, C, A, T, W, Đ) trông như thụt vào; kéo ra vài phần trăm em.
- **Chữ trải rộng màn hình:** tính cỡ bằng `vw` và kiểm tra ở 390px và 1440px; muốn chữ khít đúng chiều rộng thì đo bằng một đoạn script nhỏ, không đoán.
- `text-wrap: balance` cho tiêu đề và khối ngắn căn giữa.
- Không bao giờ đổ bóng chữ, viền chữ hay tô gradient cho chữ hiển thị.
- Chữ to trên nền tối trông đậm hơn: giảm một bậc độ đậm hoặc thêm 0.01em tracking.

## 4. Dựng chữ thân bài

- Độ dài dòng 45–75 ký tự. Rộng hơn thì mắt lạc dòng.
- Leading 1.45–1.6 cho thân bài; 1.3–1.4 cho cỡ lead lớn hơn; rộng hơn cho bài đọc dài. Dòng càng dài leading càng cần lớn.
- Chữ phụ cùng font với màu mực nhạt hơn (`--muted`), không phải độ đậm nhẹ hơn hay cỡ nhỏ hơn.
- Không căn giữa đoạn văn dài hơn ba dòng. Không căn đều hai bên.
- `text-wrap: pretty` cho thân bài.
- Nhịp đoạn: dùng khoảng cách giữa đoạn **hoặc** thụt đầu dòng, không cả hai.
- Chữ sáng trên nền tối: tăng nhẹ cả leading, tracking và độ đậm (Impeccable).
- Giữ được phóng to của trình duyệt, cài đặt cỡ chữ của người dùng.

## 5. Một font hay hai

- Một font là bình thường (một phần ba số trang nghiên cứu). Hai là giới hạn.
- Có hai thì mỗi font một việc và không bao giờ đổi: một cho tiêu đề, một cho mọi thứ còn lại.
- Không thêm font thứ ba cho nhãn, số hay trích dẫn. Không trộn hai font trong một tiêu đề.
- Nghiêng chỉ cho tên tác phẩm và nhấn mạnh thật trong đoạn văn, không để trang trí. Không tô một từ của tiêu đề bằng nghiêng, serif, màu khác hay gạch chân.
- Thao tác / Đọc: một font làm việc tốt thường là đủ; font hệ thống được phép.

## 6. Font cần tránh

Với trang Quảng bá / Trải nghiệm, các font sau là "mặc định từ dữ liệu huấn luyện": chọn chúng nghĩa là đã ngừng tìm (Impeccable). Chỉ dùng khi có lý do mà không font nào khác đáp ứng; liên tưởng với chủ thể (sách thì serif, công nghệ thì mono) không phải lý do.

Fraunces, Playfair Display, Cormorant, Lora, Crimson, Newsreader, Syne, Space Grotesk, Space Mono, IBM Plex, Inter (làm font tiêu đề), DM Sans, DM Serif, Outfit, Plus Jakarta Sans, Instrument Sans.

Cũng tránh Arial, font hệ thống, Impact, Arial Black làm giọng hiển thị của một trang có thế giới riêng.

Thư viện của `rut-huong.mjs` (43 bộ font) đã loại các font này. Muốn chọn font khác ngoài thư viện: chọn font như chọn một vật trong thế giới của chủ thể, đúng giọng của chế độ.

## 7. Tiếng Việt

Không bộ gốc nào xử lý phần này.

### Font phải có đủ dấu

Font thiếu dấu tiếng Việt thì trình duyệt lấy ký tự có dấu từ font dự phòng: các chữ "ệ", "ữ", "ặ" lệch kiểu, lệch độ đậm so với chữ xung quanh, nhìn lởm chởm. Kiểm tra **trước khi dựng**, ngay sau khi rút phiếu.

**Google Fonts:** kiểm tra font có subset `vietnamese`:

```bash
curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36" \
  "https://fonts.googleapis.com/css2?family=Archivo" | grep -c "/\* vietnamese \*/"
```

Kết quả lớn hơn 0 là có dấu. Bằng 0 là không. Thay `Archivo` bằng tên font (khoảng trắng thành `+`). Kiểm tra cả font tiêu đề lẫn font thân bài. Google Fonts tự chia subset theo `unicode-range`, không cần thêm tham số `subset`.

**Fontshare và nguồn khác:** phần lớn font Fontshare không có dấu tiếng Việt. Kiểm tra bằng mắt: tạo một trang thử dùng font đó, viết dòng thử bên dưới ở cỡ tiêu đề và cỡ thân bài, chụp bằng `chup-man-hinh.mjs`, nhìn xem có ký tự nào lệch kiểu.

```
ĐẶT BÀN Ở ĐÀ LẠT · NGỮ ỔN ẾCH ỮNG ỢT · Thiết kế ước mơ quảng trường đặc sắc · ữ ỗ ặ ể ợ ự ỹ
```

Font không có dấu thì: `node <skill>/scripts/rut-huong.mjs --ve-lai chu` cho đến khi được font có dấu, và ghi vào báo cáo.

Một số font Google thường có subset tiếng Việt, để thử khi cần thay thế (vẫn phải kiểm tra bằng lệnh trên): Be Vietnam Pro (thiết kế cho tiếng Việt), Lexend, Montserrat, Nunito, Work Sans, Barlow, Archivo, Public Sans, Chivo, Source Serif 4, Literata, EB Garamond.

### Leading và dấu chồng

Chữ hoa tiếng Việt mang dấu chồng (Ế, Ỗ, Ặ, Ữ, Ở) cao hơn chữ hoa Latin thường; dấu nặng (Ạ, Ặ, Ợ) thò xuống dưới.

- Tiêu đề lớn tiếng Việt: leading 1.05–1.15 thay cho 0.85–1.0 trong bản thiết kế gốc. Viết thường đầu câu thì có thể chặt hơn một chút so với viết hoa toàn bộ.
- Thân bài tiếng Việt: 1.55–1.7.
- Luôn chụp màn hình một tiêu đề chứa chữ hoa có dấu chồng ở mọi độ rộng và kiểm tra dấu không đụng dòng trên.

### Mặt nạ và cắt chữ

- `overflow: hidden` hay `overflow: clip` trên một dòng chữ cắt cả phía trên lẫn phía dưới. Chừa `padding-block` ở cả hai phía (khoảng 0.18em trên, 0.1–0.12em dưới) và bù bằng `margin-block` âm. Các công thức trong `07-cong-thuc-chuyen-dong.md` đã sửa sẵn.
- Không bao giờ để mép màn hình hay mặt nạ cắt **phần trên** của chữ: mất dấu là mất nghĩa ("ĐÁ" thành "ĐA", "Ở" thành "Ơ"). Cắt ở cạnh dưới hoặc bên hông.

### Khác

- `<html lang="vi">`: trình đọc màn hình phát âm đúng, trình duyệt ngắt từ đúng.
- Viết hoa toàn bộ tiếng Việt khó đọc hơn tiếng Anh vì dấu dày; dùng cho tiêu đề ngắn, tránh cho câu dài.
- `hyphens: none` trên tiêu đề (tiếng Việt vốn không gạch nối).
- Tiếng Việt nhiều từ ngắn: ngân sách tiêu đề tính theo **ký tự** (xem `09-chu-viet.md`), không theo số từ.

## 8. Tải font đúng cách

- Chỉ tải các độ đậm thực dùng (thường hai đến ba tổng cộng).
- Luôn có font dự phòng cùng loại (sans cho sans, serif cho serif). Có thể chỉnh `size-adjust` cho font dự phòng để giảm nhảy chữ khi font chính tải xong.
- `font-display: swap` (có sẵn trong link Google Fonts với `&display=swap`).
- Preload font tiêu đề nếu có chuỗi mở trang: `<link rel="preload" as="font" type="font/woff2" crossorigin href="...">`.
- Framework: dùng bộ tải font của nó với cùng font và độ đậm (`next/font/google`, `@fontsource/...`).
- **Tự host** font khi được (tải file woff2 về thư mục dự án): nhanh hơn, không phụ thuộc bên thứ ba, không lộ địa chỉ IP người xem cho bên thứ ba. Kiểm tra giấy phép font cho phép tự host (font Google và đa số Fontshare cho phép).
- Sau khi dựng, kiểm tra trong ảnh chụp rằng font đúng đã thật sự hiển thị; trang rơi về font mặc định là rơi về vẻ ngoài mặc định.

## 9. Chi tiết phân biệt chữ được dàn với chữ được gõ

- Dấu ngoặc kép cong (“ ” ‘ ’), gạch ngang thật (– —), dấu ba chấm thật (…).
- `font-variant-numeric: tabular-nums` cho giá, bảng, ngày theo cột; `oldstyle-nums` hợp với văn xuôi dài ở một số font serif.
- Link: `text-underline-offset: 0.18em; text-decoration-thickness: 0.07em` để gạch chân không đâm vào phần đuôi chữ (và dấu nặng tiếng Việt).
- `hyphens: none` trên tiêu đề. `overflow-wrap: anywhere` chỉ cho URL hay email dài.
- Khoảng cách phía trên tiêu đề ít nhất gấp đôi khoảng phía dưới: tiêu đề thuộc về đoạn văn sau nó.
- `::selection { background: var(--accent); color: var(--accent-ink); }` và vòng focus thấy được, theo bảng màu.
- Không đổi độ đậm khi hover (dòng chữ nhảy).

## 10. Lỗi script không thấy được

- Tiêu đề qua luật hai dòng nhưng ngắt xấu: một từ mồ côi ở dòng hai, hoặc ngắt giữa một cụm từ ("Cà / phê rang").
- Chữ hiển thị chặt đến mức chạm nhau, hoặc lỏng đến mức rời rạc.
- Thân bài dùng font hiển thị vốn chỉ vẽ cho cỡ lớn.
- Mọi thứ đều đậm. Nhấn mạnh mọi dòng là không nhấn dòng nào.
- Font dự phòng hiện ra thay font đã chọn (kiểm tra trong ảnh chụp).
