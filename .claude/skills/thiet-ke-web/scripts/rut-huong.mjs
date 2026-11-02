#!/usr/bin/env node
// Rút ngẫu nhiên một hướng thiết kế từ thư viện cục bộ (thu-vien/*.json).
// Không cài gói, không gọi mạng. Chỉ đọc thư viện và ghi phiếu vào .thiet-ke/ của dự án,
// cộng một file lịch sử nhỏ ở ~/.thiet-ke-web/lich-su.json để tránh lặp lại hướng vừa dùng.
//
// Cách dùng (chạy từ thư mục gốc dự án):
//   node <skill>/scripts/rut-huong.mjs --danh-sach nganh|huong|phan|giong|co
//   node <skill>/scripts/rut-huong.mjs --nganh nha-hang --mo-ta "quán cà phê rang xay ở Đà Lạt" \
//        [--phan gioi-thieu,thuc-don,thu-vien-anh,lien-he] [--giong am-ap] [--co anh-chup] \
//        [--giu mau,chu] [--tranh id,id] [--seed N] --lua-chon 3
//   node <skill>/scripts/rut-huong.mjs <cùng tham số> --huong <mã hướng đã chọn>
//   node <skill>/scripts/rut-huong.mjs --xem
//   node <skill>/scripts/rut-huong.mjs --ve-lai hero|chu|mau|huong|phan:<vai>|phan:<vai>=<mã>
//   node <skill>/scripts/rut-huong.mjs --thay-the <vai>
//
// Dữ liệu thư viện chắt lọc từ taste-skill (Leonxlnx, giấy phép MIT). Xem NGUON.md.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';
import { randomInt } from 'node:crypto';

const HERE = dirname(fileURLToPath(import.meta.url));
const LIB = join(HERE, '..', 'thu-vien');
const load = (n) => JSON.parse(readFileSync(join(LIB, n + '.json'), 'utf8'));
const L = { directions: load('directions'), heroes: load('heroes'), sections: load('sections'), type: load('type'), palettes: load('palettes'), motions: load('motions') };

// ---------- tham số ----------
const argv = process.argv.slice(2);
const opt = (name, def) => { const i = argv.indexOf('--' + name); if (i === -1) return def; const v = argv[i + 1]; return v === undefined || v.startsWith('--') ? true : v; };
const list = (v) => (typeof v === 'string' ? v.split(',').map((s) => s.trim()).filter(Boolean) : []);
const OUT = resolve(String(opt('thu-muc', '.thiet-ke')));
const SHEET = join(OUT, 'huong.json');

