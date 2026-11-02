"""Tự kiểm tra bảo mật trên máy của bạn — không gửi gì ra ngoài, không chạy file nào được quét.

    .venv\\Scripts\\python.exe tools\\kiem_tra_bao_mat.py     (hoặc chạy kiem_tra_bao_mat.bat)

Kiểm tra:
  1. Mã Python đi kèm mô hình (tải qua trust_remote_code) — tìm lệnh hệ thống, mạng, eval/exec…
  2. File trọng số dạng pickle (.bin/.pt/.pth/.ckpt/.pkl) — đọc "danh sách nhập" mà KHÔNG nạp,
     cảnh báo nếu tham chiếu tới thứ ngoài dữ liệu tensor (os, subprocess, builtins.eval…).
  3. Thư viện lõi đã cài (vieneu, sea_g2p) — đối chiếu từng file với mã băm gốc trong gói (RECORD)
     để phát hiện file bị sửa sau khi cài.
  4. Ghi mã băm các file chạy được của mô hình; lần sau báo nếu chúng bị thay đổi.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import pickletools
import re
import sys
import zipfile
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
STATE = ROOT / "data" / ".local" / "model_code_hashes.json"

RISKY_PY = re.compile(
    r"\bsubprocess\b|os\.system|os\.popen|\beval\(|\bexec\(|__import__\(|\bsocket\b|requests\.|urllib\.request|"
    r"http\.client|b64decode|marshal\.loads|ctypes\.|pickle\.loads|shutil\.rmtree|webbrowser|smtplib|ftplib")
SAFE_PICKLE_GLOBALS = re.compile(
    r"^(torch\._utils _rebuild_\w+|torch \w+Storage|torch\.serialization _get_layout|torch (float|bfloat16|half|int\d*|long|bool)\w*|"
    r"collections OrderedDict|numpy\.core\.multiarray (_reconstruct|scalar)|numpy\._core\.multiarray (_reconstruct|scalar)|"
    r"numpy (ndarray|dtype)|_codecs encode|torch\._tensor _rebuild_from_type_v2|torch\.nn\.parameter Parameter|"
    r"builtins (set|frozenset|dict|list|tuple|int|float|str|bytes|bytearray|slice|complex))$")

problems: list[str] = []
notes: list[str] = []


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pickle_globals(data: bytes) -> set[str]:
    out = io.StringIO()
    try:
        pickletools.dis(data, out=out)
    except Exception:
        pass  # pickle hỏng/không chuẩn: vẫn lấy được phần đã đọc
    text = out.getvalue()
    found = set(re.findall(r"GLOBAL\s+'([^']+)'", text))
    # STACK_GLOBAL: hai chuỗi liền trước là module và tên
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "STACK_GLOBAL" in ln:
            prev = [re.search(r"UNICODE\s+'([^']+)'", x) for x in lines[max(0, i - 4):i]]
            vals = [m.group(1) for m in prev if m]
            if len(vals) >= 2:
                found.add(f"{vals[-2]} {vals[-1]}")
    return found


def scan_pickle_file(p: Path) -> None:
    try:
        if zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as z:
                blobs = [z.read(n) for n in z.namelist() if n.endswith(".pkl")]
        else:
            raw = p.read_bytes()
            if not raw[:2] in (b"\x80\x02", b"\x80\x03", b"\x80\x04", b"\x80\x05"):
                return  # không phải pickle (vd. tokenizer.bin)
            blobs = [raw[: 50 << 20]]
    except Exception as e:
        notes.append(f"Không đọc được {p.name}: {e}")
        return
    bad = sorted({g for b in blobs for g in pickle_globals(b) if not SAFE_PICKLE_GLOBALS.match(g)})
    if bad:
        problems.append(f"File pickle tham chiếu thứ lạ: {p}  → {bad}")


def scan_models() -> dict:
    hashes = {}
    if not MODELS.exists():
        notes.append("Chưa có thư mục models/ (chưa tải mô hình).")
        return hashes
    py_files = list(MODELS.rglob("*.py"))
    for p in py_files:
        rel = str(p.relative_to(ROOT))
        hashes[rel] = sha256(p)
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if RISKY_PY.search(line) and not line.strip().startswith("#"):
                problems.append(f"{rel}:{i}: {line.strip()[:140]}")
    pk = [p for ext in ("*.bin", "*.pt", "*.pth", "*.ckpt", "*.pkl") for p in MODELS.rglob(ext)]
    for p in pk:
        if p.stat().st_size < 3 << 30:
            scan_pickle_file(p)
    notes.append(f"Đã quét {len(py_files)} file mã Python và {len(pk)} file trọng số dạng pickle trong models/.")
    notes.append(f"File .safetensors / .onnx là định dạng chỉ chứa số liệu, không chạy được mã — "
                 f"có {len(list(MODELS.rglob('*.safetensors'))) + len(list(MODELS.rglob('*.onnx')))} file.")
    return hashes


def verify_installed(dist_name: str) -> None:
    try:
        dist = metadata.distribution(dist_name)
    except metadata.PackageNotFoundError:
        notes.append(f"Chưa cài {dist_name}.")
        return
    record = dist.read_text("RECORD") or ""
    base = Path(dist.locate_file(""))
    checked = changed = 0
    for row in csv.reader(record.splitlines()):
        if len(row) < 2 or not row[1].startswith("sha256="):
            continue
        f = base / row[0]
        if not f.exists() or f.suffix == ".pyc":
            continue
        want = row[1].split("=", 1)[1]
        got = base64.urlsafe_b64encode(hashlib.sha256(f.read_bytes()).digest()).rstrip(b"=").decode()
        checked += 1
        if got != want:
            changed += 1
            problems.append(f"File của {dist_name} đã bị sửa sau khi cài: {row[0]}")
    notes.append(f"{dist_name} {dist.version}: đối chiếu {checked} file với mã băm gốc — {changed} file khác.")


def compare_hashes(now: dict) -> None:
    if not now:
        return
    try:
        before = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        before = {}
    if before:
        diff = sorted(k for k in now if k in before and before[k] != now[k])
        new = sorted(k for k in now if k not in before)
        for k in diff:
            problems.append(f"Mã đi kèm mô hình đã THAY ĐỔI kể từ lần kiểm tra trước: {k}")
        if new:
            notes.append(f"{len(new)} file mã mô hình mới (lần đầu thấy).")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(now, indent=1), encoding="utf-8")


def main() -> int:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("=== VoxViet Studio — tự kiểm tra bảo mật ===\n")
    for d in ("vieneu", "sea-g2p"):
        verify_installed(d)
    compare_hashes(scan_models())
    for n in notes:
        print("·", n)
    print()
    if problems:
        print(f"⚠ {len(problems)} điểm cần xem (không nhất thiết là mã độc — hãy gửi danh sách này để được kiểm tra):")
        for p in problems:
            print("  -", p)
        return 1
    print("✅ Không thấy dấu hiệu bất thường.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
