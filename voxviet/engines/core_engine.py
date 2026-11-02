"""Lõi giọng VoxViet — bộ máy đọc chính, chạy offline.

* 48 kHz, song ngữ Việt–Anh, tự đọc chuẩn tiếng Anh khi xen trong câu tiếng Việt.
* Clone giọng tức thì từ đoạn mẫu 3–8 giây.
* GPU (PyTorch) hoặc CPU (ONNX, không cần torch).
* Bộ giọng có sẵn của VoxViet: ``data/giong_co_san.json``.

Mã nguồn bên dưới dựa trên VieNeu-TTS v3 Turbo (Apache-2.0) — xem THIRD_PARTY_NOTICES.md.
"""

from __future__ import annotations

import gc
import logging
import threading
from pathlib import Path
from typing import Iterator

import numpy as np

from .. import catalog
from .. import settings as settings_mod
from ..text import emotions
from .base import EngineUnavailable, SynthRequest, TTSEngine

log = logging.getLogger("voxviet.core")


class VoiceCoreEngine(TTSEngine):
    id = "core"
    label = "Lõi giọng VoxViet (offline)"
    languages = ("vi", "en")
    supports_clone = True
    supports_stream = True
    sample_rate = 48_000
    description = "Đọc tiếng Việt lẫn tiếng Anh, clone giọng từ 3–8 giây mẫu, chạy hoàn toàn trên máy."

    def __init__(self):
        self._tts = None
        self._backbone: str | None = None
        self._lock = threading.RLock()

    # ── trạng thái ──
    def available(self) -> tuple[bool, str]:
        try:
            import vieneu  # noqa: F401
            return True, ""
        except Exception as e:
            return False, f"Chưa cài lõi giọng ({e}). Chạy install.bat."

    def preset_info(self) -> list[dict]:
        return [{"name": v.id, "label": v.name, "description": v.description, "gender": v.gender,
                 "region": v.region, "style": v.style} for v in catalog.all_voices()]

    def presets(self, language: str = "vi") -> list[tuple[str, str]]:
        return [(f"{v.name} — {v.description}", v.id) for v in catalog.all_voices()]

    # ── nạp mô hình ──
    def load(self, backbone: str | None = None) -> None:
        backbone = backbone or settings_mod.load().core_backbone or None
        with self._lock:
            if self._tts is not None and self._backbone == backbone:
                return
            self.unload()
            ok, why = self.available()
            if not ok:
                raise EngineUnavailable(why)
            from vieneu import Vieneu
            s = settings_mod.load()
            kwargs = {"device": s.device or "auto", "precision": s.cpu_precision or "fp32"}
            if backbone:
                kwargs["backbone_repo"] = backbone
                # Mô hình fine-tune đã merge: thư mục chứa thẳng config.json → không có subfolder.
                if (Path(backbone) / "config.json").exists():
                    kwargs["model_subfolder"] = None
                # Mô hình fine-tune không có bản ONNX → luôn chạy đường PyTorch.
                kwargs["backend"] = "pytorch"
            log.info("Đang nạp lõi giọng VoxViet %s", kwargs)
            try:
                self._tts = Vieneu(mode="v3turbo", **kwargs)
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                if any(k in msg for k in ("LocalEntryNotFound", "offline", "Offline", "403", "Connect",
                                          "ProxyError", "resolve", "HfHubHTTPError", "Max retries")):
                    raise EngineUnavailable(
                        "Chưa có mô hình lõi giọng trên máy (hoặc không tải được). Chạy download_models.bat "
                        "một lần khi có Internet, sau đó phần mềm chạy offline.") from e
                if "CUDA out of memory" in msg or "OutOfMemory" in msg:
                    raise EngineUnavailable("GPU hết bộ nhớ. Đóng bớt ứng dụng dùng GPU hoặc chọn CPU "
                                            "trong Cài đặt.") from e
                raise
            self._backbone = backbone

    def unload(self) -> None:
        with self._lock:
            if self._tts is not None:
                try:
                    self._tts.close()
                except Exception:
                    pass
                self._tts = None
                gc.collect()
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except Exception:
                    pass

    def ai_clean(self, wav: np.ndarray, sr: int = 48_000) -> np.ndarray:
        """Khử nhiễu/vang bằng AI: bộ denoiser (lõi Resemble Enhance, ONNX) đi kèm mô hình.

        Không cần tải thêm. Xử lý từng khúc ≤ 20 giây ở 44.1 kHz rồi đổi lại ``sr``."""
        from .. import audio as audio_mod
        self.load()
        den = getattr(getattr(self._tts, "engine", None), "denoiser", None)
        if den is None:
            raise EngineUnavailable("Bộ khử nhiễu AI không có trong mô hình hiện tại.")
        x = audio_mod.resample(wav, sr, 44_100)
        step = 44_100 * 20
        parts = []
        with self._lock:
            for i in range(0, len(x), step):
                parts.append(np.asarray(den.denoise(x[i:i + step], 44_100), dtype=np.float32))
        return audio_mod.resample(np.concatenate(parts) if parts else x, 44_100, sr)[: len(wav)]

    @property
    def backend(self) -> str:
        return getattr(self._tts, "backend", "?") if self._tts else "chưa nạp"

    # ── tổng hợp ──
    def _kwargs(self, req: SynthRequest) -> dict:
        emo = emotions.get(req.emotion)
        kw = {
            "temperature": float(req.temperature if req.temperature is not None else emo.temperature),
            "denoise": bool(req.extra.get("denoise", True)),
            # Mô hình fine-tune (merged) được huấn luyện chỉ với speaker embedding.
            "use_ref_codes": bool(req.extra.get("use_ref_codes", not req.backbone)),
        }
        if req.ref_audio:
            kw["ref_audio"] = str(req.ref_audio)
        elif req.preset:
            pv = catalog.get(req.preset)
            kw["voice"] = pv.base if pv else req.preset
        return kw

    def synthesize(self, req: SynthRequest) -> np.ndarray:
        self.load(req.backbone)
        with self._lock:
            wav = self._tts.infer(req.text, **self._kwargs(req))
        return np.asarray(wav, dtype=np.float32).reshape(-1)

    def stream(self, req: SynthRequest) -> Iterator[np.ndarray]:
        self.load(req.backbone)
        with self._lock:
            for chunk in self._tts.infer_stream(req.text, **self._kwargs(req)):
                yield np.asarray(chunk, dtype=np.float32).reshape(-1)
