"""Đường dẫn thư mục của dự án.

Mọi dữ liệu người dùng (kho giọng, bản thu, file xuất) nằm trong ``data/`` để dễ
chép sang máy khác. Mô hình tải về nằm trong ``models/`` (không đưa lên git).
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("VOXVIET_HOME", Path(__file__).resolve().parent.parent))
DATA = Path(os.environ.get("VOXVIET_DATA", ROOT / "data"))
VOICES = DATA / "voices"
OUTPUTS = DATA / "outputs"
RECORDINGS = DATA / "recordings"
RECORDING_SCRIPT = ROOT / "data" / "recording_script"
LEXICON_DEFAULT = ROOT / "data" / "lexicon.default.json"
LEXICON_USER = DATA / "lexicon.json"
SETTINGS = DATA / "settings.json"
MODELS = Path(os.environ.get("VOXVIET_MODELS", ROOT / "models"))
ENVS = ROOT / "envs"
TOOLS = ROOT / "tools"


def ensure_dirs() -> None:
    for p in (DATA, VOICES, OUTPUTS, RECORDINGS, MODELS):
        p.mkdir(parents=True, exist_ok=True)
