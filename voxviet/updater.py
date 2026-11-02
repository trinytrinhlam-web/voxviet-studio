"""Cập nhật phần mềm và đồng bộ dữ liệu qua GitHub (kênh cập nhật = nhánh ``main``).

Quy trình cập nhật an toàn:
  1. ``git fetch`` → so sánh phiên bản, đọc CHANGELOG.md của bản mới.
  2. Ghi mốc (commit hiện tại) vào lịch sử để có thể quay lại.
  3. ``git pull --rebase --autostash`` (giữ nguyên dữ liệu/sửa đổi của bạn).
  4. Bản vá đổi danh sách thư viện → tự cài thêm thư viện.
  5. Tự kiểm: nạp thử mã mới trong tiến trình riêng. Hỏng → tự quay lại mốc cũ.
  6. Khởi động lại phần mềm (do máy chủ thực hiện).

Đồng bộ dữ liệu: commit thư mục ``data/`` (kho giọng, bản thu, từ điển) → kéo về → đẩy lên.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import __version__, paths

BRANCH = "main"
DATA_PREFIX = "data/"
Log = Callable[[str], None]


class UpdateError(RuntimeError):
    pass


def parse_version(v: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", v or "")
    return tuple(int(n) for n in nums[:3]) or (0,)


def parse_changelog(text: str) -> list[dict]:
    """``## 0.6.0 — 2026-11-02`` + các dòng ``- …`` → [{version, date, items}]"""
    out: list[dict] = []
    for block in re.split(r"(?m)^## ", text or "")[1:]:
        head, _, body = block.partition("\n")
        m = re.match(r"\s*v?(\d+\.\d+(?:\.\d+)?)\s*(?:[—–-]\s*(.*))?", head)
        if not m:
            continue
        items = [ln.strip()[2:].strip() for ln in body.splitlines() if ln.strip().startswith(("- ", "* "))]
        out.append({"version": m.group(1), "date": (m.group(2) or "").strip(), "items": items})
    return out


