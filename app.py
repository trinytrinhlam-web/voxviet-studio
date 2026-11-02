"""Khởi động VoxViet Studio:  python app.py  [--port 7860] [--no-browser] [--online]"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = Path(os.environ.get("VOXVIET_MODELS", ROOT / "models"))
READY_MARK = MODELS / ".models_ready"


def _setup_env(online: bool) -> None:
    # Mô hình được lưu trong thư mục models/ của dự án (dễ chép sang máy khác).
    os.environ.setdefault("HF_HOME", str(MODELS / "hf"))
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
    # Đã tải mô hình → chạy hoàn toàn offline, không gọi mạng.
    if READY_MARK.exists() and not online:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def main() -> None:
    ap = argparse.ArgumentParser(description="VoxViet Studio")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--online", action="store_true", help="cho phép tải mô hình từ Internet")
    ap.add_argument("--demo", action="store_true", help="bật engine giả lập (chạy thử khi chưa có mô hình)")
    args = ap.parse_args()
    _setup_env(args.online)
    if args.demo:
        os.environ["VOXVIET_DEMO"] = "1"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    from voxviet.ui.app import launch
    print(f"\n  VoxViet Studio đang chạy: http://127.0.0.1:{args.port}\n  (đóng cửa sổ này để tắt)\n")
    launch(port=args.port, inbrowser=not args.no_browser)


if __name__ == "__main__":
    main()
