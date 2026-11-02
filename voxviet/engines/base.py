"""Giao diện chung cho mọi bộ máy đọc (engine).

Phần mềm không phụ thuộc vào một mô hình cụ thể: mỗi engine là một "phích cắm".
Muốn thêm mô hình mới chỉ cần viết một lớp con của ``TTSEngine`` và đăng ký
trong ``voxviet/engines/__init__.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

import numpy as np


@dataclass
class SynthRequest:
    text: str  # đã chuẩn hoá
    language: str = "vi"  # "vi" | "en"
    ref_audio: str | None = None  # đoạn giọng mẫu (clone)
    preset: str | None = None  # tên giọng có sẵn của engine
    emotion: str = "trung_tinh"
    temperature: float | None = None
    backbone: str | None = None  # mô hình tuỳ chỉnh (fine-tune)
    extra: dict = field(default_factory=dict)


class EngineUnavailable(RuntimeError):
    pass


class TTSEngine:
    id: str = "base"
    label: str = "Base"
    languages: tuple[str, ...] = ("vi", "en")
    online: bool = False  # cần Internet?
    supports_clone: bool = False
    supports_stream: bool = False
    sample_rate: int = 48_000
    description: str = ""

    def available(self) -> tuple[bool, str]:
        """(có dùng được không, lý do nếu không)."""
        return True, ""

    def presets(self, language: str = "vi") -> list[tuple[str, str]]:
        """Danh sách giọng có sẵn [(nhãn, id)]."""
        return []

    def load(self) -> None:  # tải mô hình (lười)
        pass

    def unload(self) -> None:
        pass

    def synthesize(self, req: SynthRequest) -> np.ndarray:
        raise NotImplementedError

    def stream(self, req: SynthRequest) -> Iterator[np.ndarray]:
        yield self.synthesize(req)
