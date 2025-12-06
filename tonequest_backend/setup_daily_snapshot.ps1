# PowerShell script to set up Windows Task Scheduler for daily rank snapshots
# Run this script as Administrator

$taskName = "ToneQuest-DailyRankSnapshot"
$scriptPath = "d:\coding\dummy_quest\tonequest_backend"
$pythonPath = (Get-Command python).Source

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute $pythonPath `
    -Argument "-m app.scripts.snapshot_ranks" `
    -WorkingDirectory $scriptPath

# Create the trigger (daily at 4:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 4:00AM

# Create the task settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

# Register the scheduled task
Register-ScheduledTask -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Daily rank snapshot for ToneQuest leaderboard" `
    -Force

Write-Host "✓ Scheduled task '$taskName' created successfully!" -ForegroundColor Green
Write-Host "  - Runs daily at 4:00 AM" -ForegroundColor Cyan
Write-Host "  - Script: $scriptPath\app\scripts\snapshot_ranks.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "To verify, run: Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
