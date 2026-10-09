---
name: gtmos-client
description: Answer any question about a TTT client's outbound data — email campaigns, replies and what prospects said, sends, leads and their custom variables, calls, call transcripts, meetings booked, DNC — through the GTMOS MCP server instead of querying Neon/Postgres databases. Use whenever a GTM engineer works a client ("how is Acme's campaign doing", "pull this week's interested replies for Globex", "what did prospects say about pricing on calls", "show me Jane's email history", "meetings booked last week", "is this list safe to load", "/client-{name}") or whenever an older skill tells you to run SQL against client_data, phoneburner_*, emailbison-gtm-master or a per-client Neon project. Replaces the database sections of every per-client /client-{name} skill; GitLab, Slack and ClickUp stay in those skills.
---

# GTMOS client data

All client campaign, call, meeting, lead and DNC data comes from **GTMOS**, through this plugin's
`gtmos` MCP server (`/api/mcp/ops`). **Never** connect to a Neon/Postgres database for this data,
and never ask the engineer for a DSN. If the `gtmos` tools aren't available, run `/mcp`: a failed
server means the token in `/plugin configure gtmos-ops@gtmos-plugins` is missing, expired or revoked.

The tool list is already filtered to what the engineer's token can call. A write tool that isn't
there is a scope problem (read-only token), not a missing feature. Say so and point them at
GTMOS → Settings → API tokens.

The server only shows the clients the engineer is assigned to in Airtable. That is enforced
server-side; you don't need to filter, and you cannot see past it.

## 1. Pin down the client first

- Every call takes `client_id`: use the client's **GTMOS slug** (e.g. `acme`,
  `globex`, `initech-learning`). If unsure, call `list_clients` and match by name.
- **State the client explicitly on every call.** Never carry a client over from earlier in the
  conversation without saying so, and never guess.
- An **empty result** usually means the wrong slug or a client not assigned to this engineer.
  Check that before concluding "there's no data".
- If the session uses a **pinned token**, tools have no `client_id` (or it must equal the pin).
  The pin decides the client; don't try to work around it.

## 2. Pick the tool by the question

| Question | Tool |
|---|---|
| Campaign list / one campaign's stats, schedule, senders | `list_email_campaigns`, `get_email_campaign` |
| Campaign performance (lifetime rates) | `email_campaign_performance` |
| Sequence copy | `get_email_campaign_sequence` |
| Sends in a window | `list_email_campaign_sends { from, to }` |
| **Real replies** (auto-replies excluded) | `list_replies { from, to }` |
| **What prospects said** | `list_replies { include_body: true, limit: 25 }` |
| One lead: custom variables + email history | `lead_engagement { email }` (+ `list_replies { lead_id, include_body: true }` for text) |
| Everything about one email address | `cross_channel_digest { email }` |
| Human (HotHawk) emails | `list_emails`, `get_email` |
| Calls / call volume by SDR or day | `list_calls`, `call_stats { from, to, group_by }` |
| A call and its transcript | `get_call { id, include_transcript: true }` — **several calls: `get_calls { ids }` (≤200)** |
| Phrase across calls | `search_transcripts { q }` (quote phrases; max 50 hits) |
| Several transcripts | `get_transcripts { ids }` (≤25) |
| Meetings booked | `list_meetings { booked_from, booked_to }` |
| Best dialing hours | `local_hour_report` |
| Leads in GTMOS | `list_leads`, `get_lead`, `lead_stats` |
| Cross-channel campaign results | `campaign_attribution { from, to }` |
| DNC status | `dnc_check_batch` (≤1,000/call); `dnc_check` only for a single record |

Loading leads → use the `load-leads` skill. Checking, adding or importing DNC → use the `dnc` skill.
A multi-call data pull (a month of calls, every transcript for a campaign) → delegate to the
`gtmos-analyst` agent so the raw rows stay out of this conversation.

## 3. Rules

- **Paginate honestly.** List tools return `next_cursor`; keep calling with `cursor` until it's
  `null` before reporting totals. Better still, use the stats tool that computes the total.
- **Prefer aggregate tools** (`call_stats`, `email_campaign_performance`, `lead_stats`,
  `campaign_attribution`) over paging raw rows to count them yourself.
- **Batch, don't loop.** `dnc_check_batch` over per-row `dnc_check`; `get_calls` / `get_transcripts`
  over per-id calls.
- **Writes:** run bulk tools with `dry_run: true` first, show the engineer the counts and a
  sample, and only then run live. Confirm anything over ~25 records, any merge, any DNC import.
- **Missing campaign?** GTMOS ingests only EmailBison campaigns the GTM director has approved. Say the
  campaign isn't approved; don't look for another source.
- **Dates:** UTC ISO-8601, `from` inclusive, `to` exclusive. Convert "last week" to absolute
  dates and say which dates you used.
- **Can't answer it?** Say exactly what you needed and which tool fell short, so the engineer can
  log it. Don't fall back to SQL or a database.
