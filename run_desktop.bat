@echo off
REM Flutter Earth Desktop App Launcher (Batch)
REM This script launches the Electron desktop application

echo Flutter Earth Desktop App
echo =========================
echo.

REM Change to the frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    ..\node-v22.17.0-win-x64\npm.cmd install
)

REM Start the Electron app
echo Starting Flutter Earth Desktop App...
..\node-v22.17.0-win-x64\npm.cmd start

pause 