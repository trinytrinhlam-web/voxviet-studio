@echo off
REM ============================================================
REM  (Tuy chon) Bo fine-tune giong - dung ma huan luyen chinh thuc
REM  cua VieNeu-TTS. Can GPU NVIDIA >= 6 GB, Internet, ~5 GB.
REM ============================================================
setlocal
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul || ( echo Hay chay install.bat truoc. & pause & exit /b 1 )
if not exist tools mkdir tools

if not exist "tools\VieNeu-TTS\finetune\train_lora.py" (
    where git >nul 2>nul
    if not errorlevel 1 (
        git clone --depth 1 https://github.com/pnnbao97/VieNeu-TTS.git tools\VieNeu-TTS
    ) else (
        echo Khong co git - tai file zip...
        powershell -NoProfile -Command "Invoke-WebRequest https://github.com/pnnbao97/VieNeu-TTS/archive/refs/heads/main.zip -OutFile tools\vieneu.zip; Expand-Archive tools\vieneu.zip -DestinationPath tools -Force; Rename-Item tools\VieNeu-TTS-main VieNeu-TTS; Remove-Item tools\vieneu.zip"
    )
)
if not exist "tools\VieNeu-TTS\finetune\train_lora.py" ( echo LOI tai ma nguon VieNeu-TTS. & pause & exit /b 1 )

cd tools\VieNeu-TTS
set "HF_HOME=%~dp0models\hf"
echo Cai thu vien fine-tune (lau, ~5 GB)...
uv sync --extra finetune
if errorlevel 1 ( echo LOI cai thu vien. & pause & exit /b 1 )
echo.
echo XONG! Mo phan mem - tab "Phong thu & Fine-tune" - muc Fine-tune.
pause
