@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║           [STEP 2] AUTO READ DARI DXF - RS SARI DARMA                   ║
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
echo  WORKFLOW: DXF → Extract → Calculate → Populate Excel
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Scan for DXF files in drawing/dxf/ folder
echo 🔍 Scanning DXF files di folder drawing/dxf/...
echo.

REM Run integrated workflow (scan + auto-select latest + convert)
"%PYTHON_CMD%" analisis_volume\auto_read_workflow.py auto

if errorlevel 1 (
    echo.
    echo ❌ Error saat processing DXF!
    pause
    exit /b 1
)

echo.
echo ✅ Proses selesai!
echo.
echo 📁 Output Location: output\volumes\Volume_dari_Gambar_AUTO.xlsx
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  NEXT STEP: Jalankan 3_RUN_ANALISIS.bat untuk compare dengan RAB
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
