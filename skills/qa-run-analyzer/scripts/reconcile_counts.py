#!/usr/bin/env python3
"""Deterministic ID/status counter for the run-analyzer's
"counts reconcile" check.

    python3 reconcile_counts.py <ISSUEKEY> [dir]
    python3 reconcile_counts.py --selftest

Reads whichever of <KEY>-test-cases/code-review/api-testing/web-testing
.md exist. Where to look (data-locations.md → "The run folder",
environment.md → EP_QA_HOME): when no dir is given, `runs/<KEY>/` is
resolved under `$EP_QA_HOME`, else `~/.ep-qa`, else (legacy) the cwd;
inside it the newest pass folder `r<N>/` wins, falling back to the cwd
itself for pre-0.32 tickets. The test-cases file is looked up in the
pass folder first, then `runs/<KEY>/docs/` (where the docs phase writes
it), then the given dir — so a retest round reconciles against its case
list without being told twice. Pass an explicit dir (e.g.
`~/.ep-qa/runs/EP-1234/r2`) to pin an older round.
Prints, per file: the set size of case
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
- `[core]` markers (the human-tier selection marker) are counted on
  `## `/`### ` TC headings of the test-cases file only (either id
  shape); they never affect status parsing.
- **Flat ids (`TC-1`, `TC-12`) are recognised too.** Bug-fix mode and
  standalone-Bug runs number their derived cases `TC-1..TC-N` with no
  REQ group, because no requirements file exists to hang them on. Until
  0.27.0 this script matched only `TC-REQ-*`, so those runs reported
  `0 distinct case ids · no status rows` while the self-test still
  passed — the count gate was silently absent exactly where the run has
  no suite and no Jira archive to fall back on (found on EP-56289).
  A flat range needs `TC-` on BOTH sides (`TC-1–TC-7`): a bare number
  after a dash is prose, the same trap ID_RANGE already guards.

Run `--selftest` before trusting the output on a new pipeline version.

The status set mirrors ../references/status-vocabulary.md — the single
home for status semantics. A status added there must be added to
STATUSES below (longest-first) and to the self-test.
"""
import os
import re
import sys

# Letter suffix allowed (TC-REQ-12a.1) — without it, 12a.1/12b.1/12c.1
# silently collapse into one id "TC-REQ-12" (real under-count incident).
# The TC-REQ- alternative comes FIRST so the flat one can never shadow it
# (it cannot anyway — "R" is not a digit — but order documents intent).
# The flat `TC-<n>` alternative is bug-fix / standalone-Bug mode's id
# shape; see the docstring's flat-id rule.
CASE_ID = re.compile(
    r"(?:TC-REQ-\d+[a-z]?(?:\.\d+)*|TC-\d+[a-z]?|RISK-[A-Z]+-\d+)")
# TC-REQ-29.1–29.3 / TC-REQ-29.1-29.3 / TC-REQ-29.1–TC-REQ-29.3
# The right side MUST be a dotted maj.min — a bare number after a dash
# is prose ("TC-REQ-20.1 — 30 characters accepted") and once invented
# 26 phantom ids when treated as a range end.
ID_RANGE = re.compile(
    r"TC-REQ-(\d+)\.(\d+)\s*[–—-]\s*(?:TC-REQ-)?(\d+)\.(\d+)")
# TC-1..TC-7 / TC-1–TC-7 — flat-id spans, as bug-fix-mode reports write
# them when summarising routing ("9 to web-testing (TC-1..TC-7, TC-10)").
# Both sides MUST carry the TC- prefix, for the same reason ID_RANGE
# demands a dotted right side: "TC-1 — 30 characters accepted" is prose.
FLAT_RANGE = re.compile(r"TC-(\d+)\s*(?:\.\.+|[–—-])\s*TC-(\d+)")
# Longest alternatives first so FAIL CONFIRMED never half-matches as FAIL.
STATUSES = (
    "FAIL CONFIRMED", "FAIL REJECTED", "NOT-TESTABLE", "NOT EXECUTED",
    "SPEC-DEFECT", "OBSERVATION", "RE-ROUTE", "PARTIAL", "BLOCKED",
    "SKIPPED", "PASS", "FAIL", "QA", "N/A",
)
STATUS_CELL = re.compile(
    r"(" + "|".join(re.escape(s) for s in STATUSES) +
    r")(?:\s*\(([^)]*)\))?(?:\s*\[([^\]]+)\])?$")
