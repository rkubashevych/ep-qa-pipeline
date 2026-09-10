---
name: qa-pipeline-code
description: >
  Orchestrator for the code + UI half of the QA pipeline (stages
  5-9, handing off to stage 10). Given a Story key, reads the test cases from the QA Service
  suite and derives the dev branches, then runs pr-summary, then
  code-review, then api-testing, then web-testing, then run-analyzer,
  records machine verdicts on a QA Service test run, builds the manual
  walk plan for what the machine could not settle, verifies the
  published state, and defers the human summary and the handback to
  qa-manual-results (stage 10). Also:
  retest mode ("retest <KEY>", "the fix landed") and bug-fix mode
  ("test the bugfix EP-1234" — Bug ticket, no docs phase needed).
  Auto-advances, pausing for the browser login, the Jira
  write confirmation, and the test-event authorisation before any
  fixture is provisioned. Use it when the user says "run the QA code
  pipeline", "run the QA checks", "review the PRs and test in the
  browser", "do code review and UI testing for a ticket". Run in a
  FRESH chat after qa-pipeline-docs.
---

# QA Pipeline -- Code & UI (stages 5-9, then hands off to stage 10)

> **Tool names:** bare names like `searchJiraIssuesUsingJql` are the
> **Atlassian MCP connector**; `get_suite` / `create_test_run` /
> `record_case_result` etc. are the **QA Service MCP connector**. The
> install-specific prefix varies — match by tool name.

> Recommended settings for the whole run: **Opus . Effort: High .
> Extended thinking: On**. Code review (stage 6) benefits most.

Runs the code-review and UI-testing half end to end. Each stage is a
real skill in this repo — this orchestrator sequences them. Start it
in a fresh chat (separate from the docs phase) for context health.
The detail this file used to carry lives in `references/`:
`run-modes.md` (bug-fix / resume / retest), `wave1-and-verification.md`
(why two waves, the closing checklist), `results-comment-template.md`,
`bug-report-template.md`, `jira-writing-style.md`.

## Input

- A Story key (e.g. `EP-44730`). Everything else is pulled from Jira.
- Optional: a per-task test host (alpha host) for the UI stage — use
  it if the QA sub-task names one.
- For stage 7: the `.env.qa-agents` variables and, for exhibitor-token
  cases, the per-event frontend host + an exhibitor login (per-event,
  not discoverable — must be supplied; must be in `ALLOWED_HOSTS`).
  api-testing pauses and asks if missing.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

**Sources of record:** `../qa-pipeline/references/sources-of-record.md`
— the register this phase builds at step 0 and the gate every finding
passes. Read it before stage 5.

**The per-case record:** `../qa-pipeline/references/test-runs.md` — the
QA Service test run step 6 creates and stage 10 closes (verdict mapping,
what stays `not_run` until the human round, retractions as re-records).
**Memory across rounds:** `../qa-pipeline/references/open-items-ledger.md`
— `<KEY>-open-items.md`, read here at step 0 in retest / bug-fix mode,
written by the analyzer and stage 9, closed only by stage 10.

## Step 0 — Gather inputs

**Session name:** suggest renaming this session to
`QA-pipeline <STORY> — code` (Claude Code: `/rename …`; Cowork: click
the chat title). One short reminder, then move on.

**Establish the run folder — before any other read or write**
(`../qa-pipeline/references/data-locations.md` → "The run folder";
`runs/` is `$EP_QA_HOME/runs/`, resolved per
`../qa-pipeline/references/environment.md` — nothing reachable →
PAUSE, never write into the plugin checkout). List `runs/<STORY>/r*`. **An explicit retest / "the fix landed" /
bug-fix request always creates `runs/<STORY>/r<max+1>/`** — the
signals below never override what the user asked for. Otherwise a
**resume** (newest folder's run report is `partial`, or its QA Service
run is `running` with `not_run` rows and no `-manual-results.md`)
continues in that folder; anything else is a first run in `r1`. Print one line: `Run folder: ~/.ep-qa/runs/EP-1234/r2
(retest 1)`. Every stage this orchestrator dispatches writes there and
nowhere else; the ledger is `runs/<STORY>/<STORY>-open-items.md`, the
docs-phase files are `runs/<STORY>/docs/`. Nothing is written to the
plugin checkout — a `<STORY>-*` file or a `runs/` folder appearing
there is a ❌ in the post-publish check (and fails `verify_plugin.py`).

