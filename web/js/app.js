// VoxViet Studio — giao diện. Mỗi màn hình là một khối init*(); điều hướng bằng #hash.
import { api, esc, runJob, toast } from "./api.js";
import { Recorder } from "./recorder.js";
import { Tape } from "./tape.js";
import { AVATAR_POOL, avatar, avatarUrl, metaHTML, VoicePicker } from "./voicepicker.js";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
let STATE = null;

// ── tiện ích điều khiển ─────────────────────────────────────────────────────
function seg(id, onChange) {
  const root = document.getElementById(id);
  const ctl = {
    get value() { return $("button[aria-pressed='true']", root)?.dataset.v; },
    set(v) { $$("button", root).forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === v))); },
  };
  root.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    ctl.set(b.dataset.v);
    onChange?.(b.dataset.v);
  });
  return ctl;
}

function fillSelect(el, items, value) {
  el.innerHTML = items.map((it) => `<option value="${esc(it.key)}">${esc(it.label)}</option>`).join("");
  if (value != null) el.value = value;
}

function range(id, fmt, onInput) {
  const el = document.getElementById(id);
  const out = document.getElementById(`${id}-v`);
  const upd = () => { if (out) out.textContent = fmt(+el.value); onInput?.(+el.value); };
  el.addEventListener("input", upd);
  upd();
  return el;
}

function busy(prefix, on, msg) {
  const box = document.getElementById(`${prefix}-busy`);
  const go = document.getElementById(`${prefix}-go`);
  if (box) box.hidden = !on;
  if (go) go.disabled = on;
  if (msg) document.getElementById(`${prefix}-busy-msg`).textContent = msg;
  if (!on) setProg(prefix, 0);
}
function setProg(prefix, p) { document.getElementById(`${prefix}-prog`)?.style.setProperty("--p", String(p)); }
const jobProgress = (prefix) => (j) => { setProg(prefix, j.progress); if (j.message) document.getElementById(`${prefix}-busy-msg`).textContent = j.message; };

function errorBox(root, msg) {
  root.innerHTML = `<div class="error-box"><svg class="icon"><use href="/icons.svg#i-triangle-alert"/></svg><span>${esc(msg)}</span></div>`;
}

const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(`vv:${k}`)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(`vv:${k}`, JSON.stringify(v)); } catch { /* bỏ qua */ } },
};

// ── điều hướng ──────────────────────────────────────────────────────────────
const VIEWS = ["doc", "hoi-thoai", "long-tieng", "truc-tiep", "kho-giong", "phong-thu", "so-sanh", "cai-dat", "cap-nhat"];
const onShow = {};
function route() {
  const id = VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : "doc";
  for (const v of VIEWS) document.getElementById(`view-${v}`).hidden = v !== id;
  $$("#nav a").forEach((a) => (a.getAttribute("href") === `#${id}` ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current")));
  onShow[id]?.();
  $("#main").scrollTop = 0;
}

// ── 1. Đọc văn bản ──────────────────────────────────────────────────────────
function initDoc() {
  const text = $("#doc-text");
  text.value = store.get("doc-text", "Xin chào! Sáng nay mình có cuộc meeting online với CEO lúc 10h30, nhớ gửi file qua email nhé. [vui] Tuyệt vời quá! [nghỉ 1s] Giá vé là 1.250.000đ.");
  const count = () => { $("#doc-count").textContent = `${text.value.length.toLocaleString("vi-VN")} ký tự`; store.set("doc-text", text.value); };
  text.addEventListener("input", count);
  count();

  const lang = seg("doc-lang", () => refreshVoices());
  const dialect = seg("doc-dialect");
  const fmt = seg("doc-fmt");
  fmt.set(STATE.settings.output_format || "wav");
  const picker = new VoicePicker($("#doc-voice"), { onChange: (v) => store.set("doc-voice", v) });
  fillSelect($("#doc-emo"), STATE.emotions);
  fillSelect($("#doc-enh"), STATE.enhance, STATE.settings.enhance);
  fillSelect($("#doc-derev"), STATE.dereverb, STATE.settings.dereverb);
  $("#doc-ai").checked = !!STATE.settings.ai_clean;
  const engines = (l) => [{ key: "auto", label: "Tự động (khuyên dùng)" }, ...STATE.engines.filter((e) => e.languages.includes(l))
    .map((e) => ({ key: e.id, label: e.label + (e.available ? "" : " — chưa sẵn sàng") }))];
  fillSelect($("#doc-engine"), engines("vi"), "auto");
  $("#doc-engine").addEventListener("change", () => refreshVoices());
  range("doc-speed", (v) => `${v.toFixed(2)}×`);
  range("doc-pause", (v) => `${v.toFixed(1)}×`);
  range("doc-temp", (v) => (v > 0 ? v.toFixed(2) : "tự động"));

  async function refreshVoices() {
    const l = lang.value;
    if (!engines(l).some((e) => e.key === $("#doc-engine").value)) fillSelect($("#doc-engine"), engines(l), "auto");
    await picker.refresh(l, $("#doc-engine").value, store.get("doc-voice", STATE.default_preset));
  }
  onShow.doc = () => refreshVoices();

  // chèn thẻ
  $("#doc-tags").addEventListener("click", (e) => {
    const b = e.target.closest(".chip");
    if (!b) return;
    const s = text.selectionStart, en = text.selectionEnd;
    const ins = b.dataset.wrap ? `<en>${text.value.slice(s, en) || "word"}</en>` : b.dataset.tag;
    text.setRangeText(ins, s, en, "end");
    text.focus();
    count();
  });

  // mở file
  $("#doc-file").addEventListener("change", async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const form = new FormData();
    form.append("file", f);
    try {
      text.value = (await api.upload("/api/text-file", form)).text;
      count();
      toast(`Đã mở ${f.name}`);
    } catch (err) { toast(err.message, "err"); }
    e.target.value = "";
  });

  // xem cách máy đọc
  $("#doc-norm-btn").addEventListener("click", async () => {
    try {
      const r = await api.post("/api/normalize", { text: text.value, language: lang.value, voice: picker.value, dialect: dialect.value });
      $("#doc-norm-out").innerHTML = r.lines.map((l) => l.kind === "pause"
        ? `<div class="sentence" style="cursor:default"><span class="t">nghỉ</span><span class="muted">${l.seconds} giây</span></div>`
        : `<div class="sentence" style="cursor:default"><span class="t">${esc(l.emotion)}</span><span>${esc(l.text)}</span></div>`).join("") || `<p class="hint">Chưa có văn bản.</p>`;
      $("#doc-norm-panel").hidden = false;
    } catch (err) { toast(err.message, "err"); }
  });
  $("#doc-norm-close").addEventListener("click", () => { $("#doc-norm-panel").hidden = true; });

  const tape = new Tape($("#doc-result"), { downloads: $("#doc-downloads") });
  async function go() {
    if (!text.value.trim()) { toast("Chưa có văn bản để đọc.", "err"); text.focus(); return; }
    busy("doc", true, "Đang đọc…");
    try {
      const temp = +$("#doc-temp").value;
      const result = await runJob("/api/jobs/tts", {
        text: text.value, language: lang.value, engine: $("#doc-engine").value, voice: picker.value,
        emotion: $("#doc-emo").value, speed: +$("#doc-speed").value, pause: +$("#doc-pause").value,
        dialect: dialect.value, enhance: $("#doc-enh").value, dereverb: $("#doc-derev").value,
        ai_clean: $("#doc-ai").checked, temperature: temp > 0 ? temp : null, fmt: fmt.value,
      }, jobProgress("doc"));
      tape.load(result);
      $("#doc-ab").hidden = false;
      $("#ab-result").innerHTML = "";
      tape.audio.play().catch(() => {});
    } catch (err) {
      errorBox($("#doc-result"), err.message);
    } finally { busy("doc", false); }
  }
  $("#doc-go").addEventListener("click", go);
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter" && !$("#view-doc").hidden) { e.preventDefault(); go(); }
  });

  // thử hậu kỳ khác
  fillSelect($("#ab-enh"), STATE.enhance, "goc");
  fillSelect($("#ab-derev"), STATE.dereverb, "tat");
  const abTape = new Tape($("#ab-result"), { sentences: false });
  $("#ab-btn").addEventListener("click", async () => {
    const btn = $("#ab-btn");
    btn.disabled = true;
    try {
      const r = await runJob("/api/jobs/remaster", { enhance: $("#ab-enh").value, dereverb: $("#ab-derev").value, ai_clean: $("#ab-ai").checked });
      abTape.load({ audio_url: r.audio_url, duration: tape.audio.duration || 0, subtitles: tape.subs },
        `<p class="hint">Đang nghe: làm trong <b>${esc($("#ab-enh").selectedOptions[0].text)}</b>, giảm vang <b>${esc($("#ab-derev").selectedOptions[0].text)}</b>${$("#ab-ai").checked ? ", khử nhiễu AI" : ""}. <a href="${r.audio_url}" download>Tải bản này</a></p>`);
      abTape.audio.play().catch(() => {});
    } catch (err) { toast(err.message, "err"); } finally { btn.disabled = false; }
  });
}