// ---------- từ vựng: tiếng Việt và tiếng Anh đều được ----------
const NGANH = {
  'phan-mem': 'saas', 'cong-cu-lap-trinh': 'dev-tool', ai: 'ai-product', 'ung-dung': 'consumer-app', 'tai-chinh': 'finance',
  agency: 'agency', 'cong-ty-sang-tao': 'agency', studio: 'studio-portfolio', 'ca-nhan': 'personal-portfolio', portfolio: 'personal-portfolio',
  'thuong-mai-dien-tu': 'ecommerce', 'cua-hang': 'ecommerce', 'san-pham': 'physical-product', 'thoi-trang': 'fashion',
  'khach-san': 'hospitality', homestay: 'hospitality', 'luu-tru': 'hospitality', 'nha-hang': 'restaurant', 'quan-an': 'restaurant', cafe: 'restaurant',
  'bat-dong-san': 'real-estate', 'kien-truc': 'architecture', 'su-kien': 'event', 'suc-khoe': 'health', 'giao-duc': 'education',
  'phi-loi-nhuan': 'nonprofit', 'van-hoa': 'culture', 'am-nhac': 'music', khac: 'other',
};
const SECTORS = ['saas', 'dev-tool', 'ai-product', 'consumer-app', 'finance', 'agency', 'studio-portfolio', 'personal-portfolio', 'ecommerce', 'physical-product', 'fashion', 'hospitality', 'restaurant', 'real-estate', 'architecture', 'event', 'health', 'education', 'nonprofit', 'culture', 'music', 'other'];
const GIONG = { 'yen-tinh': 'quiet', 'manh-me': 'bold', 'am-ap': 'warm', 'ky-thuat': 'technical', 'vui-tuoi': 'playful', 'sang-trong': 'luxury', 'tap-chi': 'editorial' };
const TONES = Object.values(GIONG);
const VAI = {
  'tinh-nang': 'features', 'dich-vu': 'features', 'trung-bay': 'showcase', 'san-pham': 'showcase', 'cach-hoat-dong': 'how-it-works', 'quy-trinh': 'how-it-works',
  'danh-gia': 'testimonial', 'cam-nhan': 'testimonial', 'bang-chung': 'proof', 'doi-tac': 'proof', 'so-lieu': 'stats', 'bang-gia': 'pricing', 'hoi-dap': 'faq',
  'keu-goi': 'cta', 'chan-trang': 'footer', 'gioi-thieu': 'intro', 'tuyen-ngon': 'intro', 've-chung-toi': 'about', 'doi-ngu': 'about', 'du-an': 'work',
  'thu-vien-anh': 'gallery', 'danh-sach': 'list', 'thuc-don': 'list', 'lich': 'list', 'lien-he': 'contact',
};
const VAI_VI = Object.fromEntries(Object.entries({ features: 'tính năng', showcase: 'trưng bày', 'how-it-works': 'cách hoạt động', testimonial: 'cảm nhận', proof: 'bằng chứng', stats: 'số liệu', pricing: 'bảng giá', faq: 'hỏi đáp', cta: 'kêu gọi', footer: 'chân trang', intro: 'giới thiệu', about: 'về chúng tôi', work: 'dự án', gallery: 'thư viện ảnh', list: 'danh sách', contact: 'liên hệ' }));
const CO = { 'anh-chup': 'photography', 'anh-san-pham': 'product-photo', 'giao-dien': 'product-ui', 'minh-hoa': 'illustration', video: 'video' };
const DEFAULT_SECTIONS = {
  saas: ['showcase', 'features', 'how-it-works', 'testimonial', 'pricing', 'faq', 'cta', 'footer'], 'dev-tool': ['showcase', 'features', 'how-it-works', 'pricing', 'faq', 'cta', 'footer'],
  'ai-product': ['showcase', 'features', 'how-it-works', 'testimonial', 'pricing', 'cta', 'footer'], 'consumer-app': ['showcase', 'features', 'testimonial', 'cta', 'footer'],
  finance: ['showcase', 'features', 'stats', 'testimonial', 'faq', 'cta', 'footer'], agency: ['intro', 'work', 'features', 'about', 'cta', 'footer'],
  'studio-portfolio': ['work', 'intro', 'features', 'about', 'cta', 'footer'], 'personal-portfolio': ['work', 'about', 'cta', 'footer'],
  ecommerce: ['gallery', 'features', 'intro', 'testimonial', 'cta', 'footer'], 'physical-product': ['showcase', 'features', 'gallery', 'intro', 'pricing', 'cta', 'footer'],
  fashion: ['gallery', 'intro', 'work', 'cta', 'footer'], hospitality: ['intro', 'gallery', 'features', 'list', 'contact', 'footer'], restaurant: ['intro', 'list', 'gallery', 'contact', 'footer'],
  'real-estate': ['intro', 'gallery', 'features', 'stats', 'contact', 'footer'], architecture: ['work', 'intro', 'about', 'contact', 'footer'],
  event: ['intro', 'list', 'features', 'pricing', 'faq', 'cta', 'footer'], health: ['intro', 'features', 'how-it-works', 'testimonial', 'faq', 'cta', 'footer'],
  education: ['intro', 'features', 'how-it-works', 'testimonial', 'pricing', 'faq', 'cta', 'footer'], nonprofit: ['intro', 'stats', 'features', 'about', 'cta', 'footer'],
  culture: ['intro', 'gallery', 'list', 'about', 'cta', 'footer'], music: ['list', 'gallery', 'about', 'cta', 'footer'], other: ['intro', 'features', 'showcase', 'cta', 'footer'],
};

