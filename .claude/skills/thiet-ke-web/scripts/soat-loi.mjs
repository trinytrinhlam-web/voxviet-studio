#!/usr/bin/env node
// Soát lỗi tĩnh cho code giao diện: tìm các dấu hiệu "trông như AI làm", lỗi chuyển động,
// lỗi trợ năng và lỗi riêng cho tiếng Việt. Chỉ đọc file, không sửa gì, không gọi mạng.
//
// Cách dùng:
//   node <skill>/scripts/soat-loi.mjs <file hoặc thư mục> [...] [--che-do quang-ba|trai-nghiem|thao-tac|doc]
//                                     [--bo-qua ma-luat,ma-luat]
//   Chế độ mặc định: quang-ba (trang marketing, landing page).
//   Thoát với mã 1 nếu còn LỖI, 0 nếu chỉ còn CẢNH BÁO hoặc sạch.
//
// Script chỉ đọc mã nguồn nên không thay được việc nhìn ảnh chụp màn hình. Kết quả sạch là mức sàn,
// không phải bằng chứng trang đẹp.

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, extname, relative } from 'node:path';

const args = process.argv.slice(2);
const getOpt = (n) => { const i = args.indexOf('--' + n); return i === -1 ? null : args[i + 1]; };
const MODE_ALIAS = { 'quang-ba': 'persuade', 'trai-nghiem': 'experience', 'thao-tac': 'operate', doc: 'read' };
const mode = MODE_ALIAS[getOpt('che-do')] || getOpt('che-do') || 'persuade';
if (!['persuade', 'experience', 'operate', 'read'].includes(mode)) { console.error('--che-do phải là quang-ba, trai-nghiem, thao-tac hoặc doc.'); process.exit(2); }
const skip = new Set((getOpt('bo-qua') || '').split(',').filter(Boolean));
const targets = args.filter((a, i) => !a.startsWith('--') && !['--che-do', '--bo-qua'].includes(args[i - 1]));
if (!targets.length) { console.error('Cần ít nhất một file hoặc thư mục. Ví dụ: node soat-loi.mjs src --che-do quang-ba'); process.exit(2); }
const page = mode === 'persuade' || mode === 'experience';