// ── 2. Hội thoại ────────────────────────────────────────────────────────────
function initDialogue() {
  const script = $("#ht-script");
  script.value = store.get("ht-script", "Người kể: Chiều hôm ấy, trời đổ mưa rất to.\nMinh (vui): Lan ơi! Lâu quá không gặp, dạo này bạn thế nào?\nLan (ngạc nhiên): Ủa, Minh hả? Sao bạn lại ở đây?\nMinh: Mình vừa về nước tuần trước. Còn có buổi meeting với khách hàng nữa.\nLan: [thì thầm] Nói nhỏ thôi, mọi người đang nhìn kìa.");
  let voices = [];
  let cast = store.get("ht-cast", {});
  const tape = new Tape($("#ht-result"), { downloads: $("#ht-downloads") });
  range("ht-gap", (v) => `${v.toFixed(2)} s`);

  const voiceOptions = (sel) => {
    const mine = voices.filter((v) => v.kind === "mine"), pre = voices.filter((v) => v.kind !== "mine");
    const GEN = { nam: "nam", nu: "nữ", male: "nam", female: "nữ" }, REG = { bac: "Bắc", trung: "Trung", nam: "Nam" };
    const opt = (v) => `<option value="${esc(v.value)}" ${v.value === sel ? "selected" : ""}>${esc(v.label)} (${[GEN[v.gender], REG[v.region]].filter(Boolean).join(", ")})</option>`;
    return (mine.length ? `<optgroup label="Giọng của bạn">${mine.map(opt).join("")}</optgroup>` : "") + `<optgroup label="Giọng có sẵn">${pre.map(opt).join("")}</optgroup>`;
  };

  const castAvatar = (name, value) => {
    const v = voices.find((x) => x.value === value);
    return avatar(name, v ? v.value : name, v?.gender, v?.avatar);
  };

  async function parse() {
    store.set("ht-script", script.value);
    let r;
    try { r = await api.post("/api/dialogue/parse", { script: script.value }); } catch { return; }
    $("#ht-count").textContent = `${r.speakers.length} nhân vật · ${r.lines} lượt`;
    const presets = voices.filter((v) => v.kind !== "mine");
    const box = $("#ht-cast");
    box.innerHTML = r.speakers.map((name, i) => {
      const c = cast[name] || { voice: presets[(i * 5) % Math.max(1, presets.length)]?.value, language: "vi", emotion: "trung_tinh", speed: 1 };
      cast[name] = c;
      return `<div class="stack" style="gap:6px" data-name="${esc(name)}">
        <div class="cast-name" data-av>${castAvatar(name, c.voice)}<span>${esc(name)}</span></div>
        <select data-k="voice" aria-label="Giọng của ${esc(name)}">${voiceOptions(c.voice)}</select>
        <div class="grid-2" style="gap:6px">
          <select data-k="emotion" aria-label="Cảm xúc của ${esc(name)}">${STATE.emotions.map((e) => `<option value="${e.key}" ${e.key === c.emotion ? "selected" : ""}>${esc(e.label)}</option>`).join("")}</select>
          <select data-k="language" aria-label="Ngôn ngữ của ${esc(name)}"><option value="vi" ${c.language === "vi" ? "selected" : ""}>Tiếng Việt</option><option value="en" ${c.language === "en" ? "selected" : ""}>English</option></select>
        </div></div>`;
    }).join("") || `<p class="hint">Chưa có lượt thoại. Mỗi dòng dạng "Tên: lời thoại".</p>`;
  }
  $("#ht-cast").addEventListener("change", (e) => {
    const row = e.target.closest("[data-name]");
    if (!row) return;
    cast[row.dataset.name][e.target.dataset.k] = e.target.value;
    store.set("ht-cast", cast);
    if (e.target.dataset.k === "voice") {
      const head = $("[data-av]", row);
      head.querySelector(".avatar").outerHTML = castAvatar(row.dataset.name, e.target.value);
    }
  });
  let t = 0;
  script.addEventListener("input", () => { clearTimeout(t); t = setTimeout(parse, 400); });
  onShow["hoi-thoai"] = async () => { voices = (await api.get("/api/voices?language=vi&engine=auto")).voices; parse(); };

  $("#ht-go").addEventListener("click", async () => {
    busy("ht", true, "Đang tạo hội thoại…");
    try {
      const result = await runJob("/api/jobs/dialogue", { script: script.value, cast, gap: +$("#ht-gap").value }, jobProgress("ht"));
      tape.load(result);
      tape.audio.play().catch(() => {});
    } catch (err) { errorBox($("#ht-result"), err.message); } finally { busy("ht", false); }
  });
}

