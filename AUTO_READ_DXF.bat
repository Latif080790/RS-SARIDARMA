@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║           AUTO READ DARI DXF - RS SARI DARMA                            ║
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
echo ═══════════════════════════════════════════════════════════════════════════
echo  WORKFLOW: DXF → Extract → Calculate → Populate Excel
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Scan for DXF files in drawing/dxf/ folder
echo 🔍 Scanning DXF files di folder drawing/dxf/...
echo.

"%PYTHON_CMD%" analisis_volume\dxf_scanner.py

echo.
echo ─────────────────────────────────────────────────────────────────────────
echo.

REM Check if user wants to continue
set /p CONTINUE="Lanjutkan dengan file DXF yang dipilih? (Y/N): "
if /i not "%CONTINUE%"=="Y" (
    echo.
    echo ✗ Dibatalkan oleh user
    pause
    exit /b 0
)

REM Check if template exists (V2)
if exist "Volume_dari_Gambar_TEMPLATE_V2.xlsx" (
    set TEMPLATE_FILE=Volume_dari_Gambar_TEMPLATE_V2.xlsx
    echo ✓ Using Template V2 (Enhanced)
) else if exist "Volume_dari_Gambar_TEMPLATE.xlsx" (
    set TEMPLATE_FILE=Volume_dari_Gambar_TEMPLATE.xlsx
    echo ✓ Using Template V1 (Legacy)
) else (
    echo ✗ Template tidak ditemukan!
    echo.
    echo Jalankan dulu: GENERATE_TEMPLATE_V2.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Memproses file DXF...
echo.

REM Run the DXF to Excel converter
"%PYTHON_CMD%" analisis_volume\dxf_to_excel.py

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

if errorlevel 1 (
    echo ✗ Terjadi error saat memproses DXF
    echo.
    echo Kemungkinan masalah:
    echo   1. File DXF corrupt atau format tidak didukung
    echo   2. Library Python belum terinstall: pip install ezdxf openpyxl
    echo   3. Template Excel rusak
    echo.
    echo Periksa pesan error di atas untuk detail.
    echo.
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════════════╗
    echo ║                  ✓ PROSES SELESAI!                                       ║
    echo ╚══════════════════════════════════════════════════════════════════════════╝
    echo.
    echo File hasil: Volume_dari_Gambar_AUTO.xlsx
    echo.
    echo Langkah selanjutnya:
    echo   1. Buka file Excel hasil auto-populate
    echo   2. Review dan koreksi data jika perlu
    echo   3. Tambah item manual jika ada yang terlewat
    echo   4. Save As: Volume_dari_Gambar.xlsx
    echo   5. Jalankan: RUN_ANALISIS.bat untuk perbandingan dengan RAB
    echo.
    echo NOTE: Baris berwarna HIJAU adalah hasil auto-populate dari DXF
    echo.
)

pause
