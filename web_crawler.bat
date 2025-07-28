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
echo Checking AI modules...
python -c "import transformers; print('✓ Transformers available')" 2>nul
if errorlevel 1 (
    echo ⚠️ Transformers not available - AI features will be limited
) else (
    echo ✓ AI modules available
)

echo.
echo Launching Enhanced Web Crawler UI with Full Automation...
echo AI enhancement is now automatic during crawling - no manual button needed!
echo Web validation runs automatically after crawling completes!
echo Dynamic optimization automatically adjusts performance based on system resources!
echo All manual controls removed - system runs autonomously!
echo ========================================
echo.

REM Launch the enhanced crawler UI with AI features
python enhanced_crawler_ui.py

echo.
echo Crawler UI closed.
pause 