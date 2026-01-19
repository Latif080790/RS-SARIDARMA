@echo off
chcp 65001 >nul
SETLOCAL EnableDelayedExpansion
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║                  [STEP 1] GENERATE ENHANCED TEMPLATE V2.0                ║
echo ║                     RS Sari Dharma Project                               ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo 📅 Timestamp: %date% %time%
echo.

REM Navigate to project root
cd /d "%~dp0.."

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

REM Run template generator with V2 argument
.venv\Scripts\python.exe analisis_volume\template_generator.py v2

if errorlevel 1 (
    echo.
    echo ❌ Error saat generate template!
    pause
    exit /b 1
)

echo.
echo ✅ Template V2 berhasil di-generate!
echo.
echo 📁 Output Location: output\templates\Volume_dari_Gambar_TEMPLATE_V2.xlsx
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  NEXT STEP: Jalankan 2_AUTO_READ_DXF.bat untuk proses DXF file
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
