import sys
import time

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from voxviet import audio, catalog
from voxviet.pipeline import Studio
from voxviet.server import create_app
from voxviet.voices import VoiceLibrary

H = {"X-VoxViet": "1"}


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(Studio(library=VoiceLibrary(tmp_path / "voices"))))


def _wait(client, jid, timeout=30):
    t = time.time()
    while time.time() - t < timeout:
        j = client.get(f"/api/jobs/{jid}").json()
        if j["status"] in ("done", "error"):
            return j
        time.sleep(0.05)
    raise TimeoutError(jid)


def test_guard_blocks_writes_without_header(client):
    assert client.post("/api/library", json={"name": "x"}).status_code == 403
    assert client.post("/api/library", json={"name": "Giọng A"}, headers=H).status_code == 200


def test_state_has_no_upstream_branding(client):
    st = client.get("/api/state").json()
    blob = str(st).lower()
    assert "vieneu" not in blob
    assert st["default_preset"] == f"preset:{catalog.default_id()}"
    voices = client.get("/api/voices?language=vi&engine=core").json()["voices"]
    names = {v["label"] for v in voices}
    assert {"Hạ Long", "Sài Gòn", "Hội An"} <= names
    assert all("vieneu" not in str(v).lower() for v in voices)


def test_catalog_maps_to_base_and_accepts_old_names():
    pv = catalog.get("ha-long")
    assert pv and pv.name == "Hạ Long" and pv.region == "bac"
    assert catalog.get(pv.base).id == "ha-long"  # mã cũ trong cài đặt cũ vẫn chạy


def test_tts_job_and_files(client):
    jid = client.post("/api/jobs/tts", json={"text": "Xin chào. Gửi email cho CEO nhé.", "voice": "preset:high",
                                             "engine": "mock"}, headers=H).json()["job"]
    j = _wait(client, jid)
    assert j["status"] == "done", j
    res = j["result"]
    assert res["audio_url"].startswith("/files/outputs/") and res["subtitles"]
    r = client.get(res["audio_url"])
    assert r.status_code == 200 and r.headers["content-type"] == "audio/wav"
    assert client.get("/files/../settings.json").status_code == 404
    jid = client.post("/api/jobs/remaster", json={"enhance": "goc", "dereverb": "tat"}, headers=H).json()["job"]
    assert _wait(client, jid)["status"] == "done"


def test_normalize_and_dialogue_parse(client):
    out = client.post("/api/normalize", json={"text": "Giá 105 nghìn. [nghỉ 1s] Hết.", "dialect": "nam"},
                      headers=H).json()
    assert any(l["kind"] == "pause" for l in out["lines"])
    assert "ngàn" in out["lines"][0]["text"] and "lẻ" in out["lines"][0]["text"]
    p = client.post("/api/dialogue/parse", json={"script": "Minh: Chào.\nLan (vui): Hi!"}, headers=H).json()
    assert p == {"speakers": ["Minh", "Lan"], "lines": 2}


def test_library_clip_upload(client, tmp_path):
    v = client.post("/api/library", json={"name": "Tôi", "dialect": "nam"}, headers=H).json()
    wav = tmp_path / "c.wav"
    t = np.arange(audio.SR * 5) / audio.SR
    sf.write(str(wav), (0.3 * np.sin(2 * np.pi * 200 * t)).astype(np.float32), audio.SR)
    with open(wav, "rb") as f:
        r = client.post(f"/api/library/{v['id']}/clips", files={"file": ("c.wav", f, "audio/wav")},
                        data={"emotion": "vui"}, headers=H)
    assert r.status_code == 200, r.text
    assert [c["key"] for c in r.json()["voice"]["clips"]] == ["vui"]
    assert client.get(f"/api/library/{v['id']}/clips/vui").status_code == 200


