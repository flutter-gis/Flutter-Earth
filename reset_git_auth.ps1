# Git Authentication Reset Script
# This script clears all git credentials and resets authentication

Write-Host "🔧 Clearing Git Authentication..." -ForegroundColor Yellow

# 1. Clear stored credentials
Write-Host "1. Clearing stored credentials..." -ForegroundColor Cyan
git config --global --unset credential.helper
git config --system --unset credential.helper
git config --local --unset credential.helper

# 2. Clear Windows Credential Manager entries
Write-Host "2. Clearing Windows Credential Manager..." -ForegroundColor Cyan
cmdkey /list | findstr git
cmdkey /delete:git:https://github.com

# 3. Clear any cached credentials
Write-Host "3. Clearing cached credentials..." -ForegroundColor Cyan
git config --global --unset-all credential.helper
git config --system --unset-all credential.helper

# 4. Reset user configuration
Write-Host "4. Resetting user configuration..." -ForegroundColor Cyan
git config --global --unset user.name
git config --global --unset user.email

# 5. Clear any stored tokens or keys
Write-Host "5. Clearing stored tokens..." -ForegroundColor Cyan
if (Test-Path "$env:USERPROFILE\.git-credentials") {
    Remove-Item "$env:USERPROFILE\.git-credentials" -Force
    Write-Host "   Removed .git-credentials file" -ForegroundColor Green
}

# 6. Check current remote configuration
Write-Host "6. Current remote configuration:" -ForegroundColor Cyan
git remote -v

# 7. Test authentication
Write-Host "7. Testing authentication..." -ForegroundColor Cyan
Write-Host "   You will be prompted for credentials on next push" -ForegroundColor Yellow

Write-Host "✅ Git authentication reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set your git user info: git config --global user.name 'Your Name'" -ForegroundColor White
Write-Host "2. Set your email: git config --global user.email 'your.email@example.com'" -ForegroundColor White
Write-Host "3. Try pushing: git push origin main" -ForegroundColor White
Write-Host "4. You'll be prompted for GitHub credentials" -ForegroundColor White 