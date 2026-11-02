"""Xử lý âm thanh: nối, nghỉ, chuẩn hoá âm lượng, đổi tốc độ, xuất file."""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

SR = 48_000  # tần số lấy mẫu chung của phần mềm (= VieNeu v3 Turbo)


def to_mono(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 2:
        # (n, ch) hoặc (ch, n)
        x = x.mean(axis=1) if x.shape[0] > x.shape[1] else x.mean(axis=0)
    return np.ascontiguousarray(x.reshape(-1), dtype=np.float32)


def resample(x: np.ndarray, sr_from: int, sr_to: int = SR) -> np.ndarray:
    x = to_mono(x)
    if sr_from == sr_to or len(x) == 0:
        return x
    try:
        import soxr
        return soxr.resample(x, sr_from, sr_to).astype(np.float32)
    except ImportError:
        n = int(round(len(x) * sr_to / sr_from))
        return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def silence(seconds: float, sr: int = SR) -> np.ndarray:
    return np.zeros(max(0, int(round(seconds * sr))), dtype=np.float32)


def trim(x: np.ndarray, sr: int = SR, threshold_db: float = -45.0, keep: float = 0.04) -> np.ndarray:
    """Cắt khoảng lặng đầu/cuối (giữ lại ``keep`` giây cho tự nhiên)."""
    x = to_mono(x)
    if len(x) == 0:
        return x
    frame = max(1, int(sr * 0.01))
    n = len(x) // frame
    if n == 0:
        return x
    rms = np.sqrt(np.mean(x[: n * frame].reshape(n, frame) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (np.max(np.abs(x)) + 1e-9) + 1e-12)
    voiced = np.where(db > threshold_db)[0]
    if len(voiced) == 0:
        return x[:0]
    pad = int(keep * sr)
    a = max(0, voiced[0] * frame - pad)
    b = min(len(x), (voiced[-1] + 1) * frame + pad)
    return x[a:b]


def fade(x: np.ndarray, sr: int = SR, ms: float = 8.0) -> np.ndarray:
    n = min(len(x) // 2, int(sr * ms / 1000))
    if n > 1:
        x = x.copy()
        ramp = np.linspace(0, 1, n, dtype=np.float32)
        x[:n] *= ramp
        x[-n:] *= ramp[::-1]
    return x


def concat(parts: list[np.ndarray]) -> np.ndarray:
    parts = [to_mono(p) for p in parts if p is not None and len(p)]
    return np.concatenate(parts).astype(np.float32) if parts else np.zeros(0, dtype=np.float32)


def loudness_normalize(x: np.ndarray, sr: int = SR, target_lufs: float = -16.0) -> np.ndarray:
    if len(x) < sr // 2 or not target_lufs:
        return peak_limit(x)
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        loud = meter.integrated_loudness(x.astype(np.float64))
        if np.isfinite(loud):
            x = pyln.normalize.loudness(x.astype(np.float64), loud, target_lufs).astype(np.float32)
    except ImportError:
        rms = np.sqrt(np.mean(x ** 2) + 1e-12)
        target_rms = 10 ** ((target_lufs + 3.0) / 20)  # xấp xỉ
        x = (x * (target_rms / rms)).astype(np.float32)
    return peak_limit(x)


def peak_limit(x: np.ndarray, ceiling: float = 0.97) -> np.ndarray:
    peak = float(np.max(np.abs(x))) if len(x) else 0.0
    return (x * (ceiling / peak)).astype(np.float32) if peak > ceiling else x.astype(np.float32)


# ── ffmpeg ────────────────────────────────────────────────────────────────────

def ffmpeg_exe() -> str | None:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _run_ffmpeg(args: list[str], data: bytes | None = None) -> bytes:
    exe = ffmpeg_exe()
    if not exe:
        raise RuntimeError("Không tìm thấy ffmpeg. Chạy install.bat hoặc `pip install imageio-ffmpeg`.")
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    proc = subprocess.run([exe, "-hide_banner", "-loglevel", "error", *args], input=data,
                          capture_output=True, creationflags=flags)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", "ignore")[-500:])
    return proc.stdout


def decode_bytes(data: bytes, sr: int = SR) -> np.ndarray:
    """Giải mã mp3/ogg/wav... (bytes) thành float32 mono ở ``sr``."""
    try:
        import soundfile as sf
        x, file_sr = sf.read(io.BytesIO(data), dtype="float32")
        return resample(x, file_sr, sr)
    except Exception:
        raw = _run_ffmpeg(["-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", str(sr), "pipe:1"], data)
        return np.frombuffer(raw, dtype=np.float32).copy()


def load(path: str | Path, sr: int = SR) -> np.ndarray:
    try:
        import soundfile as sf
        x, file_sr = sf.read(str(path), dtype="float32")
        return resample(x, file_sr, sr)
    except Exception:
        return decode_bytes(Path(path).read_bytes(), sr)


def time_stretch(x: np.ndarray, rate: float, sr: int = SR) -> np.ndarray:
    """Đổi tốc độ nói, giữ nguyên cao độ. rate > 1 = nhanh hơn."""
    if abs(rate - 1.0) < 0.01 or len(x) == 0:
        return x
    rate = float(np.clip(rate, 0.5, 2.0))
    try:
        raw = _run_ffmpeg(["-f", "f32le", "-ac", "1", "-ar", str(sr), "-i", "pipe:0",
                           "-filter:a", f"atempo={rate:.4f}", "-f", "f32le", "pipe:1"],
                          to_mono(x).tobytes())
        return np.frombuffer(raw, dtype=np.float32).copy()
    except Exception:
        import librosa
        return librosa.effects.time_stretch(to_mono(x), rate=rate).astype(np.float32)


def save(x: np.ndarray, path: str | Path, sr: int = SR) -> Path:
    """Lưu .wav / .flac / .mp3 (theo đuôi file)."""
    import soundfile as sf
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    x = peak_limit(to_mono(x))
    if path.suffix.lower() == ".mp3":
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / "a.wav"
            sf.write(str(wav), x, sr, subtype="PCM_16")
            _run_ffmpeg(["-y", "-i", str(wav), "-codec:a", "libmp3lame", "-q:a", "2", str(path)])
    elif path.suffix.lower() == ".flac":
        sf.write(str(path), x, sr, format="FLAC", subtype="PCM_16")
    else:
        sf.write(str(path), x, sr, subtype="PCM_16")
    return path


def duration(x: np.ndarray, sr: int = SR) -> float:
    return len(x) / float(sr)
