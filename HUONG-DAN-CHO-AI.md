# VoxViet Studio — Hướng dẫn dành cho trợ lý AI

> Tài liệu này viết cho **công cụ AI** (ChatGPT, Claude, Gemini, Copilot, agent tự động…) cần soạn văn bản
> hoặc gửi văn bản vào VoxViet Studio để đọc thành giọng nói. Đọc hết mục 1–3 trước khi soạn bất kỳ văn bản nào.
> Áp dụng cho VoxViet Studio **0.7.x** trở lên.

---

## 0. Tóm tắt trong 30 giây

- VoxViet Studio là phần mềm **chuyển văn bản thành giọng nói (TTS) tiếng Việt và tiếng Anh**, chạy **offline** trên máy Windows của người dùng.
- Đầu vào là **văn bản thuần (plain text, UTF-8)**, có thể chèn **thẻ điều khiển** trong ngoặc vuông: cảm xúc `[vui]`, nghỉ `[nghỉ 1s]`, và `<en>…</en>` để ép đọc tiếng Anh.
- Đầu ra là file **WAV hoặc MP3** kèm **phụ đề .srt**, lưu trong `data\outputs\` của thư mục cài (mặc định `E:\VoxViet Studio\data\outputs\`).
- Có 3 chế độ nhận văn bản: **Đọc văn bản** (một giọng), **Hội thoại** (kịch bản nhiều nhân vật), **Lồng tiếng** (file phụ đề .srt).
- Hai cách AI dùng được phần mềm:
  1. **Soạn văn bản** đúng định dạng ở mục 1–3 → người dùng dán vào phần mềm. *(Mọi AI đều làm được.)*
  2. **Tự gửi vào phần mềm** bằng công cụ dòng lệnh `tools\voxviet_cli.py` (mục 6). *(Chỉ AI chạy được lệnh trên máy người dùng.)*

---

## 1. Quy tắc viết văn bản để đọc

### 1.1. Viết như lời nói, không viết như trang web

| Nên | Không nên |
|---|---|
| Văn xuôi thuần, câu hoàn chỉnh, có dấu câu `.` `!` `?` `,` | Markdown: `#`, `**đậm**`, `*`, `-` gạch đầu dòng, bảng, khối mã |
| Mỗi đoạn văn một dòng; **dòng trống** giữa các đoạn | Emoji, ký hiệu trang trí (★ ✔ →), đường kẻ `---` |
| Tiếng Việt **có dấu đầy đủ**, chính tả chuẩn | Viết không dấu, teencode (`ko`, `dc`, `j`) |
| Câu dài vừa phải (dưới ~35 từ); câu dài thì có dấu phẩy | Câu dài cả đoạn không dấu câu |
| Danh sách → viết thành câu: "Thứ nhất, …. Thứ hai, …." | Liệt kê `1)` `a.` theo kiểu văn bản in |
| Đường link → nói bằng lời: "trang web của công ty" | URL, email, đường dẫn file |

- Dấu câu quyết định chỗ ngắt hơi: hết câu (`.` `!` `?` `…`) nghỉ ngắn, hết đoạn (dòng trống) nghỉ dài hơn.
- Ngoặc tròn `( )` và ngoặc kép được đọc bình thường. **Không dùng ngoặc vuông `[ ]` cho việc gì khác ngoài thẻ ở mục 1.3.**
- Không giới hạn độ dài: phần mềm tự chia văn bản dài thành đoạn ~220 ký tự theo ranh giới câu. Một cuốn sách vài trăm trang vẫn được, chỉ lâu hơn.

### 1.2. Số, ngày, tiền, viết tắt, tiếng Anh — phần mềm tự xử lý

Phần mềm tự chuẩn hoá trước khi đọc. **Cứ viết số bằng chữ số**, không cần viết thành chữ:

