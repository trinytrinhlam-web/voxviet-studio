// Ảnh đại diện hoạt hình pixel 16×16 (vẽ riêng cho VoxViet, không dùng hình có sẵn).
// Mỗi giọng → một nhân vật cố định: kiểu tóc, màu da, màu tóc, áo, phụ kiện, nụ cười.
// Ký hiệu ô: . trong suốt · S da · s da tối · E mắt · B má hồng · M miệng · H tóc · A phụ kiện · G kính · C áo · c cổ áo

const BASE = [
  "................",
  "................",
  "................",
  "................",
  "....SSSSSSSS....",
  "...SSSSSSSSSS...",
  "...SSSSSSSSSS...",
  "...SSESSSSESS...",
  "..sSSESSSSESSs..",
  "...SSSSSSSSSS...",
  "...SSSSMMSSSS...",
  "....SSSSSSSS....",
  "......ssss......",
  "....CCCccCCC....",
  "..CCCCCCCCCCCC..",
  "..CCCCCCCCCCCC..",
];
const BLUSH = { 9: "...SBSSSSSSBS..." };
const SMILE_U = { 10: "......MSSM......", 11: ".......MM......." };
const GLASSES = { 6: "....GGG..GGG....", 7: "....G.GGGG.G....", 8: "....GGG..GGG...." };

// Kiểu tóc: front vẽ đè lên mặt, back vẽ phía sau mặt.
const BOY = [
  { name: "đầu đinh", front: { 2: ".....HHHHHH.....", 3: "....HHHHHHHH....", 4: "...HHHHHHHHHH...", 5: "...HH......HH...", 6: "...H........H..." } },
  { name: "tóc dựng", front: { 1: "....H..H..H.....", 2: "....HHHHHHHH....", 3: "...HHHHHHHHHH...", 4: "...HHHHHHHHHH...", 5: "...HHH.HH.HHH...", 6: "...H........H..." } },
  { name: "mái lệch", front: { 2: ".....HHHHHHH....", 3: "....HHHHHHHHH...", 4: "...HHHHHHHHHHH..", 5: "...HHHHHHH..HH..", 6: "...HH.......H..." } },
  { name: "mũ lưỡi trai", front: { 2: ".....AAAAAA.....", 3: "....AAAAAAAA....", 4: "...AAAAAAAAAAAA.", 5: "...HH......HH...", 6: "...H........H..." } },
  { name: "tóc xoăn", front: { 1: ".....H.HH.H.....", 2: "....HHHHHHHH....", 3: "...HHHHHHHHHH...", 4: "..HHHHHHHHHHHH..", 5: "..HHH......HHH..", 6: "..HH........HH.." } },
];
const LONG_BACK = { ...Object.fromEntries([5, 6, 7, 8, 9, 10, 11, 12, 13].map((r) => [r, ".HHH........HHH."])), 14: ".HH..........HH." };
const LASHES = { 6: "....E......E...." };
const GIRL = [
  { name: "tóc dài", back: LONG_BACK, front: { 2: ".....HHHHHH.....", 3: "....HHHHHHHH....", 4: "...HHHHHHHHHH...", 5: "...HHHH..HHHH...", 6: "...HH......HH...", 7: "...H........H..." } },
  { name: "hai bím", front: { 2: ".....HHHHHH.....", 3: "....HHHHHHHH....", 4: "...HHHHHHHHHH...", 5: "..AHHHHHHHHHHA..", 6: ".HHH........HHH.", 7: ".HH..........HH.", 8: ".HH..........HH.", 9: ".HH..........HH.", 10: "..A..........A..", 11: "..H..........H.." } },
  { name: "búi tó", front: { 0: "......HHHH......", 1: "......HHHHA.....", 2: ".....HHHHHHA....", 3: "....HHHHHHHH....", 4: "...HHHHHHHHHH...", 5: "..HHHHHHHHHHHH..", 6: "..HH........HH..", 7: "..HH........HH..", 8: "..HH........HH..", 9: "..H..........H..", 10: "..H..........H.." } },
  { name: "tóc ngắn có nơ", front: { 1: "..........AA.AA.", 2: ".....HHHHHHAAA..", 3: "....HHHHHHAA.AA.", 4: "...HHHHHHHHHH...", 5: "..HHHHHH.HHHHH..", 6: "..HH........HH..", 7: "..HH........HH..", 8: "..HH........HH..", 9: "..HH........HH..", 10: "..H..........H.." } },
  { name: "tóc xoăn dài có băng đô", back: { ...Object.fromEntries([6, 7, 8, 9, 10, 11, 12].map((r) => [r, "..HH........HH.."])), 13: ".HHH........HHH.", 14: ".HH..........HH." },
    front: { 2: ".....HHHHHH.....", 3: "....AAAAAAAA....", 4: "...HHHHHHHHHH...", 5: "...HH.HHHH.HH...", 6: "..HH........HH.." } },
];