// Tên và ý tưởng của 20 hướng, bằng tiếng Việt. Bản đầy đủ (tiếng Anh) nằm trong thu-vien/directions.json.
const HUONG_VI = {
  'name-as-monument': ['Cái tên như tượng đài', 'Tên thương hiệu là tiêu đề, to đến mức thành kiến trúc: rộng bằng màn hình, bị mép cắt, hoặc xếp chồng kín màn hình. Chữ cái là chất liệu.'],
  'sentence-as-layout': ['Câu văn là bố cục', 'Một câu ngắn cỡ áp phích là cả bố cục; một thứ của chủ thể (ảnh, mẩu sản phẩm) nằm ngay trong câu ở chỗ một từ.'],
  'pinned-poster': ['Tấm áp phích ghim', 'Một thứ đứng yên trong khi mọi thứ khác thay đổi; mỗi bước cuộn là một trang bìa mới của cùng một tạp chí. Hợp với chủ thể là một loạt.'],
  'colour-chapters': ['Các chương màu', 'Mỗi section là một chương với một màu phẳng từ sàn đến trần; màu lấy từ chủ thể và mỗi màu mang nghĩa của chương đó.'],
  'place-carries-it': ['Nơi chốn tự nói', 'Với một nơi chốn, bức ảnh là lập luận. Một ảnh tràn viền chỗ bạn sẽ đứng; thiết kế lùi lại, chữ nhỏ ở mép như tên phim.'],
  'page-is-the-object': ['Trang chính là vật thể', 'Dựng trang thành chính món đồ in đã có trong thế giới của chủ thể: thiệp mời, thực đơn, vé, bìa đĩa, hóa đơn, tờ đề cương.'],
  'one-motif': ['Một họa tiết', 'Lấy một hình dạng từ chủ thể (tròn, vòm, vát, sọc, khấc) và để nó điều khiển cả hệ thống ở ba bốn cỡ rất khác nhau.'],
  'product-performs': ['Sản phẩm tự trình diễn', 'Phần mềm thuyết phục nhất khi đang làm việc trước mắt bạn: những mảnh sản phẩm thật, chạy được, phản hồi con trỏ.'],
  'quiet-instrument': ['Nhạc cụ trầm lặng', 'Tiết chế triệt để: tiêu đề chỉ hơi lớn hơn chữ thường, một cột hẹp, rất nhiều khoảng trống. Sự kiềm chế chính là lời khẳng định.'],
  'hero-object': ['Vật thể, thật lớn', 'Cho thấy món đồ, lớn hơn mức hợp lý: một vật được chụp lấp đầy màn hình, bị mép cắt; chữ nhỏ nép bên cạnh.'],
  'specimen-catalogue': ['Danh mục mẫu vật', 'Trình bày sản phẩm như sách nhận dạng chim: mỗi món đứng riêng trên một màu phẳng, cùng tỉ lệ, cùng góc, gọi tên giản dị.'],
  'borrowed-category': ['Khoác áo ngành khác', 'Chỉ đạo nghệ thuật cho chủ thể như thể nó thuộc một ngành sống động hơn, rồi mượn trọn phong thái của ngành đó.'],
  'contact-sheet': ['Tờ in thử', 'Cho thấy mọi thứ cùng lúc, nhỏ, theo thứ tự, như tờ in thử của nhiếp ảnh gia. Khối lượng và sự nhất quán là thông điệp.'],
  'editorial-report': ['Bản báo cáo in', 'Dàn trang như một báo cáo hay bài tạp chí được thiết kế kỹ: ảnh đầu trang, tiêu đề lớn, chữ bám một trục cột nghiêm ngặt.'],
  'loud-flat-poster': ['Áp phích phẳng, lớn tiếng', 'Thẳng thắn như áp phích đường phố: màu bão hòa phẳng, chữ đậm nhất có thể, câu ngắn, ảnh cắt dán. Kỷ luật ở lưới bên dưới.'],
  'split-stage': ['Sân khấu chia đôi', 'Một nửa màn hình không bao giờ di chuyển (ảnh cố định), nửa kia là cột chữ cuộn bình thản.'],
  'dense-tiles': ['Bảng ô ngăn nắp', 'Cả trang là một bảng ô khít nhau, mỗi ô một thứ thật; không có hero, mắt tự dạo quanh. Kích thước ô theo hệ thống nghiêm ngặt.'],
  'uneven-photographs': ['Ảnh to nhỏ so le', 'Ảnh được đặt như ảnh in trên tường phòng tranh, mỗi tấm một cỡ một vị trí, nhưng vẫn nằm trên một lưới cảm nhận được.'],
  'dark-room': ['Căn phòng tối', 'Một nền tối từ trên xuống dưới, trong đó là những vật được chiếu sáng như hiện vật trong phòng tranh mờ.'],
  'type-only-statement': ['Chỉ có chữ', 'Màn hình đầu chỉ gồm chữ, màu và khoảng trống, đủ hay để không ai nhớ đến ảnh. Ảnh đến sau, lớn và ít.'],
};

// ---------- ngẫu nhiên có seed ----------
let seed = opt('seed') !== undefined && opt('seed') !== true ? Number(opt('seed')) : randomInt(1, 2 ** 31 - 1);
const startSeed = seed;
const rnd = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const pick = (a) => a[Math.floor(rnd() * a.length)];

// ---------- lịch sử ----------
const HIST = process.env.THIET_KE_LICH_SU || join(homedir(), '.thiet-ke-web', 'lich-su.json');
const readHist = () => { try { return JSON.parse(readFileSync(HIST, 'utf8')); } catch { return []; } };
const writeHist = (e) => { try { mkdirSync(dirname(HIST), { recursive: true }); const h = readHist(); h.unshift(e); writeFileSync(HIST, JSON.stringify(h.slice(0, 24), null, 1)); } catch { /* không ghi được lịch sử thì bỏ qua */ } };
const hist = readHist();
const recent = (k, n) => hist.slice(0, Math.max(0, n)).map((h) => h[k]).filter(Boolean);
const fresh = (pool, rec) => { const f = pool.filter((x) => !rec.includes(x.id)); return f.length ? f : pool; };

// ---------- liệt kê ----------
const ds = opt('danh-sach');
if (ds) {
  if (ds === 'nganh') { for (const [vi, en] of Object.entries(NGANH)) console.log(`${vi.padEnd(22)} → ${en}`); }
  else if (ds === 'giong') { for (const [vi, en] of Object.entries(GIONG)) console.log(`${vi.padEnd(12)} → ${en}`); }
  else if (ds === 'phan') { for (const [vi, en] of Object.entries(VAI)) console.log(`${vi.padEnd(16)} → ${en}`); }
  else if (ds === 'co') { for (const [vi, en] of Object.entries(CO)) console.log(`${vi.padEnd(14)} → ${en}`); }
  else for (const d of L.directions) console.log(`${d.id.padEnd(22)} ${HUONG_VI[d.id]?.[0] || d.name} — giọng: ${d.tones.join(', ')}`);
  process.exit(0);
}

