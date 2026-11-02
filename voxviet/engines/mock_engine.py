"""Engine giả lập (tạo âm "bíp" theo số âm tiết). Dùng cho kiểm thử và chạy thử
giao diện khi chưa tải mô hình: đặt biến môi trường VOXVIET_DEMO=1."""

from __future__ import annotations

import zlib

import numpy as np

from .. import audio
from .base import SynthRequest, TTSEngine


class MockEngine(TTSEngine):
    id = "mock"
    label = "Giả lập (chạy thử, không phải giọng thật)"
    supports_clone = True
    supports_stream = True

    def presets(self, language: str = "vi") -> list[tuple[str, str]]:
        return [("Bíp cao", "high"), ("Bíp trầm", "low")]

    def synthesize(self, req: SynthRequest) -> np.ndarray:
        sr = audio.SR
        words = [w for w in req.text.split() if w.strip("[].,!?")]
        seed = zlib.crc32((req.ref_audio or req.preset or "x").encode())
        base = 180 + seed % 120 if req.preset != "low" else 110
        out = []
        for i, _w in enumerate(words):
            n = int(sr * 0.18)
            t = np.arange(n) / sr
            f = base * (1 + 0.05 * ((i % 3) - 1))
            tone = 0.2 * np.sin(2 * np.pi * f * t) * np.hanning(n)
            out.append(tone.astype(np.float32))
            out.append(audio.silence(0.04, sr))
        return audio.concat(out)

    def stream(self, req: SynthRequest):
        wav = self.synthesize(req)
        step = audio.SR // 4
        for i in range(0, len(wav), step):
            yield wav[i:i + step]