**Environment check first.** Stages 5–7 need things Cowork usually
lacks: a repo clone or `BB_EMAIL`+`BB_API_TOKEN` (5–6) and API
credentials (7). All come from ONE file: `$EP_QA_HOME/.env.qa-agents`
(`../qa-pipeline/references/environment.md`). Before running anything,
check it is reachable and that `ALLOWED_HOSTS` is set; then take every
host this run will touch — the API host, the frontend host, the
ticket's alpha host — and check each against the list. Not reachable,
list missing, host not listed or production → say so NOW and PAUSE
(mount `~/.ep-qa`, or run this phase from Claude Code — MAINTAINERS
"Where to run each stage"); do not discover this mid-run at stage 5.
State the checked hosts in the same line as the run folder.

**QA Service connector is part of this check.** The suite is the only
copy of the cases outside this machine's run folder. Suite named + no
connector → PAUSE (enable it, or start from a session that has it) —
unless `runs/<STORY>/docs/<STORY>-test-cases.md` exists here: then say
the run uses the local copy and cannot write verdicts to a run. Never
discover this at extraction time.

**Build the source register — REQUIRED, in every mode.** Rules and the
table format: `../qa-pipeline/references/sources-of-record.md`. Fetch
each governing document once and write `<KEY>-sources.md`:

1. The **acceptance criteria** — the Confluence page linked from the
   story (`getJiraIssueRemoteIssueLinks`, then `getConfluencePage`),
   which the docs phase already itemised as the AC ledger (`AC-n` on
   the context bullets, `source:` on each REQ, `Covers:` on each case
   group). Every `Source:` line a stage writes for an AC clause carries
   that id. In bug-fix and retest mode fetch the page that governs the
   *feature*, reached via the parent story or the suite.
2. The **as-built documentation** — the page written from merged code
   (ExpoPlatform: space `FRON` for the front end, `DS` for the search
   service). It is rarely linked from the ticket; the reference file
   lists the four ways to find it. **This is not optional.** A brief
   says what should exist; only the as-built doc says what deliberately
   does not, and that is the document that stops a false defect. No such
   page → record the row as `NONE FOUND` and flag it in the run report.
3. The **implementing sub-task's acceptance criteria**, from the PR /
   branch derivation below.
4. The **ticket under test** itself — for a Bug, its reproduction steps
   and stated expected result.

Show the register in chat (one line per source) before dispatching
stage 5, and pass it to every stage. `task-context` (stage 1) does this
for the docs phase, but stage 1 does **not** run in retest or bug-fix
mode — which is why this step lives here and runs unconditionally.

**Same-session shortcut:** if `<STORY>-test-cases.md` is already in
the run folder, use it and skip the Jira read-back below. The source
register is still built — test cases never substitute for it.

Otherwise, using the Atlassian connector and the Story key:

