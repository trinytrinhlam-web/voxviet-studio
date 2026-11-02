// Băng câu: dạng sóng của bản đọc, chia theo từng câu. Bấm một câu để nghe đúng câu đó.
import { esc, fmtTime } from "./api.js";

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
let audioCtx;

export class Tape {
  constructor(root, { sentences = true, downloads = null } = {}) {
    this.root = root;
    this.showSentences = sentences;
    this.downloads = downloads;
    this.audio = new Audio();
    this.audio.preload = "auto";
    this.peaks = null;
    this.subs = [];
    this.stopAt = null;
    this.raf = 0;
    this.audio.addEventListener("play", () => this.loop());
    this.audio.addEventListener("pause", () => { cancelAnimationFrame(this.raf); this.sync(); });
    this.audio.addEventListener("ended", () => { this.stopAt = null; this.sync(); });
    this.ro = new ResizeObserver(() => this.draw());
  }

  load(result, extra = "") {
    this.subs = result.subtitles || [];
    this.stopAt = null;
    this.audio.src = result.audio_url;
    this.root.innerHTML = `
      <div class="transport">
        <button class="play-btn" type="button" aria-label="Phát"><svg class="icon"><use href="/icons.svg#i-play"/></svg></button>
        <div class="tape" role="slider" tabindex="0" aria-label="Vị trí phát" aria-valuemin="0" aria-valuemax="${Math.round(result.duration || 0)}" aria-valuenow="0">
          <canvas></canvas><div class="tape-loading">Đang dựng dạng sóng…</div>
        </div>
        <span class="time"><span class="cur">0:00</span> / ${fmtTime(result.duration)}</span>
      </div>
      ${result.rtf != null ? `<div class="stats"><span>Độ dài <b>${result.duration.toFixed(1)} s</b></span><span>Thời gian tạo <b>${result.elapsed.toFixed(1)} s</b></span><span>Nhanh gấp <b>${(1 / Math.max(result.rtf, 0.001)).toFixed(1)}×</b> thời gian nghe</span><span><b>${this.subs.length}</b> câu</span></div>` : ""}
      ${(result.warnings || []).length ? `<div class="notes">${result.warnings.map((w) => `<p class="note"><svg class="icon icon-sm"><use href="/icons.svg#i-triangle-alert"/></svg><span>${esc(w)}</span></p>`).join("")}</div>` : ""}
      ${extra}
      ${this.showSentences && this.subs.length ? `<div class="sentences">${this.subs.map((s, i) => `<button class="sentence" type="button" data-i="${i}"><span class="t">${fmtTime(s.start)}</span><span>${esc(s.text)}</span></button>`).join("")}</div>` : ""}`;
    this.btn = this.root.querySelector(".play-btn");
    this.tape = this.root.querySelector(".tape");
    this.canvas = this.root.querySelector("canvas");
    this.cur = this.root.querySelector(".cur");
    this.btn.addEventListener("click", () => this.toggle());
    this.tape.addEventListener("click", (e) => {
      const r = this.tape.getBoundingClientRect();
      this.seek(((e.clientX - r.left) / r.width) * (this.audio.duration || result.duration), null);
    });
    this.tape.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") this.seek(this.audio.currentTime + 2, null);
      else if (e.key === "ArrowLeft") this.seek(this.audio.currentTime - 2, null);
      else if (e.key === " ") { e.preventDefault(); this.toggle(); }
    });
    this.root.querySelectorAll(".sentence").forEach((b) => b.addEventListener("click", () => {
      const s = this.subs[+b.dataset.i];
      this.seek(s.start, s.end);
    }));
    this.ro.disconnect();
    this.ro.observe(this.tape);
    if (this.downloads) {
      this.downloads.innerHTML = `
        <a class="btn ghost" href="${result.audio_url}" download><svg class="icon"><use href="/icons.svg#i-download"/></svg>Âm thanh</a>
        ${result.srt_url ? `<a class="btn ghost" href="${result.srt_url}" download><svg class="icon"><use href="/icons.svg#i-download"/></svg>Phụ đề .srt</a>` : ""}`;
    }
    this.decode(result.audio_url);
  }

  async decode(url) {
    try {
      audioCtx ??= new AudioContext();
      const buf = await audioCtx.decodeAudioData(await (await fetch(url)).arrayBuffer());
      const ch = buf.getChannelData(0);
      const n = 1200;
      const step = Math.max(1, Math.floor(ch.length / n));
      const peaks = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        let m = 0;
        for (let j = i * step, e = Math.min(ch.length, j + step); j < e; j++) m = Math.max(m, Math.abs(ch[j]));
        peaks[i] = m;
      }
      this.peaks = peaks;
      this.duration = buf.duration;
    } catch {
      this.peaks = null;
    }
    this.root.querySelector(".tape-loading")?.remove();
    this.draw();
  }

  toggle() {
    if (this.audio.paused) { this.stopAt = null; this.audio.play(); } else this.audio.pause();
  }

  seek(t, stopAt) {
    this.audio.currentTime = Math.max(0, t);
    this.stopAt = stopAt;
    this.audio.play();
  }

  loop() {
    cancelAnimationFrame(this.raf);
    const tick = () => {
      if (this.stopAt != null && this.audio.currentTime >= this.stopAt) {
        this.audio.pause();
        this.stopAt = null;
      }
      this.sync();
      if (!this.audio.paused) this.raf = requestAnimationFrame(tick);
    };
    this.raf = requestAnimationFrame(tick);
  }

  sync() {
    if (!this.btn) return;
    const playing = !this.audio.paused;
    this.btn.innerHTML = `<svg class="icon"><use href="/icons.svg#i-${playing ? "pause" : "play"}"/></svg>`;
    this.btn.setAttribute("aria-label", playing ? "Tạm dừng" : "Phát");
    const t = this.audio.currentTime;
    this.cur.textContent = fmtTime(t);
    this.tape.setAttribute("aria-valuenow", String(Math.round(t)));
    const idx = this.subs.findIndex((s) => t >= s.start && t < s.end + 0.05);
    this.root.querySelectorAll(".sentence").forEach((b) => b.setAttribute("aria-current", String(+b.dataset.i === idx)));
    this.draw();
  }

  draw() {
    const c = this.canvas;
    if (!c) return;
    const dpr = window.devicePixelRatio || 1;
    const w = c.clientWidth, h = c.clientHeight;
    if (!w || !h) return;
    c.width = Math.round(w * dpr);
    c.height = Math.round(h * dpr);
    const g = c.getContext("2d");
    g.scale(dpr, dpr);
    g.clearRect(0, 0, w, h);
    const dur = this.duration || this.audio.duration || 1;
    const t = this.audio.currentTime || 0;
    const active = this.subs.find((s) => t >= s.start && t < s.end + 0.05);
    // vùng của câu đang phát
    if (active && !this.audio.paused) {
      g.fillStyle = css("--surface-2");
      g.fillRect((active.start / dur) * w, 0, ((active.end - active.start) / dur) * w, h);
    }
    // ranh giới câu
    g.fillStyle = css("--line");
    for (const s of this.subs) g.fillRect(Math.round((s.start / dur) * w), h - 6, 1, 6);
    if (!this.peaks) return;
    const bars = Math.floor(w / 3);
    const mid = h / 2;
    const accent = css("--accent"), rest = css("--faint");
    for (let i = 0; i < bars; i++) {
      const p = this.peaks[Math.floor((i / bars) * this.peaks.length)] || 0;
      const bh = Math.max(1.5, Math.min(1, p * 1.25) * (h - 16));
      g.fillStyle = (i / bars) * dur <= t ? accent : rest;
      g.fillRect(i * 3, mid - bh / 2, 2, bh);
    }
  }
}
