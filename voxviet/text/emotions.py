"""Danh sách cảm xúc và cách mỗi engine thể hiện chúng.

VieNeu v3 Turbo lấy "chất giọng/cảm xúc" từ CHÍNH đoạn giọng mẫu. Vì vậy cách
hiệu quả nhất là thu mỗi cảm xúc một đoạn mẫu riêng (xem Kho giọng). Khi giọng
không có mẫu cho cảm xúc đó, phần mềm dùng mẫu trung tính và chỉ chỉnh nhẹ tốc
độ + độ "biến hoá" (temperature).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Emotion:
    key: str
    label: str
    speed: float  # hệ số tốc độ cộng thêm
    temperature: float  # VieNeu: độ biến hoá ngữ điệu
    exaggeration: float  # Chatterbox: mức cường điệu cảm xúc (0.25–2.0)
    gemini_style: str  # câu chỉ dẫn phong cách cho Gemini TTS
    aliases: tuple[str, ...] = ()


EMOTIONS: dict[str, Emotion] = {
    e.key: e
    for e in (
        Emotion("trung_tinh", "Trung tính", 1.00, 0.80, 0.50, "", ("trung tính", "trung tinh", "neutral", "bình thường")),
        Emotion("vui", "Vui vẻ", 1.05, 0.90, 0.75, "Say cheerfully, with a warm smile", ("vui", "vui vẻ", "happy")),
        Emotion("buon", "Buồn", 0.92, 0.75, 0.40, "Say sadly, slowly, with a heavy heart", ("buồn", "buon", "sad")),
        Emotion("gian", "Giận dữ", 1.04, 0.95, 0.90, "Say angrily, with frustration", ("giận", "giận dữ", "gian", "angry")),
        Emotion("ngac_nhien", "Ngạc nhiên", 1.03, 0.90, 0.80, "Say with surprise and amazement", ("ngạc nhiên", "ngac nhien", "surprised")),
        Emotion("thi_tham", "Thì thầm", 0.95, 0.70, 0.35, "Whisper softly", ("thì thầm", "thi tham", "whisper")),
        Emotion("ke_chuyen", "Kể chuyện", 0.97, 0.80, 0.55, "Narrate like an audiobook storyteller, calm and engaging", ("kể chuyện", "ke chuyen", "narrator")),
    )
}

DEFAULT = "trung_tinh"

_ALIAS: dict[str, str] = {}
for _e in EMOTIONS.values():
    _ALIAS[_e.key] = _e.key
    _ALIAS[_e.label.lower()] = _e.key
    for _a in _e.aliases:
        _ALIAS[_a.lower()] = _e.key


def resolve(name: str | None) -> str | None:
    """Tên cảm xúc (tiếng Việt có/không dấu, tiếng Anh, hoặc key) → key; None nếu lạ."""
    if not name:
        return None
    return _ALIAS.get(name.strip().lower())


def get(name: str | None) -> Emotion:
    return EMOTIONS[resolve(name) or DEFAULT]


def choices() -> list[tuple[str, str]]:
    return [(e.label, e.key) for e in EMOTIONS.values()]
