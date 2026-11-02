# VoxViet Studio — bước cài đặt chạy sau khi trình cài chép file (cũng chạy tay được để sửa bản cài):
#   powershell -ExecutionPolicy Bypass -File installer\setup.ps1 [-MigrateFrom "E:\VoiceTriny\voxviet-studio"]
# Việc làm: nối GitHub (để nhận cập nhật) → Python 3.12 riêng → PyTorch GPU nếu có card NVIDIA
# → thư viện → chuyển kho giọng + mô hình từ bản cũ → kiểm tra. Mô hình lõi giọng tải ở lần mở đầu.
param(
    [string]$AppDir = (Split-Path -Parent $PSScriptRoot),
    [string]$MigrateFrom = "",
    [string]$RepoUrl = "https://github.com/trinytrinhlam-web/voxviet-studio.git",
    [switch]$SkipGit,
    [switch]$CpuOnly,
    [switch]$NoPause
)

# Lệnh ngoài (git, uv) ghi tiến độ ra stderr: không coi là lỗi — kiểm tra mã thoát thay vào đó.
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch {}
Set-Location -LiteralPath $AppDir
New-Item -ItemType Directory -Force -Path "$AppDir\data\.local" -ErrorAction Stop | Out-Null
try { Start-Transcript -Path "$AppDir\data\.local\setup.log" -Force | Out-Null } catch {}

$Runtime = Join-Path $AppDir "runtime"
$Uv = Join-Path $Runtime "uv.exe"
$Py = Join-Path $AppDir ".venv\Scripts\python.exe"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $Runtime "python"
$env:UV_CACHE_DIR = Join-Path $Runtime "cache"
$env:UV_PYTHON_PREFERENCE = "only-managed"   # không dùng Python có sẵn trên máy → bản cài độc lập
$env:UV_NO_PROGRESS = "1"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"   # in tiếng Việt qua đường ống (mặc định cp1252 → lỗi)
$Warnings = New-Object System.Collections.Generic.List[string]

function Step($n, $text) { Write-Host ""; Write-Host "[$n/7] $text" -ForegroundColor Yellow }
function Warn($text) { Write-Host "  ! $text" -ForegroundColor DarkYellow; $script:Warnings.Add($text) }
function Run($exe, [string[]]$argv, $what) {
    & $exe @argv | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "$what thất bại (mã $LASTEXITCODE)." }
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

