#!/usr/bin/env bash
# PHƯƠNG ÁN DỰ PHÒNG cho máy có Node cũ hơn 22. Ưu tiên dùng chup-man-hinh.mjs.
# Hạn chế: Chrome headless không thu hẹp cửa sổ dưới 500px, nên ảnh "điện thoại 390px" thực ra là trang
# rộng 500px bị cắt; ảnh cả trang dùng cửa sổ rất cao nên các section 100svh sẽ phình to.
#
# Chụp màn hình một trang ở ba độ rộng (1440, 768, 390) bằng Chrome/Chromium/Edge có sẵn trên máy.
# Không cài gì, không tải gì. Ảnh lưu vào .thiet-ke/anh/ của dự án.
#
# Cách dùng (từ thư mục gốc dự án):
#   bash <skill>/scripts/chup-man-hinh.sh <url hoặc đường-dẫn/index.html> [tên-lần-chụp]
#   Ví dụ: bash .../chup-man-hinh.sh http://localhost:5173 vong-1
#          bash .../chup-man-hinh.sh dist/index.html truoc
# Biến môi trường CHROME=/đường/dẫn/chrome để chỉ định trình duyệt.

set -u
DICH="${1:-}"
TEN="${2:-$(date +%H%M%S)}"
if [ -z "$DICH" ]; then echo "Cần URL hoặc đường dẫn file HTML."; exit 2; fi
if [ -f "$DICH" ]; then DICH="file://$(cd "$(dirname "$DICH")" && pwd)/$(basename "$DICH")"; fi

CHROME="${CHROME:-}"
if [ -z "$CHROME" ]; then
  for b in google-chrome google-chrome-stable chromium chromium-browser microsoft-edge msedge; do
    command -v "$b" >/dev/null 2>&1 && CHROME="$(command -v "$b")" && break
  done
fi
if [ -z "$CHROME" ]; then
  for p in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
           "/c/Program Files/Google/Chrome/Application/chrome.exe" \
           "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"; do
    [ -x "$p" ] && CHROME="$p" && break
  done
fi
if [ -z "$CHROME" ]; then
  echo "Không tìm thấy Chrome, Chromium hay Edge. Đặt biến CHROME=/đường/dẫn hoặc chụp bằng công cụ trình duyệt bạn đang có."
  exit 2
fi

OUT=".thiet-ke/anh/$TEN"
mkdir -p "$OUT"
HOSO="$(mktemp -d)"
THEM=()
[ "$(id -u 2>/dev/null)" = "0" ] && THEM+=(--no-sandbox)   # Chrome từ chối chạy dưới root nếu thiếu cờ này
trap 'rm -rf "$HOSO"' EXIT

chup() { # tên rộng cao [cờ thêm]
  local ten="$1" w="$2" h="$3"; shift 3
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run --no-default-browser-check \
    --user-data-dir="$HOSO" --window-size="$w,$h" --virtual-time-budget=4000 \
    --screenshot="$OUT/$ten.png" "${THEM[@]}" "$@" "$DICH" >/dev/null 2>&1
  if [ -s "$OUT/$ten.png" ]; then echo "  $OUT/$ten.png"; else echo "  (không chụp được $ten)"; fi
}

echo "Chụp $DICH bằng $(basename "$CHROME"):"
# Lượt khởi động: lần chạy lạnh đầu tiên của Chrome đôi khi chụp trước khi animation chạy xong.
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run --user-data-dir="$HOSO" \
  --window-size=800,600 --virtual-time-budget=2000 --screenshot="$HOSO/khoi-dong.png" "${THEM[@]}" "$DICH" >/dev/null 2>&1
chup "desktop-man-dau" 1440 900
chup "desktop-ca-trang" 1440 7000
chup "tablet-man-dau" 768 1024
chup "dien-thoai-man-dau" 390 844
chup "dien-thoai-ca-trang" 390 9000
chup "giam-chuyen-dong" 1440 900 --force-prefers-reduced-motion
echo
echo "Mở từng ảnh để xem (ảnh cả trang có thể dư nền trống ở cuối nếu trang ngắn hơn khung chụp)."
echo "Lưu ý: ảnh cả trang dùng cửa sổ rất cao nên mọi hiệu ứng lộ diện khi cuộn đều đã chạy; nếu vẫn thấy một dải trống, đó là lỗi thật."
echo "Kiểm tra ảnh giam-chuyen-dong: mọi nội dung phải hiện đủ."
echo "Nếu một tiêu đề có hiệu ứng mở trang trông như bị thiếu, chạy lại lệnh một lần trước khi kết luận là lỗi."