| Viết | Máy đọc (giọng Bắc) |
|---|---|
| `1.250.000đ` | một triệu hai trăm năm mươi nghìn đồng |
| `10h30 ngày 2/9/2026` | mười giờ ba mươi phút ngày hai tháng chín năm hai nghìn không trăm hai mươi sáu |
| `15%`, `37,5°C`, `105 km` | mười lăm phần trăm, ba mươi bảy phẩy năm độ xê, một trăm linh năm ki lô mét |
| `TP.HCM`, `UBND`, `PGS.TS` | thành phố Hồ Chí Minh, uỷ ban nhân dân, phó giáo sư tiến sĩ |
| `CEO`, `AI` | đánh vần kiểu tiếng Anh (xi-i-ô, ây-ai) |

- Quy ước số kiểu Việt Nam: **dấu chấm ngăn hàng nghìn, dấu phẩy thập phân** (`1.250.000`, `37,5`).
- Giọng miền Nam tự đọc "ngàn" thay "nghìn", "lẻ" thay "linh".
- **Từ tiếng Anh xen trong câu tiếng Việt** được tự nhận diện và đọc theo tiếng Anh (`email`, `meeting`, `deadline`…). Tên riêng, thương hiệu, từ hiếm thì **có thể bị đọc kiểu Việt** → bọc trong `<en>…</en>`:
  - `Mình họp qua <en>Zoom</en> rồi gửi file lên <en>Google Drive</en>.`
- Viết tắt lạ, mã sản phẩm, tên riêng khó đọc → **viết lại theo cách muốn nghe**, ví dụ `VoxViet` → `vốc việt` (hoặc nhờ người dùng thêm vào *Từ điển phát âm* trong Cài đặt).
- Phân số, công thức, ký hiệu toán học, mã chương trình: **viết lại bằng lời**.

### 1.3. Thẻ điều khiển (đặt ngay trong văn bản)

| Thẻ | Tác dụng | Ví dụ |
|---|---|---|
| `[trung tính]` `[vui]` `[buồn]` `[giận]` `[ngạc nhiên]` `[thì thầm]` `[kể chuyện]` | Đổi cảm xúc cho **phần văn bản phía sau thẻ**, tới khi gặp thẻ cảm xúc khác | `[vui] Chúc mừng bạn! [buồn] Nhưng mình phải đi rồi.` |
| `[nghỉ]` | Chèn khoảng lặng 0,7 giây | `Và người chiến thắng là… [nghỉ] Lan!` |
| `[nghỉ 1.5s]` `[nghỉ 500ms]` `[nghỉ 2 giây]` | Khoảng lặng đúng độ dài (tối đa 30 giây) | `Hết chương một. [nghỉ 3s] Chương hai.` |
| `[cười]` `[thở dài]` `[hắng giọng]` | Âm thanh phi ngôn ngữ (tuỳ giọng, có thể không rõ) | `[thở dài] Lại thứ Hai rồi.` |
| `<en>…</en>` | Ép đọc tiếng Anh một cụm từ | `Bấm nút <en>Submit</en>.` |

Quy tắc dùng thẻ:
- Thẻ cảm xúc chấp nhận cả không dấu và tiếng Anh: `[vui]` = `[vui vẻ]` = `[happy]`; `[thi tham]` = `[whisper]`; `[pause 2s]` = `[nghỉ 2s]`.
- Viết đúng chính tả thẻ. Thẻ không nhận ra (ví dụ `[hào hứng]`) **không bị xoá** và có thể bị đọc thành tiếng → chỉ dùng thẻ trong bảng.
- Dùng thẻ cảm xúc **có chừng mực** (đầu đoạn hoặc chỗ đổi giọng rõ ràng). Cảm xúc thể hiện rõ nhất với giọng người dùng tự thu có mẫu riêng cho cảm xúc đó; với 25 giọng có sẵn, thẻ cảm xúc chỉ làm thay đổi nhẹ ngữ điệu.
- `[kể chuyện]` hợp với sách nói; `[thì thầm]` cho lời thì thầm ngắn.

### 1.4. Tiếng Anh nguyên văn

