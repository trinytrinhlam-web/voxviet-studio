"""Tải mô hình VieNeu-TTS v3 Turbo về thư mục models/ (chạy một lần, cần Internet).

Sau khi tải xong, phần mềm chạy hoàn toàn offline.
    python tools/download_models.py [--cpu] [--gpu]
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = Path(os.environ.get("VOXVIET_MODELS", ROOT / "models"))
os.environ.setdefault("HF_HOME", str(MODELS / "hf"))
os.environ.pop("HF_HUB_OFFLINE", None)
sys.path.insert(0, str(ROOT))


def run(device: str) -> None:
    from vieneu import Vieneu
    print(f"\n=== Đang tải & chạy thử VieNeu-TTS v3 Turbo trên {device.upper()} ===")
    t = time.time()
    tts = Vieneu(mode="v3turbo", device=device)
    print(f"Nạp xong sau {time.time() - t:.0f}s (backend={getattr(tts, 'backend', '?')}). Đang đọc thử…")
    wav = tts.infer("Xin chào, mô hình đã sẵn sàng. Let's get started!")
    out = MODELS / f"test_{device}.wav"
    tts.save(wav, str(out))
    print(f"✅ Đã tạo file thử: {out}")
    tts.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", action="store_true", help="tải bản CPU (ONNX)")
    ap.add_argument("--gpu", action="store_true", help="tải bản GPU (PyTorch)")
    args = ap.parse_args()
    MODELS.mkdir(parents=True, exist_ok=True)
    targets = []
    if args.gpu or not args.cpu:
        try:
            import torch
            if torch.cuda.is_available():
                targets.append("cuda")
            else:
                print("Không thấy GPU CUDA — bỏ qua bản GPU.")
        except ImportError:
            print("Chưa cài PyTorch — bỏ qua bản GPU.")
    # Luôn tải bản CPU để dự phòng (máy khác không có GPU vẫn chạy được).
    targets.append("cpu")
    ok = False
    for dev in targets:
        try:
            run(dev)
            ok = True
        except Exception as e:  # tiếp tục với thiết bị khác
            print(f"⚠️ Lỗi khi chạy trên {dev}: {e}")
    if ok:
        (MODELS / ".models_ready").write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
        print("\n🎉 Hoàn tất. Từ giờ phần mềm chạy offline (không cần Internet).")
    else:
        print("\n❌ Không tải được mô hình. Kiểm tra kết nối Internet rồi chạy lại.")
        sys.exit(1)


if __name__ == "__main__":
    main()
