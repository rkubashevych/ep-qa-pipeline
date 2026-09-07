# <ISSUEKEY> - QA Run Report

Phase analyzed: <docs / code / both>
Files reviewed: <list>
Generated: <YYYY-MM-DD>

## Health at a glance

| Category | Status |
|---|---|
| Run / coverage health | 🟢 / 🟡 / 🔴 |
| Input quality | 🟢 / 🟡 / 🔴 |
| Skill / process | 🟢 / 🟡 / 🔴 |
| Evidence quality | 🟢 / 🟡 / 🔴 (code phase; "—" on docs-only runs) |
| QA Service sync | 🟢 in sync / 🟢 not published yet / 🔴 no run / 🔴 partition mismatch / 🟡 stale run / 🔴 mismatch / — connector absent |
| Carried items | 🟢 none open ≥2 rounds / 🔴 <N> carried items / — first round |

## QA Service sync

> Only when the QA Service connector is present; otherwise one line:
> "Connector absent — not checked."

- Suite: `<path>` (<N> requirements / <M> cases) — or "no suite found"
- Verdict: <in sync / not published yet (docs run, pre-publish) /
  mismatch: missing <stableIds>, extra <stableIds>>
- Run (code phase, after step 6): `<title>` `<id>` — status <running /
  closed>; partition pass <N> · fail <N> · blocked <N> · known_defect
  <N> · skipped <N> · not_run <N> vs stage statistics <match / mismatch:
  …>; executed coverage: machine <N> · manual <N> · never executed <N>
  — or "no run for this pass" / "analyzer ran before step 6".

## Carried items

> From `<ISSUEKEY>-open-items.md` (`open-items-ledger.md`). "First
> round — ledger created with <N> rows" when none existed.

| # | Item | Class | First seen | Owner | Status this round |
|---|------|-------|------------|-------|-------------------|
| 1 | RISK-CR-1 — … | risk row | r1 2026-08-20 | PR author | 🔴 carried (3rd round, no decision) |

## Issues worth fixing

> Each issue tagged with bucket (Pipeline/skill, Input, Product) and severity.

- 🔴 [Input] No Confluence AC linked — requirements derived from Description only. Fix: add/link AC on the ticket.
- 🟡 [Pipeline] REQ-7 has no test cases (behavioural). Fix: re-run qa-test-cases or check why it was treated as structural.
- 🔴 [Pipeline] Evidence: TC-REQ-37.1 absence-PASS with API-created precondition / no positive control. Fix: re-run via web-testing per absence-check-protocol.md.
- 🟡 [Product] FAIL CONFIRMED: TC-REQ-1.2 — <bug>. Fix: file a bug.

If none: "No issues found — run is clean."

## Findings summary

<docs: requirement/check/test-case counts + channel breakdown + needing-clarification>
<code: code-review counters; api-testing counters + endpoint-mapping corrections; web-testing counters; confirmed bugs; routed-to-non-UI (mobile/export-email); verdict>

## Recommended next actions

- <ordered, concrete follow-ups>

---

# Chat summary format

After writing the file, the chat message is exactly this shape
(≤10 lines, worst news first, omit empty lines):

```
Run health (<docs/code>): 🟢 coverage · 🟡 input · 🟢 process · 🟢 evidence · 🟢 QA-sync · 🟢 carried (omit QA-sync when connector absent; evidence on code runs only; carried on retest rounds only)

Top issues (max 3):
1. 🔴 [Input] <one line> — fix: <one line>
2. 🟡 [Pipeline] <one line> — fix: <one line>

<docs: "N requirements → N checks → N test cases (N [UI] · N [API] · N routed); N need clarification.">
<code: "Code review N/N pass · API N/N · Web N/N — N confirmed bugs.">

Report: <ISSUEKEY>-run-report.md
```

If clean: replace the issues block with
"Run is clean — no issues found." and keep the counters line.
