@echo off
REM ================================================================
REM AUTO CONVERT DWG/PDF TO DXF
REM ================================================================

REM Navigate to project root (go up 2 levels from scripts/batch/)
cd /d "%~dp0..\..\"

echo.
echo ================================================================
echo AUTO FILE CONVERTER - DWG/PDF to DXF
echo ================================================================
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if file provided as argument
if "%~1"=="" (
    echo Usage: CONVERT_TO_DXF.bat "path\to\file.dwg"
    echo        CONVERT_TO_DXF.bat "path\to\file.pdf"
    echo.
    echo Example: CONVERT_TO_DXF.bat "drawing\dwg\struktur.dwg"
    echo.
    
    REM Check for converters
    python analisis_volume\file_converter.py
    
    pause
    exit /b 1
)

REM Run conversion
echo Converting: %~1
echo.

python analisis_volume\auto_read_workflow.py "%~1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo CONVERSION SUCCESS!
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo CONVERSION FAILED!
    echo ================================================================
)

echo.
pause
