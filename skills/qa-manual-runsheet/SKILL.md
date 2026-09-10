---
name: qa-manual-runsheet
description: >
  Stage 9 of task processing — the last automated step of
  qa-pipeline-code. Takes the test cases and the automated verdicts
  from stages 6-8, provisions and verifies fixture data on a throwaway
  test event, then builds the manual walk plan — plain-language cards
  grouped by login ("as <who>, do <this>, you should see <that>") with
  the machine's evidence kept backstage — that qa-manual-walk presents
  one card at a time. A run sheet (.xlsx) can be exported on request.
  Use it when the user says "prepare the manual tests", "build the walk
  plan", "make a run sheet", "prepare test data", "set up the data so I
  can just check the cases", or after the automated code-phase stages
  finish and before anyone tests by hand. Retest rounds reach it via
  qa-pipeline-code retest mode, scoped to the fix's blast radius;
  invoked bare on a story with prior artifacts it detects the prior run
  and asks, and it always provisions fresh fixtures. Do NOT use to run
  the session (qa-manual-walk) or to ingest results (qa-manual-results).
---

# QA Manual Run Sheet — fixtures and the walk plan

Turns finished test cases into something a person can actually execute:
the data already exists on the event, and each card says who to log in
as, what to do, and what you should see.

This stage exists because a test case and a runnable instruction are not
the same thing. "Call the public favourite-action endpoints and confirm
none returns the private favourites" is a valid test case and a useless
instruction — it names no account, no endpoint and no pass condition.

Since 0.31.0 the deliverable is the **walk plan**
(`references/walk-plan-format.md`), read by `qa-manual-walk` in a live
session; the spreadsheet (`references/runsheet-format.md`) is an
optional export generated from the plan. The reason is recorded in the
plan format's first section: the sheet had to carry everything in every
cell, and the tester could not concentrate on it. The plan keeps the
card human and moves the rigour backstage, where the agent applies it.

## Source of truth — read this before anything else

**The QA Service suite is the system of record for the cases.** The
automated stages regenerate their test-case file from it, and the suite
wins on divergence. Everything this stage produces is a *view* of that
suite. Consequences:

- **Read the cases from the suite** when one exists and the connector
  is available, exactly as `qa-pipeline-code` step 0 does. Fall back to
  `<ISSUEKEY>-test-cases.md` in the run folder only when it does not.
- **The walk plan (and any exported sheet) is never an input.** No
  automated stage reads it, and none ever should. It carries less
  detail than the machine needs by design, so treating it as a source
  would silently degrade every later run.
- **Corrections must go back to the suite.** When a tester discovers
  that an expected result is wrong, that a case needs a UI-only
  condition, or that a blocked reason was false, writing it only in the
  plan is *losing* it: the next run regenerates from the suite and
  repeats the mistake. Write it to the suite and note in the plan that
  you did. (Corrections found *during* the walk are collected by
  `qa-manual-walk` and applied by stage 10 under its confirm.)
- **Run outcomes belong on the pass's QA Service test run, never in
  `status`** (a lifecycle field) and — since 0.30.0 — no longer in
  `detail` notes either (`../qa-pipeline/references/test-runs.md`). This
  stage records nothing on the run itself: the machine verdicts were
  recorded at step 6, the human verdicts are recorded by stage 10 when
  the sheet comes back. What this stage may write to the suite is a case
  correction (above) and a `discrepancy:` note.

## Retest runs — detect, do not wait to be told

A retest is the common case, not the exception: every ticket that fails
comes back. **Never assume a bare invocation means a first run.** Before
provisioning anything, check for evidence of a prior run:

- `<ISSUEKEY>-testdata.json`, `<ISSUEKEY>-walk-plan.md`,
  `<ISSUEKEY>-walk-results.md` or `<ISSUEKEY>-runsheet.xlsx` exists in
  **any earlier `runs/<ISSUEKEY>/r*/` folder** (this pass's folder is
  empty by construction)
- a QA Service test run titled `<ISSUEKEY> …` exists for the suite
  (`list_test_runs`) **other than the one this pass's step 6 just
  created** (the orchestrator hands you its id — ignore it here) —
  an older run still `running` with `not_run` rows means the previous
  pass's manual round was never ingested; older suites may instead
  carry pre-0.30 run-outcome lines in case notes
