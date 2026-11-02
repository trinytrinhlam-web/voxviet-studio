import pytest

from voxviet.text import dialogue, emotions, srt
from voxviet.text import normalize as N
from voxviet.text.en_numbers import cardinal, expand_numbers, ordinal, year
from voxviet.text.lexicon import Lexicon


def test_parse_inline_tags():
    segs = N.parse_inline("Chào. [vui] Vui quá! [nghỉ 1.5s] [cười] Ha ha. [nghỉ 300ms] [buồn] Thôi.")
    kinds = [(s.kind, s.emotion) for s in segs]
    assert kinds == [("text", "trung_tinh"), ("text", "vui"), ("pause", "vui"), ("text", "vui"),
                     ("pause", "vui"), ("text", "buon")]
    assert segs[2].seconds == pytest.approx(1.5)
    assert segs[4].seconds == pytest.approx(0.3)
    assert "[cười]" in segs[3].text  # thẻ phi ngôn ngữ giữ nguyên cho VieNeu


def test_unknown_bracket_kept():
    segs = N.parse_inline("Xem mục [A] nhé")
    assert segs[0].text == "Xem mục [A] nhé"


@pytest.mark.parametrize("dialect,expect,absent", [
    ("bac", ["nghìn", "trăm linh"], ["ngàn", "trăm lẻ"]),
    ("nam", ["ngàn", "trăm lẻ"], ["nghìn", "trăm linh"]),
])
def test_dialect_numbers(dialect, expect, absent):
    pytest.importorskip("sea_g2p")
    out = N.prepare_vi("Có 105 người và 2.000 cây.", dialect)
    for e in expect:
        assert e in out
    for a in absent:
        assert a not in out


def test_vi_keeps_english_words():
    pytest.importorskip("sea_g2p")
    out = N.prepare_vi("Gửi email cho CEO lúc 10h30.", "bac")
    assert "email" in out and "mười giờ ba mươi" in out


def test_vi_nonverbal_tag_survives_normalization():
    pytest.importorskip("sea_g2p")
    assert "[cười]" in N.prepare_vi("[cười] Trời ơi!", "bac")


def test_english_numbers():
    assert cardinal(0) == "zero"
    assert cardinal(1250) == "one thousand two hundred fifty"
    assert cardinal(21) == "twenty-one"
    assert ordinal(21) == "twenty-first"
    assert ordinal(12) == "twelfth"
    assert year(1999) == "nineteen ninety-nine"
    assert year(2007) == "two thousand seven"
    assert year(1905) == "nineteen oh five"
    out = expand_numbers("I paid $3.50 at 10:05 am, 15% off, room 007, pi 3.14")
    assert "three dollars and fifty cents" in out
    assert "ten oh five a m" in out
    assert "fifteen percent" in out
    assert "zero zero seven" in out
    assert "three point one four" in out


def test_prepare_en_no_vietnamese_numbers():
    out = N.prepare_en("I have 3 cats & 2 dogs")
    assert out == "I have three cats and two dogs"


def test_lexicon(tmp_path):
    lex = Lexicon.load(default=tmp_path / "none.json", user=tmp_path / "none2.json")
    lex.set_entries([("all", "VoxViet", "vốc việt"), ("vi", "ai", "trí tuệ nhân tạo"), ("en", "SQL", "sequel")])
    assert lex.apply("Dùng VoxViet và ai", "vi") == "Dùng vốc việt và trí tuệ nhân tạo"
    assert lex.apply("Ai đó", "vi") == "trí tuệ nhân tạo đó"  # khoá thường → không phân biệt hoa
    assert lex.apply("trainer", "vi") == "trainer"  # chỉ khớp nguyên từ
    assert lex.apply("SQL and sql", "en") == "sequel and sql"  # khoá HOA → phân biệt hoa
    lex.save_user(tmp_path / "u.json")
    assert Lexicon.load(default=tmp_path / "x", user=tmp_path / "u.json").entries["en"]["SQL"] == "sequel"


def test_split_chunks_keeps_abbreviations_and_limits():
    chunks = N.split_chunks("Ông Dr. Smith tới TP. Hồ Chí Minh. Xin chào!\n\nĐoạn hai.", max_chars=200)
    assert chunks[0].text == "Ông Dr. Smith tới TP. Hồ Chí Minh. Xin chào!"
    assert chunks[0].pause_after == "paragraph"
    assert chunks[-1].pause_after == "none"
    long = N.split_chunks("từ " * 300, max_chars=100)
    assert all(len(c.text) <= 100 for c in long)
    one_per_sentence = N.split_chunks("Một. Hai. Ba.", group=False)
    assert [c.text for c in one_per_sentence] == ["Một.", "Hai.", "Ba."]


def test_dialogue_parse():
    lines = dialogue.parse("Người kể: Chiều mưa.\nMinh (vui): Lan ơi!\n[Lan] (ngạc nhiên): Ủa?\n"
                           "Tiếp lời Lan.\nLúc 10:30 trời tạnh.\n# ghi chú")
    assert [(l.speaker, l.emotion) for l in lines] == [
        ("Người kể", None), ("Minh", "vui"), ("Lan", "ngac_nhien"), ("Lan", None), ("Lan", None)]
    assert lines[-1].text == "Lúc 10:30 trời tạnh."
    assert dialogue.speakers(lines) == ["Người kể", "Minh", "Lan"]


def test_srt_roundtrip():
    cues = srt.parse("1\n00:00:01,000 --> 00:00:03,500\nXin <i>chào</i>\n\n2\n00:01:04.2 --> 00:01:06,000\nA\nB\n")
    assert [(c.start, c.end, c.text) for c in cues] == [(1.0, 3.5, "Xin chào"), (64.2, 66.0, "A B")]
    again = srt.parse(srt.write(cues))
    assert [(c.start, c.end, c.text) for c in again] == [(c.start, c.end, c.text) for c in cues]


def test_emotion_aliases():
    assert emotions.resolve("Vui vẻ") == "vui"
    assert emotions.resolve("thi tham") == "thi_tham"
    assert emotions.resolve("whisper") == "thi_tham"
    assert emotions.resolve("??") is None
    assert emotions.get(None).key == "trung_tinh"