1. **Test cases (and their Structural checks section).** Find the
   story's QA sub-task:
   `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype = "QA sub-task"` (prefer the newest
   with label `qa-pipeline` or a `[QA-PIPELINE]` summary).

   **Source order — suite first** (the docs phase posts no fenced copy
   of any file since 0.33.0; the suite is the record). Full rules:
   `../qa-pipeline-docs/references/qa-service-publish.md` → "Code phase
   — suite as the case source" and "Structural checks".
   - Sub-task names a **QA Service suite** + connector present →
     `get_suite` (then `get_test_case` per in-scope id when the response
     carries no `detail`) and rebuild `<STORY>-test-cases.md`: the
     authoritative copy. **Scope it to THIS run** — a suite is per
     FEATURE: execute only cases whose `detail.ticket` is `<STORY>`,
     plus team-added cases tracing to this run's requirements (flag
     them); pre-0.34 suites: the legacy tracker-line ids ("Legacy
     formats"). Never the whole suite. Report "suite holds N cases;
     M + S in scope" (M behavioural, S structural — both on the
     roster); local ids from `detail.pipelineId`.
   - Rebuild the **Structural checks** section from the `-STRUCT-`
     cases, the stableId on each line
     (`- [ ] REQ-N/struct-k · <PREFIX>-STRUCT-NN [UI] <check>`) — roster
     cases stage 8 reports by that id and step 6 records. No STRUCT
     cases (pre-0.33) → the legacy `(structural checks only)` block if
     present, else say so and skip them.
   - Rebuild **`<STORY>-requirements.md`** from the suite's
     requirements (`detail.pipelineId` → REQ-N) — without it the
     analyzer's traceability check cannot run in a fresh chat. No suite
     → the docs-phase copy in `runs/<STORY>/docs/`; neither → say once
     that upstream traceability cannot be re-verified.
   - No suite or no connector → **`runs/<STORY>/docs/`** on this
     machine (pre-0.33: legacy archive comments via
     `scripts/extract_archive.py`). Neither → offer: re-run
     `qa-pipeline-docs`, attach the files, or — Bug ticket — bug-fix
     mode.

   **Bug-fix mode (no docs phase)** — a standalone Bug ticket: the user
   says so, or step 0 finds issuetype Bug with no QA sub-task and no
   suite and ASKS "full pipeline or bug-fix mode?". Cases come from
   the bug ticket itself (2–4 mini cases, the ticket's own words as
   the expected result); they are published to the FEATURE's suite
   behind their own REQUIRED PAUSE before stage 5, so step 6 has a
   roster; stages 5–8 run unchanged; the manual round shrinks to a
   handful of cards or a one-line verdict. Full rules:
   `references/run-modes.md` → "Bug-fix mode".

   **QA Service reconciliation:** whenever the sub-task names a suite
   AND the connector is present, reconcile the extracted cases against
   the suite — the suite wins on divergence (cases may have been fixed
   in the web UI between phases); rules:
   `../qa-pipeline-docs/references/qa-service-publish.md` → "Code
   phase — suite as the case source". No suite line or no connector →
   the local docs-phase files are all there is; skip reconciliation and
   the later write-back and say so once in the final response — the
   run will leave no durable per-case record.

   **Resume mode** — the run folder first (reports, ledger,
   `-manual-results.md` which SUPERSEDES stage reports), then the QA
   Service run for verdicts, then PAUSE — a missing file on another
   machine means "cannot see it from here", not "never ran". **A stage
   is done only if its report is COMPLETE** (`Completeness:` header;
   partial → re-dispatch for the missing cases). Full rules:
   `references/run-modes.md` → "Resume mode".

   **Retest mode (the fix came back)** — the user says so, or the
   signals (newest summary ❌, `fail` / `known_defect` rows on the last
   run) make step 0 ASK "full run or retest?". Scope, confirmed by the
   user before stage 5: (1) every FAIL / FAIL CONFIRMED case, (2) the
   blast radius, (3) every case that never got a real verdict — built
   from the SUITE (`get_suite` diffed against the file; suite-only
   items are IN by default), with the ledger's open rows decided or
   carried in the same confirmation, written to
   `<STORY>-retest-scope.md` with where each old verdict was published.
   The scope binds every stage including stage 9; fixtures are FRESH;
   the retest is a NEW run on the same suite; retractions go where the
   old verdict was published. Full rules: `references/run-modes.md` →
   "Retest mode".

2. **Dev branches.** `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype in ("Backend sub-task","Frontend
   sub-task")`. Each dev sub-task's **key is its branch name** — use
   these for branch mode; no PR URLs needed. List them for the user
   before starting.
   - **Fallback — no dev sub-tasks** (Bugs, small Stories/Tasks carry
     the work on the main issue). Look for the PR/branch on the main
     issue, in order: (1) `getJiraIssueRemoteIssueLinks` on `<STORY>`
     — collect Bitbucket PR URLs; (2) scan the description and
     comments for PR URLs
     (`bitbucket.org/<workspace>/<repo>/pull-requests/<id>`);
     (3) try the issue key itself as the branch name in each repo
     (devs branch as `<KEY>` by convention — confirm existence via
     `git fetch` / the API); (4) still nothing → PAUSE and ask. Do not
     guess further. Whatever is found, list the PRs/branches (and
     where each was found) before starting.

## Split runs (Claude Code ↔ Cowork)

Stages 5–7 need repo/API creds (Claude Code); stage 8 needs a browser
backend — Playwright MCP by default (Claude Code too, one environment),
the Chrome extension as the fallback (Cowork). When the current
environment cannot run everything: run what it can, post the step-6
status line marked **PARTIAL** (name the pending stages), then start a
fresh chat in the other environment with the same Story key — resume
mode restores the finished reports from the run folder, and the last
environment posts the final status line as a NEW comment. What bridges
the two is `$EP_QA_HOME/runs/<STORY>/r<N>/` (Cowork mounts `~/.ep-qa`,
Claude Code has it on disk); if they cannot share it, the run cannot be
split — say so before starting.

## How it runs

Execute each stage by reading its `SKILL.md` and following it in full.

