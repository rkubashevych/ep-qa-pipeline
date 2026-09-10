# Bug report template — default filing path

Used by qa-pipeline-code step 7 when the `/knowledge-base` skill is
not installed. One Jira bug per confirmed finding. Draft first, show
the user, create via `createJiraIssue` only after an explicit yes.

Voice, caps and section discipline: **`jira-writing-style.md`** (same
folder) — read it before drafting. The parts that bite here: summary
≤ 120 chars; ≤ 8 repro steps; Actual result ≤ 5 observed lines (code
paths go in Source, ≤ 2 lines); the h3 skeleton is CLOSED — no ad-hoc
sections; a second defect is a second draft. A dev reads this bug, so
the defect statement comes first, in plain words, no filler, no
wrap-up.

## Duplicate check (before drafting)

Search first: `searchJiraIssuesUsingJql` with the summary's key
phrases and the affected area, e.g.
`project = EP AND issuetype = Bug AND text ~ "<key phrase>" ORDER BY created DESC`.
If a plausible match exists, show it to the user instead of drafting —
link the existing ticket in the QA sub-task comment.

## Fields

| Field | Value |
|---|---|
| Project | `EP` |
| Issue type | `Bug` |
| Summary | `[<area>] <symptom in one line — what breaks, where>` — the AC id goes in the description, not the summary |
| Priority | propose from impact (blocker flow → High); user confirms |
| Labels | `qa-pipeline` |
| Links | "relates to" the Story; mention the QA sub-task key |

## Description skeleton

```
h3. Environment
<host / alpha env from the run> · event <EVENT_ID if relevant>
Found by: qa-pipeline run on <STORY> (QA sub-task <KEY>)

h3. Steps to reproduce
<numbered steps copied from the failing TC-REQ-N.M — concrete data
from its [data: ...] annotations, not generalised>

h3. Expected result
AC-<n>: "<the register clause — the acceptance criterion the build
contradicts, quoted verbatim>" (<document>, <section>)
<the FAIL's `Source:` / `Clause:` lines are the source of these two
lines. The ledger id first, so the reader knows WHICH criterion fails
before reading the sentence; a clause from a non-AC document carries the
document name instead of an id. Never the test case's Exp: block — a
test case is not a source of record (`../../qa-pipeline/references/sources-of-record.md`)>

h3. Actual result
<what the run observed: api-testing endpoint + observed field, or
web-testing step + what the agent saw; attach the FAIL screenshot
if one was taken>

h3. Source
AC-<n> · Register row <#> — <document>, <section> · REQ-N
TC-REQ-N.M (<STORY>-test-cases.md) · its Exp: block: <verbatim>
Stage: api-testing | web-testing · Status: FAIL / FAIL CONFIRMED
Evidence: <STORY>-web-evidence.md §<n> (web) / the request + response in <STORY>-api-testing.md (api)
Code-review finding (if any): <file, line, one-line finding>
```

## Rules

- Steps, data, and expected results come from the test case and the
  run reports — do not re-derive or embellish.
- One bug per root symptom: several TCs failing for the same cause →
  one bug listing all affected TC-IDs.
- Redact every token/credential; screenshots must not show secrets.
- After creation, the new bug keys go into the human summary's
  **Confirmed bugs** (and the run's `fail` rows link them on the QA
  Service side). No extra "bugs filed" comment on the sub-task — the
  status line and the human summary are the only two comments a ticket
  gets (`results-comment-template.md`).