# Core marker on TC headings (human-tier selection; test-cases file only).
# Accepts both heading levels and both id shapes: docs-phase files write
# `### TC-REQ-n.m`, bug-fix-mode files write `## TC-n`.
CORE_MARK = re.compile(r"^#{2,3} TC-(?:REQ-)?\d.*\[core\]", re.M)
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
        if maj2 != maj:
            continue  # cross-major range: don't guess
        lo_i, hi_i = int(lo), int(hi)
        if lo_i < hi_i <= lo_i + 50:
            for n in range(lo_i, hi_i + 1):
                ids.add(f"TC-REQ-{maj}.{n}")
    for lo, hi in FLAT_RANGE.findall(text):
        lo_i, hi_i = int(lo), int(hi)
        if lo_i < hi_i <= lo_i + 50:
            for n in range(lo_i, hi_i + 1):
                ids.add(f"TC-{n}")
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


def ep_qa_home():
    """environment.md → Resolution order: $EP_QA_HOME, then ~/.ep-qa when
    it exists, else the cwd (legacy layout — runs/ beside skills/)."""
    env = os.environ.get("EP_QA_HOME")
    if env:
        return env
    home = os.path.join(os.path.expanduser("~"), ".ep-qa")
    if os.path.isdir(home):
        return home
    return "."


def resolve_run_dir(key, d=None):
    """Return the folder to read stage reports from.

    Explicit dir → as given. Otherwise the newest `runs/<key>/r<N>` under
    ep_qa_home(); when none exists, the cwd (legacy layout: files beside
    the repo root). Also returns the docs folder used as the test-cases
    fallback (may not exist).
    """
    root = ep_qa_home()
    runs = "runs" if root == "." else os.path.join(root, "runs")
    docs = os.path.join(runs, key, "docs")
    if d is not None:
        return d, docs
    base = os.path.join(runs, key)
    rounds = []
    if os.path.isdir(base):
        for name in os.listdir(base):
            if name.startswith("r") and name[1:].isdigit() and \
                    os.path.isdir(os.path.join(base, name)):
                rounds.append(int(name[1:]))
    if rounds:
        return os.path.join(base, f"r{max(rounds)}"), docs
    return ".", docs


def locate(key, stage, d, docs):
    """Pass folder first; test-cases may also live in docs/ or the cwd."""
    candidates = [os.path.join(d, f"{key}-{stage}.md")]
    if stage == "test-cases":
        candidates += [os.path.join(docs, f"{key}-{stage}.md"),
                       f"{key}-{stage}.md"]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def report(key, d=None):
    d, docs = resolve_run_dir(key, d)
    print(f"run folder: {d}")
    ids = {}
    for stage in STAGES:
        path = locate(key, stage, d, docs)
        if path is None:
            print(f"{stage}: file not present")
            continue
        text = open(path, encoding="utf-8").read()
        ids[stage] = collect_ids(text)
        counts, sources = count_statuses(text)
        cstr = " · ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        sstr = "".join(f" · source {k}={v}" for k, v in sorted(sources.items()))
        corestr = (f" · core={len(CORE_MARK.findall(text))}"
                   if stage == "test-cases" else "")
        print(f"{stage}: {len(ids[stage])} distinct case ids · "
              f"{cstr or 'no status rows'}{sstr}{corestr}")
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

| TC | Name | Arrived as | Status | Call | Evidence |
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
| TC-REQ-12a.1 | sort variant A | QA | PASS | GET /s?o=a | letter-suffix id |
| TC-REQ-12b.1 | sort variant B | QA | PASS | GET /s?o=b | letter-suffix id |

## TC-REQ-40.1 — 30 characters accepted and saved
Prose heading above must NOT parse as a range 40.1–40.30.

