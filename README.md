# Arabic Lab Reporting Desk

Standalone Flask + SQLite MVP for Arabic-first patient lookup, result entry, A4 report printing, settings-driven branding, history, and report revision flow.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
.venv/bin/flask --app app run --debug
```

The app initializes its SQLite database automatically inside `instance/labdesk.sqlite`.

## Current MVP Features

- Patient search, patient-file view, and patient creation with strict DOB selectors
- Draft report creation
- Multi-section report editing from a seeded Arabic catalog
- Numeric, choice, and text result fields
- Reference range lookup with high/low highlighting for common numeric analytes
- Preview, finalize, stable snapshot storage, and browser printing
- Report history and revision creation
- Settings page for facility branding, accent color, official print-header lines, and compact template activation/renaming
