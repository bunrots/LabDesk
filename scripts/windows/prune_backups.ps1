param(
    [int]$KeepCount = 45
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($KeepCount -lt 1) {
    throw "KeepCount must be at least 1."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$BackupsDir = Join-Path $RootDir "backups"

Set-Location $RootDir

if (-not (Test-Path $BackupsDir)) {
    New-Item -ItemType Directory -Force -Path $BackupsDir | Out-Null
    Write-Host "Backups directory created at $BackupsDir"
    return
}

$Folders = Get-ChildItem -Path $BackupsDir -Directory | Sort-Object Name -Descending

if ($Folders.Count -le $KeepCount) {
    Write-Host "Nothing to prune. Found $($Folders.Count) backup folder(s), keep count is $KeepCount."
    return
}

$FoldersToRemove = $Folders | Select-Object -Skip $KeepCount

foreach ($Folder in $FoldersToRemove) {
    Remove-Item -Path $Folder.FullName -Recurse -Force
    Write-Host "Removed old backup $($Folder.FullName)"
}

Write-Host "Backup pruning complete."
