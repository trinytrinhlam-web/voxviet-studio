"""Khởi động VoxViet Studio:  python app.py  [--app] [--port 7860] [--no-browser] [--online] [--demo]

--app: chế độ phần mềm (mở từ biểu tượng bằng pythonw.exe) — không cửa sổ dòng lệnh, nhật ký ghi ra
data/.local/voxviet.log, chỉ một phiên, đóng cửa sổ phần mềm là tắt hẳn.
"""

from __future__ import annotations

import argparse
import logging
import os

from voxviet import appmode, bootstrap


def main() -> None:
    ap = argparse.ArgumentParser(description="VoxViet Studio")
    ap.add_argument("--app", action="store_true", help="chế độ phần mềm (không cửa sổ dòng lệnh)")
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--no-browser", action="store_true", help="không tự mở cửa sổ giao diện")
    ap.add_argument("--online", action="store_true", help="cho phép tải mô hình từ Internet")
    ap.add_argument("--demo", action="store_true", help="bật engine giả lập (chạy thử khi chưa có mô hình)")
    args = ap.parse_args()
    appmode.setup_logging(to_file=args.app)
    appmode.hold_mutex()
    try:
        bootstrap.setup_env(args.online)
        if args.demo:
            os.environ["VOXVIET_DEMO"] = "1"
        from voxviet.server import run
        run(port=args.port, open_window=not args.no_browser, app_mode=args.app)
    except Exception as e:
        logging.getLogger("voxviet").exception("Không khởi động được")
        if args.app:
            appmode.message_box(f"VoxViet Studio không khởi động được:\n{e}\n\n"
                                f"Chi tiết: {appmode.log_file()}")
        raise


if __name__ == "__main__":
    main()
