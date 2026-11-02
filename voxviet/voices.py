"""Kho giọng của người dùng (tối đa 10 giọng).

Mỗi giọng là một thư mục ``data/voices/<id>/``::

    voice.json          thông tin giọng
    clips/<cảm xúc>.wav đoạn mẫu cho từng cảm xúc (trung_tinh.wav là bắt buộc)
    clips/en_<cảm xúc>.wav  (tuỳ chọn) mẫu nói tiếng Anh — giúp module tiếng Anh chuẩn hơn

Giọng có sẵn của VoxViet (Bắc/Trung/Nam) không tính vào giới hạn 10.
"""

from __future__ import annotations

import json
import re
import shutil
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import audio, paths
from .text import emotions

MAX_VOICES = 10
CLIP_MIN_SEC = 3.0
CLIP_MAX_SEC = 15.0
PRESET_PREFIX = "preset:"


@dataclass
class Voice:
    id: str
    name: str
    dialect: str = "bac"  # bac | nam | trung
    gender: str = ""
    description: str = ""
    clips: dict[str, str] = field(default_factory=dict)  # khoá cảm xúc → tên file
    backbone: str = ""  # thư mục mô hình fine-tune (tuỳ chọn)
    gemini_voice: str = ""  # giọng Gemini tương ứng khi so sánh
    avatar: str = ""  # ảnh đại diện (tên file trong web/avatars, không đuôi)
    created: float = field(default_factory=time.time)

    @property
    def folder(self) -> Path:
        return (getattr(self, "_root", None) or paths.VOICES) / self.id

    def clip_path(self, key: str) -> Path | None:
        name = self.clips.get(key)
        if not name:
            return None
        p = self.folder / "clips" / name
        return p if p.exists() else None

    def ref_for(self, emotion: str = emotions.DEFAULT, language: str = "vi") -> Path | None:
        """Chọn đoạn mẫu phù hợp nhất cho cảm xúc + ngôn ngữ."""
        emotion = emotions.resolve(emotion) or emotions.DEFAULT
        order = []
        if language == "en":
            order += [f"en_{emotion}"]
        order += [emotion]
        if language == "en":
            order += [f"en_{emotions.DEFAULT}"]
        order += [emotions.DEFAULT]
        for k in order:
            p = self.clip_path(k)
            if p:
                return p
        for k in self.clips:
            p = self.clip_path(k)
            if p:
                return p
        return None


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFD", name.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "giong"


class VoiceLibrary:
    def __init__(self, root: Path | None = None):
        self.root = Path(root or paths.VOICES)
        self.root.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[Voice]:
        out = []
        for d in sorted(self.root.iterdir()):
            f = d / "voice.json"
            if f.exists():
                try:
                    raw = json.loads(f.read_text(encoding="utf-8"))
                    known = Voice.__dataclass_fields__.keys()
                    v = Voice(**{k: val for k, val in raw.items() if k in known})
                    v._root = self.root
                    out.append(v)
                except (OSError, ValueError, TypeError):
                    continue
        out.sort(key=lambda v: v.created)
        return out

    def get(self, voice_id: str) -> Voice | None:
        for v in self.list():
            if v.id == voice_id:
                return v
        return None

    def _save(self, v: Voice) -> None:
        v.folder.mkdir(parents=True, exist_ok=True)
        (v.folder / "voice.json").write_text(json.dumps(asdict(v), ensure_ascii=False, indent=2), encoding="utf-8")

    def create(self, name: str, dialect: str = "bac", gender: str = "", description: str = "") -> Voice:
        name = (name or "").strip()
        if not name:
            raise ValueError("Hãy đặt tên cho giọng.")
        existing = self.list()
        if len(existing) >= MAX_VOICES:
            raise ValueError(f"Kho đã đủ {MAX_VOICES} giọng. Xoá bớt một giọng trước khi thêm.")
        if any(v.name.lower() == name.lower() for v in existing):
            raise ValueError(f"Đã có giọng tên '{name}'.")
        base = slugify(name)
        vid, i = base, 2
        while (self.root / vid).exists():
            vid, i = f"{base}-{i}", i + 1
        gender = {"male": "nam", "female": "nu"}.get(gender, gender)
        v = Voice(id=vid, name=name, dialect=dialect, gender=gender, description=description)
        v._root = self.root
        self._save(v)
        return v

    def update(self, voice_id: str, **changes) -> Voice:
        v = self.get(voice_id)
        if v is None:
            raise ValueError("Không tìm thấy giọng.")
        if "gender" in changes:
            changes["gender"] = {"male": "nam", "female": "nu"}.get(changes["gender"], changes["gender"])
        for k, val in changes.items():
            if k in ("name", "dialect", "gender", "description", "backbone", "gemini_voice", "avatar") and val is not None:
                setattr(v, k, val)
        self._save(v)
        return v

    def delete(self, voice_id: str) -> None:
        v = self.get(voice_id)
        if v is not None:
            shutil.rmtree(v.folder, ignore_errors=True)

    def add_clip(self, voice_id: str, src: str | Path, emotion: str = emotions.DEFAULT,
                 english: bool = False) -> tuple[Path, list[str]]:
        """Thêm đoạn mẫu; tự đổi sang mono 48 kHz, cắt lặng, giới hạn 15 giây.

        Trả về (đường dẫn file, danh sách cảnh báo)."""
        v = self.get(voice_id)
        if v is None:
            raise ValueError("Không tìm thấy giọng.")
        key = emotions.resolve(emotion) or emotions.DEFAULT
        if english:
            key = f"en_{key}"
        x = audio.trim(audio.load(src, audio.SR), audio.SR)
        warnings = []
        dur = audio.duration(x)
        if dur < CLIP_MIN_SEC:
            warnings.append(f"Đoạn mẫu chỉ {dur:.1f}s — nên từ 5–10 giây để giống giọng hơn.")
        if dur > CLIP_MAX_SEC:
            x = x[: int(CLIP_MAX_SEC * audio.SR)]
            warnings.append(f"Đoạn mẫu dài {dur:.0f}s, đã cắt còn {CLIP_MAX_SEC:.0f}s (lõi giọng dùng tối đa ~8s).")
        if len(x) and float(abs(x).max()) >= 0.999:
            warnings.append("Âm thanh bị rè/vỡ (clipping) — nên thu lại nhỏ hơn một chút.")
        x = audio.loudness_normalize(x, audio.SR, -20.0)
        out = v.folder / "clips" / f"{key}.wav"
        audio.save(x, out, audio.SR)
        v.clips[key] = out.name
        self._save(v)
        return out, warnings

    def remove_clip(self, voice_id: str, key: str) -> None:
        v = self.get(voice_id)
        if v and key in v.clips:
            p = v.clip_path(key)
            if p:
                p.unlink(missing_ok=True)
            v.clips.pop(key, None)
            self._save(v)
