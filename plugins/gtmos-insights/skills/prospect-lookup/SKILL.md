---
name: prospect-lookup
description: Look up everything GTMOS has on one prospect or company — calls, emails, replies, meetings, and whether they're on the do-not-contact list — before a meeting or follow-up. Use for "what's our history with jane@district.org", "brief me on Example ISD before my call", "has anyone talked to this person", "is this contact on our DNC".
argument-hint: "[email or company]"
---

# Prospect lookup

- **One email address:** `cross_channel_digest { email, client_id }` gives calls, emails, replies and
  meetings in one call. Add `lookup_contact { email }` for the contact record.
- **A company:** `list_calls { client_id, q: "<company>" }` and
  `list_meetings { client_id, q: "<company>" }`.
- **Do-not-contact:** `dnc_check { client_id, email }`. Report `contactable: false` with its
  reason, and treat `null` as **unknown, not clear**.

Brief in this order: who they are (role, company), every touch with its date and channel, what
they said (quote the reply or call summary), any meeting and its outcome, then DNC status. If GTMOS
has nothing, say so plainly. Don't fill gaps from general knowledge.