// ---------- gom file ----------
const EXT = new Set(['.html', '.htm', '.css', '.scss', '.sass', '.less', '.js', '.mjs', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.astro', '.mdx']);
const SKIP_DIR = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.nuxt', '.svelte-kit', '.output', 'out', 'coverage', '.thiet-ke', 'vendor']);
const files = [];
const walk = (p) => {
  let st; try { st = statSync(p); } catch { console.error('Không tìm thấy: ' + p); return; }
  if (st.isDirectory()) { for (const f of readdirSync(p)) if (!SKIP_DIR.has(f)) walk(join(p, f)); }
  else if (EXT.has(extname(p).toLowerCase()) && !/\.min\.(js|css)$/.test(p)) files.push(p);
};
targets.forEach(walk);
if (!files.length) { console.error('Không có file giao diện nào để soát.'); process.exit(2); }

// ---------- tiện ích ----------
const VI_CHARS = /[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹĂÂĐÊÔƠƯẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸ]/;
const isMarkup = (f) => /\.(html?|jsx|tsx|vue|svelte|astro|mdx)$/i.test(f);
const lineOf = (text, idx) => text.slice(0, idx).split('\n').length;
const hexToHsl = (hex) => {
  let h = hex.replace('#', ''); if (h.length === 3) h = h.split('').map((c) => c + c).join(''); if (h.length !== 6) return null;
  const r = parseInt(h.slice(0, 2), 16) / 255, g = parseInt(h.slice(2, 4), 16) / 255, b = parseInt(h.slice(4, 6), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2; if (max === min) return { h: 0, s: 0, l };
  const d = max - min, s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let hh = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return { h: hh * 60, s, l };
};

// ---------- luật ----------
// muc: 'LỖI' | 'CẢNH BÁO' | null (không áp dụng ở chế độ này)
const R = [];
const rule = (id, muc, re, msg, opts = {}) => R.push({ id, muc, re, msg, ...opts });
const pm = (onPage, onApp) => (page ? onPage : onApp);

// Chuyển động (Emil, đồng thuận cả ba bộ)
rule('transition-all', 'LỖI', /transition\s*:\s*all\b|transition-property\s*:\s*all\b|\btransition-all\b/g, 'Không dùng `transition: all`. Ghi rõ thuộc tính: `transition: transform 200ms var(--ease-out)`.');
rule('ease-in', 'LỖI', /(?<![\w-])ease-in(?!-out)(?![\w-])/g, '`ease-in` làm giao diện có cảm giác chậm. Phần tử xuất hiện dùng ease-out; ngoại lệ duy nhất là thứ biến mất hẳn, rất ngắn (dùng `--ease-exit`).', { skipIf: /--ease-in\s*:/ });
rule('scale-0', 'LỖI', /scale\(\s*0(?:\.0+)?\s*\)|(?<![\w-])scale-0(?![\w-])/g, 'Không xuất hiện từ `scale(0)`. Bắt đầu từ 0.95 kèm opacity 0.');
rule('animate-layout', 'LỖI', /transition(?:-property)?\s*:[^;{}]*\b(?:width|height|top|left|right|bottom|margin|padding)\b/g, 'Animate thuộc tính bố cục gây giật. Dùng `transform` (translate, scale); accordion dùng `grid-template-rows`.');
rule('bounce', 'CẢNH BÁO', /\banimate-(?:bounce|ping|pulse)\b/g, 'Vòng lặp nảy/nhấp nháy vô nghĩa là dấu hiệu AI. Xóa, hoặc thay bằng chuyển động có mục đích.');
rule('overshoot', 'CẢNH BÁO', /cubic-bezier\(\s*[-\d.]+\s*,\s*(-0?\.\d+|-?[1-9][\d.]*|1\.\d+)\s*,\s*[-\d.]+\s*,\s*(-0?\.\d+|1\.\d+|[2-9][\d.]*)\s*\)/g, 'Đường cong vượt ngưỡng (nảy). Không dùng cho phần tử giao diện; chỉ spring nhẹ cho kéo thả.');
rule('will-change-all', 'CẢNH BÁO', /\*\s*\{[^}]*will-change/g, '`will-change` trên mọi phần tử tốn bộ nhớ GPU. Chỉ đặt trên đúng phần tử sắp animate, khi đã thấy giật.');
rule('vh-100', 'CẢNH BÁO', /(?<![\w.])100vh\b|\bh-screen\b|\bmin-h-screen\b/g, '`100vh` sai trên điện thoại. Hero dùng `100svh`, khung ứng dụng dùng `100dvh`.');

// Trợ năng
rule('outline-none', 'LỖI', /outline\s*:\s*(?:none|0)\b|(?<![\w:-])outline-none\b/g, 'Xóa outline mà không có `:focus-visible` thay thế làm người dùng bàn phím mất dấu.', { skipIfFile: /focus-visible/ });
rule('zoom-lock', 'LỖI', /user-scalable\s*=\s*no|maximum-scale\s*=\s*1(?:\.0)?\b/g, 'Không khóa phóng to. Muốn tránh tự zoom khi gõ thì để ô nhập 16px.');
rule('img-alt', 'LỖI', /<img\b(?![^>]*\balt\s*=)[^>]*>/g, 'Ảnh thiếu `alt`. Ảnh trang trí dùng `alt=""`.', { markupOnly: true });
rule('img-size', 'CẢNH BÁO', /<img\b(?![^>]*\b(?:width|fill)\b)[^>]*>/g, 'Ảnh thiếu `width`/`height` gây nhảy bố cục khi tải.', { markupOnly: true });

// Dấu hiệu AI (taste-skill + Impeccable)
rule('gradient-text', 'LỖI', /background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text|\bbg-clip-text\b/g, 'Chữ gradient bị cả ba bộ cấm. Nhấn mạnh bằng độ đậm hoặc cỡ chữ.');
rule('gradient', pm('LỖI', 'CẢNH BÁO'), /(?:linear|radial|conic)-gradient\(|\bbg-gradient-to-\w+|\bbg-(?:linear|radial|conic)\b/g, page ? 'Trang quảng bá không dùng gradient (trừ lớp phủ trung tính dưới chữ trên ảnh). Dùng màu phẳng hoặc ảnh thật.' : 'Gradient trên màn hình ứng dụng: chỉ khi brief yêu cầu.');
rule('glass', pm('LỖI', 'CẢNH BÁO'), /backdrop-filter\s*:|\bbackdrop-blur(?:-\w+)?\b/g, page ? 'Không dùng kính mờ trên trang quảng bá. Thanh điều hướng là một thanh phẳng.' : 'Kính mờ chỉ khi có chức năng cụ thể, không để trang trí.');
rule('shadow-rest', pm('CẢNH BÁO', null), /box-shadow\s*:\s*(?!none|0\s*0\s*0)[^;]+|(?<![\w-])shadow(?:-(?:sm|md|lg|xl|2xl))?(?![\w-])/g, 'Trang quảng bá không đổ bóng cho vật đứng yên. Chỉ menu, dialog đang nổi mới có bóng. Tách bề mặt bằng một bậc tông nền.');
rule('hard-shadow', 'CẢNH BÁO', /box-shadow\s*:\s*-?\d+px\s+-?\d+px\s+0(?:px)?\s/g, 'Bóng lệch cứng (không blur) chỉ hợp với thế giới neobrutalist được chọn có chủ đích.');
rule('hairline', pm('CẢNH BÁO', null), /border(?:-top|-bottom)?\s*:\s*1px\b|<hr\b|\bdivide-[xy]\b/g, 'Trang quảng bá không dùng đường kẻ mảnh. Tách bằng khoảng trống, bậc tông nền hoặc thay đổi tỉ lệ. (Bảng và form được giữ đường kẻ.)');
rule('side-stripe', 'CẢNH BÁO', /border-(?:left|right)\s*:\s*(?:[2-9]|\d{2,})px|\bborder-[lr]-(?:[2-8])\b/g, 'Viền màu dày một bên trên thẻ/callout là dấu hiệu AI. Bỏ, hoặc dùng nền tông khác.');
rule('mono', 'CẢNH BÁO', /font-family\s*:[^;]*\bmonospace\b|\bfont-mono\b/g, 'Monospace chỉ cho code, dữ liệu, số đo; không làm "trang phục kỹ thuật".');
rule('default-font', 'CẢNH BÁO', /font-family\s*:\s*["']?(?:Inter|Arial|Roboto|Helvetica|system-ui|-apple-system)\b|family=(?:Inter|Roboto)\b/g, page ? 'Font mặc định cho giọng chính của trang. Dùng font đã rút trong phiếu hướng.' : 'Font hệ thống ổn cho màn hình ứng dụng; kiểm tra đó là lựa chọn có chủ đích.', { modes: page ? null : [] });
rule('training-font', pm('CẢNH BÁO', null), /\b(?:Fraunces|Playfair(?:\+|\s)Display|Cormorant|Lora|Crimson|Newsreader|Syne|Space(?:\+|\s)(?:Grotesk|Mono)|IBM(?:\+|\s)Plex|DM(?:\+|\s)(?:Sans|Serif)|Outfit|Plus(?:\+|\s)Jakarta|Instrument(?:\+|\s)Sans)\b/g, 'Font thuộc nhóm "AI hay chọn" (Impeccable). Chỉ dùng khi có lý do mà không font nào khác đáp ứng.');
rule('eyebrow-tw', 'CẢNH BÁO', /class(?:Name)?=["'][^"']*\buppercase\b[^"']*\btracking-(?:wide|wider|widest|\[0?\.\d+em\])\b[^"']*["']|class(?:Name)?=["'][^"']*\btracking-(?:wide|wider|widest)\b[^"']*\buppercase\b[^"']*["']/g, 'Nhãn nhỏ viết hoa giãn chữ (eyebrow) là dấu hiệu AI. Gộp thông tin vào tiêu đề hoặc bỏ.', { markupOnly: true });
rule('numbering', 'CẢNH BÁO', />\s*\(?0[1-9]\)?\s*(?:[/.·—–-]\s*)?</g, 'Đánh số 01/02/03 trang trí. Thể hiện thứ tự bằng vị trí, cỡ chữ hoặc `<ol>`.', { markupOnly: true });
rule('emoji', 'CẢNH BÁO', /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, 'Emoji thay icon hoặc gạch đầu dòng. Dùng bộ icon thật cùng nét, hoặc chữ.', { markupOnly: true });
rule('ai-palette-tw', 'CẢNH BÁO', /\b(?:bg|text|from|to|via|border|ring)-(?:purple|violet|indigo|fuchsia)-\d{2,3}\b/g, 'Tím/indigo là bảng màu "trợ lý AI". Dùng bảng màu đã rút, trừ khi là màu thương hiệu.');
rule('pill-nav', pm('CẢNH BÁO', null), /<nav\b[^>]*class(?:Name)?=["'][^"']*\brounded-full\b/g, 'Thanh điều hướng dạng viên thuốc nổi. Dùng thanh phẳng: tên, vài link, một nút.', { markupOnly: true });

// Chữ viết (copy)
const copyEn = /\b(?:unlock|supercharge|seamless(?:ly)?|elevate|effortless(?:ly)?|cutting-edge|revolutioni[sz]e|game-chang\w+|next-level|all-in-one)\b|Get started|Learn more|Welcome to\b|It['’]s not just|more than just/gi;
const copyVi = /giải pháp toàn diện|đột phá|hàng đầu|nâng tầm|tối ưu hóa trải nghiệm|trải nghiệm tuyệt vời|liền mạch|vượt trội|khám phá ngay|tìm hiểu thêm|bắt đầu ngay|chào mừng (?:bạn )?đến với|không chỉ là|đỉnh cao|cách mạng hóa|mọi lúc mọi nơi|chất lượng hàng đầu|uy tín số 1/gi;
rule('copy-en', 'CẢNH BÁO', copyEn, 'Cụm từ sáo rỗng kiểu landing page. Viết điều cụ thể chỉ chủ thể này nói được; nút ghi rõ hành động.', { markupOnly: true });
rule('copy-vi', 'CẢNH BÁO', copyVi, 'Cụm từ quảng cáo sáo rỗng. Viết điều cụ thể (con số, địa danh, chất liệu); nút ghi rõ hành động ("Đặt bàn", "Xem thực đơn").', { markupOnly: true });
rule('lorem', 'LỖI', /lorem ipsum|dolor sit amet|Image here|Ảnh ở đây|placeholder\.com|via\.placeholder/gi, 'Còn nội dung giữ chỗ. Viết nội dung mẫu cụ thể và liệt kê trong báo cáo để thay trước khi ra mắt.');

// ---------- quét ----------
const findings = [];
const add = (file, line, id, muc, msg, snippet) => { if (!skip.has(id) && muc) findings.push({ file, line, id, muc, msg, snippet }); };
let anyMotion = false, anyReduced = false, anyHover = false, anyHoverGate = false, anyTwHover = false;
let viFiles = [], tightLeading = [], fontshare = [], langEn = [], hexHits = [];

for (const f of files) {
  const text = readFileSync(f, 'utf8');
  const rel = relative(process.cwd(), f) || f;
  for (const r of R) {
    if (r.markupOnly && !isMarkup(f)) continue;
    if (r.modes && !r.modes.includes(mode)) continue;
    if (r.skipIfFile && r.skipIfFile.test(text)) continue;
    r.re.lastIndex = 0; let m; let count = 0;
    while ((m = r.re.exec(text)) && count < 6) {
      const lineText = text.split('\n')[lineOf(text, m.index) - 1] || '';
      if (r.skipIf && r.skipIf.test(lineText)) continue;
      // bỏ qua bên trong <pre>/<code> cho luật monospace
      if (r.id === 'mono' && /<(?:pre|code)\b|\bpre\b|\bcode\b/.test(lineText)) continue;
      add(rel, lineOf(text, m.index), r.id, r.muc, r.msg, m[0].slice(0, 70)); count++;
    }
  }
  if (/@keyframes|animation\s*:|transition\s*:|IntersectionObserver|\banimate-|\btransition-|motion\.|framer-motion|gsap/.test(text)) anyMotion = true;
  if (/prefers-reduced-motion|motion-safe:|motion-reduce:|useReducedMotion/.test(text)) anyReduced = true;
  if (/:hover\b/.test(text)) anyHover = true;
  if (/\(hover:\s*hover\)/.test(text)) anyHoverGate = true;
  if (/(?<![\w-])hover:[\w[]/.test(text)) anyTwHover = true;
  if (isMarkup(f) && VI_CHARS.test(text.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, ''))) viFiles.push(rel);
  const lh = text.match(/line-height\s*:\s*(?:0?\.\d+|1(?:\.0+)?)\s*(?=[;}\s!])|\bleading-none\b|\bleading-\[(?:0?\.\d+|1(?:\.0+)?)\]/g);
  if (lh) tightLeading.push(`${rel} (${[...new Set(lh)].slice(0, 3).join(', ')})`);
  if (/fontshare\.com/.test(text)) fontshare.push(rel);
  if (/<html[^>]*\blang=["']en/.test(text)) langEn.push(rel);
  for (const m of text.matchAll(/#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g)) {
    const c = hexToHsl(m[0]); if (!c) continue;
    if (c.s > 0.35 && c.l > 0.2 && c.l < 0.75 && c.h >= 245 && c.h <= 290) hexHits.push({ f: rel, line: lineOf(text, m.index), c: m[0], kind: 'tím/indigo' });
    if (c.s > 0.4 && c.l > 0.35 && c.l < 0.6 && c.h >= 10 && c.h <= 28) hexHits.push({ f: rel, line: lineOf(text, m.index), c: m[0], kind: 'đất nung/gỉ sét' });
  }
}

// luật cấp dự án
if (anyMotion && !anyReduced) add('(toàn dự án)', 0, 'reduced-motion', 'LỖI', 'Có chuyển động nhưng không có `prefers-reduced-motion` ở đâu cả. Mọi trạng thái ẩn đặt trong `@media (prefers-reduced-motion: no-preference)`.', '');
if (anyHover && !anyHoverGate) add('(toàn dự án)', 0, 'hover-gate', 'CẢNH BÁO', 'Có `:hover` nhưng không bọc trong `@media (hover: hover) and (pointer: fine)`; trên điện thoại hover sẽ dính sau khi chạm.', '');
if (anyTwHover && !anyHoverGate) add('(toàn dự án)', 0, 'hover-gate-tw', 'CẢNH BÁO', 'Tailwind `hover:` chỉ tự bọc media query từ v4. Với v3, bật `future: { hoverOnlyWhenSupported: true }`.', '');
for (const h of hexHits.slice(0, 6)) add(h.f, h.line, 'ai-palette', 'CẢNH BÁO', `Màu ${h.c} thuộc nhóm ${h.kind}, nhóm màu "trợ lý AI". Chỉ dùng nếu là màu thương hiệu.`, h.c);

// tiếng Việt
if (viFiles.length) {
  if (tightLeading.length) add('(tiếng Việt)', 0, 'vi-leading', 'CẢNH BÁO', `Trang có tiếng Việt và có leading chặt (≤ 1.0) ở: ${tightLeading.slice(0, 4).join('; ')}. Chụp màn hình kiểm tra dấu chồng trên chữ hoa (Ế, Ỗ, Ặ, Ữ) không bị cắt hoặc đụng dòng trên.`, '');
  if (fontshare.length) add('(tiếng Việt)', 0, 'vi-fontshare', 'LỖI', `Trang có tiếng Việt nhưng tải font từ Fontshare (${fontshare.slice(0, 3).join(', ')}). Phần lớn font Fontshare không có dấu tiếng Việt; trình duyệt sẽ ghép chữ có dấu bằng font dự phòng, nhìn lởm chởm. Kiểm tra hoặc đổi font (tai-lieu/03-chu.md).`, '');
  if (langEn.length) add('(tiếng Việt)', 0, 'vi-lang', 'CẢNH BÁO', `Nội dung tiếng Việt nhưng <html lang="en"> ở: ${langEn.join(', ')}. Đặt lang="vi" để trình đọc màn hình và ngắt từ đúng.`, '');
  add('(tiếng Việt)', 0, 'vi-nhac', 'GHI CHÚ', 'Nhắc: kiểm tra font thật sự có dấu (xem tai-lieu/03-chu.md), và chụp một tiêu đề viết hoa có dấu chồng ở mọi độ rộng.', '');
}

// ---------- in kết quả ----------
const errs = findings.filter((x) => x.muc === 'LỖI'), warns = findings.filter((x) => x.muc === 'CẢNH BÁO'), notes = findings.filter((x) => x.muc === 'GHI CHÚ');
const MODE_VI = { persuade: 'quảng bá', experience: 'trải nghiệm', operate: 'thao tác', read: 'đọc' };
console.log(`Soát ${files.length} file · chế độ ${MODE_VI[mode]} · ${errs.length} LỖI · ${warns.length} CẢNH BÁO\n`);
const byFile = {};
for (const x of [...errs, ...warns, ...notes]) (byFile[x.file] ||= []).push(x);
for (const [file, list] of Object.entries(byFile)) {
  console.log(file);
  for (const x of list.sort((a, b) => a.line - b.line)) console.log(`  ${{ 'LỖI': '✖ LỖI     ', 'CẢNH BÁO': '▲ CẢNH BÁO', 'GHI CHÚ': '· GHI CHÚ ' }[x.muc]} ${x.line ? 'dòng ' + String(x.line).padEnd(5) : '          '} [${x.id}] ${x.msg}${x.snippet ? `\n${' '.repeat(28)}→ ${x.snippet.replace(/\s+/g, ' ')}` : ''}`);
  console.log('');
}
if (!errs.length && !warns.length) console.log('Không phát hiện gì. Đây là mức sàn, không phải bằng chứng trang đẹp: vẫn phải chụp màn hình và tự phê bình.');
else console.log('Sửa mọi LỖI. Mỗi CẢNH BÁO coi là sai trừ khi bạn bảo vệ được nó trong một câu trước một nhà thiết kế. Bỏ qua một luật có chủ đích: --bo-qua <mã>.');
process.exit(errs.length ? 1 : 0);
