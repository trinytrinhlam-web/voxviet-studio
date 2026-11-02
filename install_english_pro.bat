@echo off
REM ============================================================
REM  (Tuy chon) Module tieng Anh Pro - Chatterbox (MIT)
REM  Cai vao moi truong rieng envs\chatterbox vi can phien ban
REM  PyTorch khac voi loi giong. Can Internet, ~4 GB.
REM ============================================================
setlocal
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul || ( echo Hay chay install.bat truoc. & pause & exit /b 1 )

if not exist "envs\chatterbox\Scripts\python.exe" (
    uv venv envs\chatterbox --python 3.11
    if errorlevel 1 ( echo LOI tao moi truong. & pause & exit /b 1 )
)
set "PY=envs\chatterbox\Scripts\python.exe"
set "IDX=cpu"
where nvidia-smi >nul 2>nul && set "IDX=cu124"
echo Cai PyTorch 2.6 (%IDX%)...
uv pip install --python %PY% torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/%IDX%
if errorlevel 1 ( echo LOI cai PyTorch. & pause & exit /b 1 )
echo Cai Chatterbox...
uv pip install --python %PY% chatterbox-tts==0.1.7
if errorlevel 1 ( echo LOI cai Chatterbox. & pause & exit /b 1 )

echo Tai mo hinh Chatterbox...
set "HF_HOME=%~dp0models\hf"
set "HF_HUB_CACHE=%~dp0models\voxviet-core"
%PY% -c "from chatterbox.tts import ChatterboxTTS; ChatterboxTTS.from_pretrained(device='cpu'); print('OK')"
if errorlevel 1 ( echo LOI tai mo hinh. & pause & exit /b 1 )

echo.
echo XONG! Mo phan mem - Cai dat - chon "Chatterbox" cho module English.
pause
