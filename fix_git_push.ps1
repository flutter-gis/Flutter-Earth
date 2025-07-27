# Git Push Issues Fix Script
# This script will diagnose and fix common git push problems

Write-Host "🔍 Diagnosing Git Push Issues..." -ForegroundColor Yellow

# 1. Check git status
Write-Host "`n📊 Checking Git Status..." -ForegroundColor Cyan
git status

# 2. Check remote configuration
Write-Host "`n🌐 Checking Remote Configuration..." -ForegroundColor Cyan
git remote -v

# 3. Check git configuration
Write-Host "`n⚙️ Checking Git Configuration..." -ForegroundColor Cyan
git config --list | Select-String "user"

# 4. Check if there are any uncommitted changes
Write-Host "`n📝 Checking for Uncommitted Changes..." -ForegroundColor Cyan
$uncommitted = git diff --name-only
$staged = git diff --cached --name-only
$untracked = git ls-files --others --exclude-standard

if ($uncommitted -or $staged -or $untracked) {
    Write-Host "❌ Found uncommitted changes!" -ForegroundColor Red
    Write-Host "Uncommitted files: $uncommitted" -ForegroundColor Red
    Write-Host "Staged files: $staged" -ForegroundColor Red
    Write-Host "Untracked files: $untracked" -ForegroundColor Red
    
    Write-Host "`n💡 To fix this, run:" -ForegroundColor Yellow
    Write-Host "git add ." -ForegroundColor Green
    Write-Host "git commit -m 'Your commit message'" -ForegroundColor Green
    Write-Host "git push" -ForegroundColor Green
} else {
    Write-Host "✅ No uncommitted changes found" -ForegroundColor Green
}

# 5. Check authentication
Write-Host "`n🔐 Checking Authentication..." -ForegroundColor Cyan
try {
    $auth = git config --global credential.helper
    if ($auth) {
        Write-Host "✅ Credential helper configured: $auth" -ForegroundColor Green
    } else {
        Write-Host "❌ No credential helper configured" -ForegroundColor Red
        Write-Host "💡 To fix this, run:" -ForegroundColor Yellow
        Write-Host "git config --global credential.helper manager-core" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error checking authentication" -ForegroundColor Red
}

# 6. Test push with verbose output
Write-Host "`n🚀 Testing Push..." -ForegroundColor Cyan
Write-Host "Attempting to push with verbose output..." -ForegroundColor Yellow
git push --verbose

Write-Host "`n✅ Diagnosis Complete!" -ForegroundColor Green
 