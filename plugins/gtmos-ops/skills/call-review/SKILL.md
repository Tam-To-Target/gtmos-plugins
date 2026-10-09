---
name: call-review
description: Review a TTT client's cold calls from GTMOS — pull a window of connected calls, read their transcripts in batches, and summarize objections, what worked, SDR coaching points and meeting conversion. Use for "review last week's calls for Acme", "what objections are SDRs hearing on Globex", "coach Jordan on his connects", "why did connect-to-meeting drop". Batches every fetch; delegates large pulls to the gtmos-analyst agent.
argument-hint: "[client] [from] [to]"
---

# Call review

Pick absolute dates first and state them (UTC, `from` inclusive, `to` exclusive).

1. **Shape the window with aggregates, not rows.** `call_stats { client_id, from, to, group_by: "sdr" }`
   (and `"day"`) for volume and connects; `list_meetings { client_id, booked_from, booked_to }` for
   outcomes. Report connect rate and meetings per connect before reading a single transcript.
2. **Pick the calls.** `list_calls { client_id, from, to, connected: true, has_transcript: true, limit: 100 }`,
   paging with `cursor`. For a coaching question, filter `sdr_id`.
3. **Read them in batches.** `get_transcripts { ids }` (≤25 per call) or `get_calls { ids }` (≤200,
   summary + sentiment without the full text). **Never** one `get_call` per row.
4. **Find a phrase across many calls** with `search_transcripts { q, client_id }` instead of reading
   everything ("\"budget\"", "\"already use\"").

More than ~50 transcripts → hand steps 2–3 to the `gtmos-analyst` agent with the client, dates and
question, and work from its summary so the raw text stays out of this conversation.

Report:
- The numbers (calls, connects, connect rate, meetings, by SDR).
- Top 3–5 objections with **how often** and one short quote each (call id + date).
- What the best calls did differently, as concrete lines an SDR can reuse.
- Per-SDR coaching points only when asked about a rep, each tied to a call id.

Speaker labels on calls imported before 2026-09-01 can be inferred rather than recorded. Hedge any
"the SDR said" claim on those. Recording links older than ~5 months may 404.
