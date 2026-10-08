# GTMOS Insights (read-only)

Ask Claude about your outbound program: calls, transcripts, meetings, email campaigns and replies.
Everything is read-only, and you see exactly the accounts your GTMOS login can see.

## Install (Claude Code)

```
/plugin install gtmos-insights --marketplace Tam-To-Target/gtmos-plugins
```

Then run `/mcp`, pick **gtmos**, and sign in with your GTMOS account. No token to copy.

## Try

- `/gtmos-insights:performance-report last month`
- `/gtmos-insights:call-insights "pricing"`
- `/gtmos-insights:prospect-lookup jane@example.org`

The server behind this plugin (`https://gtmos.tamtotarget.com/api/mcp/readonly`) exposes no tool
that can change data, whatever account signs in.
