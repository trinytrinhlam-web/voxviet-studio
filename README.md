# 🎙️ VoxViet Studio

Phần mềm **chuyển văn bản thành giọng nói Việt – Anh** với giọng đọc tự nhiên, **chạy hoàn toàn trên máy Windows của bạn** (không cần Internet sau khi cài), có thể **clone giọng của chính bạn**.

| Tính năng | Mô tả |
|---|---|
| 2 module ngôn ngữ | **Tiếng Việt** và **English**, chọn ở mỗi tab |
| Tiếng Anh xen trong tiếng Việt | "Gửi **email** cho **CEO** về dự án **AI**" → các từ tiếng Anh tự được đọc **chuẩn tiếng Anh** |
| Giọng Bắc / Nam | 25 giọng có sẵn của VoxViet, mang tên địa danh theo vùng (Hạ Long, Hội An, Sài Gòn…) + cách đọc số theo vùng (*nghìn/ngàn*, *linh/lẻ*) |
| Clone giọng | Từ một đoạn thu 5–10 giây; kho lưu **tối đa 10 giọng** |
| Cảm xúc | Trung tính, vui, buồn, giận, ngạc nhiên, thì thầm, kể chuyện — đổi giữa câu bằng thẻ `[vui]`, `[buồn]`… |
| Tốc độ | 0.6× – 1.6×, giữ nguyên cao độ giọng |
| Hội thoại | Kịch bản nhiều nhân vật, mỗi nhân vật một giọng / cảm xúc / ngôn ngữ |
| Sách nói | Văn bản dài, mở file .txt/.docx, xuất WAV/MP3 kèm phụ đề .srt |
| Lồng tiếng video | Đọc theo file phụ đề .srt, khớp đúng thời điểm |
| Trực tiếp | Phát âm thanh ngay khi đang tạo (~0,1–0,3 giây trên GPU) |
| Phòng thu + Fine-tune | Kịch bản 173 câu soạn sẵn, thu từng câu ngay trong app, fine-tune LoRA (tuỳ chọn) |
| So sánh với Google | Nghe cùng đoạn văn bằng Gemini TTS và gTTS (chỉ để **so sánh**) |
| Giao diện riêng | Thiết kế "phòng thu tối", mở trong cửa sổ riêng như ứng dụng Windows; **băng câu**: bấm một câu để nghe đúng câu đó |

---

## 1. Kiến trúc & lựa chọn công nghệ

```
Văn bản ─► Thẻ cảm xúc/nghỉ ─► Từ điển phát âm ─► Chuẩn hoá (số, ngày, tiền, Bắc/Nam)
       ─► Chia câu ─► LÕI GIỌNG VOXVIET ─► Đổi tốc độ
       ─► Hậu kỳ từng câu (khử nhiễu AI → giảm vang → làm trong → âm lượng) ─► WAV/MP3 + SRT

Giao diện (web/, HTML/CSS/JS) ◄─► Máy chủ cục bộ 127.0.0.1 (voxviet/server.py, FastAPI)
```

Mỗi **engine** là một "phích cắm" (`voxviet/engines/`). Khi có mô hình tốt hơn, chỉ cần viết thêm một engine.

