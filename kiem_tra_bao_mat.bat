@echo off
REM Tu kiem tra bao mat: ma di kem mo hinh, file trong so, thu vien loi, quet virus.
REM Khong gui gi ra ngoai.
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" ( echo Hay chay install.bat truoc. & pause & exit /b 1 )

echo ===== 1/2. Kiem tra ma nguon va mo hinh =====
".venv\Scripts\python.exe" tools\kiem_tra_bao_mat.py
echo.

REM Bo dau "\" o cuoi duong dan (neu de, dau ngoac kep dong se bi "nuot" - loi 0x80508023)
set "TARGET=%~dp0"
set "TARGET=%TARGET:~0,-1%"

echo ===== 2/2. Quet virus bang Microsoft Defender (vai phut) =====
echo Thu muc: %TARGET%
"%ProgramFiles%\Windows Defender\MpCmdRun.exe" -Scan -ScanType 3 -File "%TARGET%" -DisableRemediation
if not errorlevel 1 goto done
if errorlevel 2 (
    echo.
    echo CANH BAO: Defender bao co moi de doa - xem chi tiet trong Windows Security ^> Virus ^& threat protection.
    goto done
)

echo.
echo Cach 1 khong chay duoc - thu cach 2 bang PowerShell...
powershell -NoProfile -Command "try { Start-MpScan -ScanType CustomScan -ScanPath '%TARGET%' -ErrorAction Stop; 'Quet xong. Neu co moi de doa, Windows Security se hien canh bao.' } catch { 'Khong quet duoc: ' + $_.Exception.Message; 'Co the may dang dung phan mem diet virus khac (Defender bi tat).'; 'Cach thu cong: bam chuot phai vao thu muc ' + '%TARGET%' + ' > Scan with Microsoft Defender (hoac quet bang phan mem diet virus cua ban).' }"

:done
echo.
pause
