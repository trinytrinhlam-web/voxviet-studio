"""Giao diện VoxViet Studio (Gradio, chạy trên máy, mở trong trình duyệt)."""

from __future__ import annotations

import logging
import traceback
from pathlib import Path

import gradio as gr
import numpy as np

from .. import __version__, audio, engines, finetune, paths, recording
from .. import settings as settings_mod
from ..audio import enhance as enhance_mod
from ..engines.base import EngineUnavailable
from ..engines.google_engines import GEMINI_VOICES
from ..pipeline import Studio
from ..text import dialogue as dialogue_mod
from ..text import emotions
from ..text import normalize as norm
from ..voices import MAX_VOICES

log = logging.getLogger("voxviet.ui")

studio = Studio()
SCRIPT = recording.load_script()
MAX_CAST = 8
LANGS = [("Tiếng Việt", "vi"), ("English", "en")]
DIALECTS = [("Theo giọng đã chọn", "auto"), ("Miền Bắc", "bac"), ("Miền Nam", "nam")]
EMO_CHOICES = emotions.choices()

TAG_HELP = """
**Thẻ điều khiển trong văn bản** (gõ trực tiếp vào văn bản):

| Thẻ | Tác dụng |
|---|---|
| `[vui]` `[buồn]` `[giận]` `[ngạc nhiên]` `[thì thầm]` `[kể chuyện]` `[trung tính]` | Đổi cảm xúc cho phần phía sau |
| `[nghỉ 1.5s]` `[nghỉ 500ms]` `[nghỉ]` | Chèn khoảng lặng |
| `[cười]` `[thở dài]` `[hắng giọng]` | Âm thanh tự nhiên (VieNeu, thử nghiệm) |
| `<en>con</en>` | Ép đọc tiếng Anh khi tự nhận diện bị nhầm |

Từ tiếng Anh xen trong câu tiếng Việt (email, meeting, CEO, AI…) được **tự nhận diện và đọc chuẩn tiếng Anh**.
Từ nào đọc chưa đúng → thêm vào **Từ điển phát âm** ở tab Cài đặt.
"""

DIALOGUE_EXAMPLE = """Người kể: Chiều hôm ấy, trời đổ mưa rất to.
Minh (vui): Lan ơi! Lâu quá không gặp, dạo này bạn thế nào?
Lan (ngạc nhiên): Ủa, Minh hả? Sao bạn lại ở đây?
Minh: Mình vừa về nước tuần trước. Còn có buổi meeting với khách hàng nữa.
Lan: [thì thầm] Nói nhỏ thôi, mọi người đang nhìn kìa."""


# ── tiện ích ─────────────────────────────────────────────────────────────────

def _err(e: Exception) -> str:
    if isinstance(e, (ValueError, EngineUnavailable, RuntimeError)):
        return f"❌ {e}"
    log.error(traceback.format_exc())
    return f"❌ Lỗi: {e}"


def _engine_choices(language: str) -> list[tuple[str, str]]:
    out = [("Tự động (khuyên dùng)", "auto")]
    for e in engines.registry().values():
        if language in e.languages:
            ok, _ = e.available()
            out.append((e.label + ("" if ok else " — chưa sẵn sàng"), e.id))
    return out


def _eng(engine_id: str | None) -> str | None:
    return None if not engine_id or engine_id == "auto" else engine_id


def _voice_choices(language: str, engine_id: str | None = None) -> list[tuple[str, str]]:
    try:
        return studio.voice_options(language, _eng(engine_id))
    except Exception:
        return []


def _voice_update(language: str, engine_id: str | None = None, current: str | None = None):
    ch = _voice_choices(language, engine_id)
    values = [v for _, v in ch]
    value = current if current in values else (values[0] if values else None)
    return gr.update(choices=ch, value=value)


def _dialect(d: str | None) -> str | None:
    return None if not d or d == "auto" else d


def _progress_cb(progress: gr.Progress):
    return lambda frac, desc: progress(frac, desc=desc)


def _read_text_file(f) -> str:
    if not f:
        return ""
    p = Path(f if isinstance(f, str) else f.name)
    if p.suffix.lower() == ".docx":
        try:
            import docx
        except ImportError:
            raise gr.Error("Đọc .docx cần cài python-docx (đã có trong install.bat).")
        return "\n\n".join(par.text for par in docx.Document(str(p)).paragraphs if par.text.strip())
    for enc in ("utf-8-sig", "utf-16", "cp1258", "latin-1"):
        try:
            return p.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return p.read_text(errors="ignore")


def _files(result) -> list[str]:
    files = [str(result.path)]
    if result.srt_path:
        files.append(str(result.srt_path))
    return files


# ── tab 1: đọc văn bản ───────────────────────────────────────────────────────

def do_tts(text, language, engine_id, voice, emotion, speed, pause_scale, dialect, fmt, enhance, temperature,
           progress=gr.Progress()):
    try:
        temp = float(temperature) if temperature and float(temperature) > 0 else None
        r = studio.synthesize(text, language, voice, emotion, float(speed), _eng(engine_id), _dialect(dialect),
                              float(pause_scale), fmt, True, _progress_cb(progress), temperature=temp,
                              enhance=enhance)
        return str(r.path), _files(r), r.summary()
    except Exception as e:
        return None, None, _err(e)


def do_remaster(preset):
    try:
        p = studio.remaster(preset)
        label = dict((k, v) for v, k in enhance_mod.choices()).get(preset, preset)
        return str(p), str(p), f"🎧 Bản vừa đọc, xử lý mức **{label}** (không đọc lại nên so sánh được công bằng)."
    except Exception as e:
        return None, None, _err(e)


