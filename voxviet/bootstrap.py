"""Thiết lập môi trường TRƯỚC khi nạp thư viện mô hình (không import gì nặng ở đây).

Mô hình lõi giọng được lưu trong ``models/voxviet-core`` của dự án. Bản cài cũ để
mô hình ở ``models/hf/hub`` → tự chuyển sang thư mục mới (không phải tải lại).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = Path(os.environ.get("VOXVIET_MODELS", ROOT / "models"))
CORE_DIR = MODELS / "voxviet-core"
READY_MARK = MODELS / ".models_ready"


def migrate_model_dir() -> None:
    old = MODELS / "hf" / "hub"
    if old.is_dir() and not CORE_DIR.exists():
        try:
            CORE_DIR.parent.mkdir(parents=True, exist_ok=True)
            os.replace(old, CORE_DIR)
        except OSError:
            pass  # đang bị khoá (ví dụ app khác mở) → dùng tạm chỗ cũ ở lần sau


def setup_env(online: bool = False) -> None:
    migrate_model_dir()
    os.environ.setdefault("HF_HOME", str(MODELS / "hf"))
    os.environ.setdefault("HF_HUB_CACHE", str(CORE_DIR))
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
    if online:
        os.environ.pop("HF_HUB_OFFLINE", None)
    elif READY_MARK.exists():
        # Đã tải mô hình → chạy hoàn toàn offline, không gọi mạng.
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass
