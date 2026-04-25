#requires -Version 5.1
# Собирает .env + state.json в один zip-архив для переноса на Mac.
# Эти файлы НЕ В ГИТЕ (секреты + история постов).

$botDir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath('Desktop')
$zipPath = Join-Path $desktop "mammy-news-migration.zip"

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

$files = @()
foreach ($f in @(".env", "state.json")) {
    $full = Join-Path $botDir $f
    if (Test-Path $full) { $files += $full }
}

if ($files.Count -eq 0) {
    Write-Host "Нечего архивировать — .env и state.json не найдены."
    exit 1
}

Compress-Archive -Path $files -DestinationPath $zipPath -Force
Write-Host "Готово: $zipPath"
Write-Host ""
Write-Host "Файлы внутри:"
$files | ForEach-Object { Write-Host "  $(Split-Path $_ -Leaf)" }
Write-Host ""
Write-Host "Перенесите этот zip на Mac (через iCloud Drive, AirDrop, USB или email)."
Write-Host "На Mac распакуйте его прямо в папку с клонированным news-bot/."
