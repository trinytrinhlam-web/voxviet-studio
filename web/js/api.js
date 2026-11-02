// Gọi API máy chủ cục bộ. Mọi yêu cầu ghi gửi kèm header X-VoxViet (chống trang lạ gọi tới).
const H = { "X-VoxViet": "1" };

async function handle(res) {
  if (res.ok) return res.status === 204 ? null : res.json();
  let msg = `Lỗi ${res.status}`;
  try {
    const d = await res.json();
    msg = typeof d.detail === "string" ? d.detail : msg;
  } catch { /* giữ thông báo mặc định */ }
  throw new Error(msg);
}

export const api = {
  get: (url) => fetch(url).then(handle),
  post: (url, body) => fetch(url, { method: "POST", headers: { ...H, "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) }).then(handle),
  put: (url, body) => fetch(url, { method: "PUT", headers: { ...H, "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) }).then(handle),
  patch: (url, body) => fetch(url, { method: "PATCH", headers: { ...H, "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) }).then(handle),
  del: (url) => fetch(url, { method: "DELETE", headers: H }).then(handle),
  upload: (url, form) => fetch(url, { method: "POST", headers: H, body: form }).then(handle),
};

// Gửi một công việc nền rồi theo dõi tiến độ cho đến khi xong.
export async function runJob(url, body, onProgress) {
  const { job } = await api.post(url, body);
  for (;;) {
    await new Promise((r) => setTimeout(r, 250));
    const j = await api.get(`/api/jobs/${job}`);
    onProgress?.(j);
    if (j.status === "done") return j.result;
    if (j.status === "error") throw new Error(j.error || "Có lỗi xảy ra.");
  }
}

export function toast(text, kind = "ok") {
  const box = document.getElementById("toasts");
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  const icon = kind === "err" ? "triangle-alert" : "check";
  el.innerHTML = `<svg class="icon icon-sm"><use href="/icons.svg#i-${icon}"/></svg><span></span>`;
  el.querySelector("span").textContent = text;
  box.append(el);
  setTimeout(() => el.remove(), kind === "err" ? 7000 : 3500);
}

export const fmtTime = (s) => {
  if (!Number.isFinite(s)) return "0:00";
  const m = Math.floor(s / 60);
  const r = Math.floor(s % 60);
  return `${m}:${String(r).padStart(2, "0")}`;
};

export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
