# <ISSUEKEY> - Manual Results

Source: <runsheet.xlsx / TSV paste / triage file — list all used>
Automated record read from: <verdict files / archive comment / suite>
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

| TC | Published | Manual | Reason (from Notes) | Bug |
|----|-----------|--------|---------------------|-----|
| TC-REQ-37.1 | PASS (api-testing 2026-07-28) | FAIL | organizer Lead dashboard names the opted-out user | EP-55702 |

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
| <new> | TC-REQ-x | filed this session / offered, declined |

---

Section rules:
- Join is by TC id only. A sorted or filtered sheet must produce the
  identical report.
- Retractions carry the OLD verdict with its source and date — the
  point is the correction, not just the new value.
- Every FAIL row shows its bug key or appears in the unfiled-bugs offer.
