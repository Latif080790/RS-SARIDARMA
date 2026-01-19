@echo off
chcp 65001 >nul
color 0E

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║                  [OPTIONAL] GENERATE TEMPLATE V1                         ║
echo ║                     RS Sari Dharma Project                               ║
echo ║                  (Legacy - Gunakan V2 untuk fitur lengkap)               ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo ⚠ PERHATIAN: Ini adalah template versi lama (V1)
echo.
echo Untuk template dengan fitur enhanced (12 kolom, breakdown detail),
echo gunakan: 1_GENERATE_TEMPLATE_V2.bat
echo.

set /p CONTINUE="Tetap lanjutkan dengan Template V1? (Y/N): "
if /i not "%CONTINUE%"=="Y" (
    echo.
    echo Dibatalkan.
    pause
    exit /b 0
)

REM Navigate to project root (go up 2 levels from scripts/batch/)
cd /d "%~dp0..\..\"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo ✓ Virtual environment ditemukan
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo ⚠ Virtual environment tidak ditemukan, menggunakan Python global
    set PYTHON_CMD=python
)

echo.
echo Membuat template Excel V1...
echo.

REM Run the template generator
"%PYTHON_CMD%" analisis_volume\template_generator.py

if errorlevel 1 (
    echo.
    echo ❌ Error saat generate template!
    pause
    exit /b 1
)

echo.
echo ✅ Template V1 berhasil dibuat!
echo.
echo Output: Volume_dari_Gambar_TEMPLATE.xlsx
echo.

pause
