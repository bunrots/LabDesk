# Deployment Guide

## Goal

This project is designed for simple single-site deployment.

Recommended model:

- one machine per hospital or lab site
- browser access over the local network
- local SQLite database
- local scheduled backups

The app initializes its own database automatically on first run.

## Folders Created At Runtime

- `instance/labdesk.sqlite`
- `instance/uploads/`
- `backups/`

Keep `instance/` and `backups/` outside any future code-replacement workflow.

## Linux

Scripts:

- `scripts/linux/setup.sh`
- `scripts/linux/run.sh`
- `scripts/linux/backup.sh`

### First-time setup

```bash
chmod +x scripts/linux/*.sh
./scripts/linux/setup.sh
```

### Run the app

```bash
./scripts/linux/run.sh
```

Optional environment variables:

- `HOST`
- `PORT`

Example:

```bash
HOST=0.0.0.0 PORT=5000 ./scripts/linux/run.sh
```

### Backup

```bash
./scripts/linux/backup.sh
```

Each backup creates a timestamped folder inside `backups/`.

### Scheduling backups

Use `cron` or a `systemd` timer.

Simple `cron` example for daily 8 PM backups:

```cron
0 20 * * * /path/to/project/scripts/linux/backup.sh
```

## Windows

Scripts:

- `scripts/windows/setup.ps1`
- `scripts/windows/run.ps1`
- `scripts/windows/backup.ps1`

### First-time setup

Run PowerShell as a user who has access to the project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\setup.ps1
```

### Run the app

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\run.ps1
```

Optional parameters:

- `-HostName`
- `-Port`

Example:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\run.ps1 -HostName 0.0.0.0 -Port 5000
```

### Backup

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\backup.ps1
```

Each backup creates a timestamped folder inside `backups\`.

### Scheduling backups

Use Windows Task Scheduler.

Recommended task:

- trigger: daily
- action: `powershell.exe`
- arguments: `-ExecutionPolicy Bypass -File C:\path\to\project\scripts\windows\backup.ps1`

## Updating

Current recommended update model:

1. Stop the running app.
2. Back up `instance/` first.
3. Replace code files with the new release.
4. Re-run setup if `requirements.txt` changed.
5. Start the app again.

Do not delete:

- `instance/labdesk.sqlite`
- `instance/uploads/`
- `backups/`

## Notes

- The built-in test catalog is seeded on a fresh database automatically.
- This deployment model intentionally avoids Docker for now to keep same-day rollout simple.
- A future release can add more formal service wrappers or container deployment if needed.