- Văn bản **toàn tiếng Anh** → chọn ngôn ngữ **English** (module English, `--language en`). Không cần `<en>`.
- Văn bản **tiếng Việt có xen tiếng Anh** → giữ ngôn ngữ **Tiếng Việt**.
- Trong module English, số và tiền được đọc theo tiếng Anh (`$1,250.50` → one thousand two hundred fifty dollars and fifty cents; kiểu số Mỹ: dấu phẩy ngăn nghìn, dấu chấm thập phân).
- Module English **không** tự đọc phân số, ngày dạng `3/4` và đơn vị viết tắt (`km`, `kg`) → viết bằng chữ: `three quarters`, `March fourth`, `kilometers`.

---

## 2. Kịch bản hội thoại (nhiều nhân vật)

Dùng cho truyện có lời thoại, podcast, quảng cáo nhiều vai. Mỗi lượt nói **một dòng**:

```
Người kể: Chiều hôm ấy, trời đổ mưa rất to.
Minh (vui): Lan ơi, lâu quá không gặp!
Lan (ngạc nhiên): Ủa, Minh hả? Sao bạn lại ở đây?
Minh: [thì thầm] Nói nhỏ thôi, mình đang trốn việc. [cười]
# Dòng bắt đầu bằng # là ghi chú, không được đọc.
Lan: Trời đất. [nghỉ 1s] Thôi được rồi, đi uống cà phê nhé.
```

Quy tắc:
- Dạng dòng: `Tên: lời thoại` hoặc `Tên (cảm xúc): lời thoại`. Có thể viết `[Tên]: …`.
- Tên nhân vật **tối đa 4 từ**, giữ **giống hệt nhau** ở mọi dòng (`Minh` và `minh` là hai nhân vật khác nhau).
- Cảm xúc trong ngoặc tròn áp dụng cho cả dòng; thẻ `[ … ]` trong lời thoại vẫn dùng được.
- Dòng **không có** `Tên:` được tính là lời của nhân vật ở dòng trước.
- ⚠️ **Bẫy dấu hai chấm:** bất kỳ dòng nào bắt đầu bằng 1–4 từ rồi `:` đều bị hiểu là tên nhân vật. Trong lời thoại hay lời kể **tránh** mở đầu kiểu `Lưu ý: …`, `Kết quả: …`, `Bước 1: …` → viết `Lưu ý là …` hoặc đặt câu đó sau tên nhân vật: `Người kể: Lưu ý là …`.
- Lời dẫn truyện: đặt cho một nhân vật tên `Người kể`.
- Người dùng gán giọng cho từng nhân vật trong phần mềm (tab **Hội thoại**). Khi soạn kịch bản, AI nên **đề xuất kèm bảng phân vai** (nhân vật → giọng ở mục 4), hoặc tạo file `cast.json` (mục 6.3).

---

## 3. Lồng tiếng theo phụ đề (.srt)

Dùng file SRT chuẩn; phần mềm đọc từng câu đúng mốc thời gian, tự tăng tốc tối đa 1,35× nếu câu dài hơn khoảng thời gian.

```
1
00:00:00,000 --> 00:00:03,200
Xin chào, mình là Lan.

2
00:00:03,600 --> 00:00:07,000
Hôm nay mình sẽ hướng dẫn các bạn pha cà phê muối.
```

- Mỗi khối: số thứ tự, dòng thời gian `HH:MM:SS,mmm --> HH:MM:SS,mmm`, rồi lời (1–2 dòng), cách nhau bằng dòng trống.
- Viết lời **ngắn hơn khoảng thời gian**: tiếng Việt đọc thường ~4–5 âm tiết/giây. Câu 3 giây ≈ tối đa 12–15 âm tiết.
- Thẻ HTML như `<i>` và `{\an8}` tự bị bỏ. Không cần thẻ cảm xúc (một cảm xúc cho cả file).

---

## 4. Giọng đọc

### 4.1. 25 giọng có sẵn (mã dùng khi gửi: `preset:<mã>`)

