# Arabic Lab Reporting Desk Handbook

## Purpose

This project is a focused lab reporting application, not a full LIS.

Its job is to make this workflow fast and predictable:

1. Search for a patient.
2. Create a patient if needed.
3. Open a draft report.
4. Add one or more report sections.
5. Enter results.
6. Preview and print.
7. Finalize and reprint later from history.

The app is intentionally narrower than OpenELIS or Al Wafi. It prioritizes speed, Arabic-first operation, and printable reports.

## Current Workflow

### Reception

- The main page does not show patients until the user searches.
- Search results are paginated.
- Recent reports are shown in a small list for quick continuation.
- Creating a new patient immediately opens a draft report.

### Patient File

- Each patient has a file page showing all reports for that patient.
- New reports can also be created from the patient file.

### Draft Reports

- Drafts are editable.
- Drafts can be cancelled and deleted.
- A draft can contain multiple sections.

### Final Reports

- Finalized reports are read-only.
- Reprints come from stored snapshot HTML.
- Revisions create a new draft from a finalized report.

## Report Sections

The app uses section templates.

Each section has one of three types:

### `panel`

Use for normal grouped analyte tables.

Examples:

- CBC
- Electrolytes
- Renal panel
- Liver panel
- Lipids

### `structured`

Use for sections that are still made of fields, but are not just a simple analyte table.

Examples:

- Urine
- Stool
- CSF
- Blood smear

### `custom`

Use for a free-text report block.

This is useful for one-off or unusual report styles that do not fit the seeded templates yet.

## Test Field Types

Each test definition has one of three result types:

### `numeric`

Use for measured values.

Supports:

- unit
- printed reference text
- low value
- high value
- automatic `مرتفع` / `منخفض` flagging when a range is present

### `choice`

Use for fixed options.

Examples:

- `إيجابي / سلبي`
- blood group or compatibility values

Supports:

- predefined options list only

### `text`

Use for descriptive results.

Examples:

- smear description
- urine note
- stool note
- custom narrative report

Supports:

- free text entry only

## Reference Ranges

### What exists now

The system currently supports three levels:

1. Seeded sex/age-aware ranges in the codebase for the built-in common tests
2. A simple default range in the settings UI for newly created numeric tests
3. Optional advanced range rows in the settings UI for numeric tests when sex or age-specific rules are needed

### What the settings UI edits

For a newly added numeric test, the settings screen can store:

- printed reference text
- low value
- high value

This is stored as a generic default range.

For saved numeric tests, the advanced range block can also store optional rows with:

- sex filter
- minimum age in days
- maximum age in days
- low value
- high value
- printed reference text

### What is not yet in the settings UI

The admin UI now supports optional advanced rows, but it is still intentionally simple:

- age is entered in days only
- there is no bulk range editor
- there is no clone/import helper for many bands at once

## Settings Screen

The settings screen has two responsibilities:

1. Facility identity and print branding
2. Section and test template management

### Facility Identity

Includes:

- facility name
- report title
- subtitle
- three official header lines
- top descriptive note
- footer text
- accent color
- facility logo

### Template Management

Includes:

- creating a section
- creating a test
- renaming sections
- enabling/disabling sections
- editing tests
- enabling/disabling tests

### Important behavior

- Numeric tests show unit and range fields
- Choice tests show options only
- Text tests hide both choice and range-only controls

## Print Behavior

### Preview vs final

- Draft preview uses the current print template live
- Finalized reports store snapshot HTML

### Development behavior

In debug mode, finalized report display is allowed to re-render with the current template so print layout changes can be reviewed during development.

### Design intent

The print template aims to:

- fit A4 cleanly
- support Arabic RTL
- keep sections compact
- preserve facility branding
- support a faded watermark/logo

## Main Routes

### Patient and intake

- `/`
- `/patients`
- `/patients/<id>`

### Reports

- `/reports/new`
- `/reports/<id>/edit`
- `/reports/<id>/preview`
- `/reports/<id>/finalize`
- `/reports/<id>`
- `/reports/<id>/revise`
- `/reports/<id>/cancel`
- `/reports/history`

### Settings

- `/settings`

## Data Storage

SQLite database:

- `instance/labdesk.sqlite`

Primary tables:

- `patients`
- `reports`
- `report_sections`
- `report_items`
- `section_templates`
- `test_definitions`
- `reference_ranges`
- `lab_profile`

## Seeded Catalog

The built-in test and section catalog lives in:

- `labdesk/seeds.py`

This file also contains the initial seeded reference ranges.

## Current Constraints

- No authentication yet
- No billing
- No analyzer integration
- No inventory/sample tracking
- No full visual template designer
- No admin UI yet for advanced sex/age-specific range editing

## Safe Areas to Modify

Usually safe:

- branding and print styling
- settings page UI
- section/test editor UX
- compactness and spacing
- seeded test catalog

Needs extra care:

- finalized report snapshot behavior
- reference range logic
- report print layout
- anything that changes result field naming or persistence
