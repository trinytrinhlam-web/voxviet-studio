"""Đọc/ghi phụ đề SRT (dùng cho lồng tiếng video)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .normalize import nfc

_TIME = r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})"
_CUE_RE = re.compile(rf"{_TIME}\s*-->\s*{_TIME}")


@dataclass
class Cue:
    index: int
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


def _sec(h, m, s, ms) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000.0


def parse(srt_text: str) -> list[Cue]:
    cues: list[Cue] = []
    blocks = re.split(r"\n\s*\n", nfc(srt_text).replace("\r\n", "\n").strip())
    for block in blocks:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        for i, ln in enumerate(lines):
            m = _CUE_RE.search(ln)
            if m:
                text = " ".join(t.strip() for t in lines[i + 1:])
                text = re.sub(r"<[^>]+>|\{[^}]+\}", "", text).strip()  # bỏ thẻ định dạng
                if text:
                    g = m.groups()
                    cues.append(Cue(len(cues) + 1, _sec(*g[:4]), _sec(*g[4:]), text))
                break
    return cues


def fmt_time(t: float) -> str:
    t = max(0.0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write(cues: list[Cue]) -> str:
    return "\n".join(f"{i}\n{fmt_time(c.start)} --> {fmt_time(c.end)}\n{c.text}\n" for i, c in enumerate(cues, 1))