try {
    Write-Host "===== VoxViet Studio — cài đặt vào $AppDir =====" -ForegroundColor Cyan
    if (-not (Test-Path -LiteralPath $Uv)) { throw "Thiếu $Uv — hãy chạy lại trình cài đặt." }

    # ── 1. GitHub: nhận bản cập nhật + đồng bộ kho giọng giữa các máy ──
    Step 1 "Kết nối GitHub"
    if ($SkipGit) {
        Write-Host "  Bỏ qua (theo yêu cầu)."
    } elseif (Test-Path -LiteralPath "$AppDir\.git") {
        Write-Host "  Đã kết nối từ trước — giữ nguyên."
    } else {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            Write-Host "  Chưa có Git — đang cài bằng winget…"
            try { winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements | Out-Host } catch {}
            Refresh-Path
        }
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            Warn "Chưa cài được Git: phần mềm vẫn chạy, nhưng trang Cập nhật chưa dùng được. Cài Git tại https://git-scm.com/download/win rồi bấm 'Kết nối GitHub' trong trang Cập nhật."
        } else {
            Write-Host "  Đang tải mã nguồn mới nhất (có thể hiện cửa sổ đăng nhập GitHub)…"
            $ok = $true
            git init -q; git remote add origin $RepoUrl
            git fetch origin main
            if ($LASTEXITCODE -ne 0) { $ok = $false }
            if ($ok) { git checkout -q -f -B main origin/main; if ($LASTEXITCODE -ne 0) { $ok = $false } }
            if ($ok) {
                git branch -q --set-upstream-to=origin/main main 2>$null
                Write-Host "  Đã kết nối: $(git log -1 --format='%h %s')"
            } else {
                Remove-Item -Recurse -Force -LiteralPath "$AppDir\.git" -ErrorAction SilentlyContinue
                Warn "Chưa kết nối được GitHub (mạng hoặc đăng nhập). Phần mềm vẫn chạy; vào trang Cập nhật → 'Kết nối GitHub' để thử lại."
            }
        }
    }

    # ── 2. Python 3.12 riêng của VoxViet ──
    Step 2 "Python 3.12 riêng cho VoxViet"
    if (-not (Test-Path -LiteralPath $Py)) { Run $Uv @("venv", ".venv", "--python", "3.12") "Tạo môi trường Python" }
    Write-Host "  $(& $Py --version)"

    # ── 3. PyTorch cho GPU NVIDIA ──
    Step 3 "Card đồ hoạ"
    $torchIndex = $null
    $smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($CpuOnly) {
        Write-Host "  Chạy bằng CPU (theo yêu cầu)."
    } elseif ($smi) {
        $gpu = (& nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader 2>$null | Select-Object -First 1)
        $cc = 0
        if ($gpu) { $cc = [int](($gpu -split ",")[-1].Trim() -split "\.")[0] }
        # RTX 50xx (compute 12.x) cần CUDA 12.8; các card cũ hơn dùng CUDA 12.6
        $torchIndex = if ($cc -ge 10) { "cu128" } else { "cu126" }
        Write-Host "  $gpu → PyTorch $torchIndex (tải ~2.5 GB, lâu nhất trong các bước)"
        Run $Uv @("pip", "install", "--python", $Py, "torch==2.8.0", "torchaudio==2.8.0", "--index-url", "https://download.pytorch.org/whl/$torchIndex") "Cài PyTorch"
    } else {
        Write-Host "  Không thấy GPU NVIDIA — chạy bằng CPU (ONNX), chậm hơn nhưng vẫn đọc được."
    }

    # ── 4. Thư viện ──
    Step 4 "Thư viện"
    Run $Uv @("pip", "install", "--python", $Py, "-r", "requirements.txt") "Cài thư viện"
    if ($torchIndex) { Run $Uv @("pip", "install", "--python", $Py, "-r", "requirements-gpu.txt") "Cài thư viện GPU" }
    # Lõi giọng không kèm thư viện phụ (bỏ gradio/pillow không dùng tới — xem BAO-CAO-BAO-MAT.md)
    Run $Uv @("pip", "install", "--python", $Py, "--no-deps", "-r", "requirements-core.txt") "Cài lõi giọng"

    # ── 5. Chuyển dữ liệu từ bản cũ ──
    Step 5 "Chuyển dữ liệu từ bản cũ"
    $from = $MigrateFrom.Trim().TrimEnd("\")
    if (-not $from) {
        Write-Host "  Không có — bỏ qua."
    } elseif (-not (Test-Path -LiteralPath "$from\app.py")) {
        Warn "Không thấy bản cũ ở '$from' — bỏ qua chuyển dữ liệu."
    } elseif ((Resolve-Path -LiteralPath $from).Path -eq (Resolve-Path -LiteralPath $AppDir).Path) {
        Write-Host "  Bản cũ chính là thư mục này — bỏ qua."
    } else {
        if (Test-Path -LiteralPath "$from\data") {
            Write-Host "  Kho giọng, bản thu, từ điển, cài đặt, file đã đọc…"
            # Bản trên máy cũ là mới nhất → chép đè; bỏ hồ sơ trình duyệt và trạng thái riêng của bản cũ
            & robocopy "$from\data" "$AppDir\data" /E /R:1 /W:1 /NFL /NDL /NJH /NP /XD .app-window .local | Out-Host
            if ($LASTEXITCODE -ge 8) { Warn "Chép dữ liệu chưa trọn (robocopy mã $LASTEXITCODE)." }
        }
        if (Test-Path -LiteralPath "$from\models") {
            Write-Host "  Mô hình lõi giọng (chuyển, không phải tải lại)…"
            $dst = "$AppDir\models"
            $sameDrive = ([IO.Path]::GetPathRoot($from) -eq [IO.Path]::GetPathRoot($AppDir))
            if ($sameDrive -and -not (Test-Path -LiteralPath $dst)) {
                Move-Item -LiteralPath "$from\models" -Destination $dst -ErrorAction Stop   # cùng ổ: đổi chỗ tức thì
            } else {
                & robocopy "$from\models" $dst /E /MOVE /R:1 /W:1 /NFL /NDL /NJH /NP | Out-Host
                if ($LASTEXITCODE -ge 8) { Warn "Chuyển mô hình chưa trọn (robocopy mã $LASTEXITCODE)." }
            }
        }
        Write-Host "  Xong. Bản cũ ở '$from' giữ nguyên mã nguồn — xoá khi bạn thấy bản mới chạy tốt."
    }
    $LASTEXITCODE = 0

    # ── 6. Dọn bộ nhớ tạm của trình cài thư viện ──
    Step 6 "Dọn file tạm"
    & $Uv -q cache prune --ci | Out-Null

    # ── 7. Kiểm tra ──
    Step 7 "Kiểm tra"
    $env:VOXVIET_DEMO = "1"
    Run $Py @("-c", "import voxviet, voxviet.server, voxviet.pipeline; print('VoxViet Studio', voxviet.__version__, 'sẵn sàng')") "Kiểm tra phần mềm"
    Remove-Item Env:VOXVIET_DEMO
    if (Test-Path -LiteralPath "$AppDir\models\.models_ready") {
        Write-Host "  Mô hình lõi giọng: đã có."
    } else {
        Write-Host "  Mô hình lõi giọng: sẽ tải ở lần mở đầu (màn hình chào)."
    }

    Write-Host ""
    if ($Warnings.Count) {
        Write-Host "===== XONG, có $($Warnings.Count) lưu ý =====" -ForegroundColor Yellow
        $Warnings | ForEach-Object { Write-Host "  - $_" }
    } else {
        Write-Host "===== XONG =====" -ForegroundColor Green
    }
    $code = 0
} catch {
    Write-Host ""
    Write-Host "LỖI: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Chi tiết: $AppDir\data\.local\setup.log"
    $code = 1
}
try { Stop-Transcript | Out-Null } catch {}
if (-not $NoPause -and $code -ne 0) { Read-Host "Nhấn Enter để đóng" | Out-Null }
exit $code