### TC-REQ-41.1 — core-marked heading  [UI] [core]
### TC-REQ-41.2 — plain heading  [UI]
Exactly one [core] heading above; the bare "[core]" word in this prose
line must not count (CORE_MARK anchors on the heading).

## Statistics

| Status | Count |
|--------|-------|
| PASS | 32 |
| FAIL | 9 |
"""

SELFTEST_EXPECT = {
    "counts": {
        "NOT EXECUTED": 2, "PASS": 3, "FAIL CONFIRMED": 2,
        "NOT-TESTABLE (instrumentation)": 1, "BLOCKED (unverified)": 1,
        "QA": 1, "RE-ROUTE [UI]": 1, "SPEC-DEFECT": 1,
    },
    "sources": {"PASS(code)": 7},
    "ids_has": {"TC-REQ-7.2", "TC-REQ-29.1", "TC-REQ-29.2", "TC-REQ-29.3",
                "RISK-CR-2", "TC-REQ-32.1",
                "TC-REQ-12a.1", "TC-REQ-12b.1", "TC-REQ-40.1"},
    "ids_lacks": {"TC-REQ-7.2.", "TC-REQ-29",
                  "TC-REQ-40.2", "TC-REQ-40.30", "TC-REQ-12"},
    "core": 1,
}

# Bug-fix / standalone-Bug mode: flat `TC-<n>` ids, no REQ groups, `## `
# case headings. Added in 0.27.0 — before it, this whole shape parsed as
# zero ids and zero statuses while the docs-phase fixture above passed.
SELFTEST_BUGFIX_DOC = """
## Results

| TC | Name | Arrived as | Status | Comment |
|----|------|--------|--------|---------|
| TC-1 | reported defect, 1-result search | QA | PASS | guest only |
| TC-2 | negative sibling, unfiltered listing | QA | PASS | — |
| TC-10 | undocumented delta, replace-not-merge | QA | **FAIL** | step 2 |
| TC-11 | zero counter renders bare | QA | NOT EXECUTED | no such tab here |
| TC-12 | build provenance | QA | BLOCKED (unverified) | no probe recorded |
| RISK-CR-2 | pager mount gate | code-review risk 2 | PASS | endlessScroll false |

Routing note: 3 to web-testing (TC-1..TC-3), the rest by channel.

## TC-6 — 8 characters accepted and saved
Prose heading: the bare "8" after the dash must NOT be read as a range
end, because it carries no TC- prefix. If the guard ever breaks, this
line alone invents two phantom ids.

## TC-4 — core-marked heading  [UI] [core]
## TC-5 — plain heading  [UI]

## Statistics

