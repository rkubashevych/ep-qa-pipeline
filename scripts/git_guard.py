#!/usr/bin/env python3
"""PreToolUse hook (hooks/hooks.json, matcher Bash): refuse the two git
commands CLAUDE.md forbids — `git add -A` / `--all` / `git add .` and
`git add` with a wildcard pathspec. The working tree may hold legacy
live-credential run artefacts; staging by explicit path is the rule.

Reads the hook payload on stdin, exits 2 (block) with the reason on
stderr when the command matches, 0 otherwise. Never blocks on its own
failure: unreadable payload → exit 0."""
import json
import re
import sys

DENY = re.compile(
    r"\bgit\b[^|;&\n]*?\badd\b[^|;&\n]*?"
    r"(?:\s-[a-zA-Z]*A[a-zA-Z]*(?=\s|$)|\s--all(?=\s|$)|\s\.(?=\s|$)|\s\*|\s[^\s]*\*)",
)

def main() -> int:
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command", "") or ""
    except Exception:
        return 0
    if DENY.search(command):
        sys.stderr.write(
            "git_guard: refused — `git add -A` / `git add .` / wildcard "
            "pathspecs are forbidden in this repo (CLAUDE.md hard rules). "
            "Stage explicit paths: `git add <file> <file>`.\n"
        )
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
