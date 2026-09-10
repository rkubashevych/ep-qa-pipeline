---
name: qa-pipeline-code
description: >
  Orchestrator for the code + UI half of the QA pipeline (stages
  5-10). Given a Story key, reads the test cases from the QA Service
  suite and derives the dev branches, then runs pr-summary, then
  code-review, then api-testing, then web-testing, then run-analyzer,
  records machine verdicts on a QA Service test run (human summary
  follows at stage 10), builds the manual walk plan so a human can walk what
  the machine could not settle, verifies the published state, and
  defers the final handback to qa-manual-results (stage 10). Also:
  retest mode ("retest <KEY>", "the fix landed") and bug-fix mode
  ("test the bugfix EP-1234" — Bug ticket, no docs phase needed).
  Auto-advances, pausing for the browser login, the Jira
  write confirmation, and the test-event authorisation before any
  fixture is provisioned. Use it when the user says "run the QA code
  pipeline", "review the PRs and test in the browser", "do code review
  and UI testing for a ticket". Run in a FRESH chat after
  qa-pipeline-docs.
---

# QA Pipeline -- Code & UI (stages 5-10)

> **Tool names:** bare names like `searchJiraIssuesUsingJql` /
> `addCommentToJiraIssue` / `getTransitionsForJiraIssue` (here and in
> this skill's references) are tools of the **Atlassian MCP
> connector**; `get_suite` / `get_test_case` / `create_test_run` /
> `record_case_result` etc. belong to the **QA Service MCP
> connector**. The install-specific
> server prefix varies — match by tool name on the server that
> provides it.

> Recommended settings for the whole run: **Opus . Effort: High .
> Extended thinking: On**. Code review (stage 6) benefits most.

Runs the code-review and UI-testing half end to end. Each stage is a
real skill in this repo — this orchestrator sequences them. Start it
in a fresh chat (separate from the docs phase) for context health.

## Input

- A Story key (e.g. `EP-44730`). Everything else is pulled from Jira.
- Optional: a per-task test host (alpha host) for the UI stage — use
  it if the QA sub-task names one.
- For stage 7: the e2e `.env` variables and, for exhibitor-token
  cases, the per-event frontend host + an exhibitor login (per-event,
  not discoverable — must be supplied). api-testing pauses and asks if
  missing.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

**Sources of record:** `../qa-pipeline/references/sources-of-record.md`
— the register this phase builds at step 0 and the gate every finding
passes. Read it before stage 5. The code phase used to read no spec at
all; that is how a documented-as-designed behaviour reached the point of
being filed as a Bug.

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
(`../qa-pipeline/references/data-locations.md` → "The run folder").
List `runs/<STORY>/r*`. A **resume** (newest folder's run report is
`partial`, or its QA Service run is `running` with `not_run` rows and
no `-manual-results.md`) continues in that folder. Anything else —
first run, retest mode, bug-fix mode, "the fix landed" — creates
`runs/<STORY>/r<max+1>/`. Print one line: `Run folder: runs/EP-1234/r2
(retest 1)`. Every stage this orchestrator dispatches writes there and
nowhere else; the ledger is `runs/<STORY>/<STORY>-open-items.md`, the
docs-phase files are `runs/<STORY>/docs/`. Nothing is written to the
repo root — a `<STORY>-*` file appearing there is a ❌ in the
post-publish check.

**Environment check first.** Stages 5–7 need things Cowork usually
lacks: a repo clone or `BB_EMAIL`+`BB_API_TOKEN` (5–6) and API
credentials (7). All can come from ONE file: `.env.qa-agents` in the
mounted qa-pipeline-skill repo (preferred), falling back to the e2e
`.env` / env vars. Before running anything, check they are reachable.
If not, say so NOW and ask the user to mount the folder or run this
phase from Claude Code (MAINTAINERS "Where to run each stage") — do
not discover this mid-run at stage 5.

**QA Service connector is part of this check.** The suite is the only
copy of the cases outside this machine's run folder (no Jira archive is
posted since 0.33.0). Suite named + no connector → PAUSE and tell the
user to enable the connector or start from a session that has it —
unless `runs/<STORY>/docs/<STORY>-test-cases.md` exists here, in which
case say the run will use the local copy and cannot write verdicts to a
run. Never discover this at extraction time.

