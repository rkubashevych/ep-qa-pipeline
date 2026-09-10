# The QA Service test run — the per-case record

**Contents:** Why · One run per pass · Creating the run (step 6) ·
Verdict mapping (the single home) · What stays `not_run` in wave 1 and
why · Stage 10 — the human pass · Retractions · Retraction target rule ·
Notes are retired as a verdict store · Verification · Connector absent

## Why this file exists

On EP-53978 (five verification passes, 2026-07-29 → 2026-09-07) the
suite `common/global-search-top-results` read `requirementCoverage.
verified: 0` for all 42 cases after every pass. Each pass had appended
its verdicts as text into `detail.notes`, exactly as the write-back rule
said — and text in notes is invisible to every coverage read, every
dashboard, and every colleague who asks "has anybody run this?". Each
pass then reconstructed the prior state by hand from markdown files.

QA Service has a first-class run model, and **the rest of the team
already uses it**: `create_test_run` (fixed roster, `env`, `releaseId`,
`principal`), `record_case_result` (verdict + note + evidence,
`source: manual | machine`, **re-recording supersedes and keeps history**,
**a `fail` files one deduplicated Jira defect at record time**),
`close_test_run`, `reopen_test_run`, `get_test_run`,
`case_execution_history`, `executed_coverage`, `run_defects`.

A pipeline session even used it once, off-book, on 2026-09-02 (run
`7c3e1ab5…`, "EP-53978 retest 3", 51 cases, principal
"ep-qa-pipeline agent"). That run is the evidence behind the mapping
below — including the two mistakes it made, which this file forbids:
SPEC-DEFECT recorded as `known_defect`, and human-executed rows
recorded as `source: machine`.

## One run per pass of a ticket

A **pass** = one code-phase run of the pipeline on a ticket (a first
run, a retest round, a bug-fix check), machine stages and the human
round together. One run per pass, created at step 6 (wave 1) and
closed at stage 10.

- **Title:** `<KEY> <mode> <YYYY-MM-DD> — <env label>`. `<mode>` is one
  of `first run` (r1), `retest <k>` (r<k+1>), `bug-fix` — e.g.
  `EP-56133 first run 2026-08-20 — alpha2`, `EP-56133 retest 3
  2026-09-07 — alpha2`. Retest rounds are numbered in the title; the
  ledger (`open-items-ledger.md`) carries the round.
- **`env`:** the target host label as the run used it (`alpha2`, `rc`,
  `alphanext-<n>`). Never a credential, never a full URL with a token.
- **`releaseId`:** when the ticket's `fixVersion` or the suite names a
  release that `list_releases` returns — a verdict is resolved per
  (case, release), so this is what makes `executed_coverage` scopable.
  None known → omit, and say `release: none` in the preview; do not
  invent one.
- **`principal`** (on the run and on every machine verdict):
  `ep-qa-pipeline agent (<KEY> <mode>, stage <n>)`. On human verdicts
  (stage 10): the tester's e-mail, taken from the run sheet / the user
  — never the agent's label on a human result.
- **Roster = the scope.** Pass the suite case ids (stable ids are
  accepted) of exactly the cases step 0 put in scope — the suite cases
  marked `detail.ticket = <KEY>`, or the confirmed retest scope, or the
  bug-fix mini cases. **The roster is fixed at creation**
  and that is the point: a case authored after the pass began is not
  silently in it. Scope learned mid-run → `add_run_cases`, and the scope
  file says so. `RISK-CR-*` rows are not suite cases and cannot be on
  the roster; they enter it only via the existing "promote confirmed risk
  rows to suite cases" step (`qa-service-publish.md`), then
  `add_run_cases`. Until then their evidence lives in the stage report.
- **Bug-fix mode with no suite:** no run — there is nothing to put on a
  roster. The reports and the Jira comments are the record, as before.
  Say so once in the final response.

## Verdict mapping — the single home

