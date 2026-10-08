---
name: performance-report
description: Build a weekly or monthly outbound performance report from GTMOS — calls, connects, meetings booked, email campaign results and replies — for your company's program. Use for "how did outbound do last week", "monthly report for our SDR program", "how many meetings did we book in September", "which email campaign is working".
argument-hint: "[from] [to]"
---

# Outbound performance report

If you can see more than one client (`list_clients`), ask which one. Otherwise use the one you have.
Turn "last week" or "September" into absolute UTC dates (`from` inclusive, `to` exclusive) and
print them at the top of the report.

Pull, in parallel:
- `call_stats { client_id, from, to, group_by: "day" }` and `group_by: "sdr"`: dials, connects.
- `list_meetings { client_id, booked_from: from, booked_to: to }`: meetings booked (page with
  `cursor`), plus `attended` / `outcome` where filled in.
- `email_campaign_performance { client_id }`: lifetime rates per campaign.
- `list_replies { client_id, from, to }`: real replies (auto-replies excluded by default).
- `campaign_attribution { client_id, from, to }`: meetings per campaign across channels.

Report as:
1. **Headline**: meetings booked, connects, connect rate, replies. Compare with the previous
   window of the same length if you have it (one more `call_stats` call).
2. **Calling**: by day and by SDR, best and worst day.
3. **Email**: campaigns ranked by reply rate. Flag any campaign with sends but zero replies.
4. **Meetings**: list with date, company and campaign. Note no-shows if `attended` is set.
5. **Three observations** the numbers support, each with the figure behind it.

Use the aggregate tools for totals. Never page through raw calls just to count them. If a number is
missing because the data isn't there, say which one rather than estimating.