**Build the source register — REQUIRED, in every mode.** Rules and the
table format: `../qa-pipeline/references/sources-of-record.md`. Fetch
each governing document once and write `<KEY>-sources.md`:

1. The **product brief / acceptance criteria** — the Confluence page
   linked from the story (`getJiraIssueRemoteIssueLinks`, then
   `getConfluencePage`). In bug-fix and retest mode fetch the page that
   governs the *feature*, reached via the parent story or the suite.
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

**Same-session shortcut:** if `<STORY>-test-cases.md` (and the
checklist) are already in the run folder — e.g. the docs phase
ran in this chat — use them and skip the Jira read-back below. The
source register is still built: test cases are derived artifacts and
never substitute for it.

Otherwise, using the Atlassian connector and the Story key:

1. **Test cases / checklist.** Find the story's QA sub-task:
   `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype = "QA sub-task"` (prefer the newest
   with label `qa-pipeline` or a `[QA-PIPELINE]` summary).

   **Source order — suite first** (the docs phase posts no fenced copy
   of any file since 0.33.0; the suite is the record):
   - Sub-task names a **QA Service suite** + connector present →
     `get_suite` and rebuild `<STORY>-test-cases.md` from the suite's
     cases (id, title, levels → channel tag, traceability, `detail`
     goal/preconditions/steps/testData/assertions/notes). This is the
     authoritative copy.
     - **Scope it to THIS run.** A suite is per FEATURE and also holds
       earlier stories' cases. Execute only the cases whose
       `detail.ticket` is `<STORY>`, plus any suite case that traces
       to one of this run's requirements (`sources` with `kind: jira,
       label: <STORY>`) without the marker (team-added — flag it in
       the reconciliation list). Pre-0.34 suites carry neither: use
       the case ids on the sub-task's legacy checkbox-tracker lines.
       Never execute the whole suite because it was in the response.
       Report: "suite holds N cases; M in scope for <STORY>".
       Local ids (`TC-REQ-N.M`) come from `detail.pipelineId`.
     - Rebuild `<STORY>-checklist.md` from the suite's requirements
       PLUS its `-STRUCT-` cases — the `[UI]` presence/label/field-type
       checks stage 8 executes, one `[UI]` check per case under its REQ
       (`qa-service-publish.md` → "Structural checks"). They are roster
       cases: stage 8's verdicts on them go on the run. Pre-0.33 ticket
       with no STRUCT cases → read the legacy `(structural checks
       only)` fenced block on the sub-task if present; otherwise say so
       and skip structural checks.
     - **Rebuild `<STORY>-requirements.md`** from the suite's
       requirements (title, kind, risk, stableId → REQ-N mapping from
       `detail.pipelineId`) — without it the analyzer's traceability
       check silently cannot run in any fresh-chat code phase. No
       suite → `runs/<STORY>/docs/<STORY>-requirements.md` on this
       machine; neither → say once that upstream traceability cannot
       be re-verified.
   - No suite line, or no connector → **`runs/<STORY>/docs/`** on this
     machine (the docs phase wrote its files there). Pre-0.33 tickets
     may instead carry fenced archive comments on the sub-task —
     `scripts/extract_archive.py` (legacy) still reads them, parts and
     nested fences included.
   - Neither available → offer the choice: re-run `qa-pipeline-docs`
     (or attach the files), or — for a Bug ticket — **Bug-fix mode**
     below.

   **Bug-fix mode (no docs phase).** For testing a fix to a standalone
   Bug ticket. Two ways in: the user says so ("test the bugfix
   EP-XXXX", "quick check of the fix"), or step 0 finds issuetype Bug
   with no QA sub-task and no suite — then ASK "full pipeline or
   bug-fix mode?". How it differs from a normal run — and nothing
   else differs:
   - **Cases come from the bug ticket itself.** Derive 2–4 mini cases
     into a normal `<KEY>-test-cases.md`: TC-1 = the reproduction
     steps with the FIXED behaviour as the expected result (quote the
     ticket's own words — the source-of-record rule applies: no
     expected result that the ticket does not state); TC-2 = the
     negative sibling (the old broken input/path must not regress the
     surrounding behaviour); plus one regression case per behaviour
     the fix PR touches beyond the bug (from pr-summary's "Behaviours
     touched" — add these AFTER stage 5 runs). Channel-tag each case;
     the routing invariant applies as usual.
   - **No checklist, no QA sub-task — but a suite.** Structural checks
     are skipped (say so). **Publish the mini cases to the FEATURE's
     suite before stage 5** (append, or create the feature's suite),
     with one requirement carrying the ticket's own expected result,
     per `../qa-pipeline-docs/references/qa-service-publish.md` →
     "Bug-fix mode — the regression mini suite" — same single confirm
     as the rest of step 0. That is what lets step 6 open a run with a
     roster and stage 10 record the human verdicts; until 0.33.0 a
     bug-fix run left no durable record at all (EP-56998 open-items
     #13). Connector absent → PAUSE, say what is lost, continue only
     on an explicit yes. The Jira write-back targets are the BUG
     ticket's comments — same two-wave rule: the status comment now,
     the human-facing verdict after your manual check. A Bug or Defect
     gets exactly two comments across the whole run, and the second is
     the verdict a person actually wants to read. The reports stay in
     the run folder, so a resume needs the same machine.
   - **Stages 5–8 run unchanged** on the derived branch (the bug key
     is the branch, or use the main-issue PR fallback). All evidence
     rules, gates and pauses apply — a small scope is not a licence to
     skip the absence-check protocol or the probe rule.
   - **The manual round shrinks to fit:** stage 9 emits a handful of
     cards (or, if you say you'll verify directly, skip the plan and
     just report your result — "the fix works, ingest it" runs stage
     10 against your one-line verdict, joined to the mini cases).
     Verdict flip / bug reopen offers happen at stage 10, as always.

   **QA Service reconciliation:** whenever the sub-task names a suite
   AND the connector is present, reconcile the extracted cases against
   the suite — the suite wins on divergence (cases may have been fixed
   in the web UI between phases); rules:
   `../qa-pipeline-docs/references/qa-service-publish.md` → "Code
   phase — suite as the case source". No suite line or no connector →
   the local docs-phase files are all there is; skip reconciliation and
   the later write-back and say so once in the final response — the
   run will leave no durable per-case record.

   **Resume mode — look in this order:**
   1. **The run folder** — `<STORY>-code-review.md`,
      `-api-testing.md`, `-web-testing.md`, `-run-report.md`,
      `<STORY>-open-items.md` (the ledger — per ticket, no round
      suffix) and, when present, `<STORY>-manual-results.md` and
      `<STORY>-remaining-cases-triage.md`. The last two carry verdict
      corrections that SUPERSEDE the stage reports; a resumed run must
      honour them over older PASS/FAIL lines. When a QA Service run
      already exists for this pass (`list_test_runs` on the suite, title
      `<STORY> …`), its roster verdicts are the machine record — resume
      into that run, never create a second one for the same pass.
   2. **The QA Service run** — for the *verdicts* of a pass whose
      reports are not here: `get_test_run` gives every roster row's
      verdict, principal and note. The prose of a stage report
      (findings, blast radius, unmapped changes) exists only in the run
      folder; pre-0.33 tickets may still carry it in legacy archive
      comments on the QA sub-task (`scripts/extract_archive.py`).
   3. **No run folder for this pass → PAUSE.** The reports live only on
      the machine that ran the stages (no archive is posted since
      0.33.0). Say that plainly,
      ask whether this is the machine the earlier run used, and offer
      either to re-run the missing stages or to have the files
      attached. Never assume "no file" means "stage never ran" — on a
      different machine it means "cannot see it from here", and quietly
      re-running a 45-minute browser stage because a folder was not
      mounted is exactly the waste this guard exists to prevent. **A stage is done only if
   its report is COMPLETE — file existence is not completion.** Read
   each restored report's `Completeness:` header (older reports lack
   one — then derive it: do Scope and Statistics agree, and is every
   in-scope case present in Results or Not-executed-here?). A report
   that is `partial`, internally inconsistent, or
   header-less-and-uncheckable gets its stage RE-DISPATCHED for the
   missing cases — a resumed run must not inherit "NOT EXECUTED 15" as
   "done" (a real run did exactly that). Skip only complete stages;
   continue from the first missing or partial one (typically
   web-testing in Cowork after 5–7 ran in Claude Code) unless the user
   asks to re-run. Tell the user which stages were restored complete
   vs partial vs pending before continuing.

   **Retest mode (the fix came back).** Two ways in, both valid: the
   user says so ("retest <KEY>", "the fix landed"), OR step 0 notices
   the signals — newest human summary / manual-results comment is
   ❌ FAIL, or a previous QA Service run for this key holds `fail` /
   `known_defect` rows (or, pre-0.30, the suite carries RETEST /
   supersede lines) — and ASKS "full run or retest?" instead of
   assuming. Never require a magic phrase.
   **Scope (three tiers, confirmed by the user before stage 5):**
   1. every FAIL / FAIL CONFIRMED case (including retracted-to-FAIL) —
      the defects' own cases;
   2. the blast radius — REQ siblings, cases sharing the fixed code
      path (from the fix PR's Behaviours touched), and confirmed
      `RISK-CR-*` rows;
   3. every case that never got a real verdict: NOT EXECUTED,
      unresolved BLOCKED, rows the human never walked.
   **Read the ledger first.** `<STORY>-open-items.md`
   (`../qa-pipeline/references/open-items-ledger.md`) holds what earlier
   rounds left undecided — carried risk rows, in/out rulings never made,
   findings with no case and no key, `[core]` nominations. Show the open
   rows in the same scope confirmation ("N open items from earlier
   rounds — decide or carry each") and write any decision the user gives
   into the `Decision` column before stage 5. Prior verdicts come from
   the previous pass's QA Service run (`get_test_run`, or
   `case_execution_history` per case) — that is the record, not the
   markdown; where the retracted-verdict tier applies, note **where each
   old verdict was published** (ticket + comment id) in
   `<STORY>-retest-scope.md`, because stage 10's retraction goes there.
   Every FAIL / PARTIAL row a pass leaves `not_run` is scope tier 1 or 3
   of the next pass by construction.
   **Build the scope from the SUITE, not from the local test-cases
   file.** When the sub-task names a QA Service suite and the connector
   is present, `get_suite` FIRST and diff it against
   `<STORY>-test-cases.md`: any requirement or case the suite has and
   the file does not is IN SCOPE by default, and every such case must
   be listed by id in `<STORY>-retest-scope.md` with an explicit
   in/out decision. The suite is the system of record and moves
   between runs — a PM ruling, a QA-added case or a corrected
   expectation lands there, not in the file the docs phase wrote.
   (Real run: the suite had gained a P0 requirement and two P0 manual
   cases from a PM comment four days after the baseline. The retest
   scope was derived from the 89-case file, so neither case was in any
   stage report; one of them was then failed by accident and recorded
   as an unstatused observation, and the other was never executed at
   all.) No suite or no connector → say once in the run report that
   the scope could not be reconciled against the system of record.
   **The scope binds ALL stages including stage 9:** pr-summary runs
   on the fix branch/PR; 6–8 execute only the scoped cases;
   `qa-manual-runsheet` builds cards for the scoped cases ONLY — never
   a full-plan rebuild. Fixtures are FRESH by default: prior fixtures
   are presumed contaminated for any counter/analytics assertion (one
   run left a phantom like and a counter stuck at 15). Reuse a prior
   account only for stateless checks, after re-verifying its login and
   baseline.
   Post results as a normal comment pair with the verdict line
   prefixed `RETEST:`. The retest is a NEW run on the same suite (one
   run per pass); a FAIL that now passes is simply recorded `pass` in
   it, and the retraction comment goes to wherever the old FAIL was
   published (`test-runs.md` → "Retraction target rule"); verified
   bugs get a closing comment offered on their tickets. Everything else
   keeps its verdicts — say so in the summary. Stage 10 ingests the
   retest sheet like a first run.

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
backend — Playwright MCP by default (works in Claude Code too, enabling
a single-environment run), the Chrome extension as the fallback
(Cowork). When the
current environment cannot run everything: run what it can, post the
step-6 comments marked **PARTIAL** (per the template — name the pending
stages), then start a fresh chat in the other environment with the same
Story key. Step 0's resume mode restores the finished reports from the
run folder, and the last environment posts the final status line +
(at stage 10) the summary as NEW comments — existing comments are never
edited.

**What bridges the two environments is the run folder (0.33.0).** Both
must see `runs/<STORY>/r<N>/` — in this setup Cowork and Claude Code
mount the same qa-pipeline-skill repo, so they do. The QA Service run
carries the verdicts across regardless; the reports' prose does not
travel any other way (no archive is posted). If the two environments
cannot share the folder, that run cannot be split: say so before
starting rather than discovering it at step 0, and either run
everything in one environment or have the files carried across by hand.

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
   Executes the `[API]` QA/FAIL cases via curl with `.env`
   credentials. **PAUSE** if `.env` values or a per-event frontend
   host are missing. Produces `<STORY>-api-testing.md`.

4. **web-testing (stage 8)** — on the code-review + test-cases +
   checklist (the checklist supplies the `[UI]` structural checks).
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
   **`references/results-comment-template.md`**.

   **Wave 1 — now, agents only.** The QA Service **test run** (created
   here, closed by stage 10 — `../qa-pipeline/references/test-runs.md`),
   ONE short status comment with no verdicts (`QA automated pass
   complete — N cases, M settled by machine, K for manual — QA Service
   run <id> open. Results published after the manual round.`). **That
   is all wave 1 posts to Jira — one status line, on the QA sub-task
   when the ticket has one, otherwise on the ticket under test.**

   **No archive comments — retired in 0.33.0.** Until then wave 1 also
   pasted every stage report into fenced blocks on the QA sub-task
   ("Comment 1 — machine archive"). Why it is gone: the run is the
   per-case record (0.30.0), the run folder is the reports' home
   (0.32.0), and the dumps ran to three to five unreadable comments
   per pass — on EP-56380 three of them landed on a Defect's face,
   which is what produced the 0.26.0 target rule. A fenced file dump
   on ANY ticket is now a ❌ in the post-publish check. One ticket's
   run never writes into another ticket's thread; **the one sanctioned
   cross-ticket comment is a retraction** (stage 10, `test-runs.md` →
   "Retraction target rule"): ≤ 6 lines correcting a verdict, posted
   where that verdict was published.

   **The reports are local-only, and step 0 guards it:** a resume
   rebuilds from `runs/<STORY>/r<N>/`; on a different machine step 0
   pauses rather than silently re-running or proceeding empty. The
   verdicts themselves are always recoverable from the run.

   **Wave 2 — after `qa-manual-results` (stage 10), never now.** The
   human summary, the story comment, the stage-verdict table, and any
   request for a product decision — by then every verdict is
   human-confirmed or retracted. (Real-run rationale: a PROVISIONAL
   label prevented nothing — a mis-typed bug, three already-answered
   "product decisions", two retractions in 24h. Marking output
   tentative does not make readers treat it tentatively; withholding
   it does.)

   **The exception, and it is narrow.** A finding may publish in
   wave 1 only if ALL of: confirmed at RUNTIME (not a code read);
   evidence attached; and it blocks the manual round from proceeding.
   A code-read FAIL never qualifies.
   - **Count gate first — refuse to post while a mismatch stands.**
     Where a shell is available, run
     `python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <STORY>`
     (self-test first) and compare against each report's own
     Scope/Statistics. Any disagreement (report internal, report vs
     mechanical count, or unexplained missing ids) is fixed in the
     report BEFORE the preview — wrong numbers must not reach Jira,
     the suite, or the human summary.
   - **Publication gate — run it on the drafted comment BEFORE showing
     it.** Rules: `../qa-pipeline/references/sources-of-record.md` § 7.
     Every line a reader would take as "this is broken" carries its
     register row and its verbatim clause; a line with no clause is
     labelled `OBSERVATION (no source checked)` and phrased as a
     question, or cut; an observation a stage report labelled correctly
     must not reappear here as a defect — including inside a table of
     failures or under a column that implies a requirement ("true
     matches", "expected"); a defect owned by another ticket names that
     key on the line. A comment whose numbers are right and whose
     labels are wrong is the failure this gate exists for: it happened
     on EP-56197 with a `"True matches"` column, and the tester caught
     it, not the pipeline.
   - **REQUIRED PAUSE / CONFIRM.** Show what wave 1 will post (the
     status comment verbatim — the only comment), to which ticket, and —
     connector present — the run preview: title, `env`, release (or
     `none`), roster count (= the step-0 scope count, or say why not),
     how many rows will be recorded per verdict, how many stay
     `not_run` for the human round, and — narrow exception only — each
     `fail` **by case**, because recording a `fail` files the Jira
     defect there and then.
     Post only after an explicit yes; the one confirmation covers Jira
     and QA Service, and the per-case `fail` list is the per-bug yes.
   - **QA Service result write-back — the run:** `create_test_run` on
     the in-scope suite case ids, then `record_case_result` per case,
     `source: machine`, exactly per the mapping table in
     `../qa-pipeline/references/test-runs.md`. FAIL / PARTIAL rows stay
     `not_run` (a machine `fail` would file a bug before the human
     round; `blocked` would misreport a failure as an environment
     problem); the run is left `running` for stage 10. A run for this
     pass already exists (resume) → record into it, never a second one.
     Never overwrite lifecycle `status`; write no run lines into notes.
     Connector absent → no run; say so in the final response.
   - **The status comment is the only Jira write in wave 1.** Never
     paste report contents onto any ticket, and never substitute a
     prose summary of them either: the wave-2 human summary is the only
     narrative a ticket gets. The final response names the report paths
     (`runs/<STORY>/r<N>/`) so the user knows where the evidence is.
   - **The human summary is WAVE 2, posted by stage 10, not here.**
     Write `<STORY>-human-summary.md` now (per the template: overall
     verdict, stage-verdict table, confirmed bugs, needs a human, not
     tested, run-health line, ≤30 lines) so stage 10 has the machine's
     picture to reconcile against — but do NOT post it.
   - Use comments (`addCommentToJiraIssue`), never a description
     overwrite.
   - No QA sub-task (Bugs, Defects, small Stories) → the status
     comment goes on the MAIN issue, same confirm pause. That status
     line is the ONLY thing a human-facing ticket receives in wave 1.

7. **Bug filing — after the manual round, not before.** A bug drafted
   from an automated verdict waits for the human to walk that case:
   it goes into the walk plan as a card, and becomes a bug in stage 10
   if it survives contact. The exception is identical to step 6's:
   runtime-confirmed, evidenced, and blocking the manual round. When
   filing does happen, make ONE offer listing all the bugs; file only
   the ones the user confirms.
   - **Source gate — before drafting any bug.** Quote the sentence
     from the register that the build violates, and put it in the
     draft's "Expected result". Check the **as-built document too, not
     only the brief**: a behaviour the as-built doc records as
     deliberate is not a defect, however wrong it looks. (Real case:
     "a matching Group renders nowhere" — the as-built FE doc names
     `groups` as its own example of a type the front end does not
     render. It reached the drafting step.) If the sentence is in no
     source of record, the finding is a SPEC-DEFECT, a product question
     or an `OBSERVATION (no source checked)` — retract the FAIL per the
     supersede convention and raise it to the docs-phase owner instead
     of filing a Bug against a dev. Drafting a "you may get pushed
     back on this" caveat into a bug IS this gate firing — stop.
   - **A closed ticket is not a source.** Citing a precedent
     ("EP-XXXXX was accepted for the same thing") does not satisfy the
     gate: it shows how a similar-looking case was once ruled, not that
     the clause covers yours. Check the register first, then cite the
     precedent as supporting context if it still applies.
   - **Cases on the run's roster file through the run.** A `fail`
     recorded on the QA Service run creates one deduplicated Jira defect
     for that case (an open issue already referencing the stable id is
     linked, not duplicated). For roster cases the per-case `fail` list
     in the confirmation preview IS the draft-and-yes step; the note
     carries where / expected / actual + `Source:` + `Clause:`. The two
     paths below are for findings with **no roster case** — `RISK-CR-*`
     rows not yet promoted, human-confirmed observations.
   - **Preferred path (knowledge-base installed):** hand confirmed
     bugs to `/knowledge-base` — it dedup-searches and creates
     properly routed Jira bugs.
   - **Default path:** draft each bug per
     **`references/bug-report-template.md`**; search Jira for
     duplicates first; show every draft; create via `createJiraIssue`
     only after an explicit yes per bug. Never file silently.

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
     both move to `qa-manual-results` step 4. If the user explicitly
     wants a story note now, post the provisional variant — "✅
     Automated QA passed — manual verification pending"
     (results-comment-template.md) — with no transition. A
     machine-only PASS must never be dressed as final.
   - Transitions are optional: none configured → skip them and do
     only the reassignment + comment. Before any transition, verify it
     exists via `getTransitionsForJiraIssue`; if the configured name
     is absent, list the available ones and ask.

9. **Build the manual walk plan — `qa-manual-runsheet` (stage 9).**
   Every ticket is hand-tested after the machine finishes — this is a
   real step. Read its SKILL.md and follow it in full. It runs at the
   END of the phase because the plan's value is telling the human
   what is *left*: it needs the verdict files to decide which cases
   are settled without a card and which get SPOT-CHECK cards (on a
   real ticket: 89 blind rows vs 11 + a few spot-checks), and stages
   7–8 create ad-hoc data that clean fixtures must not collide with.

   - **REQUIRED PAUSE.** This stage creates accounts and entities on a
     live event. Ask for the throwaway test event id and explicit
     authorisation before provisioning anything. Never target an event
     with real client data; never guess an event.
   - Feed it this run's verdict files (`-code-review.md`,
     `-api-testing.md`, `-web-testing.md`) and the step-6 run id.
   - Outputs `<STORY>-walk-plan.md`, `<STORY>-testdata.json`,
     `<STORY>-testdata-notes.md` (and `<STORY>-runsheet.xlsx` only when
     the user asks for the export). **The plan, the testdata and the
     sheet carry live credentials — git-ignored, never committed or
     attached to Jira.**
   - Report account/entity counts, cards by kind (WALK / SPOT-CHECK /
     AGENT-RUNS / DEVICE / BLOCKED), how many cases were settled
     without a card, and anything not provisionable.

   Skip only if the user says they are not hand-testing this ticket.

   **Post-publish verification — always the last action of the run.**
   The analyzer ran at step 5, BEFORE steps 6–9 — nothing it certified
   covers what they actually did. Verify the final state now:
   - **Write-back landed:** connector present → `get_test_run` on the
     run step 6 created: roster count == the step-0 scope count, and
     the `progress` partition matches the stage reports under the
     `test-runs.md` mapping (`pass` = PASS + FAIL REJECTED, `blocked`,
     `skipped` = NOT EXECUTED + NOT-TESTABLE + SPEC-DEFECT,
     `known_defect` = keyed FAIL CONFIRMED, `not_run` = the FAIL /
     PARTIAL rows the human will walk). Then
     `executed_coverage(suiteId)`: `neverExecuted` fell by the recorded
     count. A mismatch is a count-gate ❌ — fix it now. Connector absent
     → state that no durable per-case record exists beyond the Jira
     comments.
   - **Findings traceable:** every FAIL / FAIL CONFIRMED across the
     three reports has a walk-plan card awaiting the tester (and a
     `not_run` roster row), a narrow-exception bug key, or an explicit
     "not carried — <reason>" line in the drafted human summary. No
     silent FAILs. Every 🔴/🟡 the analyzer left unsettled has a row in
     `<STORY>-open-items.md` (`open-items-ledger.md`).
   - **Wave-1 comment exists, on the right ticket, and nothing else
     does:** exactly one status comment (QA sub-task when there is one,
     else the ticket under test) — re-read, don't assume. A fenced file
     dump found on ANY ticket is a ❌ (archives retired 0.33.0). The
     human summary must NOT be posted yet — finding it posted early is
     a ❌.
   - **Reports are on disk:** every stage report the run produced is
     present in the run folder. They are the ONLY copy of the evidence
     — a missing one is a ❌, not a formality.
   - **Walk-plan outputs exist** — `<STORY>-walk-plan.md` and
     `-testdata.json` (unless stage 9 was skipped), and every card in
     the plan passed stage 9's voice check (no HTTP verb, curl line or
     caveat in a card body outside an AGENT-RUNS `run:` key).
   - **Everything is in the run folder:** every file this pass wrote is
     under `runs/<STORY>/r<N>/` (ledger one level up), and **no
     `<STORY>-*` file was written to the repo root**. One in the root is
     a ❌ — move it and say so.
   Append the outcome as `## Post-publish verification` (✅/❌ per
   item) to `<STORY>-run-report.md` and include one line in the final
   response. A ❌ here is a real finding — fix it or tell the user,
   never bury it.

