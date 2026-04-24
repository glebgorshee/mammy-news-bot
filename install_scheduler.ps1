#requires -Version 5.1
# Устанавливает/обновляет задачу в Планировщике: запуск бота 3 раза в день.
# Запускается один раз пользователем.

$ErrorActionPreference = "Stop"

$taskName = "MammyNewsBot"
$scriptPath = "C:\Users\FudziYama\Desktop\claude\news-bot\run_bot.ps1"

# Удалить старую задачу если есть
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Старая задача удалена"
}

# Действие: запустить PowerShell со скриптом, скрытое окно
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`""

# Триггеры: 3 раза в день — 9:00, 15:00, 21:00 МСК
$t1 = New-ScheduledTaskTrigger -Daily -At 9:00AM
$t2 = New-ScheduledTaskTrigger -Daily -At 3:00PM
$t3 = New-ScheduledTaskTrigger -Daily -At 9:00PM

# Настройки: будить компьютер, запускать при следующей возможности если пропустили,
# не запускать на батарее, перезапускать при сбое
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries:$false `
    -DontStopIfGoingOnBatteries:$true `
    -WakeToRun:$true `
    -StartWhenAvailable:$true `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5)

# Регистрируем от имени текущего пользователя (по умолчанию)
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger @($t1, $t2, $t3) `
    -Settings $settings `
    -User "$env:USERDOMAIN\$env:USERNAME" | Out-Null
Write-Host "Задача '$taskName' создана. Запуск: 9:00 / 15:00 / 21:00 ежедневно."

# Включаем таймеры пробуждения в плане питания (на AC)
# GUID bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d = Allow wake timers
powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP bd3b718a-0680-4d9d-8ab2-e1d2b4ac806d 1 | Out-Null
powercfg /setactive SCHEME_CURRENT | Out-Null
Write-Host "Таймеры пробуждения включены для плана питания (от сети)."

# Показываем итог
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State
