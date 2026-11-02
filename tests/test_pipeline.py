import numpy as np
import pytest
import soundfile as sf

from voxviet import audio, recording
from voxviet.pipeline import Studio
from voxviet.voices import MAX_VOICES, VoiceLibrary


@pytest.fixture
def studio(tmp_path):
    return Studio(library=VoiceLibrary(tmp_path / "voices"))


@pytest.fixture
def ref_wav(tmp_path):
    t = np.arange(int(6 * audio.SR)) / audio.SR
    p = tmp_path / "ref.wav"
    sf.write(str(p), (0.3 * np.sin(2 * np.pi * 180 * t)).astype(np.float32), audio.SR)
    return p


def test_audio_ops():
    x = np.concatenate([audio.silence(0.5), 0.5 * np.ones(audio.SR, np.float32), audio.silence(0.5)])
    assert audio.duration(audio.trim(x)) == pytest.approx(1.08, abs=0.03)
    assert audio.resample(np.ones(48000, np.float32), 48000, 24000).shape[0] == 24000
    assert float(np.max(np.abs(audio.peak_limit(2 * np.ones(10, np.float32))))) <= 0.971


def test_time_stretch_changes_duration():
    if not audio.ffmpeg_exe():
        pytest.skip("không có ffmpeg")
    t = np.arange(audio.SR * 2) / audio.SR
    x = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    assert audio.duration(audio.time_stretch(x, 1.25)) == pytest.approx(1.6, abs=0.05)


def test_voice_library_limits(studio, ref_wav):
    lib = studio.library
    v = lib.create("Giọng của tôi", "nam")
    assert v.id == "giong-cua-toi"
    with pytest.raises(ValueError):
        lib.create("giọng của tôi")  # trùng tên
    _p, warns = lib.add_clip(v.id, ref_wav, "vui")
    assert warns == []
    lib.add_clip(v.id, ref_wav, "trung_tinh")
    lib.add_clip(v.id, ref_wav, "trung_tinh", english=True)
    v = lib.get(v.id)
    assert v.ref_for("vui").name == "vui.wav"
    assert v.ref_for("buon").name == "trung_tinh.wav"  # thiếu → dùng trung tính
    assert v.ref_for("buon", "en").name == "en_trung_tinh.wav"
    for i in range(MAX_VOICES - 1):
        lib.create(f"Giọng {i}")
    with pytest.raises(ValueError):
        lib.create("Thứ mười một")


def test_synthesize_writes_audio_and_srt(studio, ref_wav):
    v = studio.library.create("Tôi", "bac")
    studio.library.add_clip(v.id, ref_wav)
    r = studio.synthesize("Xin chào! [vui] Hôm nay vui quá. [nghỉ 1s] Gửi email nhé.\n\nĐoạn hai.", "vi",
                          f"voice:{v.id}", speed=1.0, engine_id="mock")
    assert r.path.exists() and r.duration > 1.0
    assert len(r.subtitles) == 4 and r.srt_path.exists()
    assert any("mẫu cảm xúc" in w for w in r.warnings)  # chưa có mẫu 'vui'
    # khoảng nghỉ 1s nằm giữa câu 2 và câu 3
    assert r.subtitles[2].start - r.subtitles[1].end >= 1.0


def test_speed_makes_audio_shorter(studio):
    if not audio.ffmpeg_exe():
        pytest.skip("không có ffmpeg")
    text = "Một hai ba bốn năm sáu bảy tám chín mười."
    slow = studio.synthesize(text, "vi", "preset:high", speed=0.8, engine_id="mock", want_srt=False)
    fast = studio.synthesize(text, "vi", "preset:high", speed=1.4, engine_id="mock", want_srt=False)
    assert fast.duration < slow.duration * 0.75


def test_dialogue_and_dub(studio):
    r = studio.dialogue("Minh (vui): Chào Lan!\nLan: Chào Minh, khoẻ không?",
                        {"Minh": {"voice": "preset:high", "engine": "mock"},
                         "Lan": {"voice": "preset:low", "engine": "mock"}})
    assert [c.text.split(":")[0] for c in r.subtitles] == ["Minh", "Lan"]
    d = studio.dub_srt("1\n00:00:02,000 --> 00:00:03,000\nCâu một\n\n2\n00:00:05,000 --> 00:00:06,000\nCâu hai",
                       "vi", "preset:high", engine_id="mock")
    assert d.subtitles[0].start == pytest.approx(2.0, abs=0.01)
    assert d.subtitles[1].start == pytest.approx(5.0, abs=0.01)


def test_stream_yields_audio(studio):
    pieces = list(studio.stream("Một hai. Ba bốn.", "vi", "preset:high", engine_id="mock"))
    assert sum(len(p) for p in pieces) > audio.SR


def test_recording_session_and_build_voice(studio, ref_wav, monkeypatch, tmp_path):
    monkeypatch.setattr(recording.paths, "RECORDINGS", tmp_path / "rec")
    script = recording.load_script()
    assert len(script) > 150 and {it.group for it in script} == {"vi", "mix", "emo", "en"}
    s = recording.Session("Phiên thử")
    vi = next(it for it in script if it.group == "vi")
    happy = next(it for it in script if it.emotion == "vui" and it.group == "emo")
    en = next(it for it in script if it.group == "en")
    for it in (vi, happy, en):
        s.save_take(it, ref_wav)
    meta = (s.dir / "metadata.csv").read_text(encoding="utf-8").splitlines()
    assert meta[0] == f"{vi.id}.flac|{vi.text}" and len(meta) == 3
    vid, notes = s.build_voice(studio.library, "Giọng thu", "nam")
    v = studio.library.get(vid)
    assert set(v.clips) == {"trung_tinh", "vui", "en_trung_tinh"}