| Mã | Tên | Vùng | Giới | Phong cách |
|---|---|---|---|---|
| `ha-long` | Hạ Long | Bắc | Nam | tự nhiên *(mặc định)* |
| `trang-an` | Tràng An | Bắc | Nam | tự nhiên |
| `ho-tay` | Hồ Tây | Bắc | Nữ | tự nhiên |
| `trang-tien` | Tràng Tiền | Bắc | Nữ | bản tin |
| `hoang-lien` | Hoàng Liên | Bắc | Nam | kể chuyện |
| `sa-pa` | Sa Pa | Bắc | Nữ | tự nhiên |
| `bai-dinh` | Bái Đính | Bắc | Nam | kể chuyện |
| `ba-dinh` | Ba Đình | Bắc | Nam | bản tin |
| `tam-dao` | Tam Đảo | Bắc | Nam | tự nhiên |
| `moc-chau` | Mộc Châu | Bắc | Nam | tự nhiên |
| `yen-tu` | Yên Tử | Bắc | Nam | tự nhiên |
| `duong-lam` | Đường Lâm | Bắc | Nam | kể chuyện |
| `bat-trang` | Bát Tràng | Bắc | Nữ | kể chuyện |
| `hang-dao` | Hàng Đào | Bắc | Nữ | tự nhiên |
| `huong-son` | Hương Sơn | Bắc | Nữ | đọc truyện |
| `hai-van` | Hải Vân | Trung | Nam | tự nhiên |
| `hoi-an` | Hội An | Trung | Nữ | tự nhiên |
| `sai-gon` | Sài Gòn | Nam | Nữ | bản tin |
| `vung-tau` | Vũng Tàu | Nam | Nam | tự nhiên |
| `cuu-long` | Cửu Long | Nam | Nam | kể chuyện |
| `phu-quoc` | Phú Quốc | Nam | Nữ | kể chuyện |
| `ben-nghe` | Bến Nghé | Nam | Nam | bản tin |
| `can-tho` | Cần Thơ | Nam | Nữ | đọc truyện |
| `chau-doc` | Châu Đốc | Nam | Nam | đọc truyện |
| `ca-mau` | Cà Mau | Nam | Nữ | đọc truyện |

Gợi ý chọn: tin tức → giọng *bản tin*; sách nói, truyện → *kể chuyện* / *đọc truyện*; video đời thường, quảng cáo → *tự nhiên*. Các giọng này đọc được cả tiếng Anh.

### 4.2. Giọng của người dùng (kho giọng, tối đa 10)

Mã dạng `voice:<mã>` (ví dụ `voice:giong-cua-toi`). Danh sách thật trên máy: lệnh `voices` (mục 6.2). Không đoán mã — luôn lấy từ danh sách.

---

## 5. Tham số đọc

| Tham số | Giá trị | Mặc định | Ghi chú |
|---|---|---|---|
| Ngôn ngữ | `vi` \| `en` | `vi` | Tiếng Việt có xen tiếng Anh vẫn là `vi` |
| Cảm xúc chung | `trung_tinh` `vui` `buon` `gian` `ngac_nhien` `thi_tham` `ke_chuyen` | `trung_tinh` | Thẻ trong văn bản ghi đè từng đoạn |
| Tốc độ | 0.6 – 1.6 | 1.0 | Giữ nguyên cao độ giọng |
| Nhịp nghỉ giữa câu | 0.3 – 2.5 | 1.0 | Nhân với khoảng nghỉ câu/đoạn |
| Cách đọc số | `bac` \| `nam` | theo vùng của giọng | "nghìn/linh" hay "ngàn/lẻ" |
| Làm trong giọng | `goc` `nhe` `trong` `sang` | `trong` | Hậu kỳ EQ |
| Giảm vang | `tat` `nhe` `vua` `manh` | `vua` | |
| Khử nhiễu AI | bật/tắt | tắt | Chậm hơn một chút |
| Định dạng | `wav` \| `mp3` | theo Cài đặt | Luôn kèm file `.srt` cùng tên |

---

## 6. Gửi văn bản vào phần mềm bằng dòng lệnh (cho AI chạy được lệnh)

### 6.1. Chuẩn bị

