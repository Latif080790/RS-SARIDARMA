@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║        [STEP 3] ANALISIS VOLUME - COMPARE GAMBAR vs RAB                 ║
echo ║                     RS SARI DARMA                                        ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo.

REM Navigate to project root
cd /d "%~dp0.."

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo ✓ Virtual environment ditemukan
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo ⚠ Virtual environment tidak ditemukan, menggunakan Python global
    set PYTHON_CMD=python
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  WORKFLOW: Compare Volume Gambar vs RAB → Generate Report
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Check if required files exist
if not exist "output\volumes\Volume_dari_Gambar_AUTO.xlsx" (
    echo ❌ File Volume_dari_Gambar_AUTO.xlsx tidak ditemukan!
    echo.
    echo Silakan jalankan 2_AUTO_READ_DXF.bat terlebih dahulu
    echo.
    pause
    exit /b 1
)

REM Check if RAB file exists (check multiple possible locations)
set RAB_FOUND=0
if exist "rab\str\*.xlsx" set RAB_FOUND=1
if exist "rab\ars\*.xlsx" set RAB_FOUND=1
if exist "rab\mep\*.xlsx" set RAB_FOUND=1

if %RAB_FOUND%==0 (
    echo ⚠ File RAB tidak ditemukan di folder rab\str\, rab\ars\, atau rab\mep\
    echo.
    echo Pastikan file RAB Excel sudah ada di folder yang sesuai
    echo.
    pause
    exit /b 1
)

echo ✓ File Volume dan RAB ditemukan
echo.
echo ─────────────────────────────────────────────────────────────────────────
echo  Processing Analysis...
echo ─────────────────────────────────────────────────────────────────────────
echo.

REM Run the analysis script
"%PYTHON_CMD%" run_analisis_volume.py

if errorlevel 1 (
    echo.
    echo ❌ Error saat menjalankan analisis!
    pause
    exit /b 1
)

echo.
echo ✅ Analisis selesai!
echo.
echo 📁 Output Location: output\reports\
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  DONE! Lihat hasil analisis di folder output\reports
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
