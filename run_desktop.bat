@echo off
echo Starting Flutter Earth Desktop App...
echo.

REM Start the Electron app
cd frontend
echo Installing dependencies...
call npm install
echo.
echo Starting Electron app...
call npm start

pause 