# Báo cáo rà soát bảo mật — VoxViet Studio 0.6.1

Ngày rà soát: 2026-11-02. Phạm vi: mã VoxViet, mã nguồn lõi giọng (VieNeu-TTS 3.8.3, sea-g2p 0.10.0), thư viện đi kèm, lịch sử GitHub, các kết nối ra ngoài.

## Kết luận nhanh

- **Không thấy mã độc** trong VieNeu-TTS 3.8.3 và sea-g2p 0.10.0 (Python + file nhị phân Linux/Windows), cũng như trong bộ huấn luyện fine-tune ở tag v3.8.3.
- **Tìm thấy và đã sửa 6 lỗ hổng trong mã VoxViet**, mức cao nhất là DNS rebinding (trang web lạ điều khiển được phần mềm). Mỗi lỗ hổng có kiểm thử chống tái phát (`tests/test_security.py`).
- **Lỗ hổng đã công bố của thư viện**: có ở torch 2.8.0, transformers 4.57.6 (bị lõi giọng ghim cứng) và pillow (không được nạp). Không cái nào khai thác được trong cách VoxViet dùng, trừ khi nạp một mô hình độc hại — xem mục 3.
- **Không còn chỗ rò rỉ thông tin**: phần mềm chỉ kết nối Internet ở các chỗ liệt kê trong mục 4.

## 1. Rà mã độc trong mã nguồn lõi giọng

| Hạng mục | Cách kiểm tra | Kết quả |
|---|---|---|
| Nguồn gốc gói | So mã băm SHA-256 file đã rà với PyPI; tác giả & repo GitHub | Khớp: vieneu `7388d166…`, sea-g2p Linux `020121dd…`, Windows `118d4717…`; cùng tác giả Phạm Nguyễn Ngọc Bảo |
| 51 file Python của VieNeu | Tìm lệnh hệ thống, eval/exec, mạng, base64/marshal, pickle, đọc biến môi trường/khoá, ghi file, chuỗi mã hoá dài | Không có mã độc. Ghi chú bên dưới |
| 6 file `.pt` mẫu giọng | Đọc "danh sách nhập" của pickle bằng `pickletools` (không nạp) | Chỉ tham chiếu hàm dựng tensor của PyTorch — sạch. Không đoạn mã nào nạp chúng |
| sea-g2p (Rust, nhị phân) | Chuỗi trong file; hàm hệ thống được nhập (Linux `nm`, Windows bảng import PE) | Không nhập hàm mạng (socket/connect/send, WS2_32, WinINet, WinHTTP) hay chạy chương trình (fork/exec/system, CreateProcess, ShellExecute) |
| Bộ huấn luyện fine-tune (tag v3.8.3) | Như trên | Sạch; chỉ đẩy lên Hugging Face khi tự thêm `--push-to-hub` (VoxViet không dùng) |

Ghi chú (không phải mã độc, nhưng cần biết):
- **`trust_remote_code=True`** (đường chạy GPU): lõi giọng chạy mã Python đi kèm 2 kho mô hình trên Hugging Face (`pnnbao-ump/VieNeu-TTS-v3-Turbo`, `OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano`). Mã này đã nằm sẵn trên máy bạn sau lần tải đầu; VoxViet bật chế độ offline nên không tải lại. **Hãy chạy `kiem_tra_bao_mat.bat`** để quét mã này trên máy bạn — công cụ ghi mã băm và cảnh báo nếu nó bị thay đổi.
- **Đếm lượt tải**: khi có mạng, lõi giọng gửi một yêu cầu tải `config.json` để tăng bộ đếm lượt tải trên Hugging Face (không kèm dữ liệu của bạn). VoxViet chạy offline sau khi tải mô hình nên yêu cầu này không xảy ra.
- `serve.py` (lấy IP công khai qua api.ipify.org, mở đường hầm "bore") và `remote.py` (gửi văn bản tới máy chủ VieNeu) chỉ chạy khi gọi lệnh/chế độ riêng của VieNeu — VoxViet không dùng.

## 2. Lỗ hổng trong mã VoxViet (đã sửa)

