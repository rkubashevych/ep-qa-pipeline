# <ISSUEKEY> - Manual Results

Source: <runsheet.xlsx / TSV paste / triage file — list all used>
Automated record read from: <QA Service run <id> / verdict files / archive comment>
QA Service run: <id> — <status after this stage: closed / running (why)> · recorded <N> manual verdicts (<N> supersede a machine verdict)
Date: <YYYY-MM-DD>

## Summary

| Category | Count |
|---|---|
| CONFIRMS (manual agrees with published) | <N> |
| FILLS (first real verdict for the case) | <N> |
| RETRACTS (overturns a published verdict) | <N> |
| Non-standard verdicts (human decision needed) | <N> |
| Unmatched rows (TC id not recognised) | <N> |
| Not run (empty Result) | <N> |

## Retractions
> The most important section — always first. Never soften.

| TC | Published | Where published | Manual | Reason (from Notes) | Bug |
|----|-----------|-----------------|--------|---------------------|-----|
| TC-REQ-37.1 | PASS (api-testing 2026-07-28) | run 7c3e1ab5 · EP-56109 comment 144183 | FAIL | organizer Lead dashboard names the opted-out user | EP-55702 |

> "Where published" is what the retraction comment is addressed to
> (`test-runs.md` → "Retraction target rule"): the run always, plus the
> ticket + comment id when the old verdict reached a Jira comment.

## Fills

| TC | Was | Manual | Notes | Bug |
|----|-----|--------|-------|-----|
| TC-REQ-27.5 | no verdict (not executed) | PASS | — | — |

## Confirms

| TC | Verdict | Notes |
|----|---------|-------|
| TC-REQ-1.3 | PASS | — |

## Non-standard verdicts
> Recorded verbatim; not coerced into the four statuses.

| TC | Raw entry | Suggested handling |
|----|-----------|--------------------|
| TC-REQ-32.1 | "N/A — spec premise false" | requirement correction; see triage |

## Unmatched rows
> Rows whose TC id matched no known case. Never silently dropped.

| Row TC value | Result | Notes |
|--------------|--------|-------|

## Not run

<comma-separated TC ids with empty Result, or "none">

## Bugs

| Bug | Cases | Status |
|-----|-------|--------|
| EP-55691 | TC-REQ-1.1 | linked from Notes |
| EP-56912 | TC-REQ-4.2 | filed by the run (`fail` recorded, `created: true`) |
| <new> | RISK-CR-2 | filed this session via template / offered, declined |

## Ledger

Rows of `<ISSUEKEY>-open-items.md` closed this round (id — decision) and
rows carried forward (id — first seen). "none" when the ledger is empty.

---

Section rules:
- Join is by TC id only. A sorted or filtered sheet must produce the
  identical report.
- Retractions carry the OLD verdict with its source and date — the
  point is the correction, not just the new value.
- Every FAIL row shows its bug key or appears in the unfiled-bugs offer.
