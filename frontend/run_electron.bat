@echo off
cd /d "%~dp0"
echo Starting Flutter Earth Electron App...
echo Using local Node.js: ..\node-v22.17.0-win-x64\node.exe
echo Using local Electron: .\node_modules\electron\dist\electron.exe

..\node-v22.17.0-win-x64\node.exe .\node_modules\electron\cli.js .

if errorlevel 1 (
    echo.
    echo Error: Failed to start Electron app
    echo Please check that all dependencies are installed correctly
    pause
) 