// ── 3. Lồng tiếng ───────────────────────────────────────────────────────────
function initDub() {
  const lang = seg("lt-lang", () => picker.refresh(lang.value));
  const picker = new VoicePicker($("#lt-voice"));
  fillSelect($("#lt-emo"), STATE.emotions);
  range("lt-speed", (v) => `${v.toFixed(2)}×`);
  range("lt-stretch", (v) => `${v.toFixed(2)}×`);
  const tape = new Tape($("#lt-result"), { downloads: $("#lt-downloads") });
  onShow["long-tieng"] = () => picker.refresh(lang.value, "auto", STATE.default_preset);
  $("#lt-file").addEventListener("change", async (e) => {
    const f = e.target.files[0];
    if (f) { $("#lt-srt").value = await f.text(); toast(`Đã mở ${f.name}`); }
    e.target.value = "";
  });
  $("#lt-go").addEventListener("click", async () => {
    if (!$("#lt-srt").value.trim()) { toast("Chưa có phụ đề.", "err"); return; }
    busy("lt", true, "Đang lồng tiếng…");
    try {
      const result = await runJob("/api/jobs/dub", { srt: $("#lt-srt").value, language: lang.value, voice: picker.value,
        emotion: $("#lt-emo").value, speed: +$("#lt-speed").value, max_stretch: +$("#lt-stretch").value }, jobProgress("lt"));
      tape.load(result);
    } catch (err) { errorBox($("#lt-result"), err.message); } finally { busy("lt", false); }
  });
}

