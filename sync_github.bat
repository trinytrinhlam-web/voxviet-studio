@echo off
REM ============================================================
REM  Dong bo kho giong, ban thu, tu dien len GitHub (va lay ve
REM  thay doi tu may khac). Chay o cuoi moi buoi lam viec.
REM ============================================================
setlocal
cd /d "%~dp0"
where git >nul 2>nul || ( echo Can cai Git: https://git-scm.com/download/win & pause & exit /b 1 )

git add -A
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Dong bo du lieu %DATE% %TIME%"
)
echo Lay thay doi tu GitHub...
git pull --rebase --autostash
if errorlevel 1 ( echo Co xung dot - hay mo GitHub Desktop de xu ly. & pause & exit /b 1 )
echo Day len GitHub...
git push
if errorlevel 1 ( echo Day len that bai - kiem tra dang nhap GitHub. & pause & exit /b 1 )
echo.
echo XONG - da dong bo.
pause
