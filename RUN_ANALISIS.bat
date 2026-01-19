@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║             SISTEM ANALISIS VOLUME - RS SARI DARMA                      ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo ✓ Virtual environment ditemukan
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo ⚠ Virtual environment tidak ditemukan, menggunakan Python global
    set PYTHON_CMD=python
)

echo.
echo Menjalankan analisis...
echo.

REM Run the script
"%PYTHON_CMD%" run_analisis_volume.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if errorlevel 1 (
    echo ✗ Terjadi error saat menjalankan script
    echo.
    echo Pastikan:
    echo   1. Python sudah terinstall
    echo   2. Library sudah terinstall: pip install pandas openpyxl
    echo   3. File Volume_dari_Gambar.xlsx sudah ada
    echo.
) else (
    echo ✓ Analisis selesai!
    echo.
    echo Silakan buka file: LAPORAN_PERBANDINGAN_VOLUME.xlsx
    echo.
)

pause