10. **The human round — `qa-manual-walk` then `qa-manual-results`
    (stage 10, deferred).** The human run happens after this
    orchestrator finishes — often days later, in a different chat.
    It has two halves:
    - **The walk (live half).** The tester says "walk me through
      <STORY>" and `qa-manual-walk` presents the plan one card at a
      time, answers questions from backstage, runs the AGENT-RUNS
      cards itself, keeps `<STORY>-walk-state.json` for resume, and
      writes `<STORY>-walk-results.md`. It records nothing.
    - **The write-back.** At the end of the walk — or when a tester
      hands back a filled sheet / TC-Result-Notes table instead —
      `qa-manual-results` joins by TC id, reconciles against the
      machine record, shows every `fail` about to be recorded, and on
      the tester's yes writes back with explicit retractions and — per
      the two-wave rule — posts the FIRST human-facing summary, files
      the surviving bugs, and makes the handback offers.
    End THIS run by telling the user plainly: nothing human-facing has
    been published yet; the walk is next, and stage 10's write-back is
    where the team hears the result.

## Between stages

- Keep chat output short: one line per hand-off. Each stage's own
  rules and templates apply unchanged.
- **Run clock (progress + time left):** stamp the wall clock (`date
  +%H:%M`) at step 0 and after every stage/step completes; post
  exactly ONE line per boundary:
  `⏱ Stage <n>/<total> done — <name> · elapsed <E> min · ~<R> min left`.
  Initial budgets (minutes): step 0 8 · pr-summary 15 · code-review 30
  · api-testing 25 · web-testing 45 · analyzer 8 · run + publish
  10 · walk plan 30. Compute `<R>` as the unfinished budgets scaled by
  the run's own pace (elapsed ÷ sum of finished budgets, clamped to
  0.5–3); round to 5 minutes, keep the `~`. Stamp both ends of every
  user-waiting pause (browser login, Jira write confirmation, test-
  event authorisation) and subtract waited time from elapsed — waiting
  is not pace. Retest / bug-fix runs: halve the budgets of the
  scoped-down stages. No shell available → skip the clock silently.