### Stage isolation (context health)

When subagents are available (Task tool in Claude Code, Agent tool in
Cowork), run stages 5–7 each as a SEPARATE subagent so a multi-PR
story does not exhaust the orchestrator's context:

- Give the subagent the stage's SKILL.md path, the input file paths,
  and the run folder. It follows the SKILL.md in full, writes
  the stage report, and returns only a short summary (<= 10 lines:
  counters, verdict, blockers) — never the report content.
- Resolve everything that could pause BEFORE dispatching (step 0's
  environment check). Subagents cannot ask the user — one that hits a
  missing input stops and RETURNS the blocker; the orchestrator asks,
  then re-dispatches.
- Stage 8 stays in the main conversation (browser + interactive
  pauses); the analyzer is light — run it inline.
- No subagents → run everything inline, and make sure stage 8 starts
  with enough context left.

1. **pr-summary (stage 5)** — on the derived branches (branch mode;
   the repository-scoped token is enough) or on the PR URLs the
   fallback found. Groups changes per sub-task (or per PR/branch).
   Produces `<STORY>-pr-summary.md`.

2. **code-review (stage 6)** — on the test-cases + pr-summary across
   all branches. Keys results by REQ-ID with a PR/branch column.
   Produces `<STORY>-code-review.md`.

3. **api-testing (stage 7)** — on the code-review + test-cases.
   Executes the `[API]` QA/FAIL cases via curl with `.env.qa-agents`
   credentials. **PAUSE** if values are missing or a host is not in
   `ALLOWED_HOSTS`. Produces `<STORY>-api-testing.md`.

4. **web-testing (stage 8)** — on the code-review + test-cases (its
   Structural checks section supplies the `[UI]` structural checks).
   Scope per the routing invariant
   (`../qa-run-analyzer/references/status-vocabulary.md`). Backend:
   Playwright MCP by default, Chrome extension only when its tools are
   absent (web-testing "Execution backends"); the report header names
   the one used. **PAUSE** (extension backend only) for browser login
   and any unknown navigation path. Produces `<STORY>-web-testing.md`
   and, for every FAIL, `<STORY>-web-evidence.md` §n (+ screenshots in
   `evidence/` where the backend can write them).

5. **qa-run-analyzer** — run automatically; writes
   `<STORY>-run-report.md`.
6. **Publish in two waves — only the first happens now.** Formats:
   **`references/results-comment-template.md`**; the reasoning and the
   closing checklist: **`references/wave1-and-verification.md`**.

   **Wave 1 — now, agents only.** The QA Service **test run** (created
   here, closed by stage 10 — `../qa-pipeline/references/test-runs.md`)
   and ONE status comment with no verdicts (`QA automated pass complete
   — N cases, M settled by machine, K for manual — QA Service run <id>
   open. Results published after the manual round.`) on the QA sub-task
   when the ticket has one, otherwise on the ticket under test. **That
   is all wave 1 writes to Jira.** No archive comments (retired 0.33.0
   — a fenced file dump on ANY ticket is a ❌), no prose summary of the
   reports, no description overwrite; the one sanctioned cross-ticket
   comment is stage 10's retraction (`test-runs.md` → "Retraction target
   rule").

   **Wave 2 — after `qa-manual-results` (stage 10), never now:** the
   human summary, the story note, the stage-verdict table, any request
   for a product decision. **The narrow exception:** a finding may
   publish in wave 1 only if ALL of — confirmed at RUNTIME, evidence
   attached, blocks the manual round. A code-read FAIL never qualifies.

   - **Count gate first.** Where a shell is available run
     `reconcile_counts.py <STORY>` (self-test first) and compare with
     each report's Scope/Statistics; any disagreement is fixed in the
     report BEFORE the preview — wrong numbers must not reach Jira, the
     suite or the human summary.
   - **Publication gate on the drafted comment BEFORE showing it**
     (`../qa-pipeline/references/sources-of-record.md` § 7): every line
     a reader would take as "this is broken" carries its register row
     and verbatim clause; no clause → `OBSERVATION (no source checked)`,
     phrased as a question or cut; a correctly labelled observation
     never reappears as a defect, not even inside a table; a defect owned
     by another ticket names that key. Right numbers with wrong labels is
     the failure this gate exists for (EP-56197, the `"True matches"`
     column).
   - **REQUIRED PAUSE / CONFIRM.** Show the status comment verbatim and
     its ticket, and — connector present — the run preview: title
     (`test-runs.md` modes), `env`, release (or `none`), roster count
     (= the step-0 scope count, or say why not), rows per verdict, rows
     left `not_run` for the human round, and — narrow exception only —
     each `fail` **by case** (recording a `fail` files the Jira defect
     there and then). One explicit yes covers Jira and QA Service.
   - **After the yes, in this order:** (1) `create_test_run` on the
     in-scope suite case ids; (2) `record_case_result` per row, `source:
     machine`, exactly per the `test-runs.md` mapping — FAIL / PARTIAL
     rows stay `not_run`, the run stays `running` for stage 10, a run
     that already exists for this pass (resume) is recorded into, never
     duplicated, lifecycle `status` never overwritten, no run lines in
     notes; (3) write `<STORY>-human-summary.md` per the template with
     `Status: DRAFT — awaiting stage 10` — stage 10's picture to
     reconcile against, NOT posted; (4) post the status comment
     (`addCommentToJiraIssue`), which quotes the run id from (1).
   - Connector absent → no run; say so in the final response. The
     final response names the report paths (`runs/<STORY>/r<N>/`) — the
     only copy of the evidence.

