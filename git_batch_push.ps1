# PowerShell script to commit and push files in batches of 100
$files = git status --porcelain | Where-Object { $_ -match '^[AM\?]' } | ForEach-Object { $_.Substring(3) }
$batchSize = 100
for ($i = 0; $i -lt $files.Count; $i += $batchSize) {
    $batch = $files[$i..([Math]::Min($i + $batchSize - 1, $files.Count - 1))]
    git add $batch
    git commit -m "Batch commit $($i / $batchSize + 1)"
    git push
} 