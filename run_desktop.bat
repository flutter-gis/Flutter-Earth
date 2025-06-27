@echo off
echo Starting Flutter Earth Desktop App...
echo.

REM Set Node.js path
set NODE_PATH=C:\Flutter-Earth\node-v22.17.0-win-x64
set PATH=%NODE_PATH%;%PATH%

REM Start the Electron app
cd frontend
echo Installing dependencies...
call "%NODE_PATH%\npm" install
echo.
echo Starting Electron app...
call "%NODE_PATH%\npm" start

pause 