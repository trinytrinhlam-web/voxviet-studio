# Ghi nguồn mã nguồn & tài nguyên bên thứ ba

VoxViet Studio (giấy phép MIT, xem `LICENSE`) được xây trên các thành phần mã nguồn mở dưới đây. Tên, giao diện, bộ giọng có sẵn (tên riêng theo địa danh), xử lý văn bản, hậu kỳ âm thanh và toàn bộ phần mềm bao quanh là của VoxViet Studio; các thành phần dưới đây được dùng làm mã nguồn bên trong và giữ nguyên giấy phép gốc.

| Thành phần | Dùng làm | Tác giả | Giấy phép |
|---|---|---|---|
| [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) (gói `vieneu`, mô hình v3 Turbo) | Mã nguồn & trọng số của **lõi giọng VoxViet**; bộ huấn luyện fine-tune (`tools/voxviet-trainer`) | Phạm Nguyễn Ngọc Bảo | Apache-2.0 |
| [sea-g2p](https://pypi.org/project/sea-g2p/) | Chuẩn hoá văn bản, chuyển chữ → âm, nhận diện tiếng Anh xen kẽ | (xem trang dự án) | Apache-2.0 |
| MOSS-Audio-Tokenizer-Nano (OpenMOSS) | Bộ mã hoá âm thanh của lõi giọng | OpenMOSS Team | Xem trang mô hình |
| [Resemble Enhance](https://github.com/resemble-ai/resemble-enhance) (phần denoiser, bản ONNX đi kèm mô hình) | Khử nhiễu AI | Resemble AI | MIT |
| [Chatterbox](https://github.com/resemble-ai/chatterbox) (tuỳ chọn) | Module tiếng Anh Pro | Resemble AI | MIT |
| [Be Vietnam Pro](https://github.com/bettergui/BeVietnamPro) | Font giao diện (`web/fonts/`) | The Be Vietnam Pro Project Authors | SIL OFL 1.1 (`web/fonts/OFL.txt`) |
| [Lucide](https://lucide.dev) | Icon giao diện | Lucide Contributors | ISC |
| [Fluent Emoji 3D](https://github.com/microsoft/fluentui-emoji) | Ảnh đại diện 3D của các giọng (`web/avatars/`, thu nhỏ 160px, WebP) | Microsoft Corporation | MIT (`web/avatars/LICENSE-fluentui-emoji.txt`) |
| [FastAPI](https://fastapi.tiangolo.com), [Uvicorn](https://www.uvicorn.org) | Máy chủ cục bộ của giao diện | — | MIT / BSD-3 |

Các dịch vụ Google (Gemini TTS, gTTS) chỉ được gọi khi bạn dùng tab "So sánh với Google", theo điều khoản của Google.

Dữ liệu giọng nói của chính bạn (`data/voices`, `data/recordings`) thuộc về bạn.