def do_preview_norm(text, language, voice, dialect):
    if not (text or "").strip():
        return ""
    d = _dialect(dialect)
    if d is None:
        try:
            d = studio.resolve_voice(voice, emotions.DEFAULT, language, studio.pick_engine(language, check=False)).dialect
        except Exception:
            d = settings_mod.load().dialect
    lines = []
    for seg in norm.parse_inline(text):
        if seg.kind == "pause":
            lines.append(f"⏸ nghỉ {seg.seconds:.2f}s")
            continue
        for ch in norm.split_chunks(seg.text):
            lines.append(f"[{emotions.get(seg.emotion).label}] {norm.prepare(ch.text, language, d, studio.lexicon)}")
    return "\n".join(lines)


# ── tab 2: hội thoại ─────────────────────────────────────────────────────────

def do_parse_cast(script):
    lines = dialogue_mod.parse(script or "")
    names = dialogue_mod.speakers(lines)[:MAX_CAST]
    updates = []
    for i in range(MAX_CAST):
        vis = i < len(names)
        updates.append(gr.update(visible=vis))
        updates.append(gr.update(value=names[i] if vis else ""))
    info = f"Tìm thấy {len(names)} nhân vật, {len(lines)} lượt thoại." if names else "Chưa có lượt thoại nào."
    if len(dialogue_mod.speakers(lines)) > MAX_CAST:
        info += f" (chỉ hiện {MAX_CAST} nhân vật đầu; nhân vật còn lại dùng giọng mặc định)"
    return [*updates, info]


def do_dialogue(script, gap, fmt, *cast_vals, progress=gr.Progress()):
    try:
        cast = {}
        for i in range(MAX_CAST):
            name, voice, lang, emo, speed = cast_vals[i * 5:(i + 1) * 5]
            if name:
                cast[name] = {"voice": voice, "language": lang, "emotion": emo, "speed": speed}
        first = next(iter(cast.values()), {})
        r = studio.dialogue(script, cast, default={"voice": first.get("voice"), "language": "vi"},
                            gap=float(gap), fmt=fmt, progress=_progress_cb(progress))
        return str(r.path), _files(r), r.summary()
    except Exception as e:
        return None, None, _err(e)


# ── tab 3: lồng tiếng ────────────────────────────────────────────────────────

def do_dub(srt_file, srt_text, language, voice, emotion, speed, max_stretch, fmt, progress=gr.Progress()):
    try:
        text = _read_text_file(srt_file) if srt_file else srt_text
        r = studio.dub_srt(text, language, voice, emotion, float(speed), None, float(max_stretch), fmt,
                           _progress_cb(progress))
        return str(r.path), _files(r), r.summary()
    except Exception as e:
        return None, None, _err(e)


# ── tab 4: trực tiếp ─────────────────────────────────────────────────────────

def do_live(text, language, voice, emotion, speed):
    if not (text or "").strip():
        return
    try:
        buf = []
        for piece in studio.stream(text, language, voice, emotion, float(speed)):
            buf.append(piece)
            if sum(len(b) for b in buf) >= audio.SR // 5:  # gửi mỗi ~0.2s âm thanh
                yield (audio.SR, (np.clip(np.concatenate(buf), -1, 1) * 32767).astype(np.int16))
                buf = []
        if buf:
            yield (audio.SR, (np.clip(np.concatenate(buf), -1, 1) * 32767).astype(np.int16))
    except Exception as e:
        raise gr.Error(_err(e))


# ── tab 5: kho giọng ─────────────────────────────────────────────────────────

def _library_table():
    rows = []
    for v in studio.library.list():
        clips = ", ".join(
            (("EN " if k.startswith("en_") else "") + emotions.get(k.removeprefix("en_")).label) for k in v.clips
        ) or "(chưa có mẫu)"
        rows.append([v.name, {"bac": "Bắc", "nam": "Nam", "trung": "Trung"}.get(v.dialect, v.dialect),
                     v.gender, clips, "✔" if v.backbone else ""])
    return rows


def _library_choices():
    return [(v.name, v.id) for v in studio.library.list()]


def _library_refresh(selected=None):
    ch = _library_choices()
    ids = [i for _, i in ch]
    sel = selected if selected in ids else (ids[0] if ids else None)
    return (_library_table(), gr.update(choices=ch, value=sel), f"Kho: {len(ch)}/{MAX_VOICES} giọng")


def do_create_voice(name, dialect, gender):
    try:
        v = studio.library.create(name, dialect, gender)
        return (*_library_refresh(v.id), f"✅ Đã tạo giọng '{v.name}'. Giờ hãy thêm đoạn mẫu trung tính.")
    except Exception as e:
        return (*_library_refresh(), _err(e))


def do_add_clip(voice_id, clip, emotion, english):
    if not voice_id:
        return (*_library_refresh(), "❌ Chọn giọng trước.")
    if not clip:
        return (*_library_refresh(voice_id), "❌ Hãy thu âm hoặc tải lên một đoạn mẫu.")
    try:
        _p, warns = studio.library.add_clip(voice_id, clip, emotion, bool(english))
        msg = "✅ Đã lưu mẫu." + "".join(f"\n⚠️ {w}" for w in warns)
        return (*_library_refresh(voice_id), msg)
    except Exception as e:
        return (*_library_refresh(voice_id), _err(e))


def do_delete_voice(voice_id, confirm):
    if not voice_id:
        return (*_library_refresh(), "❌ Chọn giọng.")
    if not confirm:
        return (*_library_refresh(voice_id), "Tích ô 'Tôi chắc chắn' để xoá.")
    v = studio.library.get(voice_id)
    studio.library.delete(voice_id)
    return (*_library_refresh(), f"🗑️ Đã xoá giọng '{v.name if v else voice_id}'.")