// ---------- logic rút ----------
const imageryMode = (inp) => {
  if (inp.have.includes('product-photo') || inp.have.includes('photography')) return 'own';
  if (['saas', 'dev-tool', 'ai-product', 'consumer-app', 'finance'].includes(inp.sector)) return 'interface';
  if (['physical-product', 'ecommerce'].includes(inp.sector)) return 'no-product-photo';
  return 'atmosphere';
};
const pictureLed = (x) => (x.tags || []).includes('photo-led') || (x.tags || []).includes('object-led');
const worksWithoutPictures = (x) => !pictureLed(x) || (x.tags || []).some((t) => ['ui-led', 'type-led', 'colour-field'].includes(t));
const softwareOnly = (x) => (x.directions || [])[0] === 'product-performs' || (x.tags || []).includes('ui-led') || /data-ui|interface fragment/i.test(x.blueprint || '');

function directionPool(inp) {
  const has = (n) => inp.have.includes(n) || n === 'photography';
  let pool = L.directions.filter((d) => (d.sectors.includes(inp.sector) || d.sectors.includes('*')) && !inp.avoid.includes(d.id));
  const ok = pool.filter((d) => (d.needs || []).every(has)); if (ok.length) pool = ok;
  const mode = imageryMode(inp);
  if (mode === 'interface' || mode === 'no-product-photo') { const plain = pool.filter((d) => !d.needsPictures); if (plain.length >= 3) pool = plain; }
  if (inp.tone) { const toned = pool.filter((d) => (d.tones || []).includes(inp.tone)); if (toned.length >= 2) pool = toned; }
  if (!pool.length) pool = L.directions.filter((d) => !inp.avoid.includes(d.id));
  return pool;
}
function dealHero(dir, inp, ex = []) {
  let pool = L.heroes.filter((h) => (dir.heroes || []).includes(h.id) || (h.directions || []).includes(dir.id)); if (!pool.length) pool = L.heroes;
  if (imageryMode(inp) !== 'interface' && !inp.have.includes('product-ui')) { const p = pool.filter((h) => !softwareOnly(h)); if (p.length) pool = p; }
  const ok = pool.filter((h) => !ex.includes(h.id) && (h.needs || []).every((n) => n === 'photography' || inp.have.includes(n)));
  return pick(fresh(ok.length ? ok : pool, recent('hero', 3)));
}
function dealType(dir, ex = []) {
  let pool = L.type.filter((t) => (dir.type || []).includes(t.id) || (dir.typeClasses || []).includes(t.class)); if (!pool.length) pool = L.type;
  const p = pool.filter((t) => !ex.includes(t.id));
  return pick(fresh(p.length ? p : pool, recent('type', Math.min(6, pool.length - 1))));
}
function dealPalette(dir, ex = []) {
  let pool = L.palettes.filter((p) => (dir.palettes || []).includes(p.id) || (p.tags || []).some((t) => (dir.paletteTags || []).includes(t))); if (!pool.length) pool = L.palettes;
  const p = pool.filter((x) => !ex.includes(x.id));
  return pick(fresh(p.length ? p : pool, recent('palette', Math.min(6, pool.length - 1))));
}
function sectionPool(dir, role, inp) {
  let pool = L.sections.filter((s) => s.role === role); if (!pool.length) return [];
  const mode = imageryMode(inp);
  const ok = pool.filter((s) => (s.needs || []).every((n) => n === 'photography' || inp.have.includes(n) || (n === 'product-ui' && mode === 'interface'))); if (ok.length) pool = ok;
  if (mode !== 'interface' && !inp.have.includes('product-ui')) { const p = pool.filter((s) => !softwareOnly(s)); if (p.length) pool = p; }
  if (mode === 'interface' || mode === 'no-product-photo') {
    const honest = pool.filter((s) => (mode === 'interface' ? worksWithoutPictures(s) : !(s.tags || []).includes('object-led') || worksWithoutPictures(s)));
    if (honest.length >= 2) pool = honest;
  }
  const byDir = pool.filter((s) => (s.directions || []).includes(dir.id)); if (byDir.length) return byDir;
  const byTag = pool.filter((s) => (s.tags || []).some((t) => (dir.sectionTags || []).includes(t)));
  return byTag.length ? byTag : pool;
}
function dealSection(dir, role, used, prevShape, nextShape, inp) {
  let pool = sectionPool(dir, role, inp); if (!pool.length) return null;
  if (imageryMode(inp) === 'interface') { const ui = pool.filter((s) => (s.tags || []).includes('ui-led')); if (ui.length >= 2 && rnd() < 0.6) pool = ui; }
  const unused = pool.filter((s) => !used.includes(s.id)); if (unused.length) pool = unused;
  const varied = pool.filter((s) => s.shape !== prevShape && s.shape !== nextShape); if (varied.length) pool = varied;
  return pick(pool);
}
function deal(inp) {
  const forced = inp.direction ? L.directions.find((d) => d.id === inp.direction) : null;
  const pool = directionPool(inp);
  const dir = forced || pick(fresh(pool, recent('direction', Math.min(5, pool.length - 1))));
  const s = { phienBan: 1, luc: new Date().toISOString(), seed: startSeed, veLai: [], input: inp, imagery: imageryMode(inp), direction: dir };
  s.hero = dealHero(dir, inp);
  s.type = inp.keep.includes('type') ? null : dealType(dir);
  s.palette = inp.keep.includes('palette') ? null : dealPalette(dir);
  s.motion = L.motions.find((m) => m.id === (s.hero?.motion || dir.motion)) || L.motions.find((m) => m.id === dir.motion) || null;
  s.sections = [];
  for (const role of inp.sections) {
    const sec = dealSection(dir, role, s.sections.map((x) => x.id), s.sections.at(-1)?.shape, null, inp);
    s.sections.push(sec || { id: null, role, name: role, blueprint: null });
  }
  return s;
}

