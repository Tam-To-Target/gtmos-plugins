# GTMOS Ops (internal)

Tam To Target's internal GTMOS plugin. One MCP server (`/api/mcp/ops`) whose tool list follows
your token:

| Token | You get |
|---|---|
| Superadmin (`sdr-launch.admin`) | Every tool: reads, data-plane writes, client config, webhooks, retention |
| GTM-write (GTM engineers) | Reads + leads, accounts, campaigns, DNC writes, for your Airtable-assigned clients only |
| Read | Reads only |

Scoping is enforced by GTMOS on every call. The plugin can't widen it.

## Install

```
/plugin install gtmos-ops --marketplace Tam-To-Target/gtmos-plugins
```

The install dialog asks for your **GTMOS API token** (GTMOS → Settings → API tokens). It's
stored in your OS keychain. Change it later with `/plugin configure gtmos-ops@gtmos-plugins`.

## What's inside

| Piece | What it does |
|---|---|
| `gtmos` MCP server | `/api/mcp/ops`, authenticated with your token |
| `gtmos-client` skill | Answers any question about a client's calls, emails, replies, meetings, leads, DNC |
| `load-leads` skill | Dial lists as one job (`admin_import_dial_list`: preview → approve → result), saved per-client profiles |
| `dnc` skill | Batch DNC checks (1,000/call), source audit, add/import/remove |
| `call-review` skill | Objections, coaching points and conversion from transcripts |
| `client-ops-check` skill | Superadmin health check of one client's wiring (read-only) |
| `gtmos-analyst` agent | Read-only subagent for big pulls, so raw rows stay out of your context |
| Write guard hook | Bulk and destructive writes ask you first unless they're an explicit `dry_run: true` |

The write guard reads `hooks/guard-table.json`. A GTMOS test fails when a new write tool ships
without a row there.

## Requirements

`python3` on PATH (for the guard hook).

## Releasing a change

The manifest pins `version`, so installed copies only update when it changes. **Bump
`.claude-plugin/plugin.json`'s `version` in the same PR as any change under `plugins/gtmos-ops/`**,
or `claude plugin update` will report "already at the latest version" and keep the old skills.

| Version | Date | Change |
|---|---|---|
| 1.0.3 | 2026-10-09 | `load-leads`: lists go through `admin_import_dial_list` (doc 81) — one job, profiles, extensions, enrollment |
| 1.0.2 | 2026-10-09 | Published in the public `Tam-To-Target/gtmos-plugins` marketplace (no GitHub login needed); example client names made generic |
| 1.0.1 | 2026-10-08 | `load-leads`: 15 leads per call (the 50 cap was reverted), real-write timing |
| 1.0.0 | 2026-10-08 | First release |
