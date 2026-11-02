"""Tải mô hình lõi giọng VoxViet về ``models/voxviet-core`` (chạy một lần, cần Internet).

Sau khi tải xong, phần mềm chạy hoàn toàn offline.
    python tools/download_models.py [--cpu] [--gpu]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from voxviet import bootstrap  # noqa: E402

bootstrap.setup_env(online=True)


def run(device: str) -> None:
    from vieneu import Vieneu  # mã nguồn lõi giọng
    print(f"\n=== Đang tải & chạy thử lõi giọng VoxViet trên {device.upper()} ===")
    t = time.time()
    tts = Vieneu(mode="v3turbo", device=device)
    print(f"Nạp xong sau {time.time() - t:.0f}s (backend={getattr(tts, 'backend', '?')}). Đang đọc thử…")
    wav = tts.infer("Xin chào, VoxViet Studio đã sẵn sàng. Let's get started!")
    out = bootstrap.MODELS / f"test_{device}.wav"
    tts.save(wav, str(out))
    print(f"✅ Đã tạo file thử: {out}")
    tts.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu", action="store_true", help="tải bản CPU (ONNX)")
    ap.add_argument("--gpu", action="store_true", help="tải bản GPU (PyTorch)")
    args = ap.parse_args()
    bootstrap.MODELS.mkdir(parents=True, exist_ok=True)
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
        bootstrap.READY_MARK.write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
        print(f"\n🎉 Hoàn tất. Mô hình nằm ở {bootstrap.CORE_DIR}. Từ giờ phần mềm chạy offline.")
    else:
        print("\n❌ Không tải được mô hình. Kiểm tra kết nối Internet rồi chạy lại.")
        sys.exit(1)


if __name__ == "__main__":
    main()