// ── 4. Trực tiếp ────────────────────────────────────────────────────────────
function initLive() {
  const lang = seg("tt-lang", () => picker.refresh(lang.value));
  const picker = new VoicePicker($("#tt-voice"));
  fillSelect($("#tt-emo"), STATE.emotions);
  range("tt-speed", (v) => `${v.toFixed(2)}×`);
  onShow["truc-tiep"] = () => picker.refresh(lang.value, "auto", STATE.default_preset);
  let ws = null, ctx = null, playHead = 0, sources = [], levels = new Array(120).fill(0), sentAt = 0;
  const canvas = $("#tt-meter");

  function drawMeter() {
    const dpr = devicePixelRatio || 1, w = canvas.clientWidth, h = canvas.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    const g = canvas.getContext("2d");
    g.scale(dpr, dpr);
    const accent = getComputedStyle(document.documentElement).getPropertyValue("--accent");
    const faint = getComputedStyle(document.documentElement).getPropertyValue("--line");
    const n = levels.length, bw = w / n;
    levels.forEach((lv, i) => {
      const bh = Math.max(2, Math.min(1, lv * 1.6) * (h - 12));
      g.fillStyle = lv > 0.02 ? accent : faint;
      g.fillRect(i * bw + 1, (h - bh) / 2, Math.max(1, bw - 2), bh);
    });
  }
  new ResizeObserver(drawMeter).observe(canvas);

  function connect() {
    return new Promise((resolve, reject) => {
      if (ws && ws.readyState === 1) return resolve(ws);
      ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/live`);
      ws.binaryType = "arraybuffer";
      ws.onopen = () => resolve(ws);
      ws.onerror = () => reject(new Error("Không kết nối được máy chủ."));
      ws.onmessage = (ev) => {
        if (typeof ev.data === "string") {
          const d = JSON.parse(ev.data);
          if (d.first_ms != null) { $("#tt-first").textContent = `${d.first_ms} ms`; addHistory(d.first_ms); }
          if (d.done) $("#tt-state").textContent = "đã đọc xong";
          if (d.error) { $("#tt-state").textContent = "lỗi"; toast(d.error, "err"); }
          return;
        }
        const pcm = new Float32Array(ev.data);
        const buf = ctx.createBuffer(1, pcm.length, 48000);
        buf.copyToChannel(pcm, 0);
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(ctx.destination);
        playHead = Math.max(playHead, ctx.currentTime + 0.03);
        src.start(playHead);
        playHead += buf.duration;
        sources.push(src);
        // mức âm lượng cho thanh đo
        const step = Math.max(1, Math.floor(pcm.length / 8));
        for (let i = 0; i < pcm.length; i += step) {
          let m = 0;
          for (let j = i; j < Math.min(pcm.length, i + step); j++) m = Math.max(m, Math.abs(pcm[j]));
          const at = (playHead - buf.duration + (i / pcm.length) * buf.duration - ctx.currentTime) * 1000;
          setTimeout(() => { levels.push(m); levels.shift(); drawMeter(); }, Math.max(0, at));
        }
      };
      ws.onclose = () => { ws = null; };
    });
  }

  let lastText = "";
  function addHistory(ms) {
    const h = $("#tt-history");
    if (h.querySelector("p")) h.innerHTML = "";
    const b = document.createElement("button");
    b.type = "button";
    b.innerHTML = `<span></span><span class="ms">${ms} ms</span>`;
    b.firstChild.textContent = lastText;
    b.addEventListener("click", () => say(b.firstChild.textContent));
    h.prepend(b);
    while (h.children.length > 12) h.lastChild.remove();
  }

  async function say(textValue) {
    const textv = (textValue ?? $("#tt-text").value).trim();
    if (!textv) return;
    ctx ??= new AudioContext({ sampleRate: 48000 });
    await ctx.resume();
    try { await connect(); } catch (err) { toast(err.message, "err"); return; }
    stop(false);
    lastText = textv;
    sentAt = performance.now();
    $("#tt-state").textContent = "đang nói";
    $("#tt-first").textContent = "…";
    ws.send(JSON.stringify({ text: textv, language: lang.value, voice: picker.value, emotion: $("#tt-emo").value, speed: +$("#tt-speed").value }));
    if (textValue == null) $("#tt-text").value = "";
  }
  function stop(label = true) {
    sources.forEach((s) => { try { s.stop(); } catch { /* đã dừng */ } });
    sources = [];
    playHead = 0;
    if (label) $("#tt-state").textContent = "đã dừng";
  }
  $("#tt-go").addEventListener("click", () => say());
  $("#tt-stop").addEventListener("click", () => stop());
  $("#tt-text").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); say(); } });
  void sentAt;
}

// ── 5. Kho giọng ────────────────────────────────────────────────────────────
function initLibrary() {
  let lib = { voices: [], max: 10 };
  let selected = null;
  let recorder = null, recKey = null;
  const dialect = seg("kg-dialect");
  const gender = seg("kg-gender");
  const player = new Audio();
  const SLOT_KEYS = [...STATE.emotions.map((e) => ({ key: e.key, label: e.label, en: false })), { key: "trung_tinh", label: "Tiếng Anh · trung tính", en: true }];

  async function load() {
    lib = await api.get("/api/library");
    if (!lib.voices.some((v) => v.id === selected)) selected = lib.voices[0]?.id || null;
    $("#kg-count").textContent = `${lib.voices.length}/${lib.max}`;
    $("#kg-mine").innerHTML = lib.voices.map((v) => `<button type="button" class="voice-opt" data-id="${esc(v.id)}" aria-selected="${v.id === selected}">${avatar(v.name, `voice:${v.id}`, v.gender, v.avatar)}<span style="min-width:0"><span class="name">${esc(v.name)}</span>${metaHTML({ kind: "mine", gender: v.gender, region: v.dialect, clips: v.clips })}</span></button>`).join("")
      || `<p class="hint">Chưa có giọng nào. Tạo giọng bên dưới, rồi thêm một đoạn nói 5–10 giây.</p>`;
    $("#kg-new button[type=submit]").disabled = lib.voices.length >= lib.max;
    renderDetail();
  }

  // Dải chọn nhân vật: ưu tiên nhân vật cùng giới tính, rồi đến nhân vật còn lại.
  function avatarChoices(v) {
    const sex = v.gender === "nu" || v.gender === "female" ? "nu" : v.gender === "nam" || v.gender === "male" ? "nam" : "";
    const first = sex ? AVATAR_POOL[sex] : [...AVATAR_POOL.nam, ...AVATAR_POOL.nu];
    const rest = sex ? AVATAR_POOL[sex === "nam" ? "nu" : "nam"] : [];
    return [...first, ...rest].map((a) => `<button type="button" class="avatar-pick" data-a="${a}" role="radio" aria-checked="${v.avatar_id === a}" aria-label="Nhân vật ${a}">
      <img src="${avatarUrl(a)}" alt="" loading="lazy"></button>`).join("");
  }

  function renderDetail() {
    const v = lib.voices.find((x) => x.id === selected);
    const box = $("#kg-detail");
    if (!v) {
      box.innerHTML = `<h2>Giọng của bạn</h2><p class="hint" style="margin-top:8px">Mỗi giọng cần ít nhất một đoạn mẫu <b>trung tính</b> dài 5–10 giây. Thêm mẫu cho từng cảm xúc (đọc một câu vui bằng giọng vui…) để cảm xúc rõ hơn. Bạn có thể thu ngay tại đây hoặc tải file lên.</p>`;
      return;
    }
    const has = (k, en) => v.clips.find((c) => c.key === (en ? `en_${k}` : k));
    box.innerHTML = `
      <div class="panel-head"><div class="cast-name">${avatar(v.name, `voice:${v.id}`, v.gender, v.avatar)}<div><h2>${esc(v.name)}</h2>${metaHTML({ gender: v.gender, region: v.dialect })}</div>
          <div class="seg" role="group" aria-label="Giới tính của giọng" id="kg-vgender" style="margin-left:var(--sp-3)">
            <button type="button" data-v="nam" aria-pressed="${v.gender === "nam" || v.gender === "male"}"><svg class="icon icon-xs sex nam" aria-hidden="true"><use href="/icons.svg#i-mars"/></svg> Nam</button>
            <button type="button" data-v="nu" aria-pressed="${v.gender === "nu" || v.gender === "female"}"><svg class="icon icon-xs sex nu" aria-hidden="true"><use href="/icons.svg#i-venus"/></svg> Nữ</button></div></div>
        <div class="toolbar"><button class="btn" type="button" id="kg-preview"><svg class="icon"><use href="/icons.svg#i-headphones"/></svg>Nghe thử</button>
        <button class="btn danger" type="button" id="kg-delete"><svg class="icon"><use href="/icons.svg#i-trash-2"/></svg>Xoá giọng</button></div></div>
      <div class="stack">
        <div class="meter" id="kg-meter" ${recKey ? "" : "hidden"}><i></i></div>
        <div class="slots">${SLOT_KEYS.map((s) => {
          const c = has(s.key, s.en);
          const k = s.en ? `en_${s.key}` : s.key;
          return `<div class="slot ${c ? "filled" : ""}" data-k="${k}" data-emo="${s.key}" data-en="${s.en}">
            <div class="slot-head"><span>${esc(s.label)}</span><span class="slot-state">${c ? "đã có" : s.key === "trung_tinh" && !s.en ? "bắt buộc" : "chưa có"}</span></div>
            <div class="slot-actions">
              ${c ? `<button class="btn" type="button" data-act="play" aria-label="Nghe mẫu ${esc(s.label)}"><svg class="icon icon-sm"><use href="/icons.svg#i-play"/></svg></button>` : ""}
              <button class="btn ${recKey === k ? "rec live" : ""}" type="button" data-act="rec"><svg class="icon icon-sm"><use href="/icons.svg#i-mic"/></svg>${recKey === k ? "Dừng" : "Thu"}</button>
              <label class="btn"><svg class="icon icon-sm"><use href="/icons.svg#i-upload"/></svg>Tải lên<input type="file" accept="audio/*" class="sr-only" data-act="file"></label>
              ${c ? `<button class="btn danger" type="button" data-act="del" aria-label="Xoá mẫu ${esc(s.label)}"><svg class="icon icon-sm"><use href="/icons.svg#i-trash-2"/></svg></button>` : ""}
            </div></div>`;
        }).join("")}</div>
        <div class="field"><span class="label">Nhân vật đại diện</span>
          <div class="avatar-grid" role="radiogroup" aria-label="Chọn nhân vật đại diện">${avatarChoices(v)}</div></div>
        <div id="kg-prev-out"></div>
        <details><summary class="section-label" style="cursor:pointer">Mô hình fine-tune của giọng này</summary>
          <div class="toolbar" style="margin-top:8px"><input type="text" id="kg-backbone" value="${esc(v.backbone)}" placeholder="Đường dẫn thư mục merged sau khi fine-tune" style="flex:1"><button class="btn" type="button" id="kg-backbone-save">Lưu</button></div></details>
      </div>`;
    seg("kg-vgender", async (g) => { await api.patch(`/api/library/${v.id}`, { gender: g }); load(); });
    $(".avatar-grid", box).addEventListener("click", async (e) => {
      const b = e.target.closest("button[data-a]");
      if (!b) return;
      await api.patch(`/api/library/${v.id}`, { avatar: b.dataset.a });
      load();
    });
    let confirm = false;
    $("#kg-delete").addEventListener("click", async (e) => {
      if (!confirm) { confirm = true; e.currentTarget.lastChild.textContent = "Bấm lần nữa để xoá"; return; }
      await api.del(`/api/library/${v.id}`);
      toast(`Đã xoá giọng ${v.name}`);
      selected = null;
      load();
    });
    $("#kg-preview").addEventListener("click", async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      try {
        const r = await runJob("/api/jobs/preview-voice", { voice: `voice:${v.id}` });
        const t = new Tape($("#kg-prev-out"), { sentences: false });
        t.load(r);
        t.audio.play().catch(() => {});
      } catch (err) { toast(err.message, "err"); } finally { btn.disabled = false; }
    });
    $("#kg-backbone-save").addEventListener("click", async () => {
      try { await api.patch(`/api/library/${v.id}`, { backbone: $("#kg-backbone").value.trim() }); toast("Đã lưu."); } catch (err) { toast(err.message, "err"); }
    });
  }

  async function upload(v, slot, blob, filename) {
    const form = new FormData();
    form.append("file", blob, filename);
    form.append("emotion", slot.dataset.emo);
    form.append("english", slot.dataset.en);
    try {
      const r = await api.upload(`/api/library/${v}/clips`, form);
      toast(r.warnings.length ? r.warnings[0] : "Đã lưu mẫu.", r.warnings.length ? "err" : "ok");
    } catch (err) { toast(err.message, "err"); }
    load();
  }

  $("#kg-detail").addEventListener("click", async (e) => {
    const b = e.target.closest("[data-act]");
    const slot = e.target.closest(".slot");
    if (!b || !slot || b.dataset.act === "file") return;
    const k = slot.dataset.k;
    if (b.dataset.act === "play") { player.src = `/api/library/${selected}/clips/${k}?t=${Date.now()}`; player.play(); }
    if (b.dataset.act === "del") { await api.del(`/api/library/${selected}/clips/${k}`); load(); }
    if (b.dataset.act === "rec") {
      if (recorder?.recording) {
        const blob = await recorder.stop();
        recKey = null;
        await upload(selected, slot, blob, "mau.webm");
      } else {
        recorder = new Recorder({ onLevel: (lv) => { const m = $("#kg-meter"); m?.style.setProperty("--lv", String(Math.min(1, lv))); m?.classList.toggle("hot", lv > 0.97); } });
        try { await recorder.start(); recKey = k; renderDetail(); } catch { toast("Không mở được micro. Kiểm tra quyền micro của cửa sổ.", "err"); }
      }
    }
  });
  $("#kg-detail").addEventListener("change", (e) => {
    if (e.target.dataset.act !== "file" || !e.target.files[0]) return;
    upload(selected, e.target.closest(".slot"), e.target.files[0], e.target.files[0].name);
  });
  $("#kg-mine").addEventListener("click", (e) => {
    const b = e.target.closest(".voice-opt");
    if (b) { selected = b.dataset.id; load(); }
  });
  $("#kg-new").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const v = await api.post("/api/library", { name: $("#kg-name").value, dialect: dialect.value, gender: gender.value });
      selected = v.id;
      $("#kg-name").value = "";
      toast(`Đã tạo giọng ${v.name}. Thêm đoạn mẫu trung tính để dùng.`);
      load();
    } catch (err) { toast(err.message, "err"); }
  });

  // giọng có sẵn
  let filter = "";
  async function presets() {
    const { voices } = await api.get("/api/voices?language=vi&engine=auto");
    const list = voices.filter((v) => v.kind === "preset" && (!filter || v.region === filter));
    $("#kg-presets").innerHTML = list.map((v) => `<div class="preset-row">${avatar(v.label, v.value, v.gender, v.avatar)}<span><span class="name">${esc(v.label)}</span>${metaHTML(v)}</span>
      <button class="btn ghost icon-only" type="button" data-v="${esc(v.value)}" aria-label="Nghe thử ${esc(v.label)}"><svg class="icon"><use href="/icons.svg#i-play"/></svg></button></div>`).join("");
  }
  $("#kg-filter").addEventListener("click", (e) => {
    const c = e.target.closest(".chip");
    if (!c) return;
    filter = c.dataset.v;
    $$("#kg-filter .chip").forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
    presets();
  });
  $("#kg-presets").addEventListener("click", async (e) => {
    const b = e.target.closest("button[data-v]");
    if (!b) return;
    b.disabled = true;
    b.innerHTML = `<svg class="icon spin"><use href="/icons.svg#i-loader-circle"/></svg>`;
    try {
      const r = await runJob("/api/jobs/preview-voice", { voice: b.dataset.v });
      player.src = r.audio_url;
      player.play();
    } catch (err) { toast(err.message, "err"); }
    b.disabled = false;
    b.innerHTML = `<svg class="icon"><use href="/icons.svg#i-play"/></svg>`;
  });
  onShow["kho-giong"] = () => { load(); presets(); };
}

// ── 6. Phòng thu ────────────────────────────────────────────────────────────
async function initStudio() {
  const { items, groups } = await api.get("/api/recording/script");
  let idx = 0, done = new Set(), recorder = null;
  const session = $("#pt-session");
  session.value = store.get("pt-session", "giong-cua-toi");
  const dialect = seg("pt-dialect");
  const player = new Audio();
  $("#pt-jump").innerHTML = items.map((it, i) => `<option value="${i}">${it.id} · ${esc(it.text.slice(0, 48))}</option>`).join("");
  range("ft-epochs", (v) => String(v));
  $("#ft-status").textContent = STATE.finetune.ok ? "Bộ fine-tune đã sẵn sàng" : STATE.finetune.message;

  async function loadSession() {
    store.set("pt-session", session.value);
    try {
      const s = await api.get(`/api/recording/${encodeURIComponent(session.value || "giong-cua-toi")}`);
      done = new Set(s.recorded);
      const mins = s.stats.seconds / 60;
      $("#pt-summary").textContent = `Đã thu ${s.stats.done}/${s.stats.total} câu · ${mins.toFixed(1)} phút. ` +
        (mins >= 10 ? "Đủ dữ liệu để fine-tune." : `Clone tức thì chỉ cần vài câu; fine-tune cần thêm khoảng ${Math.ceil(10 - mins)} phút.`);
      $("#pt-groups").innerHTML = Object.entries(s.stats.groups).map(([g, [a, b]]) => `<div class="group-bar"><div class="row"><span>${esc(groups[g] || g)}</span><span class="num muted">${a}/${b}</span></div><div class="progress"><i style="--p:${b ? a / b : 0}"></i></div></div>`).join("");
    } catch (err) { toast(err.message, "err"); }
    show();
  }
  function show() {
    const it = items[idx];
    $("#pt-text").textContent = it.text;
    $("#pt-pos").textContent = `Câu ${idx + 1}/${items.length}`;
    $("#pt-group").textContent = groups[it.group] || it.group;
    $("#pt-emo").textContent = `Cảm xúc: ${it.emotion_label}`;
    $("#pt-done").innerHTML = done.has(it.id) ? `<span style="color:var(--ok)">đã thu</span>` : "chưa thu";
    $("#pt-jump").value = String(idx);
    $("#pt-play").disabled = !done.has(it.id);
    $("#pt-del").disabled = !done.has(it.id);
  }
  const move = (d) => { idx = (idx + d + items.length) % items.length; $("#pt-msg").innerHTML = ""; show(); };
  const nextMissing = () => {
    for (let k = 1; k <= items.length; k++) { const j = (idx + k) % items.length; if (!done.has(items[j].id)) { idx = j; break; } }
    show();
  };
  $("#pt-prev").addEventListener("click", () => move(-1));
  $("#pt-next").addEventListener("click", () => move(1));
  $("#pt-next-missing").addEventListener("click", nextMissing);
  $("#pt-jump").addEventListener("change", (e) => { idx = +e.target.value; show(); });
  session.addEventListener("change", loadSession);
  $("#pt-play").addEventListener("click", () => { player.src = `/api/recording/${encodeURIComponent(session.value)}/takes/${items[idx].id}?t=${Date.now()}`; player.play(); });
  $("#pt-del").addEventListener("click", async () => { await api.del(`/api/recording/${encodeURIComponent(session.value)}/takes/${items[idx].id}`); loadSession(); });

  async function toggleRec() {
    const btn = $("#pt-rec");
    if (recorder?.recording) {
      const blob = await recorder.stop();
      btn.classList.remove("live");
      btn.querySelector("span").textContent = "Thu";
      const form = new FormData();
      form.append("file", blob, "take.webm");
      try {
        const r = await api.upload(`/api/recording/${encodeURIComponent(session.value)}/takes/${items[idx].id}`, form);
        $("#pt-msg").innerHTML = `<p class="hint" style="color:var(--ok)">Đã lưu ${items[idx].id} (${r.duration.toFixed(1)} s).</p>` + r.warnings.map((w) => `<p class="note"><svg class="icon icon-sm"><use href="/icons.svg#i-triangle-alert"/></svg><span>${esc(w)}</span></p>`).join("");
        done.add(items[idx].id);
        await loadSession();
        nextMissing();
      } catch (err) { $("#pt-msg").innerHTML = `<p class="note"><svg class="icon icon-sm"><use href="/icons.svg#i-triangle-alert"/></svg><span>${esc(err.message)}</span></p>`; }
      return;
    }
    recorder = new Recorder({ onLevel: (lv) => { $("#pt-meter").style.setProperty("--lv", String(Math.min(1, lv))); $("#pt-meter").classList.toggle("hot", lv > 0.97); } });
    try {
      await recorder.start();
      btn.classList.add("live");
      btn.querySelector("span").textContent = "Dừng & lưu";
      $("#pt-meter-hint").textContent = "Đang thu. Vạch nên dao động khoảng giữa; chuyển đỏ là quá to.";
    } catch { toast("Không mở được micro. Kiểm tra quyền micro của cửa sổ.", "err"); }
  }
  $("#pt-rec").addEventListener("click", toggleRec);
  document.addEventListener("keydown", (e) => {
    if ($("#view-phong-thu").hidden || e.code !== "Space" || ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
    e.preventDefault();
    toggleRec();
  });

  $("#pt-build").addEventListener("click", async () => {
    try {
      const r = await api.post(`/api/recording/${encodeURIComponent(session.value)}/build-voice`, { name: $("#pt-vname").value, dialect: dialect.value });
      $("#pt-build-msg").textContent = r.notes.join(" ");
      toast("Đã tạo giọng trong Kho giọng.");
    } catch (err) { $("#pt-build-msg").textContent = err.message; }
  });
  $("#ft-go").addEventListener("click", async () => {
    const log = $("#ft-log");
    log.hidden = false;
    log.textContent = "Đang bắt đầu…";
    $("#ft-go").disabled = true;
    try {
      const r = await runJob("/api/jobs/finetune", { session: session.value, run: $("#ft-run").value, epochs: +$("#ft-epochs").value, rank: +$("#ft-rank").value, low_vram: $("#ft-low").checked },
        (j) => { log.textContent = j.log.join("\n") || j.message; log.scrollTop = log.scrollHeight; });
      log.textContent += `\n\nXong. Vào Kho giọng → chọn giọng → "Mô hình fine-tune của giọng này" và dán:\n${r.merged}`;
    } catch (err) { log.textContent += `\n\n${err.message}`; } finally { $("#ft-go").disabled = false; }
  });
  onShow["phong-thu"] = async () => {
    const { sessions } = await api.get("/api/recording/sessions");
    $("#pt-sessions").innerHTML = sessions.map((s) => `<option value="${esc(s)}">`).join("");
    loadSession();
  };
}

// ── 7. So sánh ──────────────────────────────────────────────────────────────
function initCompare() {
  const lang = seg("ss-lang", () => picker.refresh(lang.value));
  const picker = new VoicePicker($("#ss-voice"));
  fillSelect($("#ss-emo"), STATE.emotions);
  fillSelect($("#ss-gvoice"), STATE.gemini_voices.map((g) => ({ key: g, label: g })), STATE.settings.gemini_voice || "Kore");
  onShow["so-sanh"] = () => picker.refresh(lang.value, "auto", STATE.default_preset);
  $("#ss-go").addEventListener("click", async () => {
    busy("ss", true, "Đang tạo…");
    const out = $("#ss-out");
    try {
      const r = await runJob("/api/jobs/compare", { text: $("#ss-text").value, language: lang.value, voice: picker.value, gemini_voice: $("#ss-gvoice").value, emotion: $("#ss-emo").value }, jobProgress("ss"));
      out.innerHTML = r.items.map((_, i) => `<div class="panel stack"><h2>${esc(r.items[i].name)}</h2><div data-i="${i}"></div></div>`).join("");
      r.items.forEach((it, i) => {
        const box = $(`[data-i="${i}"]`, out);
        if (it.ok) new Tape(box, { sentences: false }).load(it);
        else errorBox(box, it.error);
      });
    } catch (err) { toast(err.message, "err"); } finally { busy("ss", false); }
  });
}

// ── 8. Cài đặt ──────────────────────────────────────────────────────────────
function initSettings() {
  const s = STATE.settings;
  const save = async (patch) => {
    try {
      STATE.settings = await api.put("/api/settings", patch);
      $("#cd-saved").textContent = "Đã lưu";
      setTimeout(() => { $("#cd-saved").textContent = ""; }, 1800);
      keyHint();
    } catch (err) { toast(err.message, "err"); }
  };
  const bind = (id, key) => { const c = seg(id, (v) => save({ [key]: v })); c.set(s[key]); return c; };
  bind("cd-device", "device"); bind("cd-prec", "cpu_precision"); bind("cd-dialect", "dialect"); bind("cd-fmt", "output_format"); bind("cd-en", "english_engine");
  fillSelect($("#cd-enh"), STATE.enhance, s.enhance);
  fillSelect($("#cd-derev"), STATE.dereverb, s.dereverb);
  $("#cd-enh").addEventListener("change", (e) => save({ enhance: e.target.value }));
  $("#cd-derev").addEventListener("change", (e) => save({ dereverb: e.target.value }));
  $("#cd-ai").checked = !!s.ai_clean;
  $("#cd-ai").addEventListener("change", (e) => save({ ai_clean: e.target.checked }));
  $("#cd-lufs").value = s.target_lufs; $("#cd-sp").value = s.sentence_pause; $("#cd-pp").value = s.paragraph_pause;
  range("cd-lufs", (v) => `${v} LUFS`); range("cd-sp", (v) => `${v.toFixed(2)} s`); range("cd-pp", (v) => `${v.toFixed(2)} s`);
  for (const [id, key] of [["cd-lufs", "target_lufs"], ["cd-sp", "sentence_pause"], ["cd-pp", "paragraph_pause"]]) {
    $(`#${id}`).addEventListener("change", (e) => save({ [key]: +e.target.value }));
  }
  const keyHint = () => { $("#cd-key-hint").textContent = STATE.settings.has_gemini_key ? `Đã lưu key ${STATE.settings.gemini_key_hint}. Dán key mới để thay.` : "Chưa có key. Lấy miễn phí tại aistudio.google.com."; };
  keyHint();
  $("#cd-key").addEventListener("change", (e) => { if (e.target.value.trim()) { save({ gemini_api_key: e.target.value.trim() }); e.target.value = ""; } });
  if (s.gemini_model) $("#cd-gmodel").insertAdjacentHTML("beforeend", `<option value="${esc(s.gemini_model)}">${esc(s.gemini_model)}</option>`);
  $("#cd-gmodel").value = s.gemini_model || "";
  $("#cd-gmodel").addEventListener("change", (e) => save({ gemini_model: e.target.value }));
  $("#cd-gmodels").addEventListener("click", async () => {
    try {
      const { models } = await api.get("/api/gemini/models");
      $("#cd-gmodel").innerHTML = `<option value="">Tự chọn mới nhất</option>` + models.map((m) => `<option value="${esc(m)}">${esc(m)}</option>`).join("");
      $("#cd-gmodel").value = STATE.settings.gemini_model || "";
      toast(`Tìm thấy ${models.length} model đọc giọng.`);
    } catch (err) { toast(err.message, "err"); }
  });
  fillSelect($("#cd-gvoice"), STATE.gemini_voices.map((g) => ({ key: g, label: g })), s.gemini_voice);
  $("#cd-gvoice").addEventListener("change", (e) => save({ gemini_voice: e.target.value }));

  $("#cd-check").addEventListener("click", system);
  $("#cd-preload").addEventListener("click", async (e) => {
    const b = e.currentTarget; b.disabled = true;
    try { const r = await api.post("/api/preload"); toast(`Đã nạp lõi giọng (${r.backend}).`); system(); } catch (err) { toast(err.message, "err"); }
    b.disabled = false;
  });

  // từ điển
  const SECT = [["all", "Cả hai"], ["vi", "Tiếng Việt"], ["en", "English"]];
  const row = (r = ["all", "", ""]) => `<tr><td><select aria-label="Áp dụng cho">${SECT.map(([k, l]) => `<option value="${k}" ${k === r[0] ? "selected" : ""}>${l}</option>`).join("")}</select></td>
    <td><input type="text" value="${esc(r[1])}" aria-label="Từ gốc"></td><td><input type="text" value="${esc(r[2])}" aria-label="Cách đọc"></td>
    <td><button class="btn ghost icon-only" type="button" aria-label="Xoá dòng"><svg class="icon icon-sm"><use href="/icons.svg#i-x"/></svg></button></td></tr>`;
  async function loadLex() { const { rows } = await api.get("/api/lexicon"); $("#lx-rows").innerHTML = rows.map(row).join("") || row(); }
  $("#lx-add").addEventListener("click", () => { $("#lx-rows").insertAdjacentHTML("beforeend", row()); $("#lx-rows tr:last-child input").focus(); });
  $("#lx-rows").addEventListener("click", (e) => { if (e.target.closest("button")) e.target.closest("tr").remove(); });
  $("#lx-save").addEventListener("click", async () => {
    const rows = $$("#lx-rows tr").map((tr) => [$("select", tr).value, ...$$("input", tr).map((i) => i.value.trim())]).filter((r) => r[1] && r[2]);
    try { await api.put("/api/lexicon", { rows }); $("#lx-msg").textContent = `Đã lưu ${rows.length} từ.`; } catch (err) { toast(err.message, "err"); }
  });
  onShow["cai-dat"] = () => { loadLex(); system(); };
}

// ── 9. Cập nhật ─────────────────────────────────────────────────────────────
function initUpdate() {
  const setBadge = (on) => { $("#nav-update-badge").hidden = !on; };
  setBadge(!!STATE.update?.available);
  let lastInfo = null;

  function stateLine(kind, text) {
    $("#cn-state").innerHTML = `<span class="dot ${kind}"></span><span></span>`;
    $("#cn-state span:last-child").textContent = text;
  }

  function renderNotes(info) {
    const panel = $("#cn-notes-panel");
    if (!info || !info.available) { panel.hidden = true; return; }
    panel.hidden = false;
    $("#cn-notes-title").textContent = `Có gì mới trong ${info.latest}`;
    const notes = info.notes?.length ? info.notes : [{ version: info.latest, date: "", items: info.commits.map((c) => c.subject) }];
    $("#cn-notes").innerHTML = notes.map((n) => `<div><h3>Phiên bản ${esc(n.version)}<span class="hint">${esc(n.date)}</span></h3>
      <ul>${n.items.map((it) => `<li>${esc(it)}</li>`).join("")}</ul></div>`).join("");
  }

  function renderStatus(st) {
    $("#cn-version").textContent = st.version;
    $("#cn-last").textContent = st.last_check ? `Kiểm tra lần cuối: ${st.last_check}` : "";
    const avail = lastInfo ? lastInfo.available : st.cached?.available;
    if (!st.git) stateLine("bad", "Máy chưa cài Git — cần Git để cập nhật.");
    else if (!st.repo) stateLine("warn", "Chưa kết nối GitHub.");
    else if (avail) stateLine("warn", `Có bản mới ${lastInfo?.latest || st.cached.latest}`);
    else if (st.last_check) stateLine("ok", "Bạn đang dùng bản mới nhất");
    else stateLine("", "Chưa kiểm tra");
    $("#cn-apply").hidden = !avail;
    if (lastInfo?.available) $("#cn-apply span").textContent = `Cập nhật lên ${lastInfo.latest}`;
    setBadge(!!avail);
    $("#cn-connect").hidden = !st.git || st.repo;
    $("#cn-channel").innerHTML = st.repo
      ? `<div class="status-line"><span class="dot ok"></span><span>GitHub · nhánh main</span></div><div class="hint" style="word-break:break-all">${esc(st.remote || "")}</div><div class="hint num">Mã bản đang chạy: ${esc(st.commit || "")}</div>`
      : `<div class="hint">Chưa có kênh cập nhật.</div>`;
    const dc = st.data_changes || 0;
    $("#cn-sync-stats").innerHTML = `<span>Lần cuối: <b>${esc(st.last_sync || "chưa")}</b></span><span>Chưa gửi: <b>${dc}</b> thay đổi</span>`;
    $("#cn-sync").disabled = !st.repo;
    const hist = st.history || [];
    $("#cn-history").innerHTML = hist.length ? hist.map((h) => `<div class="history-row">
        <span class="dot ${h.ok ? "ok" : "bad"}" title="${h.ok ? "Thành công" : "Không thành công"}"></span>
        <span>${esc(h.from)} → ${esc(h.to)}${h.note ? ` <span class="hint">· ${esc(h.note)}</span>` : ""}</span>
        <span class="when">${esc(h.time)}</span></div>`).join("") : `<p class="hint">Chưa có lần cập nhật nào.</p>`;
    $("#cn-rollback").disabled = !hist.some((h) => h.ok && h.from_commit);
  }

  async function refresh() {
    try { renderStatus(await api.get("/api/update/status")); } catch (err) { stateLine("bad", err.message); }
  }

  async function check() {
    const b = $("#cn-check");
    b.disabled = true;
    stateLine("", "Đang hỏi GitHub…");
    try {
      lastInfo = await api.post("/api/update/check");
      renderNotes(lastInfo);
      if (!lastInfo.available) toast(lastInfo.data_only ? "Phần mềm đã mới nhất. Có dữ liệu mới từ máy khác — bấm Đồng bộ ngay." : "Bạn đang dùng bản mới nhất.");
    } catch (err) { toast(err.message, "err"); }
    b.disabled = false;
    refresh();
  }

  // Chờ phần mềm khởi động lại (boot_id đổi) rồi tải lại giao diện.
  async function waitRestart(oldBoot) {
    $("#cn-busy-msg").textContent = "Đang khởi động lại phần mềm…";
    for (let i = 0; i < 120; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      try {
        const st = await api.get("/api/state");
        if (st.boot_id !== oldBoot) { location.hash = "#cap-nhat"; location.reload(); return; }
      } catch { /* máy chủ đang khởi động lại */ }
    }
    $("#cn-busy-msg").textContent = "Phần mềm chưa khởi động lại được. Hãy đóng cửa sổ và mở lại VoxViet Studio từ biểu tượng trên Desktop (hoặc run.bat).";
  }

  async function runWithLog(url, label) {
    const log = $("#cn-log");
    log.hidden = false;
    log.textContent = "";
    busy("cn", true, label);
    $("#cn-check").disabled = true;
    const oldBoot = STATE.boot_id;
    try {
      const r = await runJob(url, {}, (j) => { setProg("cn", j.progress); log.textContent = j.log.join("\n"); log.scrollTop = log.scrollHeight; });
      if (r.restarting) { await waitRestart(oldBoot); return; }
    } catch (err) {
      log.textContent += `\n\n${err.message}`;
      toast(err.message, "err");
    }
    busy("cn", false);
    $("#cn-check").disabled = false;
    refresh();
  }

  $("#cn-check").addEventListener("click", check);
  $("#cn-apply").addEventListener("click", () => runWithLog("/api/jobs/update", "Đang cập nhật…"));
  let confirmRb = false;
  $("#cn-rollback").addEventListener("click", (e) => {
    if (!confirmRb) { confirmRb = true; e.currentTarget.lastChild.textContent = "Bấm lần nữa để quay lại"; return; }
    runWithLog("/api/jobs/rollback", "Đang quay lại phiên bản trước…");
  });
  $("#cn-sync").addEventListener("click", async () => {
    const b = $("#cn-sync"), log = $("#cn-sync-log");
    b.disabled = true;
    log.hidden = false;
    log.textContent = "Đang đồng bộ…";
    try {
      const r = await runJob("/api/jobs/sync", {}, (j) => { log.textContent = j.log.join("\n") || j.message; });
      toast(`Đã đồng bộ: gửi ${r.committed}, nhận ${r.pulled} thay đổi.`);
    } catch (err) { log.textContent += `\n${err.message}`; toast(err.message, "err"); }
    b.disabled = false;
    refresh();
  });
  $("#cn-connect").addEventListener("submit", async (e) => {
    e.preventDefault();
    try { renderStatus(await api.post("/api/update/connect", { url: $("#cn-url").value })); toast("Đã kết nối GitHub."); } catch (err) { toast(err.message, "err"); }
  });
  onShow["cap-nhat"] = refresh;
}

async function system() {
  try {
    const s = await api.get("/api/system");
    const core = STATE.engines.find((e) => e.id === "core");
    const lines = [
      s.gpu ? ["ok", `GPU ${s.gpu.name} · ${s.gpu.vram_gb} GB · CUDA ${s.gpu.cuda}`] : ["warn", "Không thấy GPU NVIDIA — chạy bằng CPU, chậm hơn."],
      core?.available ? ["ok", `Lõi giọng VoxViet: ${s.core_backend === "chưa nạp" ? "sẵn sàng (nạp khi đọc lần đầu)" : `đang chạy (${s.core_backend})`}`] : ["bad", core?.why || "Lõi giọng chưa sẵn sàng."],
      [s.ffmpeg ? "ok" : "bad", s.ffmpeg ? "ffmpeg có sẵn (đổi tốc độ, xuất MP3)" : "Thiếu ffmpeg — chạy lại install.bat"],
      ...STATE.engines.filter((e) => e.id !== "core" && e.id !== "mock").map((e) => [e.available ? "ok" : "", `${e.label}${e.available ? "" : ` — ${e.why}`}`]),
      ["", `Dữ liệu: ${s.data_dir}`],
    ];
    const box = $("#cd-sys");
    if (box) box.innerHTML = lines.map(([k, t]) => `<div class="status-line"><span class="dot ${k}"></span><span>${esc(t)}</span></div>`).join("");
    $("#core-dot").className = `dot ${core?.available ? (s.gpu ? "ok" : "warn") : "bad"}`;
    $("#core-status").textContent = core?.available ? `Lõi giọng · ${s.gpu ? "GPU" : "CPU"}` : "Lõi giọng chưa sẵn sàng";
  } catch { /* máy chủ đang bận */ }
}

// ── màn hình chào lần đầu: tải mô hình lõi giọng ──────────────────────────────
function initWelcome() {
  const box = $("#welcome");
  const show = () => { box.hidden = false; $("#wc-go").focus(); };
  if (!STATE.models_ready && !STATE.demo) show();
  $("#cd-models").hidden = STATE.models_ready || STATE.demo;
  $("#cd-models").addEventListener("click", show);
  $("#wc-later").addEventListener("click", () => { box.hidden = true; });

  const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
  $("#wc-go").addEventListener("click", async () => {
    const t0 = Date.now();
    const tick = setInterval(() => { $("#wc-time").textContent = fmt((Date.now() - t0) / 1000); }, 1000);
    $("#wc-actions").hidden = true;
    $("#wc-err").hidden = true;
    $("#wc-busy").hidden = false;
    $("#wc-log-box").hidden = false;
    $("#wc-mark").classList.add("live");
    const oldBoot = STATE.boot_id;
    try {
      await runJob("/api/jobs/download-models", {}, (j) => {
        if (j.message) $("#wc-msg").textContent = j.message;
        const log = $("#wc-log");
        log.textContent = j.log.join("\n");
        log.scrollTop = log.scrollHeight;
      });
      $("#wc-msg").textContent = "Tải xong — đang mở lại phần mềm…";
      for (let i = 0; i < 180; i++) {
        await new Promise((r) => setTimeout(r, 1000));
        try {
          const st = await api.get("/api/state");
          if (st.boot_id !== oldBoot) { location.reload(); return; }
        } catch { /* đang khởi động lại */ }
      }
      throw new Error("Phần mềm chưa mở lại được. Hãy đóng cửa sổ và mở lại VoxViet Studio.");
    } catch (err) {
      errorBox($("#wc-err"), err.message);
      $("#wc-err").hidden = false;
      $("#wc-busy").hidden = true;
      $("#wc-actions").hidden = false;
      $("#wc-go span").textContent = "Thử lại";
      $("#wc-mark").classList.remove("live");
    } finally {
      clearInterval(tick);
    }
  });
}

// Báo cho phần mềm biết cửa sổ này đang mở. Đóng hết cửa sổ → phần mềm tự tắt (chế độ ứng dụng).
// Mất kết nối (đang khởi động lại sau cập nhật) → tự nối lại.
function presence() {
  let ws = null;
  let wait = 1000;
  const open = () => {
    if (ws && ws.readyState <= 1) return;
    ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/presence`);
    ws.onopen = () => { wait = 1000; };
    ws.onclose = () => { ws = null; setTimeout(open, wait); wait = Math.min(wait * 1.5, 4000); };
  };
  open();
  document.addEventListener("visibilitychange", () => { if (!document.hidden) open(); });
}

// ── khởi động ───────────────────────────────────────────────────────────────
async function boot() {
  try {
    STATE = await api.get("/api/state");
  } catch {
    document.getElementById("main").innerHTML = `<div class="error-box" style="max-width:560px"><svg class="icon"><use href="/icons.svg#i-triangle-alert"/></svg><span>Không mở được phiên làm việc của VoxViet. Hãy đóng cửa sổ này và mở lại VoxViet Studio từ biểu tượng trên Desktop (hoặc run.bat).</span></div>`;
    return;
  }
  presence();
  $("#version").textContent = `VoxViet Studio ${STATE.version}${STATE.demo ? " · chạy thử" : ""}`;
  initDoc(); initDialogue(); initDub(); initLive(); initLibrary(); initSettings();
  await initStudio().catch((e) => toast(e.message, "err"));
  initCompare();
  initUpdate();
  initWelcome();
  window.addEventListener("hashchange", route);
  route();
  system();
}
boot();
