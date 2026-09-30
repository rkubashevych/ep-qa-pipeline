#!/usr/bin/env python3
"""plan_hash.py — what the user approved is what gets written.

    python3 plan_hash.py make  <PLAN.json>   # at the preview: freeze + print the hash
    python3 plan_hash.py show  <PLAN.json>   # render the preview FROM the file
    python3 plan_hash.py check <PLAN.json>   # after the yes, before the first write
    python3 plan_hash.py --selftest

A plan is the exact list of outward writes one confirmation covers:

    {"step": "qa-pipeline-code step 6 (a)+(b)", "ticket": "EP-1234",
     "writes": [{"tool": "create_test_run", "args": {...}},
                {"tool": "addCommentToJiraIssue", "args": {"issueKey": "EP-1235",
                                                           "commentBody": "..."}}]}

`make` writes <PLAN>.approved.json (a frozen copy) and <PLAN>.sha256.
`check` recomputes the hash of <PLAN.json> as it is now; on a mismatch it
names the writes that differ from the approved copy and exits 1 — stop,
show the difference, ask again. Protocol and where it applies:
skills/qa-pipeline/references/write-plans.md.

Why (0.47.0): a chat "yes" was the only record of what was approved, and
the 40-90 calls that followed were composed afresh — after a late
"improvement", a second look at a case, or a context compaction mid-
publish, what landed could differ from what was shown and nothing would
notice. Borrowed from qa-service's implement consent token
(lib/server/mcp/consent.ts: a hash over the canonical plan, re-checked at
apply time). Stdlib only.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile


def canonical(plan):
    return json.dumps(plan, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(plan):
    return hashlib.sha256(canonical(plan).encode("utf-8")).hexdigest()


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        plan = json.load(f)
    if not isinstance(plan, dict) or not isinstance(plan.get("writes"), list) or not plan["writes"]:
        raise ValueError("a plan is an object with a non-empty `writes` list")
    for i, w in enumerate(plan["writes"], 1):
        if not isinstance(w, dict) or not isinstance(w.get("tool"), str) or not isinstance(w.get("args"), dict):
            raise ValueError(f"write #{i}: needs `tool` (string) and `args` (object)")
    return plan


def paths(path):
    base = path[:-5] if path.endswith(".json") else path
    return base + ".approved.json", base + ".sha256"


def summary(plan):
    counts = {}
    for w in plan["writes"]:
        counts[w["tool"]] = counts.get(w["tool"], 0) + 1
    return " · ".join(f"{n}× {t}" for t, n in counts.items())


def cmd_make(path):
    plan = load(path)
    approved, sha_path = paths(path)
    h = digest(plan)
    shutil.copyfile(path, approved)
    with open(sha_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(h + "\n")
    print(f"plan {os.path.basename(path)}: {len(plan['writes'])} write(s) — {summary(plan)}")
    print(f"sha256 {h[:12]}  (show this in the preview; `check` must print the same before any write)")
    return 0


LONG_KEYS = ("commentBody", "body", "description", "note", "summary", "markdown", "content")


def cmd_show(path):
    plan = load(path)
    print(f"# {plan.get('step', 'plan')} — {plan.get('ticket', '')}".rstrip(" —"))
    for i, w in enumerate(plan["writes"], 1):
        short = {k: v for k, v in w["args"].items()
                 if not (k in LONG_KEYS and isinstance(v, str) and len(v) > 120)}
        print(f"#{i} {w['tool']} {json.dumps(short, ensure_ascii=False)}")
        for k in LONG_KEYS:
            v = w["args"].get(k)
            if isinstance(v, str) and len(v) > 120:
                print(f"   {k}:")
                for line in v.splitlines():
                    print(f"   | {line}")
    return 0


def cmd_check(path):
    approved, sha_path = paths(path)
    if not os.path.exists(sha_path) or not os.path.exists(approved):
        print(f"check: no approved copy for {os.path.basename(path)} — run `make` at the preview first")
        return 2
    want = open(sha_path, encoding="utf-8").read().strip()
    plan = load(path)
    got = digest(plan)
    if got == want:
        print(f"check: OK — sha256 {got[:12]} matches the approved preview ({len(plan['writes'])} write(s))")
        return 0
    old = load(approved)["writes"]
    new = plan["writes"]
    diffs = []
    for i in range(max(len(old), len(new))):
        a = old[i] if i < len(old) else None
        b = new[i] if i < len(new) else None
        if a is None:
            diffs.append(f"#{i + 1} ADDED   {b['tool']}")
        elif b is None:
            diffs.append(f"#{i + 1} REMOVED {a['tool']}")
        elif canonical(a) != canonical(b):
            keys = sorted(k for k in set(a["args"]) | set(b["args"])
                          if a["args"].get(k) != b["args"].get(k))
            what = "tool" if a["tool"] != b["tool"] else ", ".join(keys)
            diffs.append(f"#{i + 1} CHANGED {b['tool']} ({what})")
    if canonical({k: v for k, v in plan.items() if k != "writes"}) != \
            canonical({k: v for k, v in load(approved).items() if k != "writes"}):
        diffs.append("plan header changed")
    print(f"check: CHANGED since the approved preview (approved {want[:12]}, now {got[:12]}) — "
          f"do NOT write; show this and ask again:")
    for d in diffs:
        print("  " + d)
    return 1


def selftest():
    errs = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "EP-1-step6-plan.json")
        plan = {"step": "t", "ticket": "EP-1", "writes": [
            {"tool": "create_test_run", "args": {"caseIds": ["a", "b"], "env": "alpha2"}},
            {"tool": "addCommentToJiraIssue", "args": {"issueKey": "EP-2", "commentBody": "x" * 200}}]}
        json.dump(plan, open(p, "w", encoding="utf-8"))
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            if cmd_make(p) != 0 or cmd_check(p) != 0:
                errs.append("make → check on an untouched plan did not pass")
            # key order and whitespace are not changes
            json.dump(json.loads(open(p).read()), open(p, "w", encoding="utf-8"), indent=4, sort_keys=True)
            if cmd_check(p) != 0:
                errs.append("re-serialising the same plan counted as a change")
            plan["writes"][1]["args"]["commentBody"] = "y" * 200
            plan["writes"].append({"tool": "record_case_result", "args": {"verdict": "pass"}})
            json.dump(plan, open(p, "w", encoding="utf-8"))
            buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_check(p)
        out = buf.getvalue()
        if rc != 1 or "#2 CHANGED addCommentToJiraIssue (commentBody)" not in out or "#3 ADDED" not in out:
            errs.append(f"a changed plan was not caught precisely:\n{out}")
        try:
            json.dump({"writes": []}, open(p, "w", encoding="utf-8"))
            load(p)
            errs.append("an empty plan was accepted")
        except ValueError:
            pass
    if errs:
        print("SELFTEST FAIL")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("SELFTEST PASS — make/check, reserialisation, changed + added writes, empty plan refused")


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if argv[:1] == ["--selftest"]:
        selftest()
        return 0
    if len(argv) != 2 or argv[0] not in ("make", "show", "check"):
        print(__doc__)
        return 2
    try:
        return {"make": cmd_make, "show": cmd_show, "check": cmd_check}[argv[0]](argv[1])
    except (ValueError, json.JSONDecodeError, OSError) as e:
        print(f"{argv[0]}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
