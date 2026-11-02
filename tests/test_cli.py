"""tools/voxviet_cli.py: công cụ dòng lệnh để AI/người gửi văn bản vào phần mềm đang chạy."""

import importlib.util
import json
import os
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn

from voxviet import paths
from voxviet.pipeline import Studio
from voxviet.server import create_app
from voxviet.voices import VoiceLibrary

TOKEN = "c" * 40
_spec = importlib.util.spec_from_file_location("voxviet_cli", Path(__file__).parent.parent / "tools" / "voxviet_cli.py")
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


@pytest.fixture(scope="module")
def running(tmp_path_factory):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    lib = tmp_path_factory.mktemp("v")
    srv = uvicorn.Server(uvicorn.Config(create_app(Studio(library=VoiceLibrary(lib)), auth_token=TOKEN),
                                        host="127.0.0.1", port=port, log_level="error"))
    th = threading.Thread(target=srv.run, daemon=True)
    th.start()
    for _ in range(100):
        if srv.started:
            break
        time.sleep(0.05)
    local = paths.DATA / ".local"
    local.mkdir(parents=True, exist_ok=True)
    (local / "session_token").write_text(TOKEN, encoding="utf-8")
    (local / "instance.json").write_text(json.dumps({"port": port}), encoding="utf-8")
    yield port
    srv.should_exit = True
    th.join(timeout=5)


def _run(capsys, *args):
    code = cli.main(["--no-start", *args])
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    return code, out


def test_voices(running, capsys):
    code, out = _run(capsys, "voices")
    assert code == 0 and any(v["value"] == "preset:ha-long" for v in out["voices"])


def test_doc_from_text(running, capsys):
    code, out = _run(capsys, "doc", "--voice", "preset:sai-gon", "--text", "Xin chào [vui] các bạn! [nghỉ 0.5s] Hẹn gặp lại.")
    assert code == 0, out
    assert out["audio"] and os.path.exists(out["audio"]) and out["srt"] and out["duration_s"] > 0


def test_dialogue_with_cast(running, capsys, tmp_path):
    script = tmp_path / "kb.txt"
    script.write_text("Người kể: Chiều hôm ấy trời mưa.\nMinh (vui): Lan ơi!\nLan: Ủa, Minh hả?\n", encoding="utf-8")
    cast = tmp_path / "cast.json"
    cast.write_text(json.dumps({"Người kể": {"voice": "preset:hoang-lien"}, "Minh": {"voice": "preset:ha-long"},
                                "Lan": {"voice": "preset:ho-tay", "emotion": "ngac_nhien"}}), encoding="utf-8")
    code, out = _run(capsys, "dialogue", "--file", str(script), "--cast", str(cast))
    assert code == 0, out
    assert out["speakers"] == ["Người kể", "Minh", "Lan"] and os.path.exists(out["audio"])


def test_dub_and_check(running, capsys):
    srt = "1\n00:00:00,000 --> 00:00:02,000\nXin chào.\n\n2\n00:00:02,500 --> 00:00:04,000\nTạm biệt.\n"
    code, out = _run(capsys, "dub", "--voice", "preset:ho-tay", "--text", srt)
    assert code == 0 and os.path.exists(out["audio"])
    code, out = _run(capsys, "check", "--text", "Giá 1.250.000đ, gửi email cho CEO.")
    assert code == 0 and out["lines"] and out["lines"][0]["kind"] == "text"


def test_errors_are_json(running, capsys):
    code, out = _run(capsys, "doc", "--text", "   ")
    assert code == 1 and out["ok"] is False and "văn bản" in out["error"]