- `<ISSUEKEY>-open-items.md` exists (the ledger only exists after a
  first round)
- the QA sub-task's newest human summary or manual-results comment is
  ❌ FAIL
- defects exist under the story

Any of these found → **PAUSE and ask: "prior run detected — full fresh
run, or retest?"** Never silently rebuild the full plan on top of a
finished run. On a real story the difference is 89 cards and 84 accounts
versus about 30 cards and a dozen.

When it is a retest:

- **Scope the plan.** Cards ONLY for the retest scope (provided by
  `qa-pipeline-code` retest mode, or ask for it): the failed cases,
  the other cases in the same REQ groups (the fix's blast radius), any
  case whose defect is marked fixed, and every case that never got a
  real verdict — blocked, amber, or skipped. Cases that passed on an
  unrelated path keep their verdict and get no card; say so in the
  final response. A retest plan is short by design — that is its
  value.
- **Fixtures are always fresh. This is not negotiable.** Prior
  fixtures are presumed contaminated for every counter / analytics /
  lead assertion: accumulated interactions make their baselines
  unreadable (a real run left a phantom like on one target and a
  counter stuck at 15 on another — no counter case can ever be judged
  against those again). Read the prior `testdata.json` only to know
  what exists and which accounts to RETIRE; provision new dedicated
  targets with verified zero baselines for anything numeric. Reuse a
  prior account only for stateless checks, after re-proving its login.
  Note in the testdata-notes file which prior fixtures were abandoned
  as contaminated, so cleanup can target them.
- **Carry the history into the card.** A card being retested carries
  the prior verdict, the defect key, and the date in its `retest:`
  backstage key, and the agent says so when the card comes up. A
  tester who cannot learn that a case failed last time cannot tell a
  fix from a fluke.
- **Ask which fix landed.** If the user has not said, ask. A retest
  scoped to defects that were not actually fixed wastes the whole run.

## Non-goals

- Not a test-case authoring tool. Cases come from `qa-test-cases`; this
  stage makes them executable, and reports back when one is wrong.
- Not a results store. The suite holds outcomes; the plan is a working
  surface.
- Not the session itself. Presenting the cards and collecting verdicts
  is `qa-manual-walk`; recording them is `qa-manual-results`.
- Not an input to `api-testing`, `web-testing` or either orchestrator.

## Input

1. The **QA Service suite** for the story, when one exists — primary.
   Otherwise `<ISSUEKEY>-test-cases.md` from the qa-test-cases skill.
2. `<ISSUEKEY>-checklist.md` — supplies the structural checks. Optional.
3. Any verdict files that already exist — `<ISSUEKEY>-code-review.md`,
   `-api-testing.md`, `-web-testing.md` — and the pass's QA Service
   test run when one exists. Optional; used to decide which cases are
   settled without a card and to fill each card's `machine:` key.
4. `$EP_QA_HOME/.env.qa-agents` for host and credentials
   (`../qa-pipeline/references/environment.md`) — and its
   `ALLOWED_HOSTS`, which the provisioning host must match.
5. **Whether this is a first run or a retest** — see "Retest runs"
   above. Detect it; ask when the evidence is ambiguous.
6. **A throwaway test event id, and explicit authorisation from the user
   to create and modify data on it.** This stage mutates a live
   environment. Never proceed without that authorisation, and never
   target an event that carries real client data.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

If the test-cases file is missing, ask for it. If the event id or the
authorisation is missing, PAUSE and ask — do not guess an event.

## Output

- `<ISSUEKEY>-testdata.json` — machine-readable record of every account
  and entity created, keyed so a script can map case → data.
- `<ISSUEKEY>-testdata-notes.md` — human log: what was created, what
  could not be, what behaved unexpectedly, what needs manual cleanup.
- `<ISSUEKEY>-walk-plan.md` — **the deliverable**: the cards, grouped
  into login sessions, each with its backstage block, plus the coverage
  map (format: **references/walk-plan-format.md**). Read by
  `qa-manual-walk`.
- **On request only** ("export the sheet", or a tester who will work
  from a file without the agent): `<ISSUEKEY>-runsheet.xlsx` generated
  **from the plan** by `build_runsheet_<ISSUEKEY>.py` (format:
  **references/runsheet-format.md**). Do = the card's Do; Expect = the
  card's You should see followed by the backstage lines a tester
  without an agent still needs (`say-first`, `wait`, `positive-control`,
  `how-to`, and for AGENT-RUNS the `run` line). The sheet is a
  rendering of the plan, never edited on its own.

## The six rules that make a card usable

These come from a real run where the sheet was technically complete and
still cost the tester hours. They apply to every card, and to the
exported sheet's rows. Follow them literally.

1. **One explicit "Log in as" per card.** Exactly one account, with
   email and password stated once in the session header the card
   belongs to. Not a role name, not an internal fixture key, not a list
   of three accounts for the tester to choose between. If a case
   genuinely needs two sessions, it is a card in the second account's
   session, or a numbered switch inside Do.

2. **Every card has a "You should see".** The pass condition, stated so
   a verdict can be reached without opening another file. A card
   without it cannot be judged, only performed.

3. **Name the surface, not the intent.** "Open Marketplace → Brands and
   click the star on any brand card", not "attempt to favourite a
   brand".

4. **Record the positive control on absence checks.** A card whose pass
   condition is "nothing appears" is worthless alone — it passes when
   the feature is broken and nothing was ever created. Pair it with the
   thing that proves the state existed, in the same sentence:
   "interactions list empty **and** the counter reads 1".

5. **Verify every blocked reason before writing it.** A wrong "blocked"
   is worse than no card: it removes a case from testing on a false
   premise. In one run, four cases were wrongly blocked on reasons that
   dissolved on a single check — a setting that did exist, a count
   surface that did exist, a brand that did exist. The probe goes in
   the card's `blocked:` key; `qa-manual-walk` re-probes it live.

6. **Never share a fixture across counter cases.** Anything that asserts
   on a number needs its own dedicated target with a verified zero
   baseline. Shared "main" fixtures accumulate interactions from other
   cases and make every counter assertion unreadable.

And the rule the sheet taught last: **the card says who, do, see — the
backstage says why.** No caveat, scope warning, machine verdict, HTTP
verb or harness line in the card body; every one of those has a
backstage key (`walk-plan-format.md` → Voice rules). A case that *is* a
request is an AGENT-RUNS card the agent executes, not a curl line the
tester pastes.

## Traps that produce false passes

Read **references/provisioning-rules.md** in full before provisioning.
It carries the environment-specific detail. The three that matter most:

- **How the data was created changes what the platform records.**
  Actions performed over the API frequently skip client-side tracking,
  so any case touching counters, leads, analytics or statistics must be
  exercised **through the UI** or it passes for the wrong reason. This
  is the single most expensive trap in this pipeline.
- **Analytics-backed surfaces lag.** Reading immediately after an action
  shows a clean result. Establish the lag for the surface before
  trusting any "nothing appeared" verdict, and put the required wait in
  the card's `wait:` and `say-first:` keys.
- **A flag named like state may be a capability.** Confirm what a field
  means before building assertions on it. Prefer what the UI renders
  over what an endpoint reports when the two can disagree.

## Workflow

### Step 1 — Read the cases and derive the data need

For each case extract: the roles involved and which one *acts*, the
target entities and their types, the precondition, and the pass
condition. Group cases that can share a fixture — but never counter
cases (rule 6).

### Step 2a — Select the manual set: minimum cards, full AC coverage

The machine runs ALL cases (stages 6–8) and the QA Service suite keeps
ALL cases — that never changes. The human walks a SELECTED set, because
a full hand-run of 90 cases costs a day and most of it re-proves what a
representative would prove. Build the selection with the same
test-design techniques that built the cases ("row" below = one card in
the plan, one row in an exported sheet):

1. **Must-walk (never reducible):** every case with no runtime-verified
   machine verdict — QA, FAIL claims, routed-in, unresolved BLOCKED,
   NOT EXECUTED — plus the VERIFY spot-checks (High-risk or
   code-reading-only machine PASSes), plus the `[core]` case of every
   behavioural REQ even when machine-settled. A machine-settled clean
   PASS on a Low/Medium-risk core case enters in short form
   (VERIFY-style row: the fastest action that would expose a wrong
   verdict), so the all-AC guarantee stays cheap.
2. **Reduce by technique, not by mood:** within the must-walk set, one
   representative per equivalence class; boundary rows only where the
   boundary is the point; a pairwise pick instead of a full combination
   sweep; and when several cases walk the same fixture through the same
   surface, ONE row carries them with a `Covers: TC-x, TC-y, …` note.
3. **Coverage gate — the floor under the reduction:** after selecting,
   map rows → REQ ids. Every behavioural REQ of THIS ticket must have
   a WALKED ROW — a machine verdict alone no longer covers a REQ. **In
   retest mode the floor applies to the scoped REQs only** — the fix's
   blast radius — never to REQs whose cases passed on an unrelated
   path in the previous round; re-walking those is the waste the
   retest scope exists to prevent. The
   REQ's `[core]` case is the default representative (short form where
   machine-settled at Low/Medium risk, full form otherwise). For cases
   from an older suite without `[core]` markers, pick a representative
   by the same technique logic, say so in the Coverage section, **and
   record each nomination as a `nomination` row in
   `<ISSUEKEY>-open-items.md`**
   (`../qa-pipeline/references/open-items-ledger.md`) — a nomination
   already in the ledger from an earlier round is reused, not re-chosen,
   so the same representative is walked every round. Print
   the map in the plan's Coverage section and the final response:
   "N cases → M cards, covering R/R requirements walked".
