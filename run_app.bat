@echo off
echo ========================================
echo    Flutter Earth Desktop App
echo ========================================
echo.
echo Starting Flutter Earth...
echo Using local Node.js and Electron (no internet required)
echo.

cd /d "%~dp0"
cd frontend

echo Running: ..\node-v22.17.0-win-x64\node.exe .\node_modules\electron\cli.js .
..\node-v22.17.0-win-x64\node.exe .\node_modules\electron\cli.js .

if errorlevel 1 (
    echo.
    echo Error: App failed to start
    echo Check the console for error messages
    pause
) 