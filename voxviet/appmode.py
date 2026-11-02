"""Chạy như một phần mềm thật (mở từ biểu tượng trên Desktop, không có cửa sổ dòng lệnh):

- ghi nhật ký ra ``data/.local/voxviet.log`` (pythonw.exe không có cửa sổ để in),
- chỉ một phiên: mở lại biểu tượng khi phần mềm đang chạy → chỉ mở thêm cửa sổ,
- báo lỗi bằng hộp thoại Windows khi không khởi động được.
"""

from __future__ import annotations

import io
import json
import logging
import os
import socket
import sys
import urllib.request
from pathlib import Path

from . import paths

LOG_MAX = 2 * 1024 * 1024
PORTS = range(7860, 7870)


def local_dir() -> Path:
    d = paths.DATA / ".local"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_file() -> Path:
    return local_dir() / "voxviet.log"


def setup_logging(to_file: bool) -> None:
    """to_file: ghi nhật ký ra file (chế độ ứng dụng / không có cửa sổ dòng lệnh)."""
    if to_file or sys.stdout is None or sys.stderr is None:
        f = log_file()
        try:
            if f.exists() and f.stat().st_size > LOG_MAX:
                f.replace(f.with_suffix(".log.1"))
        except OSError:
            pass
        stream = io.open(f, "a", encoding="utf-8", errors="replace", buffering=1)
        sys.stdout = sys.stderr = stream
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, force=True,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def child_stderr():
    """Nơi nhận lỗi của tiến trình con: file nhật ký nếu có, không thì bỏ đi (pythonw không có console)."""
    try:
        sys.stderr.fileno()
        return sys.stderr
    except (AttributeError, OSError, ValueError, io.UnsupportedOperation):
        import subprocess
        return subprocess.DEVNULL


# ── một phiên duy nhất ───────────────────────────────────────────────────────

def _instance_file() -> Path:
    return local_dir() / "instance.json"


def port_free(port: int) -> bool:
    with socket.socket() as s:
        if os.name != "nt":  # như uvicorn: bỏ qua kết nối cũ đang TIME_WAIT (Windows không cần)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def is_voxviet(port: int, token: str, timeout: float = 2.0) -> bool:
    """Cổng này có phải VoxViet của chính máy này (cùng khoá phiên) đang chạy không."""
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/state",
                                 headers={"Cookie": f"vv_session={token}", "Host": f"127.0.0.1:{port}"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # không đi qua proxy
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status == 200 and "boot_id" in json.loads(r.read().decode("utf-8"))
    except Exception:
        return False


def running_port(token: str) -> int | None:
    try:
        port = int(json.loads(_instance_file().read_text(encoding="utf-8"))["port"])
    except (OSError, ValueError, KeyError, TypeError):
        port = PORTS.start
    return port if not port_free(port) and is_voxviet(port, token) else None


def choose_port(preferred: int) -> int:
    for p in [preferred, *PORTS]:
        if port_free(p):
            return p
    raise RuntimeError(f"Các cổng {PORTS.start}–{PORTS.stop - 1} đều đang bị chương trình khác dùng.")


def remember_port(port: int) -> None:
    _instance_file().write_text(json.dumps({"port": port, "pid": os.getpid()}), encoding="utf-8")


_MUTEX = None


def hold_mutex() -> None:
    """Windows: đánh dấu "VoxViet đang chạy" để trình cài/gỡ nhắc đóng phần mềm trước (AppMutex)."""
    global _MUTEX
    if os.name == "nt" and _MUTEX is None:
        try:
            import ctypes
            _MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, "VoxVietStudio.Running")
        except Exception:
            pass


def message_box(text: str, title: str = "VoxViet Studio") -> None:
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, text, title, 0x10)  # MB_ICONERROR
            return
        except Exception:
            pass
    print(f"{title}: {text}", file=sys.stderr)
