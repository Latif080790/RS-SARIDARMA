@echo off
chcp 65001 >nul
cls

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                                                                          ║
echo ║         ANALISIS DETAIL PEKERJAAN STRUKTUR vs RAB STRUKTUR               ║
echo ║                        RS SARI DARMA                                     ║
echo ║                                                                          ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo  📋 FITUR ANALISIS DETAIL:
echo  ────────────────────────────────────────────────────────────────────────
echo.
echo  ✅ Kategori otomatis (Tanah, Pondasi, Beton, Bekisting, Pembesian, dll)
echo  ✅ Extract spesifikasi teknis (K-grade, diameter besi, dimensi)
echo  ✅ Matching cerdas dengan threshold berbeda per kategori
echo  ✅ Deteksi selisih volume dan dampak biaya
echo  ✅ Identifikasi item yang hilang di RAB atau Gambar
echo  ✅ Laporan Excel lengkap dengan 4 sheet terpisah
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  REQUIREMENT:
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo  1️⃣  Volume dari Gambar AUTO sudah ada
echo     (Jalankan: 2_AUTO_READ_DXF.bat terlebih dahulu)
echo.
echo  2️⃣  File RAB Struktur ada di: rab\str\BOQ-Dokumen Struktur.xlsx
echo.
pause
echo.

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
echo ═══════════════════════════════════════════════════════════════════════════
echo  MEMULAI ANALISIS DETAIL...
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Run detailed struktur analysis
"%PYTHON_CMD%" examples\analisis_struktur_detail.py

if errorlevel 1 (
    echo.
    echo ❌ Error saat menjalankan analisis!
    echo.
    echo 💡 Troubleshooting:
    echo   - Pastikan file Volume_dari_Gambar_AUTO.xlsx ada di output\volumes\
    echo   - Pastikan file BOQ-Dokumen Struktur.xlsx ada di rab\str\
    echo   - Cek apakah virtual environment sudah terinstall dengan benar
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Analisis selesai!
echo.
echo 📁 Output Location: output\reports\STRUKTUR_ANALYSIS_DETAIL_*.xlsx
echo.
echo 📋 LAPORAN EXCEL BERISI 4 SHEET:
echo ─────────────────────────────────────────────────────────────────────────
echo  1. Summary               - Ringkasan per kategori pekerjaan
echo  2. Matched Items         - Item yang berhasil di-match (lengkap)
echo  3. Missing in RAB        - Item di Gambar tapi tidak ada di RAB
echo  4. RAB Not in Gambar     - Item di RAB tapi tidak ada di Gambar
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo  DONE! Buka file Excel untuk melihat hasil analisis detail
echo ═══════════════════════════════════════════════════════════════════════════
echo.

pause
