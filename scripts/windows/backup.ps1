Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = Join-Path $RootDir "backups\$Timestamp"
$InstanceDir = Join-Path $RootDir "instance"
$DbFile = Join-Path $InstanceDir "labdesk.sqlite"
$UploadsDir = Join-Path $InstanceDir "uploads"

Set-Location $RootDir

if (-not (Test-Path $DbFile)) {
    throw "Database file not found at $DbFile"
}

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
Copy-Item $DbFile (Join-Path $BackupDir "labdesk.sqlite")

if (Test-Path $UploadsDir) {
    Copy-Item $UploadsDir (Join-Path $BackupDir "uploads") -Recurse
}

Write-Host "Backup created at $BackupDir"
