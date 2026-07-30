#!/usr/bin/env python3
"""Deterministic ID/status counter for the run-analyzer's
"counts reconcile" check.

    python3 reconcile_counts.py <ISSUEKEY> [dir]
    python3 reconcile_counts.py --selftest

Reads whichever of <KEY>-test-cases/code-review/api-testing/web-testing
.md exist in dir (default cwd). Prints, per file: the set size of case
ids, status counts from RESULT ROWS ONLY, and the TC ids that are in
the test-cases file but missing from each downstream file. The analyzer
verifies this output instead of recounting by hand — it still judges
WHY a gap exists (routed out, structural, dropped).

Counting rules (each fixes a real defect from the EP-53978 run report /
PIPELINE-REVIEW-2026-07-30.md):
- A status is counted only on a table row whose FIRST cell is a case id
  (TC-REQ-* or RISK-*). Statistics/summary tables (`| PASS | 32 |`)
  are therefore never counted.
- One status per row: the LAST cell that exactly matches the status
  vocabulary. `PASS(code)` / `PASS (code)` is a SOURCE marker, not a
  row status — it is tallied separately and never counted as PASS.
- Ids are digits-and-dots only: `TC-REQ-7.2.` at a sentence end yields
  `TC-REQ-7.2`, never a phantom `7.2.` id.
- Bold statuses (`**FAIL CONFIRMED**`) and qualified statuses
  (`NOT-TESTABLE (instrumentation)`, `BLOCKED (unverified)`) count.
- Range rows (`TC-REQ-29.1–29.3`) expand to every id in the range.

Run `--selftest` before trusting the output on a new pipeline version.
"""
import os
import re
import sys

CASE_ID = re.compile(r"(?:TC-REQ-\d+(?:\.\d+)*|RISK-[A-Z]+-\d+)")
# TC-REQ-29.1–29.3 / TC-REQ-29.1-29.3 / TC-REQ-29.1–TC-REQ-29.3
ID_RANGE = re.compile(
    r"TC-REQ-(\d+)\.(\d+)\s*[–—-]\s*(?:TC-REQ-)?(?:(\d+)\.)?(\d+)")
# Longest alternatives first so FAIL CONFIRMED never half-matches as FAIL.
STATUSES = (
    "FAIL CONFIRMED", "FAIL REJECTED", "NOT-TESTABLE", "NOT EXECUTED",
    "SPEC-DEFECT", "OBSERVATION", "RE-ROUTE", "PARTIAL", "BLOCKED",
    "SKIPPED", "PASS", "FAIL", "QA", "N/A",
)
STATUS_CELL = re.compile(
    r"(" + "|".join(re.escape(s) for s in STATUSES) +
    r")(?:\s*\(([^)]*)\))?(?:\s*\[([^\]]+)\])?$")
STAGES = ["test-cases", "code-review", "api-testing", "web-testing"]


def norm_cell(cell):
    """Strip whitespace and markdown bold/italic markers."""
    return cell.strip().strip("*").strip()


def cell_status(cell):
    """Return the canonical status token for a cell, or None.

    `PASS(code)` is returned as the distinct token 'PASS(code)' so the
    caller can treat it as a source marker rather than a verdict.
    Qualified NOT-TESTABLE/BLOCKED keep their qualifier.
    """
    m = STATUS_CELL.fullmatch(norm_cell(cell))
    if not m:
        return None
    status, qual, chan = m.group(1), (m.group(2) or "").strip(), \
        (m.group(3) or "").strip()
    if chan and status != "RE-ROUTE":
        return None  # a channel suffix is only legal on RE-ROUTE
    if status == "PASS" and qual.lower() == "code":
        return "PASS(code)"
    if qual and status in ("NOT-TESTABLE", "BLOCKED"):
        return f"{status} ({qual})"
    if status == "RE-ROUTE":
        return f"RE-ROUTE [{chan}]" if chan else "RE-ROUTE"
    return status


def collect_ids(text):
    """All case ids in the text, with TC ranges expanded."""
    ids = set(CASE_ID.findall(text))
    for maj, lo, maj2, hi in ID_RANGE.findall(text):
        if maj2 and maj2 != maj:
            continue  # cross-major range: don't guess
        lo_i, hi_i = int(lo), int(hi)
        if lo_i < hi_i <= lo_i + 50:
            for n in range(lo_i, hi_i + 1):
                ids.add(f"TC-REQ-{maj}.{n}")
    return ids


