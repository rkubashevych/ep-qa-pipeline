---
name: qa-run-analyzer
description: >
  Post-run health check for the QA pipeline. Reads whatever pipeline
  output files are present (context, requirements, checklist,
  test-cases, pr-summary, code-review, web-testing) and reports how the
  run went: coverage/traceability gaps, weak inputs, signs a stage
  misbehaved, and a findings digest. Writes a short run report and a
  chat summary. Auto-called at the end of qa-pipeline-docs and
  qa-pipeline-code; also run on demand. Use when the user says "analyze
  the run", "run health check", "how did that run go", "what's worth
  fixing", or after any pipeline phase.
---

# QA Run Analyzer

> Recommended settings: **Sonnet . Effort: Medium . Extended thinking: Off**

A meta-review of the pipeline RUN, not the product. Read-only: it never
edits the pipeline files, only inspects them and writes its own report.

## Input

Reads from the working directory whichever of these exist (upload them
if the chat is new):
`<ISSUEKEY>-context.md`, `<ISSUEKEY>-requirements.md`,
`<ISSUEKEY>-checklist.md`, `<ISSUEKEY>-test-cases.md`,
`<ISSUEKEY>-pr-summary.md`, `<ISSUEKEY>-code-review.md`,
`<ISSUEKEY>-api-testing.md`, `<ISSUEKEY>-web-testing.md`.

Detect the phase from what is present:
- Docs phase = context/requirements/checklist/test-cases.
- Code phase = pr-summary/code-review/api-testing/web-testing.
Analyze whatever is there; do not require files from the other phase.

## What to check

Group every issue under one of three buckets so the fix is obvious:
- **Pipeline/skill** — the run or a stage misbehaved; fix the process
  or the skill.
- **Input** — the ticket/AC was weak; fix upstream (Jira/Confluence).
- **Product** — a real defect in the software; file/track a bug.

Severity: use 🔴 blocker, 🟡 warning, 🟢 ok.

### 1. Run / coverage health (Pipeline)
- Every REQ-N in the requirements file has >=1 checklist item; every
  behavioural requirement has >=1 test case. List orphans (REQ with no
  checks / no test cases).
- REQ-ID traceability is intact across requirements -> checklist ->
  test-cases -> code-review -> web-testing. Flag IDs that appear in one
  file but vanish in the next.
- Counts reconcile: code-review TC count == test-cases TC count;
  web-testing executed == QA+FAIL `[UI]` items;
  api-testing executed == QA+FAIL `[API]` items. Flag `[API]` items that
  are neither in api-testing nor routed out.
- BLOCKED test cases (web-testing / api-testing) and any
  empty/placeholder sections.

### 2. Input quality (Input)
- Missing-AC warning present (no Confluence acceptance criteria)?
- Any "(unresolved conflict)" left in requirements?
- "Requirements needing clarification" > 0 in test-cases stats?
- Grooming findings that were left as-is / skipped by the user.

### 3. Skill / process malfunctions (Pipeline/skill)
- A stage produced no output or a malformed file (missing the sections
  its template defines).
- Channel tags (`[UI]`/`[API]`/`[mobile]`/`[export/email]`) missing on
  checklist or test cases.
- A stage that clearly errored or was skipped in the chain.

### 4. Findings summary (Product)
- Docs phase: # requirements, # checks, # test cases, channel
  breakdown, # needing clarification.
- Code phase: code-review PASS/FAIL/QA/N/A; api-testing PASS/FAIL/
  FAIL CONFIRMED/FAIL REJECTED/PARTIAL/BLOCKED/QA plus any
  endpoint-mapping corrections (ticket endpoint != real endpoint);
  web-testing PASS/FAIL/FAIL CONFIRMED/FAIL REJECTED/BLOCKED/OBSERVATION;
  the list of confirmed bugs; what was routed to "Not executed here"
  (mobile/export-email); overall verdict.

## Output

Write `<ISSUEKEY>-run-report.md` per references/output-template.md, then
give a short chat summary: the run's health (🟢/🟡/🔴 per category) and
the top issues worth fixing, newest concern first. Keep the chat
message brief; the detail lives in the file.

If the run is clean, say so plainly — do not invent issues.
