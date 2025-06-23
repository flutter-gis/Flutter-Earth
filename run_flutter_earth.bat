@echo off
echo Starting Flutter Earth...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the application
python main.py

REM Check if the application exited with an error
if errorlevel 1 (
    echo.
    echo Flutter Earth exited with an error
    pause
    exit /b 1
)

echo.
echo Flutter Earth has closed
pause 