- Thư mục cài mặc định: `E:\VoxViet Studio` (bản cài cũ có thể ở thư mục khác — hỏi người dùng nếu không thấy).
- Luôn dùng Python của phần mềm: `.venv\Scripts\python.exe`, chạy **trong thư mục cài**.
- Phần mềm chưa mở thì công cụ **tự mở** (hiện cửa sổ). Lần đọc đầu tiên sau khi mở mất thêm vài chục giây để nạp mô hình.
- Phần mềm chỉ chạy **một việc một lúc**; gửi nhiều lệnh thì chúng xếp hàng.
- Nếu người dùng **đóng cửa sổ** phần mềm, nó tự tắt sau ~12 giây (khi không còn việc đang chạy); lệnh sau sẽ tự mở lại.

```bat
cd /d "E:\VoxViet Studio"
.venv\Scripts\python.exe tools\voxviet_cli.py <lệnh> [tuỳ chọn]
```

Văn bản đưa vào bằng **một** trong ba cách: `--file đường_dẫn.txt` (khuyên dùng, file UTF-8), `--text "…"`, hoặc qua stdin. Văn bản dài, nhiều dòng hay có dấu ngoặc kép → **luôn ghi ra file UTF-8 rồi dùng `--file`**.

### 6.2. Các lệnh

| Lệnh | Việc | Tuỳ chọn chính |
|---|---|---|
| `voices` | Liệt kê giọng (có sẵn + kho giọng) | `--language vi\|en` |
| `check` | Xem máy sẽ đọc văn bản thế nào (sau chuẩn hoá), **không** tạo âm thanh | `--file/--text`, `--voice`, `--dialect` |
| `doc` | Đọc văn bản → âm thanh + phụ đề | `--voice`, `--language`, `--emotion`, `--speed`, `--pause`, `--dialect`, `--enhance`, `--dereverb`, `--ai-clean`, `--mp3` |
| `dialogue` | Kịch bản nhiều nhân vật | `--file` kịch bản, `--cast cast.json`, `--gap` (giây giữa lượt), `--mp3` |
| `dub` | Lồng tiếng theo .srt | `--file` srt, `--voice`, `--speed`, `--max-stretch`, `--mp3` |

Tuỳ chọn chung: `--timeout <giây>`, `--no-start` (đặt **trước** tên lệnh: không tự mở phần mềm).

Ví dụ:

```bat
.venv\Scripts\python.exe tools\voxviet_cli.py voices
.venv\Scripts\python.exe tools\voxviet_cli.py check --file bai_viet.txt
.venv\Scripts\python.exe tools\voxviet_cli.py doc --file bai_viet.txt --voice preset:hoang-lien --emotion ke_chuyen --mp3
.venv\Scripts\python.exe tools\voxviet_cli.py doc --text "Xin chào [vui] các bạn!" --voice preset:sai-gon --speed 1.1
.venv\Scripts\python.exe tools\voxviet_cli.py dialogue --file kich_ban.txt --cast cast.json --mp3
.venv\Scripts\python.exe tools\voxviet_cli.py dub --file video.srt --voice preset:ho-tay
```

### 6.3. File phân vai `cast.json` (cho `dialogue`)

Khoá là **tên nhân vật đúng như trong kịch bản**:

```json
{
  "Người kể": {"voice": "preset:hoang-lien", "emotion": "ke_chuyen"},
  "Minh":     {"voice": "preset:ha-long", "speed": 1.05},
  "Lan":      {"voice": "preset:ho-tay"},
  "Jenny":    {"voice": "preset:sa-pa", "language": "en"}
}
```

Mỗi nhân vật: `voice` (bắt buộc nên có), `emotion`, `speed`, `language` (`vi`/`en`). Nhân vật thiếu trong cast dùng giọng của nhân vật đầu tiên trong file và có cảnh báo.

### 6.4. Kết quả

In ra **một dòng JSON** ở stdout (tiến độ in ra stderr). Mã thoát `0` = thành công, `1` = lỗi.

