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

## Issues worth fixing

> Each issue tagged with bucket (Pipeline/skill, Input, Product) and severity.

- 🔴 [Input] No Confluence AC linked — requirements derived from Description only. Fix: add/link AC on the ticket.
- 🟡 [Pipeline] REQ-7 has no test cases (behavioural). Fix: re-run qa-test-cases or check why it was treated as structural.
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
Run health (<docs/code>): 🟢 coverage · 🟡 input · 🟢 process

Top issues (max 3):
1. 🔴 [Input] <one line> — fix: <one line>
2. 🟡 [Pipeline] <one line> — fix: <one line>

<docs: "N requirements → N checks → N test cases (N [UI] · N [API] · N routed); N need clarification.">
<code: "Code review N/N pass · API N/N · Web N/N — N confirmed bugs.">

Report: <ISSUEKEY>-run-report.md
```

If clean: replace the issues block with
"Run is clean — no issues found." and keep the counters line.
