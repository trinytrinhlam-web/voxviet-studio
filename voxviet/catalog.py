"""Bộ giọng có sẵn của VoxViet Studio (``data/giong_co_san.json``).

Mỗi giọng mang tên riêng của phần mềm; mã giọng gốc trong lõi ("nen") chỉ dùng nội bộ.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache

from . import paths

CATALOG_FILE = paths.ROOT / "data" / "giong_co_san.json"
REGION_LABEL = {"bac": "miền Bắc", "trung": "miền Trung", "nam": "miền Nam"}
GENDER_LABEL = {"nam": "Nam", "nu": "Nữ"}


@dataclass(frozen=True)
class PresetVoice:
    id: str
    name: str
    base: str
    region: str
    gender: str
    style: str
    hidden: bool = False
    enhance: str | None = None
    dereverb: str | None = None
    avatar: str = ""

    @property
    def description(self) -> str:
        return f"{GENDER_LABEL.get(self.gender, '')} · {REGION_LABEL.get(self.region, '')} · {self.style}"


@lru_cache(maxsize=1)
def _load() -> tuple[str, tuple[PresetVoice, ...]]:
    raw = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    voices = tuple(
        PresetVoice(id=v["id"], name=v["ten"], base=v["nen"], region=v.get("vung", ""),
                    gender=v.get("gioi", ""), style=v.get("phong_cach", ""), hidden=bool(v.get("an")),
                    enhance=v.get("lam_trong"), dereverb=v.get("giam_vang"), avatar=v.get("anh", ""))
        for v in raw.get("giong", [])
    )
    return raw.get("mac_dinh", voices[0].id if voices else ""), voices


def all_voices(include_hidden: bool = False) -> list[PresetVoice]:
    return [v for v in _load()[1] if include_hidden or not v.hidden]


def default_id() -> str:
    return _load()[0]


def get(voice_id: str) -> PresetVoice | None:
    """Theo mã của VoxViet; chấp nhận cả mã giọng gốc (tương thích cài đặt cũ)."""
    for v in _load()[1]:
        if v.id == voice_id or v.base == voice_id:
            return v
    return None
