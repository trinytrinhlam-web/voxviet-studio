"""Gửi văn bản vào VoxViet Studio từ dòng lệnh — dành cho người và công cụ AI khác.

Chỉ dùng thư viện chuẩn của Python. Tự tìm cổng và khoá phiên của phần mềm đang chạy trên máy này;
chưa chạy thì tự mở (kèm cửa sổ). Kết quả in ra dạng JSON trên một dòng (stdout), tiến độ in ra stderr.

Ví dụ (chạy trong thư mục cài, ví dụ E:\\VoxViet Studio):
    .venv\\Scripts\\python.exe tools\\voxviet_cli.py voices
    .venv\\Scripts\\python.exe tools\\voxviet_cli.py doc --voice preset:ha-long --file bai.txt --mp3
    .venv\\Scripts\\python.exe tools\\voxviet_cli.py doc --voice preset:sai-gon --text "Xin chào [vui] các bạn!"
    .venv\\Scripts\\python.exe tools\\voxviet_cli.py dialogue --file kich_ban.txt --cast cast.json
    .venv\\Scripts\\python.exe tools\\voxviet_cli.py dub --file phu_de.srt --voice preset:ho-tay
    .venv\\Scripts\\python.exe tools\\voxviet_cli.py check --file bai.txt      (xem máy sẽ đọc thế nào)

Chi tiết định dạng văn bản và tham số: HUONG-DAN-CHO-AI.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("VOXVIET_DATA", ROOT / "data"))
LOCAL = DATA / ".local"
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # máy này → không qua proxy


class CliError(Exception):
    pass


def _say(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ── kết nối phần mềm ─────────────────────────────────────────────────────────

class Client:
    def __init__(self, port: int, token: str):
        self.base = f"http://127.0.0.1:{port}"
        self.token = token

    def call(self, method: str, path: str, body: dict | None = None, timeout: float = 30) -> dict:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method, headers={
            "Cookie": f"vv_session={self.token}", "X-VoxViet": "1", "Content-Type": "application/json"})
        try:
            with _OPENER.open(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                detail = json.loads(e.read().decode("utf-8")).get("detail")
            except Exception:
                detail = None
            raise CliError(detail or f"Lỗi HTTP {e.code} ở {path}") from None

    def job(self, path: str, body: dict, timeout: float) -> dict:
        jid = self.call("POST", path, body)["job"]
        t0, last = time.time(), ""
        while True:
            j = self.call("GET", f"/api/jobs/{jid}")
            msg = f"{int(j.get('progress', 0) * 100):3d}% {j.get('message') or ''}"
            if msg != last:
                _say(msg)
                last = msg
            if j["status"] == "done":
                return j["result"]
            if j["status"] == "error":
                raise CliError(j.get("error") or "Có lỗi xảy ra.")
            if time.time() - t0 > timeout:
                raise CliError(f"Quá {int(timeout)} giây mà chưa xong (việc vẫn chạy tiếp trong phần mềm).")
            time.sleep(0.5)


def _read_token() -> str | None:
    try:
        tok = (LOCAL / "session_token").read_text(encoding="utf-8").strip()
        return tok or None
    except OSError:
        return None


def _try_connect() -> Client | None:
    tok = _read_token()
    if not tok:
        return None
    ports = []
    try:
        ports.append(int(json.loads((LOCAL / "instance.json").read_text(encoding="utf-8"))["port"]))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    ports += [p for p in range(7860, 7870) if p not in ports]
    for port in ports:
        c = Client(port, tok)
        try:
            if "boot_id" in c.call("GET", "/api/state", timeout=2):
                return c
        except Exception:
            continue
    return None


def _python_for_app() -> str:
    win = os.name == "nt"
    venv = ROOT / ".venv" / ("Scripts" if win else "bin")
    for name in (("pythonw.exe", "python.exe") if win else ("python",)):
        if (venv / name).exists():
            return str(venv / name)
    return sys.executable


def connect(start: bool = True, wait: float = 90) -> Client:
    c = _try_connect()
    if c or not start:
        if not c:
            raise CliError("VoxViet Studio chưa chạy. Mở phần mềm trước, hoặc bỏ --no-start.")
        return c
    _say("VoxViet Studio chưa chạy — đang mở…")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen([_python_for_app(), str(ROOT / "app.py"), "--app"], cwd=str(ROOT), creationflags=flags,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(1)
        c = _try_connect()
        if c:
            return c
    raise CliError(f"Không mở được VoxViet Studio sau {int(wait)} giây. Xem {LOCAL / 'voxviet.log'}")


# ── tiện ích ─────────────────────────────────────────────────────────────────

def _text_arg(a) -> str:
    if a.file:
        raw = Path(a.file).read_bytes()
        for enc in ("utf-8-sig", "utf-16", "cp1258"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
        raise CliError(f"Không đọc được {a.file} (hãy lưu dạng UTF-8).")
    if a.text is not None:
        return a.text
    if not sys.stdin.isatty():
        return sys.stdin.buffer.read().decode("utf-8-sig")
    raise CliError("Chưa có văn bản: dùng --text, --file, hoặc truyền qua stdin.")


def _local_path(url: str | None) -> str | None:
    if not url or not url.startswith("/files/"):
        return None
    return str((DATA / url[len("/files/"):]).resolve())


def _result(r: dict) -> dict:
    return {"ok": True, "audio": _local_path(r.get("audio_url")), "srt": _local_path(r.get("srt_url")),
            "duration_s": r.get("duration"), "elapsed_s": r.get("elapsed"), "warnings": r.get("warnings", [])}


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--text", help="văn bản (đặt trong ngoặc kép)")
    p.add_argument("--file", help="file văn bản UTF-8")
    p.add_argument("--mp3", action="store_true", help="xuất MP3 (mặc định theo Cài đặt, thường là WAV)")
    p.add_argument("--timeout", type=float, default=6 * 3600, help="giây tối đa chờ kết quả")


# ── lệnh ─────────────────────────────────────────────────────────────────────

def cmd_voices(c: Client, a) -> dict:
    vs = c.call("GET", f"/api/voices?language={a.language}")["voices"]
    return {"ok": True, "voices": [{k: v.get(k) for k in ("value", "label", "kind", "region", "gender", "style")}
                                   for v in vs]}


def cmd_doc(c: Client, a) -> dict:
    body = {"text": _text_arg(a), "language": a.language, "voice": a.voice, "emotion": a.emotion,
            "speed": a.speed, "pause": a.pause, "dialect": a.dialect, "fmt": "mp3" if a.mp3 else None,
            "enhance": a.enhance, "dereverb": a.dereverb, "ai_clean": a.ai_clean or None}
    return _result(c.job("/api/jobs/tts", {k: v for k, v in body.items() if v is not None}, a.timeout))


def cmd_dialogue(c: Client, a) -> dict:
    script = _text_arg(a)
    cast = json.loads(Path(a.cast).read_text(encoding="utf-8-sig")) if a.cast else {}
    found = c.call("POST", "/api/dialogue/parse", {"script": script})["speakers"]
    missing = [s for s in found if s not in cast]
    if missing:
        _say(f"Nhân vật chưa gán giọng (dùng giọng của nhân vật đầu tiên trong cast): {', '.join(missing)}")
    body = {"script": script, "cast": cast, "gap": a.gap, "fmt": "mp3" if a.mp3 else None}
    out = _result(c.job("/api/jobs/dialogue", body, a.timeout))
    out["speakers"] = found
    return out


def cmd_dub(c: Client, a) -> dict:
    body = {"srt": _text_arg(a), "language": a.language, "voice": a.voice, "emotion": a.emotion,
            "speed": a.speed, "max_stretch": a.max_stretch, "fmt": "mp3" if a.mp3 else None}
    return _result(c.job("/api/jobs/dub", body, a.timeout))


def cmd_check(c: Client, a) -> dict:
    r = c.call("POST", "/api/normalize", {"text": _text_arg(a), "language": a.language, "voice": a.voice,
                                          "dialect": a.dialect})
    return {"ok": True, **r}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="voxviet_cli", description="Gửi văn bản vào VoxViet Studio.")
    ap.add_argument("--no-start", action="store_true", help="không tự mở phần mềm nếu chưa chạy")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("voices", help="liệt kê giọng")
    p.add_argument("--language", default="vi", choices=["vi", "en"])
    p.set_defaults(fn=cmd_voices)

    p = sub.add_parser("doc", help="đọc văn bản → file âm thanh + phụ đề")
    _common(p)
    p.add_argument("--voice", default=None, help="preset:<mã> hoặc voice:<mã> (xem lệnh voices)")
    p.add_argument("--language", default="vi", choices=["vi", "en"])
    p.add_argument("--emotion", default="trung_tinh")
    p.add_argument("--speed", type=float, default=1.0, help="0.6 – 1.6")
    p.add_argument("--pause", type=float, default=1.0, help="nhịp nghỉ giữa câu, 0.3 – 2.5")
    p.add_argument("--dialect", choices=["bac", "nam"], default=None, help="cách đọc số; mặc định theo giọng")
    p.add_argument("--enhance", choices=["goc", "nhe", "trong", "sang"], default=None)
    p.add_argument("--dereverb", choices=["tat", "nhe", "vua", "manh"], default=None)
    p.add_argument("--ai-clean", action="store_true", help="khử nhiễu AI (chậm hơn)")
    p.set_defaults(fn=cmd_doc)

    p = sub.add_parser("dialogue", help="kịch bản nhiều nhân vật")
    _common(p)
    p.add_argument("--cast", help='file JSON: {"Tên": {"voice": "preset:ha-long", "emotion": "vui", ...}}')
    p.add_argument("--gap", type=float, default=0.35, help="khoảng lặng giữa các lượt nói (giây)")
    p.set_defaults(fn=cmd_dialogue)

    p = sub.add_parser("dub", help="lồng tiếng theo phụ đề .srt")
    _common(p)
    p.add_argument("--voice", default=None)
    p.add_argument("--language", default="vi", choices=["vi", "en"])
    p.add_argument("--emotion", default="trung_tinh")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--max-stretch", type=float, default=1.35, help="tăng tốc tối đa để vừa thời lượng câu")
    p.set_defaults(fn=cmd_dub)

    p = sub.add_parser("check", help="xem văn bản sau chuẩn hoá (máy sẽ đọc thế nào), không tạo âm thanh")
    _common(p)
    p.add_argument("--voice", default=None)
    p.add_argument("--language", default="vi", choices=["vi", "en"])
    p.add_argument("--dialect", choices=["bac", "nam"], default=None)
    p.set_defaults(fn=cmd_check)

    a = ap.parse_args(argv)
    try:
        out = a.fn(connect(start=not a.no_start), a)
        code = 0
    except CliError as e:
        out, code = {"ok": False, "error": str(e)}, 1
    except (OSError, ValueError) as e:
        out, code = {"ok": False, "error": f"{type(e).__name__}: {e}"}, 1
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
