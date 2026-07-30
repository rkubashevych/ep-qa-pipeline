---
name: qa-manual-runsheet
description: >
  Stage 4.5 of task processing. Takes the test cases created by the
  qa-test-cases skill, provisions and verifies the fixture data on a
  throwaway test event, then produces a lean run sheet a human can work
  straight through — one explicit "Log in as" account, one action, one
  expected result per row.
  Use it when the user says "prepare the manual tests", "make a run
  sheet", "prepare test data", "set up the data so I can just check the
  cases", or after the docs phase (qa-pipeline-docs) finishes and before
  anyone starts testing by hand.
---

# QA Manual Run Sheet

Turns finished test cases into something a person can actually execute:
the data already exists on the event, and each row says who to log in
as, what to do, and what counts as a pass.

This stage exists because a test case and a runnable instruction are not
the same thing. "Call the public favourite-action endpoints and confirm
none returns the private favourites" is a valid test case and a useless
instruction — it names no account, no endpoint and no pass condition.

## Source of truth — read this before anything else

**The QA Service suite is the system of record for the cases.** The
automated stages regenerate their test-case file from it, and the suite
wins on divergence. Everything this stage produces is a *view* of that
suite.

Consequences that must be respected:

- **Read the cases from the suite** when a suite exists and the connector
  is available, exactly as `qa-pipeline-code` step 0 does. Fall back to
  `<ISSUEKEY>-test-cases.md` / the Jira archive only when it does not.
- **The run sheet is never an input.** No automated stage reads it, and
  none ever should. It carries less detail than the machine needs by
  design — one login, one action, one pass condition — so treating it as
  a source would silently degrade every later run.
- **Corrections must go back to the suite.** When a tester discovers that
  an expected result is wrong, that a case needs a UI-only condition, or
  that a blocked reason was false, writing it in the sheet is *losing*
  it: the next run regenerates from the suite and repeats the mistake.
  Write it to the suite and note in the sheet that you did.
- **Run outcomes belong in the case's `detail` notes, never in
  `status`.** `status` is a lifecycle field. Record the verdict, the
  date, whether it was human-executed or analysis-derived, and the
  defect key.

If a verdict already recorded in the suite is later found wrong, mark the
correction explicitly as superseding the earlier line — the notes are
append-only and two bare verdicts side by side tell a reader nothing.

## Non-goals

- Not a test-case authoring tool. Cases come from `qa-test-cases`; this
  stage makes them executable, and reports back when one is wrong.
- Not a results store. The suite holds outcomes; the sheet is a working
  surface.
- Not an input to `api-testing`, `web-testing` or either orchestrator.

## Input

1. The **QA Service suite** for the story, when one exists — primary.
   Otherwise `<ISSUEKEY>-test-cases.md` from the qa-test-cases skill.
2. `<ISSUEKEY>-checklist.md` — supplies the structural checks. Optional.
3. Any verdict files that already exist — `<ISSUEKEY>-code-review.md`,
   `-api-testing.md`, `-web-testing.md`. Optional; used to mark rows
   that are already settled so the human does not re-walk them.
4. `.env.qa-agents` (or the e2e project `.env`) for host and credentials.
5. **A throwaway test event id, and explicit authorisation from the user
   to create and modify data on it.** This stage mutates a live
   environment. Never proceed without that authorisation, and never
   target an event that carries real client data.

If the test-cases file is missing, ask for it. If the event id or the
authorisation is missing, PAUSE and ask — do not guess an event.

## Output

- `<ISSUEKEY>-testdata.json` — machine-readable record of every account
  and entity created, keyed so a script can map case → data.
- `<ISSUEKEY>-testdata-notes.md` — human log: what was created, what
  could not be, what behaved unexpectedly, what needs manual cleanup.
- `<ISSUEKEY>-runsheet.xlsx` — the run sheet (format:
  **references/runsheet-format.md**).
- `build_runsheet_<ISSUEKEY>.py` — the generator, so the sheet can be
  rebuilt when data changes instead of hand-patched.

## The six rules that make a run sheet usable

These come from a real run where the sheet was technically complete and
still cost the tester hours. Follow them literally.

1. **One explicit "Log in as" per row.** Exactly one account, with email
   and password inline. Not a role name, not an internal fixture key,
   not a list of three accounts for the tester to choose between. If a
   case genuinely needs two sessions, split it into two rows or put the
   second in the Do column as a numbered step.

2. **Every row has an Expect.** The pass condition, stated so a verdict
   can be reached without opening another file. A sheet without this
   column cannot be used to record results, only to look busy.

3. **Name the surface, not the intent.** "Open Marketplace → Brands and
   click the star on any brand card", not "attempt to favourite a
   brand".

4. **Record the positive control on absence checks.** A row whose pass
   condition is "nothing appears" is worthless alone — it passes when
   the feature is broken and nothing was ever created. Pair it with the
   thing that proves the state existed, e.g. "interactions list empty
   **and** the counter reads 1".