def do_voice_details(voice_id):
    v = studio.library.get(voice_id) if voice_id else None
    if not v:
        return gr.update(choices=[], value=None), "", "", None
    clip_choices = [(k, k) for k in v.clips]
    ref = v.ref_for()
    return (gr.update(choices=clip_choices, value=clip_choices[0][1] if clip_choices else None),
            v.backbone, v.gemini_voice, str(ref) if ref else None)


def do_play_clip(voice_id, key):
    v = studio.library.get(voice_id) if voice_id else None
    p = v.clip_path(key) if (v and key) else None
    return str(p) if p else None


def do_remove_clip(voice_id, key):
    if voice_id and key:
        studio.library.remove_clip(voice_id, key)
    return (*_library_refresh(voice_id), f"🗑️ Đã xoá mẫu {key}.")


def do_save_voice_meta(voice_id, backbone, gemini_voice):
    if not voice_id:
        return "❌ Chọn giọng."
    backbone = (backbone or "").strip()
    if backbone and not Path(backbone).exists():
        return "❌ Thư mục mô hình không tồn tại."
    studio.library.update(voice_id, backbone=backbone, gemini_voice=gemini_voice or "")
    return "✅ Đã lưu."


def do_preview_voice(voice_id, language, emotion):
    if not voice_id:
        return None, "❌ Chọn giọng."
    try:
        r = studio.preview_voice(f"voice:{voice_id}", language, emotion)
        return str(r.path), r.summary()
    except Exception as e:
        return None, _err(e)


# ── tab 6: phòng thu ─────────────────────────────────────────────────────────

def _item_choices():
    return [(f"{it.id} · {it.text[:60]}", i) for i, it in enumerate(SCRIPT)]


def _item_view(session_name, idx):
    idx = int(idx or 0) % max(1, len(SCRIPT))
    it = SCRIPT[idx]
    s = recording.Session(session_name or "giong-cua-toi")
    take = str(s.take_path(it.id)) if s.has(it.id) else None
    emo = emotions.get(it.emotion).label
    head = (f"### {it.id} — {recording.GROUP_LABELS.get(it.group, it.group)} · Cảm xúc: **{emo}** "
            f"{'· ✅ đã thu' if take else ''}\n\n# {it.text}")
    return head, take, s.stats_text(), gr.update(value=idx)


def do_rec_nav(session_name, idx, delta):
    return _item_view(session_name, int(idx or 0) + delta)


def do_rec_next_missing(session_name, idx):
    s = recording.Session(session_name or "giong-cua-toi")
    n = len(SCRIPT)
    for k in range(1, n + 1):
        j = (int(idx or 0) + k) % n
        if not s.has(SCRIPT[j].id):
            return _item_view(session_name, j)
    return _item_view(session_name, idx)


def do_rec_save(session_name, idx, mic):
    if not mic:
        return (*_item_view(session_name, idx), None, "❌ Chưa có bản thu. Bấm nút micro để thu.")
    try:
        s = recording.Session(session_name or "giong-cua-toi")
        _p, dur, warns = s.save_take(SCRIPT[int(idx)], mic)
        msg = f"✅ Đã lưu {SCRIPT[int(idx)].id} ({dur:.1f}s)." + "".join(f"\n⚠️ {w}" for w in warns)
        nxt = do_rec_next_missing(session_name, idx)
        return (*nxt, None, msg)
    except Exception as e:
        return (*_item_view(session_name, idx), mic, _err(e))


def do_rec_delete(session_name, idx):
    s = recording.Session(session_name or "giong-cua-toi")
    s.delete_take(SCRIPT[int(idx)].id)
    return (*_item_view(session_name, idx), "🗑️ Đã xoá bản thu câu này.")


def do_build_voice(session_name, voice_name, dialect):
    try:
        s = recording.Session(session_name or "giong-cua-toi")
        vid, notes = s.build_voice(studio.library, voice_name or session_name, dialect)
        return "✅ " + "\n".join(notes)
    except Exception as e:
        return _err(e)


def do_export_review(session_name):
    s = recording.Session(session_name or "giong-cua-toi")
    return str(recording.export_csv_for_review(s, s.dir / "danh_sach_cau.csv"))


def do_finetune(session_name, run_name, epochs, rank, low_vram):
    s = recording.Session(session_name or "giong-cua-toi")
    s.write_metadata()
    logs = []
    try:
        for line in finetune.train(s.dir, (run_name or s.name).strip(), float(epochs), int(rank), bool(low_vram)):
            logs.append(line)
            yield "\n".join(logs[-400:])
        merged = finetune.output_dir((run_name or s.name).strip()) / "merged"
        logs.append(f"\n👉 Vào Kho giọng → chọn giọng của bạn → dán đường dẫn này vào ô 'Mô hình fine-tune':\n{merged}")
        yield "\n".join(logs[-400:])
    except Exception as e:
        logs.append(_err(e))
        yield "\n".join(logs[-400:])


# ── tab 7: so sánh ───────────────────────────────────────────────────────────

def do_compare(text, language, voice, gemini_voice, emotion, progress=gr.Progress()):
    outs, msgs = [], []
    jobs = [("VoxViet (offline)", None, voice), ("Gemini", "gemini", f"preset:{gemini_voice}"),
            ("gTTS", "gtts", "preset:" + ("com" if language == "en" else "com.vn"))]
    for i, (name, eng, v) in enumerate(jobs):
        progress(i / 3, desc=f"Đang tạo bản {name}…")
        try:
            r = studio.synthesize(text, language, v, emotion, engine_id=eng, want_srt=False, name=f"so-sanh-{name}",
                                  fmt="wav")
            outs.append(str(r.path))
            msgs.append(f"**{name}**: {r.duration:.1f}s, tạo trong {r.elapsed:.1f}s")
        except Exception as e:
            outs.append(None)
            msgs.append(f"**{name}**: {_err(e)}")
    return (*outs, "\n\n".join(msgs))


