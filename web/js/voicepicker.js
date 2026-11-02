// Ô chọn giọng: giọng của bạn + giọng có sẵn theo vùng. Ảnh đại diện theo giới tính, nhãn phong cách có icon.
import { api, esc } from "./api.js";

const REGION = { bac: "miền Bắc", trung: "miền Trung", nam: "miền Nam" };
// Giới tính: chấp nhận cả mã cũ (male/female) lẫn mã của catalog (nam/nu).
export const sexOf = (g) => ({ nam: "nam", male: "nam", nu: "nu", female: "nu" }[g] || "");
const SEX = {
  nam: { label: "Giọng nam", icon: "mars", band: [205, 260] },
  nu: { label: "Giọng nữ", icon: "venus", band: [325, 385] },
};
// Phong cách đọc → icon + nhãn ngắn.
const STYLE = {
  "tự nhiên": { icon: "message-circle", label: "Tự nhiên", cls: "st-natural" },
  "bản tin": { icon: "newspaper", label: "Bản tin", cls: "st-news" },
  "tin tức": { icon: "newspaper", label: "Bản tin", cls: "st-news" },
  "kể chuyện": { icon: "drama", label: "Kể chuyện", cls: "st-story" },
  "đọc truyện": { icon: "book-open", label: "Đọc truyện", cls: "st-book" },
};

export function hueOf(key) {
  let h = 0;
  for (const ch of key) h = (h * 31 + ch.codePointAt(0)) >>> 0;
  return (h * 137.508) % 360; // góc vàng: các giọng cạnh nhau lệch màu rõ
}

const icon = (name, cls = "icon icon-xs") => `<svg class="${cls}" aria-hidden="true"><use href="/icons.svg#i-${name}"/></svg>`;

// Ảnh đại diện: giọng nam tông xanh, giọng nữ tông hồng (mỗi giọng một sắc riêng trong dải),
// góc dưới có huy hiệu giới tính. Không rõ giới tính: màu theo tên.
export function avatar(label, key, gender = "") {
  const words = (label || "?").trim().split(/\s+/);
  const letter = (words.length > 1 ? words[0][0] + words[words.length - 1][0] : words[0][0]).toUpperCase();
  const sx = SEX[sexOf(gender)];
  const hue = sx ? sx.band[0] + (hueOf(key) % (sx.band[1] - sx.band[0])) : hueOf(key);
  const badge = sx ? `<span class="sex-badge ${sexOf(gender)}">${icon(sx.icon, "icon")}</span>` : "";
  return `<span class="avatar${sx ? ` av-${sexOf(gender)}` : ""}" style="--h:${(hue % 360).toFixed(0)}" aria-hidden="true">${esc(letter)}${badge}</span>`;
}

// Dòng mô tả: [icon giới tính] miền … [nhãn phong cách]. Có chữ ẩn cho trình đọc màn hình.
export function metaHTML(v) {
  const sx = SEX[sexOf(v.gender)];
  const parts = [];
  if (sx) parts.push(`<span class="sex ${sexOf(v.gender)}" title="${sx.label}">${icon(sx.icon)}<span class="sr-only">${sx.label}</span></span>`);
  if (REGION[v.region]) parts.push(`<span>${REGION[v.region]}</span>`);
  const st = STYLE[(v.style || "").toLowerCase()];
  if (st) parts.push(`<span class="style-tag ${st.cls}">${icon(st.icon)}${st.label}</span>`);
  if (v.kind === "mine") parts.push(`<span>· ${v.clips?.length ? `${v.clips.length} mẫu` : "chưa có mẫu"}</span>`);
  return `<span class="vmeta">${parts.join("")}</span>`;
}

export function voiceMeta(v) {
  if (v.kind === "mine") return `Giọng của bạn · ${REGION[v.region] || ""}${v.clips?.length ? ` · ${v.clips.length} mẫu` : " · chưa có mẫu"}`;
  return [SEX[sexOf(v.gender)]?.label, REGION[v.region], v.style].filter(Boolean).join(" · ");
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
      ? `${avatar(v.label, v.value, v.gender)}<span style="flex:1;min-width:0"><span style="display:block;font-weight:500">${esc(v.label)}</span>${metaHTML(v)}</span><svg class="icon icon-sm"><use href="/icons.svg#i-chevron-down"/></svg>`
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
        ${avatar(v.label, v.value, v.gender)}<span style="min-width:0"><span class="name">${esc(v.label)}</span>${metaHTML(v)}</span></button>`;
    this.list.innerHTML =
      (mine.length ? `<div class="list-label">Giọng của bạn</div>${mine.map(row).join("")}` : "") +
      (presets.length ? `<div class="list-label">Giọng có sẵn</div>${presets.map(row).join("")}` : "") ||
      `<p class="hint" style="padding:8px 10px">Không có giọng nào trong nhóm này.</p>`;
  }
}