const SKIN = [["#f7d7bd", "#e9b996"], ["#efc29f", "#d9a17a"], ["#dca37c", "#c08360"], ["#b98060", "#9a6447"]];
const HAIR = ["#2a201b", "#47302a", "#6e4428", "#1f2638", "#b07a35", "#7d3b33"];
const BOY_SHIRT = [["#4f7fdc", "#3a63b3"], ["#3ea37b", "#2c8060"], ["#2f8fab", "#236f86"], ["#6c70d8", "#5155b0"], ["#e08a3c", "#b86c28"]];
const GIRL_SHIRT = [["#e06a9b", "#bd4f7d"], ["#c98ad8", "#a56ab5"], ["#f08b5e", "#cc6c42"], ["#5bb8a6", "#439686"], ["#e45f7c", "#c04661"]];
const BOY_ACC = ["#e2483d", "#3b7be0", "#2fa36d"];
const GIRL_ACC = ["#ff5f8f", "#ffd34d", "#8f7cff", "#ff8a3d"];
const FIXED = { E: "#1c1b25", M: "#b4444f", B: "#f39aa9", G: "#20222c" };

function hash(str) {
  let h = 2166136261;
  for (const ch of str) h = Math.imul(h ^ ch.codePointAt(0), 16777619);
  return h >>> 0;
}
function rng(seed) {
  let s = seed || 1;
  return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; };
}
const pick = (r, arr) => arr[Math.floor(r() * arr.length) % arr.length];

const cache = new Map();

/** Trả về chuỗi <svg> nhân vật pixel cho `key` (cố định). sex: "nam" | "nu" | "" (đoán theo key). */
export function pixelAvatarSVG(key, sex = "") {
  const id = `${key}|${sex}`;
  if (cache.has(id)) return cache.get(id);
  const r = rng(hash(key));
  const s = sex === "nam" || sex === "nu" ? sex : (r() < 0.5 ? "nam" : "nu");
  const style = pick(r, s === "nam" ? BOY : GIRL);
  const [skin, skinDark] = pick(r, SKIN);
  const [shirt, collar] = pick(r, s === "nam" ? BOY_SHIRT : GIRL_SHIRT);
  const pal = { ...FIXED, S: skin, s: skinDark, H: pick(r, HAIR), A: pick(r, s === "nam" ? BOY_ACC : GIRL_ACC), C: shirt, c: collar };
  const grid = BASE.map((row) => row.split(""));
  const paint = (layer) => {
    for (const [row, line] of Object.entries(layer || {})) {
      [...line].forEach((ch, x) => { if (ch !== ".") grid[+row][x] = ch; });
    }
  };
  // vẽ tóc phía sau trước mặt: chỉ tô ô còn trống của nền
  for (const [row, line] of Object.entries(style.back || {})) {
    [...line].forEach((ch, x) => { if (ch !== "." && grid[+row][x] === ".") grid[+row][x] = ch; });
  }
  if (s === "nu" || r() < 0.25) paint(BLUSH);
  if (s === "nu") paint(LASHES);
  if (r() < 0.45) paint(SMILE_U);
  if (s === "nam" && style.name !== "mũ lưỡi trai" && r() < 0.3) paint(GLASSES);
  paint(style.front);
  // gộp các ô liền nhau cùng màu thành một hình chữ nhật cho gọn
  let rects = "";
  grid.forEach((row, y) => {
    for (let x = 0; x < 16;) {
      const ch = row[x];
      let w = 1;
      while (x + w < 16 && row[x + w] === ch) w++;
      if (ch !== ".") rects += `<rect x="${x}" y="${y}" width="${w}" height="1" fill="${pal[ch]}"/>`;
      x += w;
    }
  });
  // khung nhìn hơi phóng vào khuôn mặt (cắt bớt mép trống) cho nhân vật to, rõ hơn
  const svg = `<svg viewBox="1 0.5 14 14.5" shape-rendering="crispEdges" aria-hidden="true">${rects}</svg>`;
  cache.set(id, { svg, sex: s });
  return cache.get(id);
}