# ── tab 8: cài đặt ───────────────────────────────────────────────────────────

def do_save_settings(device, precision, dialect, fmt, lufs, sp, pp, en_engine, key, model, gvoice, enh):
    old = settings_mod.load()
    reload_model = (old.device, old.cpu_precision) != (device, precision)
    s = settings_mod.update(device=device, cpu_precision=precision, dialect=dialect, output_format=fmt, enhance=enh,
                            target_lufs=float(lufs), sentence_pause=float(sp), paragraph_pause=float(pp),
                            english_engine=en_engine, gemini_api_key=(key or "").strip(),
                            gemini_model=model or "", gemini_voice=gvoice or "Kore")
    if reload_model:
        engines.get("vieneu").unload()  # nạp lại theo thiết bị mới ở lần đọc tiếp theo
    return f"✅ Đã lưu cài đặt (thiết bị: {s.device})."


def do_list_gemini_models(key):
    if key:
        settings_mod.update(gemini_api_key=key.strip())
    try:
        models = engines.get("gemini").list_models(refresh=True)
        return gr.update(choices=[("Tự chọn mới nhất", "")] + [(m, m) for m in models], value=""), \
            f"✅ Tìm thấy {len(models)} model TTS: {', '.join(models[:6])}"
    except Exception as e:
        return gr.update(), _err(e)


def do_system_check():
    lines = [f"**VoxViet Studio {__version__}**", ""]
    try:
        import torch
        if torch.cuda.is_available():
            p = torch.cuda.get_device_properties(0)
            lines.append(f"🟢 GPU: {p.name} — {p.total_memory / 1024**3:.1f} GB VRAM, CUDA {torch.version.cuda}")
        else:
            lines.append("🟡 Không thấy GPU CUDA → chạy bằng CPU (ONNX). Vẫn dùng được, chậm hơn.")
    except ImportError:
        lines.append("🟡 Chưa cài PyTorch → chạy bằng CPU (ONNX).")
    for e in engines.registry().values():
        ok, why = e.available()
        lines.append(f"{'🟢' if ok else '⚪'} {e.label}{'' if ok else ' — ' + why}")
    ok, why = finetune.status()
    lines.append(f"{'🟢' if ok else '⚪'} Fine-tune: {why}")
    lines.append(f"{'🟢' if audio.ffmpeg_exe() else '🔴'} ffmpeg (đổi tốc độ, xuất MP3)")
    lines.append(f"\n📁 Dữ liệu: `{paths.DATA}`  \n📁 Mô hình: `{paths.MODELS}`")
    return "\n\n".join(lines)


def do_preload():
    try:
        eng = engines.get("vieneu")
        eng.load()
        return f"✅ Đã nạp VieNeu-TTS (backend: {eng.backend})."
    except Exception as e:
        return _err(e)


def do_save_lexicon(rows):
    try:
        data = rows.values.tolist() if hasattr(rows, "values") else (rows or [])
        studio.lexicon.set_entries([(r[0], r[1], r[2]) for r in data if len(r) >= 3])
        studio.lexicon.save_user()
        return "✅ Đã lưu từ điển phát âm."
    except Exception as e:
        return _err(e)


# ── dựng giao diện ───────────────────────────────────────────────────────────

CSS = """
.big-sentence h1 {font-size: 1.6rem !important; line-height: 1.5;}
footer {display: none !important;}
"""


def _out_controls():
    with gr.Column():
        out_audio = gr.Audio(label="Kết quả", type="filepath", interactive=False)
        out_files = gr.File(label="Tải về (âm thanh + phụ đề .srt)", file_count="multiple", interactive=False)
        status = gr.Markdown()
    return out_audio, out_files, status


