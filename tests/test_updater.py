"""Kiểm thử module cập nhật với repo git tạm: một 'GitHub' (bare) và hai 'máy'."""

import shutil
import subprocess
from pathlib import Path

import pytest

from voxviet.updater import Updater, UpdateError, parse_changelog, parse_version

pytestmark = pytest.mark.skipif(not shutil.which("git"), reason="cần git")


def sh(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit_all(root, msg):
    sh(root, "add", "-A")
    sh(root, "commit", "-q", "-m", msg)


@pytest.fixture
def world(tmp_path):
    remote = tmp_path / "github.git"
    sh(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    dev = tmp_path / "dev"
    sh(tmp_path, "clone", "-q", str(remote), str(dev))
    for r in (dev,):
        sh(r, "config", "user.email", "t@t"); sh(r, "config", "user.name", "t")
    write(dev, "voxviet/__init__.py", '__version__ = "0.5.0"\n')
    write(dev, "CHANGELOG.md", "# Nhật ký\n\n## 0.5.0 — 2026-11-01\n- Ảnh đại diện 3D\n")
    write(dev, "requirements.txt", "numpy\n")
    write(dev, "data/voices/.gitkeep", "")
    commit_all(dev, "v0.5.0")
    sh(dev, "push", "-q", "origin", "HEAD:main")
    machine = tmp_path / "may-a"
    sh(tmp_path, "clone", "-q", str(remote), str(machine))
    sh(machine, "config", "user.email", "a@a"); sh(machine, "config", "user.name", "a")
    up = Updater(root=machine, state_file=tmp_path / "state-a.json")
    return {"tmp": tmp_path, "remote": remote, "dev": dev, "machine": machine, "up": up}


def release(dev, version, note, extra=None):
    write(dev, "voxviet/__init__.py", f'__version__ = "{version}"\n')
    cl = (dev / "CHANGELOG.md").read_text(encoding="utf-8")
    write(dev, "CHANGELOG.md", cl.replace("# Nhật ký\n\n", f"# Nhật ký\n\n## {version} — 2026-11-02\n- {note}\n\n"))
    for rel, text in (extra or {}).items():
        write(dev, rel, text)
    commit_all(dev, f"v{version}")
    sh(dev, "push", "-q", "origin", "HEAD:main")


def test_parse_helpers():
    assert parse_version("0.10.2") > parse_version("0.9.9")
    cl = parse_changelog("# x\n\n## 0.6.0 — 2026-11-02\n- Cập nhật trong app\n- Đồng bộ\n\n## 0.5.0\n- A\n")
    assert cl[0] == {"version": "0.6.0", "date": "2026-11-02", "items": ["Cập nhật trong app", "Đồng bộ"]}
    assert cl[1]["version"] == "0.5.0"


def test_check_and_apply_update(world):
    up = world["up"]
    assert up.check()["available"] is False
    release(world["dev"], "0.6.0", "Module cập nhật")
    info = up.check()
    assert info["available"] and info["latest"] == "0.6.0" and info["current"] == "0.5.0"
    assert [n["version"] for n in info["notes"]] == ["0.6.0"] and not info["needs_deps"]
    logs = []
    res = up.apply(log=logs.append, self_test=lambda: None)
    assert res == {"from": "0.5.0", "to": "0.6.0"} and up.local_version() == "0.6.0"
    assert up.history()[0]["ok"]
    assert up.status()["last_result"]["available"] is False  # không báo "có bản mới" sai sau khi cập nhật
    assert up.check()["available"] is False
    # quay lại phiên bản trước
    assert up.rollback()["to"] == "0.5.0" and up.local_version() == "0.5.0"
    assert up.status()["last_check"] is None and up.check()["available"] is True


def test_broken_update_rolls_back_automatically(world):
    up = world["up"]
    release(world["dev"], "0.6.1", "Bản lỗi")
    def bad_test():
        raise RuntimeError("SyntaxError giả lập")
    with pytest.raises(UpdateError, match="tự quay lại 0.5.0"):
        up.apply(self_test=bad_test)
    assert up.local_version() == "0.5.0" and up.history()[0]["ok"] is False


def test_deps_installed_when_requirements_change(world):
    up = world["up"]
    release(world["dev"], "0.6.0", "Thêm thư viện", {"requirements.txt": "numpy\nwebsockets\n"})
    assert up.check()["needs_deps"]
    called = []
    up.apply(install_deps=lambda log: called.append(True), self_test=lambda: None)
    assert called == [True]


def test_local_user_data_survives_update(world):
    up, m = world["up"], world["machine"]
    write(m, "data/voices/giong-cua-toi/voice.json", '{"name": "Giọng của tôi"}')  # chưa commit
    release(world["dev"], "0.6.0", "x")
    up.apply(self_test=lambda: None)
    assert (m / "data/voices/giong-cua-toi/voice.json").exists()


def test_sync_data_between_two_machines(world):
    up_a, m_a = world["up"], world["machine"]
    m_b = world["tmp"] / "may-b"
    sh(world["tmp"], "clone", "-q", str(world["remote"]), str(m_b))
    sh(m_b, "config", "user.email", "b@b"); sh(m_b, "config", "user.name", "b")
    up_b = Updater(root=m_b, state_file=world["tmp"] / "state-b.json")
    write(m_a, "data/voices/giong-a/voice.json", "{}")
    assert up_a.sync_data()["committed"] == 1
    info_b = up_b.check()
    assert info_b["data_only"] and not info_b["available"]  # dữ liệu mới không phải bản cập nhật phần mềm
    assert up_b.sync_data()["pulled"] == 1 and (m_b / "data/voices/giong-a/voice.json").exists()


def test_sync_refuses_when_software_update_pending(world):
    release(world["dev"], "0.6.0", "x")
    with pytest.raises(UpdateError, match="Cập nhật ngay"):
        world["up"].sync_data()


def test_update_api_flow(world, tmp_path):
    import time as _t

    from fastapi.testclient import TestClient

    from voxviet.pipeline import Studio
    from voxviet.server import create_app
    from voxviet.voices import VoiceLibrary

    class NoSelfTest(Updater):
        def self_test(self):
            return None

    restarted = []
    up = NoSelfTest(root=world["machine"], state_file=tmp_path / "st.json")
    client = TestClient(create_app(Studio(library=VoiceLibrary(tmp_path / "v")), updater=up,
                                   restart=lambda: restarted.append(1)))
    H = {"X-VoxViet": "1"}
    assert client.get("/api/update/status").json()["repo"] is True
    release(world["dev"], "0.6.0", "Có gì mới")
    info = client.post("/api/update/check", headers=H).json()
    assert info["available"] and info["notes"][0]["items"] == ["Có gì mới"]
    assert client.get("/api/state").json()["update"] == {"available": True, "latest": "0.6.0"}
    jid = client.post("/api/jobs/update", headers=H).json()["job"]
    for _ in range(200):
        j = client.get(f"/api/jobs/{jid}").json()
        if j["status"] in ("done", "error"):
            break
        _t.sleep(0.05)
    assert j["status"] == "done", j
    assert j["result"]["to"] == "0.6.0" and restarted == [1] and any("0.6.0" in ln for ln in j["log"])
