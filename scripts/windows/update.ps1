param(
    [string]$TargetRef = "",
    [string]$RemoteName = "origin",
    [switch]$SkipBackup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Set-Location $RootDir

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git was not found."
}

if (-not (Test-Path .\.git)) {
    throw "This folder is not a Git repository."
}

& git diff --quiet
if ($LASTEXITCODE -ne 0) {
    throw "Tracked local changes were found. Commit or discard them before updating."
}

& git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    throw "Tracked staged changes were found. Commit or discard them before updating."
}

if (-not $SkipBackup) {
    & (Join-Path $ScriptDir "backup.ps1")
}

Write-Host "Fetching updates from $RemoteName..."
& git fetch --prune --tags $RemoteName
if ($LASTEXITCODE -ne 0) {
    throw "git fetch failed."
}

if ([string]::IsNullOrWhiteSpace($TargetRef)) {
    $RemoteHead = (& git symbolic-ref --quiet --short "refs/remotes/$RemoteName/HEAD" 2>$null).Trim()
    if ($RemoteHead) {
        $TargetRef = $RemoteHead.Substring($RemoteName.Length + 1)
    } else {
        $TargetRef = "main"
    }
}

$ResolvedRef = $null
$DisplayRef = $TargetRef
$TargetKind = $null

& git show-ref --verify --quiet "refs/tags/$TargetRef"
if ($LASTEXITCODE -eq 0) {
    $ResolvedRef = "refs/tags/$TargetRef"
    $TargetKind = "tag"
} else {
    & git show-ref --verify --quiet "refs/remotes/$RemoteName/$TargetRef"
    if ($LASTEXITCODE -eq 0) {
        $ResolvedRef = "refs/remotes/$RemoteName/$TargetRef"
        $DisplayRef = "$RemoteName/$TargetRef"
        $TargetKind = "branch"
    } else {
        & git rev-parse --verify --quiet "$TargetRef`^{commit}"
        if ($LASTEXITCODE -eq 0) {
            $ResolvedRef = $TargetRef
            $TargetKind = "commit"
        }
    }
}

if (-not $ResolvedRef) {
    throw "Could not resolve target ref: $TargetRef. Use a Git tag such as v0.2.0 or a branch name such as main."
}

if ($TargetKind -eq "branch") {
    & git show-ref --verify --quiet "refs/heads/$TargetRef"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Switching to local branch $TargetRef..."
        & git switch $TargetRef
    } else {
        Write-Host "Creating tracking branch $TargetRef from $RemoteName/$TargetRef..."
        & git switch --track -c $TargetRef "$RemoteName/$TargetRef"
    }

    if ($LASTEXITCODE -ne 0) {
        throw "git switch failed."
    }

    & git branch --set-upstream-to="$RemoteName/$TargetRef" $TargetRef | Out-Null
    Write-Host "Fast-forwarding $TargetRef from $RemoteName/$TargetRef..."
    & git pull --ff-only
    if ($LASTEXITCODE -ne 0) {
        throw "git pull --ff-only failed."
    }
} elseif ($TargetKind -eq "tag" -or $TargetKind -eq "commit") {
    Write-Host "Checking out $DisplayRef..."
    & git checkout --detach $ResolvedRef
    if ($LASTEXITCODE -ne 0) {
        throw "git checkout failed."
    }
} else {
    throw "Unexpected target type for $TargetRef"
}

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    Write-Host "Virtual environment not found. Creating it now..."
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv .venv
    } else {
        throw "Python 3 was not found."
    }
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

New-Item -ItemType Directory -Force -Path .\instance\uploads | Out-Null
New-Item -ItemType Directory -Force -Path .\backups | Out-Null

$CurrentCommit = (& git rev-parse --short HEAD).Trim()
Write-Host "Update complete."
if ($TargetKind -eq "branch") {
    Write-Host "Current ref: $TargetRef"
} else {
    Write-Host "Current ref: $DisplayRef"
}
Write-Host "Current commit: $CurrentCommit"
Write-Host "Next steps:"
Write-Host "1. Start the app with powershell -ExecutionPolicy Bypass -File .\scripts\windows\run.ps1"
Write-Host "2. Verify it with powershell -ExecutionPolicy Bypass -File .\scripts\windows\healthcheck.ps1"
