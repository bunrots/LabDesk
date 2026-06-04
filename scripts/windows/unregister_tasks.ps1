param(
    [string]$TaskPrefix = "LabDesk"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskNames = @(
    "$TaskPrefix Start App",
    "$TaskPrefix Daily Backup",
    "$TaskPrefix Weekly Backup Cleanup"
)

foreach ($TaskName in $TaskNames) {
    $Existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $Existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed task: $TaskName"
    } else {
        Write-Host "Task not found: $TaskName"
    }
}

Write-Host "Task removal complete."
