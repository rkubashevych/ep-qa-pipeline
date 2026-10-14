#!/usr/bin/env python3
"""qs_watch.py — what changed in QA Service since we last looked.

    python3 qs_watch.py due                    # exit 0 = a check is due (>= 7 days or never), 1 = not due
    python3 qs_watch.py diff <NEW.json> [--plugin-root DIR] [--write]
    python3 qs_watch.py show                   # the last snapshot's date and counts
    python3 qs_watch.py --selftest

QA Service publishes no changelog. What it does publish is a description
of itself, cheap to read: its MCP tool names, its method skills with a
content digest (list_skills), the agent-backed actions with their MCP
status and the skill / agent / rule digests they run on
(list_agent_actions), and its manual pages (list_help_topics). The
qa-service-watch skill collects those into NEW.json; this script keeps
the dated snapshots and says what was added, removed or changed since
the last one. With --plugin-root it also names the plugin files that
mention each changed item, which is the first triage signal: a changed
skill the plugin mirrors needs our copy refreshed; a new tool nobody
mentions is a candidate to integrate.

NEW.json shape (every key optional, missing = not collected):

    {"takenAt": "2026-10-14T11:00:00Z",
     "tools":      ["start_generate_test_cases", "..."],
     "skills":     {"test-planning-and-design": "19d88114a5dd"},
     "agents":     {"bitbucket-test-implementer": "dcc4b9502809"},
     "rules":      {"tags": "398d8ef2a1b6"},
     "actions":    {"implement_tests": {"mcp": "available", "tool": "start_implement_tests"}},
     "helpTopics": {"dev-requests": "dev-requests — asking developers ..."}}

State lives in $EP_QA_HOME/qa-service-watch/ (default ~/.ep-qa):
snapshot-<YYYY-MM-DD>.json per check, state.json with the last check.
`diff --write` stores NEW as today's snapshot and moves the clock; a
plain `diff` only reads. Stdlib only.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile

DUE_DAYS = 7
CATEGORIES = ("tools", "skills", "agents", "rules", "actions", "helpTopics")


def home():
    h = os.environ.get("EP_QA_HOME") or os.path.join(os.path.expanduser("~"), ".ep-qa")
    return os.path.join(h, "qa-service-watch")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def state(d):
    p = os.path.join(d, "state.json")
    return load(p) if os.path.exists(p) else {}


def last_snapshot(d):
    if not os.path.isdir(d):
        return None, None
    snaps = sorted(f for f in os.listdir(d) if f.startswith("snapshot-") and f.endswith(".json"))
    if not snaps:
        return None, None
    return snaps[-1], load(os.path.join(d, snaps[-1]))


def as_map(cat, value):
    """Every category as {key: comparable value}."""
    if value is None:
        return None
    if cat == "tools":
        return {t: True for t in value}
    if cat == "actions":
        return {k: json.dumps(v, sort_keys=True) for k, v in value.items()}
    return dict(value)


def diff(old, new):
    out = {}
    for cat in CATEGORIES:
        o, n = as_map(cat, (old or {}).get(cat)), as_map(cat, new.get(cat))
        if n is None:
            continue  # not collected this time: say nothing rather than report it all removed
        if o is None:
            out[cat] = {"added": sorted(n), "removed": [], "changed": [], "baseline": True}
            continue
        out[cat] = {
            "added": sorted(set(n) - set(o)),
            "removed": sorted(set(o) - set(n)),
            "changed": sorted(k for k in set(n) & set(o) if n[k] != o[k]),
        }
    return out


def mentions(root, key):
    """Plugin files that mention `key` (skills/, README) — grep, stdlib fallback."""
    hits = []
    for base in ("skills", "README.md"):
        p = os.path.join(root, base)
        if os.path.isfile(p):
            files = [p]
        else:
            files = [os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs
                     if f.endswith((".md", ".py"))] if os.path.isdir(p) else []
        for f in files:
            try:
                with open(f, encoding="utf-8") as fh:
                    if key in fh.read():
                        hits.append(os.path.relpath(f, root).replace(os.sep, "/"))
            except (OSError, UnicodeDecodeError):
                pass
    return sorted(set(hits))


def render(d, root=None, old_name=None):
    lines = [f"Compared with: {old_name or 'nothing (first check: everything is baseline)'}"]
    total = 0
    for cat, r in d.items():
        n = len(r["added"]) + len(r["removed"]) + len(r["changed"])
        if r.get("baseline"):
            lines.append(f"{cat}: baseline, {len(r['added'])} items recorded")
            continue
        total += n
        if not n:
            lines.append(f"{cat}: no change")
            continue
        lines.append(f"{cat}:")
        for kind in ("added", "removed", "changed"):
            for k in r[kind]:
                where = ""
                if root:
                    m = mentions(root, k)
                    where = f"  [plugin: {', '.join(m)}]" if m else "  [plugin: not mentioned]"
                lines.append(f"  {kind:7} {k}{where}")
    lines.append(f"Total changes: {total}")
    return "\n".join(lines)


def cmd_due():
    s = state(home())
    last = s.get("lastCheck")
    if not last:
        print("due: never checked")
        return 0
    days = (dt.date.today() - dt.date.fromisoformat(last)).days
    if days >= DUE_DAYS:
        print(f"due: last check {last} ({days} days ago)")
        return 0
    print(f"not due: last check {last} ({days} days ago, next on day {DUE_DAYS})")
    return 1


def cmd_diff(args):
    new_path = args[0]
    root = None
    if "--plugin-root" in args:
        root = args[args.index("--plugin-root") + 1]
    new = load(new_path)
    d = home()
    old_name, old = last_snapshot(d)
    result = diff(old, new)
    print(render(result, root, old_name))
    if "--write" in args:
        os.makedirs(d, exist_ok=True)
        today = dt.date.today().isoformat()
        with open(os.path.join(d, f"snapshot-{today}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(new, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        with open(os.path.join(d, "state.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"lastCheck": today, "comparedWith": old_name}, f, indent=2)
            f.write("\n")
        print(f"Stored snapshot-{today}.json; next check due in {DUE_DAYS} days.")
    return 0


def cmd_show():
    name, snap = last_snapshot(home())
    if not name:
        print("no snapshot yet")
        return 1
    counts = {c: len(snap.get(c) or {}) for c in CATEGORIES}
    print(name, json.dumps(counts))
    return 0


def selftest():
    old = {"tools": ["a", "b"], "skills": {"s1": "d1", "s2": "d2"}, "actions": {"x": {"mcp": "planned"}}}
    new = {"tools": ["a", "c"], "skills": {"s1": "d1", "s2": "d9"}, "actions": {"x": {"mcp": "available"}}}
    r = diff(old, new)
    assert r["tools"] == {"added": ["c"], "removed": ["b"], "changed": []}, r["tools"]
    assert r["skills"]["changed"] == ["s2"] and not r["skills"]["added"], r["skills"]
    assert r["actions"]["changed"] == ["x"], r["actions"]
    assert "agents" not in r, "a category not collected must not be reported"
    first = diff(None, new)
    assert first["skills"].get("baseline") and first["skills"]["added"] == ["s1", "s2"], first
    with tempfile.TemporaryDirectory() as t:
        os.environ["EP_QA_HOME"] = t
        p = os.path.join(t, "new.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(new, f)
        assert cmd_due() == 0, "never checked must be due"
        with open(os.devnull, "w") as dn:
            saved = sys.stdout
            sys.stdout = dn
            try:
                cmd_diff([p, "--write"])
            finally:
                sys.stdout = saved
        assert cmd_due() == 1, "just checked must not be due"
        assert last_snapshot(home())[0].startswith("snapshot-")
    print("SELFTEST PASS")
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "due":
        return cmd_due()
    if argv[0] == "diff" and len(argv) >= 2:
        return cmd_diff(argv[1:])
    if argv[0] == "show":
        return cmd_show()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
