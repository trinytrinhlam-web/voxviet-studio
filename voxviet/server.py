"""Máy chủ cục bộ của VoxViet Studio: API cho giao diện ``web/`` (chỉ nghe 127.0.0.1).

Bảo vệ: mọi yêu cầu thay đổi dữ liệu phải có header ``X-VoxViet: 1`` (trang web lạ
không gửi được header này tới localhost), WebSocket chỉ nhận từ chính giao diện.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import sys
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__, audio, catalog, engines, finetune, paths, recording
from .updater import Updater, UpdateError
from . import settings as settings_mod
from .audio import enhance as enhance_mod
from .engines.base import EngineUnavailable
from .engines.google_engines import GEMINI_VOICES
from .pipeline import VOICE_PREFIX, Result, Studio
from .text import dialogue as dialogue_mod
from .text import emotions
from .text import normalize as norm
from .voices import MAX_VOICES, PRESET_PREFIX

log = logging.getLogger("voxviet.server")
BOOT_ID = uuid.uuid4().hex[:10]  # đổi mỗi lần khởi động — giao diện dùng để biết phần mềm đã khởi động lại
_ARGV = [os.path.abspath(sys.argv[0]), *sys.argv[1:]] if sys.argv and sys.argv[0] else []
WEB_DIR = paths.ROOT / "web"
AVATAR_DIR = WEB_DIR / "avatars"


def _avatar_url(slug: str | None) -> str | None:
    return f"/avatars/{slug}.webp" if slug and (AVATAR_DIR / f"{slug}.webp").is_file() else None
GUARD_HEADER = "x-voxviet"
SESSION_COOKIE = "vv_session"
MAX_BODY = 200 * 1024 * 1024  # 200 MB — đủ cho file âm thanh dài, chặn yêu cầu làm đầy ổ đĩa
DEFAULT_HOSTS = {"127.0.0.1", "localhost"}


def allowed_hosts() -> set[str]:
    extra = {h.strip() for h in os.environ.get("VOXVIET_ALLOWED_HOSTS", "").split(",") if h.strip()}
    return DEFAULT_HOSTS | extra


def _host_ok(host_header: str, hosts: set[str]) -> bool:
    """Chống DNS rebinding: chỉ nhận yêu cầu gửi tới đúng 127.0.0.1/localhost (bỏ phần cổng)."""
    host = (host_header or "").rsplit(":", 1)[0] if not (host_header or "").startswith("[") else host_header
    return host in hosts


def session_token() -> str:
    """Khoá phiên ngẫu nhiên, lưu riêng trên máy (data/.local, không đồng bộ). Giữ qua các lần
    khởi động lại để cửa sổ đang mở vẫn dùng được sau khi cập nhật."""
    import secrets
    f = paths.DATA / ".local" / "session_token"
    try:
        tok = f.read_text(encoding="utf-8").strip()
        if len(tok) >= 32:
            return tok
    except OSError:
        pass
    tok = secrets.token_urlsafe(32)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(tok, encoding="utf-8")
    return tok


# ── công việc chạy nền (một luồng: GPU chỉ chạy một việc một lúc) ─────────────

class Jobs:
    def __init__(self):
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="voxviet-job")
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def submit(self, kind: str, fn: Callable[[Callable[[float, str], None], Callable[[str], None]], Any]) -> str:
        jid = uuid.uuid4().hex[:12]
        job = {"id": jid, "kind": kind, "status": "queued", "progress": 0.0, "message": "Đang chờ…",
               "result": None, "error": None, "log": [], "created": time.time()}
        with self._lock:
            self._jobs[jid] = job
            # giữ tối đa 50 việc gần nhất
            for old in sorted(self._jobs.values(), key=lambda j: j["created"])[:-50]:
                self._jobs.pop(old["id"], None)

        def progress(frac: float, msg: str) -> None:
            job["progress"] = float(max(0.0, min(1.0, frac)))
            job["message"] = msg

        def logline(line: str) -> None:
            job["log"].append(line)
            del job["log"][:-400]

        def run():
            job["status"] = "running"
            job["message"] = "Đang xử lý…"
            try:
                job["result"] = fn(progress, logline)
                job["status"] = "done"
                job["progress"] = 1.0
                job["message"] = "Xong"
            except Exception as e:
                job["status"] = "error"
                job["error"] = _friendly(e)
                if not isinstance(e, (ValueError, EngineUnavailable, RuntimeError)):
                    log.error(traceback.format_exc())

        self._pool.submit(run)
        return jid

    def get(self, jid: str) -> dict | None:
        return self._jobs.get(jid)


def schedule_restart(delay: float = 1.0) -> None:
    """Khởi động lại phần mềm: mở tiến trình mới (chờ cổng trống) rồi thoát tiến trình hiện tại."""
    def go():
        args = list(_ARGV)
        if "--no-browser" not in args:
            args.append("--no-browser")  # cửa sổ giao diện đang mở sẵn, chỉ cần tải lại
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" and sys.executable.lower().endswith("pythonw.exe") else 0
        subprocess.Popen([sys.executable, *args], cwd=str(paths.ROOT), creationflags=flags,
                         env=dict(os.environ, VOXVIET_RESTARTED="1"))
        os._exit(0)
    threading.Timer(delay, go).start()


def _wait_port_free(port: int, timeout: float = 30.0) -> None:
    t = time.time()
    while time.time() - t < timeout:
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return
            except OSError:
                time.sleep(0.3)


def _friendly(e: Exception) -> str:
    if isinstance(e, (ValueError, EngineUnavailable, RuntimeError)):
        return str(e)
    return f"Lỗi không mong đợi: {e}"


def _file_url(p: Path | None) -> str | None:
    if p is None:
        return None
    try:
        rel = Path(p).resolve().relative_to(paths.DATA.resolve())
    except ValueError:
        return None
    return "/files/" + rel.as_posix()


def _result_json(r: Result) -> dict:
    return {
        "audio_url": _file_url(r.path), "srt_url": _file_url(r.srt_path), "name": r.path.name,
        "duration": round(r.duration, 2), "elapsed": round(r.elapsed, 2),
        "rtf": round(r.elapsed / r.duration, 3) if r.duration else None,
        "warnings": list(dict.fromkeys(r.warnings)),
        "subtitles": [{"start": round(c.start, 3), "end": round(c.end, 3), "text": c.text} for c in r.subtitles],
    }


def _eng(engine_id: str | None) -> str | None:
    return None if not engine_id or engine_id == "auto" else engine_id


def _dialect(d: str | None) -> str | None:
    return None if not d or d == "auto" else d


# ── dựng ứng dụng ─────────────────────────────────────────────────────────────

def create_app(studio: Studio | None = None, updater: Updater | None = None,
               restart: Callable[[], None] | None = None, auth_token: str | None = None) -> FastAPI:
    """auth_token: khoá phiên — khi có, mọi /api/ và /files/ đòi cookie đúng khoá (cửa sổ phần mềm
    nhận cookie qua đường dẫn mở cửa sổ ?t=…). Không có (kiểm thử) → chỉ kiểm tra Host + header."""
    import hmac
    hosts = allowed_hosts()

    def token_ok(cookie: str | None) -> bool:
        return auth_token is None or (bool(cookie) and hmac.compare_digest(cookie, auth_token))

    studio = studio or Studio()
    updater = updater or Updater()
    restart = restart or schedule_restart
    jobs = Jobs()
    app = FastAPI(title="VoxViet Studio", docs_url=None, redoc_url=None, openapi_url=None)
    update_cache: dict = {}

    def auto_check():
        """Tự kiểm tra bản mới tối đa mỗi ngày một lần (chạy nền, lỗi thì bỏ qua)."""
        try:
            if not updater.is_repo():
                return
            last = updater.status().get("last_check")
            if last and time.time() - time.mktime(time.strptime(last, "%Y-%m-%d %H:%M")) < 20 * 3600:
                cached = updater.status().get("last_result") or {}
                update_cache.update(cached)
                return
            update_cache.update({k: v for k, v in updater.check().items() if k in ("current", "latest", "available")})
        except Exception as e:  # không có mạng, chưa đăng nhập GitHub…
            log.info("Bỏ qua tự kiểm tra cập nhật: %s", e)

    if os.environ.get("VOXVIET_DEMO") != "1" and os.environ.get("VOXVIET_NO_AUTOCHECK") != "1":
        threading.Thread(target=auto_check, daemon=True).start()

    @app.middleware("http")
    async def guard(request: Request, call_next):
        from fastapi.responses import RedirectResponse
        if not _host_ok(request.headers.get("host", ""), hosts):
            return JSONResponse({"detail": "Địa chỉ truy cập không hợp lệ."}, status_code=403)
        path = request.url.path
        # Cửa sổ phần mềm mở bằng /?t=<khoá> → ghi cookie phiên rồi chuyển về trang chính.
        if auth_token and path == "/" and request.query_params.get("t"):
            if not hmac.compare_digest(request.query_params["t"], auth_token):
                return JSONResponse({"detail": "Khoá phiên không đúng."}, status_code=403)
            resp = RedirectResponse("/", status_code=303)
            resp.set_cookie(SESSION_COOKIE, auth_token, httponly=True, samesite="strict", path="/")
            return resp
        if (path.startswith("/api/") or path.startswith("/files/")) and not token_ok(request.cookies.get(SESSION_COOKIE)):
            return JSONResponse({"detail": "Phiên không hợp lệ — hãy mở phần mềm bằng run.bat."}, status_code=401)
        if request.method not in ("GET", "HEAD", "OPTIONS") and request.headers.get(GUARD_HEADER) != "1":
            return JSONResponse({"detail": "Yêu cầu không hợp lệ."}, status_code=403)
        try:
            if int(request.headers.get("content-length") or 0) > MAX_BODY:
                return JSONResponse({"detail": "File quá lớn (tối đa 200 MB)."}, status_code=413)
        except ValueError:
            return JSONResponse({"detail": "Yêu cầu không hợp lệ."}, status_code=400)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        # Chỉ chạy mã của chính phần mềm: chặn mã chèn (inline script, onerror=…) và mọi kết nối ra ngoài.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; media-src 'self' blob:; font-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    def body_text(data: dict, key: str, default: str = "") -> str:
        v = data.get(key, default)
        return v if isinstance(v, str) else default

    # ── trạng thái chung ──
    def voice_options(language: str, engine_id: str | None) -> list[dict]:
        eng = studio.pick_engine(language, _eng(engine_id), check=False)
        out = []
        if eng.supports_clone:
            for v in studio.library.list():
                out.append({"value": f"{VOICE_PREFIX}{v.id}", "label": v.name, "kind": "mine",
                            "region": v.dialect, "gender": v.gender, "clips": sorted(v.clips),
                            "avatar": _avatar_url(v.avatar)})
        if eng.id in ("core", "mock"):  # mock = chế độ chạy thử, hiện đúng bộ giọng thật
            for v in catalog.all_voices():
                out.append({"value": f"{PRESET_PREFIX}{v.id}", "label": v.name, "kind": "preset",
                            "region": v.region, "gender": v.gender, "style": v.style,
                            "description": v.description, "avatar": _avatar_url(v.avatar)})
        else:
            for label, pid in eng.presets(language):
                out.append({"value": f"{PRESET_PREFIX}{pid}", "label": label, "kind": "preset"})
        return out

    def settings_json() -> dict:
        s = asdict(settings_mod.load())
        key = s.pop("gemini_api_key", "")
        s["has_gemini_key"] = bool(key)
        s["gemini_key_hint"] = f"…{key[-4:]}" if len(key) > 8 else ""
        s.pop("extra", None)
        return s

    @app.get("/api/state")
    def state():
        engs = []
        for e in engines.registry().values():
            ok, why = e.available()
            engs.append({"id": e.id, "label": e.label, "languages": list(e.languages), "online": e.online,
                         "available": ok, "why": why, "clone": e.supports_clone})
        ft_ok, ft_msg = finetune.status()
        return {
            "version": __version__, "demo": "mock" in engines.registry(),
            "engines": engs, "settings": settings_json(),
            "emotions": [{"key": k, "label": lbl} for lbl, k in emotions.choices()],
            "enhance": [{"key": k, "label": lbl} for lbl, k in enhance_mod.choices()],
            "dereverb": [{"key": k, "label": lbl} for lbl, k in enhance_mod.dereverb_choices()],
            "gemini_voices": GEMINI_VOICES, "max_voices": MAX_VOICES,
            "default_preset": f"{PRESET_PREFIX}{catalog.default_id()}",
            "finetune": {"ok": ft_ok, "message": ft_msg},
            "avatars": sorted(p.stem for p in AVATAR_DIR.glob("*.webp")) if AVATAR_DIR.exists() else [],
            "boot_id": BOOT_ID,
            "update": {k: update_cache.get(k) for k in ("available", "latest")},
        }

    @app.get("/api/voices")
    def voices(language: str = "vi", engine: str = "auto"):
        return {"voices": voice_options(language, engine)}

    @app.post("/api/normalize")
    async def normalize(request: Request):
        data = await request.json()
        text, language = body_text(data, "text"), body_text(data, "language", "vi")
        d = _dialect(body_text(data, "dialect"))
        if d is None:
            try:
                eng = studio.pick_engine(language, check=False)
                d = studio.resolve_voice(body_text(data, "voice"), emotions.DEFAULT, language, eng).dialect
            except Exception:
                d = settings_mod.load().dialect
        lines = []
        for seg in norm.parse_inline(text):
            if seg.kind == "pause":
                lines.append({"kind": "pause", "seconds": round(seg.seconds, 2)})
                continue
            for ch in norm.split_chunks(seg.text):
                lines.append({"kind": "text", "emotion": emotions.get(seg.emotion).label,
                              "text": norm.prepare(ch.text, language, d, studio.lexicon)})
        return {"lines": lines, "dialect": d}

    @app.post("/api/text-file")
    async def text_file(file: UploadFile = File(...)):
        suffix = Path(file.filename or "").suffix.lower()
        raw = await file.read()
        if suffix == ".docx":
            import io

            import docx
            doc = docx.Document(io.BytesIO(raw))
            return {"text": "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())}
        for enc in ("utf-8-sig", "utf-16", "cp1258", "latin-1"):
            try:
                return {"text": raw.decode(enc)}
            except UnicodeDecodeError:
                continue
        return {"text": raw.decode("utf-8", "ignore")}

    # ── việc chạy nền ──
    @app.get("/api/jobs/{jid}")
    def job(jid: str):
        j = jobs.get(jid)
        if not j:
            raise HTTPException(404, "Không tìm thấy công việc.")
        return j

    @app.post("/api/jobs/tts")
    async def job_tts(request: Request):
        d = await request.json()
        if not body_text(d, "text").strip():
            raise HTTPException(400, "Chưa có văn bản.")
        temp = d.get("temperature")
        temp = float(temp) if temp else None

        def run(progress, _log):
            r = studio.synthesize(
                d["text"], d.get("language", "vi"), d.get("voice"), d.get("emotion") or emotions.DEFAULT,
                float(d.get("speed", 1.0)), _eng(d.get("engine")), _dialect(d.get("dialect")),
                float(d.get("pause", 1.0)), d.get("fmt"), True, progress, temperature=temp,
                enhance=d.get("enhance"), dereverb=d.get("dereverb"), ai_clean=d.get("ai_clean"))
            return _result_json(r)
        return {"job": jobs.submit("tts", run)}

    @app.post("/api/jobs/remaster")
    async def job_remaster(request: Request):
        d = await request.json()

        def run(progress, _log):
            progress(0.2, "Đang xử lý lại bản vừa đọc…")
            p = studio.remaster(d.get("enhance", "trong"), d.get("dereverb", "vua"), bool(d.get("ai_clean")))
            return {"audio_url": _file_url(p), "name": p.name}
        return {"job": jobs.submit("remaster", run)}

    @app.post("/api/dialogue/parse")
    async def dialogue_parse(request: Request):
        d = await request.json()
        lines = dialogue_mod.parse(body_text(d, "script"))
        return {"speakers": dialogue_mod.speakers(lines), "lines": len(lines)}

    @app.post("/api/jobs/dialogue")
    async def job_dialogue(request: Request):
        d = await request.json()
        cast = d.get("cast") or {}
        first = next(iter(cast.values()), {})

        def run(progress, _log):
            r = studio.dialogue(d.get("script", ""), cast, default={"voice": first.get("voice"), "language": "vi"},
                                gap=float(d.get("gap", 0.35)), fmt=d.get("fmt"), progress=progress)
            return _result_json(r)
        return {"job": jobs.submit("dialogue", run)}

    @app.post("/api/jobs/dub")
    async def job_dub(request: Request):
        d = await request.json()

        def run(progress, _log):
            r = studio.dub_srt(d.get("srt", ""), d.get("language", "vi"), d.get("voice"),
                               d.get("emotion") or emotions.DEFAULT, float(d.get("speed", 1.0)), None,
                               float(d.get("max_stretch", 1.35)), d.get("fmt"), progress)
            return _result_json(r)
        return {"job": jobs.submit("dub", run)}

    @app.post("/api/jobs/compare")
    async def job_compare(request: Request):
        d = await request.json()
        text, language = d.get("text", ""), d.get("language", "vi")
        if not text.strip():
            raise HTTPException(400, "Chưa có văn bản.")

        def run(progress, _log):
            out = []
            plan = [("VoxViet (offline)", None, d.get("voice")),
                    ("Google Gemini TTS", "gemini", f"{PRESET_PREFIX}{d.get('gemini_voice') or 'Kore'}"),
                    ("Google gTTS", "gtts", PRESET_PREFIX + ("com" if language == "en" else "com.vn"))]
            for i, (name, eng, voice) in enumerate(plan):
                progress(i / len(plan), f"Đang tạo bản {name}…")
                try:
                    r = studio.synthesize(text, language, voice, d.get("emotion") or emotions.DEFAULT,
                                          engine_id=eng, want_srt=False, name=f"so-sanh-{eng or 'voxviet'}",
                                          fmt="wav")
                    out.append({"name": name, "ok": True, **_result_json(r)})
                except Exception as e:
                    out.append({"name": name, "ok": False, "error": _friendly(e)})
            return {"items": out}
        return {"job": jobs.submit("compare", run)}

    @app.post("/api/jobs/preview-voice")
    async def job_preview(request: Request):
        d = await request.json()

        def run(progress, _log):
            r = studio.preview_voice(d.get("voice", ""), d.get("language", "vi"),
                                     d.get("emotion") or emotions.DEFAULT)
            return _result_json(r)
        return {"job": jobs.submit("preview", run)}

    # ── đọc trực tiếp (WebSocket, PCM float32 48 kHz) ──
    @app.websocket("/api/live")
    async def live(ws: WebSocket):
        origin = ws.headers.get("origin", "")
        host = ws.headers.get("host", "")
        origin_host = origin.split("//", 1)[-1] if origin else host
        if (not _host_ok(host, hosts) or not _host_ok(origin_host, hosts)
                or not token_ok(ws.cookies.get(SESSION_COOKIE))):
            await ws.close(code=1008)
            return
        await ws.accept()
        loop = asyncio.get_running_loop()
        try:
            while True:
                d = await ws.receive_json()
                text = (d.get("text") or "").strip()
                if not text:
                    continue
                queue: asyncio.Queue = asyncio.Queue()

                def produce():
                    try:
                        for piece in studio.stream(text, d.get("language", "vi"), d.get("voice"),
                                                   d.get("emotion") or emotions.DEFAULT,
                                                   float(d.get("speed", 1.0))):
                            loop.call_soon_threadsafe(queue.put_nowait, np.asarray(piece, dtype=np.float32))
                        loop.call_soon_threadsafe(queue.put_nowait, None)
                    except Exception as e:
                        loop.call_soon_threadsafe(queue.put_nowait, e)

                t0 = time.time()
                first = True
                threading.Thread(target=produce, daemon=True).start()
                while True:
                    item = await queue.get()
                    if item is None:
                        await ws.send_json({"done": True})
                        break
                    if isinstance(item, Exception):
                        await ws.send_json({"error": _friendly(item)})
                        break
                    if first:
                        await ws.send_json({"first_ms": int((time.time() - t0) * 1000), "sr": audio.SR})
                        first = False
                    await ws.send_bytes(np.clip(item, -1, 1).astype("<f4").tobytes())
        except WebSocketDisconnect:
            return

    # ── kho giọng ──
    def voice_json(v) -> dict:
        return {"id": v.id, "name": v.name, "dialect": v.dialect, "gender": v.gender, "backbone": v.backbone,
                "gemini_voice": v.gemini_voice, "avatar": _avatar_url(v.avatar), "avatar_id": v.avatar,
                "clips": [{"key": k, "url": f"/api/library/{v.id}/clips/{k}"} for k in sorted(v.clips)]}

    @app.get("/api/library")
    def library():
        return {"voices": [voice_json(v) for v in studio.library.list()], "max": MAX_VOICES}

    @app.post("/api/library")
    async def library_create(request: Request):
        d = await request.json()
        try:
            v = studio.library.create(d.get("name", ""), d.get("dialect", "bac"), d.get("gender", ""))
        except ValueError as e:
            raise HTTPException(400, str(e))
        return voice_json(v)

    @app.patch("/api/library/{vid}")
    async def library_update(vid: str, request: Request):
        d = await request.json()
        backbone = d.get("backbone")
        if backbone and not Path(backbone).exists():
            raise HTTPException(400, "Thư mục mô hình không tồn tại.")
        try:
            if "avatar" in d and d["avatar"] and not _avatar_url(d["avatar"]):
                raise ValueError("Không có ảnh đại diện này.")
            v = studio.library.update(vid, **{k: d.get(k) for k in ("name", "dialect", "gender", "backbone",
                                                                     "gemini_voice", "avatar") if k in d})
        except ValueError as e:
            raise HTTPException(404, str(e))
        return voice_json(v)

    @app.delete("/api/library/{vid}")
    def library_delete(vid: str):
        studio.library.delete(vid)
        return {"ok": True}

    @app.post("/api/library/{vid}/clips")
    async def library_add_clip(vid: str, file: UploadFile = File(...), emotion: str = Form("trung_tinh"),
                               english: bool = Form(False)):
        suffix = Path(file.filename or "clip.webm").suffix or ".webm"
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / f"clip{suffix}"
            tmp.write_bytes(await file.read())
            try:
                _p, warns = studio.library.add_clip(vid, tmp, emotion, english)
            except (ValueError, RuntimeError) as e:
                raise HTTPException(400, str(e))
        v = studio.library.get(vid)
        return {"voice": voice_json(v), "warnings": warns}

    @app.get("/api/library/{vid}/clips/{key}")
    def library_clip(vid: str, key: str):
        v = studio.library.get(vid)
        p = v.clip_path(key) if v else None
        if not p:
            raise HTTPException(404, "Không có mẫu này.")
        return FileResponse(p, media_type="audio/wav")

    @app.delete("/api/library/{vid}/clips/{key}")
    def library_remove_clip(vid: str, key: str):
        studio.library.remove_clip(vid, key)
        return {"voice": voice_json(studio.library.get(vid))} if studio.library.get(vid) else {"ok": True}

    # ── phòng thu ──
    script = recording.load_script()

    @app.get("/api/recording/script")
    def rec_script():
        return {"items": [{"id": it.id, "group": it.group, "emotion": it.emotion,
                           "emotion_label": emotions.get(it.emotion).label, "text": it.text} for it in script],
                "groups": recording.GROUP_LABELS}

    @app.get("/api/recording/sessions")
    def rec_sessions():
        return {"sessions": recording.Session.list_names()}

    @app.get("/api/recording/{session}")
    def rec_session(session: str):
        s = recording.Session(session)
        st = s.stats(script)
        return {"name": s.name, "recorded": [it.id for it in script if s.has(it.id)], "stats": st,
                "summary": s.stats_text()}

    @app.post("/api/recording/{session}/takes/{item_id}")
    async def rec_save(session: str, item_id: str, file: UploadFile = File(...)):
        it = next((x for x in script if x.id == item_id), None)
        if it is None:
            raise HTTPException(404, "Không có câu này.")
        s = recording.Session(session)
        suffix = Path(file.filename or "take.webm").suffix or ".webm"
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / f"take{suffix}"
            tmp.write_bytes(await file.read())
            try:
                _p, dur, warns = s.save_take(it, tmp)
            except (ValueError, RuntimeError) as e:
                raise HTTPException(400, str(e))
        return {"duration": round(dur, 2), "warnings": warns, "summary": s.stats_text()}

    script_ids = {it.id for it in script}

    def check_item(item_id: str) -> None:
        # mã câu phải có trong kịch bản (chặn "..\\..\\" trên Windows)
        if item_id not in script_ids:
            raise HTTPException(404, "Không có câu này.")

    @app.get("/api/recording/{session}/takes/{item_id}")
    def rec_take(session: str, item_id: str):
        check_item(item_id)
        s = recording.Session(session)
        if not s.has(item_id):
            raise HTTPException(404, "Câu này chưa thu.")
        return FileResponse(s.take_path(item_id), media_type="audio/flac")

    @app.delete("/api/recording/{session}/takes/{item_id}")
    def rec_delete(session: str, item_id: str):
        check_item(item_id)
        s = recording.Session(session)
        s.delete_take(item_id)
        return {"summary": s.stats_text()}

    @app.post("/api/recording/{session}/build-voice")
    async def rec_build(session: str, request: Request):
        d = await request.json()
        try:
            vid, notes = recording.Session(session).build_voice(studio.library, d.get("name") or session,
                                                                d.get("dialect", "bac"))
        except ValueError as e:
            raise HTTPException(400, str(e))
        return {"voice_id": vid, "notes": notes}

    @app.post("/api/jobs/finetune")
    async def job_finetune(request: Request):
        d = await request.json()
        s = recording.Session(d.get("session") or "giong-cua-toi")
        from .voices import slugify
        run_name = slugify(str(d.get("run") or s.name))[:60]  # chặn "../" trong tên thư mục

        def run(progress, logline):
            s.write_metadata()
            for line in finetune.train(s.dir, run_name, float(d.get("epochs", 3)), int(d.get("rank", 16)),
                                       bool(d.get("low_vram", True))):
                logline(line)
                progress(0.5, line[:120])
            return {"merged": str(finetune.output_dir(run_name) / "merged")}
        return {"job": jobs.submit("finetune", run)}

    # ── cài đặt, từ điển, hệ thống ──
    @app.get("/api/settings")
    def get_settings():
        return settings_json()

    @app.put("/api/settings")
    async def put_settings(request: Request):
        d = await request.json()
        old = settings_mod.load()
        allowed = {"device", "cpu_precision", "dialect", "output_format", "target_lufs", "enhance", "dereverb",
                   "ai_clean", "sentence_pause", "paragraph_pause", "english_engine", "gemini_model",
                   "gemini_voice"}
        changes = {k: v for k, v in d.items() if k in allowed}
        if isinstance(d.get("gemini_api_key"), str) and d["gemini_api_key"].strip():
            changes["gemini_api_key"] = d["gemini_api_key"].strip()
        if d.get("clear_gemini_key"):
            changes["gemini_api_key"] = ""
        s = settings_mod.update(**changes)
        if (old.device, old.cpu_precision) != (s.device, s.cpu_precision):
            engines.get("core").unload()
        return settings_json()

    @app.get("/api/gemini/models")
    def gemini_models():
        try:
            return {"models": engines.get("gemini").list_models(refresh=True)}
        except Exception as e:
            raise HTTPException(400, _friendly(e))

    @app.get("/api/lexicon")
    def get_lexicon():
        return {"rows": studio.lexicon.rows()}

    @app.put("/api/lexicon")
    async def put_lexicon(request: Request):
        d = await request.json()
        rows = [r for r in d.get("rows", []) if isinstance(r, list) and len(r) >= 3]
        studio.lexicon.set_entries([(r[0], r[1], r[2]) for r in rows])
        studio.lexicon.save_user()
        return {"rows": studio.lexicon.rows()}

    @app.get("/api/system")
    def system():
        info: dict[str, Any] = {"version": __version__, "data_dir": str(paths.DATA),
                                "models_dir": str(paths.MODELS), "ffmpeg": bool(audio.ffmpeg_exe())}
        try:
            import torch
            if torch.cuda.is_available():
                p = torch.cuda.get_device_properties(0)
                info["gpu"] = {"name": p.name, "vram_gb": round(p.total_memory / 1024 ** 3, 1),
                               "cuda": torch.version.cuda}
        except Exception:
            pass
        core = engines.get("core")
        info["core_backend"] = getattr(core, "backend", "?")
        return info

    @app.post("/api/preload")
    def preload():
        try:
            core = engines.get("core")
            core.load()
            return {"ok": True, "backend": core.backend}
        except Exception as e:
            raise HTTPException(400, _friendly(e))

    # ── cập nhật & đồng bộ ──
    def upd_error(e: Exception) -> HTTPException:
        return HTTPException(400, _friendly(e))

    @app.get("/api/update/status")
    def update_status():
        st = updater.status()
        st["cached"] = dict(update_cache)
        st["boot_id"] = BOOT_ID
        return st

    @app.post("/api/update/check")
    def update_check():
        try:
            info = updater.check()
        except Exception as e:
            raise upd_error(e)
        update_cache.update({k: info[k] for k in ("current", "latest", "available")})
        return info

    @app.post("/api/jobs/update")
    def job_update():
        def run(progress, logline):
            progress(0.1, "Đang cập nhật…")
            res = updater.apply(log=logline)
            update_cache.update({"available": False, "latest": res["to"]})
            logline("Đang khởi động lại phần mềm…")
            restart()
            return {**res, "restarting": True}
        return {"job": jobs.submit("update", run)}

    @app.post("/api/jobs/rollback")
    def job_rollback():
        def run(progress, logline):
            res = updater.rollback(log=logline)
            logline("Đang khởi động lại phần mềm…")
            restart()
            return {**res, "restarting": True}
        return {"job": jobs.submit("rollback", run)}

    @app.post("/api/jobs/sync")
    def job_sync():
        def run(progress, logline):
            progress(0.2, "Đang đồng bộ với GitHub…")
            return updater.sync_data(log=logline)
        return {"job": jobs.submit("sync", run)}

    @app.post("/api/update/connect")
    async def update_connect(request: Request):
        d = await request.json()
        try:
            updater.connect(d.get("url", ""))
        except Exception as e:
            raise upd_error(e)
        return updater.status()

    @app.post("/api/update/restart")
    def update_restart():
        restart()
        return {"restarting": True}

    # ── file kết quả & giao diện ──
    @app.get("/files/{rel:path}")
    def files(rel: str):
        base = paths.DATA.resolve()
        p = (base / rel).resolve()
        if base not in p.parents or not p.is_file():
            raise HTTPException(404)
        media = {".wav": "audio/wav", ".mp3": "audio/mpeg", ".flac": "audio/flac",
                 ".srt": "application/x-subrip"}.get(p.suffix.lower())
        return FileResponse(p, media_type=media, filename=p.name if p.suffix.lower() == ".srt" else None)

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
    return app


def run(port: int = 7860, open_window: bool = True) -> None:
    import uvicorn
    if os.environ.get("VOXVIET_RESTARTED") == "1":
        _wait_port_free(port)  # tiến trình cũ đang thoát
    token = session_token()
    app = create_app(auth_token=token)
    url = f"http://127.0.0.1:{port}/"
    if open_window:
        threading.Timer(1.2, open_app_window, args=(f"{url}?t={token}",)).start()
    print(f"\n  VoxViet Studio đang chạy: {url}\n  (đóng cửa sổ dòng lệnh này để tắt phần mềm)\n")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def open_app_window(url: str) -> None:
    """Mở giao diện trong cửa sổ riêng (Edge/Chrome chế độ ứng dụng), không có thanh địa chỉ."""
    import os
    import subprocess
    import webbrowser
    candidates = []
    if os.name == "nt":
        pf = [os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
              os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("LOCALAPPDATA", "")]
        for base in pf:
            candidates += [Path(base) / "Microsoft/Edge/Application/msedge.exe",
                           Path(base) / "Google/Chrome/Application/chrome.exe"]
    else:
        for name in ("microsoft-edge", "google-chrome", "chromium", "chromium-browser"):
            exe = shutil.which(name)
            if exe:
                candidates.append(Path(exe))
    profile = paths.DATA / ".app-window"
    for exe in candidates:
        if exe.is_file():
            try:
                # Hồ sơ trình duyệt riêng cho cửa sổ phần mềm; tắt đồng bộ tài khoản, tải nền,
                # dịch trang… để cửa sổ không tự kết nối ra ngoài.
                subprocess.Popen([str(exe), f"--app={url}", "--window-size=1440,900",
                                  f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
                                  "--disable-sync", "--disable-background-networking", "--disable-component-update",
                                  "--disable-domain-reliability", "--metrics-recording-only",
                                  "--disable-features=Translate,MediaRouter,OptimizationHints,AutofillServerCommunication"])
                return
            except OSError:
                continue
    webbrowser.open(url)
