param(
    [string]$TaskPrefix = "LabDesk",
    [string]$HostName = "0.0.0.0",
    [int]$Port = 5000,
    [string]$DailyBackupTime = "20:00",
    [string]$WeeklyCleanupTime = "03:00",
    [ValidateSet("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")]
    [string]$WeeklyCleanupDay = "Sunday",
    [int]$KeepBackupCount = 45
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$PowerShellExe = Join-Path $PSHOME "powershell.exe"
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

function Get-TimeToday([string]$TimeValue) {
    try {
        $Parsed = [DateTime]::ParseExact($TimeValue, "HH:mm", $null)
    } catch {
        throw "Time value '$TimeValue' must use HH:mm format."
    }
    return (Get-Date).Date.AddHours($Parsed.Hour).AddMinutes($Parsed.Minute)
}

function New-TaskActionForScript([string]$ScriptPath, [string]$Arguments) {
    $EscapedScript = '"' + $ScriptPath + '"'
    $FullArguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File $EscapedScript"
    if ($Arguments) {
        $FullArguments += " $Arguments"
    }
    return New-ScheduledTaskAction -Execute $PowerShellExe -Argument $FullArguments -WorkingDirectory $RootDir
}

function Register-OrReplaceTask(
    [string]$TaskName,
    $Action,
    $Trigger
) {
    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew

    $Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Force | Out-Null
}

Set-Location $RootDir

$RunScript = Join-Path $RootDir "scripts\windows\run.ps1"
$BackupScript = Join-Path $RootDir "scripts\windows\backup.ps1"
$PruneScript = Join-Path $RootDir "scripts\windows\prune_backups.ps1"

foreach ($Path in @($RunScript, $BackupScript, $PruneScript)) {
    if (-not (Test-Path $Path)) {
        throw "Required script not found: $Path"
    }
}

$StartupAction = New-TaskActionForScript -ScriptPath $RunScript -Arguments "-HostName `"$HostName`" -Port $Port"
$StartupTrigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
Register-OrReplaceTask -TaskName "$TaskPrefix Start App" -Action $StartupAction -Trigger $StartupTrigger

$BackupAction = New-TaskActionForScript -ScriptPath $BackupScript -Arguments ""
$BackupTrigger = New-ScheduledTaskTrigger -Daily -At (Get-TimeToday $DailyBackupTime)
Register-OrReplaceTask -TaskName "$TaskPrefix Daily Backup" -Action $BackupAction -Trigger $BackupTrigger

$CleanupAction = New-TaskActionForScript -ScriptPath $PruneScript -Arguments "-KeepCount $KeepBackupCount"
$CleanupTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $WeeklyCleanupDay -At (Get-TimeToday $WeeklyCleanupTime)
Register-OrReplaceTask -TaskName "$TaskPrefix Weekly Backup Cleanup" -Action $CleanupAction -Trigger $CleanupTrigger

Write-Host "Scheduled tasks registered:"
Write-Host " - $TaskPrefix Start App"
Write-Host " - $TaskPrefix Daily Backup"
Write-Host " - $TaskPrefix Weekly Backup Cleanup"
Write-Host ""
Write-Host "Current retention count: keep newest $KeepBackupCount backup folder(s)."
