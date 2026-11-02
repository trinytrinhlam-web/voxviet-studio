@echo off
REM ============================================================
REM  (Tuy chon) Bo fine-tune giong (bo huan luyen cua ma nguon loi
REM  giong, Apache-2.0). Can GPU NVIDIA >= 6 GB, Internet, ~5 GB.
REM ============================================================
setlocal
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul || ( echo Hay chay install.bat truoc. & pause & exit /b 1 )
if not exist tools mkdir tools

if not exist "tools\voxviet-trainer\finetune\train_lora.py" (
    where git >nul 2>nul
    if not errorlevel 1 (
        REM Ghim dung ban v3.8.3 (commit c1390ab) da duoc ra soat ma nguon
        git clone --depth 1 --branch v3.8.3 https://github.com/pnnbao97/VieNeu-TTS.git tools\voxviet-trainer
    ) else (
        echo Khong co git - tai file zip...
        powershell -NoProfile -Command "Invoke-WebRequest https://github.com/pnnbao97/VieNeu-TTS/archive/refs/tags/v3.8.3.zip -OutFile tools\vieneu.zip; Expand-Archive tools\vieneu.zip -DestinationPath tools -Force; Rename-Item tools\VieNeu-TTS-3.8.3 voxviet-trainer; Remove-Item tools\vieneu.zip"
    )
)
if not exist "tools\voxviet-trainer\finetune\train_lora.py" ( echo LOI tai bo huan luyen. & pause & exit /b 1 )

cd tools\voxviet-trainer
set "HF_HOME=%~dp0models\hf"
set "HF_HUB_CACHE=%~dp0models\voxviet-core"
echo Cai thu vien fine-tune (lau, ~5 GB)...
uv sync --extra finetune
if errorlevel 1 ( echo LOI cai thu vien. & pause & exit /b 1 )
echo.
echo XONG! Mo phan mem - tab "Phong thu & Fine-tune" - muc Fine-tune.
pause
