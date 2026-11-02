// Ô chọn giọng: giọng của bạn + giọng có sẵn theo vùng. Ảnh đại diện theo giới tính, nhãn phong cách có icon.
import { api, esc } from "./api.js";

const REGION = { bac: "miền Bắc", trung: "miền Trung", nam: "miền Nam" };
// Giới tính: chấp nhận cả mã cũ (male/female) lẫn mã của catalog (nam/nu).
export const sexOf = (g) => ({ nam: "nam", male: "nam", nu: "nu", female: "nu" }[g] || "");
const SEX = {
  nam: { label: "Giọng nam", icon: "mars" },
  nu: { label: "Giọng nữ", icon: "venus" },
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

// Ảnh đại diện 3D (Microsoft Fluent Emoji 3D, giấy phép MIT — web/avatars/).
// Giọng có ảnh riêng thì dùng ảnh đó; chưa có thì chọn cố định theo giới tính + tên.
export const AVATAR_POOL = {
  nam: ["man-light", "boy-light", "man-curly-light", "boy-medlight", "man-raising-light", "man-singer-light",
    "man-tech-medlight", "man-ok-medium", "man-teacher-light", "man-office-light", "man-cook-light", "man-artist-medlight"],
  nu: ["woman-light", "girl-light", "woman-curly-light", "girl-medlight", "woman-ok-light", "woman-singer-medlight",
    "woman-tech-medlight", "woman-curly-medlight", "woman-teacher-light", "woman-office-light", "woman-cook-light",
    "woman-headscarf-medlight"],
};
export const avatarUrl = (slug) => `/avatars/${slug}.webp`;

export function avatar(label, key, gender = "", img = null) {
  const k = key || label || "?";
  let sex = sexOf(gender);
  const h = hueOf(k);
  if (!sex) sex = Math.floor(h) % 2 ? "nam" : "nu";
  const pool = AVATAR_POOL[sex];
  const src = img || avatarUrl(pool[Math.floor(h * 7) % pool.length]);
  return `<span class="avatar img av-${sex}" aria-hidden="true"><img src="${esc(src)}" alt="" loading="lazy" decoding="async" draggable="false"></span>`;
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
      ? `${avatar(v.label, v.value, v.gender, v.avatar)}<span style="flex:1;min-width:0"><span style="display:block;font-weight:500">${esc(v.label)}</span>${metaHTML(v)}</span><svg class="icon icon-sm"><use href="/icons.svg#i-chevron-down"/></svg>`
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
        ${avatar(v.label, v.value, v.gender, v.avatar)}<span style="min-width:0"><span class="name">${esc(v.label)}</span>${metaHTML(v)}</span></button>`;
    this.list.innerHTML =
      (mine.length ? `<div class="list-label">Giọng của bạn</div>${mine.map(row).join("")}` : "") +
      (presets.length ? `<div class="list-label">Giọng có sẵn</div>${presets.map(row).join("")}` : "") ||
      `<p class="hint" style="padding:8px 10px">Không có giọng nào trong nhóm này.</p>`;
  }
}
