@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║             GENERATE TEMPLATE EXCEL - RS SARI DARMA                     ║
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
echo Membuat template Excel...
echo.

REM Run the template generator
"%PYTHON_CMD%" analisis_volume\template_generator.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if errorlevel 1 (
    echo ✗ Terjadi error saat membuat template
    echo.
    echo Pastikan:
    echo   1. Python sudah terinstall
    echo   2. Library sudah terinstall: pip install openpyxl
    echo.
) else (
    echo ✓ Template berhasil dibuat!
    echo.
    echo File: Volume_dari_Gambar_TEMPLATE.xlsx
    echo.
    echo Langkah selanjutnya:
    echo   1. Buka file template
    echo   2. Isi data volume dari gambar DED
    echo   3. Simpan dengan nama: Volume_dari_Gambar.xlsx
    echo   4. Jalankan: RUN_ANALISIS.bat
    echo.
)

pause
