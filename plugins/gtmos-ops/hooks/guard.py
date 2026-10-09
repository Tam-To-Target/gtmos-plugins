#!/usr/bin/env python3
"""PreToolUse guard for gtmos-ops: bulk and destructive GTMOS writes ask first.

Reads the hook payload on stdin. For a tool in guard-table.json's "guard" list,
prints a PreToolUse "ask" decision naming the client and the row count — unless
the call is an explicit dry run (dry_run: true), which writes nothing. Anything
else gets no output, so the normal permission flow applies.

Never blocks on its own failure: a bad payload exits 0 silently, because a
broken guard must not take the team's tools down with it.
"""
import json
import os
import sys

PREFIX = "mcp__plugin_gtmos-ops_gtmos__"


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    tool = event.get("tool_name") or ""
    if not tool.startswith(PREFIX):
        return 0
    op = tool[len(PREFIX):]
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard-table.json")) as fh:
            guarded = set(json.load(fh)["guard"])
    except Exception:
        return 0
    if op not in guarded:
        return 0

    args = event.get("tool_input") or {}
    if args.get("dry_run") is True:
        return 0  # a preview writes nothing

    client = args.get("client_id") or args.get("client") or "(no client_id given)"
    counts = [f"{len(v)} {k}" for k, v in args.items() if isinstance(v, list) and v]
    dry = "dry_run omitted (check this tool's default)" if "dry_run" not in args else f"dry_run={args['dry_run']}"
    reason = (
        f"GTMOS write: {op} on client {client}"
        + (f", {', '.join(counts)}" if counts else "")
        + f", {dry}. This changes live customer data. Run with dry_run: true first if you have not."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
