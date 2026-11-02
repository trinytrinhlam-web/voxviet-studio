"""Làm trong giọng (hậu kỳ) — xử lý bộ lọc, chạy nhanh trên CPU, không cần mô hình.

Bộ mã hoá âm thanh của mô hình TTS thường làm mất bớt dải cao và dư dải trầm-trung
(200–400 Hz) → giọng nghe "đục", "tối". Chuỗi xử lý:

  1. Lọc cắt trầm (high-pass)        — bỏ tiếng ù, rung dưới ~80–100 Hz
  2. Giảm dải "bùn" ~250–300 Hz      — bớt đục, bớt "nói trong hộp"
  3. Tăng dải hiện diện ~3–4 kHz     — chữ rõ, phụ âm sắc
  4. Tăng dải "không khí" ≥ 8–10 kHz — sáng, thoáng
  5. Exciter nhẹ                      — tạo lại hài âm cao bị codec làm mất
  6. Giới hạn đỉnh mềm               — không bị rè khi tăng âm

Bộ lọc giữ trạng thái giữa các mẩu → dùng được cho chế độ đọc trực tiếp (streaming).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from scipy.signal import sosfilt, sosfilt_zi
except ImportError:  # scipy luôn có sẵn qua librosa; phòng hờ
    sosfilt = None


@dataclass(frozen=True)
class Preset:
    key: str
    label: str
    hp_hz: float = 0.0
    mud_hz: float = 300.0
    mud_db: float = 0.0
    presence_hz: float = 3500.0
    presence_db: float = 0.0
    air_hz: float = 9000.0
    air_db: float = 0.0
    exciter: float = 0.0
    pre_gain_db: float = 0.0


PRESETS: dict[str, Preset] = {p.key: p for p in (
    Preset("goc", "Gốc (không xử lý)"),
    Preset("nhe", "Nhẹ — giữ âm sắc tự nhiên", hp_hz=80, mud_hz=280, mud_db=-2.0, presence_hz=4000,
           presence_db=1.5, air_hz=9000, air_db=1.5, exciter=0.0, pre_gain_db=-1.0),
    Preset("trong", "Trong — khuyên dùng", hp_hz=90, mud_hz=280, mud_db=-4.5, presence_hz=3500,
           presence_db=3.0, air_hz=7000, air_db=3.0, exciter=0.06, pre_gain_db=-2.0),
    Preset("sang", "Sáng — cho giọng rất đục/tối", hp_hz=100, mud_hz=250, mud_db=-4.0, presence_hz=3200,
           presence_db=4.0, air_hz=6500, air_db=5.0, exciter=0.12, pre_gain_db=-3.0),
)}
DEFAULT = "trong"


def choices() -> list[tuple[str, str]]:
    return [(p.label, p.key) for p in PRESETS.values()]


# ── Biquad (RBJ Audio EQ Cookbook) ────────────────────────────────────────────

def _norm(b, a):
    return np.array([b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]])


def _highpass(f, sr, q=0.7071):
    w = 2 * np.pi * f / sr
    c, al = np.cos(w), np.sin(w) / (2 * q)
    return _norm([(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al])


def _peak(f, sr, db, q=1.0):
    A = 10 ** (db / 40)
    w = 2 * np.pi * f / sr
    c, al = np.cos(w), np.sin(w) / (2 * q)
    return _norm([1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A])


def _high_shelf(f, sr, db):
    A = 10 ** (db / 40)
    w = 2 * np.pi * f / sr
    c = np.cos(w)
    al = np.sin(w) / 2 * np.sqrt(2)  # độ dốc S = 1
    sa = 2 * np.sqrt(A) * al
    return _norm(
        [A * ((A + 1) + (A - 1) * c + sa), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sa)],
        [(A + 1) - (A - 1) * c + sa, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sa],
    )


class _Chain:
    """Chuỗi biquad có trạng thái (dùng được cho streaming)."""

    def __init__(self, sections: list[np.ndarray]):
        self.sos = np.vstack(sections) if sections else None
        self.zi = np.zeros((len(sections), 2)) if sections else None

    def __call__(self, x: np.ndarray) -> np.ndarray:
        if self.sos is None or len(x) == 0:
            return x
        y, self.zi = sosfilt(self.sos, x, zi=self.zi)
        return y


def soft_clip(x: np.ndarray, threshold: float = 0.89) -> np.ndarray:
    """Giới hạn đỉnh mềm: dưới ngưỡng giữ nguyên, trên ngưỡng nén cong (không rè gắt)."""
    out = np.asarray(x, dtype=np.float32).copy()
    over = np.abs(out) > threshold
    if np.any(over):
        head = 1.0 - threshold
        v = out[over]
        out[over] = np.sign(v) * (threshold + head * np.tanh((np.abs(v) - threshold) / head))
    return out


class Enhancer:
    """Xử lý theo mẩu, giữ trạng thái bộ lọc giữa các lần gọi."""

    def __init__(self, preset: str | None = DEFAULT, sr: int = 48_000):
        self.p = PRESETS.get(preset or DEFAULT, PRESETS[DEFAULT])
        self.sr = sr
        self.active = self.p.key != "goc" and sosfilt is not None
        if not self.active:
            return
        p, nyq = self.p, sr / 2
        main = []
        if p.hp_hz:
            main.append(_highpass(p.hp_hz, sr))
        if p.mud_db:
            main.append(_peak(p.mud_hz, sr, p.mud_db, q=1.0))
        if p.presence_db:
            main.append(_peak(p.presence_hz, sr, p.presence_db, q=0.8))
        if p.air_db and p.air_hz < nyq * 0.9:
            main.append(_high_shelf(p.air_hz, sr, p.air_db))
        self.main = _Chain(main)
        # Exciter: tách dải > 3 kHz → bão hoà nhẹ tạo hài âm → giữ phần > 6 kHz → trộn lại.
        self.ex_in = _Chain([_highpass(3000, sr), _highpass(3000, sr)]) if p.exciter else None
        self.ex_out = _Chain([_highpass(6000, sr), _highpass(6000, sr)]) if p.exciter else None
        self.gain = 10 ** (p.pre_gain_db / 20)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64).reshape(-1)
        if not self.active or len(x) == 0:
            return x.astype(np.float32)
        y = self.main(x)
        if self.ex_in is not None:
            band = self.ex_in(x)
            drive = 4.0
            harm = np.tanh(drive * band) / drive
            y = y + self.p.exciter * self.ex_out(harm) * 4.0
        return soft_clip(y * self.gain)


def process(x: np.ndarray, preset: str | None = DEFAULT, sr: int = 48_000) -> np.ndarray:
    """Xử lý một đoạn hoàn chỉnh (trạng thái bộ lọc mới)."""
    if len(x) == 0:
        return np.asarray(x, dtype=np.float32)
    # Đệm 50 ms im lặng ở đầu để bộ lọc ổn định, tránh "tách" ở đầu câu.
    pad = int(0.05 * sr)
    y = Enhancer(preset, sr)(np.concatenate([np.zeros(pad), np.asarray(x, dtype=np.float64)]))
    return y[pad:].astype(np.float32)


# ── Giảm vang (dereverberation) ───────────────────────────────────────────────
#
# Phương pháp trừ phổ vang muộn (Lebart et al., 2001): phần vang của phòng ở thời
# điểm t ≈ năng lượng của chính tín hiệu cách đó ~50 ms, suy giảm theo hàm mũ với
# thời gian vang T60. Ước lượng phần đó cho từng dải tần rồi trừ đi (có ngưỡng sàn
# để tránh tiếng "lọc nước"). Không cần mô hình, chạy nhanh trên CPU.

@dataclass(frozen=True)
class DereverbLevel:
    key: str
    label: str
    t60: float = 0.0  # giây — giả định độ vang của phòng
    floor: float = 1.0  # mức giữ lại tối thiểu (0..1), càng thấp càng khử mạnh


DEREVERB: dict[str, DereverbLevel] = {d.key: d for d in (
    DereverbLevel("tat", "Tắt"),
    DereverbLevel("nhe", "Nhẹ", t60=0.30, floor=0.50),
    DereverbLevel("vua", "Vừa — khuyên dùng", t60=0.40, floor=0.32),
    DereverbLevel("manh", "Mạnh", t60=0.60, floor=0.18),
)}
DEREVERB_DEFAULT = "vua"


def dereverb_choices() -> list[tuple[str, str]]:
    return [(d.label, d.key) for d in DEREVERB.values()]


def dereverb(x: np.ndarray, level: str | None = DEREVERB_DEFAULT, sr: int = 48_000) -> np.ndarray:
    lv = DEREVERB.get(level or DEREVERB_DEFAULT, DEREVERB[DEREVERB_DEFAULT])
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    if lv.t60 <= 0 or len(x) < 2048:
        return x.astype(np.float32)
    n_fft, hop = 1024, 256
    win = np.hanning(n_fft + 1)[:-1]
    pad = n_fft
    xp = np.pad(x, (pad, pad + n_fft))
    n_frames = 1 + (len(xp) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    spec = np.fft.rfft(xp[idx] * win, axis=1)  # (T, F)
    power = np.abs(spec) ** 2
    # Làm mượt năng lượng theo thời gian (ước lượng ổn định hơn).
    smooth = np.empty_like(power)
    acc = power[0]
    for t in range(n_frames):
        acc = 0.6 * acc + 0.4 * power[t]
        smooth[t] = acc
    delay = max(1, int(round(0.05 * sr / hop)))  # ~50 ms: ranh giới vang sớm/muộn
    decay = np.exp(-13.8155 * delay * hop / (sr * lv.t60))  # suy giảm năng lượng sau `delay`
    late = np.zeros_like(smooth)
    late[delay:] = decay * smooth[:-delay]
    gain = np.sqrt(np.clip(1.0 - late / (smooth + 1e-12), lv.floor ** 2, 1.0))
    # Làm mượt hệ số theo thời gian để tránh tiếng "lấp lánh" (musical noise).
    g = np.empty_like(gain)
    prev = gain[0]
    for t in range(n_frames):
        a = np.where(gain[t] < prev, 0.5, 0.2)  # giảm nhanh, hồi chậm (từng dải tần)
        prev = a * gain[t] + (1 - a) * prev
        g[t] = prev
    frames = np.fft.irfft(spec * g, n=n_fft, axis=1) * win
    out = np.zeros(len(xp))
    norm = np.zeros(len(xp))
    for t in range(n_frames):
        s = t * hop
        out[s:s + n_fft] += frames[t]
        norm[s:s + n_fft] += win ** 2
    out = out / np.maximum(norm, 1e-8)
    return out[pad:pad + len(x)].astype(np.float32)
