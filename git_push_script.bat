@echo off
REM Flutter Earth Repository Push Script
REM This script helps you commit and push all changes to the repository

echo 🚀 Flutter Earth Repository Push Script
echo ======================================

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Error: Not in a git repository!
    echo Please run this script from the Flutter Earth root directory.
    pause
    exit /b 1
)

REM Check git status
echo 📊 Checking git status...
git status

REM Add all files
echo 📁 Adding all files...
git add .

REM Get commit message from user
echo.
echo 💬 Enter commit message (or press Enter for default):
set /p commit_message=

REM Use default message if none provided
if "%commit_message%"=="" (
    set commit_message=�� v2.0.0: Enhanced GEE Crawler & Frontend Integration

✨ New Features:
- Enhanced Google Earth Engine crawler with comprehensive data extraction
- Automatic satellite data classification and categorization
- Ready-to-use Earth Engine code snippets for each dataset
- Frontend integration with real-time crawler data loading
- Smart satellite information display with detailed metadata
- Progress tracking and detailed logging

🛠️ Improvements:
- Streamlined data structure with essential fields only
- Better satellite detection with comprehensive keyword lists
- Improved data type categorization
- Enhanced frontend satellite info view
- Configuration integration with crawler output

🎨 UI/UX:
- Updated satellite information panels
- Real-time data loading from crawler output
- Interactive satellite details with code snippets
- Filtering by satellite, category, and publisher

📚 Documentation:
- Comprehensive README update with crawler documentation
- Usage instructions for enhanced features
- Development guidelines for crawler customization
- Technical architecture documentation
)

REM Commit changes
echo �� Committing changes...
git commit -m "%commit_message%"

REM Check if remote exists and push
echo 🌐 Pushing to remote repository...
git push origin main
if %errorlevel% equ 0 (
    echo ✅ Successfully pushed to repository!
) else (
    echo ⚠️  Push failed. Check your remote configuration.
    echo To add a remote repository, run:
    echo git remote add origin ^<your-repo-url^>
    echo Then run this script again.
)

echo.
echo �� Flutter Earth v2.0.0 is ready!
echo ==================================
echo ✨ Enhanced GEE Crawler with comprehensive data extraction
echo 🛰️ Real-time satellite data integration
echo �� Ready-to-use Earth Engine code snippets
echo 🎨 Beautiful themes and animations
echo 🌈 Inclusive design for everyone
echo.
echo 🌍 Happy Earth exploring! ✨
pause 