7. **Bug filing — after the manual round, not before.** A bug drafted
   from an automated verdict waits for the human to walk that case: it
   is a card in the walk plan and becomes a bug in stage 10 if it
   survives contact. The exception is step 6's, identically narrow.
   When filing does happen, ONE offer listing all the bugs; file only
   the ones the user confirms.
   - **Source gate before drafting** (`sources-of-record.md` § 7): the
     draft's Expected result is the register clause the build
     violates, checked against the **as-built document, not only the
     brief** — behaviour the as-built doc records as deliberate is not
     a defect. No clause in any source → SPEC-DEFECT, product question
     or `OBSERVATION (no source checked)`: retract the FAIL (a
     re-record, `test-runs.md` → Retractions) and raise it to the
     docs-phase owner. A "you may get pushed back on this" caveat in a
     draft IS this gate firing — stop. A closed ticket's precedent is
     context, not a source.
   - **Roster cases file through the run:** the per-case `fail` list in
     the step-6 preview IS the draft-and-yes; the note carries where /
     expected / actual + `Source:` + `Clause:`. The paths below are for
     findings with **no roster case** (unpromoted `RISK-CR-*` rows,
     human-confirmed observations).
   - **Preferred path (knowledge-base installed):** `/knowledge-base`
     dedup-searches and creates routed Jira bugs. **Default path:**
     draft per **`references/bug-report-template.md`**, search Jira for
     duplicates, show every draft, `createJiraIssue` only after an
     explicit yes per bug. Never file silently.

8. **Close the loop — hand the story back (wave 2, stage 10).** Never
   transition or reassign silently — show and confirm first. **Never
   ask a named person for a decision before the manual round** — nor
   before the source-fidelity check confirms the question is real: on
   one run, three of four "product decisions" were already answered by
   the AC page. Asking a colleague to decide what the spec already
   decides implies the spec is ambiguous when it is not.
   - **❌ FAIL or ⚠ PASS WITH GAPS with confirmed bugs:** the
     reassignment + "back to dev" offer happens at stage 10 with
     human-confirmed verdicts (narrow wave-1 exception: a
     runtime-confirmed, evidenced, blocking fault may be escalated
     now). Comment links the human summary and bug keys; transition
     per `../qa-pipeline-docs/references/publish-config.md` if
     configured.
   - **✅ PASS: the handback WAITS for the human.** Do NOT post the
     "QA passed" story note or apply the "QA done" transition here —
     both move to `qa-manual-results` step 4b. If the user explicitly
     wants a story note now, post the provisional variant — "✅
     Automated QA passed — manual verification pending"
     (results-comment-template.md) — with no transition. A
     machine-only PASS must never be dressed as final.
   - Transitions are optional: none configured → skip them and do
     only the reassignment + comment. Before any transition, verify it
     exists via `getTransitionsForJiraIssue`; if the configured name
     is absent, list the available ones and ask.

