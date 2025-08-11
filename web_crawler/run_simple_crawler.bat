@echo off
echo ========================================
echo Simple Web Crawler
echo ========================================
echo.
echo Starting Simple Crawler...
echo.
echo The crawler window should appear shortly.
echo If you don't see it, check your taskbar or press Alt+Tab.
echo.
echo Press Ctrl+C to stop the crawler.
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PySide6 is available
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Installing PySide6...
    pip install PySide6
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import requests, bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install requests beautifulsoup4
)

echo Starting crawler...
python simple_crawler.py

echo.
echo Crawler finished.
pause 