// ---------- điều chỉnh: chỗ bản thiết kế mâu thuẫn với luật nhà ----------
function dieuChinh(bp, s) {
  const text = [bp.blueprint, bp.mobile, bp.headline].filter(Boolean).join(' ');
  const n = [];
  if (/\b(9|10|11|12)(?:\.\d)?px\b(?!\s*(?:gaps?|gutters?|margins?|padding|radius|corners?|apart|inset|offset|tall|wide|thick|borders?|rules?|line\b|dots?|of|between|below|above|under|from))/.test(text)) n.push('Có chữ 9–12px: dùng cỡ nhỏ nhất của trang (từ 13px).');
  if (/\b(14|15)px\s*(?:paragraphs?|body|text|descriptions?|copy|sentences?|answers?)/i.test(text)) n.push('Đoạn văn 14–15px: chữ thân bài từ 16px.');
  if (/\d{1,2}% (?:opacity|black|ink|grey|gray|white)|opacity:? ?0?\.\d/i.test(text)) n.push('Có làm mờ chữ: mọi chữ người xem đọc phải đạt tương phản 4.5:1; mục không hoạt động mờ không dưới 40%.');
  if (/\d+px (?:corner )?radius|radius (?:of )?\d+px|\brounded\b|\bpill/i.test(text)) n.push('Tự đặt bo góc riêng: dùng một bo góc và một kiểu nút cho cả trang.');
  if (/\b(?:serif|sans-serif|condensed|grotesk|italic|monospace|mono|all caps|uppercase|capitals|script)\b/i.test(text)) n.push(s.type ? `Nhắc đến kiểu chữ: dùng font đã rút (tiêu đề ${s.type.display.family}, thân bài ${s.type.text.family}).` : 'Nhắc đến kiểu chữ: dùng font của thương hiệu.');
  if (/\b(green|red|blue|yellow|orange|pink|purple|teal|navy|cream|beige|brown|grey|gray)\b/i.test(text)) n.push('Nhắc đến màu cụ thể: quy về vai trò của bảng màu (--bg, --surface, --ink, --muted, --accent chỉ cho nút chính).');
  if (/(?<!\b(?:no|without|never|not|nor) (?:a |any )?)\b(?:rule|rules|hairline|border|borders|divider|thin line|1px line)\b/i.test(text)) n.push('Có kẻ đường/viền: chỉ giữ trong bảng, form, hoặc mảnh giao diện sản phẩm; chỗ khác tách bằng khoảng trống hoặc bậc tông nền.');
  if (/shadow|glow/i.test(text)) n.push('Có đổ bóng: chỉ cho thứ đang nổi trên trang (menu, dialog), không cho vật đứng yên.');
  if (/\b0[1-9]\b(?![:.,]\d)|numbered|index number/i.test(text)) n.push('Có đánh số 01, 02: bỏ số trừ khi là dữ liệu thật (giá, ngày, số lượng).');
  if (/leading 0\.[6-9]|line-height:? ?0\.[6-9]/i.test(text)) n.push('Leading dưới 1.0: với tiếng Việt, kiểm tra dấu chồng trên chữ hoa (Ế, Ỗ, Ặ) không bị cắt hay đụng dòng trên; thường cần 1.05–1.15.');
  if (/tops? of the (?:letters|word|name|wordmark)|(?:letters|wordmark|name|word)\b[^.;]{0,30}\b(?:sliced|cut|cropped|clipped)[^.;]{0,20}\btop/i.test(text)) n.push('Cắt phần trên chữ: không làm (người xem đọc là lỗi, và với tiếng Việt sẽ mất dấu). Cắt ở cạnh dưới hoặc bên hông.');
  if (bp.archetype && /single action[^.;]{0,40}?\b(?:text link|underlined (?:text )?link)/i.test(text)) n.push('Hành động chính là link chữ: trên màn hình đầu phải là nút thật (cao từ 44px), đặt ở chỗ link.');
  return n;
}

