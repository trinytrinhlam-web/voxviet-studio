"""Bộ điều phối: văn bản → (chuẩn hoá, chia đoạn, cảm xúc, nghỉ) → engine → file âm thanh.

Dùng chung cho mọi chế độ: đọc văn bản / sách nói, hội thoại nhiều nhân vật,
lồng tiếng theo phụ đề SRT, và đọc trực tiếp (streaming).
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

import numpy as np

from . import audio, engines, paths
from . import settings as settings_mod
from .audio import enhance as enhance_mod
from .engines.base import EngineUnavailable, SynthRequest, TTSEngine
from .text import dialogue as dialogue_mod
from .text import emotions
from .text import normalize as norm
from .text import srt as srt_mod
from .text.lexicon import Lexicon
from .voices import PRESET_PREFIX, Voice, VoiceLibrary

log = logging.getLogger("voxviet.pipeline")

Progress = Callable[[float, str], None]
VOICE_PREFIX = "voice:"


@dataclass
class Result:
    path: Path
    duration: float
    subtitles: list[srt_mod.Cue] = field(default_factory=list)
    srt_path: Path | None = None
    warnings: list[str] = field(default_factory=list)
    elapsed: float = 0.0

    def summary(self) -> str:
        rtf = self.elapsed / self.duration if self.duration else 0
        s = f"✅ Xong: {self.duration:.1f}s âm thanh trong {self.elapsed:.1f}s (RTF {rtf:.2f}) → {self.path.name}"
        if self.warnings:
            s += "\n" + "\n".join(f"⚠️ {w}" for w in dict.fromkeys(self.warnings))
        return s


@dataclass
class ResolvedVoice:
    label: str
    ref_audio: str | None = None
    preset: str | None = None
    backbone: str | None = None
    dialect: str = "bac"
    voice: Voice | None = None


RAW_DIR_NAME = ".raw"  # bản thô (chưa hậu kỳ) của các lần đọc gần nhất — để thử lại mức làm trong
RAW_KEEP = 5


class _Writer:
    """Ghi âm thanh THÔ dần ra file (không giữ cả cuốn sách trong RAM).

    ``final`` là đường dẫn file kết quả; bản thô nằm ở ``outputs/.raw/``. Khi xong,
    ``_master`` đọc bản thô và xử lý hậu kỳ từng câu ra file kết quả."""

    def __init__(self, final: Path, sr: int = audio.SR):
        import soundfile as sf
        self.final = final
        path = final.parent / RAW_DIR_NAME / f"{final.stem}.wav"
        self.path = path
        self.sr = sr
        path.parent.mkdir(parents=True, exist_ok=True)
        self._f = sf.SoundFile(str(path), "w", samplerate=sr, channels=1, subtype="PCM_16")
        self.frames = 0

    @property
    def time(self) -> float:
        return self.frames / self.sr

    def write(self, x: np.ndarray) -> None:
        if x is not None and len(x):
            x = audio.peak_limit(np.asarray(x, dtype=np.float32))
            self._f.write(x)
            self.frames += len(x)

    def close(self) -> None:
        self._f.close()


def _out_path(name: str, ext: str = "wav") -> Path:
    from .voices import slugify
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return paths.OUTPUTS / f"{stamp}_{slugify(name)[:40]}.{ext}"


def _master(raw: Path, out: Path, spans: list[tuple[float, float]], preset: str | None,
            target_lufs: float, sr: int = audio.SR, dereverb: str | None = None,
            clean_fn: Callable[[np.ndarray], np.ndarray] | None = None) -> Path:
    """Hậu kỳ TỪNG câu (theo spans), giữ nguyên khoảng lặng:
    khử nhiễu AI (tuỳ chọn) → giảm vang → làm trong (EQ) → cân bằng âm lượng.

    Đọc/ghi theo khối nên dùng được cho sách nói dài hàng giờ."""
    import soundfile as sf
    out.parent.mkdir(parents=True, exist_ok=True)
    with sf.SoundFile(str(raw)) as fin, \
            sf.SoundFile(str(out), "w", samplerate=sr, channels=1, subtype="PCM_16") as fout:
        total, pos = fin.frames, 0

        def copy(n: int) -> None:
            nonlocal pos
            while n > 0:
                k = min(n, sr * 10)
                fout.write(fin.read(k, dtype="float32"))
                n -= k
                pos += k

        for a, b in sorted(spans):
            a = max(int(round(a * sr)), pos)
            b = min(int(round(b * sr)), total)
            if b <= a:
                continue
            copy(a - pos)
            seg = fin.read(b - a, dtype="float32")
            pos += b - a
            n = len(seg)
            if clean_fn is not None:
                seg = clean_fn(seg)
            seg = enhance_mod.dereverb(seg, dereverb, sr)
            seg = enhance_mod.process(seg, preset, sr)
            seg = np.pad(seg, (0, max(0, n - len(seg))))[:n]  # giữ đúng độ dài (khớp phụ đề)
            seg = audio.loudness_normalize(seg, sr, target_lufs)
            fout.write(seg)
        copy(total - pos)
    return out


def _cleanup_raw(folder: Path, keep: int = RAW_KEEP) -> None:
    files = sorted(folder.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in files[keep:]:
        p.unlink(missing_ok=True)


def _strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\[[^\]]{1,40}\]|</?en>", "", text)).strip()


class Studio:
    def __init__(self, library: VoiceLibrary | None = None, lexicon: Lexicon | None = None):
        paths.ensure_dirs()
        self.library = library or VoiceLibrary()
        self.lexicon = lexicon or Lexicon.load()
        # Bản thô của lần đọc gần nhất: (đường dẫn thô, spans, đường dẫn kết quả, engine id)
        self.last_take: tuple[Path, list[tuple[float, float]], Path] | None = None

    # ── giọng & engine ────────────────────────────────────────────────────────
    def voice_options(self, language: str = "vi", engine_id: str | None = None) -> list[tuple[str, str]]:
        eng = self.pick_engine(language, engine_id, check=False)
        opts: list[tuple[str, str]] = []
        if eng.supports_clone:
            opts += [(f"🎙️ {v.name} ({ {'bac': 'Bắc', 'nam': 'Nam', 'trung': 'Trung'}.get(v.dialect, v.dialect)})",
                      f"{VOICE_PREFIX}{v.id}") for v in self.library.list()]
        opts += [(f"📦 {label}", f"{PRESET_PREFIX}{pid}") for label, pid in eng.presets(language)]
        return opts

    def pick_engine(self, language: str, engine_id: str | None = None, check: bool = True) -> TTSEngine:
        if engine_id:
            eng = engines.get(engine_id)
        else:
            s = settings_mod.load()
            eng = engines.get("vieneu")
            if language == "en" and s.english_engine == "chatterbox":
                cb = engines.get("chatterbox")
                if cb.available()[0]:
                    eng = cb
            if "mock" in engines.registry():  # chế độ chạy thử (--demo)
                eng = engines.get("mock")
        if check:
            ok, why = eng.available()
            if not ok:
                raise EngineUnavailable(why)
        return eng

    def resolve_voice(self, value: str | None, emotion: str, language: str, eng: TTSEngine) -> ResolvedVoice:
        s = settings_mod.load()
        value = value or ""
        if value.startswith(VOICE_PREFIX):
            v = self.library.get(value[len(VOICE_PREFIX):])
            if v is None:
                raise ValueError("Giọng đã bị xoá khỏi kho.")
            if eng.supports_clone:
                ref = v.ref_for(emotion, language)
                if ref is None:
                    raise ValueError(f"Giọng '{v.name}' chưa có đoạn mẫu nào. Vào tab Kho giọng để thêm.")
                return ResolvedVoice(v.name, ref_audio=str(ref), backbone=v.backbone or None, dialect=v.dialect, voice=v)
            # engine không clone được (Google): dùng giọng tương ứng nếu có
            return ResolvedVoice(v.name, preset=v.gemini_voice or None, dialect=v.dialect, voice=v)
        if value.startswith(PRESET_PREFIX):
            pid = value[len(PRESET_PREFIX):]
            dialect = s.dialect
            if hasattr(eng, "preset_info"):
                for d in eng.preset_info():
                    if d["name"] == pid and d["region"] in ("bac", "nam"):
                        dialect = d["region"]
            return ResolvedVoice(pid, preset=pid, dialect=dialect)
        return ResolvedVoice("mặc định", dialect=s.dialect)

    # ── lõi tổng hợp ──────────────────────────────────────────────────────────
    def _synth_chunk(self, eng: TTSEngine, text: str, language: str, rv: ResolvedVoice, emotion: str,
                     dialect: str, temperature: float | None = None) -> np.ndarray:
        prepared = norm.prepare(text, language, dialect, self.lexicon)
        if not _strip_tags(prepared):
            return np.zeros(0, dtype=np.float32)
        req = SynthRequest(text=prepared, language=language, ref_audio=rv.ref_audio, preset=rv.preset,
                           emotion=emotion, temperature=temperature, backbone=rv.backbone)
        wav = eng.synthesize(req)
        return audio.fade(audio.trim(wav, audio.SR))

    def _render_text(self, writer: _Writer, text: str, language: str, voice: str | None, emotion: str,
                     speed: float, engine_id: str | None, dialect: str | None, pause_scale: float,
                     progress: Progress | None, subs: list[srt_mod.Cue], warnings: list[str],
                     prog_range: tuple[float, float] = (0.0, 1.0), temperature: float | None = None) -> None:
        s = settings_mod.load()
        eng = self.pick_engine(language, engine_id)
        segments = norm.parse_inline(text, emotion)
        plan: list[tuple[str, object]] = []  # ("chunk", (Chunk, emotion)) | ("pause", seconds)
        for seg in segments:
            if seg.kind == "pause":
                plan.append(("pause", seg.seconds))
                continue
            for ch in norm.split_chunks(seg.text):
                plan.append(("chunk", (ch, seg.emotion)))
        n_chunks = max(1, sum(1 for k, _ in plan if k == "chunk"))
        done = 0
        rv_cache: dict[str, ResolvedVoice] = {}
        lo, hi = prog_range
        for kind, item in plan:
            if kind == "pause":
                writer.write(audio.silence(float(item)))
                continue
            ch, emo = item
            if emo not in rv_cache:
                rv_cache[emo] = self.resolve_voice(voice, emo, language, eng)
                rvv = rv_cache[emo]
                if rvv.voice is not None and emo != emotions.DEFAULT and rvv.voice.clip_path(emo) is None:
                    warnings.append(f"Giọng '{rvv.voice.name}' chưa có mẫu cảm xúc '{emotions.get(emo).label}' "
                                    "→ dùng mẫu trung tính (cảm xúc sẽ nhẹ). Thu thêm mẫu để rõ hơn.")
            rv = rv_cache[emo]
            if progress:
                progress(lo + (hi - lo) * done / n_chunks, f"Đang đọc đoạn {done + 1}/{n_chunks}…")
            wav = self._synth_chunk(eng, ch.text, language, rv, emo, dialect or rv.dialect, temperature)
            rate = float(speed) * emotions.get(emo).speed
            wav = audio.time_stretch(wav, rate)
            wav = audio.loudness_normalize(wav, audio.SR, s.target_lufs)
            start = writer.time
            writer.write(wav)
            subs.append(srt_mod.Cue(len(subs) + 1, start, writer.time, _strip_tags(ch.text)))
            gap = {"sentence": s.sentence_pause, "paragraph": s.paragraph_pause}.get(ch.pause_after, s.sentence_pause)
            writer.write(audio.silence(gap * pause_scale))
            done += 1
        if progress:
            progress(hi, "Hoàn tất đoạn")

    def _clean_fn(self, ai_clean: bool, warnings: list[str] | None = None):
        if not ai_clean:
            return None
        eng = engines.get("vieneu")
        if not eng.available()[0] or "mock" in engines.registry():
            return None

        def fn(x: np.ndarray) -> np.ndarray:
            try:
                return eng.ai_clean(x, audio.SR)
            except Exception as e:  # không để hỏng cả bản đọc vì bước tuỳ chọn
                if warnings is not None:
                    warnings.append(f"Bỏ qua khử nhiễu AI: {e}")
                return x
        return fn

    def _finish(self, writer: _Writer, subs, warnings, t0, fmt: str | None, want_srt: bool,
                enhance: str | None = None, dereverb: str | None = None,
                ai_clean: bool | None = None) -> Result:
        writer.close()
        s = settings_mod.load()
        preset = enhance or s.enhance
        dereverb = dereverb or s.dereverb
        ai_clean = s.ai_clean if ai_clean is None else ai_clean
        spans = [(c.start, c.end) for c in subs]
        path = _master(writer.path, writer.final, spans, preset, s.target_lufs, dereverb=dereverb,
                       clean_fn=self._clean_fn(ai_clean, warnings))
        self.last_take = (writer.path, spans, writer.final)
        _cleanup_raw(writer.path.parent)
        fmt = (fmt or s.output_format or "wav").lower()
        if fmt == "mp3":
            mp3 = path.with_suffix(".mp3")
            try:
                audio.save(audio.load(path), mp3)
                path.unlink(missing_ok=True)
                path = mp3
            except Exception as e:
                warnings.append(f"Không xuất được MP3 ({e}); giữ file WAV.")
        srt_path = None
        if want_srt and subs:
            srt_path = path.with_suffix(".srt")
            srt_path.write_text(srt_mod.write(subs), encoding="utf-8")
        return Result(path, writer.time, subs, srt_path, warnings, time.time() - t0)

    # ── API công khai ─────────────────────────────────────────────────────────
    def synthesize(self, text: str, language: str = "vi", voice: str | None = None,
                   emotion: str = emotions.DEFAULT, speed: float = 1.0, engine_id: str | None = None,
                   dialect: str | None = None, pause_scale: float = 1.0, fmt: str | None = None,
                   want_srt: bool = True, progress: Progress | None = None, name: str | None = None,
                   temperature: float | None = None, enhance: str | None = None,
                   dereverb: str | None = None, ai_clean: bool | None = None) -> Result:
        if not (text or "").strip():
            raise ValueError("Chưa có văn bản.")
        t0 = time.time()
        writer = _Writer(_out_path(name or text[:30]))
        subs: list[srt_mod.Cue] = []
        warnings: list[str] = []
        try:
            self._render_text(writer, text, language, voice, emotion, speed, engine_id, dialect, pause_scale,
                              progress, subs, warnings, temperature=temperature)
        except BaseException:
            writer.close()
            writer.path.unlink(missing_ok=True)
            raise
        return self._finish(writer, subs, warnings, t0, fmt, want_srt, enhance, dereverb, ai_clean)

    def dialogue(self, script: str, cast: dict[str, dict], default: dict | None = None,
                 gap: float = 0.35, fmt: str | None = None, progress: Progress | None = None,
                 enhance: str | None = None, dereverb: str | None = None,
                 ai_clean: bool | None = None) -> Result:
        """cast: {tên nhân vật: {"voice":..., "language": "vi"|"en", "emotion":..., "speed":..., "engine": ...}}"""
        lines = dialogue_mod.parse(script)
        if not lines:
            raise ValueError("Kịch bản trống. Mỗi dòng dạng 'Tên: lời thoại'.")
        default = default or {}
        t0 = time.time()
        writer = _Writer(_out_path("hoi-thoai"))
        subs: list[srt_mod.Cue] = []
        warnings: list[str] = []
        try:
            for i, ln in enumerate(lines):
                c = {**default, **(cast.get(ln.speaker) or {})}
                if not c.get("voice"):
                    warnings.append(f"Nhân vật '{ln.speaker}' chưa được gán giọng → dùng giọng mặc định.")
                n0 = len(subs)
                self._render_text(
                    writer, ln.text, c.get("language", "vi"), c.get("voice"),
                    ln.emotion or c.get("emotion") or emotions.DEFAULT, float(c.get("speed", 1.0)),
                    c.get("engine") or None, None, 1.0, progress, subs, warnings,
                    prog_range=(i / len(lines), (i + 1) / len(lines)),
                )
                for cue in subs[n0:]:
                    cue.text = f"{ln.speaker}: {cue.text}"
                writer.write(audio.silence(gap))
        except BaseException:
            writer.close()
            writer.path.unlink(missing_ok=True)
            raise
        return self._finish(writer, subs, warnings, t0, fmt, True, enhance, dereverb, ai_clean)

    def dub_srt(self, srt_text: str, language: str = "vi", voice: str | None = None,
                emotion: str = emotions.DEFAULT, speed: float = 1.0, engine_id: str | None = None,
                max_stretch: float = 1.35, fmt: str | None = None, progress: Progress | None = None,
                enhance: str | None = None, dereverb: str | None = None,
                ai_clean: bool | None = None) -> Result:
        """Lồng tiếng theo phụ đề: mỗi câu đặt đúng thời điểm, tự tăng tốc nếu dài hơn khung thời gian."""
        cues = srt_mod.parse(srt_text)
        if not cues:
            raise ValueError("Không đọc được phụ đề SRT.")
        s = settings_mod.load()
        eng = self.pick_engine(language, engine_id)
        t0 = time.time()
        writer = _Writer(_out_path("long-tieng"))
        warnings: list[str] = []
        subs: list[srt_mod.Cue] = []
        try:
            for i, cue in enumerate(cues):
                if progress:
                    progress(i / len(cues), f"Câu {i + 1}/{len(cues)}")
                segs = [sg for sg in norm.parse_inline(cue.text, emotion) if sg.kind == "text"]
                emo = segs[0].emotion if segs else emotion
                rv = self.resolve_voice(voice, emo, language, eng)
                text = " ".join(sg.text for sg in segs)
                wav = self._synth_chunk(eng, text, language, rv, emo, rv.dialect)
                wav = audio.time_stretch(wav, float(speed) * emotions.get(emo).speed)
                nxt = cues[i + 1].start if i + 1 < len(cues) else None
                slot = (nxt - cue.start) if nxt is not None else max(cue.duration, audio.duration(wav))
                slot = max(slot, cue.duration, 0.3)
                dur = audio.duration(wav)
                if dur > slot:
                    rate = min(max_stretch, dur / slot)
                    wav = audio.time_stretch(wav, rate)
                    if audio.duration(wav) > slot + 0.05:
                        warnings.append(f"Câu {cue.index} dài hơn khung phụ đề {audio.duration(wav) - slot:.1f}s "
                                        "(đã tăng tốc tối đa) — các câu sau sẽ lệch nhẹ.")
                wav = audio.loudness_normalize(wav, audio.SR, s.target_lufs)
                if writer.time < cue.start:
                    writer.write(audio.silence(cue.start - writer.time))
                start = writer.time
                writer.write(wav)
                subs.append(srt_mod.Cue(cue.index, start, writer.time, cue.text))
        except BaseException:
            writer.close()
            writer.path.unlink(missing_ok=True)
            raise
        return self._finish(writer, subs, warnings, t0, fmt, True, enhance, dereverb, ai_clean)

    def stream(self, text: str, language: str = "vi", voice: str | None = None,
               emotion: str = emotions.DEFAULT, speed: float = 1.0, engine_id: str | None = None,
               dialect: str | None = None, enhance: str | None = None) -> Iterator[np.ndarray]:
        """Đọc trực tiếp: phát ngay từng mẩu âm thanh khi vừa tạo xong (độ trễ thấp).

        Có làm trong giọng; bộ lọc giữ trạng thái giữa các mẩu nên không bị "tách" ở chỗ nối."""
        s = settings_mod.load()
        eng = self.pick_engine(language, engine_id)
        fx = enhance_mod.Enhancer(enhance or s.enhance, audio.SR)
        for piece in self._stream_raw(text, language, voice, emotion, speed, eng, dialect, s):
            yield fx(piece)

    def _stream_raw(self, text, language, voice, emotion, speed, eng, dialect, s) -> Iterator[np.ndarray]:
        for seg in norm.parse_inline(text, emotion):
            if seg.kind == "pause":
                yield audio.silence(seg.seconds)
                continue
            rv = self.resolve_voice(voice, seg.emotion, language, eng)
            rate = float(speed) * emotions.get(seg.emotion).speed
            for ch in norm.split_chunks(seg.text, max_chars=160, group=False):
                prepared = norm.prepare(ch.text, language, dialect or rv.dialect, self.lexicon)
                if not _strip_tags(prepared):
                    continue
                req = SynthRequest(text=prepared, language=language, ref_audio=rv.ref_audio, preset=rv.preset,
                                   emotion=seg.emotion, backbone=rv.backbone)
                if eng.supports_stream and abs(rate - 1.0) < 0.02:
                    for piece in eng.stream(req):
                        yield piece
                else:
                    yield audio.time_stretch(eng.synthesize(req), rate)
                yield audio.silence(s.sentence_pause)

    def remaster(self, preset: str, dereverb: str = "tat", ai_clean: bool = False) -> Path:
        """Xử lý lại bản đọc gần nhất với mức hậu kỳ khác (không cần đọc lại)."""
        if not self.last_take or not self.last_take[0].exists():
            raise ValueError("Chưa có bản đọc nào để xử lý lại — hãy bấm Đọc trước.")
        raw, spans, final = self.last_take
        tag = f"{preset}-vang_{dereverb}" + ("-ai" if ai_clean else "")
        out = final.with_name(f"{final.stem}__{tag}.wav")
        return _master(raw, out, spans, preset, settings_mod.load().target_lufs, dereverb=dereverb,
                       clean_fn=self._clean_fn(ai_clean))

    def preview_voice(self, voice: str, language: str = "vi", emotion: str = emotions.DEFAULT,
                      engine_id: str | None = None) -> Result:
        sample = ("Xin chào, đây là giọng đọc thử. Hôm nay trời đẹp, mình cùng đi uống cà phê nhé!"
                  if language == "vi" else "Hello! This is a quick voice preview. Have a wonderful day.")
        return self.synthesize(sample, language, voice, emotion, engine_id=engine_id, want_srt=False,
                               name="nghe-thu", fmt="wav")
