@echo off
REM ============================================================
REM  VoxViet Studio - Cai dat lan dau (can Internet, ~3-6 GB)
REM ============================================================
setlocal EnableDelayedExpansion
cd /d "%~dp0"
echo.
echo  ===== VoxViet Studio - CAI DAT =====
echo.

REM --- 1. uv (trinh quan ly Python, tu tai Python 3.12) ---
where uv >nul 2>nul
if errorlevel 1 (
    echo [1/5] Dang cai uv...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)
where uv >nul 2>nul
if errorlevel 1 (
    echo LOI: khong cai duoc uv. Hay cai thu cong tai https://docs.astral.sh/uv/ roi chay lai.
    pause & exit /b 1
)

REM --- 2. Moi truong Python ---
echo [2/5] Tao moi truong Python 3.12 (.venv)...
if not exist ".venv\Scripts\python.exe" (
    uv venv .venv --python 3.12
    if errorlevel 1 ( echo LOI tao moi truong. & pause & exit /b 1 )
)
set "PY=.venv\Scripts\python.exe"

REM --- 3. PyTorch (GPU neu co card NVIDIA) ---
set "TORCH_INDEX="
where nvidia-smi >nul 2>nul
if not errorlevel 1 (
    set "CC_MAJOR=0"
    for /f "tokens=1 delims=." %%a in ('nvidia-smi --query-gpu^=compute_cap --format^=csv^,noheader 2^>nul') do (
        if "!CC_MAJOR!"=="0" set "CC_MAJOR=%%a"
    )
    REM RTX 50xx (Blackwell, compute 12.x) can CUDA 12.8; cac card cu hon dung CUDA 12.6
    if !CC_MAJOR! GEQ 10 ( set "TORCH_INDEX=cu128" ) else ( set "TORCH_INDEX=cu126" )
    echo [3/5] Tim thay GPU NVIDIA ^(compute !CC_MAJOR!.x^) - cai PyTorch !TORCH_INDEX!...
    uv pip install --python %PY% torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/!TORCH_INDEX!
    if errorlevel 1 ( echo LOI cai PyTorch. & pause & exit /b 1 )
) else (
    echo [3/5] Khong thay GPU NVIDIA - se chay bang CPU ^(ONNX^), bo qua PyTorch.
)

REM --- 4. Thu vien ---
echo [4/5] Cai thu vien...
uv pip install --python %PY% -r requirements.txt
if errorlevel 1 ( echo LOI cai thu vien. & pause & exit /b 1 )
if defined TORCH_INDEX (
    uv pip install --python %PY% -r requirements-gpu.txt
    if errorlevel 1 ( echo LOI cai thu vien GPU. & pause & exit /b 1 )
)

REM --- 5. Tai mo hinh ---
echo [5/5] Tai mo hinh VieNeu-TTS (lan dau ~1-3 GB)...
%PY% tools\download_models.py
if errorlevel 1 ( echo Tai mo hinh that bai - chay lai download_models.bat sau. )

echo.
echo  ===== XONG - Chay run.bat de mo phan mem =====
echo  (Tuy chon) install_english_pro.bat : giong tieng Anh Chatterbox
echo  (Tuy chon) install_finetune.bat    : fine-tune giong cua ban
echo.
pause
