---
name: qa-pipeline
description: >
  The pipeline's front door. Give it a ticket (key, URL, or pasted) —
  it reads the ticket's type and pipeline state, proposes the right
  route, and on confirmation invokes it: docs phase for a fresh
  Story/Task, code phase when the docs are published, bug-fix mode for
  a standalone Bug, retest when a fix landed, manual-results ingestion
  when the run sheet is back. Use when the user says "qa this ticket",
  "process EP-1234 for testing", "run the pipeline on this", or pastes
  a ticket and asks to test it without naming a mode. Do NOT use when
  the user names a specific mode or stage ("run the docs pipeline",
  "retest", "ingest the results") — those skills trigger directly.
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
3. On that sub-task, when it exists: a QA Service suite line? code-phase
   archive/status comments? a manual-results comment?
4. Working directory: `<KEY>-runsheet.xlsx`, `<KEY>-testdata.json`,
   stage reports, `<KEY>-recon.md` — local evidence of a run in flight.

## Step 2 — Propose the route

| State observed | Proposed route |
|---|---|
| Story/Task (or Bug with real scope), no QA sub-task, no suite | **Docs phase** — `qa-pipeline-docs` now; code phase afterwards in a FRESH chat (hand the user the exact command) |
| Bug, no QA sub-task, no suite | **Bug-fix mode** — `qa-pipeline-code`, cases derived from the ticket |
| QA sub-task/suite exists, no code-phase results | **Code phase** — `qa-pipeline-code` (fresh chat recommended if this one already ran the docs phase) |
| Code-phase results exist, newest summary ❌ or user says the fix landed | **Retest mode** — `qa-pipeline-code` retest |
| Run sheet emitted, user holds results / filled sheet | **Ingestion** — `qa-manual-results` |
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
