@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

title Flutter Earth - Launcher

:menu
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    FLUTTER EARTH LAUNCHER                    ║
echo  ║                                                              ║
echo  ║  Choose your preferred interface and mode:                   ║
echo  ║                                                              ║
echo  ║  [1] HTML Desktop App (Electron) - Recommended              ║
echo  ║  [2] HTML Web Interface (Browser) - New UI                  ║
echo  ║  [3] QML Desktop Interface (Legacy)                         ║
echo  ║  [4] Combined Mode (Backend + Frontend)                     ║
echo  ║  [5] Setup & Install Dependencies                            ║
echo  ║  [6] Exit                                                     ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto html_desktop
if "%choice%"=="2" goto html_web
if "%choice%"=="3" goto qml_interface
if "%choice%"=="4" goto combined_mode
if "%choice%"=="5" goto setup_install
if "%choice%"=="6" goto exit_program

echo Invalid choice. Please select 1-6.
timeout /t 2 /nobreak >nul
goto menu

:html_desktop
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                HTML DESKTOP APP (ELECTRON)                   ║
echo  ║                                                              ║
echo  ║  Starting Flutter Earth as a desktop application...          ║
echo  ║  This runs in a native window using Electron.                ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Node.js is available
if not exist "node-v22.17.0-win-x64\node.exe" (
    echo ERROR: Node.js not found in node-v22.17.0-win-x64 directory!
    echo Please ensure the Node.js distribution is present.
    pause
    goto menu
)

REM Set Node.js path
set "NODE_DIR=%CD%\node-v22.17.0-win-x64"
set "PATH=%NODE_DIR%;%PATH%"

cd Flutter-Earth

REM Check if dependencies are installed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        goto menu
    )
    echo Dependencies installed successfully.
    echo.
)

echo Starting desktop application...
echo The application will open in a desktop window.
echo Press Ctrl+C to stop the application.
echo.
npm start

echo.
echo Application has closed.
pause
goto menu

:html_web
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                HTML WEB INTERFACE (BROWSER)                  ║
echo  ║                                                              ║
echo  ║  Choose how to run the web interface:                        ║
echo  ║                                                              ║
echo  ║  [1] Direct Browser Opening (No Server)                     ║
echo  ║  [2] Local Server (Recommended)                             ║
echo  ║  [3] Back to Main Menu                                      ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
set /p web_choice="Enter your choice (1-3): "

if "%web_choice%"=="1" goto direct_browser
if "%web_choice%"=="2" goto local_server
if "%web_choice%"=="3" goto menu

echo Invalid choice.
timeout /t 2 /nobreak >nul
goto html_web

:direct_browser
echo.
echo Opening Flutter Earth HTML interface in your default browser...
echo This runs completely offline - no server required.
echo.
cd frontend
start flutter_earth.html
echo.
echo Interface opened in browser!
pause
goto menu

:local_server
echo.
echo Starting local server for Flutter Earth...
echo The interface will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

cd frontend

REM Check if Python is available for server
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Trying alternative methods...
    
    REM Try Node.js http-server if available
    if exist "..\node-v22.17.0-win-x64\npx.exe" (
        echo Using Node.js http-server...
        set "PATH=..\node-v22.17.0-win-x64;%PATH%"
        npx http-server -p 8000 -o flutter_earth.html
    ) else (
        echo No server method available. Opening directly in browser...
        start flutter_earth.html
    )
) else (
    echo Using Python HTTP server...
    python -m http.server 8000
)

echo.
echo Server stopped.
pause
goto menu

:qml_interface
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                QML DESKTOP INTERFACE (LEGACY)                ║
echo  ║                                                              ║
echo  ║  Starting the original QML-based interface...                ║
echo  ║  This requires Qt and Python dependencies.                   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    goto menu
)

cd Flutter-Earth

echo Starting QML interface...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo Flutter Earth exited with an error
    pause
    goto menu
)

echo.
echo Application has closed
pause
goto menu

:combined_mode
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    COMBINED MODE                             ║
echo  ║                                                              ║
echo  ║  Starting both backend and frontend servers...               ║
echo  ║                                                              ║
echo  ║  Backend API: http://localhost:5000                          ║
echo  ║  Frontend: http://localhost:8000                             ║
echo  ║                                                              ║
echo  ║  Press Ctrl+C to stop both servers                           ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    goto menu
)

cd Flutter-Earth

echo Starting backend server in background...
start "Backend Server" cmd /k "python main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend server...
cd frontend
python -m http.server 8000

echo.
echo Stopping all servers...
taskkill /f /im python.exe >nul 2>&1

echo Both servers have been stopped
pause
goto menu

:setup_install
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    SETUP & INSTALL                           ║
echo  ║                                                              ║
echo  ║  Choose what to install/setup:                               ║
echo  ║                                                              ║
echo  ║  [1] Install Python Dependencies                             ║
echo  ║  [2] Install Node.js Dependencies                             ║
echo  ║  [3] Setup Google Earth Engine Authentication                ║
echo  ║  [4] Run Full Setup (All of the above)                       ║
echo  ║  [5] Back to Main Menu                                       ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
set /p setup_choice="Enter your choice (1-5): "

if "%setup_choice%"=="1" goto install_python_deps
if "%setup_choice%"=="2" goto install_node_deps
if "%setup_choice%"=="3" goto setup_auth
if "%setup_choice%"=="4" goto full_setup
if "%setup_choice%"=="5" goto menu

echo Invalid choice.
timeout /t 2 /nobreak >nul
goto setup_install

:install_python_deps
echo.
echo Installing Python dependencies...
cd Flutter-Earth\flutter_earth_pkg
pip install -r requirements.txt
echo.
echo Python dependencies installed!
pause
goto setup_install

:install_node_deps
echo.
echo Installing Node.js dependencies...
cd Flutter-Earth
npm install
echo.
echo Node.js dependencies installed!
pause
goto setup_install

:setup_auth
echo.
echo Setting up Google Earth Engine authentication...
echo Please follow the prompts to authenticate with Google Earth Engine.
echo.
cd Flutter-Earth
python -c "from flutter_earth_pkg.flutter_earth.auth_setup import setup_auth; setup_auth()"
echo.
echo Authentication setup complete!
pause
goto setup_install

:full_setup
echo.
echo Running full setup...
echo.

REM Install Python dependencies
echo [1/4] Installing Python dependencies...
cd Flutter-Earth\flutter_earth_pkg
pip install -r requirements.txt

REM Install Node.js dependencies
echo [2/4] Installing Node.js dependencies...
cd ..\..
cd Flutter-Earth
npm install

REM Setup authentication
echo [3/4] Setting up authentication...
python -c "from flutter_earth_pkg.flutter_earth.auth_setup import setup_auth; setup_auth()"

REM Verify installation
echo [4/4] Verifying installation...
python --version
node --version
echo.
echo Full setup complete!
pause
goto menu

:exit_program
echo.
echo Thank you for using Flutter Earth!
echo.
exit /b 0 