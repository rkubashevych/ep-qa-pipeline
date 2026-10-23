# Bug report template — every bug this pipeline files

Used by qa-pipeline-code step 7 and by qa-manual-results steps 4–5 when
the `/knowledge-base` skill is not installed. One Jira ticket per confirmed
finding — a **Defect** under the main task when the fault is new in the
change under test, a **Bug** when it is already on production ("Defect
or Bug" below). Draft first, show the user, create via `createJiraIssue`
only after an explicit yes.

**This template covers roster bugs too — since 0.43.6.** It used to
apply only to findings with no covering case, because a roster `fail`
let qa-service file the ticket. That path produces a case dump reported
by the service account, and the reporter cannot be corrected afterwards
(`../../qa-pipeline/references/test-runs.md` → "File the ticket FIRST").
So a roster bug is drafted here, created through the Atlassian connector
(which authenticates as the operator), and only then is the `fail`
recorded — the open ticket dedupes it.

Voice, caps and section discipline: **`jira-writing-style.md`** (same
folder) — read it before drafting. The parts that bite here: summary
≤ 120 chars; ≤ 8 repro steps; Actual result ≤ 5 observed lines (code
paths go in Source, ≤ 2 lines); the h3 skeleton is CLOSED — no ad-hoc
sections; a second defect is a second draft. A dev reads this bug, so
the defect statement comes first, in plain words, no filler, no
wrap-up.

## Defect or Bug — decide first, since 0.75.0

**The question is one: is the faulty behaviour already on production?**

| Where the fault lives | Issue type | Placement |
|---|---|---|
| **Not on production yet** — in the change under test, on its first testing on alpha or RC (the ticket's PRs, its new screens, its new behaviour) | **`Defect`** (a sub-task type) | `parent` = **the main task**: the Story / Task under test. Ticket under test is itself a Defect → its parent. A bug-fix whose fix introduced a new fault → the Bug under test. No "relates to" link — the parent is the link |
| **Already on production** — the behaviour exists without the ticket's change: a pre-existing fault the run merely surfaced, a bug-fix regression case failing on behaviour the fix never touched (EP-58774), an RC finding also present in the released build | **`Bug`** (standalone) | "relates to" the ticket under test |

How to tell, without testing production (the pipeline never calls a
production host — `../../qa-pipeline/references/environment.md`):

- **Defect** when the failing code path is in the ticket's PR diffs
  (stage 5's `pr-summary`), or the failing surface does not exist
  before the ticket. This is the default for a FAIL on a case of the
  ticket's own requirements.
- **Bug** when the failing code predates the ticket's PRs (`git log` /
  `git blame` on the line names an older commit already on the
  production line), or the user / tester says it is on production.
- **Unsure → ask**, in the draft preview: "`<symptom>` — Defect under
  `<KEY>` (new in this change) or Bug (already on production)?" Never
  guess; a Defect under the wrong Story sends a pre-existing fault back
  to a developer who did not cause it, and a Bug for a new fault lets
  the Story pass with it.

Every draft states its choice and the one-line reason
(`type: Defect — the fault is in PR #5630's diff`) so the yes covers it.
A FAIL on the bug-fix ticket's **own** expected result files nothing:
the fix fails and goes back (`run-modes.md` → "Bug-fix mode (no docs phase)").

## Duplicate check (before drafting)

Search first: `searchJiraIssuesUsingJql` with the summary's key
phrases and the affected area, across **both** types, e.g.
`project = EP AND issuetype in (Bug, Defect) AND text ~ "<key phrase>" ORDER BY created DESC`.
If a plausible match exists, show it to the user instead of drafting —
link the existing ticket in the QA sub-task comment.

## Fields

| Field | Value |
|---|---|
| Project | `EP` |
| Issue type | `Defect` + `parent` = the main task, or `Bug` — per "Defect or Bug" above |
| Summary | **roster bug:** `[<STABLE-ID>] <symptom in one line — what breaks, where>`; **no covering case:** `[<area>] <symptom …>`. The AC id goes in the description, not the summary |
| Priority | propose from impact (blocker flow → High); user confirms |
| Assignee, Team (`customfield_10001`), Components | **required** — the create is a 400 without them (EP-58260). Assignee: ask the user before the preview. Team and Component: from recent bugs in the same area (`reporter = currentUser()`) |
| Labels | `qa-pipeline`, plus the repo when one surface owns it (`admin-ui`, `portal-ui`) |
| Links | **Bug:** "relates to" the ticket under test; mention the QA sub-task key. **Defect:** none — `parent` carries it |

**The `[<STABLE-ID>]` prefix on a roster bug is the dedupe key** — it is
how `record_case_result` finds the open ticket and links it instead of
filing a second. Never omit it, never strip it from an existing ticket.
EP-57409 was filed without it moments before qa-service auto-filed
EP-57410 for the same case; the team got two tickets and one was closed
as a duplicate.

## The tracker's own fields — fill them, they are not optional

The EP project has a **structured bug form**, and a description-only
ticket leaves it empty. qa-service's auto-filed tickets do exactly that,
which is most of why they read badly (EP-57509, 2026-09-18). Set these
alongside `description`:

| Field | Id | Type |
|---|---|---|
| Steps to reproduce | `customfield_10377` | **ADF** — a plain string is rejected |
| Expected result | `customfield_10147` | **ADF** |
| Actual result | `customfield_10146` | **ADF** |
| Admin panel URL | `customfield_10259` | string |
| Frontend URL | `customfield_10260` | string |
| Environment name | `customfield_10252` | string |
| Event name | `customfield_10253` | string |
| **Defect only:** Environment | `customfield_10378` | option — Branch / Alpha / RC, where it was found |
| **Defect only:** Development area | `customfield_10415` | option |
| **Defect only:** Event ID | `customfield_12478` | string |

The three ADF fields take
`{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"…"}]}]}`
— passing a string returns `Operation value must be an Atlassian
Document`. The error response lists every settable field for the issue
type, so when a field id here goes stale, read it back from that list
rather than guessing.

**`reporter` cannot be set on this project** ("not on the appropriate
screen") — which is exactly why the ticket is created by the operator's
own connector rather than corrected afterwards.

**Re-check labels a few minutes after creation.** The AI Bug Analyzer
bot rewrites `labels` on new tickets and drops ones set at creation
(observed on EP-57509, 2026-09-18).

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
Evidence: <STORY>-web-evidence.md §<n> (web) / <STORY>-api-evidence.md §<n> (api)
Code-review finding (if any): <file, line, one-line finding>
```

## Rules

- Steps, data, and expected results come from the test case and the
  run reports — do not re-derive or embellish.
- One bug per root symptom: several TCs failing for the same cause →
  one bug listing all affected TC-IDs.
- Redact every token/credential; screenshots must not show secrets.
- After creation, the new bug keys go into the human summary's
  **Bugs** (and the run's `fail` rows link them on the QA
  Service side). No extra "bugs filed" comment on the sub-task — the
  status line and the human summary are the only two comments a ticket
  gets (`results-comment-template.md`).
