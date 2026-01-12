$targetPath = ".\intermediate_data"

if (Test-Path $targetPath) {
    Get-ChildItem -Path $targetPath | ForEach-Object {
        if ($_.Name -notmatch "era5") {
            Write-Host "Deleting: $($_.FullName)" -ForegroundColor Yellow
            Remove-Item $_.FullName -Recurse -Force
        }
    }
    Write-Host "Clean Finish: " -ForegroundColor Green
} else {
    Write-Host "Can't find path: $targetPath" -ForegroundColor Red
}
