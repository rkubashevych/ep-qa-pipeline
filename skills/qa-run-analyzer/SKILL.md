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

> **Tool names:** `list_suites` / `get_suite` / `list_test_runs` /
> `get_test_run` / `executed_coverage` / `case_execution_history` are
> tools of the **QA Service MCP connector** (install-specific server
> prefix varies — match by tool name).

A meta-review of the pipeline RUN, not the product. Read-only toward the
pipeline files: it never edits a stage report, only inspects them and
writes its own report — plus the one file it maintains,
`<ISSUEKEY>-open-items.md` (`../qa-pipeline/references/open-items-ledger.md`),
where every finding the run did not settle is appended so the next round
inherits it instead of rediscovering it.

## Input

Reads whichever of these exist — resolved per
`../qa-pipeline/references/data-locations.md` (run folder first;
asking the user is the last resort):
`<ISSUEKEY>-context.md`, `<ISSUEKEY>-requirements.md`,
`<ISSUEKEY>-checklist.md`, `<ISSUEKEY>-test-cases.md`,
`<ISSUEKEY>-pr-summary.md`, `<ISSUEKEY>-code-review.md`,
`<ISSUEKEY>-api-testing.md`, `<ISSUEKEY>-web-testing.md`,
`<ISSUEKEY>-web-evidence.md` (the FAIL evidence sections § 5 checks),
`<ISSUEKEY>-sources.md` (the source register § 7 checks against),
`<ISSUEKEY>-recon.md`,
`<ISSUEKEY>-walk-plan.md` (stage 9's plan — for the voice check and
the coverage map), `<ISSUEKEY>-walk-results.md` (the walk's verdicts),
`<ISSUEKEY>-manual-results.md`,
`<ISSUEKEY>-remaining-cases-triage.md`, and any tester results table
(`<ISSUEKEY>-preserved-entries.tsv` or similar TC/Result/Notes file).
The last four carry post-publication corrections: when present, they
are MORE current than the stage reports — a stage-report PASS
contradicted there is a retracted verdict, not a pass. **Match them to
the round first:** a walk-results or manual-results file whose `Run:`
line names an earlier run is a stale artefact (EP-56197 r4 open-items
#24), not this round's correction — flag it 🟡 and do not read it as
current.

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
- Recon usage: when open questions reached the ticket, flag 🟡 any
  BEHAVIOUR-class question posted while env access existed and no
  `<KEY>-recon.md` was produced — an observable fact was asked of a
  human. A recon answer that changed a case's premise without the
  requirement being updated is 🔴 (same discipline as any source).
- **The AC→REQ seam** (the only unguarded end of the chain): when
  `<KEY>-context.md` is present, every numbered/bulleted item in its
  Requirements and "Additional requirements (from comments)" sections
  maps to a REQ-N in the requirements file (grooming numbers them in
  order of appearance, so this is a count + ordering comparison). An
  AC item with no REQ is 🔴 — the whole downstream coverage guarantee
  is anchored on this seam.
- REQ-ID traceability is intact across requirements -> checklist ->
  test-cases -> code-review -> web-testing. Flag IDs that appear in one
  file but vanish in the next.
- Core marker integrity: every behavioural requirement has exactly ONE
  test case marked `[core]` on its heading — 🔴 on zero or multiple
  (structural requirements have none; `reconcile_counts.py` prints the
  core count). When a walk plan exists for the ticket, every
  behavioural REQ maps to a card in its Coverage section — a
  behavioural REQ line reading machine-only is 🔴 (coverage gate
  regression).
- Depth conformance (advisory): a High-risk REQ group whose `Applied
  techniques:` line names no extended technique (3-value BVA, Decision
  Table, invalid transitions, Pairwise) and gives no reason is 🟡.
- Counts reconcile (where a shell is available, run
  `scripts/reconcile_counts.py --selftest` first — if the self-test
  fails, do NOT trust the script: recount by hand and raise a 🔴
  [Pipeline] finding. When it passes, run
  `scripts/reconcile_counts.py <ISSUEKEY>` from this skill's folder and
  verify its ID sets / status counts instead of recounting by hand —
  you still judge WHY a gap exists. Note: `source PASS(code)=N` is a
  source-marker tally, not a verdict count; range rows are expanded;
  `RISK-*` ids appear as "ids NOT in test-cases" — that is expected for
  risk-chasing rows, judge them, don't suppress them):
  code-review TC count == test-cases TC count;
  web-testing executed == QA+FAIL `[UI]` items + routed-in cases
  (api-testing's "Route to web-testing" + code-review `RE-ROUTE [UI]`);
  api-testing executed == QA+FAIL `[API]` items minus those it routed
  to web-testing. Flag `[API]` items that
  are neither in api-testing nor routed out. Do not "certify" the
  routing by arithmetic alone — if a case's hazard (from code-review
  findings) lives on a surface its channel never touched, flag it 🔴
  even when the counts balance.
- Structural checklist items (`[UI]` presence/type/label checks with
  no test case) appear in web-testing's "Structural checks" section —
  as executed or explicitly "not visited". Flag structural checks
  that are neither there nor explained by a Notes line.
- BLOCKED test cases (web-testing / api-testing) and any
  empty/placeholder sections.
- Completeness integrity: 🔴 when a report whose `Completeness:`
  header says `partial` (or that lacks the header AND has internal
  disagreement) feeds the run's final verdict without its missing
  cases being named in the human summary; 🔴 when any single report's
  Scope and Statistics totals disagree with each other (a real report
  shipped Scope 60 vs Statistics 62 and was resumed as "done").
- Unmapped changes: if code-review's "Unmapped changes" section is
  non-empty, surface each entry as 🟡 "PR behaviour with no covering
  case — scope creep or missing requirement; decide which". If the
  section is absent entirely (not even "None"), flag 🟡 that the
  reverse gap check did not run.
- Blast radius: if the pr-summary's "Shared / high blast-radius files"
  section is non-empty, surface it as 🟡 with a one-line note per file
  ("shared file X changed — flows outside this ticket may be affected;
  not covered by this ticket-scoped run"). This is a visibility flag
  for regression risk, not a failure of the run.

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

### 4. QA Service sync (Pipeline) — only when the connector is present

Skip this section entirely (and say so in one line) when the QA
Service MCP tools are not in the session, or when the user declined
publishing for this run — record the reason and treat it as a normal
outcome, never a gap or a 🔴. Otherwise, locate the
ticket's suite (`list_suites` match on the story / the `QA Service
suite:` line in the QA sub-task description) and report ONE of:

- 🟢 **in sync** — suite exists; **this ticket's** requirements
  (`sources` with `kind: jira, label: <KEY>`) and cases
  (`detail.ticket = <KEY>`) match the requirements/test-cases files by
  count and by `detail.pipelineId` (compare via `get_suite`; a
  per-feature suite also holds other tickets' items — never count
  those; account for deliberately skipped duplicates listed in the
  publish preview). Pre-0.34 suites carry no markers: fall back to the
  legacy tracker-line ids. **`-STRUCT-` cases are expected extras**
  (0.33.0): their count must equal the checklist's structural `[UI]`
  checks, not appear in the test-cases file — S structural cases
  beyond N test cases is in sync; S ≠ the checklist's count is the
  mismatch below.
- 🟡 **archive posted** — any fenced `File: <name>` block found in a
  comment written by this round on any ticket. Archives were retired
  in 0.33.0; name the comment so it can be deleted.
- 🟢 **not published yet** — no suite found AND this analyzer run is
  inside the docs orchestrator (publish is its step 6, which runs
  after this check — expected, not a failure).
- 🔴 **publish incomplete / mismatch** — suite exists but counts or
  IDs diverge from the files: list the missing/extra stableIds.
- **The run** (`../qa-pipeline/references/test-runs.md`) — code phase,
  when run after step 6 (on-demand, or a later round's step 0; in the
  orchestrated flow this analyzer runs BEFORE step 6, so the
  orchestrator's **post-publish verification** does this check there):
  `list_test_runs` on the suite, find this pass's run by title.
  - 🔴 **no run** — verdicts exist in stage reports and none reached
    the system of record; every "still stands" statement in this
    ticket's history is about markdown files (EP-53978: five passes,
    `verified: 0`).
  - 🔴 **partition mismatch** — `get_test_run` `progress` does not
    match the stage statistics under the mapping table (`pass` = PASS +
    FAIL REJECTED, `blocked`, `skipped` = NOT EXECUTED + NOT-TESTABLE +
    SPEC-DEFECT, `known_defect` = keyed FAIL CONFIRMED, `not_run` = the
    FAIL / PARTIAL rows awaiting the human), or roster count ≠ scope.
  - 🔴 **machine `fail` outside the narrow exception** — a `fail`
    recorded with `source: machine` whose case is not runtime-confirmed
    + evidenced + blocking: it filed a Jira defect before the human
    round (`run_defects` shows the key).
  - 🟡 **SPEC-DEFECT as `known_defect`**, or a human-executed row with
    `source: machine`, or a machine verdict with a person as principal
    — the two mapping errors the 2026-09-02 off-book run made.
  - 🟡 **stale run** — status `running` (`stale: true`) with
    `not_run` rows and no `<KEY>-manual-results.md`: the manual round
    was never ingested; the ticket's verdicts are still provisional.
    Same finding as §5's "manual results never ingested", seen from the
    service side.
  - `executed_coverage(suiteId[, releaseId])` is reported in the
    findings summary as two numbers — machine and manual — never one
    percentage.
- 🔴 **zeroed status buckets** — every case-status bucket reads 0
  against a non-zero total: the cases were written with a `status`
  outside `planned/implemented/partial/deferred/na` (e.g. `draft`).
  Fixable with a re-`edit_test_case` pass, not a re-publish.
- 🔴 **collapsed requirement kinds** — 0 rules AND 0 invariants AND 0
  risks among the suite's requirements: everything was filed as `fr`.
  Fixable in place with `edit_requirement` (`kind` + corrected
  `stableId`, which rewrites references).
- 🔴 **zeroed level table** — `stats.byLevel` sums to 0 against a
  non-zero case total: the cases were written without the `levels` code
  array (`AE`/`E2E`/`M`/`U`/`I`/`C`…). Those cases are also invisible to
  the implement workflow. Fixable with a re-`edit_test_case` pass.
- 🟡 **empty trace graph** — `traceLinks` is `[]` while cases carry
  `traceability`: the links never materialized; re-sending
  `traceability` on a case rebuilds the suite's edges.
- 🟡 **bare suite header** — no `summary` / `owner` / `status` /
  `lastReviewed` on the suite. Fixable with `edit_suite`.

This is the independent check on the QA Service publish — the publish
step verifies itself, but this skill re-checks it with fresh
instructions in a later stage/chat, so a silently skipped or partial
publish surfaces here.

### 5. Evidence quality (Pipeline) — can the verdicts be believed?

Audit against `../api-testing/references/absence-check-protocol.md`:

- 🔴 any absence-check PASS (in api-testing or web-testing) with no
  positive control recorded on the same surface in this run.
- 🔴 any PASS/PARTIAL on an instrumented-surface assertion (counter /
  lead / analytics / statistics / notification / dashboard) whose
  precondition provenance is API-created or unstated.
- 🔴 the same surface cited as conclusive evidence in one case and
  dismissed as unmeasurable/lagging in another case of the same run
  (one run carried nine PASSes and one BLOCKED on the same
  "No data to show" read — those cannot both be right).
- 🟡 any absence verdict from a single immediate read with no second
  read after the measured ingestion lag.
- 🔴 a web-testing FAIL / FAIL CONFIRMED with neither a
  `<KEY>-web-evidence.md §n` reading nor a screenshot in
  `runs/<KEY>/r<N>/evidence/` — a claim, not a verdict. A `§n` reading
  alone is compliant (the Playwright backend cannot always write the
  file — `playwright-executor.md` → Evidence); a screenshot alone is
  compliant on the extension backend.
- 🟡 routing integrity: every case in api-testing's "Route to
  web-testing" section and every code-review `RE-ROUTE [UI]` case
  appears in web-testing's Results (or its Not-executed-here with a
  reason). A routed case that vanished is a coverage hole, not a pass.
- 🔴 retraction integrity: any case whose manual result / triage entry
  contradicts a published verdict and whose roster row was not
  re-recorded (`get_test_run` — the row still carries the old verdict
  and no later row has `supersedesId` pointing at it), or whose old
  verdict reached a Jira comment on some ticket and that ticket carries
  no retraction comment (`test-runs.md` → "Retraction target rule").
  The record is asserting something the run's own artifacts disprove —
  flag it until `qa-manual-results` has been run.
- 🟡 manual results never ingested: stage-9 outputs exist for this
  ticket (`<KEY>-walk-plan.md` / `<KEY>-runsheet.xlsx` / testdata
  files, or the run report says stage 9 ran) but no
  `<KEY>-manual-results.md` exists and no manual-results comment is on
  the QA sub-task. A `<KEY>-walk-state.json` with no results file is a
  walk stopped mid-way — say so ("walk in progress, N of M cards
  answered, nothing recorded"). The ticket's verdicts are still
  PROVISIONAL however old they are — say so, never let silence read as
  "verified".
- 🟡 walk-plan voice: a card body in `<KEY>-walk-plan.md` carries an
  HTTP verb, an endpoint, a status code, a curl line or a file path
  outside an AGENT-RUNS card's `run:` key, or a caveat / scope warning
  / machine verdict outside its backstage block
  (`qa-manual-runsheet/references/walk-plan-format.md` → Voice rules).
  The plan is unreadable to the person it is for; name the cards.
- 🟡 source mislabel in the walk: a `machine (witnessed)` row of
  `<KEY>-walk-results.md` recorded as `source: manual` on the run (or
  the reverse) — the 0.30.0 honesty rule, checked from the walk side.

### 6. Findings summary (Product)
- Docs phase: # requirements, # checks, # test cases, channel
  breakdown, # needing clarification.
- Code phase: code-review PASS/FAIL/QA/RE-ROUTE/N/A; api-testing PASS/FAIL/
  FAIL CONFIRMED/FAIL REJECTED/PARTIAL/BLOCKED/NOT-TESTABLE (older
  reports may use QA for this) plus NOT-TESTABLE (instrumentation)
  routed cases and any
  endpoint-mapping corrections (ticket endpoint != real endpoint);
  web-testing PASS/FAIL/FAIL CONFIRMED/FAIL REJECTED/BLOCKED/OBSERVATION;
  the list of confirmed bugs; what was routed to "Not executed here"
  (mobile/export-email); overall verdict.

### 7. Source fidelity (Input) — is the premise true, not just consistent?

Every other check in this skill is a CONSISTENCY check: do the counts
agree, is traceability intact, does each case map to a requirement.
Consistency cannot detect a wrong premise propagated uniformly — it is
the one property such an error preserves. This dimension is the only
one that looks outward.

For every FAIL / FAIL CONFIRMED, and every requirement marked High
risk:
- does the requirement's `source` name a SINGLE document containing the
  whole statement? A source string joining two documents with "and" is
  a finding — flag it and name the clause that may not be covered.
- did any stage report a verdict against a clause absent from the
  implementing sub-task's acceptance criteria?
- do any two requirements in the suite fail to be jointly satisfiable?

Flag 🔴 when a published FAIL rests on a clause found in only one of
several cited sources. That is a retraction waiting to happen, and it
is cheaper to find here than after the bug is filed.

**The register.** The code phase builds `<KEY>-sources.md` at step 0
(`../qa-pipeline/references/sources-of-record.md`). Check it:

- 🔴 **no register at all** — the run produced verdicts against no
  source of record. Every FAIL in it is provisional in a way the
  reports do not say.
- 🔴 **no as-built document row** (and no `NONE FOUND` row recording
  that it was looked for). The brief says what should exist; only the
  as-built page says what deliberately does not. Missing it is how a
  documented-as-designed behaviour reaches the bug-drafting step — the
  incident that created this check (EP-56133, 2026-09-07: `groups`
  renders nowhere, and the as-built FE doc names `groups` as its own
  example of a type the front end does not render).
- 🔴 **any FAIL / FAIL CONFIRMED / `RISK-CR-*` row without a
  `Source:` + `Clause:` pair.** Count them; name them.
- 🟡 **any `OBSERVATION (no source checked)` presented as a defect** —
  in a defect list, a bug draft, a run-sheet row phrased as a fault, or
  the human summary's confirmed-bugs section. The status is correct and
  its placement is not.
- 🟡 **a defect resting on a precedent ticket instead of a clause.**
  A closed ticket shows how a similar case was ruled; it is not a
  source of record.

### 8. Carried items (Pipeline) — what earlier rounds left open

Rules and format: `../qa-pipeline/references/open-items-ledger.md`.
Read `runs/<ISSUEKEY>/<ISSUEKEY>-open-items.md` (per ticket, one level
above this round's `r<N>/` folder; legacy tickets: the repo root).
Then:

- 🔴 **carried item** — any open row (`Closed = —`) whose `First seen`
  is two or more rounds before this one and whose `Decision` is `—`.
  Name the row and its owner. When its class is `[Pipeline]`, this 🔴
  is what MAINTAINERS step 1 requires a CHANGELOG answer to.
- 🟡 **ledger missing on a retest** — this is a retest / bug-fix round
  (a prior run report, scope file or QA Service run exists for the key)
  and there is no ledger: the round started without the previous round's
  memory. (On EP-56197 four items were "carried a third round" with
  nothing recording that they had been carried at all.)
- **Write the ledger** — the one file this skill maintains. For each
  🔴/🟡 of this report that the run did not settle (unmapped changes
  awaiting a decision, risk rows carried without a verdict, findings
  with no case / requirement / bug key, suite-vs-file divergences
  awaiting an in/out ruling, unanswered open questions the code phase
  depends on, defects owned by another ticket this close depends on):
  update `Last seen` on the matching row, or append a row with
  `First seen` = this round. Never fill `Decision` or `Closed` — stage
  10 owns those. Product verdicts do not go here (the run holds them);
  items with their own bug key do not either (Jira holds them).

## Output

Write `<ISSUEKEY>-run-report.md` per references/output-template.md, then
give a chat summary in the exact shape of the **"Chat summary format"**
section of that template (≤10 lines: health line, top-3 issues, one
counters line). The detail lives in the file, not the chat.

If the run is clean, say so plainly — do not invent issues.