def build() -> gr.Blocks:
    s = settings_mod.load()
    with gr.Blocks(title="VoxViet Studio") as demo:
        gr.Markdown(f"# 🎙️ VoxViet Studio <small>v{__version__}</small>\n"
                    "Chuyển văn bản thành giọng nói Việt – Anh, chạy hoàn toàn trên máy của bạn.")

        # ── 1. Đọc văn bản ──
        with gr.Tab("📖 Đọc văn bản"):
            with gr.Row():
                with gr.Column(scale=3):
                    t_text = gr.Textbox(label="Văn bản", lines=12, placeholder="Nhập hoặc dán văn bản…")
                    with gr.Row():
                        t_file = gr.File(label="Hoặc mở file (.txt, .docx)", file_types=[".txt", ".md", ".docx"],
                                         scale=2)
                        t_norm_btn = gr.Button("🔍 Xem cách máy sẽ đọc", scale=1)
                    t_norm = gr.Textbox(label="Văn bản sau chuẩn hoá", lines=4, interactive=False)
                    with gr.Accordion("Hướng dẫn thẻ cảm xúc / nghỉ / tiếng Anh", open=False):
                        gr.Markdown(TAG_HELP)
                with gr.Column(scale=2):
                    t_lang = gr.Radio(LANGS, value="vi", label="Module ngôn ngữ")
                    t_engine = gr.Dropdown(_engine_choices("vi"), value="auto", label="Bộ máy đọc")
                    t_voice = gr.Dropdown(_voice_choices("vi"), label="Giọng", allow_custom_value=False)
                    t_refresh = gr.Button("🔄 Làm mới danh sách giọng", size="sm")
                    t_emo = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, label="Cảm xúc")
                    t_speed = gr.Slider(0.6, 1.6, value=1.0, step=0.05, label="Tốc độ")
                    t_pause = gr.Slider(0.3, 2.5, value=1.0, step=0.1, label="Nhịp nghỉ giữa câu")
                    t_dialect = gr.Radio(DIALECTS, value="auto", label="Cách đọc số (nghìn/ngàn, linh/lẻ)")
                    t_enh = gr.Dropdown(enhance_mod.choices(), value=s.enhance, label="Làm trong giọng (hậu kỳ)")
                    t_fmt = gr.Radio(["wav", "mp3"], value=s.output_format, label="Định dạng")
                    with gr.Accordion("Nâng cao", open=False):
                        t_temp = gr.Slider(0.0, 1.0, value=0.0, step=0.05,
                                           label="Độ biến hoá ngữ điệu (0 = tự động theo cảm xúc)",
                                           info="Thấp (0.5–0.7): giọng ổn định, sạch hơn. Cao (0.9+): biểu cảm "
                                                "hơn nhưng dễ lẫn tạp âm.")
                    t_btn = gr.Button("▶️ Đọc", variant="primary", size="lg")
                    t_audio, t_files, t_status = _out_controls()
                    with gr.Accordion("🎧 Chuốt giọng bản vừa đọc (so sánh các mức làm trong)", open=True):
                        gr.Markdown("Nghe lại **cùng bản vừa đọc** với mức xử lý khác — không cần đọc lại. "
                                    "Mức hợp nhất → chọn ở ô *Làm trong giọng* hoặc đặt mặc định trong Cài đặt.")
                        with gr.Row():
                            t_rm_preset = gr.Radio(enhance_mod.choices(), value="goc", label="Mức")
                            t_rm_btn = gr.Button("🎧 Nghe với mức này")
                        t_rm_audio = gr.Audio(label="Bản xử lý lại", type="filepath", interactive=False)
                        t_rm_file = gr.File(label="Tải về", interactive=False)
                        t_rm_msg = gr.Markdown()
            t_file.change(_read_text_file, t_file, t_text)
            t_lang.change(lambda lang: (gr.update(choices=_engine_choices(lang), value="auto"),
                                        _voice_update(lang)), t_lang, [t_engine, t_voice])
            t_engine.change(lambda lang, e, v: _voice_update(lang, e, v), [t_lang, t_engine, t_voice], t_voice)
            t_refresh.click(lambda lang, e, v: _voice_update(lang, e, v), [t_lang, t_engine, t_voice], t_voice)
            t_norm_btn.click(do_preview_norm, [t_text, t_lang, t_voice, t_dialect], t_norm)
            t_btn.click(do_tts, [t_text, t_lang, t_engine, t_voice, t_emo, t_speed, t_pause, t_dialect, t_fmt,
                                 t_enh, t_temp], [t_audio, t_files, t_status])
            t_rm_btn.click(do_remaster, t_rm_preset, [t_rm_audio, t_rm_file, t_rm_msg])

        # ── 2. Hội thoại ──
        with gr.Tab("🎭 Hội thoại"):
            with gr.Row():
                with gr.Column(scale=3):
                    d_script = gr.Textbox(label="Kịch bản (mỗi dòng 'Tên (cảm xúc): lời thoại')", lines=14,
                                          value=DIALOGUE_EXAMPLE)
                    d_parse = gr.Button("👥 Tìm nhân vật")
                    d_info = gr.Markdown()
                with gr.Column(scale=4):
                    gr.Markdown("**Gán giọng cho từng nhân vật**")
                    cast_inputs, cast_rows, parse_outputs = [], [], []
                    vc = _voice_choices("vi")
                    for i in range(MAX_CAST):
                        with gr.Row(visible=False) as row:
                            nm = gr.Textbox(show_label=False, interactive=False, scale=2, container=False)
                            vo = gr.Dropdown(vc, value=(vc[i % len(vc)][1] if vc else None), show_label=False,
                                             scale=3, container=False)
                            lg = gr.Dropdown(LANGS, value="vi", show_label=False, scale=1, container=False)
                            em = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, show_label=False, scale=2,
                                             container=False)
                            sp = gr.Slider(0.6, 1.6, value=1.0, step=0.05, show_label=False, scale=2,
                                           container=False)
                        lg.change(lambda lang, v: _voice_update(lang, None, v), [lg, vo], vo)
                        cast_rows.append(row)
                        cast_inputs += [nm, vo, lg, em, sp]
                        parse_outputs += [row, nm]
                    with gr.Row():
                        d_gap = gr.Slider(0.0, 1.5, value=0.35, step=0.05, label="Khoảng nghỉ giữa lượt thoại (s)")
                        d_fmt = gr.Radio(["wav", "mp3"], value=s.output_format, label="Định dạng")
                    d_btn = gr.Button("▶️ Tạo hội thoại", variant="primary", size="lg")
                    d_audio, d_files, d_status = _out_controls()
            d_parse.click(do_parse_cast, d_script, parse_outputs + [d_info])
            demo.load(do_parse_cast, d_script, parse_outputs + [d_info])
            d_btn.click(do_dialogue, [d_script, d_gap, d_fmt, *cast_inputs], [d_audio, d_files, d_status])

        # ── 3. Lồng tiếng ──
        with gr.Tab("🎬 Lồng tiếng (SRT)"):
            gr.Markdown("Mỗi câu phụ đề được đọc **đúng thời điểm**; câu dài hơn khung thời gian sẽ được "
                        "tự tăng tốc (tối đa theo thanh trượt). Ghép file âm thanh này vào video bằng "
                        "CapCut / Premiere / DaVinci.")
            with gr.Row():
                with gr.Column(scale=3):
                    s_file = gr.File(label="File phụ đề .srt", file_types=[".srt"])
                    s_text = gr.Textbox(label="Hoặc dán nội dung SRT", lines=12)
                with gr.Column(scale=2):
                    s_lang = gr.Radio(LANGS, value="vi", label="Module ngôn ngữ")
                    s_voice = gr.Dropdown(_voice_choices("vi"), label="Giọng")
                    s_emo = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, label="Cảm xúc")
                    s_speed = gr.Slider(0.6, 1.6, value=1.0, step=0.05, label="Tốc độ")
                    s_stretch = gr.Slider(1.0, 1.8, value=1.35, step=0.05, label="Tăng tốc tối đa để vừa khung")
                    s_fmt = gr.Radio(["wav", "mp3"], value=s.output_format, label="Định dạng")
                    s_btn = gr.Button("▶️ Lồng tiếng", variant="primary", size="lg")
                    s_audio, s_files, s_status = _out_controls()
            s_lang.change(lambda lang, v: _voice_update(lang, None, v), [s_lang, s_voice], s_voice)
            s_btn.click(do_dub, [s_file, s_text, s_lang, s_voice, s_emo, s_speed, s_stretch, s_fmt],
                        [s_audio, s_files, s_status])

        # ── 4. Trực tiếp ──
        with gr.Tab("⚡ Trực tiếp"):
            gr.Markdown("Gõ câu rồi nhấn **Enter** — âm thanh phát ngay khi vừa tạo (độ trễ thấp, "
                        "dùng cho trợ lý ảo / nói chuyện trực tiếp).")
            with gr.Row():
                l_lang = gr.Radio(LANGS, value="vi", label="Module")
                l_voice = gr.Dropdown(_voice_choices("vi"), label="Giọng")
                l_emo = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, label="Cảm xúc")
                l_speed = gr.Slider(0.6, 1.6, value=1.0, step=0.05, label="Tốc độ (khác 1.0 sẽ trễ hơn)")
            l_text = gr.Textbox(label="Câu nói", placeholder="Xin chào, tôi có thể giúp gì cho bạn?")
            l_audio = gr.Audio(label="Đang phát", streaming=True, autoplay=True, interactive=False)
            l_lang.change(lambda lang, v: _voice_update(lang, None, v), [l_lang, l_voice], l_voice)
            l_text.submit(do_live, [l_text, l_lang, l_voice, l_emo, l_speed], l_audio)

        # ── 5. Kho giọng ──
        with gr.Tab("🗂️ Kho giọng"):
            lib_count = gr.Markdown()
            lib_table = gr.Dataframe(headers=["Tên", "Vùng", "Giới tính", "Mẫu đã có", "Fine-tune"],
                                     interactive=False, value=_library_table())
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### ➕ Tạo giọng mới")
                    v_name = gr.Textbox(label="Tên giọng", placeholder="Giọng của tôi")
                    v_dialect = gr.Radio([("Bắc", "bac"), ("Nam", "nam"), ("Trung", "trung")], value="bac",
                                         label="Vùng miền")
                    v_gender = gr.Radio([("Nam", "male"), ("Nữ", "female"), ("Khác", "")], value="",
                                        label="Giới tính")
                    v_create = gr.Button("Tạo giọng", variant="primary")
                with gr.Column():
                    gr.Markdown("### 🎤 Thêm đoạn mẫu (5–10 giây, nói tự nhiên, phòng yên tĩnh)")
                    v_sel = gr.Dropdown(_library_choices(), label="Giọng")
                    v_clip = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Đoạn mẫu")
                    with gr.Row():
                        v_clip_emo = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, label="Cảm xúc của mẫu")
                        v_clip_en = gr.Checkbox(label="Mẫu nói tiếng Anh", value=False)
                    v_add = gr.Button("💾 Lưu mẫu", variant="primary")
            v_msg = gr.Markdown()
            with gr.Accordion("Chi tiết / nghe thử / xoá", open=False):
                with gr.Row():
                    v_clips = gr.Dropdown([], label="Các mẫu của giọng")
                    v_clip_play = gr.Audio(label="Nghe mẫu", type="filepath", interactive=False)
                    v_clip_del = gr.Button("Xoá mẫu này")
                with gr.Row():
                    v_backbone = gr.Textbox(label="Mô hình fine-tune (thư mục merged, tuỳ chọn)")
                    v_gemini = gr.Dropdown([(g, g) for g in GEMINI_VOICES],
                                           label="Giọng Gemini tương ứng (khi so sánh)", allow_custom_value=True)
                    v_meta_save = gr.Button("Lưu")
                with gr.Row():
                    v_prev_lang = gr.Radio(LANGS, value="vi", label="Nghe thử bằng")
                    v_prev_emo = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, label="Cảm xúc")
                    v_prev = gr.Button("🔊 Nghe thử giọng")
                v_prev_audio = gr.Audio(label="Nghe thử", type="filepath", interactive=False)
                with gr.Row():
                    v_confirm = gr.Checkbox(label="Tôi chắc chắn muốn xoá giọng này")
                    v_del = gr.Button("🗑️ Xoá giọng", variant="stop")
            lib_outs = [lib_table, v_sel, lib_count]
            demo.load(lambda: _library_refresh(), None, lib_outs)
            v_create.click(do_create_voice, [v_name, v_dialect, v_gender], lib_outs + [v_msg])
            v_add.click(do_add_clip, [v_sel, v_clip, v_clip_emo, v_clip_en], lib_outs + [v_msg])
            v_del.click(do_delete_voice, [v_sel, v_confirm], lib_outs + [v_msg])
            v_sel.change(do_voice_details, v_sel, [v_clips, v_backbone, v_gemini, v_clip_play])
            v_clips.change(do_play_clip, [v_sel, v_clips], v_clip_play)
            v_clip_del.click(do_remove_clip, [v_sel, v_clips], lib_outs + [v_msg])
            v_meta_save.click(do_save_voice_meta, [v_sel, v_backbone, v_gemini], v_msg)
            v_prev.click(do_preview_voice, [v_sel, v_prev_lang, v_prev_emo], [v_prev_audio, v_msg])

        # ── 6. Phòng thu & fine-tune ──
        with gr.Tab("🎚️ Phòng thu & Fine-tune"):
            gr.Markdown(
                "Đọc lần lượt các câu trong kịch bản (tiếng Việt, Việt xen Anh, cảm xúc, tiếng Anh). "
                "**Mẹo:** phòng yên tĩnh, micro cách miệng ~20 cm, đọc tự nhiên như nói chuyện, giữ cùng một "
                "âm lượng. Chỉ cần vài câu là đủ để *clone tức thì*; 10–30 phút để *fine-tune*.")
            with gr.Row():
                r_session = gr.Dropdown(recording.Session.list_names() or ["giong-cua-toi"],
                                        value=(recording.Session.list_names() or ["giong-cua-toi"])[0],
                                        allow_custom_value=True, label="Tên phiên thu (gõ tên mới để tạo)")
                r_jump = gr.Dropdown(_item_choices(), value=0, label="Chuyển tới câu")
            r_stats = gr.Markdown()
            r_head = gr.Markdown(elem_classes=["big-sentence"])
            with gr.Row():
                r_mic = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Thu câu này")
                r_take = gr.Audio(label="Bản đã lưu", type="filepath", interactive=False)
            with gr.Row():
                r_prev = gr.Button("◀ Câu trước")
                r_save = gr.Button("💾 Lưu & sang câu chưa thu", variant="primary")
                r_next = gr.Button("Câu sau ▶")
                r_del = gr.Button("Xoá bản thu câu này", variant="stop")
            r_msg = gr.Markdown()
            view_outs = [r_head, r_take, r_stats, r_jump]
            r_jump.change(_item_view, [r_session, r_jump], view_outs)
            r_session.change(_item_view, [r_session, r_jump], view_outs)
            r_prev.click(lambda s_, i: do_rec_nav(s_, i, -1), [r_session, r_jump], view_outs)
            r_next.click(lambda s_, i: do_rec_nav(s_, i, 1), [r_session, r_jump], view_outs)
            r_save.click(do_rec_save, [r_session, r_jump, r_mic], view_outs + [r_mic, r_msg])
            r_del.click(do_rec_delete, [r_session, r_jump], view_outs + [r_msg])
            demo.load(_item_view, [r_session, r_jump], view_outs)
            with gr.Accordion("👤 Tạo giọng trong Kho từ các câu đã thu (clone tức thì)", open=True):
                with gr.Row():
                    r_vname = gr.Textbox(label="Tên giọng", value="Giọng của tôi")
                    r_vdialect = gr.Radio([("Bắc", "bac"), ("Nam", "nam"), ("Trung", "trung")], value="bac",
                                          label="Vùng miền")
                    r_build = gr.Button("Tạo / cập nhật giọng", variant="primary")
                    r_export = gr.Button("📄 Xuất danh sách câu (Excel)")
                r_build_msg = gr.Markdown()
                r_export_file = gr.File(label="Danh sách", interactive=False)
            with gr.Accordion("🧪 Fine-tune giọng (nâng cao, không bắt buộc)", open=False):
                gr.Markdown("Cần GPU NVIDIA ≥ 6 GB và đã chạy `install_finetune.bat`. Thời gian: khoảng "
                            "30–90 phút cho 20 phút dữ liệu. Có thể đóng trình duyệt nhưng **không tắt** cửa sổ "
                            "dòng lệnh.")
                ft_status = gr.Markdown(finetune.status()[1])
                with gr.Row():
                    ft_run = gr.Textbox(label="Tên mô hình", value="giong-cua-toi")
                    ft_epochs = gr.Slider(1, 10, value=3, step=1, label="Số epoch")
                    ft_rank = gr.Dropdown([8, 16, 32], value=16, label="LoRA rank")
                    ft_low = gr.Checkbox(value=True, label="Tiết kiệm VRAM (6 GB)")
                ft_btn = gr.Button("🚀 Bắt đầu fine-tune", variant="primary")
                ft_log = gr.Textbox(label="Nhật ký", lines=16, max_lines=16, autoscroll=True)
            r_build.click(do_build_voice, [r_session, r_vname, r_vdialect], r_build_msg)
            r_export.click(do_export_review, r_session, r_export_file)
            ft_btn.click(do_finetune, [r_session, ft_run, ft_epochs, ft_rank, ft_low], ft_log)

        # ── 7. So sánh Google ──
        with gr.Tab("⚖️ So sánh với Google"):
            gr.Markdown("Nghe **cùng một đoạn** bằng VoxViet (offline) và 2 dịch vụ Google miễn phí để đánh giá "
                        "độ tự nhiên. Google chỉ dùng làm **mẫu tham khảo**, cần Internet và (với Gemini) API key.")
            with gr.Row():
                c_text = gr.Textbox(label="Văn bản", lines=4,
                                    value="Chào bạn! Hôm nay mình sẽ hướng dẫn cách dùng Google Drive để "
                                          "backup dữ liệu, chỉ mất khoảng 5 phút thôi.")
                with gr.Column():
                    c_lang = gr.Radio(LANGS, value="vi", label="Ngôn ngữ")
                    c_voice = gr.Dropdown(_voice_choices("vi"), label="Giọng VoxViet")
                    c_gvoice = gr.Dropdown(GEMINI_VOICES,
                                           value=s.gemini_voice or "Kore", label="Giọng Gemini")
                    c_emo = gr.Dropdown(EMO_CHOICES, value=emotions.DEFAULT, label="Cảm xúc")
                    c_btn = gr.Button("⚖️ So sánh", variant="primary")
            with gr.Row():
                c_a = gr.Audio(label="VoxViet (offline)", type="filepath", interactive=False)
                c_b = gr.Audio(label="Google Gemini TTS", type="filepath", interactive=False)
                c_c = gr.Audio(label="Google gTTS", type="filepath", interactive=False)
            c_msg = gr.Markdown()
            c_lang.change(lambda lang, v: _voice_update(lang, None, v), [c_lang, c_voice], c_voice)
            c_btn.click(do_compare, [c_text, c_lang, c_voice, c_gvoice, c_emo], [c_a, c_b, c_c, c_msg])

        # ── 8. Cài đặt ──
        with gr.Tab("⚙️ Cài đặt"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Máy & âm thanh")
                    st_device = gr.Radio([("Tự động", "auto"), ("GPU (CUDA)", "cuda"), ("CPU", "cpu")],
                                         value=s.device, label="Thiết bị chạy mô hình")
                    st_prec = gr.Radio([("fp32 — chất lượng cao", "fp32"), ("int8 — nhanh (CPU có VNNI)", "int8")],
                                       value=s.cpu_precision, label="Độ chính xác khi chạy CPU")
                    st_dialect = gr.Radio([("Bắc", "bac"), ("Nam", "nam")], value=s.dialect,
                                          label="Cách đọc số mặc định")
                    st_fmt = gr.Radio(["wav", "mp3"], value=s.output_format, label="Định dạng mặc định")
                    st_lufs = gr.Slider(-30, -10, value=s.target_lufs, step=1, label="Âm lượng chuẩn (LUFS)")
                    st_enh = gr.Radio(enhance_mod.choices(), value=s.enhance,
                                      label="Làm trong giọng mặc định (dùng cho mọi tab)")
                    st_sp = gr.Slider(0.0, 1.0, value=s.sentence_pause, step=0.05, label="Nghỉ giữa câu (s)")
                    st_pp = gr.Slider(0.0, 2.0, value=s.paragraph_pause, step=0.05, label="Nghỉ giữa đoạn (s)")
                    st_en = gr.Radio([("VieNeu (mặc định, cùng giọng clone)", "vieneu"),
                                      ("Chatterbox (tiếng Anh Pro, cần cài thêm)", "chatterbox")],
                                     value=s.english_engine, label="Bộ máy cho module English")
                with gr.Column():
                    gr.Markdown("### Google (chỉ để so sánh)")
                    st_key = gr.Textbox(label="Gemini API key (miễn phí tại aistudio.google.com)",
                                        value=s.gemini_api_key, type="password")
                    with gr.Row():
                        st_model = gr.Dropdown([("Tự chọn mới nhất", "")] +
                                               ([(s.gemini_model, s.gemini_model)] if s.gemini_model else []),
                                               value=s.gemini_model, label="Model Gemini TTS",
                                               allow_custom_value=True)
                        st_models_btn = gr.Button("Tải danh sách model", size="sm")
                    st_gvoice = gr.Dropdown(GEMINI_VOICES,
                                            value=s.gemini_voice or "Kore", label="Giọng Gemini mặc định")
                    st_gmsg = gr.Markdown()
                    gr.Markdown("### Hệ thống")
                    with gr.Row():
                        st_check = gr.Button("🩺 Kiểm tra hệ thống")
                        st_preload = gr.Button("⏬ Nạp mô hình ngay")
                    st_sys = gr.Markdown()
            st_save = gr.Button("💾 Lưu cài đặt", variant="primary")
            st_msg = gr.Markdown()
            gr.Markdown("### 📚 Từ điển phát âm\nThêm từ đọc sai: *mục* = `all` / `vi` / `en`, *từ gốc*, "
                        "*cách đọc* (viết theo cách đọc, hoặc `<en>…</en>` để ép đọc tiếng Anh).")
            lx_table = gr.Dataframe(headers=["mục", "từ gốc", "cách đọc"], value=studio.lexicon.rows(),
                                    interactive=True, datatype=["str", "str", "str"], row_count=(3, "dynamic"))
            lx_save = gr.Button("💾 Lưu từ điển")
            lx_msg = gr.Markdown()
            st_save.click(do_save_settings, [st_device, st_prec, st_dialect, st_fmt, st_lufs, st_sp, st_pp, st_en,
                                             st_key, st_model, st_gvoice, st_enh], st_msg)
            st_models_btn.click(do_list_gemini_models, st_key, [st_model, st_gmsg])
            st_check.click(do_system_check, None, st_sys)
            st_preload.click(do_preload, None, st_sys)
            lx_save.click(do_save_lexicon, lx_table, lx_msg)
    return demo


def launch(port: int = 7860, inbrowser: bool = True, share: bool = False) -> None:
    demo = build()
    demo.queue(default_concurrency_limit=1).launch(
        server_name="127.0.0.1", server_port=port, inbrowser=inbrowser, share=share,
        allowed_paths=[str(paths.DATA)], css=CSS, theme=gr.themes.Soft(), show_error=True,
    )
