@echo off
echo Starting Enhanced Earth Engine Catalog Crawler...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if the crawler script exists
if not exist "enhanced_crawler_ui.py" (
    echo Error: enhanced_crawler_ui.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing/updating dependencies...
pip install -r requirements_crawler.txt

REM Launch the crawler UI
echo.
echo Launching Enhanced Earth Engine Catalog Crawler UI...
echo.
python enhanced_crawler_ui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Crawler exited with an error. Press any key to close...
    pause
) 