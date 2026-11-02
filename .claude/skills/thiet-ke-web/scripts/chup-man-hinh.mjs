#!/usr/bin/env node
// Chụp một trang ở 1440, 768 và 390px như người xem thật thấy, bằng Chrome/Chromium/Edge có sẵn trên máy.
// Điều khiển Chrome qua giao thức DevTools (WebSocket có sẵn trong Node 22+). Không cài gì, không tải gì.
//
// Cách dùng (từ thư mục gốc dự án):
//   node <skill>/scripts/chup-man-hinh.mjs <url hoặc đường-dẫn/index.html> [tên-lần-chụp]
//   Ví dụ: node .../chup-man-hinh.mjs http://localhost:5173 vong-1
// Biến môi trường CHROME=/đường/dẫn/chrome để chỉ định trình duyệt.
//
// Ảnh vào .thiet-ke/anh/<tên>/:
//   <độ-rộng>-01.png, -02.png...  từng màn hình khi cuộn từ trên xuống (tối đa 12 mỗi độ rộng)
//   1440-giam-chuyen-dong.png     màn hình đầu khi bật giảm chuyển động
// Kèm báo cáo ngắn: cuộn ngang, font thực sự đã tải, phần tử còn ẩn sau khi cuộn.

import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , target, nameArg] = process.argv;
if (!target) { console.error('Cần URL hoặc đường dẫn file HTML.'); process.exit(2); }
if (typeof WebSocket === 'undefined') {
  console.error('Script này cần Node 22 trở lên (có WebSocket sẵn). Với Node cũ hơn, dùng chup-man-hinh.sh (ảnh điện thoại sẽ kém chính xác).');
  process.exit(2);
}
const url = /^[a-z]+:\/\//i.test(target) ? target : pathToFileURL(resolve(target)).href;
const name = nameArg || new Date().toTimeString().slice(0, 8).replace(/:/g, '');
const OUT = join('.thiet-ke', 'anh', name);
mkdirSync(OUT, { recursive: true });

// ---------- tìm trình duyệt ----------
const candidates = [
  process.env.CHROME,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/microsoft-edge',
  '/snap/bin/chromium',
].filter(Boolean);
const chrome = candidates.find((p) => existsSync(p));
if (!chrome) { console.error('Không tìm thấy Chrome, Chromium hay Edge. Đặt biến CHROME=/đường/dẫn.'); process.exit(2); }

// ---------- khởi động Chrome ----------
const profile = mkdtempSync(join(tmpdir(), 'thiet-ke-chrome-'));
const args = ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--mute-audio', 'about:blank'];
if (process.getuid && process.getuid() === 0) args.unshift('--no-sandbox'); // Chrome từ chối chạy dưới root nếu thiếu cờ này
const proc = spawn(chrome, args, { stdio: 'ignore' });
const cleanup = () => { try { proc.kill(); } catch {} try { rmSync(profile, { recursive: true, force: true }); } catch {} };
process.on('exit', cleanup);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let wsUrl = null;
for (let i = 0; i < 100 && !wsUrl; i++) {
  await sleep(100);
  try { const [port, path] = readFileSync(join(profile, 'DevToolsActivePort'), 'utf8').trim().split('\n'); wsUrl = `ws://127.0.0.1:${port}${path}`; } catch {}
}
if (!wsUrl) { console.error('Chrome không khởi động được.'); process.exit(1); }

// ---------- giao thức DevTools tối giản ----------
const ws = new WebSocket(wsUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let id = 0; const pending = new Map(); const listeners = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { const { res, rej } = pending.get(m.id); pending.delete(m.id); m.error ? rej(new Error(m.error.message)) : res(m.result); }
  else if (m.method) listeners.forEach((f) => f(m));
};
const send = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
const once = (method, sessionId, timeout = 20000) => new Promise((res) => {
  const t = setTimeout(() => res(null), timeout);
  const f = (m) => { if (m.method === method && m.sessionId === sessionId) { clearTimeout(t); listeners.splice(listeners.indexOf(f), 1); res(m.params); } };
  listeners.push(f);
});

