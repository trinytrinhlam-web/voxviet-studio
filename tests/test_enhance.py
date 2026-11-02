import numpy as np
import pytest
import soundfile as sf

from voxviet.audio import enhance as E
from voxviet.pipeline import Studio
from voxviet.voices import VoiceLibrary

SR = 48_000


def _gain_db(preset, f):
    t = np.arange(SR) / SR
    x = 0.1 * np.sin(2 * np.pi * f * t)
    y = E.Enhancer(preset, SR)(x)[SR // 2:]
    return 20 * np.log10(np.sqrt(np.mean(y ** 2)) / np.sqrt(np.mean(x[SR // 2:] ** 2)))


@pytest.mark.parametrize("preset", ["nhe", "trong", "sang"])
def test_presets_cut_mud_and_boost_clarity(preset):
    mud, presence, air = _gain_db(preset, 300), _gain_db(preset, 3500), _gain_db(preset, 12000)
    rumble = _gain_db(preset, 50)
    assert presence - mud > 3.0  # dải rõ chữ được nâng so với dải gây đục
    assert air - mud > 3.0
    assert rumble < mud - 5  # tiếng ù được cắt


def test_off_is_identity():
    x = np.random.default_rng(1).normal(0, 0.1, SR).astype(np.float32)
    assert np.allclose(E.process(x, "goc"), x)


def test_streaming_equals_batch():
    x = np.random.default_rng(0).normal(0, 0.1, SR * 2)
    a = E.Enhancer("trong")(x)
    e = E.Enhancer("trong")
    b = np.concatenate([e(x[i:i + 777]) for i in range(0, len(x), 777)])
    assert np.allclose(a, b, atol=1e-6)


def test_soft_clip_bounds_and_transparent_below_threshold():
    x = np.linspace(-3, 3, 1001)
    y = E.soft_clip(x)
    assert np.max(np.abs(y)) <= 1.0
    small = np.linspace(-0.8, 0.8, 11)
    assert np.allclose(E.soft_clip(small), small)


def test_remaster_last_take(tmp_path):
    st = Studio(library=VoiceLibrary(tmp_path / "v"))
    r = st.synthesize("Một hai ba. Bốn năm sáu.", "vi", "preset:high", engine_id="mock", enhance="trong")
    raw, spans, final = st.last_take
    assert raw.exists() and final == r.path and spans == [(c.start, c.end) for c in r.subtitles]
    p = st.remaster("goc")
    a, _ = sf.read(str(p))
    b, _ = sf.read(str(r.path))
    assert len(a) == len(b)  # cùng độ dài, chỉ khác hậu kỳ
    assert not np.allclose(a, b)


def _reverberant(seed=0):
    rng = np.random.default_rng(seed)
    dry = np.zeros(SR * 3)
    gaps = np.ones(len(dry), bool)
    for k in range(7):
        s, n = int((0.1 + k * 0.4) * SR), int(0.15 * SR)
        dry[s:s + n] = rng.normal(0, 0.2, n) * np.hanning(n)
        gaps[s:s + int(0.2 * SR)] = False
    t = np.arange(int(0.8 * SR)) / SR
    ir = rng.normal(0, 1, len(t)) * np.exp(-6.9 * t / 0.5)
    ir *= 0.25 / np.sqrt(np.sum(ir ** 2))
    ir[0] = 1.0
    return np.convolve(dry, ir)[:len(dry)], gaps


def test_dereverb_reduces_tail_keeps_speech():
    wet, gaps = _reverberant()

    def db(x, m):
        return 10 * np.log10(np.mean(x[m] ** 2) + 1e-15)

    prev_tail = 0.0
    for lv in ("nhe", "vua", "manh"):
        y = E.dereverb(wet, lv, SR)
        assert len(y) == len(wet)
        tail = db(y, gaps) - db(wet, gaps)
        speech = db(y, ~gaps) - db(wet, ~gaps)
        assert tail < prev_tail - 2.0  # mức sau khử mạnh hơn mức trước
        assert speech > -1.5  # lời nói gần như nguyên vẹn
        prev_tail = tail
    assert np.allclose(E.dereverb(wet, "tat", SR), wet.astype(np.float32))


def test_remaster_with_dereverb(tmp_path):
    st = Studio(library=VoiceLibrary(tmp_path / "v"))
    r = st.synthesize("Một hai ba bốn năm.", "vi", "preset:high", engine_id="mock", dereverb="manh")
    p = st.remaster("trong", "nhe", False)
    assert "vang_nhe" in p.name and sf.info(str(p)).frames == sf.info(str(r.path)).frames
