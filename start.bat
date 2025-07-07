@echo off
title Flutter Earth - Enhanced v2.0
color 0A

echo.
echo ========================================
echo    FLUTTER EARTH - ENHANCED v2.0
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

:: Check if local Node.js is available
if not exist "node-v22.17.0-win-x64\node.exe" (
    echo [ERROR] Local Node.js not found at node-v22.17.0-win-x64\node.exe
    echo Please ensure Node.js is properly installed in the project directory
    pause
    exit /b 1
)

echo [INFO] Python found
echo [INFO] Local Node.js found
echo.

:: Set PATH to include local Node.js for the current session
set PATH=%CD%\node-v22.17.0-win-x64;%PATH%

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Start Electron frontend using local Node.js
echo [INFO] Starting Electron frontend...
cd frontend
npm start

echo.
echo [SUCCESS] Flutter Earth is starting up!
echo.
echo Backend: http://localhost:5000
echo Frontend: Electron app will open automatically
echo.
echo Press any key to close this window...
pause >nul 