@echo off
echo ========================================
echo Lightweight Web Crawler Launcher
echo ========================================
echo.

cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Checking Python dependencies...
python -c "import requests, bs4, PySide6" 2>nul
if %errorlevel% equ 0 (
    echo ✓ All dependencies available
) else (
    echo ⚠ Some dependencies missing - installing...
    pip install requests beautifulsoup4 PySide6
)

echo.
echo Launching Lightweight Web Crawler...
echo.
echo Features:
echo • Fast text extraction without heavy ML models
echo • Online keyword-based classification
echo • Lightweight and memory-efficient
echo • Focus on data quality over quantity
echo.

python lightweight_crawler.py

echo.
echo Crawler finished.
pause 