def count_statuses(text):
    """(status_counts, source_counts) from result rows only."""
    counts, sources = {}, {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c for c in line.split("|")][1:-1]
        if not cells or not CASE_ID.match(norm_cell(cells[0])):
            continue
        tokens = [t for t in (cell_status(c) for c in cells[1:]) if t]
        real = [t for t in tokens if t != "PASS(code)"]
        if "PASS(code)" in tokens:
            sources["PASS(code)"] = sources.get("PASS(code)", 0) + 1
        if real:
            status = real[-1]  # the status column is the last verdict cell
            counts[status] = counts.get(status, 0) + 1
    return counts, sources


def report(key, d):
    ids = {}
    for stage in STAGES:
        path = os.path.join(d, f"{key}-{stage}.md")
        if not os.path.exists(path):
            print(f"{stage}: file not present")
            continue
        text = open(path, encoding="utf-8").read()
        ids[stage] = collect_ids(text)
        counts, sources = count_statuses(text)
        cstr = " · ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        sstr = "".join(f" · source {k}={v}" for k, v in sorted(sources.items()))
        print(f"{stage}: {len(ids[stage])} distinct case ids · "
              f"{cstr or 'no status rows'}{sstr}")
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


SELFTEST_DOC = """
## Results

| TC | Name | Source | Status | Call | Evidence |
|----|------|--------|--------|------|----------|
| TC-REQ-1.4 | Non-GDPR event | PASS(code) | NOT EXECUTED | — | no env |
| TC-REQ-6.1 | Re-opt-in | PASS(code) | PASS | POST /x | ok, see TC-REQ-7.2. |
| TC-REQ-7.2 | Widget | PASS (code) | **FAIL CONFIRMED** | GET /y | named user visible |
| TC-REQ-8.1 | Absence | PASS(code) | NOT-TESTABLE (instrumentation) | — | API-only precondition |
| TC-REQ-9.1 | Blocker | PASS(code) | BLOCKED (unverified) | — | no probe |
| TC-REQ-29.1–29.3 | Mobile bulk | PASS(code) | NOT EXECUTED | /api/x | route missing |
| RISK-CR-2 | duplicate-on-top-of-public | code-review risk 2 | **FAIL CONFIRMED** | POST /z | private row on top |
| TC-REQ-2.1 | code-review style row | QA | needs runtime |
| TC-REQ-16.3 | legacy edit path | RE-ROUTE [UI] | client-side clearGDPRCache |
| TC-REQ-32.1 | admin duplicate toggle | PASS(code) | SPEC-DEFECT | POST /v | premise wrong |

## Statistics

| Status | Count |
|--------|-------|
| PASS | 32 |
| FAIL | 9 |
"""

SELFTEST_EXPECT = {
    "counts": {
        "NOT EXECUTED": 2, "PASS": 1, "FAIL CONFIRMED": 2,
        "NOT-TESTABLE (instrumentation)": 1, "BLOCKED (unverified)": 1,
        "QA": 1, "RE-ROUTE [UI]": 1, "SPEC-DEFECT": 1,
    },
    "sources": {"PASS(code)": 7},
    "ids_has": {"TC-REQ-7.2", "TC-REQ-29.1", "TC-REQ-29.2", "TC-REQ-29.3",
                "RISK-CR-2", "TC-REQ-32.1"},
    "ids_lacks": {"TC-REQ-7.2.", "TC-REQ-29"},
}


def selftest():
    counts, sources = count_statuses(SELFTEST_DOC)
    ids = collect_ids(SELFTEST_DOC)
    errs = []
    if counts != SELFTEST_EXPECT["counts"]:
        errs.append(f"status counts {counts} != {SELFTEST_EXPECT['counts']}")
    if sources != SELFTEST_EXPECT["sources"]:
        errs.append(f"source counts {sources} != {SELFTEST_EXPECT['sources']}")
    missing = SELFTEST_EXPECT["ids_has"] - ids
    if missing:
        errs.append(f"ids missing: {sorted(missing)}")
    phantom = SELFTEST_EXPECT["ids_lacks"] & ids
    if phantom:
        errs.append(f"phantom ids: {sorted(phantom)}")
    if errs:
        print("SELFTEST FAIL")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("SELFTEST PASS — statistics-table exclusion, one-status-per-row, "
          "PASS(code) separation, trailing-period ids, bold/qualified "
          "statuses, RE-ROUTE [UI], range expansion all verified")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--selftest":
        selftest()
        return
    report(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")


if __name__ == "__main__":
    main()
