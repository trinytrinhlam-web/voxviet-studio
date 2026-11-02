@echo off
REM Tai lai / kiem tra mo hinh VieNeu-TTS (can Internet)
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" ( echo Hay chay install.bat truoc. & pause & exit /b 1 )
".venv\Scripts\python.exe" tools\download_models.py %*
pause
