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
- `scripts/linux/update.sh`
- `scripts/linux/healthcheck.sh`

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

### Health check

```bash
./scripts/linux/healthcheck.sh
```

Optional environment variables:

- `HOST`
- `PORT`

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
- `scripts/windows/update.ps1`
- `scripts/windows/healthcheck.ps1`
- `scripts/windows/prune_backups.ps1`
- `scripts/windows/register_tasks.ps1`
- `scripts/windows/unregister_tasks.ps1`

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

### Health check

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\healthcheck.ps1
```

Optional parameters:

- `-HostName`
- `-Port`

### Scheduling backups

Use Windows Task Scheduler.

Recommended task:

- trigger: daily
- action: `powershell.exe`
- arguments: `-ExecutionPolicy Bypass -File C:\path\to\project\scripts\windows\backup.ps1`

### Register scheduled tasks automatically

This project also includes a helper script that registers three tasks:

- start the app at user logon
- run a daily backup
- prune older backups weekly

Example:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\register_tasks.ps1
```

Optional parameters:

- `-TaskPrefix`
- `-HostName`
- `-Port`
- `-DailyBackupTime`
- `-WeeklyCleanupTime`
- `-WeeklyCleanupDay`
- `-KeepBackupCount`

Example with custom settings:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\register_tasks.ps1 `
  -TaskPrefix "LabDesk" `
  -HostName 0.0.0.0 `
  -Port 5000 `
  -DailyBackupTime 20:00 `
  -WeeklyCleanupDay Sunday `
  -WeeklyCleanupTime 03:00 `
  -KeepBackupCount 45
```

The default retention policy keeps the newest `45` backup folders.

### Remove scheduled tasks

If you need to remove the registered Windows tasks later:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\unregister_tasks.ps1
```

Optional parameter:

- `-TaskPrefix`

## Updating

Recommended update model:

1. Stop the running app.
2. Run the updater script with a target Git tag or branch.
3. Start the app again.
4. Run the health check.

The updater script:

- creates a backup first by default
- fetches tags and branches from the remote
- uses normal tracking for branches like `main`
- checks out tags in detached mode for stable deployments
- refreshes Python dependencies
- preserves `instance/` and `backups/`

### Linux update

Deploy a specific tagged release:

```bash
./scripts/linux/update.sh v0.2.0
```

Deploy the latest `main` branch state from `origin`:

```bash
./scripts/linux/update.sh main
```

If you run the script without an argument, it follows the remote default branch automatically.

Optional environment variables:

- `REMOTE` to use a remote other than `origin`
- `SKIP_BACKUP=1` if you intentionally want to skip the automatic backup

### Windows update

Deploy a specific tagged release:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\update.ps1 -TargetRef v0.2.0
```

Deploy the latest `main` branch state from `origin`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\update.ps1 -TargetRef main
```

If you run the script without `-TargetRef`, it follows the remote default branch automatically.

Optional parameters:

- `-RemoteName`
- `-SkipBackup`

### Important update notes

- The scripts intentionally refuse to continue if tracked local code changes exist.
- Untracked runtime folders such as `instance/` and `backups/` are not touched.
- Branches like `main` stay attached and fast-forward on update.
- Tags remain pinned by detached checkout, which is useful for fixed releases.

Do not delete:

- `instance/labdesk.sqlite`
- `instance/uploads/`
- `backups/`

## Notes

- The built-in test catalog is seeded on a fresh database automatically.
- This deployment model intentionally avoids Docker for now to keep same-day rollout simple.
- A future release can add more formal service wrappers or container deployment if needed.