4. **Risk extras:** add rows for High-risk cases in the fix's blast
   radius even when machine-settled, and anything the QA sub-task's
   ⚠ SPECIAL ATTENTION block names.
5. **What's left out is named, not dropped:** unselected cases appear
   in the Coverage section as `settled (<status>, <source>)`.
   Stage 10 records those verdicts as machine-only — the summary's
   PARTIALLY VERIFIED wording already covers that honestly.

A card's verdict applies to every case in its `covers:` list unless the
tester singles one out — the walk names them when recording, and stage
10 expands the list on ingestion.

### Step 2 — Classify every case

- **READY** — data can be provisioned; the human can run it.
- **NEEDS FIXTURE** — requires something you cannot create (a differently
  configured event, an ownerless entity, a log-group grant). Say exactly
  what would unblock it and who can provide it.
- **ALREADY SETTLED** — an existing verdict file answers it with
  runtime-grade evidence (executed in stage 7/8 under the
  absence-check protocol) AND the case's risk is Low/Medium. Carry the
  verdict and its source so the human skips it.
- **VERIFY (spot-check)** — the machine has a PASS, but it is exactly
  the kind the creator's error model distrusts: a PASS on a
  `[risk: High]` requirement, or ANY PASS whose only evidence is code
  reading (code-review PASS, never executed). One SPOT-CHECK card:
  same who / do / see, trimmed to the fastest action that would expose
  a wrong PASS. Never mark these skipped — ~half of unverified machine
  PASSes are historically wrong, and the High-risk ones are where that
  hurts.
