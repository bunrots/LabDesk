# Arabic Lab Reporting Desk MVP Plan

## Product Goal

Deliver a standalone Arabic-first lab reporting desk for small teams that need fast patient lookup, result entry, A4 report printing, and stable report history without the complexity of a full LIS.

## MVP Scope

- Patient search and creation
- DOB-only patient intake with day/month/year entry or direct date input
- Draft report creation linked to one patient
- One report containing one or more report sections
- Seeded Arabic section catalog for the lab's current tests
- Result entry using `numeric`, `choice`, and `text` field types
- Preview, finalize, print, and reprint
- Finalized snapshot storage
- Revision flow that creates a new draft from a finalized report
- Name-first workflow with timestamp-random internal patient/report identifiers
- Settings-backed lab branding and basic template management

## Explicitly Deferred

- Billing and receipts
- Inventory and sample lifecycle tracking
- Analyzer integration
- Advanced permissions and authentication
- In-app template designer
- PDF generation beyond browser-native print

## Implementation Notes

- Flask with server-rendered Jinja templates
- SQLite database stored in `instance/labdesk.sqlite`
- Seeded test definitions and reference ranges live in `labdesk/seeds.py`
- Facility profile and section/template metadata are configurable from `/settings`
- Draft reports are editable; finalized reports are read-only
- Reprints use stored snapshot HTML rather than live recalculation
- Arabic RTL layout and print CSS are part of the initial build

## Current Routes

- `/` and `/patients`
- `/reports/new`
- `/reports/<id>/edit`
- `/reports/<id>/preview`
- `/reports/<id>/finalize`
- `/reports/history`
- `/reports/<id>`
- `/reports/<id>/revise`
- `/settings`