| Engine | Vai trò | Giấy phép | Chạy |
|---|---|---|---|
| **Lõi giọng VoxViet** (mã nguồn: [VieNeu-TTS v3 Turbo](https://github.com/pnnbao97/VieNeu-TTS)) | **Lõi chính**: Việt + Anh, clone giọng, streaming, fine-tune LoRA | Apache-2.0 | Offline, GPU hoặc CPU |
| Chatterbox ([resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox)) | Tuỳ chọn cho module English: giọng Anh rất tự nhiên, chỉnh mức cảm xúc | MIT | Offline (môi trường riêng) |
| Google Gemini TTS | **Chỉ làm mẫu so sánh** (gói miễn phí, cần API key) | Dịch vụ Google | Cần Internet |
| Google gTTS | **Chỉ làm mẫu so sánh** (mức cơ bản) | Dịch vụ Google | Cần Internet |

VoxViet Studio dùng VieNeu-TTS **chỉ làm mã nguồn bên trong**: tên, giao diện, bộ giọng, xử lý văn bản và hậu kỳ là của VoxViet; mô hình được lưu ở `models/voxviet-core`. Giấy phép Apache-2.0 yêu cầu giữ ghi nguồn, nên nguồn gốc được ghi ở `THIRD_PARTY_NOTICES.md` và mục **Cài đặt → Giới thiệu**.

Vì sao chọn mã nguồn này làm lõi:
- Huấn luyện trên hơn 10.000 giờ dữ liệu song ngữ, có bộ chuyển chữ→âm (`sea-g2p`) **tự nhận diện từ tiếng Anh trong câu tiếng Việt** và phát âm theo tiếng Anh.
- Clone giọng tức thì 3–8 giây; chất giọng và cảm xúc lấy theo đoạn mẫu.
- Vừa với GPU 6 GB; có đường chạy CPU (ONNX) để dự phòng.
- Có mã fine-tune LoRA chính thức chạy được trên GPU ~6 GB.

---

## 2. Yêu cầu

- Windows 10/11 64-bit, RAM ≥ 8 GB (khuyên 16 GB), ổ trống ~10 GB.
- Card NVIDIA (6 GB VRAM là đủ). Không có GPU vẫn chạy được bằng CPU, nhưng chậm hơn.
- Internet **chỉ khi cài đặt**, lần đầu tải mô hình. Sau đó chạy offline.

## 3. Cài đặt (một lần)

1. Tải mã nguồn vào thư mục dự án (đường dẫn **không có dấu**), ví dụ `E:\VoiceTriny`:
   ```bat
   cd /d E:\
   git clone https://github.com/trinytrinhlam-web/voxviet-studio.git VoiceTriny
   ```
   (Nếu `E:\VoiceTriny` đã có file: tải ZIP từ GitHub rồi giải nén vào đó.)
2. Nhấp đúp **`install.bat`**. Script tự làm các việc sau:
   - cài `uv` và Python 3.12 riêng cho phần mềm (không ảnh hưởng Python khác trên máy);
   - phát hiện card NVIDIA rồi cài PyTorch bản CUDA phù hợp;
   - cài thư viện, tải mô hình lõi giọng về `models/voxviet-core` và đọc thử một câu.
3. Nhấp đúp **`run.bat`**. Phần mềm mở trong **cửa sổ riêng** (Edge ở chế độ ứng dụng, không có thanh địa chỉ). Nếu máy không có Edge/Chrome thì mở trong trình duyệt mặc định tại `http://127.0.0.1:7860`.

Tuỳ chọn:
- `install_english_pro.bat`: cài Chatterbox cho module English. Sau đó vào **Cài đặt → Bộ máy cho module English → Chatterbox**.
- `install_finetune.bat`: cài bộ fine-tune giọng (cần GPU).

Muốn chạy thử giao diện khi chưa có mô hình: `run.bat --demo` (âm thanh là tiếng "bíp" giả lập).

## 4. Hướng dẫn sử dụng

### 📖 Đọc văn bản
Chọn ngôn ngữ (Tiếng Việt / English), **Giọng**, **Cảm xúc**, **Tốc độ**, rồi bấm **Đọc** (hoặc **Ctrl + Enter**). Kết quả hiện trên **băng câu**: dạng sóng chia theo từng câu; bấm một câu trong danh sách để nghe đúng câu đó. File lưu ở `data/outputs/`, kèm phụ đề `.srt` (nút tải ở góc băng câu).

Các nút **Chèn** dưới ô văn bản thêm nhanh thẻ cảm xúc, khoảng nghỉ, tiếng cười hoặc bọc từ đang chọn để ép đọc tiếng Anh. Bấm **Xem cách máy đọc** để kiểm tra số, ngày tháng và từ viết tắt trước khi đọc.

**Thẻ điều khiển** (gõ thẳng vào văn bản):

```
Xin chào các bạn! [vui] Hôm nay mình có tin cực vui. [nghỉ 1s]
[buồn] Nhưng cũng có một tin buồn... [thở dài] [nghỉ 500ms]
[trung tính] Cuộc meeting với CEO dời sang 10h30 ngày 15/3.
```

| Thẻ | Tác dụng |
|---|---|
| `[vui]` `[buồn]` `[giận]` `[ngạc nhiên]` `[thì thầm]` `[kể chuyện]` `[trung tính]` | Đổi cảm xúc cho phần phía sau |
| `[nghỉ 1.5s]` `[nghỉ 500ms]` `[nghỉ]` | Chèn khoảng lặng |
| `[cười]` `[thở dài]` `[hắng giọng]` | Âm thanh tự nhiên (thử nghiệm) |
| `<en>…</en>` | Ép đọc tiếng Anh khi tự nhận diện bị nhầm |

### ✨ Làm trong giọng (hậu kỳ)
Bộ nén âm của mô hình làm mất bớt âm cao, nên giọng có thể nghe hơi **đục** hoặc **tối**. Mỗi câu đọc ra được xử lý lần lượt qua các bước:
- cắt tiếng ù dưới khoảng 90 Hz;
- giảm dải gây đục quanh 300 Hz;
- tăng độ rõ chữ quanh 3,5 kHz;
- tăng độ sáng từ khoảng 7 kHz trở lên;
- tạo lại một ít âm cao bị mất (exciter);
- giới hạn đỉnh mềm để không bị rè.

| Mức | Khi nào dùng |
|---|---|
| Gốc | Không xử lý gì |
| Nhẹ | Giọng vốn đã khá trong, chỉ chỉnh rất ít |
| **Trong** (mặc định) | Hợp với phần lớn giọng |
| Sáng | Giọng rất đục hoặc tối |

**Giảm vang** (Tắt / Nhẹ / *Vừa* / Mạnh): ước lượng phần vang của phòng rồi trừ khỏi giọng theo từng dải tần. Thử trên tín hiệu có vang nhân tạo: phần đuôi vang giảm khoảng 4 / 7 / 11 dB, còn lời nói gần như giữ nguyên (giảm dưới 1 dB).
**Khử nhiễu AI** (tuỳ chọn): dùng bộ khử nhiễu đi kèm mô hình lõi giọng (Resemble Enhance), không phải tải thêm, chạy chậm hơn một chút.
Thứ tự xử lý mỗi câu: khử nhiễu AI → giảm vang → làm trong → cân bằng âm lượng.

Sau khi đọc, khung **Thử hậu kỳ khác trên bản này** (dưới băng câu) cho phép nghe **cùng một bản đọc** ở từng mức mà không phải đọc lại, nên so sánh được công bằng. Chọn xong mức hợp nhất thì đặt làm mặc định trong Cài đặt. Trong mục **Nâng cao**, *Độ biến hoá ngữ điệu* đặt khoảng 0.6–0.7 sẽ cho giọng ổn định và sạch hơn.

### 🎭 Hội thoại
Mỗi dòng có dạng `Tên (cảm xúc): lời thoại`. Danh sách nhân vật tự cập nhật khi bạn gõ; gán giọng, cảm xúc, ngôn ngữ cho từng người rồi bấm **Tạo hội thoại**. Dòng không ghi tên được tính cho người nói ở dòng trước.

### 🎬 Lồng tiếng (SRT)
Tải file phụ đề lên. Mỗi câu được đặt đúng thời điểm trong phụ đề; câu dài hơn khung thời gian sẽ được tăng tốc tối đa theo mức bạn chọn. Sau đó ghép file âm thanh vào video bằng CapCut, Premiere hoặc DaVinci.

### ⚡ Trực tiếp
Gõ câu rồi nhấn Enter, âm thanh phát ngay trong lúc đang tạo. Dùng cho trợ lý ảo hoặc nói chuyện trực tiếp.

### 🗂️ Kho giọng (tối đa 10)
1. Tạo giọng: nhập tên, chọn vùng miền.
2. Mỗi giọng có một ô cho từng cảm xúc. Ở ô **Trung tính** (bắt buộc), bấm **Thu** để thu thẳng bằng micro (bấm lần nữa để dừng và lưu), hoặc **Tải lên** một file 5–10 giây.
3. Để cảm xúc rõ hơn, điền thêm các ô khác (đọc một câu vui bằng giọng vui vào ô "Vui vẻ"…).
4. Ô **Tiếng Anh · trung tính** (tuỳ chọn) giúp module English giống giọng bạn hơn.
5. Bên dưới là **25 giọng có sẵn** lọc theo Bắc / Trung / Nam; bấm ▶ để nghe thử.

> **Cảm xúc hoạt động thế nào?** Lõi giọng lấy chất giọng và cảm xúc từ chính đoạn mẫu. Khi thiếu mẫu cho một cảm xúc, phần mềm dùng mẫu trung tính và chỉ chỉnh nhẹ tốc độ cùng độ biến hoá ngữ điệu, nên cảm xúc sẽ nhẹ. Thu đủ mẫu cho từng cảm xúc là cách hiệu quả nhất.

### 🎚️ Phòng thu & Fine-tune
Kịch bản `data/recording_script/script_vi_en.txt` gồm 173 câu, khoảng 25–35 phút nếu đọc hết:

| Nhóm | Số câu | Mục đích |
|---|---|---|
| Tiếng Việt | 90 | Phủ đủ 6 thanh điệu, các vần, phụ âm; câu hỏi, số, ngày tháng |
| Việt xen Anh | 25 | Học cách bạn đọc từ tiếng Anh trong câu Việt |
| Cảm xúc | 33 | Vui, buồn, giận, ngạc nhiên, thì thầm, kể chuyện, trang trọng |
| Tiếng Anh | 25 | Cho module English |

Cách làm:
1. Bấm **Thu** (hoặc phím **Space**), đọc câu đang hiện, bấm lần nữa để dừng: bản thu tự lưu và chuyển sang câu chưa thu tiếp theo. Thanh đo mức micro chuyển đỏ khi quá to. App tự cắt khoảng lặng, chuẩn âm lượng và cảnh báo khi bị rè.
2. **Tạo / cập nhật giọng**: app tự chọn câu tốt nhất (khoảng 7 giây) cho mỗi cảm xúc và đưa vào Kho giọng. Đây là *clone tức thì*, dùng được ngay, chỉ cần vài câu.
3. **Fine-tune** (nâng cao): khi đã thu được 10 phút trở lên, bấm **Bắt đầu fine-tune**. Xong thì dán đường dẫn thư mục `merged` vào ô *Mô hình fine-tune* của giọng trong Kho giọng. Mất khoảng 30–90 phút trên GPU 6 GB (bật "Tiết kiệm VRAM").

Mẹo thu âm:
- Phòng yên tĩnh, nhiều đồ vải để giảm tiếng vang.
- Micro cách miệng khoảng 20 cm, tránh thổi hơi trực tiếp vào micro.
- Đọc tự nhiên như đang nói chuyện, giữ đều âm lượng và tốc độ giữa các buổi thu.

### ⚖️ So sánh với Google
Nghe cùng một đoạn văn bằng 3 cách: VoxViet (offline), Gemini TTS và gTTS. Gemini cần API key miễn phí từ [aistudio.google.com](https://aistudio.google.com/apikey); dán key vào tab Cài đặt. Phần mềm tự hỏi Google danh sách model TTS hiện có, vì tên model thay đổi theo thời gian. **Google không tham gia vào việc tạo giọng chính.**

### ⚙️ Cài đặt
- Thiết bị (GPU/CPU), phương ngữ đọc số mặc định, định dạng xuất, âm lượng chuẩn, độ dài nghỉ.
- **Từ điển phát âm**: thêm từ đọc sai, ví dụ `vi | VoxViet | vốc việt` hoặc `all | SQL | <en>sequel</en>`.
- **Kiểm tra hệ thống**: xem GPU, engine nào đã sẵn sàng.

---

## 5. Dùng trên nhiều máy (đồng bộ qua GitHub)

Kho giọng (`data/voices/`), bản thu (`data/recordings/`, dạng FLAC) và từ điển (`data/lexicon.json`) được lưu trong repo.

- **Cuối buổi làm việc:** chạy `sync_github.bat` để commit, kéo thay đổi từ máy khác và đẩy lên.
- **Sang máy mới:** `git clone` repo → `install.bat` → `run.bat`. Kho giọng và bản thu đã có sẵn.
- **Cập nhật phần mềm:** chạy `update.bat`.

Không đưa lên GitHub:
- `models/` (mô hình lớn, `install.bat` tự tải lại);
- `data/settings.json` (chứa API key);
- `data/outputs/`.

> ⚠️ Repo chứa **giọng nói của bạn**, nên để repo ở chế độ **Private**.

## 6. Cấu trúc thư mục

```
app.py                     khởi động (máy chủ cục bộ + mở cửa sổ)
web/                       giao diện: index.html, css/, js/, font Be Vietnam Pro, icon Lucide
voxviet/
  server.py                API cho giao diện (chỉ nghe 127.0.0.1)
  catalog.py               bộ giọng có sẵn (data/giong_co_san.json)
  text/                    chuẩn hoá, thẻ, phương ngữ, từ điển, hội thoại, SRT, đọc số tiếng Anh
  engines/                 core_engine (lõi giọng) · chatterbox_engine (+worker) · google_engines · mock_engine
  audio/                   nối, nghỉ, đổi tốc độ, âm lượng, xuất WAV/MP3/FLAC
  voices.py                kho giọng (≤10)
  pipeline.py              điều phối: đọc / hội thoại / lồng tiếng / trực tiếp
  recording.py             phòng thu
  finetune.py              fine-tune LoRA
data/recording_script/     kịch bản thu âm
tools/download_models.py   tải mô hình về models/voxviet-core
.claude/skills/thiet-ke-web skill thiết kế dùng khi chỉnh giao diện (SAN-PHAM.md, THIET-KE.md)
tests/                     kiểm thử tự động (pytest)
```

## 7. Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| "Chưa có mô hình lõi giọng trên máy" | Chạy `download_models.bat` khi có Internet |
| "GPU hết bộ nhớ" | Đóng game hoặc trình duyệt nặng; hoặc Cài đặt → Thiết bị → CPU |
| Một từ tiếng Anh bị đọc kiểu Việt (vd. *con*, *to*) | Bọc từ đó trong `<en>…</en>`, hoặc thêm vào Từ điển phát âm |
| Câu rất ngắn đọc lạ | Viết câu dài hơn một chút hoặc thêm dấu câu |
| Cảm xúc chưa rõ | Thu mẫu riêng cho cảm xúc đó trong Kho giọng |
| Giọng có tiếng vang | Tăng **Giảm vang** lên *Mạnh*, bật **Khử nhiễu AI** |
| Giọng nghe đục / tối | Thử mức **Sáng** trong mục Chuốt giọng; giảm *Độ biến hoá ngữ điệu* còn 0.6–0.7; một số giọng có sẵn vốn được thu kém trong hơn, nên thử giọng khác |
| Giọng clone chưa giống | Dùng mẫu 7–10 giây, sạch, không nhạc nền; hoặc fine-tune |

## 8. Giấy phép & sử dụng có trách nhiệm

- Mã nguồn VoxViet Studio: MIT.
- Thành phần bên thứ ba (VieNeu-TTS, sea-g2p, Resemble Enhance, Chatterbox, Be Vietnam Pro, Lucide…): xem `THIRD_PARTY_NOTICES.md`. Dịch vụ Google tuân theo điều khoản của Google.
- **Chỉ clone giọng của chính bạn, hoặc của người đã đồng ý rõ ràng.** Không dùng để giả mạo hay lừa đảo.

## 9. Phát triển

```bash
pip install -r requirements.txt pytest
python -m pytest -q          # kiểm thử (dùng engine giả lập, không cần mô hình)
python app.py --demo         # chạy giao diện với engine giả lập
node .claude/skills/thiet-ke-web/scripts/soat-loi.mjs web --che-do thao-tac   # soát giao diện
```