```json
{"ok": true, "audio": "E:\\VoxViet Studio\\data\\outputs\\20261102-101500_xin-chao.mp3", "srt": "E:\\VoxViet Studio\\data\\outputs\\20261102-101500_xin-chao.srt", "duration_s": 12.4, "elapsed_s": 3.1, "warnings": []}
```

```json
{"ok": false, "error": "Chưa có văn bản."}
```

- `dialogue` có thêm `"speakers": [...]`; `voices` trả `"voices": [{"value": "preset:ha-long", "label": "Hạ Long", "region": "bac", "gender": "nam", "style": "tự nhiên", …}]`; `check` trả `"lines": [{"kind": "text", "emotion": "Vui vẻ", "text": "…đã chuẩn hoá…"}, {"kind": "pause", "seconds": 1.0}]`.
- Đọc `warnings` và báo lại cho người dùng (ví dụ giọng chưa gán, phải tăng tốc câu phụ đề).
- Lỗi "Lõi giọng chưa sẵn sàng" / "chưa tải mô hình" → người dùng cần mở phần mềm và tải lõi giọng ở màn hình chào (cần Internet một lần).

### 6.5. Quy trình khuyên dùng cho AI

1. Soạn văn bản theo mục 1 (hoặc kịch bản mục 2, phụ đề mục 3) → ghi ra file `.txt` UTF-8.
2. Chạy `check` với file đó → đọc `lines` → sửa chỗ đọc sai (thêm `<en>`, viết lại tên riêng) → lặp lại nếu cần.
3. Chạy `doc` / `dialogue` / `dub` → báo người dùng đường dẫn `audio` và `srt`.

---

## 7. API HTTP (nâng cao — chỉ khi không dùng được `voxviet_cli.py`)

Máy chủ chỉ nghe ở `127.0.0.1`, cổng trong `data\.local\instance.json` (thường 7860).
Mọi yêu cầu cần:
- Header `Host: 127.0.0.1:<cổng>` (tên khác bị chặn).
- Cookie `vv_session=<khoá>` — khoá là nội dung file `data\.local\session_token`. **Không gửi khoá này ra ngoài máy.**
- Với POST/PUT/DELETE: header `X-VoxViet: 1` và `Content-Type: application/json`.

| Phương thức & đường dẫn | Thân yêu cầu (JSON) | Trả về |
|---|---|---|
| `GET /api/voices?language=vi` | — | `{"voices": [...]}` |
| `POST /api/normalize` | `{"text", "language", "voice", "dialect"}` | `{"lines": [...], "dialect"}` |
| `POST /api/jobs/tts` | `{"text", "language", "voice", "emotion", "speed", "pause", "dialect", "fmt", "enhance", "dereverb", "ai_clean"}` | `{"job": "<id>"}` |
| `POST /api/dialogue/parse` | `{"script"}` | `{"speakers": [...], "lines": n}` |
| `POST /api/jobs/dialogue` | `{"script", "cast": {...}, "gap", "fmt"}` | `{"job": "<id>"}` |
| `POST /api/jobs/dub` | `{"srt", "language", "voice", "emotion", "speed", "max_stretch", "fmt"}` | `{"job": "<id>"}` |
| `GET /api/jobs/<id>` | — | `{"status": "queued\|running\|done\|error", "progress": 0–1, "message", "result", "error"}` |

Kết quả việc xong (`result`): `{"audio_url": "/files/outputs/<tên>.wav", "srt_url": "/files/outputs/<tên>.srt", "duration", "elapsed", "warnings", "subtitles": [...]}`. File thật nằm ở `data\outputs\<tên>` (bỏ tiền tố `/files/`, ghép với thư mục `data`).

---

## 8. Ví dụ hoàn chỉnh

### 8.1. Đoạn sách nói (chế độ Đọc văn bản, giọng `preset:hoang-lien`)

