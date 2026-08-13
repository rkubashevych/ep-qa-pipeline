---
name: qa-pipeline-code
description: >
  Orchestrator for the code + UI half of the QA pipeline (stages
  5-10). Given a Story key, reads the test cases from the story's QA
  sub-task and derives the dev branches, then runs pr-summary, then
  code-review, then api-testing, then web-testing, then run-analyzer,
  archives machine results on the QA sub-task (human summary follows
  at stage 10), builds the manual run sheet so a human can walk what
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
> connector**; `get_suite` / `get_test_case` / `edit_test_case` etc.
> belong to the **QA Service MCP connector**. The install-specific
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

## Step 0 — Gather inputs

**Session name:** suggest renaming this session to
`QA-pipeline <STORY> — code` (Claude Code: `/rename …`; Cowork: click
the chat title). One short reminder, then move on.

**Environment check first.** Stages 5–7 need things Cowork usually
lacks: a repo clone or `BB_EMAIL`+`BB_API_TOKEN` (5–6) and API
credentials (7). All can come from ONE file: `.env.qa-agents` in the
mounted qa-pipeline-skill repo (preferred), falling back to the e2e
`.env` / env vars. Before running anything, check they are reachable.
If not, say so NOW and ask the user to mount the folder or run this
phase from Claude Code (MAINTAINERS "Where to run each stage") — do
not discover this mid-run at stage 5.

**QA Service connector is part of this check.** If the QA sub-task's
description names a QA Service suite and the connector is NOT in this
session, there is nothing to rebuild the cases from — a
suite-published ticket carries no Jira archive (0.11.2 dedup). Suite
named + no connector + no archive comment → PAUSE and tell the user to
enable the connector or start from a session that has it. Never
discover this at extraction time.

**Same-session shortcut:** if `<STORY>-test-cases.md` (and the
checklist) are already in the working directory — e.g. the docs phase
ran in this chat — use them and skip the Jira read-back below.

Otherwise, using the Atlassian connector and the Story key:

1. **Test cases / checklist.** Find the story's QA sub-task:
   `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype = "QA sub-task"` (prefer the newest
   with label `qa-pipeline` or a `[QA-PIPELINE]` summary).

   **Source order — suite first** (since 0.11.2 the docs phase posts
   no fenced archive when it published a suite):
   - Sub-task names a **QA Service suite** + connector present →
     `get_suite` and rebuild `<STORY>-test-cases.md` from the suite's
     cases (id, title, levels → channel tag, traceability, `detail`
     goal/preconditions/steps/testData/assertions/notes). This is the
     authoritative copy.
     - **Scope it to THIS run.** A suite is per FEATURE and also holds
       earlier stories' cases. Execute only the ids on the sub-task's
       checkbox tracker (each line carries its case id), plus any
       suite case that traces to this run's requirements with no
       tracker line (team-added — flag it in the reconciliation
       list). Never execute the whole suite because it was in the
       response. Report: "suite holds N cases; M in scope for
       <STORY>".
     - Rebuild `<STORY>-checklist.md` from the suite's requirements
       PLUS the `(structural checks only)` fenced block on the
       sub-task — those `[UI]` presence/label/field-type checks exist
       only there and stage 8 needs them. Block missing on an older
       ticket → say so; structural checks will be skipped.
     - **Rebuild `<STORY>-requirements.md`** from the suite's
       requirements (title, kind, risk, stableId → REQ-N mapping from
       the tracker lines) — without it the analyzer's traceability
       check silently cannot run in any fresh-chat code phase. No
       suite → use the requirements block from the docs archive
       comment (posted since 0.17.0); neither exists (older tickets)
       → say once that upstream traceability cannot be re-verified.
   - No suite line, or no connector → fall back to the **fenced
     archive comments** (posted exactly in that case). Extract the
     fenced blocks from the description/comments; large files may be
     split as `File: <name> (part i/N)` blocks — collect and
     concatenate in order. Prefer `scripts/extract_archive.py` (this
     skill's folder) on the saved comment bodies — it handles labels,
     parts, and nested fences deterministically; extract manually only
     if it cannot run. Write `<STORY>-checklist.md` and
     `<STORY>-test-cases.md` to the working directory.
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
   - **No checklist, no suite, no QA sub-task.** Structural checks are
     skipped (say so); the write-back targets are the BUG ticket's
     comments — same two-wave rule: archive + status comment now, the
     human-facing verdict after your manual check.
   - **Stages 5–8 run unchanged** on the derived branch (the bug key
     is the branch, or use the main-issue PR fallback). All evidence
     rules, gates and pauses apply — a small scope is not a licence to
     skip the absence-check protocol or the probe rule.
   - **The manual round shrinks to fit:** stage 9 emits a handful of
     rows (or, if you say you'll verify directly, skip the sheet and
     just report your result — "the fix works, ingest it" runs stage
     10 against your one-line verdict, joined to the mini cases).
     Verdict flip / bug reopen offers happen at stage 10, as always.

   **QA Service reconciliation:** whenever the sub-task names a suite
   AND the connector is present, reconcile the extracted cases against
   the suite — the suite wins on divergence (cases may have been fixed
   in the web UI between phases); rules:
   `../qa-pipeline-docs/references/qa-service-publish.md` → "Code
   phase — suite as the case source". No suite line or no connector →
   the Jira archive is authoritative; skip reconciliation and the
   later write-back silently and say so once in the final response.
   Never block on QA Service.

   **Resume mode:** if the sub-task has a results **archive comment**
   from an earlier partial run (fenced blocks labeled
   `File: <STORY>-code-review.md` etc. —
   `references/results-comment-template.md`), extract those files too.
   Also extract, when present, `File: <STORY>-manual-results.md` and
   any `File: <STORY>-remaining-cases-triage.md` — they carry verdict
   corrections that SUPERSEDE the stage reports; a resumed run must
   honour them over older PASS/FAIL lines. **A stage is done only if
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
   ❌ FAIL, or the suite carries RETEST/supersede lines — and ASKS
   "full run or retest?" instead of assuming. Never require a magic
   phrase.
   **Scope (three tiers, confirmed by the user before stage 5):**
   1. every FAIL / FAIL CONFIRMED case (including retracted-to-FAIL) —
      the defects' own cases;
   2. the blast radius — REQ siblings, cases sharing the fixed code
      path (from the fix PR's Behaviours touched), and confirmed
      `RISK-CR-*` rows;
   3. every case that never got a real verdict: NOT EXECUTED,
      unresolved BLOCKED, rows the human never walked.
   **The scope binds ALL stages including stage 9:** pr-summary runs
   on the fix branch/PR; 6–8 execute only the scoped cases;
   `qa-manual-runsheet` builds rows for the scoped cases ONLY — never
   a full-sheet rebuild. Fixtures are FRESH by default: prior fixtures
   are presumed contaminated for any counter/analytics assertion (one
   run left a phantom like and a counter stuck at 15). Reuse a prior
   account only for stateless checks, after re-verifying its login and
   baseline.
   Post results as a normal comment pair with the verdict line
   prefixed `RETEST:`. Write-backs follow the retraction convention (a
   FAIL that now passes gets its supersede line); verified bugs get a
   closing comment offered on their tickets. Everything else keeps its
   verdicts — say so in the summary. Stage 10 ingests the retest sheet
   like a first run.

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
backend — Playwright MCP (works in Claude Code too, enabling a
single-environment run) or the Chrome extension (Cowork). When the
current environment cannot run everything: run what it can, post the
two step-6 comments marked **PARTIAL** (per the template — name the
pending stages), then start a fresh chat in the other environment with
the same Story key. Step 0's resume mode restores the finished
reports, and the last environment posts the final archive + summary as
a NEW pair — existing comments are never edited.

## How it runs

Execute each stage by reading its `SKILL.md` and following it in full.

### Stage isolation (context health)

When subagents are available (Task tool in Claude Code, Agent tool in
Cowork), run stages 5–7 each as a SEPARATE subagent so a multi-PR
story does not exhaust the orchestrator's context:

- Give the subagent the stage's SKILL.md path, the input file paths,
  and the working directory. It follows the SKILL.md in full, writes
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
   Playwright MCP when available, Chrome extension otherwise.
   **PAUSE** (extension backend only) for browser login and any
   unknown navigation path. Produces `<STORY>-web-testing.md`.

5. **qa-run-analyzer** — run automatically; writes
   `<STORY>-run-report.md`.

6. **Publish in two waves — only the first happens now.** Formats:
   **`references/results-comment-template.md`**.

   **Wave 1 — now, agents only.** The machine archive comment(s) (a
   resumed run needs them; they are unreadable to a human and tag no
   one), the QA Service suite write-back, and ONE short status comment
   on the QA sub-task with no verdicts: `QA automated pass complete —
   N cases, M settled by machine, K for manual. Results published
   after the manual round.`

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
   - **REQUIRED PAUSE / CONFIRM.** Show what wave 1 will post (archive
     comment(s) + status comment), to which sub-task, and — connector
     present — the write-back line (how many cases get a run note).
     Post only after an explicit yes; the one confirmation covers Jira
     and QA Service.
   - **QA Service result write-back:** append each executed case's
     outcome to its suite case notes — rules and note format:
     `../qa-pipeline-docs/references/qa-service-publish.md` → "Result
     write-back". Never overwrite lifecycle `status`. Connector absent
     → skip with a note in the final response.
   - **Comment 1 — machine archive (for agents):** the full
     `<STORY>-code-review.md`, `-api-testing.md`, `-web-testing.md`
     and `-run-report.md`, each in its own fenced code block preceded
     by a plain `File: <name>` line (same convention as the docs-phase
     archive). Do not shorten or reformat.
   - **Comment 2 — human summary — is WAVE 2, posted by stage 10, not
     here.** Write `<STORY>-human-summary.md` now (per the template:
     overall verdict, stage-verdict table, confirmed bugs, needs a
     human, not tested, run-health line, ≤30 lines) so stage 10 has
     the machine's picture to reconcile against — but do NOT post it.
   - Use comments (`addCommentToJiraIssue`), never a description
     overwrite.
   - No QA sub-task (the fallback case) → post the wave-1 comments to
     the MAIN issue — same format, same confirm pause.
   - **Tracker note:** the connector cannot tick the docs-phase
     checkbox tracker. The human summary is the source of truth for
     automated results; the tracker holds the human's manual
     verification. Remind the user in the final response.

7. **Bug filing — after the manual round, not before.** A bug drafted
   from an automated verdict waits for the human to walk that case:
   it goes into the run sheet as a row, and becomes a bug in stage 10
   if it survives contact. The exception is identical to step 6's:
   runtime-confirmed, evidenced, and blocking the manual round. When
   filing does happen, make ONE offer listing all the bugs; file only
   the ones the user confirms.
   - **Source gate — before drafting any bug.** Quote the sentence
     from the acceptance criteria (or the implementing sub-task) that
     the build violates, and put it in the draft's "Expected result".
     If that sentence is in no source of record, the finding is a
     SPEC-DEFECT or a product question — retract the FAIL per the
     supersede convention and raise it to the docs-phase owner instead
     of filing a Bug against a dev. Drafting a "you may get pushed
     back on this" caveat into a bug IS this gate firing — stop.
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

9. **Build the manual run sheet — `qa-manual-runsheet` (stage 9).**
   Every ticket is hand-tested after the machine finishes — this is a
   real step. Read its SKILL.md and follow it in full. It runs at the
   END of the phase because the sheet's value is telling the human
   what is *left*: it needs the verdict files to mark settled rows and
   VERIFY spot-checks (on a real ticket: 89 blind rows vs 11 + a few
   spot-checks), and stages 7–8 create ad-hoc data that clean fixtures
   must not collide with.

   - **REQUIRED PAUSE.** This stage creates accounts and entities on a
     live event. Ask for the throwaway test event id and explicit
     authorisation before provisioning anything. Never target an event
     with real client data; never guess an event.
   - Feed it this run's verdict files (`-code-review.md`,
     `-api-testing.md`, `-web-testing.md`).
   - Outputs `<STORY>-runsheet.xlsx`, `<STORY>-testdata.json`,
     `<STORY>-testdata-notes.md`. **They carry live credentials —
     git-ignored, never committed or attached to Jira.**
   - Report account/entity counts, the ready / must-test / blocked
     split, and anything not provisionable.

   Skip only if the user says they are not hand-testing this ticket.

   **Post-publish verification — always the last action of the run.**
   The analyzer ran at step 5, BEFORE steps 6–9 — nothing it certified
   covers what they actually did. Verify the final state now:
   - **Write-back landed:** connector present → `get_test_case` on a
     sample (all, if few) of the cases step 6 planned to annotate;
     confirm the run line is in `notes` and the count matches the
     plan. Connector absent → state that no durable per-case record
     exists beyond the Jira comments.
   - **Findings traceable:** every FAIL / FAIL CONFIRMED across the
     three reports has a run-sheet row awaiting the tester, a
     narrow-exception bug key, or an explicit "not carried — <reason>"
     line in the drafted human summary. No silent FAILs.
   - **Wave-1 comments exist:** the archive comment(s) and the status
     comment are on the sub-task — re-read, don't assume. The human
     summary must NOT be posted yet — finding it posted early is a ❌.
   - **Runsheet outputs exist** (unless stage 9 was skipped).
   Append the outcome as `## Post-publish verification` (✅/❌ per
   item) to `<STORY>-run-report.md` and include one line in the final
   response. A ❌ here is a real finding — fix it or tell the user,
   never bury it.

10. **Ingest the manual results — `qa-manual-results` (stage 10,
    deferred).** The human run happens after this orchestrator
    finishes — often days later, in a different chat. When the tester
    hands back the filled sheet (or a TC/Result/Notes table), run
    `qa-manual-results`: it joins by TC id, reconciles against the
    machine record, writes back with explicit retractions, and — per
    the two-wave rule — posts the FIRST human-facing summary, files
    the surviving bugs, and makes the handback offers. End THIS run by
    telling the user plainly: nothing human-facing has been published
    yet; stage 10 is where the team hears the result.

## Between stages

- Keep chat output short: one line per hand-off. Each stage's own
  rules and templates apply unchanged.
- **The orchestrator never asserts a product claim from its own
  observation.** A defect, a reclassification, a reachability claim, a
  "this is actually fine" — every such statement is produced by a
  stage skill under that stage's evidence rules, or dispatched to one.
  On real runs the dominant error source was the orchestrator
  narrating conclusions between stages from a single glance.

## Final response

Report: the files produced; the overall (machine) verdict and
confirmed bugs; confirmation that the wave-1 comments (machine archive
+ status comment) were posted to the QA sub-task (key + URL) and that
the human summary is written but deliberately NOT posted (two-wave
rule); the QA Service write-back counts (or "skipped — connector not
enabled") and any step-0 reconciliation changes; which bugs (if any)
passed the narrow exception and were filed, or that filing waits for
stage 10; which handoff was performed or deferred; the tracker
reminder (checkboxes are manual-only). Reuse the human-summary content
rather than inventing a third format.

Then, from step 9: the run-sheet path, how many cases the tester still
has to walk vs how many the machine settled, and the reminder that the
run sheet and provisioning record hold live credentials and stay out
of version control and Jira.
