@echo off
REM Cap nhat phan mem tu GitHub roi cai lai thu vien neu can
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
git pull --rebase --autostash || ( echo Loi git pull. & pause & exit /b 1 )
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
if exist ".venv\Lib\site-packages\torch" uv pip install --python .venv\Scripts\python.exe -r requirements-gpu.txt
echo XONG.
pause