@dataclass
class Updater:
    root: Path = field(default_factory=lambda: paths.ROOT)
    state_file: Path = field(default_factory=lambda: paths.DATA / ".local" / "update.json")
    python: str = field(default_factory=lambda: sys.executable)

    # ── tiện ích git ──────────────────────────────────────────────────────────
    def git(self, *args: str, check: bool = True, timeout: int = 120) -> str:
        exe = shutil.which("git")
        if not exe:
            raise UpdateError("Máy chưa cài Git. Tải tại https://git-scm.com/download/win rồi mở lại phần mềm.")
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C", LANG="C")
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            p = subprocess.run([exe, "-c", "core.quotepath=off", *args], cwd=str(self.root), capture_output=True,
                               text=True, encoding="utf-8", errors="replace", env=env, timeout=timeout,
                               creationflags=flags)
        except subprocess.TimeoutExpired:
            raise UpdateError(f"Git không phản hồi (git {args[0]}). Kiểm tra Internet.") from None
        if check and p.returncode != 0:
            err = (p.stderr or p.stdout).strip().splitlines()
            raise UpdateError(_friendly_git_error(err[-1] if err else f"git {args[0]} lỗi"))
        return p.stdout.strip()

    def is_repo(self) -> bool:
        if not shutil.which("git"):
            return False
        try:
            return self.git("rev-parse", "--is-inside-work-tree", check=True, timeout=15) == "true" and \
                Path(self.git("rev-parse", "--show-toplevel", timeout=15)).resolve() == self.root.resolve()
        except UpdateError:
            return False

    # ── lưu trạng thái cục bộ (không đồng bộ) ─────────────────────────────────
    def _state(self) -> dict:
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save_state(self, st: dict) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")

    def history(self) -> list[dict]:
        return self._state().get("history", [])

    def _add_history(self, entry: dict) -> None:
        st = self._state()
        st.setdefault("history", []).insert(0, entry)
        st["history"] = st["history"][:30]
        self._save_state(st)

    # ── trạng thái & kiểm tra ─────────────────────────────────────────────────
    def local_version(self) -> str:
        m = re.search(r'__version__\s*=\s*"([^"]+)"', (self.root / "voxviet" / "__init__.py").read_text(encoding="utf-8"))
        return m.group(1) if m else __version__

    def status(self) -> dict:
        st = self._state()
        info = {"version": self.local_version(), "git": bool(shutil.which("git")), "repo": False,
                "last_check": st.get("last_check"), "last_result": st.get("last_result"),
                "last_sync": st.get("last_sync"), "history": st.get("history", [])[:10]}
        if not info["git"]:
            return info
        info["repo"] = self.is_repo()
        if info["repo"]:
            info["commit"] = self.git("rev-parse", "--short", "HEAD")
            info["remote"] = _hide_token(self.git("remote", "get-url", "origin", check=False))
            dirty = [ln[3:] for ln in self.git("status", "--porcelain", check=False).splitlines() if ln.strip()]
            info["data_changes"] = len([d for d in dirty if d.startswith(DATA_PREFIX)])
            info["code_changes"] = len([d for d in dirty if not d.startswith(DATA_PREFIX)])
        return info

    def check(self) -> dict:
        """Hỏi GitHub có bản mới không (không thay đổi gì trên máy)."""
        if not self.is_repo():
            raise UpdateError("Thư mục phần mềm chưa kết nối GitHub. Bấm 'Kết nối GitHub' trong trang Cập nhật.")
        self.git("fetch", "--quiet", "origin", BRANCH, timeout=180)
        behind = int(self.git("rev-list", "--count", f"HEAD..origin/{BRANCH}") or 0)
        ahead = int(self.git("rev-list", "--count", f"origin/{BRANCH}..HEAD") or 0)
        local_v = self.local_version()
        remote_init = self.git("show", f"origin/{BRANCH}:voxviet/__init__.py", check=False)
        m = re.search(r'__version__\s*=\s*"([^"]+)"', remote_init)
        remote_v = m.group(1) if m else local_v
        changed = self.git("diff", "--name-only", "HEAD", f"origin/{BRANCH}").splitlines() if behind else []
        code_files = [f for f in changed if not f.startswith(DATA_PREFIX)]
        notes = [c for c in parse_changelog(self.git("show", f"origin/{BRANCH}:CHANGELOG.md", check=False))
                 if parse_version(c["version"]) > parse_version(local_v)]
        commits = []
        if behind:
            for ln in self.git("log", "--format=%h\x1f%ad\x1f%s", "--date=short", f"HEAD..origin/{BRANCH}").splitlines()[:30]:
                h, d, s = (ln.split("\x1f") + ["", "", ""])[:3]
                commits.append({"hash": h, "date": d, "subject": s})
        result = {
            "current": local_v, "latest": remote_v, "behind": behind, "ahead": ahead,
            "available": bool(code_files),  # chỉ dữ liệu thay đổi → không phải bản cập nhật phần mềm
            "data_only": bool(changed) and not code_files,
            "needs_deps": any(Path(f).name.startswith("requirements") for f in code_files),
            "notes": notes, "commits": commits, "files": len(code_files),
        }
        st = self._state()
        st["last_check"] = time.strftime("%Y-%m-%d %H:%M")
        st["last_result"] = {k: result[k] for k in ("current", "latest", "available")}
        self._save_state(st)
        return result

    # ── cài bản vá ────────────────────────────────────────────────────────────
    def apply(self, log: Log = print, install_deps: Callable[[Log], None] | None = None,
              self_test: Callable[[], None] | None = None) -> dict:
        info = self.check()
        if not info["behind"]:
            raise UpdateError("Bạn đang dùng bản mới nhất.")
        prev = self.git("rev-parse", "HEAD")
        prev_v = self.local_version()
        log(f"Mốc hiện tại: {prev_v} ({prev[:7]}) — có thể quay lại nếu cần.")
        log(f"Đang tải bản vá ({info['behind']} thay đổi)…")
        try:
            self.git("pull", "--rebase", "--autostash", "origin", BRANCH, timeout=300)
        except UpdateError as e:
            self.git("rebase", "--abort", check=False)
            raise UpdateError(f"Không áp dụng được bản vá, phần mềm giữ nguyên. Chi tiết: {e}") from None
        new_v = self.local_version()
        changed = self.git("diff", "--name-only", prev, "HEAD").splitlines()
        try:
            if any(Path(f).name.startswith("requirements") for f in changed):
                log("Bản vá cần thêm thư viện — đang cài…")
                (install_deps or self.install_deps)(log)
            log("Đang kiểm tra bản mới…")
            (self_test or self.self_test)()
        except Exception as e:
            log(f"Bản mới có lỗi: {e}")
            log("Đang quay lại phiên bản cũ…")
            self.git("reset", "--keep", prev, check=False)
            self._add_history({"time": time.strftime("%Y-%m-%d %H:%M"), "from": prev_v, "to": new_v,
                               "from_commit": prev, "ok": False, "note": str(e)[:200]})
            raise UpdateError(f"Bản cập nhật {new_v} không chạy được nên đã tự quay lại {prev_v}. Lỗi: {e}") from None
        self._add_history({"time": time.strftime("%Y-%m-%d %H:%M"), "from": prev_v, "to": new_v,
                           "from_commit": prev, "to_commit": self.git("rev-parse", "HEAD"), "ok": True})
        st = self._state()  # kết quả kiểm tra cũ ("có bản mới") không còn đúng nữa
        st["last_result"] = {"current": new_v, "latest": new_v, "available": False}
        self._save_state(st)
        log(f"✅ Đã cập nhật {prev_v} → {new_v}.")
        return {"from": prev_v, "to": new_v}

    def rollback(self, log: Log = print) -> dict:
        last = next((h for h in self.history() if h.get("ok") and h.get("from_commit")), None)
        if not last:
            raise UpdateError("Chưa có lần cập nhật nào để quay lại.")
        cur_v = self.local_version()
        log(f"Quay lại phiên bản {last['from']} ({last['from_commit'][:7]})…")
        self.git("reset", "--keep", last["from_commit"])
        self._add_history({"time": time.strftime("%Y-%m-%d %H:%M"), "from": cur_v, "to": last["from"],
                           "from_commit": None, "ok": True, "note": "quay lại"})
        st = self._state()  # để lần mở sau tự kiểm tra lại
        st.pop("last_check", None)
        st.pop("last_result", None)
        self._save_state(st)
        return {"from": cur_v, "to": self.local_version()}

    def install_deps(self, log: Log) -> None:
        uv = shutil.which("uv") or str(Path.home() / ".local" / "bin" / ("uv.exe" if os.name == "nt" else "uv"))
        reqs = ["requirements.txt"]
        try:
            import torch  # noqa: F401
            reqs.append("requirements-gpu.txt")
        except Exception:
            pass
        for req in reqs:
            if not (self.root / req).exists():
                continue
            cmd = ([uv, "pip", "install", "--python", self.python, "-r", req] if Path(uv).exists()
                   else [self.python, "-m", "pip", "install", "-r", req])
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            p = subprocess.run(cmd, cwd=str(self.root), capture_output=True, text=True, encoding="utf-8",
                               errors="replace", creationflags=flags, timeout=1800)
            for ln in (p.stdout + p.stderr).strip().splitlines()[-8:]:
                log("  " + ln)
            if p.returncode != 0:
                raise UpdateError(f"Cài thư viện thất bại ({req}).")

    def self_test(self) -> None:
        """Nạp thử mã mới trong tiến trình riêng (không ảnh hưởng phần mềm đang chạy)."""
        code = "import voxviet, voxviet.server, voxviet.pipeline, voxviet.updater; print(voxviet.__version__)"
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        p = subprocess.run([self.python, "-c", code], cwd=str(self.root), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180, creationflags=flags,
                           env=dict(os.environ, VOXVIET_DEMO="1"))
        if p.returncode != 0:
            raise UpdateError((p.stderr.strip().splitlines() or ["không nạp được mã mới"])[-1])

    # ── đồng bộ dữ liệu ──────────────────────────────────────────────────────
    def sync_data(self, log: Log = print) -> dict:
        info = self.check()
        if info["available"]:
            raise UpdateError(f"Có bản cập nhật phần mềm {info['latest']} trên GitHub. Hãy bấm 'Cập nhật ngay' "
                              "trước, rồi đồng bộ.")
        self.git("add", "-A", "--", "data")
        committed = 0
        if self.git("diff", "--cached", "--name-only"):
            committed = len(self.git("diff", "--cached", "--name-only").splitlines())
            host = socket.gethostname()
            self.git("commit", "-m", f"Đồng bộ dữ liệu từ {host} {time.strftime('%Y-%m-%d %H:%M')}")
            log(f"Đã ghi {committed} thay đổi dữ liệu trên máy này.")
        else:
            log("Máy này không có dữ liệu mới.")
        before = self.git("rev-parse", "HEAD")
        try:
            self.git("pull", "--rebase", "--autostash", "origin", BRANCH, timeout=300)
        except UpdateError as e:
            self.git("rebase", "--abort", check=False)
            raise UpdateError(f"Xung đột khi lấy dữ liệu từ máy khác: {e}") from None
        pulled = int(self.git("rev-list", "--count", f"{before}..HEAD") or 0) if before else 0
        log(f"Đã lấy {pulled} thay đổi từ GitHub." if pulled else "GitHub không có dữ liệu mới.")
        if int(self.git("rev-list", "--count", f"origin/{BRANCH}..HEAD") or 0):
            self.git("push", "origin", f"HEAD:{BRANCH}", timeout=300)
            log("Đã đẩy dữ liệu lên GitHub.")
        st = self._state()
        st["last_sync"] = time.strftime("%Y-%m-%d %H:%M")
        self._save_state(st)
        return {"committed": committed, "pulled": pulled}

    def connect(self, url: str, log: Log = print) -> None:
        """Thư mục cài từ ZIP: nối với repo GitHub rồi lấy bản mới nhất (giữ dữ liệu chưa theo dõi)."""
        if self.is_repo():
            raise UpdateError("Thư mục đã kết nối GitHub.")
        if not re.match(r"^https://github\.com/[\w.-]+/[\w.-]+?(\.git)?$", url.strip()):
            raise UpdateError("Địa chỉ phải dạng https://github.com/<tài khoản>/<repo>")
        self.git("init", "-q")
        self.git("remote", "add", "origin", url.strip())
        log("Đang tải từ GitHub…")
        self.git("fetch", "origin", BRANCH, timeout=300)
        self.git("checkout", "-q", "-f", "-B", BRANCH, f"origin/{BRANCH}")
        self.git("branch", "-q", f"--set-upstream-to=origin/{BRANCH}", BRANCH, check=False)


def _hide_token(url: str) -> str:
    return re.sub(r"//[^@/]+@", "//", url or "")


def _friendly_git_error(line: str) -> str:
    low = line.lower()
    if "could not resolve host" in low or "unable to access" in low:
        return "Không kết nối được GitHub (kiểm tra Internet)."
    if "authentication" in low or "403" in low or "could not read username" in low:
        return "GitHub từ chối truy cập — hãy đăng nhập lại GitHub trên máy này (chạy update.bat một lần)."
    if "conflict" in low:
        return "Có xung đột giữa thay đổi trên máy này và trên GitHub."
    return line