// ---------- in phiếu ----------
const VAI_TEN = (r) => VAI_VI[r] || r;
function render(s) {
  const d = s.direction; const o = []; const p = (x = '') => o.push(x);
  const [tenVi, yVi] = HUONG_VI[d.id] || [d.name, ''];
  p(`# PHIẾU HƯỚNG THIẾT KẾ: ${tenVi} (\`${d.id}\`)`);
  p(`seed ${s.seed} · rút ngày ${s.luc.slice(0, 10)} · ngành ${s.input.sector}${s.input.tone ? ' · giọng ' + s.input.tone : ''}${s.veLai.length ? ' · đã vẽ lại: ' + s.veLai.join(', ') : ''}`);
  if (s.input.brief) p(`Mô tả: ${s.input.brief}`);
  p();
  p('| | |'); p('| --- | --- |');
  p(`| Hướng | ${tenVi} |`);
  p(`| Hero | ${s.hero.name} (\`${s.hero.id}\`) |`);
  p(`| Chữ | ${s.type ? s.type.name : 'giữ của thương hiệu'} |`);
  p(`| Màu | ${s.palette ? s.palette.name : 'giữ của thương hiệu'} |`);
  p(`| Các section | ${s.sections.map((x) => VAI_TEN(x.role) + (x.name && x.name !== x.role ? ' (' + x.name + ')' : '')).join(' → ')} |`);
  p(`| Chuyển động chủ đạo | ${s.motion ? s.motion.name + ' (`' + s.motion.id + '`)' : 'không'} |`);
  p();
  p('**Đây là hướng của lần dựng này. Nhận lấy nó.** Đừng trộn với bố cục bạn vốn định làm, và đừng vẽ lại chỉ vì lạ: lạ chính là mục đích. Chỉ vẽ lại một ô khi nó trái với ràng buộc thương hiệu hoặc cần tài sản không tồn tại, và ghi lý do vào báo cáo.');
  p();
  p('Các phần của phiếu được viết riêng nên đôi chỗ vênh nhau. Phân xử theo thứ tự: **luật nhà** (SKILL.md và tai-lieu/) → **hướng** (ý tưởng, thói quen bố cục, chỗ đặt màu nhấn) → **hệ chữ và bảng màu** → **bản thiết kế hero** → **bản thiết kế section**. Lấy hình học (cột, tỉ lệ, cái gì ở đâu) từ bản thiết kế; mọi thứ khác lấy từ các tầng trên. Mọi cỡ chữ quy về tối đa năm bậc; một kiểu nút, một bo góc, một cặp lề cho cả trang.');
  p();
  p('Phần mô tả chi tiết bên dưới giữ nguyên tiếng Anh vì là dữ liệu đo đạc gốc; đọc như số liệu kỹ thuật.');
  p();
  p('## 1. Ý tưởng'); if (yVi) p(yVi); p(); p(d.idea); p();
  p('Viết ngay một câu vào ghi chú: **"Trên trang này, [thứ chỉ chủ thể này có] trở thành [thiết bị mà hướng này gọi đến]."** Điền chỗ trống đầu từ danh sách kiểm kê (tên và ý nghĩa của tên, con phố, các con số, ràng buộc riêng). Rồi đặt tên đối thủ gần nhất vào câu: nếu câu vẫn đúng, ý tưởng là của cả ngành chứ không phải của khách hàng. Sau đó gọi tên "một thứ sống động" người xem có thể làm trên trang.');
  p();
  p('## 2. Bố cục'); p(d.composition); if (d.pitfalls) { p(); p('**Cạm bẫy:** ' + d.pitfalls); } if (d.richness) { p(); p('**Độ đầy đặn:** ' + d.richness); } p();
  if (s.type) {
    const t = s.type;
    p(`## 3. Chữ: ${t.name}`); p(t.note);
    p('```html'); for (const l of [...new Set([t.display.css, t.text.css].filter(Boolean))]) p(l); p('```');
    p(`- Tiêu đề: **${t.display.family}** (${t.display.source}): ${t.display.settings}`);
    p(`- Thân bài: **${t.text.family}** (${t.text.source}): ${t.text.settings}`);
    if (t.scale) { p('```css'); p(':root {'); for (const [k, v] of Object.entries(t.scale)) p(`  --${k}: ${v};`); p('}'); p('```'); }
    if (d.typography) p(d.typography);
    p();
    const fontshare = [t.display, t.text].some((x) => x.source === 'fontshare');
    p(`**Nếu nội dung có tiếng Việt: bắt buộc kiểm tra font có đủ dấu trước khi dựng** (xem tai-lieu/03-chu.md, mục tiếng Việt).${fontshare ? ' Font này lấy từ Fontshare; phần lớn font Fontshare KHÔNG có dấu tiếng Việt, khả năng cao phải vẽ lại ô chữ bằng `--ve-lai chu`.' : ' Font này lấy từ Google Fonts: kiểm tra có subset `vietnamese`.'}`);
    p();
  } else { p('## 3. Chữ'); p('Giữ của thương hiệu. ' + (d.typography || '')); p(); }
  if (s.palette) {
    const c = s.palette;
    p(`## 4. Màu: ${c.name}`); p('```css'); p(':root {');
    for (const k of ['bg', 'surface', 'ink', 'muted', 'accent', 'accentInk']) if (c[k]) p(`  --${k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())}: ${c[k]};`);
    (c.fields || []).forEach((f, i) => p(`  --field-${i + 1}: ${f.bg};${f.ink ? `  --field-${i + 1}-ink: ${f.ink};` : ''}`));
    p('}'); p('```'); p(c.note); if (d.colour) p(d.colour); p();
  } else { p('## 4. Màu'); p('Giữ của thương hiệu. ' + (d.colour || '')); p(); }
  p('## 5. Hình ảnh');
  const MODE = {
    interface: '**Chủ thể là phần mềm và chưa có ảnh chụp màn hình, nên hình ảnh của nó chính là giao diện của nó.** Ở mọi chỗ phiếu nói "ảnh", dựng một mảnh sản phẩm bằng HTML ở kích thước thật (nhãn thật, số cộng lại khớp, một mục đang được chọn), theo tai-lieu/02-man-hinh-ung-dung.md.',
    'no-product-photo': '**Chưa có ảnh sản phẩm và không được làm giả.** Ở chỗ cần ảnh món đồ, vẽ món đồ bằng SVG: các mảnh thành hình phẳng, lớn, một ngôn ngữ đồ họa, đúng màu làm nó đáng mua; đặt giữa ảnh thật về thế giới của nó (tai-lieu/10-hinh-anh.md).',
    atmosphere: '**Dự án chưa có ảnh riêng.** Ưu tiên ảnh thật về thế giới của chủ thể từ kho ảnh mở (bưu thiếp cũ về con phố, bản đồ cũ, chất liệu cận cảnh, hiện vật bảo tàng), tải về và ghi nguồn trên trang. Xem tai-lieu/10-hinh-anh.md.',
    own: '**Dùng ảnh của chính dự án ở mọi ô ảnh.** Ô nào thiếu thì dùng ảnh thật về thế giới của chủ thể từ kho ảnh mở, có ghi nguồn.',
  };
  p(MODE[s.imagery]); p(); if (d.imagery) p(d.imagery); p();
  p('**Mức sàn:** ít nhất bốn ảnh thật trên trang (thường sáu đến mười hai); hình SVG tự vẽ không tính. Một hình ảnh chuyển động nếu có video thật phù hợp.');
  p();
  p(`## 6. Hero: ${s.hero.name}`); p(s.hero.blueprint); if (s.hero.mobile) { p(); p('**Điện thoại:** ' + s.hero.mobile); } if (s.hero.headline) { p(); p('**Tiêu đề:** ' + s.hero.headline); }
  const hn = dieuChinh(s.hero, s); if (hn.length) { p(); p('**Điều chỉnh cho trang này:**'); hn.forEach((x) => p('- ' + x)); }
  p();
  p('## 7. Các section');
  s.sections.forEach((x, i) => {
    p(`### ${i + 1}. ${VAI_TEN(x.role)}${x.name && x.name !== x.role ? ': ' + x.name : ''}${x.id ? ' (`' + x.id + '`)' : ''}`);
    if (!x.blueprint) { p('Thư viện không có bản thiết kế cho vai này; tự dựng theo luật nhà, khác dạng với section kề bên.'); p(); return; }
    p(x.blueprint); if (x.mobile) { p(); p('**Điện thoại:** ' + x.mobile); }
    const sn = dieuChinh(x, s); if (sn.length) { p(); p('**Điều chỉnh cho trang này:**'); sn.forEach((y) => p('- ' + y)); }
    p();
  });
  p('Không có hai section liền nhau cùng bố cục. Mang ý tưởng vào mọi section, kể cả bảng giá, hỏi đáp và chân trang.');
  p();
  p('## 8. Chuyển động');
  if (s.motion) { p(`**${s.motion.name}** (\`${s.motion.id}\`): ${s.motion.description}`); p(); }
  p('Chuyển động dựng sau cùng, theo tai-lieu/06-chuyen-dong.md; công thức trong tai-lieu/07-cong-thuc-chuyen-dong.md (tra bảng theo mã ở trên).');
  return o.join('\n');
}

