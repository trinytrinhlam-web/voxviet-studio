"""Cài đặt người dùng, lưu ở ``data/settings.json``."""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field, fields
from typing import Any

from . import paths


@dataclass
class Settings:
    # Thiết bị chạy mô hình: "auto" | "cuda" | "cpu"
    device: str = "auto"
    # CPU: "fp32" (chất lượng cao) | "int8" (nhanh, cần CPU hỗ trợ VNNI)
    cpu_precision: str = "fp32"
    # Phương ngữ mặc định cho cách đọc số: "bac" | "nam"
    dialect: str = "bac"
    # Định dạng xuất: "wav" | "mp3"
    output_format: str = "wav"
    # Chuẩn hoá âm lượng (LUFS). 0 = tắt.
    target_lufs: float = -16.0
    # Khoảng nghỉ giữa các câu (giây) — nhân thêm theo "nhịp nghỉ" trong giao diện
    sentence_pause: float = 0.25
    paragraph_pause: float = 0.6
    # Google (chỉ để so sánh, cần Internet)
    gemini_api_key: str = ""
    gemini_model: str = ""  # để trống = tự chọn model TTS mới nhất tìm được
    gemini_voice: str = "Kore"
    # Engine tiếng Anh: "vieneu" | "chatterbox"
    english_engine: str = "vieneu"
    # Đường dẫn backbone VieNeu tuỳ chỉnh (mô hình đã fine-tune). Trống = mặc định.
    vieneu_backbone: str = ""
    extra: dict = field(default_factory=dict)


_lock = threading.Lock()
_cached: Settings | None = None


def load() -> Settings:
    global _cached
    with _lock:
        if _cached is not None:
            return _cached
        s = Settings()
        if paths.SETTINGS.exists():
            try:
                raw = json.loads(paths.SETTINGS.read_text(encoding="utf-8"))
                known = {f.name for f in fields(Settings)}
                for k, v in raw.items():
                    if k in known:
                        setattr(s, k, v)
            except (OSError, ValueError):
                pass
        _cached = s
        return s


def save(s: Settings) -> None:
    global _cached
    with _lock:
        paths.SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        paths.SETTINGS.write_text(json.dumps(asdict(s), ensure_ascii=False, indent=2), encoding="utf-8")
        _cached = s


def update(**changes: Any) -> Settings:
    s = load()
    for k, v in changes.items():
        if hasattr(s, k):
            setattr(s, k, v)
    save(s)
    return s
