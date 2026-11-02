// Ô chọn giọng: giọng của bạn + giọng có sẵn theo vùng. Mỗi giọng một chữ cái và màu cố định.
import { api, esc } from "./api.js";

const REGION = { bac: "miền Bắc", trung: "miền Trung", nam: "miền Nam" };
const GENDER = { nam: "Nam", nu: "Nữ", male: "Nam", female: "Nữ" };

export function hueOf(key) {
  let h = 0;
  for (const ch of key) h = (h * 31 + ch.codePointAt(0)) >>> 0;
  return (h * 137.508) % 360; // góc vàng: các giọng cạnh nhau lệch màu rõ
}

export function avatar(label, key) {
  const words = (label || "?").trim().split(/\s+/);
  const letter = (words.length > 1 ? words[0][0] + words[words.length - 1][0] : words[0][0]).toUpperCase();
  return `<span class="avatar" style="background:oklch(0.80 0.09 ${hueOf(key).toFixed(0)})" aria-hidden="true">${esc(letter)}</span>`;
}

export function voiceMeta(v) {
  if (v.kind === "mine") return `Giọng của bạn · ${REGION[v.region] || ""}${v.clips?.length ? ` · ${v.clips.length} mẫu` : " · chưa có mẫu"}`;
  if (v.description) return v.description;
  return [GENDER[v.gender], REGION[v.region], v.style].filter(Boolean).join(" · ");
}

export class VoicePicker {
  constructor(root, { onChange } = {}) {
    this.root = root;
    this.onChange = onChange;
    this.voices = [];
    this.value = null;
    this.open = false;
    root.innerHTML = `
      <button type="button" class="voice-current" aria-expanded="false"></button>
      <div class="voice-picker" hidden>
        <div class="chips" style="margin-top:var(--sp-2)">
          <button class="chip" type="button" data-f="" aria-pressed="true">Tất cả</button>
          <button class="chip" type="button" data-f="mine" aria-pressed="false">Của bạn</button>
          <button class="chip" type="button" data-f="bac" aria-pressed="false">Bắc</button>
          <button class="chip" type="button" data-f="trung" aria-pressed="false">Trung</button>
          <button class="chip" type="button" data-f="nam" aria-pressed="false">Nam</button>
        </div>
        <div class="voice-list" role="listbox" aria-label="Danh sách giọng"></div>
      </div>`;
    this.btn = root.querySelector(".voice-current");
    this.panel = root.querySelector(".voice-picker");
    this.list = root.querySelector(".voice-list");
    this.filter = "";
    this.btn.addEventListener("click", () => this.toggle());
    root.querySelectorAll(".chip").forEach((c) => c.addEventListener("click", () => {
      this.filter = c.dataset.f;
      root.querySelectorAll(".chip").forEach((x) => x.setAttribute("aria-pressed", String(x === c)));
      this.renderList();
    }));
    this.list.addEventListener("click", (e) => {
      const opt = e.target.closest(".voice-opt");
      if (!opt) return;
      this.set(opt.dataset.v, true);
      this.toggle(false);
    });
  }

  async refresh(language = "vi", engine = "auto", fallback = null) {
    const { voices } = await api.get(`/api/voices?language=${language}&engine=${engine}`);
    this.voices = voices;
    const keep = voices.find((v) => v.value === this.value);
    this.set(keep ? this.value : (voices.find((v) => v.value === fallback)?.value || voices[0]?.value || null), false);
  }

  set(value, notify) {
    this.value = value;
    const v = this.voices.find((x) => x.value === value);
    this.btn.innerHTML = v
      ? `${avatar(v.label, v.value)}<span style="flex:1;min-width:0"><span style="display:block;font-weight:500">${esc(v.label)}</span><span class="meta">${esc(voiceMeta(v))}</span></span><svg class="icon icon-sm"><use href="/icons.svg#i-chevron-down"/></svg>`
      : `<span class="muted">Chưa có giọng</span>`;
    this.renderList();
    if (notify) this.onChange?.(value, v);
  }

  get current() { return this.voices.find((x) => x.value === this.value) || null; }

  toggle(force) {
    this.open = force ?? !this.open;
    this.panel.hidden = !this.open;
    this.btn.setAttribute("aria-expanded", String(this.open));
  }

  renderList() {
    const f = this.filter;
    const mine = this.voices.filter((v) => v.kind === "mine" && (!f || f === "mine" || f === v.region));
    const presets = this.voices.filter((v) => v.kind !== "mine" && f !== "mine" && (!f || f === v.region));
    const row = (v) => `<button type="button" class="voice-opt" role="option" data-v="${esc(v.value)}" aria-selected="${v.value === this.value}">
        ${avatar(v.label, v.value)}<span><span class="name">${esc(v.label)}</span><br><span class="meta">${esc(voiceMeta(v))}</span></span></button>`;
    this.list.innerHTML =
      (mine.length ? `<div class="list-label">Giọng của bạn</div>${mine.map(row).join("")}` : "") +
      (presets.length ? `<div class="list-label">Giọng có sẵn</div>${presets.map(row).join("")}` : "") ||
      `<p class="hint" style="padding:8px 10px">Không có giọng nào trong nhóm này.</p>`;
  }
}
