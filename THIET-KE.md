# VoxViet Studio — hệ thiết kế

**Chế độ bề mặt:** Thao tác (`thao-tac`). Quy trình: `.claude/skills/thiet-ke-web/tai-lieu/02-man-hinh-ung-dung.md`.

**Bối cảnh vật lý:** buổi tối, phòng ít đèn, đeo tai nghe, nghe từng câu → **tối**.

**Câu hỏi của màn hình chính (Đọc văn bản):** "Bản đọc này đã đúng ý chưa — câu nào cần sửa?"
→ khối lớn nhất là văn bản + **băng câu** (dạng sóng chia theo từng câu, bấm để nghe đúng câu đó).

**Nét nhận diện (chọn một):** màu hổ phách của đèn "ON AIR" chỉ đặt trên dữ liệu âm thanh (sóng đang phát, câu đang chọn, mức âm lượng) và nút hành động chính.

**Phần tử chỉ sản phẩm này có:** băng câu; logo là chữ V dựng từ các vạch đo mức âm lượng.

## Token

| Vai trò | Giá trị |
|---|---|
| `--bg` | `oklch(0.175 0.007 70)` than ấm (nền nội dung) |
| `--rail` | `oklch(0.150 0.007 70)` thanh bên, lớp trung tính thứ hai |
| `--surface` / `--surface-2` | `oklch(0.215 0.008 70)` / `oklch(0.255 0.009 70)` |
| `--line` | `oklch(0.315 0.010 70)` |
| `--ink` / `--muted` | `oklch(0.935 0.010 85)` / `oklch(0.740 0.014 80)` |
| `--accent` / `--accent-ink` | `oklch(0.815 0.135 76)` hổ phách / `oklch(0.215 0.035 70)` |
| `--rec` | `oklch(0.660 0.190 27)` chỉ cho nút thu âm |
| `--ok` `--warn` `--danger` | `oklch(0.780 0.120 150)` `oklch(0.840 0.130 92)` `oklch(0.700 0.170 25)` |

- **Font:** Be Vietnam Pro 400/500/600 (tự lưu, có đủ dấu). Một font cho mọi thứ; số dùng `tabular-nums`.
- **Thang chữ (rem, tỉ lệ ~1.15):** 0.8125 · 0.875 · 1 · 1.125 · 1.375. Tiêu đề trang 1.375rem/600.
- **Bo góc:** 6px (điều khiển), 10px (panel). Không đổ bóng, trừ menu nổi.
- **Chuyển động:** 120–200ms, chỉ `transform`/`opacity`, có `prefers-reduced-motion`.
- **Icon:** Lucide (ISC), nét 1.75, cỡ 18px.