const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId: s } = await send('Target.attachToTarget', { targetId, flatten: true });
await send('Page.enable', {}, s);
await send('Runtime.enable', {}, s);

const evaluate = async (expression) => (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true }, s)).result.value;
const shot = async (file) => { const { data } = await send('Page.captureScreenshot', { format: 'png' }, s); writeFileSync(file, Buffer.from(data, 'base64')); return file; };

async function load(width, height, reduce) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 600, screenWidth: width, screenHeight: height }, s);
  await send('Emulation.setTouchEmulationEnabled', { enabled: width < 600 }, s);
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: reduce ? 'reduce' : 'no-preference' }] }, s);
  const loaded = once('Page.loadEventFired', s);
  await send('Page.navigate', { url }, s);
  await loaded;
  await evaluate('document.fonts ? document.fonts.ready.then(() => true) : true');
  await sleep(1600); // chuỗi mở trang tối đa 1,2 giây theo luật nhà
}

const report = [];
console.log(`Chụp ${url} bằng ${chrome.split(/[\\/]/).pop()}:`);
for (const [w, h] of [[1440, 900], [768, 1024], [390, 844]]) {
  await load(w, h, false);
  // Cuộn qua cả trang một lượt để kích hoạt mọi hiệu ứng lộ diện, rồi quay lại đầu.
  const total = await evaluate(`(async () => {
    const H = () => document.documentElement.scrollHeight;
    for (let y = 0; y < H(); y += Math.round(innerHeight * 0.6)) { scrollTo(0, y); await new Promise(r => setTimeout(r, 180)); }
    scrollTo(0, H()); await new Promise(r => setTimeout(r, 400));
    scrollTo(0, 0); await new Promise(r => setTimeout(r, 1200));
    return H();
  })()`);
  const screens = Math.min(12, Math.ceil(total / h));
  for (let i = 0; i < screens; i++) {
    await evaluate(`scrollTo(0, ${i * h}); new Promise(r => setTimeout(r, 1100))`);
    const f = await shot(join(OUT, `${w}-${String(i + 1).padStart(2, '0')}.png`));
    console.log('  ' + f);
  }
  if (Math.ceil(total / h) > 12) console.log(`  (trang dài ${Math.ceil(total / h)} màn hình ở ${w}px; chỉ chụp 12 màn hình đầu)`);
  const info = await evaluate(`(() => {
    const vw = document.documentElement.clientWidth;
    const overflow = document.documentElement.scrollWidth - vw;
    const wide = [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.right > vw + 2 && getComputedStyle(e).position !== 'fixed'; }).slice(0, 3).map(e => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/)[0] : ''));
    const hidden = [...document.querySelectorAll('h1,h2,h3,p,img,figure,li,a,button')].filter(e => { const cs = getComputedStyle(e); return e.getClientRects().length && parseFloat(cs.opacity) < 0.05 && cs.visibility !== 'hidden'; }).length;
    const fonts = document.fonts ? [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')))] : [];
    return { overflow, wide, hidden, fonts };
  })()`);
  if (info.overflow > 1) report.push(`${w}px: trang cuộn ngang ${info.overflow}px (thủ phạm có thể là: ${info.wide.join(', ') || 'không rõ'}).`);
  if (info.hidden) report.push(`${w}px: còn ${info.hidden} phần tử có opacity ~0 sau khi đã cuộn hết trang. Một hiệu ứng lộ diện có thể không chạy.`);
  if (w === 1440) report.push(`Font đã tải thật: ${info.fonts.length ? info.fonts.join(', ') : 'không có font web nào (đang dùng font hệ thống)'}.`);
}
await load(1440, 900, true);
console.log('  ' + await shot(join(OUT, '1440-giam-chuyen-dong.png')));

console.log('\nBáo cáo nhanh:');
report.forEach((r) => console.log('  - ' + r));
console.log('\nMở từng ảnh để xem, theo thứ tự cuộn. Ảnh giảm chuyển động phải hiện đủ nội dung.');
console.log('Trang dùng ES module, fetch hay router: chạy dev server và truyền URL http:// thay vì đường dẫn file.');
ws.close(); cleanup(); process.exit(0);
