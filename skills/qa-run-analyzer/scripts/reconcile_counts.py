#!/usr/bin/env python3
"""Deterministic ID/status counter for the run-analyzer's
"counts reconcile" check.

    python3 reconcile_counts.py <ISSUEKEY> [dir]

Reads whichever of <KEY>-test-cases/code-review/api-testing/web-testing
.md exist in dir (default cwd). Prints, per file: the set size of
TC-REQ ids, status counts found in table rows, and the TC ids that are
in the test-cases file but missing from each downstream file. The
analyzer verifies this output instead of recounting by hand — it still
judges WHY a gap exists (routed out, structural, dropped)."""
import os
import re
import sys

TC = re.compile(r"TC-REQ-[\w][\w.]*")
STATUS = re.compile(
    r"\|\s*(PASS|FAIL CONFIRMED|FAIL REJECTED|NOT-TESTABLE|PARTIAL|"
    r"BLOCKED|OBSERVATION|N/A|FAIL|QA)\s*\|")
STAGES = ["test-cases", "code-review", "api-testing", "web-testing"]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    key, d = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else ".")
    ids, base = {}, None
    for stage in STAGES:
        path = os.path.join(d, f"{key}-{stage}.md")
        if not os.path.exists(path):
            print(f"{stage}: file not present")
            continue
        text = open(path, encoding="utf-8").read()
        ids[stage] = set(TC.findall(text))
        counts = {}
        for m in STATUS.findall(text):
            counts[m] = counts.get(m, 0) + 1
        cstr = " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"{stage}: {len(ids[stage])} distinct TC ids · {cstr or 'no status rows'}")
    base = ids.get("test-cases")
    if base:
        for stage in STAGES[1:]:
            if stage in ids:
                miss = sorted(base - ids[stage])
                extra = sorted(ids[stage] - base)
                if miss:
                    print(f"{stage}: MISSING from it: {', '.join(miss)}")
                if extra:
                    print(f"{stage}: ids NOT in test-cases: {', '.join(extra)}")


if __name__ == "__main__":
    main()
