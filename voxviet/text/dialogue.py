"""Đọc kịch bản hội thoại nhiều nhân vật.

Định dạng (mỗi dòng một lượt nói)::

    Người kể: Chiều hôm ấy, trời đổ mưa.
    Minh (vui): Lan ơi, lâu quá không gặp!
    [Lan] (ngạc nhiên): Ủa, Minh hả? Sao bạn ở đây?
    Lan: [thì thầm] Nói nhỏ thôi...   ← thẻ trong lời thoại vẫn dùng được
    # dòng bắt đầu bằng # là ghi chú, bị bỏ qua
    Dòng không có tên → thuộc về nhân vật của dòng trước.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import emotions
from .normalize import nfc

NARRATOR = "Người kể"

_LINE_RE = re.compile(
    r"^\s*\[?(?P<name>[^\[\]():：\n]{1,40}?)\]?\s*(?:\((?P<emo>[^()\n]{1,30})\))?\s*[:：](?:\s+|$)(?P<text>.*)$"
)


@dataclass
class Line:
    speaker: str
    text: str
    emotion: str | None = None  # None = dùng cảm xúc mặc định của nhân vật


def parse(script: str) -> list[Line]:
    lines: list[Line] = []
    for raw in nfc(script).splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        m = _LINE_RE.match(s)
        if m and len(m.group("name").split()) <= 4:
            name = m.group("name").strip()
            emo = emotions.resolve(m.group("emo")) if m.group("emo") else None
            text = m.group("text").strip()
            if text:
                lines.append(Line(name, text, emo))
            continue
        speaker = lines[-1].speaker if lines else NARRATOR
        lines.append(Line(speaker, s, None))
    return lines


def speakers(lines: list[Line]) -> list[str]:
    seen: list[str] = []
    for ln in lines:
        if ln.speaker not in seen:
            seen.append(ln.speaker)
    return seen