- **The orchestrator never asserts a product claim from its own
  observation.** A defect, a reclassification, a reachability claim, a
  "this is actually fine" — every such statement is produced by a
  stage skill under that stage's evidence rules, or dispatched to one.
  On real runs the dominant error source was the orchestrator
  narrating conclusions between stages from a single glance.
- **Chat is a publication surface, and the gate applies to it.** What
  is said to the user is held to the report's standard: every finding
  presented as a defect carries its `Source:` and `Clause:`, and an
  `OBSERVATION (no source checked)` carries its label. Never list
  unsourced observations in one numbered run alongside verified
  failures — equal presentation grants equal authority, and the user
  then acts on it. (Real case: three observations were presented as
  "issues 4, 5 and 6" beside two confirmed failures; one was as-built
  behaviour, two were unfileable. The reports had labelled all three
  correctly — the chat summary was what lost the labels.)

## Final response

Report: the files produced and their full paths — **and that they are
the only copy of the evidence**; the
overall (machine) verdict and confirmed bugs; confirmation of what
wave 1 posted and where (key + URL — one status comment, nothing
else), and that the human summary is written but
deliberately NOT posted (two-wave rule); the QA Service run id and its
recorded counts per verdict + how many rows stay `not_run` for the
human (or "no run — connector not enabled" / "no run — no suite for
this ticket") and any step-0 reconciliation changes; the open-items
ledger's open-row count; which bugs (if any)
passed the narrow exception and were filed, or that filing waits for
stage 10; which handoff was performed or deferred. Reuse the human-summary content
rather than inventing a third format.

Then, from step 9: the walk-plan path, how many cards the tester will
walk (by kind) vs how many cases the machine settled, the reminder that
the plan and provisioning record hold live credentials and stay out of
version control and Jira, and the hand-off line: "walk me through
<STORY>" starts the session.
