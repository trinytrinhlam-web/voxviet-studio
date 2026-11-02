"""Engine Google — CHỈ để làm mẫu so sánh (cần Internet, không phải lõi).

* Gemini TTS (gói miễn phí của Google AI Studio, cần API key): giọng rất tự
  nhiên, điều khiển cảm xúc bằng câu chỉ dẫn. Không clone được giọng của bạn.
* gTTS (không cần key): giọng của Google Dịch, khá "máy" — mức chuẩn tối thiểu.

Tên model Gemini TTS thay đổi theo thời gian, nên phần mềm hỏi Google danh sách
model hiện có rồi tự chọn model TTS mới nhất (có thể chọn tay trong Cài đặt).
"""

from __future__ import annotations

import base64
import io
import json
import re
import urllib.error
import urllib.request

import numpy as np

from .. import audio
from .. import settings as settings_mod
from ..text import emotions
from .base import EngineUnavailable, SynthRequest, TTSEngine

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_VOICES = [
    "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede", "Callirrhoe", "Autonoe",
    "Enceladus", "Iapetus", "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalgethi",
    "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird",
    "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat",
]


def _http_json(url: str, payload: dict | None = None, api_key: str = "", timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("x-goog-api-key", api_key)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        try:
            msg = json.loads(body)["error"]["message"]
        except Exception:
            msg = body[:300]
        raise RuntimeError(f"Google trả lỗi {e.code}: {msg}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Không kết nối được Google (cần Internet): {e.reason}") from None


def _version_key(name: str) -> tuple:
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", name)[:1]] or [0.0]
    return (nums[0], "pro" not in name, "preview" not in name)


class GeminiEngine(TTSEngine):
    id = "gemini"
    label = "Google Gemini TTS (mẫu so sánh — cần Internet)"
    languages = ("vi", "en")
    online = True
    sample_rate = 24_000
    description = "Gói miễn phí Google AI Studio. Chỉ dùng để so sánh chất lượng."

    def __init__(self):
        self._models: list[str] | None = None

    def available(self) -> tuple[bool, str]:
        if not settings_mod.load().gemini_api_key:
            return False, "Chưa nhập Gemini API key (tab Cài đặt). Lấy miễn phí tại aistudio.google.com."
        return True, ""

    def presets(self, language: str = "vi") -> list[tuple[str, str]]:
        return [(v, v) for v in GEMINI_VOICES]

    def list_models(self, refresh: bool = False) -> list[str]:
        key = settings_mod.load().gemini_api_key
        if not key:
            raise EngineUnavailable(self.available()[1])
        if self._models is None or refresh:
            names, token = [], ""
            for _ in range(10):
                url = f"{GEMINI_BASE}/models?pageSize=200" + (f"&pageToken={token}" if token else "")
                data = _http_json(url, api_key=key)
                for m in data.get("models", []):
                    n = m.get("name", "").removeprefix("models/")
                    if "tts" in n.lower():
                        names.append(n)
                token = data.get("nextPageToken", "")
                if not token:
                    break
            # Ưu tiên bản Flash (gói miễn phí) mới nhất.
            names.sort(key=_version_key, reverse=True)
            self._models = names
        return self._models

    def _model(self) -> str:
        s = settings_mod.load()
        if s.gemini_model:
            return s.gemini_model
        models = self.list_models()
        if not models:
            raise RuntimeError("Tài khoản không có model Gemini TTS nào.")
        flash = [m for m in models if "flash" in m]
        return (flash or models)[0]

    def synthesize(self, req: SynthRequest) -> np.ndarray:
        ok, why = self.available()
        if not ok:
            raise EngineUnavailable(why)
        s = settings_mod.load()
        style = emotions.get(req.emotion).gemini_style
        lang_hint = "in Vietnamese" if req.language == "vi" else "in English"
        prompt = f"{style} {lang_hint}: {req.text}" if style else f"Read aloud naturally {lang_hint}: {req.text}"
        voice = req.preset if req.preset in GEMINI_VOICES else (s.gemini_voice or "Kore")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
            },
        }
        data = _http_json(f"{GEMINI_BASE}/models/{self._model()}:generateContent", payload, api_key=s.gemini_api_key)
        try:
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Gemini không trả âm thanh: {json.dumps(data)[:300]}") from None
        raw = base64.b64decode(part["data"])
        mime = part.get("mimeType", "")
        m = re.search(r"rate=(\d+)", mime)
        if "L16" in mime or "pcm" in mime.lower():
            pcm = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
            return audio.resample(pcm, int(m.group(1)) if m else 24000, audio.SR)
        return audio.decode_bytes(raw, audio.SR)


class GTTSEngine(TTSEngine):
    id = "gtts"
    label = "Google gTTS (mẫu cơ bản — cần Internet)"
    languages = ("vi", "en")
    online = True
    description = "Giọng Google Dịch, không cần key. Mốc chất lượng thấp nhất để so sánh."

    def available(self) -> tuple[bool, str]:
        try:
            import gtts  # noqa: F401
            return True, ""
        except ImportError:
            return False, "Chưa cài gTTS (pip install gTTS)."

    def presets(self, language: str = "vi") -> list[tuple[str, str]]:
        if language == "en":
            return [("Anh–Mỹ", "com"), ("Anh–Anh", "co.uk"), ("Anh–Úc", "com.au")]
        return [("Mặc định", "com.vn")]

    def synthesize(self, req: SynthRequest) -> np.ndarray:
        from gtts import gTTS
        buf = io.BytesIO()
        try:
            gTTS(req.text, lang=req.language, tld=req.preset or "com").write_to_fp(buf)
        except Exception as e:
            raise RuntimeError(f"gTTS lỗi (cần Internet): {e}") from None
        return audio.decode_bytes(buf.getvalue(), audio.SR)