Pipeline statuses come from `status-vocabulary.md`; the run vocabulary
is `pass | fail | blocked | known_defect | skipped | flaky`. This table
is the only place the mapping lives. **A `fail` files a Jira defect the
moment it is recorded** (verified: EP-56912 was created by the
2026-09-02 run's single `fail`, `created: true`) — read the table with
that in mind.

| Pipeline status (stage) | Run verdict | `note` (required on fail/blocked; write it always) |
|---|---|---|
| `PASS` (API/WEB); `PASS` (CR, code-determined) | `pass` | one line: what was observed, control line for absence checks; CR-only: `PASS (code) — <file:line>` so a reader knows nothing ran |
| `FAIL REJECTED` | `pass` | `FAIL REJECTED — CR finding <…> refuted: <observed>` |
| `BLOCKED` (with `Probe:`) | `blocked` | the probe and its response |
| `BLOCKED (unverified)` | `blocked` | `UNVERIFIED — <reason>; would verify: <…>` |
| `NOT EXECUTED`, `NOT-TESTABLE`, `NOT-TESTABLE (instrumentation)` | `skipped` | `NOT EXECUTED — <environmental reason>` / `NOT-TESTABLE — <correct endpoint>` (a routed case is not skipped — it carries the executing stage's verdict) |
| `SPEC-DEFECT` | `skipped` | `SPEC-DEFECT — case says <X>, source says <Y>` **plus** the `discrepancy:` line on the case (`qa-service-publish.md`). **Never `known_defect`** — that asserts a product defect exists; the defect is in the case text |
| `FAIL CONFIRMED` whose defect already has a Jira key (the bug this retest re-tests, or a key named in the case) | `known_defect` | `FAIL CONFIRMED — <key>: <observed>`. Files nothing; the key is already open |
| `FAIL`, `FAIL CONFIRMED` with no key, `PARTIAL`, code-review `FAIL` runtime could not reach | **none — the row stays `not_run` in wave 1** | — (see next section) |
| narrow wave-1 exception: runtime-confirmed + evidenced + **blocking the manual round** | `fail` | where / expected / actual + `Source:` + `Clause:`. Named case by case in the confirmation preview: recording it **is** filing the bug |
| `OBSERVATION`, `OBSERVATION (no source checked)` | none on its own (a case that passed is `pass`; the observation goes in its note, labelled) | `… OBSERVATION (no source checked): <question form>` |
| `QA`, `N/A`, `RE-ROUTE [UI]` (CR) | none — input statuses; the executing stage's verdict is recorded | — |
| human `PASS` / `FAIL` / `BLOCKED` / `SKIPPED` (stage 10) | `pass` / `fail` / `blocked` / `skipped`, **`source: manual`** | the tester's Notes verbatim, bug key if any |
| human non-standard entry ("N/A — premise false") | none — listed for a human decision, never coerced | — |

`flaky` is never written by the pipeline: a verdict that changed between
two reads is a `blocked` with both reads in the note, or a defect.

Evidence entries take http(s) URLs on the service's host allowlist —
the Jira URL of the bug or of the wave-1 status comment, a jam.dev link
from the tester. A screenshot that exists only on disk is referenced by
path in the note (`evidence: <KEY>-web-evidence.md §n`); it cannot be
uploaded here.

## What stays `not_run` in wave 1, and why

The two-wave rule says no defect is filed and no verdict is shown to a
human before the human round. A machine `fail` **is** a filing — the
service creates the Jira defect at record time, and nothing in
`record_case_result` suppresses it. So a machine FAIL recorded in wave 1
would file a bug from a verdict that has a measured ~50 % base rate of
being wrong when it came from a code read.

`blocked` was considered for these rows and rejected: in the executed
tier the whole team reads, `blocked` says "the environment prevented
execution". A failure recorded as blocked hides a defect behind an
environment problem — the exact inversion of "prefer BLOCKED over a
false PASS".

`not_run` is the honest state: **no confirmed verdict exists yet.** It
is what the run sheet already means by "the human must walk this row",
and `get_test_run`'s `currentCaseId` is where the tester resumes. The
run therefore stays `running` after wave 1 whenever any FAIL / PARTIAL
row exists, and the wave-1 status comment says so
(`… K for manual — QA Service run <id> open`). Stage 10 closes it.

The machine's evidence for those rows is not lost: it is in the stage
report (in the run folder — the only copy since 0.33.0) and in the
walk plan card's `machine:` backstage key. What is withheld
is only the *verdict*, until a person confirms it.

## Stage 10 — the human pass

Same run, `source: manual`, principal = the tester. For every row with a
manual Result: `record_case_result`. A row the machine already recorded
(a `[core]` spot-check, a retracted PASS) is **re-recorded** — the
service supersedes and keeps both, each with its own principal and
timestamp. If the run's status is `completed` (every row had a verdict),
call `reopen_test_run` first; it edits nothing. When the sheet is fully
ingested: `close_test_run` with `mode: closed` — `aborted` only when the
pass was abandoned and the user says so. Never leave a fully-ingested run
`running`: a stale run is what the analyzer flags as "manual results
never ingested".

A human `fail` files the defect (deduplicated per case: an open issue
already referencing the stable id is linked, not duplicated —
`created: false` in `run_defects`). That replaces the draft-per-template
path for **cases on the roster**: the stage-10 confirmation preview lists
every `fail` about to be recorded, case by case, and the explicit yes is
the per-bug yes. Findings with no covering case (RISK rows, observations
the human confirmed) still go the template route.

## Retractions

A retraction is a re-record. `case_execution_history` shows
old → new with who and when; nothing is edited. The pipeline's own
history-in-notes convention (`SUPERSEDES …`, `⚠ CURRENT VERDICT:`) is
therefore **not written any more** — it re-implemented what the service
does natively, and it was invisible to coverage reads. Read old notes
for pre-0.30 history; write no new run lines into notes.

The communication half is unchanged and load-bearing: a stage that
records a retraction says so in its Jira human summary — retractions
first, `old → new` with the reason and the run id.

## Retraction target rule — the one sanctioned cross-ticket comment

**A retraction is posted where the verdict it retracts was published**,
on whatever ticket that is. On EP-53978 (retest 3), three cases were
published as FAIL CONFIRMED in comments on **EP-56109**; the retest that
passed them ran under **EP-56133**, a Bug with no QA sub-task. The 0.26.0
"no walk-up" rule left the retraction with nowhere to land, and a reader
of EP-56109 kept seeing three confirmed failures that were fixed.

Rules:

- The retraction comment is **not a dump**: ≤ 6 lines — the run id,
  each case (`<stable id> — <old> → <new>`), the reason, and the
  ticket/run that established the new verdict. No fenced dumps, no
  summary of the new run.
- It goes to the ticket **and comment thread** where the retracted
  verdict was published, even when that ticket is not the one under
  test. Stage 10's reconciliation therefore records, for every RETRACTS
  row, *where* the old verdict was published (ticket key + comment id —
  the retest-scope file already carries it; it is now a required
  column).
- Nothing else crosses tickets: status lines and summaries stay on the
  ticket under test (its QA sub-task when it has one). Archive comments
  no longer exist at all (0.33.0).

## Notes are retired as a verdict store

`detail.notes` keeps exactly two pipeline-written things: the
`discrepancy:` line for a SPEC-DEFECT (a property of the case, not a
verdict) and pre-0.30 history. Everything that used to be a "run line"
is a `record_case_result`. The `⚠ CURRENT VERDICT:` first line is no
longer maintained; where one exists from an earlier release it stays as
history and the run is the current truth.

## Verification (post-publish, and analyzer §4)

- `get_test_run`: roster count == the scope count step 0 confirmed;
  the `progress` partition matches the stage reports' statistics under
  the mapping above (`pass` = PASS + FAIL REJECTED, `blocked` = BLOCKED
  + BLOCKED (unverified), `skipped` = NOT EXECUTED + NOT-TESTABLE +
  SPEC-DEFECT, `known_defect` = keyed FAIL CONFIRMED, `not_run` = the
  FAIL / PARTIAL rows awaiting the human). A mismatch is a count-gate
  failure — fix before the run is left.
- `executed_coverage(suiteId[, releaseId])`: `neverExecuted` fell by
  the number of rows recorded; `machine` and `manual` are reported as
  separate numbers, never one percentage.
- After stage 10: the run is `closed`; `run_defects` lists every human
  `fail` with a key; every RETRACTS row has a `supersedesId` and a
  retraction comment on the original ticket.

## Connector absent

No run. The Jira comments and the reports on disk carry everything, the
final response says "no durable per-case record — QA Service connector
not enabled", and the analyzer treats it as a normal outcome, not a 🔴.
