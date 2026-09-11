---
name: qa-pipeline
description: >
  The pipeline's front door. Give it a ticket (key, URL, or pasted) —
  it reads the ticket's type and pipeline state, proposes the right
  route, and on confirmation invokes it: docs phase for a fresh
  Story/Task, code phase when the docs are published, bug-fix mode for
  a standalone Bug, retest when a fix landed, the guided manual walk
  when the walk plan is built, manual-results ingestion when a filled
  sheet is back. Use when the user says "qa this ticket", "process
  EP-1234 for testing", "run the pipeline on this", or pastes a ticket
  and asks to test it without naming a mode. Do NOT use when the user
  names a specific mode or stage ("run the docs pipeline", "retest",
  "walk me through", "ingest the results") — those skills trigger
  directly.
---

# QA Pipeline — dispatcher

One question, answered by evidence: *where in its QA lifecycle is this
ticket, and what is the next pipeline action?* This skill contains no
testing logic — it reads state, proposes, confirms, and hands off. The
invoked orchestrator's own rules then apply in full.

> **Tool names:** `getJiraIssue` / `searchJiraIssuesUsingJql` are
> Atlassian MCP connector tools; `list_suites` belongs to the QA
> Service connector (prefixes vary per install — match by tool name).

## Step 1 — Read the state

From the ticket key/URL (ask if the paste has none):
1. `getJiraIssue` — issuetype, status, summary.
2. Pipeline QA sub-task? `searchJiraIssuesUsingJql`:
   `parent = <KEY> AND issuetype = "QA sub-task"` (newest with the
   pipeline label wins).
3. On that sub-task, when it exists: a QA Service suite line? a
   code-phase status comment? a human summary? (The stage reports are
   local-only — Jira carries no archive since 0.33.0, so their absence
   on the ticket says nothing about whether the code phase ran; check
   the run folder and `list_test_runs` on the suite.)
4. Run folder: `<KEY>-walk-plan.md`, `<KEY>-walk-state.json`
   (a walk in progress), `<KEY>-walk-results.md`, `<KEY>-runsheet.xlsx`,
   `<KEY>-testdata.json`, stage reports, `<KEY>-recon.md` — local
   evidence of a run in flight.

**Where to find inputs:** `references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

## Step 2 — Propose the route

Rows are keyed in the order the evidence is trusted: run folder, then
the QA Service suite/run, then Jira (a Jira comment alone never decides).

| State observed (run folder → QA Service → Jira) | Proposed route |
|---|---|
| No run folder, no suite, no QA sub-task; ticket is a Story/Task (or Bug with real scope) | **Docs phase** — `qa-pipeline-docs` now; code phase afterwards in a FRESH chat (hand the user the exact command) |
| No run folder, no suite, no QA sub-task; ticket is a Bug | **Bug-fix mode** — `qa-pipeline-code`, cases derived from the ticket |
| Suite exists (or a QA sub-task carries its suite line); no `r<N>/` reports, no test run | **Code phase** — `qa-pipeline-code` (fresh chat recommended if this one already ran the docs phase) |
| `r<N>/` reports or a test run exist; newest summary ❌ or the user says the fix landed | **Retest mode** — `qa-pipeline-code` retest |
| `-walk-plan.md` present, no `-walk-results.md` (or a `-walk-state.json` in progress) | **Guided walk** — `qa-manual-walk` (resume when state exists) |
| Complete `-walk-results.md` not yet written back, or a filled sheet / TC-Result-Notes table in hand | **Ingestion** — `qa-manual-results` |
| A phase stopped mid-way — e.g. stage reports written but no test run recorded, or a run left `running` with no results comment | **Resume** — re-enter the same skill at the step that never ran; it records into the existing run, never a new one |
| Signals conflict or several apply | Present the observed state and the 2–3 plausible routes; the user picks |

Always show the evidence with the proposal, one line each ("QA sub-task
EP-55890 exists with suite line; no code-phase comments → code phase").
Never start any route without an explicit yes — the routes write to
tracker and test environments, and a wrong route on the right ticket
wastes a phase.

## Step 3 — Hand off

Invoke the chosen skill and follow it IN FULL — no shortcuts because
the dispatcher "already read" the ticket. Pass along what step 1
learned (the QA sub-task key, suite line, local artifacts) so the
orchestrator's step 0 doesn't re-discover it.

## Rules

- Read-only until the confirmation: the dispatcher itself never posts,
  never provisions, never edits.
- A Bug attached to a Story with an existing suite is usually a retest
  or bug-fix candidate against that suite's cases — say so rather than
  proposing a fresh docs run.
- If the user's message already names a mode, this skill should not
  have fired — hand over silently to the named skill.
