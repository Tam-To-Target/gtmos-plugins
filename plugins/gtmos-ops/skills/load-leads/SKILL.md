---
name: load-leads
description: Load leads into GTMOS (and from there into the client's CRM) through the gtmos MCP server's admin_create_leads batch tool. Use when a GTM engineer wants to push, load, import or upload a list, CSV or set of contacts for a client ("load these 400 leads into Acme", "push this CSV to Globex's HubSpot", "add these prospects to the Naviance campaign"). Covers the dry run, attribution rules, lead_origin convention and how to read the results without crying wolf.
argument-hint: "[client] [file]"
---

# Loading leads into GTMOS

Leads go in through **`admin_create_leads`**: up to **15 leads per call**, one client per call.
Never loop `admin_create_lead` over a list. A real write costs ~3s per lead either way, so a
15-lead call takes ~45s — send chunks one after another, not in parallel, and expect ~3 minutes
per 60 leads. A dry run is ~10× faster.

If `admin_create_leads` is not in your tool list, the token is read-only. Tell the engineer to
mint a GTM-write token (GTMOS → Settings → API tokens) and update it with
`/plugin configure gtmos-ops@gtmos-plugins`.

## 1. Pin down the client

Use the GTMOS slug (`list_clients` if unsure). Say which client you are loading into before every
call; never carry one over from earlier without saying so.

## 2. Build the rows in GTMOS vocabulary

Each lead needs **`email` or `phone`**. Everything else is optional. Use GTMOS names; the rename to
HubSpot happens at push time:

| Send | HubSpot gets |
|---|---|
| `first_name`, `last_name` | `firstname`, `lastname` |
| `company_name` | `company` |
| `job_title` | `jobtitle` |
| `company_domain` | `website` |
| `linkedin_url` | `hs_linkedin_url` |
| `email`, `phone`, `state` | unchanged |

- **Unknown keys pass through to the CRM unchanged.** A stray `Notes` column or a misspelled
  property dead-letters that lead at push time. Show the engineer every non-standard key before
  the live run.
- **Phone-only rows** (valid phone, no email) are stored and dialable but never pushed to a CRM:
  status `stored_no_email`. That is finished, not failed. Send `first_name`/`last_name` and
  `company_name` with them.
- `custom_data` (≤20 keys, `[a-z0-9_]`, values ≤500 chars) stays in GTMOS and is never pushed.

### Attribution: all four or none

`campaign_name`, `campaign_type`, `lead_origin`, `lead_origin_details`. Three of four is refused.

- `campaign_type` is one of `Inbound`, `Targeted List`, `Signal`, `Event`, `ICP Fit`.
- `lead_origin` is **client-facing**: `[Source Type] - [Specific Detail]`, and the Source Type
  must equal `campaign_type`. Good: `Signal - Job Posting`, `Targeted List - PA Title I Schools`.
- **No tool names** (`Clay`, `Apollo`, `ZoomInfo`, `Starbridge`, `PhoneBurner`…) and no bare
  category (`ICP Fit`, `ICP Fit - Prospects`). If you can't write a specific reason, ask.
- `lead_origin_details` is read by whoever works the lead: "Head of IT at a mid-size TX district",
  not "from list".

## 3. Dry run, show, confirm, load

1. Split into chunks of 15. Call `admin_create_leads` with **`dry_run: true`** for each chunk.
   (It defaults to true anyway; say it explicitly.)
2. Show the engineer: client, total rows, the per-status counts summed across chunks, how many
   `would_push`, any pass-through property names, and one sample row.
3. Ask for a go-ahead. Over ~25 leads, always.
4. Re-run with **`dry_run: false`**. The plugin's guard will also ask; that is expected.

`check_dnc` defaults to **true**. Turn it off only for a list that was already scrubbed, and say
so. It only lets a *match* through; a DNC check that errored or had no data still holds the push.

## 4. Read the results honestly

Every response has a top-level **`stored_in_gtmos`** and an `effect` block. Read those before the
statuses.

**Expected. Report it plainly, don't escalate:**

| Status | Meaning |
|---|---|
| `queued`, `subscriptions: 0` | Stored in GTMOS; CRM delivery isn't wired for this client. Normal for most clients. |
| `pending` | Held: no CRM connected or its grant is inactive. Kept intact for a later backfill. |
| `do_not_contact` | Suppressed by DNC. `matched_on: "domain"` means the whole company is blocked. |
| `no_dnc_data` | The **client** has zero DNC sources. The lead **is stored**; only the push is held. Fix is a DNC source (see the `dnc` skill), then replay with `admin_leads_backfill` (dry run first). Never re-send. |
| `created: false` | An idempotent update of someone already known. |
| `duplicate_in_batch` | A later row with the same email (or phone + name) as an earlier one. |

**Real problems:**

- `failed` with a `push_error` naming a property → fix the data; a retry won't help.
- `dnc_check_error` → transient; retry, and say it is **not** a suppression.
- A mix of `subscriptions: 0` and `1+` in one run → the subscription changed mid-run; replay the
  `0` rows with `admin_leads_backfill` (dry run first; one lead: `admin_retry_lead_push`).
- 401/403 on every chunk → credential or deploy, not data.

**The test:** a result identical on every row is a property of the client or the credential, not
of the list. Name the client-level fact before you use the word "issue".

Report in the engineer's terms: how many landed, how many were held and why, how many were
suppressed and on what.
