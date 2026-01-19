@echo off
chcp 65001 >nul
SETLOCAL EnableDelayedExpansion
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║                  GENERATE ENHANCED TEMPLATE V2.0                         ║
echo ║                     RS Sari Dharma Project                               ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo 📅 Timestamp: %date% %time%
echo.

REM Check if Python virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment tidak ditemukan!
    echo.
    echo Silakan jalankan: python -m venv .venv
    echo Lalu: .venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

echo 🔨 Generating Enhanced Template V2...
echo.

REM Run template generator
".venv\Scripts\python.exe" -c "from analisis_volume.template_generator import VolumeTemplateGenerator; gen = VolumeTemplateGenerator('Volume_dari_Gambar_TEMPLATE_V2.xlsx'); gen.generate()"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error generating template!
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║                    ✅ TEMPLATE V2 GENERATED!                            ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo 📄 File: Volume_dari_Gambar_TEMPLATE_V2.xlsx
echo.
echo 🆕 NEW FEATURES:
echo    ✓ 12 Columns (Kode, Lantai, Lokasi/Grid added)
echo    ✓ Breakdown per lantai (Basement, Lt.1, Lt.2, Atap)
echo    ✓ Kode referensi (K1, K2, B1, B2, P1, P2, dll)
echo    ✓ 34+ items dengan detail lengkap
echo.
echo 📋 NEXT STEPS:
echo    1. Buka file template
echo    2. Isi data volume dengan kolom lengkap
echo    3. Save as: Volume_dari_Gambar.xlsx
echo    4. Run: RUN_ANALISIS.bat
echo.
echo    💡 Or use AUTO-READ: AUTO_READ_DXF.bat (if you have DXF file)
echo.

pause
