@echo off
REM Tu kiem tra bao mat: ma di kem mo hinh, file trong so, thu vien loi. Khong gui gi ra ngoai.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" ( echo Hay chay install.bat truoc. & pause & exit /b 1 )
".venv\Scripts\python.exe" tools\kiem_tra_bao_mat.py
echo.
echo Quet virus bang Windows Defender (co the mat vai phut)...
"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -Scan -ScanType 3 -File "%~dp0" -DisableRemediation
pause
