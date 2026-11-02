"""Phòng thu: đọc kịch bản, lưu từng câu, xuất bộ dữ liệu để fine-tune.

Mỗi phiên thu là một thư mục ``data/recordings/<tên phiên>/`` đúng định dạng
fine-tune của bộ huấn luyện::

    metadata.csv      file_name|text  (mỗi dòng một câu đã thu)
    raw_audio/<mã>.flac
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from . import audio, paths
from .text import emotions
from .voices import VoiceLibrary, slugify

SCRIPT_FILE = paths.RECORDING_SCRIPT / "script_vi_en.txt"
GROUP_LABELS = {"vi": "Tiếng Việt", "mix": "Việt xen Anh", "emo": "Cảm xúc", "en": "Tiếng Anh"}


@dataclass
class ScriptItem:
    id: str
    group: str
    emotion: str
    text: str


def load_script(path: Path | None = None) -> list[ScriptItem]:
    items = []
    for line in Path(path or SCRIPT_FILE).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|", 3)
        if len(parts) == 4:
            items.append(ScriptItem(*[p.strip() for p in parts]))
    return items


class Session:
    def __init__(self, name: str):
        self.name = slugify(name)
        self.dir = paths.RECORDINGS / self.name
        self.audio_dir = self.dir / "raw_audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_names() -> list[str]:
        if not paths.RECORDINGS.exists():
            return []
        return sorted(d.name for d in paths.RECORDINGS.iterdir() if d.is_dir())

    def take_path(self, item_id: str) -> Path:
        return self.audio_dir / f"{item_id}.flac"  # FLAC: nhẹ hơn WAV ~50%, dễ đồng bộ GitHub

    def has(self, item_id: str) -> bool:
        return self.take_path(item_id).exists()

    def save_take(self, item: ScriptItem, src: str | Path) -> tuple[Path, float, list[str]]:
        x = audio.trim(audio.load(src, audio.SR), audio.SR, keep=0.15)
        dur = audio.duration(x)
        warns = []
        if dur < 1.0:
            raise ValueError("Bản thu gần như im lặng — kiểm tra micro.")
        if dur > 15.0:
            warns.append(f"Câu dài {dur:.1f}s (>15s) sẽ bị bỏ qua khi fine-tune; nên đọc nhanh hơn chút.")
        if float(abs(x).max()) >= 0.999:
            warns.append("Bị vỡ tiếng (clipping) — để micro xa hơn hoặc giảm âm lượng thu.")
        x = audio.loudness_normalize(x, audio.SR, -20.0)
        out = audio.save(x, self.take_path(item.id), audio.SR)
        self.write_metadata()
        return out, dur, warns

    def delete_take(self, item_id: str) -> None:
        self.take_path(item_id).unlink(missing_ok=True)
        self.write_metadata()

    def write_metadata(self, script: list[ScriptItem] | None = None, groups: set[str] | None = None) -> Path:
        script = script or load_script()
        meta = self.dir / "metadata.csv"
        with open(meta, "w", encoding="utf-8", newline="") as f:
            for it in script:
                if self.has(it.id) and (groups is None or it.group in groups):
                    f.write(f"{self.take_path(it.id).name}|{it.text}\n")
        return meta

    def stats(self, script: list[ScriptItem] | None = None) -> dict:
        import soundfile as sf
        script = script or load_script()
        done, total_sec = 0, 0.0
        per_group: dict[str, list[int]] = {}
        for it in script:
            g = per_group.setdefault(it.group, [0, 0])
            g[1] += 1
            if self.has(it.id):
                done += 1
                g[0] += 1
                try:
                    total_sec += sf.info(str(self.take_path(it.id))).duration
                except Exception:
                    pass
        return {"done": done, "total": len(script), "seconds": total_sec, "groups": per_group}

    def stats_text(self) -> str:
        st = self.stats()
        groups = ", ".join(f"{GROUP_LABELS.get(k, k)} {a}/{b}" for k, (a, b) in st["groups"].items())
        mins = st["seconds"] / 60
        hint = ("✅ Đủ để fine-tune (≥10 phút)." if mins >= 10 else
                f"Cần thêm ~{10 - mins:.0f} phút để fine-tune (clone tức thì thì chỉ cần 1 câu).")
        return f"Đã thu {st['done']}/{st['total']} câu — {mins:.1f} phút. {groups}. {hint}"

    def build_voice(self, library: VoiceLibrary, voice_name: str, dialect: str = "bac") -> tuple[str, list[str]]:
        """Tạo giọng trong Kho giọng từ các câu đã thu: mỗi cảm xúc chọn câu 5–10 giây."""
        import soundfile as sf
        script = load_script()
        best: dict[str, tuple[float, Path]] = {}
        for it in script:
            p = self.take_path(it.id)
            if not p.exists():
                continue
            try:
                d = sf.info(str(p)).duration
            except Exception:
                continue
            key = f"en_{it.emotion}" if it.group == "en" else it.emotion
            score = abs(d - 7.0)  # gần 7 giây là tốt nhất
            if key not in best or score < best[key][0]:
                best[key] = (score, p)
        if emotions.DEFAULT not in best:
            raise ValueError("Cần thu ít nhất một câu trung tính tiếng Việt trước.")
        existing = next((v for v in library.list() if v.name.lower() == voice_name.strip().lower()), None)
        v = existing or library.create(voice_name, dialect)
        notes = []
        for key, (_s, p) in sorted(best.items()):
            english = key.startswith("en_")
            emo = key[3:] if english else key
            _out, w = library.add_clip(v.id, p, emo, english=english)
            notes += w
        return v.id, [f"Đã gán {len(best)} mẫu: {', '.join(sorted(best))}"] + notes


def export_csv_for_review(session: Session, out: Path) -> Path:
    """Xuất bảng (mã, nhóm, đã thu, câu) để xem lại trong Excel."""
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma", "nhom", "cam_xuc", "da_thu", "cau"])
        for it in load_script():
            w.writerow([it.id, it.group, it.emotion, "x" if session.has(it.id) else "", it.text])
    return out
