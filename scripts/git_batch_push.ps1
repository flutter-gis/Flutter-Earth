# Flutter Earth Git Batch Push Script (PowerShell)
# This script automates batch git operations for the Flutter Earth project

param(
    [string]$Message = "",
    [switch]$Auto,
    [switch]$Status,
    [switch]$Help
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Function to check if git is available
function Test-Git {
    try {
        $null = git --version
        return $true
    }
    catch {
        Write-Error "Git is not installed or not in PATH"
        return $false
    }
}

# Function to check if we're in a git repository
function Test-GitRepository {
    try {
        $null = git rev-parse --git-dir
        return $true
    }
    catch {
        Write-Error "Not in a git repository"
        return $false
    }
}

# Function to check git status
function Test-GitChanges {
    Write-Status "Checking git status..."
    
    try {
        git diff-index --quiet HEAD --
        if ($LASTEXITCODE -eq 0) {
            Write-Warning "No changes to commit"
            return $false
        } else {
            Write-Status "Changes detected"
            return $true
        }
    }
    catch {
        Write-Error "Failed to check git status"
        return $false
    }
}

# Function to add all changes
function Add-GitChanges {
    Write-Status "Adding all changes..."
    
    try {
        git add .
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Changes added to staging area"
            return $true
        } else {
            Write-Error "Failed to add changes"
            return $false
        }
    }
    catch {
        Write-Error "Failed to add changes: $($_.Exception.Message)"
        return $false
    }
}

# Function to commit changes
function Commit-GitChanges {
    param([string]$CommitMessage)
    
    if ([string]::IsNullOrEmpty($CommitMessage)) {
        $CommitMessage = "Update Flutter Earth project - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }
    
    Write-Status "Committing changes with message: $CommitMessage"
    
    try {
        git commit -m $CommitMessage
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Changes committed successfully"
            return $true
        } else {
            Write-Error "Failed to commit changes"
            return $false
        }
    }
    catch {
        Write-Error "Failed to commit changes: $($_.Exception.Message)"
        return $false
    }
}

# Function to push changes
function Push-GitChanges {
    Write-Status "Pushing changes to remote repository..."
    
    try {
        $CurrentBranch = git branch --show-current
        Write-Status "Current branch: $CurrentBranch"
        
        git push origin $CurrentBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Changes pushed successfully to $CurrentBranch"
            return $true
        } else {
            Write-Error "Failed to push changes"
            return $false
        }
    }
    catch {
        Write-Error "Failed to push changes: $($_.Exception.Message)"
        return $false
    }
}

# Function to show git status
function Show-GitStatus {
    Write-Status "Current git status:"
    Write-Host "==================" -ForegroundColor $White
    git status --short
    Write-Host "==================" -ForegroundColor $White
}

# Function to show recent commits
function Show-RecentCommits {
    Write-Status "Recent commits:"
    Write-Host "==================" -ForegroundColor $White
    git log --oneline -5
    Write-Host "==================" -ForegroundColor $White
}

# Function to check remote status
function Test-RemoteStatus {
    Write-Status "Checking remote status..."
    
    try {
        # Fetch latest changes
        git fetch origin
        
        $CurrentBranch = git branch --show-current
        $BehindCount = git rev-list HEAD..origin/$CurrentBranch --count
        
        if ([int]$BehindCount -gt 0) {
            Write-Warning "Local branch is $BehindCount commits behind remote"
            Write-Status "Consider pulling latest changes first"
            return $false
        } else {
            Write-Success "Local branch is up to date with remote"
            return $true
        }
    }
    catch {
        Write-Error "Failed to check remote status: $($_.Exception.Message)"
        return $false
    }
}

# Function to handle conflicts
function Handle-MergeConflicts {
    Write-Warning "Merge conflicts detected!"
    Write-Status "Please resolve conflicts manually and then run this script again"
    Write-Status "To abort merge: git merge --abort"
    Write-Status "To continue after resolving: git add . && git commit"
    exit 1
}

# Function to show help
function Show-Help {
    Write-Host "Usage: $($MyInvocation.MyCommand.Name) [OPTIONS]" -ForegroundColor $White
    Write-Host "Options:" -ForegroundColor $White
    Write-Host "  -Message <string>     Commit message" -ForegroundColor $White
    Write-Host "  -Auto                 Auto-commit with default message" -ForegroundColor $White
    Write-Host "  -Status               Show git status and recent commits" -ForegroundColor $White
    Write-Host "  -Help                 Show this help message" -ForegroundColor $White
    Write-Host "" -ForegroundColor $White
    Write-Host "Examples:" -ForegroundColor $White
    Write-Host "  $($MyInvocation.MyCommand.Name) -Message 'Fix bug in theme system'" -ForegroundColor $White
    Write-Host "  $($MyInvocation.MyCommand.Name) -Auto" -ForegroundColor $White
    Write-Host "  $($MyInvocation.MyCommand.Name) -Status" -ForegroundColor $White
}

# Main function
function Main {
    Write-Status "Starting Flutter Earth Git Batch Push Script"
    Write-Host "==============================================" -ForegroundColor $White
    
    # Show help if requested
    if ($Help) {
        Show-Help
        return
    }
    
    # Check prerequisites
    if (-not (Test-Git)) {
        exit 1
    }
    
    if (-not (Test-GitRepository)) {
        exit 1
    }
    
    # Show status if requested
    if ($Status) {
        Show-GitStatus
        Show-RecentCommits
        Test-RemoteStatus
        return
    }
    
    # Check remote status
    if (-not (Test-RemoteStatus)) {
        Write-Warning "Consider pulling latest changes before pushing"
        $Continue = Read-Host "Continue anyway? (y/N)"
        if ($Continue -notmatch "^[Yy]$") {
            Write-Status "Aborted by user"
            return
        }
    }
    
    # Check if there are changes to commit
    if (-not (Test-GitChanges)) {
        if ($Auto) {
            Write-Warning "No changes to commit, but auto-commit was requested"
            return
        } else {
            Write-Status "No changes to commit"
            return
        }
    }
    
    # Show current status
    Show-GitStatus
    
    # Auto-commit or prompt for action
    if ($Auto) {
        if (-not (Add-GitChanges)) {
            exit 1
        }
        if (-not (Commit-GitChanges -CommitMessage $Message)) {
            exit 1
        }
    } else {
        $CommitChanges = Read-Host "Add and commit changes? (Y/n)"
        if ($CommitChanges -match "^[Nn]$") {
            Write-Status "Aborted by user"
            return
        }
        
        if (-not (Add-GitChanges)) {
            exit 1
        }
        if (-not (Commit-GitChanges -CommitMessage $Message)) {
            exit 1
        }
    }
    
    # Push changes
    if (Push-GitChanges) {
        Write-Success "Git push completed successfully!"
        Show-RecentCommits
    } else {
        Write-Error "Git push failed"
        exit 1
    }
}

# Handle script interruption
trap {
    Write-Error "Script interrupted"
    exit 1
}

# Run main function
Main 