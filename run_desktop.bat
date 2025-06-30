@echo off
echo Starting Flutter Earth Desktop App...
echo.

REM Set local Node.js and npm paths
set NODE_DIR=%~dp0node-v22.17.0-win-x64
set PATH=%NODE_DIR%;%NODE_DIR%\node_modules\npm\bin;%PATH%

REM Move to frontend directory
cd /d %~dp0frontend

REM Use local npm to install dependencies if needed
if not exist node_modules (
    "%NODE_DIR%\npm.cmd" install
    if errorlevel 1 goto error
)

REM Start the app using local npm
"%NODE_DIR%\npm.cmd" start
if errorlevel 1 goto error

goto end

:error
echo.
echo =============================
echo ERROR: The app failed to start or a command failed.
echo Please scroll up for details.
echo The command prompt will remain open so you can read the error.
echo =============================

:end
pause 