```
[kể chuyện] Năm 1945, ở một làng nhỏ ven sông Hồng, có một cậu bé tên là An.

Mỗi sáng, An dậy từ 5 giờ để phụ mẹ gánh nước. Con đường ra bến dài chừng 2 km, đất đỏ trơn trượt sau mưa.

[nghỉ 1s] Một hôm, An nhặt được một chiếc hộp gỗ nhỏ. [thì thầm] Bên trong có một lá thư viết bằng tiếng Pháp.

[ngạc nhiên] An tròn mắt. Cậu chưa từng thấy chữ viết lạ như thế bao giờ!
```

### 8.2. Quảng cáo xen tiếng Anh (giọng `preset:sai-gon`, tốc độ 1.05)

```
[vui] Chào cả nhà! Cuối tuần này, cửa hàng giảm giá đến 50% cho toàn bộ sản phẩm.

Chỉ cần đặt hàng qua ứng dụng, nhập mã <en>SUMMER</en> là được miễn phí giao hàng cho đơn từ 299.000đ.

Chương trình kéo dài từ ngày 15/6 đến hết ngày 20/6. [nghỉ 0.5s] Nhanh tay lên nhé!
```

### 8.3. Hội thoại + phân vai

Kịch bản `kich_ban.txt`:

```
Người kể: Sáng thứ Hai, văn phòng vẫn còn vắng.
Hùng (vui): Chào chị Mai! Chị đã xem bản kế hoạch em gửi qua email chưa?
Mai: Chị xem rồi. [nghỉ 0.5s] Phần ngân sách còn thiếu chi phí quảng cáo.
Hùng (ngạc nhiên): Ôi, em quên mất. Để em bổ sung ngay trước buổi meeting lúc 10h.
```

`cast.json`:

```json
{"Người kể": {"voice": "preset:duong-lam"}, "Hùng": {"voice": "preset:vung-tau"}, "Mai": {"voice": "preset:trang-tien"}}
```

---

## 9. Lỗi thường gặp & cách sửa

| Hiện tượng | Nguyên nhân | Cách sửa |
|---|---|---|
| Máy đọc "thăng", "sao sao" | Văn bản có Markdown (`#`, `**`) | Bỏ Markdown, bảng, emoji |
| Máy đánh vần "hát tê tê phê ét hai chấm gạch chéo…" | Có URL / email | Nói bằng lời, không ghi địa chỉ |
| Tên thương hiệu tiếng Anh đọc kiểu Việt | Không tự nhận ra là tiếng Anh | Bọc `<en>Tên</en>` |
| Đọc nguyên chữ "[hào hứng]" | Thẻ không có trong danh sách | Chỉ dùng thẻ ở mục 1.3 |
| Hội thoại xuất hiện nhân vật lạ "Lưu ý", "Bước 1" | Dòng bắt đầu bằng `vài từ:` | Viết lại không dùng dấu hai chấm đầu dòng |
| Ngắt hơi sai chỗ, đọc liền một hơi | Câu quá dài, thiếu dấu câu | Chia câu, thêm dấu phẩy |
| `1.5` đọc thành "một chấm năm" | Tiếng Việt dùng dấu phẩy thập phân | Viết `1,5` (đọc "một phẩy năm") |
| Phụ đề lồng tiếng bị tăng tốc, nói nhanh | Lời dài hơn khoảng thời gian | Rút gọn lời hoặc nới thời gian trong .srt |
| `ok: false`, "VoxViet Studio chưa chạy" | Dùng `--no-start` khi phần mềm tắt | Mở phần mềm hoặc bỏ `--no-start` |
| "Giọng đã bị xoá khỏi kho" | Mã `voice:` không còn | Chạy `voices`, chọn lại |

---

## 10. Điều AI **không** được làm

- Không dùng phần mềm để giả giọng người khác khi chưa có sự đồng ý rõ ràng của họ; không tạo nội dung lừa đảo, mạo danh.
- Không gửi khoá phiên (`session_token`), file trong `data\` hay đoạn ghi âm giọng của người dùng ra ngoài máy.
- Không sửa, xoá file trong thư mục cài (trừ file văn bản do chính AI tạo để đọc) và không thay đổi Cài đặt của người dùng nếu không được yêu cầu.
