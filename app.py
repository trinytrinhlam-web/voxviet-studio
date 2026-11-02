"""Khởi động VoxViet Studio:  python app.py  [--port 7860] [--no-browser] [--online] [--demo]"""

from __future__ import annotations

import argparse
import logging
import os

from voxviet import bootstrap


def main() -> None:
    ap = argparse.ArgumentParser(description="VoxViet Studio")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--no-browser", action="store_true", help="không tự mở cửa sổ giao diện")
    ap.add_argument("--online", action="store_true", help="cho phép tải mô hình từ Internet")
    ap.add_argument("--demo", action="store_true", help="bật engine giả lập (chạy thử khi chưa có mô hình)")
    args = ap.parse_args()
    bootstrap.setup_env(args.online)
    if args.demo:
        os.environ["VOXVIET_DEMO"] = "1"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    from voxviet.server import run
    run(port=args.port, open_window=not args.no_browser)


if __name__ == "__main__":
    main()
