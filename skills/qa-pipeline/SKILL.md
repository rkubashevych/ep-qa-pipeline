---
name: qa-pipeline
description: >
  The pipeline's front door. Give it a ticket (key, URL, or pasted) —
  it reads the ticket's type and pipeline state, proposes the right
  route, and on confirmation invokes it: refinement (questions +
  sizing) before estimation, docs phase for a fresh Story/Task, code
  phase when the docs are published, bug-fix mode for
  a standalone Bug, retest when a fix landed, the guided manual walk
  when the walk plan is built, manual-results ingestion when a filled
  sheet is back, the RC smoke for a "[Regression] RC release" ticket.
  Use when the user says "qa this ticket", "process
  EP-1234 for testing", "run the pipeline on this", or pastes a ticket
  and asks to test it without naming a mode. Do NOT use when the user
  names a specific mode or stage ("run the docs pipeline", "prepare
  for estimation", "retest", "walk me through", "ingest the results")
  — those skills trigger
  directly.
---

# QA Pipeline — dispatcher

One question, answered by evidence: *where in its QA lifecycle is this
ticket, and what is the next pipeline action?* This skill contains no
testing logic — it reads state, proposes, confirms, and hands off. The
invoked orchestrator's own rules then apply in full.

> **Tool names:** `getJiraIssue` / `searchJiraIssuesUsingJql` are
> Atlassian MCP connector tools; `search` / `list_test_runs` belong to the QA
> Service connector (prefixes vary per install — match by tool name).

## Step 1 — Read the state

From the ticket key/URL (ask if the paste has none):
1. `getJiraIssue` — issuetype, status, summary.
2. Pipeline QA sub-task? `searchJiraIssuesUsingJql`:
   `parent = <KEY> AND labels = "qa-pipeline"` (newest wins). **Match
   on the label, never on the issue type** — the type differs per
   project and a type filter returns silently empty in the wrong one:
   HV has a `QA sub-task` type, EP does not (verified 2026-09-17), so
   every EP pipeline sub-task is a plain `Sub-task`. The label is the
   one thing the pipeline sets itself, so it holds in both.
3. On that sub-task, when it exists: a QA Service suite line? a
   code-phase status comment? a human summary? (The stage reports are
   local-only — Jira carries no archive since 0.33.0, so their absence
   on the ticket says nothing about whether the code phase ran; check
   the run folder and `list_test_runs` on the suite. Find the suite with
   `search {query: <feature words or prefix>, kinds: ["suite"]}` — never
   `list_suites` first: it returns the whole product, ~190 KB. A run in
   status `completed` or `closed` is done; `running` with `stale: true`
   is a pass whose manual results were never ingested.)
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
| The ticket is an RC regression ticket (summary `[Regression] RC release …`, scope items linked in the description), or the user asks whether items are on RC | **RC smoke** — `qa-rc-smoke` on that ticket. Step 1's sub-task and suite reads do not apply to it; the mode reads each scope item's state itself. Never the docs phase: the ticket is a container, not a story |
| No suite; the user's words are about estimation, refinement or "what questions do we have" — or the ticket is a QA sub-task a human created (no pipeline label) and dev has not started | **Refinement** — `qa-refinement` on the parent Story: questions comment + QA sizing, no test cases; the docs phase follows once the answers are in |
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
- A QA sub-task given as input is not a docs-phase target on its own:
  route on its parent Story. A human-created one (no pipeline label)
  usually means estimation is next, so refinement is the default
  proposal. Carry its key forward so the docs phase can adopt it later.
