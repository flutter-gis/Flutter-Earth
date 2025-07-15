@echo off
cd /d "%~dp0web_crawler"

REM Activate venv if present
if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
)

REM Launch the enhanced crawler UI
python enhanced_crawler_ui.py

pause 