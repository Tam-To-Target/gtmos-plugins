---
name: call-insights
description: Find what prospects are saying on your cold calls — top objections, competitor mentions, buying signals, and the talk tracks that lead to meetings — from GTMOS call transcripts. Use for "what objections are we hearing", "who mentioned a competitor", "what are prospects saying about pricing", "find calls where they asked for a demo".
argument-hint: "[topic or phrase]"
---

# Call insights

1. Fix the client and an absolute date window first (default: the last 30 days), and say both.
2. For a **topic or phrase**, start with `search_transcripts { q, client_id }`. Quote exact
   phrases (`"already use"`, `"budget"`, `"send me an email"`). Run several related searches
   rather than reading everything.
3. For **themes across calls**, list connected calls with transcripts:
   `list_calls { client_id, from, to, connected: true, has_transcript: true, limit: 100 }`, then
   read them in batches with `get_transcripts { ids }` (up to 25 at a time). Never fetch one
   call at a time.
4. Tie themes to outcomes: `list_meetings { client_id, booked_from, booked_to }` shows which
   conversations turned into meetings.

Report:
- Each theme with **how many calls** mention it, out of how many you read.
- One or two short quotes per theme, each with the call date.
- What the calls that booked meetings did differently, as concrete phrasing.
- What you didn't read (e.g. "120 of 340 connected calls"), so the sample size is clear.

Don't name or quote the prospect's personal details beyond company and role in a summary meant to
be shared.
