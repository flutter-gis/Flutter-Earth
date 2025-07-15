@echo off
echo Installing Tesseract OCR...

REM Create Tesseract installation directory
set TESSERACT_DIR=C:\Program Files\Tesseract-OCR
if not exist "%TESSERACT_DIR%" mkdir "%TESSERACT_DIR%"

REM Copy files from downloaded source
echo Copying Tesseract files...
xcopy "C:\Users\U1060469\Downloads\tesseract-5.5.1\*" "%TESSERACT_DIR%\" /E /I /Y

REM Add to PATH
echo Adding Tesseract to PATH...
setx PATH "%PATH%;%TESSERACT_DIR%"

REM Test installation
echo Testing Tesseract installation...
"%TESSERACT_DIR%\tesseract.exe" --version

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Tesseract installed successfully!
    echo Tesseract is now available at: %TESSERACT_DIR%
    echo PATH has been updated to include Tesseract.
) else (
    echo.
    echo ⚠ Tesseract installation may have issues.
    echo Please check the installation manually.
)

pause 