| # | Lỗ hổng | Mức | Cách khai thác | Đã sửa |
|---|---|---|---|---|
| 1 | **DNS rebinding** | Cao | Trang web độc hại trỏ tên miền của nó về 127.0.0.1 → gọi API như giao diện: tạo/xoá giọng, đọc cài đặt, chạy cập nhật | Chỉ nhận yêu cầu tới `127.0.0.1`/`localhost`; thêm **khoá phiên** ngẫu nhiên (cookie HttpOnly, SameSite=Strict) — chỉ cửa sổ do `run.bat` mở mới có |
| 2 | XSS qua `voice.json` | Trung bình | Kho giọng đồng bộ từ GitHub; trường `id` bị sửa được chèn thẳng vào HTML | Mã giọng = tên thư mục (đã kiểm tra), mọi chỗ hiển thị đều escape; thêm **Content-Security-Policy** chặn mọi mã chèn |
| 3 | Đọc/xoá file tuỳ ý qua `voice.json` | Trung bình | Tên file mẫu giọng dạng `../../…` → phần mềm đọc hoặc xoá file ngoài thư mục | Chỉ chấp nhận tên file mẫu hợp lệ, đường dẫn phải nằm trong thư mục giọng |
| 4 | Đường dẫn ngoài thư mục ở Phòng thu (Windows) | Trung bình | Mã câu `..\..\x` (Windows coi `\` là phân cách) → đọc/xoá file `.flac` ngoài thư mục | Mã câu phải có trong kịch bản |
| 5 | Tên mô hình fine-tune chứa `../` | Thấp | Ghi kết quả huấn luyện ra ngoài thư mục `output` | Chuẩn hoá tên (chỉ chữ, số, gạch ngang) |
| 6 | Không giới hạn dung lượng tải lên | Thấp | Yêu cầu cực lớn làm đầy ổ đĩa | Giới hạn 200 MB |

Bổ sung: tên model Gemini được kiểm tra trước khi ghép vào địa chỉ; tiêu đề bảo mật (`X-Frame-Options`, `nosniff`, `no-referrer`); WebSocket kiểm tra địa chỉ + khoá phiên.

Kiểm tra tự động: `bandit` (không lỗi mức cao; mọi lệnh con dùng danh sách tham số, không qua shell), 61 kiểm thử (14 kiểm thử bảo mật), chạy thử máy chủ thật trong trình duyệt với khoá phiên + CSP: không lỗi.

## 3. Lỗ hổng đã công bố của thư viện (pip-audit, 2026-11-02)

| Thư viện | Phiên bản | Số lỗ hổng | Có ảnh hưởng tới VoxViet? | Xử lý |
|---|---|---|---|---|
| torch | 2.8.0 | 8 | Không trực tiếp: lỗi treo/hỏng bộ nhớ với dữ liệu tấn công ở vài hàm cụ thể; lỗi `weights_only` chỉ khi nạp file `.pth` độc hại (lõi giọng nạp `.safetensors`) | Không nâng được — lõi giọng ghim `torch==2.8.0` cho GPU |
| transformers | 4.57.6 | 7 | Chỉ khi nạp **mô hình độc hại** (config/checkpoint/tokenizer bị cài bẫy) | Không nâng được — lõi giọng ghim; mô hình chỉ từ 2 nguồn cố định, chạy offline; `kiem_tra_bao_mat.bat` giám sát |
| pillow | 12.3.0 | 39 | Không: chỉ do gradio kéo theo (lõi giọng khai báo cần gradio), VoxViet không nạp gradio/pillow | Bỏ gradio & pillow khỏi bản đóng gói |
| Các thư viện khác | — | 0 | — | Đã **ghim phiên bản** thư viện trực tiếp trong `requirements.txt` |

Nguyên tắc: **chỉ đặt "Mô hình fine-tune" của giọng là thư mục do chính bạn huấn luyện** — nạp mô hình lạ là con đường duy nhất để các lỗ hổng trên gây hại.

## 4. Kết nối ra ngoài & thông tin cá nhân

| Khi nào | Tới đâu | Gửi gì |
|---|---|---|
| Cài đặt (`install.bat`) | astral.sh (uv), pypi.org, download.pytorch.org | Không gửi dữ liệu; chỉ tải phần mềm |
| Tải mô hình lần đầu | huggingface.co | Không; sau đó chạy offline |
| Tự kiểm tra cập nhật (mỗi ngày) / Cập nhật / Đồng bộ | github.com (repo của bạn) | Đồng bộ: kho giọng, bản thu, từ điển — **không còn ghi tên máy tính** vào lịch sử |
| Tab So sánh với Google (chỉ khi bấm) | generativelanguage.googleapis.com, translate.google.com | Đoạn văn bản cần đọc (+ API key với Gemini) |
| Cửa sổ ứng dụng (Edge) | — | Hồ sơ trình duyệt riêng; đã tắt đồng bộ, tải nền, dịch trang |

- Gemini API key lưu ở `data/settings.json` (không đưa lên GitHub, API không bao giờ trả lại key).
- Giao diện bị CSP chặn mọi kết nối ngoài chính phần mềm.
- Lịch sử GitHub (12 commit): không có khoá/mật khẩu, chưa từng có file cài đặt, mô hình hay khoá phiên.

## 5. Việc bạn nên làm

1. Chạy **`kiem_tra_bao_mat.bat`** trên máy (quét mã đi kèm mô hình, file trọng số, đối chiếu thư viện lõi với mã băm gốc, rồi quét virus bằng Windows Defender). Chạy lại sau mỗi lần tải lại mô hình.
2. Giữ repo GitHub ở chế độ **Private** (chứa giọng nói của bạn).
3. Chỉ mở phần mềm bằng `run.bat` (cửa sổ khác không có khoá phiên sẽ bị từ chối — đúng như thiết kế).
4. Bật xác thực 2 lớp cho tài khoản GitHub: ai đẩy được mã lên repo thì bản cập nhật sẽ chạy trên máy bạn.
