param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 5000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$DbFile = Join-Path $RootDir "instance\labdesk.sqlite"
$UploadsDir = Join-Path $RootDir "instance\uploads"
$BackupsDir = Join-Path $RootDir "backups"

Set-Location $RootDir

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    throw "FAIL: virtual environment not found. Run scripts/windows/setup.ps1 first."
}

if (-not (Test-Path $DbFile)) {
    throw "FAIL: database file not found at $DbFile"
}

if (-not (Test-Path $UploadsDir)) {
    throw "FAIL: uploads directory not found at $UploadsDir"
}

if (-not (Test-Path $BackupsDir)) {
    New-Item -ItemType Directory -Force -Path $BackupsDir | Out-Null
}

$Url = "http://$HostName`:$Port/"
try {
    $Response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
} catch {
    throw "FAIL: could not reach $Url - $($_.Exception.Message)"
}

if ($Response.StatusCode -ge 400) {
    throw "FAIL: $Url returned status $($Response.StatusCode)"
}

Write-Host "OK: app reachable at $Url (status $($Response.StatusCode))"
Write-Host "OK: database file exists"
Write-Host "OK: uploads directory exists"
Write-Host "OK: backups directory exists"