// ---------- chạy ----------
const save = (s) => { mkdirSync(OUT, { recursive: true }); writeFileSync(SHEET, JSON.stringify(s, null, 1)); };
const loadSheet = () => { if (!existsSync(SHEET)) { console.error(`Chưa có phiếu ở ${SHEET}. Rút một hướng trước.`); process.exit(2); } return JSON.parse(readFileSync(SHEET, 'utf8')); };

if (opt('xem')) { console.log(render(loadSheet())); process.exit(0); }

const alt = opt('thay-the');
if (alt) {
  const s = loadSheet(); const role = VAI[alt] || alt;
  const pool = sectionPool(s.direction, role, s.input);
  const all = L.sections.filter((x) => x.role === role && !pool.includes(x));
  console.log(`# Các bản thiết kế cho vai "${VAI_TEN(role)}"\n\nHợp với hướng hiện tại:`);
  for (const x of pool) console.log(`- \`${x.id}\` ${x.name} [${x.shape}]: ${x.blueprint.slice(0, 160)}…`);
  console.log('\nCác bản khác cùng vai:');
  for (const x of all) console.log(`- \`${x.id}\` ${x.name} [${x.shape}]`);
  console.log(`\nChọn: --ve-lai phan:${alt}=<mã>`);
  process.exit(0);
}

