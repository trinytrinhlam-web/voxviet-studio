"""Chuẩn bị văn bản trước khi đưa vào mô hình.

Gồm:
  * Thẻ điều khiển trong văn bản (cảm xúc, nghỉ, âm phi ngôn ngữ).
  * Chuẩn hoá tiếng Việt (số, ngày, tiền, viết tắt) qua ``sea-g2p`` — thư viện
    mà VieNeu-TTS dùng, có nhận diện từ tiếng Anh xen kẽ để đọc chuẩn tiếng Anh.
  * Khác biệt cách đọc số Bắc/Nam ("nghìn"/"ngàn", "linh"/"lẻ").
  * Chuẩn hoá tiếng Anh (đọc số theo tiếng Anh).
  * Chia văn bản dài thành các đoạn vừa phải.

Thẻ hỗ trợ (đặt trong ngoặc vuông)::

    [vui] [buồn] [giận] [ngạc nhiên] [thì thầm] [kể chuyện] [trung tính]
        → đổi cảm xúc cho phần văn bản phía sau
    [nghỉ 1.5s] [nghỉ 500ms] [nghỉ] [pause 2s]
        → chèn khoảng lặng
    [cười] [thở dài] [hắng giọng]   (hoặc [chuckle] [sigh] [clear throat])
        → âm thanh phi ngôn ngữ, VieNeu tự xử lý
    <en>...</en>
        → ép đọc tiếng Anh một cụm từ (khi tự nhận diện bị nhầm)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from . import emotions
from .en_numbers import expand_numbers
from .lexicon import Lexicon

NONVERBAL = {"cười", "cuoi", "thở dài", "tho dai", "hắng giọng", "hang giong", "chuckle", "sigh", "clear throat"}

_TAG_RE = re.compile(r"\[([^\[\]\n]{1,40})\]")
_PAUSE_RE = re.compile(r"^(?:nghỉ|nghi|pause|dừng|dung)\s*(\d+(?:[.,]\d+)?)?\s*(ms|s|giây|giay)?$", re.IGNORECASE)
DEFAULT_PAUSE = 0.7


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


@dataclass
class Segment:
    kind: str  # "text" | "pause"
    text: str = ""
    emotion: str = emotions.DEFAULT
    seconds: float = 0.0


def parse_inline(text: str, emotion: str = emotions.DEFAULT) -> list[Segment]:
    """Tách thẻ cảm xúc / nghỉ. Thẻ phi ngôn ngữ giữ nguyên trong văn bản."""
    text = nfc(text)
    segs: list[Segment] = []
    cur = emotions.resolve(emotion) or emotions.DEFAULT
    pos = 0
    buf: list[str] = []

    def flush():
        joined = "".join(buf).strip()
        buf.clear()
        if joined:
            segs.append(Segment("text", joined, cur))

    for m in _TAG_RE.finditer(text):
        inner = m.group(1).strip()
        low = inner.lower()
        emo = emotions.resolve(low)
        pause = _PAUSE_RE.match(low)
        if emo is None and pause is None:
            continue  # thẻ phi ngôn ngữ hoặc ngoặc vuông thường: để nguyên
        buf.append(text[pos:m.start()])
        pos = m.end()
        flush()
        if emo is not None:
            cur = emo
        else:
            val, unit = pause.group(1), (pause.group(2) or "s").lower()
            sec = float(val.replace(",", ".")) if val else DEFAULT_PAUSE
            if unit == "ms":
                sec /= 1000.0
            segs.append(Segment("pause", seconds=max(0.0, min(sec, 30.0)), emotion=cur))
    buf.append(text[pos:])
    flush()
    return segs


# ── Tiếng Việt ────────────────────────────────────────────────────────────────

_normalizer = None
_normalizer_failed = False


def _sea_normalize(text: str) -> str:
    global _normalizer, _normalizer_failed
    if _normalizer_failed:
        return text
    if _normalizer is None:
        try:
            from sea_g2p import Normalizer
            _normalizer = Normalizer(lang="vi")
        except Exception:  # thư viện chưa cài: để VieNeu tự chuẩn hoá
            _normalizer_failed = True
            return text
    return _normalizer.normalize(text)


_NUMW = r"(?:không|một|mốt|hai|ba|bốn|tư|năm|lăm|nhăm|sáu|bảy|tám|chín|mười|mươi|trăm|chục)"
_DIALECT_RULES = {
    "bac": [
        (re.compile(rf"\b({_NUMW}) ngàn\b"), r"\1 nghìn"),
        (re.compile(r"\btrăm lẻ\b"), "trăm linh"),
        (re.compile(r"\bnghìn lẻ\b"), "nghìn linh"),
    ],
    "nam": [
        (re.compile(rf"\b({_NUMW}) nghìn\b"), r"\1 ngàn"),
        (re.compile(r"\btrăm linh\b"), "trăm lẻ"),
        (re.compile(r"\bngàn linh\b"), "ngàn lẻ"),
    ],
}


def apply_dialect(text: str, dialect: str) -> str:
    for pat, rep in _DIALECT_RULES.get(dialect, []):
        text = pat.sub(rep, text)
    return text


_NONVERBAL_SPLIT = re.compile(r"(\[[^\[\]\n]{1,40}\])")


def prepare_vi(text: str, dialect: str = "bac", lexicon: Lexicon | None = None) -> str:
    """Chuẩn hoá văn bản tiếng Việt (có thể xen tiếng Anh)."""
    text = nfc(text)
    if lexicon is not None:
        text = lexicon.apply(text, "vi")
    parts = _NONVERBAL_SPLIT.split(text)
    out = []
    for p in parts:
        if not p:
            continue
        if _NONVERBAL_SPLIT.fullmatch(p):
            out.append(f" {p} ")
            continue
        if p.strip():
            out.append(apply_dialect(_sea_normalize(p), dialect))
    return re.sub(r"\s+", " ", "".join(out)).strip()


# ── Tiếng Anh ─────────────────────────────────────────────────────────────────

def prepare_en(text: str, lexicon: Lexicon | None = None) -> str:
    text = nfc(text)
    if lexicon is not None:
        text = lexicon.apply(text, "en")
    text = expand_numbers(text)
    text = text.replace("&", " and ").replace("@", " at ")
    return re.sub(r"\s+", " ", text).strip()


def prepare(text: str, language: str, dialect: str = "bac", lexicon: Lexicon | None = None) -> str:
    return prepare_en(text, lexicon) if language == "en" else prepare_vi(text, dialect, lexicon)


# ── Chia đoạn ─────────────────────────────────────────────────────────────────

# Kết thúc câu: . ! ? … theo sau bởi khoảng trắng + (chữ hoa | ngoặc | số), hoặc hết chuỗi.
_SENT_END = re.compile(r"(?<=[.!?…])[\"”’)\]]*\s+(?=[\"“‘(\[]*[A-ZÀ-ỸĐ0-9<])")
_ABBREV = re.compile(r"\b(?:TP|Mr|Mrs|Ms|Dr|St|Th\.S|TS|PGS|GS|ThS|Tp|vs|etc|e\.g|i\.e)\.$", re.IGNORECASE)
_SOFT_BREAK = re.compile(r"(?<=[,;:—–])\s+")


@dataclass
class Chunk:
    text: str
    pause_after: str  # "sentence" | "paragraph" | "none"


def split_sentences(paragraph: str) -> list[str]:
    raw = _SENT_END.split(paragraph.strip())
    out: list[str] = []
    for s in raw:
        if out and _ABBREV.search(out[-1]):
            out[-1] = f"{out[-1]} {s}"
        else:
            out.append(s)
    return [s.strip() for s in out if s.strip()]


def _split_long(sentence: str, max_chars: int) -> list[str]:
    if len(sentence) <= max_chars:
        return [sentence]
    pieces, cur = [], ""
    for part in _SOFT_BREAK.split(sentence):
        if cur and len(cur) + 1 + len(part) > max_chars:
            pieces.append(cur)
            cur = part
        else:
            cur = f"{cur} {part}".strip()
    if cur:
        pieces.append(cur)
    final = []
    for p in pieces:
        while len(p) > max_chars:
            cut = p.rfind(" ", 0, max_chars)
            cut = cut if cut > max_chars // 3 else max_chars
            final.append(p[:cut].strip())
            p = p[cut:].strip()
        if p:
            final.append(p)
    return final


def split_chunks(text: str, max_chars: int = 220, group: bool = True) -> list[Chunk]:
    """Chia văn bản thành các đoạn ≤ max_chars, giữ ranh giới câu/đoạn văn.

    group=True gộp các câu ngắn liền nhau (ngữ điệu liền mạch hơn);
    group=False mỗi câu một đoạn (độ trễ thấp cho chế độ trực tiếp).
    """
    chunks: list[Chunk] = []
    paragraphs = [p for p in re.split(r"\n\s*\n|\r?\n", nfc(text)) if p.strip()]
    for pi, para in enumerate(paragraphs):
        sents: list[str] = []
        for s in split_sentences(para):
            sents.extend(_split_long(s, max_chars))
        merged: list[str] = []
        for s in sents:
            if group and merged and len(merged[-1]) + 1 + len(s) <= max_chars:
                merged[-1] = f"{merged[-1]} {s}"
            else:
                merged.append(s)
        for si, s in enumerate(merged):
            last_in_para = si == len(merged) - 1
            pause = "paragraph" if last_in_para and pi < len(paragraphs) - 1 else ("none" if last_in_para else "sentence")
            chunks.append(Chunk(s, pause))
    return chunks
