@echo off
REM ============================================================
REM  Cap nhat VoxViet Studio tu GitHub.
REM  Du lieu cua ban (kho giong, ban thu, cai dat) duoc giu nguyen.
REM  Hay TAT cua so run.bat truoc khi chay file nay.
REM ============================================================
setlocal
cd /d "%~dp0"
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
set "REPO=https://github.com/trinytrinhlam-web/voxviet-studio.git"
where git >nul 2>nul || ( echo Can cai Git: https://git-scm.com/download/win & pause & exit /b 1 )

echo Phien ban hien tai:
findstr /c:"__version__" voxviet\__init__.py

if not exist ".git" goto from_zip

REM --- Thu muc da ket noi GitHub: keo ban moi, giu nguyen thay doi/commit cua ban ---
git pull --rebase --autostash origin main
if errorlevel 1 ( echo LOI git pull - chup man hinh loi gui lai de duoc ho tro. & pause & exit /b 1 )
goto after_code

:from_zip
REM --- Cai tu file ZIP (chua co .git): ket noi GitHub roi lay ban moi nhat ---
echo Thu muc nay chua ket noi GitHub - dang ket noi...
git init -q
git remote add origin %REPO%
git fetch origin main
if errorlevel 1 ( echo LOI: khong tai duoc tu GitHub - kiem tra Internet / dang nhap GitHub. & pause & exit /b 1 )
git checkout -q -f -B main origin/main
if errorlevel 1 ( echo LOI cap nhat ma nguon. & pause & exit /b 1 )
git branch -q --set-upstream-to=origin/main main 2>nul

:after_code

echo Phien ban moi:
findstr /c:"__version__" voxviet\__init__.py
git log -1 --format="  %%h  %%s"

echo Cap nhat thu vien...
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
if exist ".venv\Lib\site-packages\torch" uv pip install --python .venv\Scripts\python.exe -r requirements-gpu.txt
uv pip install --python .venv\Scripts\python.exe --no-deps -r requirements-core.txt

echo.
echo  ===== XONG - mo lai run.bat, roi nhan Ctrl+F5 tren trinh duyet =====
pause
