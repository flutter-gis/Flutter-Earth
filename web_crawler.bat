@echo off
echo ========================================
echo Enhanced Web Crawler UI Launcher
echo ========================================
echo.

cd /d "%~dp0web_crawler"

echo Current directory: %CD%
echo.

REM Activate venv if present
if exist ..\venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call ..\venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo No virtual environment found, using system Python.
)

echo.
echo Checking for enhanced crawler UI...
if exist enhanced_crawler_ui.py (
    echo ✓ Found enhanced_crawler_ui.py
) else (
    echo ❌ enhanced_crawler_ui.py not found!
    pause
    exit /b 1
)

echo.
echo Checking Python dependencies...
python -c "import PySide6; print('✓ PySide6 is available')" 2>nul
if errorlevel 1 (
    echo ❌ PySide6 is not installed. Installing...
    pip install PySide6
)

echo.
echo Launching Enhanced Web Crawler UI with Output Directory Feature...
echo Look for the "Output Directory Settings" section in the UI
echo ========================================
echo.

REM Launch the enhanced crawler UI
python enhanced_crawler_ui.py

echo.
echo Crawler UI closed.
pause 