@echo off
REM VoxViet Studio - mo phan mem (chay offline)
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Chua cai dat. Hay chay install.bat truoc.
    pause & exit /b 1
)
title VoxViet Studio - dong cua so nay de tat
".venv\Scripts\python.exe" app.py %*
if errorlevel 1 pause