| Status | Count |
|--------|-------|
| PASS | 3 |
| FAIL | 1 |
"""

SELFTEST_BUGFIX_EXPECT = {
    "counts": {
        "PASS": 3, "FAIL": 1, "NOT EXECUTED": 1,
        "BLOCKED (unverified)": 1,
    },
    "sources": {},
    # TC-3 comes only from the TC-1..TC-3 span; TC-4/5/6 only from headings.
    "ids_has": {"TC-1", "TC-2", "TC-3", "TC-4", "TC-5", "TC-6",
                "TC-10", "TC-11", "TC-12", "RISK-CR-2"},
    # TC-7/TC-8 would appear if the flat-range guard let a bare number be
    # a range end; TC-REQ-1 would appear if the id shapes cross-matched.
    "ids_lacks": {"TC-7", "TC-8", "TC-REQ-1"},
    "core": 1,
}


def check(doc, expect, label, errs):
    """Run one fixture and append any mismatches to errs."""
    counts, sources = count_statuses(doc)
    ids = collect_ids(doc)
    if counts != expect["counts"]:
        errs.append(f"[{label}] status counts {counts} != {expect['counts']}")
    if sources != expect.get("sources", {}):
        errs.append(f"[{label}] source counts {sources} != "
                    f"{expect.get('sources', {})}")
    missing = expect["ids_has"] - ids
    if missing:
        errs.append(f"[{label}] ids missing: {sorted(missing)}")
    phantom = expect["ids_lacks"] & ids
    if phantom:
        errs.append(f"[{label}] phantom ids: {sorted(phantom)}")
    core = len(CORE_MARK.findall(doc))
    if core != expect["core"]:
        errs.append(f"[{label}] core count {core} != {expect['core']}")


def check_run_folder(errs):
    """runs/<KEY>/r<N> resolution: newest round wins, docs/ supplies the
    case file, legacy cwd is the fallback (data-locations.md 0.32.0);
    EP_QA_HOME wins over the cwd (environment.md 0.39.0)."""
    import tempfile
    key = "EP-0"
    cwd = os.getcwd()
    saved = {k: os.environ.pop(k, None) for k in ("EP_QA_HOME", "HOME", "USERPROFILE")}
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        # a real ~/.ep-qa must not leak into the test: point ~ at the tmp dir
        os.environ["HOME"] = os.environ["USERPROFILE"] = tmp
        try:
            # EP_QA_HOME set → runs/ is looked up there, not in the cwd
            os.makedirs(os.path.join(tmp, "elsewhere", "runs", key, "r3"))
            os.environ["EP_QA_HOME"] = os.path.join(tmp, "elsewhere")
            d, _ = resolve_run_dir(key)
            if d != os.path.join(tmp, "elsewhere", "runs", key, "r3"):
                errs.append(f"run-folder: EP_QA_HOME ignored, gave {d!r}")
            del os.environ["EP_QA_HOME"]
            # legacy: no EP_QA_HOME, nothing under runs/ → cwd
            d, _ = resolve_run_dir(key)
            if d != ".":
                errs.append(f"run-folder: legacy fallback gave {d!r}, want '.'")
            # rounds: r1, r2, r10 → r10 (numeric, not lexical)
            for r in ("r1", "r2", "r10"):
                os.makedirs(os.path.join("runs", key, r))
            os.makedirs(os.path.join("runs", key, "docs"))
            d, docs = resolve_run_dir(key)
            if d != os.path.join("runs", key, "r10"):
                errs.append(f"run-folder: newest round gave {d!r}, want r10")
            # explicit dir pins an older round
            d2, _ = resolve_run_dir(key, os.path.join("runs", key, "r2"))
            if not d2.endswith("r2"):
                errs.append(f"run-folder: explicit dir ignored ({d2!r})")
            # test-cases: pass folder first, then docs/, then cwd
            open(os.path.join(docs, f"{key}-test-cases.md"), "w").write("x")
            p = locate(key, "test-cases", d, docs)
            if p != os.path.join(docs, f"{key}-test-cases.md"):
                errs.append(f"run-folder: docs/ fallback for test-cases gave {p!r}")
            open(os.path.join(d, f"{key}-test-cases.md"), "w").write("x")
            p = locate(key, "test-cases", d, docs)
            if p != os.path.join(d, f"{key}-test-cases.md"):
                errs.append(f"run-folder: pass folder should win for test-cases ({p!r})")
            # a stage report is never taken from docs/ or cwd
            open(f"{key}-code-review.md", "w").write("x")
            if locate(key, "code-review", d, docs) is not None:
                errs.append("run-folder: code-review must not fall back to cwd")
        finally:
            os.chdir(cwd)
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


def selftest():
    errs = []
    check(SELFTEST_DOC, SELFTEST_EXPECT, "docs-phase", errs)
    check(SELFTEST_BUGFIX_DOC, SELFTEST_BUGFIX_EXPECT, "bug-fix", errs)
    check_run_folder(errs)
    if errs:
        print("SELFTEST FAIL")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print("SELFTEST PASS — statistics-table exclusion, one-status-per-row, "
          "PASS(code) separation, trailing-period ids, bold/qualified "
          "statuses, RE-ROUTE [UI], range expansion, [core] heading "
          "counting, bug-fix-mode flat ids (TC-<n>, flat spans, "
          "`## ` headings), and runs/<KEY>/r<N> folder resolution "
          "(EP_QA_HOME first, newest round, docs/ case-file fallback, "
          "legacy cwd) all "
          "verified")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--selftest":
        selftest()
        return
    report(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)


if __name__ == "__main__":
    main()