const redraw = opt('ve-lai');
let sheet;
if (redraw) {
  sheet = loadSheet(); const what = String(redraw); const dir = sheet.direction;
  if (what === 'hero') sheet.hero = dealHero(dir, sheet.input, [sheet.hero.id]);
  else if (what === 'chu') sheet.type = dealType(dir, [sheet.type?.id].filter(Boolean));
  else if (what === 'mau') sheet.palette = dealPalette(dir, [sheet.palette?.id].filter(Boolean));
  else if (what === 'huong') { const inp = { ...sheet.input, avoid: [...sheet.input.avoid, dir.id], direction: null }; const veLai = sheet.veLai; sheet = deal(inp); sheet.veLai = veLai; }
  else if (what.startsWith('phan:')) {
    const [raw, wanted] = what.slice(5).split('='); const role = VAI[raw] || raw;
    const i = sheet.sections.findIndex((x) => x.role === role);
    if (i === -1) { console.error(`Phiếu không có section vai "${raw}".`); process.exit(2); }
    if (wanted) {
      const c = L.sections.find((x) => x.id === wanted);
      if (!c) { console.error(`Không có bản thiết kế mã ${wanted}. Xem bằng --thay-the ${raw}.`); process.exit(2); }
      sheet.sections[i] = c.role === role ? c : { ...c, role, name: `${c.name} (mượn từ vai ${c.role})` };
    } else sheet.sections[i] = dealSection(dir, role, sheet.sections.map((x) => x.id), sheet.sections[i - 1]?.shape, sheet.sections[i + 1]?.shape, sheet.input) || sheet.sections[i];
  } else { console.error('Ô không hợp lệ. Dùng: hero, chu, mau, huong, phan:<vai>, phan:<vai>=<mã>.'); process.exit(2); }
  sheet.veLai = [...(sheet.veLai || []), what];
} else {
  const rawSector = String(opt('nganh', ''));
  const sector = NGANH[rawSector] || rawSector;
  if (!SECTORS.includes(sector)) { console.error('Thiếu --nganh. Chọn ngành gần nhất (xem --danh-sach nganh); dùng "khac" khi không ngành nào hợp.'); process.exit(2); }
  const rawTone = typeof opt('giong') === 'string' ? opt('giong') : null;
  const tone = rawTone ? (GIONG[rawTone] || rawTone) : null;
  const sections = list(opt('phan')).map((r) => VAI[r] || r).filter((r) => r !== 'hero');
  const inp = {
    brief: typeof opt('mo-ta') === 'string' ? opt('mo-ta') : '', sector,
    tone: TONES.includes(tone) ? tone : null,
    have: list(opt('co')).map((x) => CO[x] || x),
    keep: list(opt('giu')).map((x) => ({ mau: 'palette', chu: 'type' }[x] || x)),
    avoid: list(opt('tranh')),
    sections: sections.length ? sections : DEFAULT_SECTIONS[sector],
    direction: typeof opt('huong') === 'string' ? opt('huong') : null,
  };
  if (inp.direction && !L.directions.some((d) => d.id === inp.direction)) { console.error(`Không có hướng mã ${inp.direction}. Xem --danh-sach huong.`); process.exit(2); }
  if (!inp.direction) {
    const n = Math.max(2, Math.min(5, Number(opt('lua-chon')) || 3));
    const pool = directionPool(inp); const out = [];
    let rest = fresh(pool, recent('direction', Math.min(5, pool.length - n)));
    while (out.length < n && pool.length > out.length) { if (!rest.length) rest = pool.filter((d) => !out.includes(d)); const d = pick(rest); out.push(d); rest = rest.filter((x) => x !== d); }
    console.log(`# ${n} hướng được rút cho mô tả này\n`);
    console.log('Chọn hướng có cách bố cục mang được một ý tưởng từ danh sách kiểm kê của bạn, không phải hướng quen thuộc nhất. Rồi chạy lại cùng lệnh, thêm `--huong <mã>`.\n');
    for (const d of out) {
      const [ten, y] = HUONG_VI[d.id] || [d.name, ''];
      console.log(`## \`${d.id}\`: ${ten}`); console.log(y);
      if (d.needsPictures) console.log('Cần nhiều ảnh. Không có ảnh riêng thì mỗi ảnh là ảnh thật về thế giới của chủ thể từ kho ảnh mở, hoặc hình bạn tự vẽ.');
      if ((d.needs || []).length) console.log('Cần có: ' + d.needs.join(', '));
      console.log('');
    }
    process.exit(0);
  }
  sheet = deal(inp);
}
save(sheet);
if (!redraw || String(redraw) === 'huong') writeHist({ luc: sheet.luc, direction: sheet.direction.id, type: sheet.type?.id, palette: sheet.palette?.id, hero: sheet.hero?.id, sector: sheet.input.sector });
console.log(render(sheet));
