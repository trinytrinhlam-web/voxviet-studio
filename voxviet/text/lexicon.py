"""Từ điển phát âm do người dùng định nghĩa.

Ví dụ: muốn "VoxViet" đọc thành "vốc việt", hay "SQL" đọc là "<en>sequel</en>".
File: ``data/lexicon.default.json`` (mặc định, đi kèm phần mềm) và
``data/lexicon.json`` (của bạn, ghi đè mặc định). Cấu trúc::

    {"vi": {"từ gốc": "cách đọc"}, "en": {...}, "all": {...}}

Khoá có chữ HOA → so khớp phân biệt hoa/thường; khoá toàn chữ thường → không phân biệt.
Luôn so khớp nguyên từ (không thay giữa chừng một từ khác).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths

SECTIONS = ("all", "vi", "en")


@dataclass
class Lexicon:
    entries: dict[str, dict[str, str]] = field(default_factory=lambda: {s: {} for s in SECTIONS})
    _compiled: dict[str, list[tuple[re.Pattern, str]]] = field(default_factory=dict, repr=False)

    @classmethod
    def load(cls, default: Path | None = None, user: Path | None = None) -> "Lexicon":
        lex = cls()
        for p in (default or paths.LEXICON_DEFAULT, user or paths.LEXICON_USER):
            if p and Path(p).exists():
                try:
                    raw = json.loads(Path(p).read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                for sec in SECTIONS:
                    lex.entries[sec].update({k: v for k, v in (raw.get(sec) or {}).items() if k})
        return lex

    def save_user(self, path: Path | None = None) -> None:
        p = Path(path or paths.LEXICON_USER)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.entries, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_entries(self, rows: list[tuple[str, str, str]]) -> None:
        """rows: [(section, word, reading)]"""
        self.entries = {s: {} for s in SECTIONS}
        for sec, word, reading in rows:
            sec = (sec or "all").strip().lower()
            if sec not in SECTIONS:
                sec = "all"
            word, reading = (word or "").strip(), (reading or "").strip()
            if word and reading:
                self.entries[sec][word] = reading
        self._compiled.clear()

    def rows(self) -> list[list[str]]:
        return [[sec, w, r] for sec in SECTIONS for w, r in self.entries[sec].items()]

    def _patterns(self, lang: str) -> list[tuple[re.Pattern, str]]:
        if lang not in self._compiled:
            merged: dict[str, str] = {}
            merged.update(self.entries.get("all", {}))
            merged.update(self.entries.get(lang, {}))
            pats = []
            for word in sorted(merged, key=len, reverse=True):
                flags = 0 if any(ch.isupper() for ch in word) else re.IGNORECASE
                pats.append((re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", flags), merged[word]))
            self._compiled[lang] = pats
        return self._compiled[lang]

    def apply(self, text: str, lang: str = "vi") -> str:
        for pat, reading in self._patterns(lang):
            text = pat.sub(lambda _m, r=reading: r, text)
        return text
