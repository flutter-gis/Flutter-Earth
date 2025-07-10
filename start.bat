@echo off
title Flutter Earth - Dear PyGui v2.0
color 0A

echo.
echo ========================================
echo    FLUTTER EARTH - DEAR PYGUI v2.0
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [INFO] Python found
echo.

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Check if required packages are installed
echo [INFO] Checking required packages...
python -c "import dearpygui" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dear PyGui not found, installing...
    pip install dearpygui
)

python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Matplotlib not found, installing...
    pip install matplotlib
)

:: Run startup coordinator
echo [INFO] Running startup coordinator...
python startup_coordinator.py

:: Start Dear PyGui application
echo [INFO] Starting Dear PyGui application...
python main.py

echo.
echo [SUCCESS] Flutter Earth is starting up!
echo.
echo Application: Dear PyGui window will open automatically
echo.
echo Press any key to close this window...
pause >nul 