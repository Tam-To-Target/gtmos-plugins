---
name: client-ops-check
description: Superadmin health check of one TTT client's GTMOS wiring — DNC sources and how stale they are, lead-push and meeting webhooks, CRM settings, PhoneBurner seats, and lead push backlog. Use when ops asks "is Acme set up right", "why aren't Globex's leads reaching HubSpot", "check client health before go-live", or before onboarding/offboarding a client. Read-only; it recommends fixes but never applies them.
argument-hint: "[client]"
---

# Client ops check (read-only)

Needs the admin tools (`admin_get_client`, `admin_list_webhooks`, `admin_get_client_settings`).
If they aren't in your tool list, the token isn't a superadmin token. Say so and run only the
parts a GTM-write token can see (`list_dnc_sources`, `lead_stats`).

Run these for the one named client, in parallel where possible:

1. `admin_get_client { client, include: ["dnc", "dnc_sources", "leads", "pb_seats"] }`
2. `admin_list_webhooks { client }`
3. `admin_get_client_settings { client }`
4. `lead_stats { client_id }` and `call_stats { client_id, from: <7 days ago>, to: <today>, group_by: "day" }`

Then report **one table**, one row per check, with a verdict (OK / WATCH / FIX) and the evidence:

| Check | FIX when | WATCH when |
|---|---|---|
| DNC exists | zero sources (nothing suppresses this client) | — |
| DNC freshness | any active source not synced in >14 days while the client dialled this week | 7–14 days |
| DNC health | a source not in `ok` state | — |
| Lead push wiring | client expected to sync to a CRM but no **enabled** `lead.push_requested` subscription | subscription exists but disabled |
| Push backlog | `pending`/`failed` leads growing | any `failed` with a property error |
| Dialer seats | client dials (calls this week) but has no PhoneBurner seat | — |
| Activity | — | zero calls in 7 days for an active client |

Rules:
- `subscriptions: 0` / no lead-push webhook is **normal for most clients**. It's FIX only when the
  client was expected to sync. Ask if you don't know.
- Enabling a webhook is human-gated by design: there is no tool for it. Point at the admin UI.
- Don't run any write tool from this skill. List the fix, name the tool or screen, and stop.
- Dates absolute (`2026-10-08`), never "last week".
