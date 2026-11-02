"""Module tiếng Anh "Pro": Chatterbox (MIT) — clone giọng + điều khiển cường độ cảm xúc.

Chạy trong tiến trình riêng (``envs/chatterbox``) vì xung đột phiên bản thư viện
với lõi giọng. Cài bằng ``install_english_pro.bat``. Không bắt buộc: nếu chưa cài,
module tiếng Anh tự dùng lõi giọng VoxViet.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
from pathlib import Path

import numpy as np

from .. import audio, paths
from .. import settings as settings_mod
from ..text import emotions
from .base import EngineUnavailable, SynthRequest, TTSEngine


def _env_python() -> Path:
    base = paths.ENVS / "chatterbox"
    return base / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


class ChatterboxEngine(TTSEngine):
    id = "chatterbox"
    label = "Chatterbox (tiếng Anh, offline)"
    languages = ("en",)
    supports_clone = True
    sample_rate = 24_000
    description = "Giọng tiếng Anh rất tự nhiên, clone giọng, chỉnh mức cảm xúc."

    def __init__(self):
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def available(self) -> tuple[bool, str]:
        if _env_python().exists():
            return True, ""
        return False, "Chưa cài Chatterbox. Chạy install_english_pro.bat (không bắt buộc)."

    def load(self, backbone: str | None = None) -> None:
        with self._lock:
            if self._proc and self._proc.poll() is None:
                return
            ok, why = self.available()
            if not ok:
                raise EngineUnavailable(why)
            dev = settings_mod.load().device
            dev = "" if dev in ("", "auto") else dev
            worker = Path(__file__).with_name("chatterbox_worker.py")
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            env = dict(os.environ, PYTHONIOENCODING="utf-8")
            self._proc = subprocess.Popen(
                [str(_env_python()), str(worker)] + ([dev] if dev else []),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None,
                text=True, encoding="utf-8", bufsize=1, creationflags=flags, env=env,
            )
            while True:  # chờ dòng {"ready": true}; bỏ qua log khác
                line = self._proc.stdout.readline()
                if not line:
                    raise EngineUnavailable("Chatterbox khởi động thất bại — xem cửa sổ dòng lệnh.")
                try:
                    if json.loads(line).get("ready"):
                        break
                except ValueError:
                    continue

    def unload(self) -> None:
        with self._lock:
            if self._proc and self._proc.poll() is None:
                try:
                    self._proc.stdin.write(json.dumps({"cmd": "quit"}) + "\n")
                    self._proc.stdin.flush()
                    self._proc.wait(timeout=10)
                except Exception:
                    self._proc.kill()
            self._proc = None

    def synthesize(self, req: SynthRequest) -> np.ndarray:
        self.load()
        emo = emotions.get(req.emotion)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.wav"
            msg = {
                "cmd": "synth", "text": req.text, "ref": req.ref_audio, "out": str(out),
                "exaggeration": req.extra.get("exaggeration", emo.exaggeration),
                "cfg_weight": req.extra.get("cfg_weight", 0.3 if emo.exaggeration > 0.6 else 0.5),
                "temperature": req.temperature if req.temperature is not None else 0.8,
            }
            with self._lock:
                self._proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
                self._proc.stdin.flush()
                while True:
                    line = self._proc.stdout.readline()
                    if not line:
                        self._proc = None
                        raise RuntimeError("Tiến trình Chatterbox đã dừng bất ngờ.")
                    try:
                        resp = json.loads(line)
                        break
                    except ValueError:
                        continue
            if not resp.get("ok"):
                raise RuntimeError(f"Chatterbox lỗi: {resp.get('error')}")
            return audio.load(out, audio.SR)
