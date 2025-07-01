@echo off
REM Flutter Earth Git Push Script (Windows Batch)
REM This script automates the git push process for the Flutter Earth project

setlocal enabledelayedexpansion

REM Set colors for output
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Function to print colored output
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM Function to check if git is available
:check_git
git --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Git is not installed or not in PATH"
    exit /b 1
)
goto :eof

REM Function to check if we're in a git repository
:check_repo
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    call :print_error "Not in a git repository"
    exit /b 1
)
goto :eof

REM Function to check git status
:check_status
call :print_status "Checking git status..."
git diff-index --quiet HEAD --
if errorlevel 1 (
    call :print_status "Changes detected"
    exit /b 0
) else (
    call :print_warning "No changes to commit"
    exit /b 1
)

REM Function to add all changes
:add_changes
call :print_status "Adding all changes..."
git add .
if errorlevel 1 (
    call :print_error "Failed to add changes"
    exit /b 1
)
call :print_success "Changes added to staging area"
goto :eof

REM Function to commit changes
:commit_changes
set "commit_message=%~1"
if "%commit_message%"=="" (
    REM Generate default commit message
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "date_str=%%c-%%b-%%a"
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "time_str=%%a%%b"
    set "commit_message=Update Flutter Earth project - !date_str! !time_str!"
)

call :print_status "Committing changes with message: %commit_message%"
git commit -m "%commit_message%"
if errorlevel 1 (
    call :print_error "Failed to commit changes"
    exit /b 1
)
call :print_success "Changes committed successfully"
goto :eof

REM Function to push changes
:push_changes
call :print_status "Pushing changes to remote repository..."

REM Get current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set "current_branch=%%i"
call :print_status "Current branch: %current_branch%"

REM Push to remote
git push origin "%current_branch%"
if errorlevel 1 (
    call :print_error "Failed to push changes"
    exit /b 1
)
call :print_success "Changes pushed successfully to %current_branch%"
goto :eof

REM Function to show git status
:show_status
call :print_status "Current git status:"
echo ==================
git status --short
echo ==================
goto :eof

REM Function to show recent commits
:show_recent_commits
call :print_status "Recent commits:"
echo ==================
git log --oneline -5
echo ==================
goto :eof

REM Function to check remote status
:check_remote
call :print_status "Checking remote status..."

REM Fetch latest changes
git fetch origin

REM Check if local is behind remote
for /f "tokens=*" %%i in ('git branch --show-current') do set "current_branch=%%i"
for /f "tokens=*" %%i in ('git rev-list HEAD..origin/%current_branch% --count') do set "behind_count=%%i"

if %behind_count% gtr 0 (
    call :print_warning "Local branch is %behind_count% commits behind remote"
    call :print_status "Consider pulling latest changes first"
    exit /b 1
) else (
    call :print_success "Local branch is up to date with remote"
    exit /b 0
)

REM Main function
:main
call :print_status "Starting Flutter Earth Git Push Script"
echo ==============================================

REM Check prerequisites
call :check_git
if errorlevel 1 exit /b 1

call :check_repo
if errorlevel 1 exit /b 1

REM Parse command line arguments
set "commit_message="
set "auto_commit=false"
set "show_info=false"

:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="-m" (
    set "commit_message=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--message" (
    set "commit_message=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="-a" (
    set "auto_commit=true"
    shift
    goto :parse_args
)
if "%~1"=="--auto" (
    set "auto_commit=true"
    shift
    goto :parse_args
)
if "%~1"=="-s" (
    set "show_info=true"
    shift
    goto :parse_args
)
if "%~1"=="--status" (
    set "show_info=true"
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    echo Usage: %~nx0 [OPTIONS]
    echo Options:
    echo   -m, --message MESSAGE  Commit message
    echo   -a, --auto            Auto-commit with default message
    echo   -s, --status          Show git status and recent commits
    echo   -h, --help            Show this help message
    exit /b 0
)
if "%~1"=="--help" (
    echo Usage: %~nx0 [OPTIONS]
    echo Options:
    echo   -m, --message MESSAGE  Commit message
    echo   -a, --auto            Auto-commit with default message
    echo   -s, --status          Show git status and recent commits
    echo   -h, --help            Show this help message
    exit /b 0
)
call :print_error "Unknown option: %~1"
echo Use -h or --help for usage information
exit /b 1

:end_parse

REM Show status if requested
if "%show_info%"=="true" (
    call :show_status
    call :show_recent_commits
    call :check_remote
    exit /b 0
)

REM Check remote status
call :check_remote
if errorlevel 1 (
    call :print_warning "Consider pulling latest changes before pushing"
    set /p "continue=Continue anyway? (y/N): "
    if /i not "!continue!"=="y" (
        call :print_status "Aborted by user"
        exit /b 0
    )
)

REM Check if there are changes to commit
call :check_status
if errorlevel 1 (
    if "%auto_commit%"=="true" (
        call :print_warning "No changes to commit, but auto-commit was requested"
        exit /b 0
    ) else (
        call :print_status "No changes to commit"
        exit /b 0
    )
)

REM Show current status
call :show_status

REM Auto-commit or prompt for action
if "%auto_commit%"=="true" (
    call :add_changes
    if errorlevel 1 exit /b 1
    call :commit_changes "%commit_message%"
    if errorlevel 1 exit /b 1
) else (
    set /p "commit_changes=Add and commit changes? (Y/n): "
    if /i "!commit_changes!"=="n" (
        call :print_status "Aborted by user"
        exit /b 0
    )
    
    call :add_changes
    if errorlevel 1 exit /b 1
    call :commit_changes "%commit_message%"
    if errorlevel 1 exit /b 1
)

REM Push changes
call :push_changes
if errorlevel 1 (
    call :print_error "Git push failed"
    exit /b 1
)

call :print_success "Git push completed successfully!"
call :show_recent_commits
exit /b 0

REM Run main function
call :main %* 