5. **Verify every blocked reason before writing it.** A wrong "blocked"
   is worse than no row: it removes a case from testing on a false
   premise. In one run, four cases were wrongly blocked on reasons that
   dissolved on a single check — a setting that did exist, a count
   surface that did exist, a brand that did exist.

6. **Never share a fixture across counter cases.** Anything that asserts
   on a number needs its own dedicated target with a verified zero
   baseline. Shared "main" fixtures accumulate interactions from other
   cases and make every counter assertion unreadable.

## Traps that produce false passes

Read **references/provisioning-rules.md** in full before provisioning.
It carries the environment-specific detail. The three that matter most:

- **How the data was created changes what the platform records.**
  Actions performed over the API frequently skip client-side tracking,
  so any case touching counters, leads, analytics or statistics must be
  exercised **through the UI** or it passes for the wrong reason. This
  is the single most expensive trap in this pipeline: it has produced
  false passes in the automated stages and in manual review.
- **Analytics-backed surfaces lag.** Reading immediately after an action
  shows a clean result. Establish the lag for the surface before
  trusting any "nothing appeared" verdict, and put the required wait in
  the row.
- **A flag named like state may be a capability.** Confirm what a field
  means before building assertions on it. Prefer what the UI renders
  over what an endpoint reports when the two can disagree.

## Workflow

### Step 1 — Read the cases and derive the data need

For each case extract: the roles involved and which one *acts*, the
target entities and their types, the precondition, and the pass
condition. Group cases that can share a fixture — but never counter
cases (rule 6).

### Step 2 — Classify every case

- **READY** — data can be provisioned; the human can run it.
- **NEEDS FIXTURE** — requires something you cannot create (a differently
  configured event, an ownerless entity, a log-group grant). Say exactly
  what would unblock it and who can provide it.
- **ALREADY SETTLED** — an existing verdict file already answers it.
  Carry the verdict and its source so the human skips it.

Probe every NEEDS FIXTURE reason against the live system before
accepting it (rule 5).

### Step 3 — Provision

Create the accounts and entities. Per rule 6 and the fresh-per-
destructive-case rule in the references: any case that mutates state a
later case depends on gets its own account, so cases can be run in any
order and re-run individually.

Set every attribute the cases depend on **explicitly** — consent flags,
names, categories, roles. Defaults are not neutral: a fixture that
silently defaults to the wrong consent state will invalidate cases
quietly.

### Step 4 — Verify each fixture, then verify the baseline

Read every account and entity back from the API. Confirm each login
actually authenticates and lands cleanly — no blocking profile-completion
dialog, no forced redirect. For every target used in a counter case,
record its zero baseline and read it **twice** so the figure is trusted.

Report the verification result honestly. A sheet full of ids that do not
resolve is worse than no sheet.

### Step 5 — Emit the run sheet

Per **references/runsheet-format.md**. Lead with the six columns the
tester works in; push accounts, entities, prior verdicts and caveats to
reference sheets they open only when something looks wrong.

### Step 6 — Write findings back to the suite

Anything this stage *learned* about a case goes back to the QA Service
suite before you hand over, because the sheet is not a source:

- a blocked reason you probed and disproved
- an expected result that contradicts the documented behaviour
- a condition the case needs to be valid (UI-only, required wait,
  an instrument that cannot be trusted)
- a behaviour with no case covering it — create the case

Then note in the sheet's reference material that the suite was updated,
so the next person knows the two agree.

### Step 7 — Self-check before handing over

- Every case in the test-cases file appears exactly once.
- Every READY row names exactly one login and has a non-empty Expect.
- Every account and entity referenced resolves to a row on the reference
  sheets.
- No blocked reason is unverified.
- No absence-check row is missing its positive control.
- **Secret scan before handover.** The emitted artifacts carry live
  credentials by design (`-testdata.json`, the runsheet, the generator
  script). Confirm every emitted file matches a `.gitignore` broad rule
  (`git status --short` shows none of them as untracked-unignored), and
  run a secret scan over the working tree (the `secret-leak-scan` skill
  or `gitleaks`). If any emitted artifact escapes the ignore rules,
  widen the pattern in `.gitignore` before handing over — never leave it
  for the commit step to catch.

State the counts (ready / needs fixture / already settled) and the
verification results in the final response.

## Rules

- All output in English.
- Keep chat output short: one line per stage.
- **Never touch production.** Confirm the target event before writing.
- Any write outside the provisioning plan must be disclosed in the notes
  file, with what was changed and whether it was reverted.
- Do not favourite, connect, book or otherwise perform the actions the
  test cases ask the human to perform, unless a case's *precondition*
  requires that state to exist. Preconditions are yours; steps are
  theirs.
- Where a precondition must be created through the UI to be valid (see
  the tracking trap above), say so in the row rather than creating it
  over the API and leaving a fixture that cannot pass.

## Final response

Report: the four output paths; ready / needs-fixture / already-settled
counts; the verification results including how many logins were proven
to work; anything that could not be provisioned and what would unblock
it; and any live data left in a mutated state that a human must clean up.
