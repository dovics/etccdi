# 设置目标路径
$targetPath = ".\intermediate_data"

if (Test-Path $targetPath) {
    # 获取目录下所有项
    Get-ChildItem -Path $targetPath | ForEach-Object {
        # 如果名称中不包含 era5 (不区分大小写)
        if ($_.Name -notmatch "era5") {
            Write-Host "正在删除: $($_.FullName)" -ForegroundColor Yellow
            Remove-Item $_.FullName -Recurse -Force
        }
    }
    Write-Host "清理完成！" -ForegroundColor Green
} else {
    Write-Host "找不到路径: $targetPath" -ForegroundColor Red
}