def test_live_websocket(client):
    with client.websocket_connect("/api/live") as ws:
        ws.send_json({"text": "Một hai ba.", "voice": "preset:high"})
        total, got_first = 0, False
        while True:
            msg = ws.receive()
            if msg.get("bytes"):
                total += len(msg["bytes"]) // 4
            elif msg.get("text"):
                import json
                d = json.loads(msg["text"])
                got_first |= "first_ms" in d
                if d.get("done") or d.get("error"):
                    assert not d.get("error"), d
                    break
        assert got_first and total > audio.SR // 2


def test_settings_roundtrip_hides_key(client):
    s = client.put("/api/settings", json={"gemini_api_key": "AIza-secret-1234", "enhance": "sang"}, headers=H).json()
    assert s["has_gemini_key"] and "secret" not in str(s) and s["enhance"] == "sang"


def test_live_over_real_uvicorn(tmp_path):
    """TestClient không cần thư viện websockets; máy chủ thật thì cần — kiểm tra đường thật."""
    import json
    import socket
    import threading

    import uvicorn
    from websockets.sync.client import connect

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(Studio(library=VoiceLibrary(tmp_path / "v"))),
                                           host="127.0.0.1", port=port, log_level="error"))
    th = threading.Thread(target=server.run, daemon=True)
    th.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    try:
        with connect(f"ws://127.0.0.1:{port}/api/live", origin=f"http://127.0.0.1:{port}") as ws:
            ws.send(json.dumps({"text": "Một hai.", "voice": "preset:high"}))
            got_audio = False
            while True:
                msg = ws.recv(timeout=20)
                if isinstance(msg, bytes):
                    got_audio = True
                elif json.loads(msg).get("done"):
                    break
            assert got_audio
    finally:
        server.should_exit = True
        th.join(timeout=5)


def _fake_download(monkeypatch, tmp_path, ok: bool):
    """Thay tools/download_models.py bằng script giả: ghi file vào thư mục mô hình tạm."""
    from voxviet import bootstrap, server
    models = tmp_path / "models"
    monkeypatch.setattr(bootstrap, "MODELS", models)
    monkeypatch.setattr(bootstrap, "READY_MARK", models / ".models_ready")
    script = tmp_path / "fake_dl.py"
    script.write_text(
        "import sys, pathlib, time\n"
        f"m = pathlib.Path({str(models)!r}); (m / 'voxviet-core').mkdir(parents=True, exist_ok=True)\n"
        "(m / 'voxviet-core' / 'w.bin').write_bytes(b'0' * 3_000_000)\n"
        "print('Đang tải lõi giọng…'); time.sleep(2)\n"
        + ("(m / '.models_ready').write_text('ok')\nprint('Hoàn tất')\n" if ok else "sys.exit(1)\n"),
        encoding="utf-8")
    monkeypatch.setattr(server, "download_cmd", lambda: [sys.executable, str(script)])


def test_download_models_job(tmp_path, monkeypatch):
    _fake_download(monkeypatch, tmp_path, ok=True)
    restarted = []
    c = TestClient(create_app(Studio(library=VoiceLibrary(tmp_path / "v")), restart=lambda: restarted.append(1)))
    assert c.get("/api/state").json()["models_ready"] is False
    jid = c.post("/api/jobs/download-models", headers=H).json()["job"]
    seen_size = False
    t = time.time()
    while time.time() - t < 30:
        j = c.get(f"/api/jobs/{jid}").json()
        seen_size |= "MB" in (j["message"] or "")
        if j["status"] in ("done", "error"):
            break
        time.sleep(0.2)
    assert j["status"] == "done", j
    assert j["result"]["restarting"] and restarted == [1]
    assert seen_size and "Hoàn tất" in "\n".join(j["log"])
    assert c.get("/api/state").json()["models_ready"] is True


def test_download_models_failure(tmp_path, monkeypatch):
    _fake_download(monkeypatch, tmp_path, ok=False)
    restarted = []
    c = TestClient(create_app(Studio(library=VoiceLibrary(tmp_path / "v")), restart=lambda: restarted.append(1)))
    j = _wait(c, c.post("/api/jobs/download-models", headers=H).json()["job"])
    assert j["status"] == "error" and "Thử lại" in j["error"] and not restarted
