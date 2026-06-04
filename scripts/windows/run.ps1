param(
    [string]$HostName = "0.0.0.0",
    [int]$Port = 5000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Set-Location $RootDir

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    throw "Virtual environment not found. Run scripts/windows/setup.ps1 first."
}

New-Item -ItemType Directory -Force -Path .\instance\uploads | Out-Null
New-Item -ItemType Directory -Force -Path .\backups | Out-Null

& .\.venv\Scripts\python.exe -m waitress --host=$HostName --port=$Port app:app