- **AGENT-RUNS** — READY, but the case is a request (an `[API]` case
  with no UI path, a harness line, anything with an HTTP verb). It gets
  a card the *agent* executes during the walk, with the tester supplying
  only the human-only input (a token from an email, a code from a
  phone). This is what keeps curl out of the human's hands: on EP-56998
  nine of eleven rows handed the tester a harness command.

Probe every NEEDS FIXTURE reason against the live system before
accepting it (rule 5).

### Step 3 — Provision

**First, the host:** the API host (and the event's frontend host, when
one is used) must match `ALLOWED_HOSTS` — `load-env.sh --host-allowed
HOST` — or this step PAUSES naming it. Production is refused even when
listed (`environment.md`). Then, with the event authorisation from the
orchestrator's pause in hand, create the accounts and entities. Per
rule 6 and the fresh-per-destructive-case rule in the references: any
case that mutates state a later case depends on gets its own account,
so cases can be run in any order and re-run individually. **Every
account gets its own random password** (`secrets.token_urlsafe`, never
a fixed string) and is recorded in `-testdata.json` with
`"throwaway": true` so stage 10 can retire it.

Set every attribute the cases depend on **explicitly** — consent flags,
names, categories, roles. Defaults are not neutral: a fixture that
silently defaults to the wrong consent state will invalidate cases
quietly.

### Step 4 — Verify each fixture, then verify the baseline

