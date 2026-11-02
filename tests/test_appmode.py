"""Chế độ ứng dụng: đóng cửa sổ là tắt, chỉ một phiên, nhật ký ra file."""

import socket
import threading
import time

import pytest
import uvicorn
from websockets.sync.client import connect

from voxviet import appmode
from voxviet.pipeline import Studio
from voxviet.server import create_app
from voxviet.voices import VoiceLibrary

TOKEN = "t" * 40


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def live_server(tmp_path):
    started = []

    def start(**kw):
        port = _free_port()
        app = create_app(Studio(library=VoiceLibrary(tmp_path / "v")), auth_token=TOKEN, **kw)
        srv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
        th = threading.Thread(target=srv.run, daemon=True)
        th.start()
        for _ in range(100):
            if srv.started:
                break
            time.sleep(0.05)
        started.append((srv, th))
        return port, app

    yield start
    for srv, th in started:
        srv.should_exit = True
        th.join(timeout=5)


def _presence(port, token=TOKEN):
    return connect(f"ws://127.0.0.1:{port}/api/presence", origin=f"http://127.0.0.1:{port}",
                   additional_headers={"Cookie": f"vv_session={token}"})


def test_close_window_exits(live_server):
    exited = threading.Event()
    port, app = live_server(idle_exit=exited.set, idle_grace=1.0, startup_grace=30.0)
    with _presence(port):
        time.sleep(0.5)
        assert app.state.presence["count"] == 1
        time.sleep(1.5)
        assert not exited.is_set()      # cửa sổ còn mở → chưa tắt
    assert exited.wait(5)                # đóng cửa sổ → tắt sau thời gian chờ


def test_reload_does_not_exit(live_server):
    exited = threading.Event()
    port, _ = live_server(idle_exit=exited.set, idle_grace=2.0, startup_grace=30.0)
    with _presence(port):
        pass
    time.sleep(0.5)
    with _presence(port):                # tải lại trang: nối lại ngay
        time.sleep(2.5)
        assert not exited.is_set()


def test_startup_grace_when_never_opened(live_server):
    exited = threading.Event()
    live_server(idle_exit=exited.set, idle_grace=0.5, startup_grace=1.5)
    time.sleep(1.0)
    assert not exited.is_set()           # cửa sổ đang mở chậm → chưa tắt
    assert exited.wait(3)                # không cửa sổ nào kết nối → tắt


def test_presence_requires_token(live_server):
    port, app = live_server()
    with pytest.raises(Exception):
        with _presence(port, token="sai") as ws:
            ws.recv(timeout=2)
    assert app.state.presence["count"] == 0


def test_single_instance_detection(live_server):
    port, _ = live_server()
    assert appmode.is_voxviet(port, TOKEN)
    assert not appmode.is_voxviet(port, "khoa-khac")
    appmode.remember_port(port)
    assert appmode.running_port(TOKEN) == port
    assert appmode.choose_port(port) != port  # cổng đang bận → chọn cổng khác


def test_setup_logging_to_file(monkeypatch):
    import logging
    import sys
    root = logging.getLogger()
    saved = root.handlers[:]
    monkeypatch.setattr(sys, "stdout", None)
    monkeypatch.setattr(sys, "stderr", None)
    appmode.setup_logging(to_file=False)   # pythonw: không có stdout → tự ghi ra file
    try:
        print("xin chào nhật ký")
        assert "xin chào nhật ký" in appmode.log_file().read_text(encoding="utf-8")
    finally:
        stream = sys.stdout
        root.handlers[:] = saved
        stream.close()
