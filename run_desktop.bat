@echo off
echo Starting Flutter Earth Desktop App...
echo.

REM Set PATH to use local Node.js installation
set PATH=%~dp0node-v22.17.0-win-x86;%PATH%

REM Start the Electron app
cd frontend
echo Installing dependencies...
call npm install
echo.
echo Starting Electron app...
call npm start

pause 