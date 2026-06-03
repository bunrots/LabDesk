# Architecture Notes

## Stack

- Python
- Flask
- SQLite
- Jinja templates
- Local CSS and JS only

## App Shape

The app is server-rendered.

There is no SPA frontend. Most behavior is handled by:

- Flask routes in `labdesk/routes.py`
- business logic in `labdesk/services.py`
- schema and migrations in `labdesk/db.py`
- seeded catalog and built-in ranges in `labdesk/seeds.py`
- templates in `labdesk/templates/`
- styling in `labdesk/static/app.css`

## Key Files

### Backend

- `app.py`
- `labdesk/routes.py`
- `labdesk/services.py`
- `labdesk/db.py`
- `labdesk/seeds.py`

### Templates

- `labdesk/templates/base.html`
- `labdesk/templates/patients/index.html`
- `labdesk/templates/patients/show.html`
- `labdesk/templates/reports/edit.html`
- `labdesk/templates/reports/preview.html`
- `labdesk/templates/reports/show.html`
- `labdesk/templates/reports/_print_document.html`
- `labdesk/templates/reports/history.html`
- `labdesk/templates/settings/index.html`

### Static

- `labdesk/static/app.css`
- `labdesk/static/fonts/`

## Data Model Summary

### `patients`

Stores:

- internal patient number
- full name
- sex
- date of birth
- optional phone
- notes

### `reports`

Stores:

- internal report number
- patient link
- report date
- status: `draft` or `final`
- revision link
- print count
- snapshot HTML
- notes

### `report_sections`

One report can contain multiple sections.

Each section stores:

- section code
- Arabic display name
- section type
- display order

### `report_items`

Each item inside a section stores:

- test code
- Arabic label
- result type
- result value
- unit
- reference text
- computed flag
- comment

### `section_templates`

Admin-defined section catalog:

- code
- Arabic name
- type
- active state

### `test_definitions`

Admin-defined test catalog:

- section
- test code
- label
- result type
- default unit
- default choice list
- active state

### `reference_ranges`

Stores numeric range rules.

Currently used for:

- seeded built-in ranges
- generic default ranges created from the settings UI for numeric tests
- optional advanced sex/age-specific rows created from the settings UI for numeric tests

### `lab_profile`

Stores facility branding:

- facility name
- report title
- subtitle
- official header lines
- header notes
- footer text
- logo filename
- accent color

## Report Rendering

### Draft preview

Draft reports are rendered live using the current print template.

### Finalized reports

Finalized reports store snapshot HTML so reprints stay stable.

### Development override

When Flask runs in debug mode, finalized views may be re-rendered live so layout changes can be reviewed without re-finalizing everything manually.

## Settings UI Logic

### Section creation

Section types:

- `panel`
- `structured`
- `custom`

### Test creation

Conditional behavior:

- `numeric`: unit + range fields visible
- `choice`: choice options visible
- `text`: only plain text behavior

For saved numeric tests, the settings UI also exposes an optional advanced range manager that writes directly into `reference_ranges`.

## Styling Model

The UI uses CSS variables for shared brand styling.

Important variables:

- `--accent`
- `--brand`
- `--brand-deep`
- `--brand-soft`

The report print layout has additional dedicated styling for:

- letterhead
- watermark
- metadata table
- section headers
- printable results table

## Migration Philosophy

This project currently uses lightweight runtime migrations in `labdesk/db.py`.

That means:

- schema changes should stay simple
- new columns should be added carefully
- destructive migrations should be avoided unless explicitly planned

## Operational Notes

- The database is local SQLite
- The app is intended for small-lab local network deployment
- Browser print is the current output path
- The app is optimized for Arabic-first workflows