Read every account and entity back from the API. Confirm each login
actually authenticates and lands cleanly — no blocking profile-completion
dialog, no forced redirect. For every target used in a counter case,
record its zero baseline and read it **twice** so the figure is trusted.

Report the verification result honestly. A plan full of ids that do not
resolve is worse than no plan.

### Step 5 — Emit the walk plan

Per **references/walk-plan-format.md**. Group the cards into sessions
by login account, order each session the way the product presents its
surfaces (destructive cards last), and write every card in the human
voice: who, do, see — with everything else in the backstage block.
Before writing a card, apply the voice rules' test: could a colleague
who has never read the ticket do this and tell you pass or fail from
what they saw?

**Translation is the work of this step.** The test-cases file is
written for stages 6–8 and the count gate — `Pre:` / `Steps:` / `Exp:`,
`[data: …]`, channel tags, technique names, forbidden-word discipline.
That register is correct there and wrong on a card. Rewrite; do not
copy. The case id on the card is what keeps the two joined.

Then the coverage map. Then, **only if asked**, the exported sheet via
`build_runsheet_<ISSUEKEY>.py` (per **references/runsheet-format.md**),
rendered from the plan.

### Step 6 — Write findings back to the suite

Anything this stage *learned* about a case goes back to the QA Service
suite before you hand over, because the plan is not a source. **Batch
them into ONE preview and wait for a yes** — the suite is shared
production data (`qa-service-publish.md` → Preconditions), and the
walk routes the same kind of correction through stage 10's confirm:

- a blocked reason you probed and disproved
- an expected result that contradicts the documented behaviour
- a condition the case needs to be valid (UI-only, required wait,
  an instrument that cannot be trusted)
- a behaviour with no case covering it — create the case

Then note in the plan's header that the suite was updated, so the next
person knows the two agree.

### Step 7 — Self-check before handing over

- Every case in scope appears exactly once: on a card, in a `covers:`
  list, or as `settled` in the coverage map.
- Every card names exactly one login (via its session) and has a
  non-empty "You should see".
- **Voice check, every card:** no HTTP verb, endpoint, status code,
  curl line, DevTools recipe or file path outside an AGENT-RUNS card's
  `run:` key; no caveat, scope warning or machine verdict in the card
  body; Do ≤ 3 lines, You should see ≤ 2; title reads as a sentence.
- Every account and entity referenced resolves to `-testdata.json`.
- No blocked reason is unverified; every BLOCKED card's `blocked:` key
  names its probe.
- No absence-check card is missing its positive control.
- Every behavioural REQ has a card in the coverage map.
- **Secret scan before handover.** The emitted artifacts carry live
  credentials by design (`-testdata.json`, the walk plan, any exported
  runsheet, the generator script). Confirm every emitted file matches a
  `.gitignore` broad rule **and lives under `$EP_QA_HOME/runs/`, not in
  the plugin checkout** (`environment.md`); run a secret scan over the
  run folder (the `secret-leak-scan` skill or `gitleaks`). If any
  emitted artifact landed in the checkout, move it and say so — never
  leave it for the commit step to catch.

State the counts (cards by kind / settled without a card) and the
verification results in the final response.

## Rules

- All output in English.
- Keep chat output short: one line per stage.
- **Never touch production.** The host passed `ALLOWED_HOSTS`
  (`../qa-pipeline/references/environment.md`); confirm the target
  event before writing — two gates, both required.
- Any write outside the provisioning plan must be disclosed in the notes
  file, with what was changed and whether it was reverted.
- Do not favourite, connect, book or otherwise perform the actions the
  test cases ask the human to perform, unless a case's *precondition*
  requires that state to exist. Preconditions are yours; steps are
  theirs.
- Where a precondition must be created through the UI to be valid (see
  the tracking trap above), say so in the card rather than creating it
  over the API and leaving a fixture that cannot pass.

## Final response

Report: the output paths (testdata, notes, walk plan; the sheet only if
exported); cards by kind (WALK / SPOT-CHECK / AGENT-RUNS / DEVICE /
BLOCKED) and how many cases were settled without a card; the coverage
line ("N cases → M cards, R/R requirements walked"); the verification
results including how many logins were proven to work; anything that
could not be provisioned and what would unblock it; any live data left
in a mutated state that a human must clean up; and the one-line
hand-off: "walk me through <KEY>" starts the session.
