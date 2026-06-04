# Arabic Lab Reporting Desk

Standalone Flask + SQLite app for Arabic-first patient lookup, result entry, A4 report printing, facility branding, report history, and revision flow.

## Quick Start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app app run --debug
```

The app initializes its SQLite database automatically inside `instance/labdesk.sqlite`.

## Core Features

- Patient search, patient-file view, and patient creation with strict DOB selectors
- Draft report creation and cancellation
- Multi-section report editing from a seeded Arabic catalog
- Numeric, choice, and text result fields
- Default and optional advanced sex/age-aware reference-range support with high/low highlighting
- Preview, finalize, stable snapshot storage, and browser printing
- Report history and revision creation
- Settings page for facility branding, print-header lines, accent color, and template management

## Documentation

- [Project Handbook](docs/HANDBOOK.md)
- [Architecture Notes](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Deployment

Cross-platform helper scripts live in:

- `scripts/linux/`
- `scripts/windows/`

Each platform currently includes:

- `setup`
- `run`
- `backup`
- `healthcheck`

Windows also includes:

- task registration / removal helpers

## Main Concepts

- `Panel`: standard grouped tests shown as a compact table
- `Structured`: mixed descriptive sections such as urine, stool, CSF, or smear-style sections
- `Custom`: a free-text section for unusual reports
- `Numeric` test: supports unit, printed reference text, low/high defaults, and high/low flagging
- `Choice` test: supports predefined options such as `إيجابي/سلبي`
- `Text` test: supports descriptive/manual narrative entry