9. **Build the manual walk plan — `qa-manual-runsheet` (stage 9).**
   Every ticket is hand-tested after the machine finishes. Read its
   SKILL.md and follow it in full. It runs at the END of the phase
   because the plan's value is telling the human what is *left* (on a
   real ticket: 89 blind rows vs 11 + a few spot-checks), and stages
   7–8 create ad-hoc data clean fixtures must not collide with.
   - **REQUIRED PAUSE.** It creates accounts and entities on a live
     event: ask for the throwaway test event id and explicit
     authorisation first. Never an event with real client data; never
     a guessed event. The host passed `ALLOWED_HOSTS` at step 0; the
     event authorisation is the second, separate gate.
   - Feed it this run's verdict files and the step-6 run id. Outputs
     `<STORY>-walk-plan.md`, `-testdata.json`, `-testdata-notes.md`
     (`-runsheet.xlsx` only on request) — **live throwaway credentials,
     under `$EP_QA_HOME/runs/`, never in Jira**. Report counts: cards
     by kind, cases settled without a card, anything not provisionable.
   Skip only if the user says they are not hand-testing this ticket.

   **Post-publish verification — always the last action of the run**
   (`references/wave1-and-verification.md` → the list). The analyzer
   ran at step 5, BEFORE steps 6–9; verify the final state now: the
   write-back landed (`get_test_run` roster == scope, `progress`
   partition == the reports under the `test-runs.md` mapping,
   `executed_coverage` moved); every FAIL has a card, a bug key or a
   "not carried" line; exactly one wave-1 comment on the right ticket
   and nothing else (no dump, no early summary); every report on disk;
   walk-plan outputs exist and pass the voice check; everything under
   `runs/<STORY>/r<N>/`, nothing in the checkout. Append
   `## Post-publish verification` (✅/❌ per item) to
   `<STORY>-run-report.md`; a ❌ is a real finding — fix it or tell the
   user, never bury it.

10. **The human round — `qa-manual-walk` then `qa-manual-results`
    (stage 10, deferred).** It happens after this orchestrator finishes,
    often days later, in another chat: the tester says "walk me through
    <STORY>" and `qa-manual-walk` presents the plan one card at a time
    (records nothing; writes `<STORY>-walk-results.md`); then
    `qa-manual-results` joins by TC id, reconciles against the machine
    record, and on the tester's yes writes back with explicit
    retractions, posts the FIRST human-facing summary, files the
    surviving bugs and makes the handback offers. End THIS run by
    saying plainly: nothing human-facing has been published yet; the
    walk is next; stage 10's write-back is where the team hears the
    result.

## Between stages

- Keep chat output short: one line per hand-off. Each stage's own
  rules and templates apply unchanged.
- **Run clock:** stamp the wall clock at step 0 and after every
  stage/step; post exactly ONE line per boundary:
  `⏱ Stage <n>/<total> done — <name> · elapsed <E> min · ~<R> min left`.
  Budgets (minutes): step 0 8 · pr-summary 15 · code-review 30 ·
  api-testing 25 · web-testing 45 · analyzer 8 · run + publish 10 ·
  walk plan 30. `<R>` = unfinished budgets × the run's own pace
  (elapsed ÷ finished budgets, clamped 0.5–3), rounded to 5, with the
  `~`. Subtract user-waiting pauses (login, confirmations, event
  authorisation) — waiting is not pace. Retest / bug-fix: halve the
  scoped-down stages. No shell → skip the clock silently.
- **The orchestrator never asserts a product claim from its own
  observation.** A defect, a reclassification, a "this is actually
  fine" — every such statement comes from a stage skill under that
  stage's evidence rules, or is dispatched to one. On real runs the
  dominant error was the orchestrator narrating conclusions between
  stages from a glance.
- **Chat is a publication surface, and the gate applies to it.** Every
  finding presented as a defect carries `Source:` and `Clause:`; an
  `OBSERVATION (no source checked)` carries its label; never list
  unsourced observations in one numbered run with verified failures —
  equal presentation grants equal authority (three observations once
  went out as "issues 4, 5 and 6" beside two confirmed failures; the
  reports had labelled them, the chat summary lost the labels).

## Final response

Report: the report paths — **the only copy of the evidence**; the
machine verdict and confirmed bugs; what wave 1 posted and where (one
status comment, key + URL, nothing else) and that the human summary is
written but deliberately NOT posted; the QA Service run id with counts
per verdict and rows left `not_run` (or "no run — connector not
enabled" / "no run — no suite"); step-0 reconciliation changes; the
ledger's open-row count; bugs filed under the narrow exception, or that
filing waits for stage 10; the handoff performed or deferred. Reuse the
human-summary content rather than inventing a third format. Then, from
step 9: the walk-plan path, cards the tester will walk (by kind) vs
cases the machine settled, the reminder that the plan and testdata hold
live credentials, and the hand-off line: "walk me through <STORY>"
starts the session.
