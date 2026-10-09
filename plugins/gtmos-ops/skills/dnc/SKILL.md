---
name: dnc
description: Check, export, add, import or remove Do Not Contact (DNC) records for a TTT client in GTMOS through the gtmos MCP server. Use when someone asks "is this list safe to load", "check these emails against Globex's DNC", "add acme.com to Acme's DNC", "import this opt-out CSV", "why was this lead push held", or "does this client even have DNC data". Always batch checks; never loop dnc_check.
argument-hint: "[client]"
---

# DNC in GTMOS

DNC is per client: `jane@acme.com` can be blocked for one client and fine for another. Every
question starts with **which client**. An answer without a client named means nothing.

GTMOS's DNC gates the two things GTMOS owns: **lead push to the CRM** and **call-queue task
creation**. Getting contacts out of PhoneBurner or EmailBison is a separate, superadmin-owned
process. Load the list, report what landed, stop there; don't promise dialer removal.

## Check a list: `dnc_check_batch`, always

Up to **1,000 contacts per call**, ~0.75s. One `dnc_check` per row costs ~1.2s each. That loop
was 136,000 calls in 30 days. Use `dnc_check` only for a single ad-hoc lookup.

`dnc_check_batch { client_id, contacts: [{ email?, phone?, domain? }, …] }`. A check matches on any
identifier plus the domain derived from an email, so an email-only check still catches a
company-wide block.

`contactable` has **three** values. Treat it that way:

| `status` | `contactable` | Meaning |
|---|---|---|
| `do_not_contact` | `false` | Matched. `matched_on: "domain"` means the whole company. |
| `ok` | `true` | Checked against ≥1 real source, no match. |
| `no_dnc_data` | `null` | The client has **zero DNC sources**. Nothing was checked. Not a pass. |
| `invalid_identifier` | `null` | The row had no email, phone or domain. |

Never report `null` as safe. Report the counters (`checked`, `suppressed`, `contactable`,
`unknown`, `invalid`) and **always** the envelope's `dnc_last_synced_at` / `dnc_data_age_days`.
A large entry count on a list last synced weeks ago is not protection. Clients have been dialled
against lists 21–44 days stale while every check said they were fine. Over ~7 days old, say so.

## Audit a client's DNC

- `list_dnc_sources { client_id }`: every source with type (`hubspot_list`, `csv`, `manual`),
  level, entry count and sync health. A source not in `ok` state is frozen at its last good read.
  `csv` sources never re-sync on their own. Zero sources means nothing suppresses this client
  anywhere. Hand that over as a finding.
- `list_dnc_entries { client_id, search?, identifier_type?, source_id?, added_after? }`: page
  with `next_cursor` until it's null. A DNC export is suppression PII: don't write it into the
  repo or a client folder.

## Add or import (needs a GTM-write token)

- One person or domain: `admin_add_dnc_entry`. Re-adding the same identifier returns the existing
  entry with `created: false`. `Idempotency-Key` is **not** enforced here, so don't rely on it.
- A list: `admin_import_dnc_entries { client_id, source_label, entries | csv, mode, dry_run }` into a **named source**. Copy `source_label` exactly from
  `list_dnc_sources`. A near-miss label silently plans a new source (`source_id: null` in the
  dry run).
  - `mode: "append"` adds. `mode: "replace"` **deletes every entry of that source not in your
    payload**. Never `replace` a source you didn't create.
  - Run with `dry_run: true`, show the diff and sample, confirm, then `dry_run: false`.
- **Never suppress a consumer domain** (`gmail.com`, `outlook.com`, …). It would block every
  contact on it for that client. GTMOS drops these server-side and counts them as skipped.

## Remove

`admin_remove_dnc_entry { id }` only deletes entries owned by a **`manual`** source. A row inside
a `csv` or `hubspot_list` source returns 409: re-import that source without the row, or have ops
remove it from the HubSpot list. Confirm before un-suppressing anyone. Un-blocking a genuine
opt-out is the worse error.

## "Why was this lead push held?"

| Outcome | Meaning | Fix |
|---|---|---|
| `do_not_contact` | A real match. | Expected. Report what matched. |
| `dnc_check_error` | The lookup failed. Not a match. | Transient; replay with `admin_leads_backfill`. |
| `no_dnc_data` | The client has no DNC sources. | Load a source, then backfill. Not retryable before that. |

A client with no HubSpot portal has no list to sync. Its suppression has to arrive as a client
CSV, which is ops' job.
