# GTMOS plugins

Plugins for [GTMOS](https://gtmos.tamtotarget.com), Tam To Target's go-to-market operating system.

| Plugin | What it does |
|---|---|
| [`gtmos-insights`](plugins/gtmos-insights) | Read-only access to your outbound program: calls, transcripts, meetings booked, email campaigns and replies. |

## Claude Code

```
/plugin install gtmos-insights --marketplace Tam-To-Target/gtmos-plugins
```

Older Claude Code versions take two steps:

```
/plugin marketplace add Tam-To-Target/gtmos-plugins
/plugin install gtmos-insights@gtmos-plugins
```

Then run `/mcp`, pick **gtmos**, and sign in with your GTMOS account.

## Other assistants

The same read-only server works in any MCP client that supports OAuth:

```
https://gtmos.tamtotarget.com/api/mcp/readonly
```

Step-by-step instructions for Claude Desktop, ChatGPT and Codex are in GTMOS under
**Settings → API tokens → Connect an AI assistant**.

## Security

This repository holds no credentials. You sign in to GTMOS yourself, and you only ever see the
accounts your GTMOS login can already see. The server refuses every write.
