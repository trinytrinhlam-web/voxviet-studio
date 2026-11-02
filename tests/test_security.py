"""Kiểm thử bảo mật: mỗi kiểu tấn công đã thử khi rà soát phải bị chặn."""

import json
import os
import pickle
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import voxviet.server as server
from voxviet.pipeline import Studio
from voxviet.server import create_app
from voxviet.voices import VoiceLibrary

H = {"X-VoxViet": "1"}
TOKEN = "k" * 43


@pytest.fixture
def lib(tmp_path):
    return VoiceLibrary(tmp_path / "voices")


@pytest.fixture
def client(lib):
    return TestClient(create_app(Studio(library=lib)))


def test_dns_rebinding_blocked(client):
    evil = {"Host": "evil.example:7860", "Origin": "http://evil.example:7860"}
    assert client.get("/api/settings", headers=evil).status_code == 403
    assert client.post("/api/library", json={"name": "x"}, headers={**H, **evil}).status_code == 403
    assert client.get("/", headers=evil).status_code == 403


def test_csrf_header_required(client):
    assert client.post("/api/library", json={"name": "x"}).status_code == 403


def test_security_headers(client):
    r = client.get("/api/state")
    csp = r.headers["content-security-policy"]
    assert "script-src 'self'" in csp and "connect-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert r.headers["x-frame-options"] == "DENY" and r.headers["x-content-type-options"] == "nosniff"


def test_session_token_required(lib):
    c = TestClient(create_app(Studio(library=lib), auth_token=TOKEN))
    assert c.get("/api/state").status_code == 401
    assert c.get("/files/outputs/x.wav").status_code == 401
    assert c.get("/?t=sai", follow_redirects=False).status_code == 403
    r = c.get(f"/?t={TOKEN}", follow_redirects=False)
    assert r.status_code == 303 and "httponly" in r.headers["set-cookie"].lower() \
        and "samesite=strict" in r.headers["set-cookie"].lower()
    assert c.get("/api/state").status_code == 200  # cookie đã được ghi
    with pytest.raises(WebSocketDisconnect):  # WebSocket không có cookie → bị đóng
        with TestClient(create_app(Studio(library=lib), auth_token=TOKEN)).websocket_connect("/api/live") as ws:
            ws.receive_text()


def test_websocket_foreign_origin_rejected(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/live", headers={"Origin": "http://evil.example"}) as ws:
            ws.receive_text()


@pytest.mark.parametrize("item", ["..\\..\\..\\bimat", "%2e%2e", "vi001.flac", "x" * 300])
def test_recording_item_must_be_in_script(client, item):
    assert client.get(f"/api/recording/a/takes/{item}").status_code == 404
    assert client.delete(f"/api/recording/a/takes/{item}", headers=H).status_code == 404


def test_tampered_voice_json_is_neutralised(client, lib, tmp_path):
    secret = tmp_path / "bimat.wav"
    secret.write_bytes(b"RIFF-bimat")
    d = lib.root / "giong-la"
    (d / "clips").mkdir(parents=True)
    (d / "voice.json").write_text(json.dumps({
        "id": '"><img src=x onerror=alert(1)>', "name": "<script>alert(1)</script>",
        "clips": {"trung_tinh": "../../../bimat.wav", "vui": "/etc/passwd"}, "avatar": "../../x",
    }), encoding="utf-8")
    weird = lib.root / "Thu Muc Khong Hop Le"
    weird.mkdir()
    (weird / "voice.json").write_text("{}", encoding="utf-8")
    voices = client.get("/api/library").json()["voices"]
    assert [v["id"] for v in voices] == ["giong-la"]  # id = tên thư mục, thư mục lạ bị bỏ qua
    assert voices[0]["avatar"] is None
    assert lib.get("giong-la").clip_path("trung_tinh") is None
    assert client.get("/api/library/giong-la/clips/trung_tinh").status_code == 404
    client.delete("/api/library/giong-la/clips/trung_tinh", headers=H)
    assert secret.exists()  # không xoá được file ngoài thư mục giọng


def test_upload_size_limit(client, monkeypatch):
    monkeypatch.setattr(server, "MAX_BODY", 1000)
    r = client.post("/api/text-file", files={"file": ("a.txt", b"a" * 5000)}, headers=H)
    assert r.status_code == 413


def test_invalid_gemini_model_rejected(monkeypatch):
    from voxviet import settings
    from voxviet.engines.google_engines import GeminiEngine
    monkeypatch.setattr(settings, "_cached", settings.Settings(gemini_api_key="k", gemini_model="../../x?a=b"))
    with pytest.raises(RuntimeError, match="không hợp lệ"):
        GeminiEngine()._model()


def test_finetune_run_name_cannot_escape(client, monkeypatch):
    from voxviet import finetune
    seen = []
    monkeypatch.setattr(finetune, "train", lambda ds, run, *a, **k: seen.append(run) or iter(()))
    client.post("/api/jobs/finetune", json={"run": "../../../Windows/System32"}, headers=H)
    import time
    for _ in range(100):
        if seen:
            break
        time.sleep(0.02)
    assert seen and "/" not in seen[0] and "\\" not in seen[0] and ".." not in seen[0]


def test_security_scanner_detects_planted_payloads(tmp_path):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import kiem_tra_bao_mat as K
    K.problems.clear()
    K.notes.clear()
    repo = tmp_path / "models" / "repo"
    repo.mkdir(parents=True)

    class Evil:
        def __reduce__(self):
            return (os.system, ("echo pwned",))
    (repo / "pytorch_model.bin").write_bytes(pickle.dumps(Evil(), protocol=4))  # chỉ ghi, KHÔNG nạp
    (repo / "modeling.py").write_text("import subprocess\nsubprocess.run(['calc'])\n")
    K.MODELS, K.ROOT, K.STATE = tmp_path / "models", tmp_path, tmp_path / "state.json"
    K.compare_hashes(K.scan_models())
    text = "\n".join(K.problems)
    assert "subprocess" in text and "system" in text
    # lần quét sau: file mã bị sửa → cảnh báo thay đổi
    K.problems.clear()
    (repo / "modeling.py").write_text("print('khác')\n")
    K.compare_hashes(K.scan_models())
    assert any("THAY ĐỔI" in p for p in K.problems)
