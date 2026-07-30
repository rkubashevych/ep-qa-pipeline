---
name: qa-pipeline-code
description: >
  Orchestrator for the code + UI half of the QA pipeline (stages
  5-10). Given a Story key, reads the test cases from the story's QA
  sub-task (published by qa-pipeline-docs) and derives the dev branches
  from the backend/frontend sub-tasks, then runs pr-summary ->
  code-review -> api-testing -> web-testing -> run-analyzer, posts the
  results back to the QA sub-task (marked PROVISIONAL), builds the
  manual run sheet (qa-manual-runsheet) so a human can walk what the
  machine could not settle, verifies the published state, and defers
  the final handback to qa-manual-results (stage 10). Also supports
  retest mode for verifying dev fixes. Auto-advances, pausing for the browser login, the Jira
  write confirmation, and the test-event authorisation before any
  fixture is provisioned. Use it when the user says "run the QA code
  pipeline", "review the PRs and test in the browser", "do code review
  and UI testing for a ticket". Run in a FRESH chat after
  qa-pipeline-docs.
---

# QA Pipeline -- Code & UI (stages 5-10)

> Recommended settings for the whole run: **Opus . Effort: High .
> Extended thinking: On**. Code review (stage 6) benefits most.
> Stage 7 (api-testing) runs the `[API]` cases; stage 8 (web-testing)
> runs the `[UI]` cases.

Runs the code-review and UI-testing half end to end. Each stage is a
real skill in this repo -- this orchestrator sequences them. Start it in
a fresh chat (separate from the docs phase) for context/token health.

## Input

- A Story key (e.g. `EP-44730`) — same as the docs phase. Everything
  else is pulled from Jira; you should not need to attach files.
- Optional: a per-task test host (alpha host) for the UI stage. If the
  QA sub-task names one, use it.
- For stage 7 (api-testing): the e2e `.env` (ADMIN_BASE_URL,
  ADMIN_USERNAME/PASSWORD, ORGANIZER_API_KEY, EVENT_ID, BASE_URL) and,
  for exhibitor-token cases, the per-event frontend host + an exhibitor
  login. The frontend host is per-event and not discoverable — it must
  be supplied. api-testing pauses and asks if these are missing.

## Step 0 — Gather inputs

**Session name:** suggest the user rename this session to
`QA-pipeline <STORY> — code` (Claude Code: `/rename QA-pipeline
<STORY> — code`; Cowork: click the chat title). One short reminder,
then move on.

**Environment check first.** Stages 5–7 need things Cowork usually
does not have: a repo clone or `BB_EMAIL`+`BB_API_TOKEN` (stages 5–6)
and API credentials (stage 7). All of these can come from ONE file:
`.env.qa-agents` in the mounted qa-pipeline-skill repo (preferred),
falling back to the e2e project's `.env` / env vars. Before running anything, check they are
reachable (a mounted folder holding them, or the env vars set). If
they are not, say so NOW and ask the user to either mount the folder
that has them or run this phase from Claude Code (see MAINTAINERS
"Where to run each stage") — do not discover this mid-run at stage 5.

**QA Service connector is part of this check.** If the QA sub-task's
description names a QA Service suite and the connector is NOT in this
session, there is nothing to rebuild the cases from — a
suite-published ticket carries no Jira archive (0.11.2 dedup). Verify
this NOW: suite named + no connector + no archive comment → PAUSE and
tell the user to enable the connector or start from a session that has
it. Never discover this at extraction time.

**Same-session shortcut:** if the `<STORY>-test-cases.md` (and
checklist) files are already in the working directory — e.g. you ran
`qa-pipeline-docs` in this same chat — use them directly and skip the
Jira read-back below. Only pull from Jira when the files are not present
(the fresh-chat case).

Otherwise, using the Atlassian connector and the Story key:

1. **Test cases / checklist.** Find the story's QA sub-task created by
   the docs phase: `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype = "QA sub-task"` (prefer the newest
   with label `qa-pipeline` or a `[QA-PIPELINE]` summary).

   **Source order — suite first.** Since 0.11.2 the docs phase does not
   post the fenced archive when it published a QA Service suite (the
   cases were duplicated in Jira otherwise). So:
   - the sub-task description names a **QA Service suite** and the
     connector is present → `get_suite` and rebuild
     `<STORY>-test-cases.md` from the suite's cases (id, title, levels →
     channel tag, traceability, and `detail`
     goal/preconditions/steps/testData/assertions/notes). This is the
     authoritative copy of the cases.
     - **Scope it to THIS run.** A suite is per FEATURE, so it also
       holds cases from earlier stories. Execute only the cases whose
       ids appear on the sub-task's checkbox tracker (each line carries
       its QA Service case id), plus any suite case that traces to a
       requirement in this run and has no tracker line (team-added —
       flag it in the reconciliation list). Never execute the whole
       suite because it happens to be in the response. Report the
       numbers: "suite holds N cases; M in scope for <STORY>". Rebuild `<STORY>-checklist.md`
     from the suite's requirements PLUS the
     `(structural checks only)` fenced block on the sub-task — those
     `[UI]` presence/label/field-type checks have no test case and exist
     only there; stage 8 needs them. If that block is missing on an
     older ticket, say so — structural checks will be skipped.
     **Also rebuild `<STORY>-requirements.md` from the suite's
     requirements** (title, kind, risk, and the stableId → REQ-N
     mapping carried on the tracker lines): without it, the analyzer's
     traceability check silently cannot run in any fresh-chat code
     phase — the documented normal flow. When there is no suite, use
     the requirements block from the docs archive comment (posted
     since 0.17.0); on older tickets where neither exists, say once
     that upstream traceability cannot be re-verified this run.
   - no suite line, or no connector → fall back to the **fenced archive
     comments**, which the docs phase posts in exactly that case.
   - neither available → tell the user to re-run `qa-pipeline-docs` (or
     attach the files).

   When falling back to the archive, read the description (and comments)
   and extract the fenced code blocks holding the checklist and test
   cases. Large files may be split across
   comments as `File: <name> (part i/N)` blocks — collect all parts and
   concatenate them in order. Prefer running
   `scripts/extract_archive.py` (in this skill's folder) on the saved
   comment bodies — it handles labels, parts, and nested fences
   deterministically; fall back to manual extraction only if the script
   cannot run. Write the results to the working directory as
   `<STORY>-checklist.md` and `<STORY>-test-cases.md` so the stage
   skills can consume them.
   - **QA Service reconciliation:** whenever the QA sub-task names a
     QA Service suite (the docs phase published one) and the connector
     is present. No suite line or no connector → Jira archive is
     authoritative, skip reconciliation and the later write-back
     silently; say so once in the final response. Otherwise, after
     extracting the files reconcile the test cases
     against the published suite — the suite wins on divergence
     (cases may have been fixed in the web UI between phases). Rules:
     `qa-pipeline-docs/references/qa-service-publish.md` → "Code phase
     — suite as the case source". Connector absent → Jira archive is
     authoritative, as before; never block on QA Service.
   - If no pipeline QA sub-task exists, tell the user to run
     `qa-pipeline-docs` first (or to attach the test-cases file).
   - **Resume mode:** if the sub-task also has a results **archive
     comment** from an earlier partial run (fenced blocks labeled
     `File: <STORY>-code-review.md` etc. — see
     `references/results-comment-template.md`), extract those files to
     the working directory too. Also extract, when present:
     `File: <STORY>-manual-results.md` (posted by `qa-manual-results`)
     and any `File: <STORY>-remaining-cases-triage.md` — they carry
     verdict corrections that SUPERSEDE the stage reports; a resumed
     run that reconciles cases must honour them over older PASS/FAIL
     lines. **A stage is done only if its report is COMPLETE — file
     existence is not completion.** For each restored report, read its
     `Completeness:` header (older reports lack one — then derive it:
     do the Scope and Statistics totals agree, and is every in-scope
     case present in Results or Not-executed-here?). A report that is
     `partial`, internally inconsistent, or header-less-and-uncheckable
     gets its stage RE-DISPATCHED for the missing cases — a resumed
     run must not inherit "NOT EXECUTED 15" as "done" (a real run did
     exactly that). Skip only stages whose reports are complete, and
     continue from the first missing or partial stage
     (typically web-testing in Cowork after 5–7 ran in Claude Code),
     unless the user asks to re-run. Tell the user which stages were
     restored complete vs partial vs pending before continuing.
   - **Retest mode (the fix came back):** when the QA sub-task's
     newest human summary (or manual-results comment) is ❌ FAIL and
     the user says the fix has landed, do not re-run everything. Scope
     this run to: every FAIL / FAIL CONFIRMED case (including
     retracted-to-FAIL ones), the other cases of the same REQ groups
     (the fix's blast radius), and any `RISK-CR-*` rows that were
     confirmed. Run stages 5–8 on that scope only — pr-summary on the
     fix branch/PR — and post the results as a normal comment pair
     with the verdict line prefixed `RETEST:`. Write-backs follow the
     retraction convention (a FAIL that now passes gets its supersede
     line), and verified bugs get a closing comment offered on their
     tickets. Everything else from the prior run keeps its verdicts —
     say so in the summary.
2. **Dev branches.** `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype in ("Backend sub-task","Frontend
   sub-task")`. Each dev sub-task's **key is its branch name** (e.g.
   `EP-47975`, `EP-54610`). Use these as the branches for branch mode —
   no PR URLs needed. List them for the user before starting.
   - **Fallback — no dev sub-tasks.** Some tickets (Bugs, small
     Stories, Tasks) carry the dev work on the main issue itself, with
     no backend/frontend sub-tasks. If the JQL returns none, look for
     the PR/branch on the main issue, in this order:
     1. **Remote / development links:** `getJiraIssueRemoteIssueLinks`
        on `<STORY>` — collect any Bitbucket PR URLs.
     2. **Description and comments:** scan the issue's description and
        comments for Bitbucket PR URLs
        (`bitbucket.org/<workspace>/<repo>/pull-requests/<id>`).
     3. **Issue key as branch:** if no PR URL is found, try the issue
        key itself as the branch name (branch mode) — devs branch as
        `<KEY>` by convention, so `git fetch` / the Bitbucket API can
        confirm whether such a branch exists in the backend and/or
        frontend repo. Use each repo where it exists.
     4. **Still nothing:** PAUSE and ask the user for the PR URL(s) or
        branch name(s). Do not guess further.

     Whatever the fallback finds, list the PRs/branches for the user
     (with where each was found) before starting, same as the sub-task
     path.

## Split runs (Claude Code ↔ Cowork)

Stages 5–7 need repo/API creds (Claude Code); stage 8 needs a browser
backend — the Playwright MCP (works in Claude Code too, making a
single-environment run possible) or the Chrome extension (Cowork).
When the current environment cannot run everything:
run what it can, post the two step-6 comments marked **PARTIAL** (per
the template — name the pending stages), then start a fresh chat in the
other environment with the same Story key. Step 0's resume mode
restores the finished reports from the archive comment, and the last
environment posts the final archive + summary as a NEW pair — existing
comments are never edited.

## How it runs

Execute each stage by reading its `SKILL.md` and following it in full.

### Stage isolation (context health)

When the environment supports subagents (the Task tool in Claude Code,
the Agent tool in Cowork), run stages 5-7 (pr-summary, code-review,
api-testing) each as a SEPARATE subagent instead of inline, so a
multi-PR story does not exhaust the orchestrator's context:

- Give the subagent: the stage's SKILL.md path, the input file paths,
  and the working directory. It follows the stage SKILL.md in full,
  writes the stage's report file, and returns only a short summary
  (<= 10 lines: counters, verdict, blockers). It must NOT paste the
  report content into its reply.
- Resolve everything that could pause BEFORE dispatching (step 0's
  environment check: repo/creds, `.env`, hosts). Subagents cannot ask
  the user - a subagent that hits a missing input stops and RETURNS
  the blocker; the orchestrator asks the user, then re-dispatches.
- Stage 8 (web-testing) stays in the main conversation - it needs the
  browser extension and interactive pauses (login, navigation).
  qa-run-analyzer is light; run it inline.
- If subagents are not available, run everything inline as before,
  and make sure stage 8 starts with enough context left.

1. **pr-summary (stage 5)** -- run on the derived branches (branch mode; the
   repository-scoped token is enough) or, when step 0's fallback found
   PR URLs on the main issue, on those PRs directly. Groups changes
   per sub-task (or per PR/branch when there are no sub-tasks).
   Produces `<STORY>-pr-summary.md`.

2. **code-review (stage 6)** -- run on the test-cases + pr-summary across all the
   branches. Keys results by REQ-ID with a PR/branch column.
   Produces `<STORY>-code-review.md`.

3. **api-testing (stage 7)** -- run on the code-review + test-cases. Executes the
   `[API]` cases (status QA/FAIL) against the REST API via curl using
   `.env` credentials; covers admin REST, legacy admin-panel and
   exhibitor-token (frontend) cases. Read-only by default; any write
   snapshots-and-reverts or uses a throwaway entity.
   - **PAUSE** if `.env` (ADMIN_BASE_URL, ORGANIZER_API_KEY, EVENT_ID,
     admin creds) or a per-event frontend host is missing.
   - Produces `<STORY>-api-testing.md`.

4. **web-testing (stage 8)** -- run on the code-review + test-cases + checklist
   (the checklist supplies the `[UI]` structural checks).
   - Executes only `[UI]` test cases. `[API]` cases are handled by
     stage 3 (api-testing); only `[mobile]`/`[export/email]` remain
     under "Not executed here".
   - Backend: Playwright MCP when available (headless, scripted login
     from `.env.qa-agents`, FAIL screenshots + console evidence — no
     login pause); Chrome extension otherwise.
   - **PAUSE** (extension backend only) for browser login (per
     `login-config.md`, or the per-task host) and any unknown
     navigation path.
   - Produces `<STORY>-web-testing.md`.

5. **qa-run-analyzer** -- run automatically; also reads
   `<STORY>-api-testing.md`. Writes `<STORY>-run-report.md`.

6. **Post results back to the QA sub-task** -- TWO comments, per
   **`references/results-comment-template.md`** (formats live there,
   not here):
   - **Count gate first — refuse to post while a mismatch stands.**
     Where a shell is available, run
     `python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <STORY>`
     (self-test first) and compare its mechanical counts against each
     report's own Scope/Statistics numbers. Any disagreement (a
     report's Scope vs its Statistics, or a report vs the mechanical
     count, or an ID set with unexplained missing cases) is fixed in
     the report BEFORE the preview is shown — wrong numbers must not
     reach Jira, the suite, or the human summary.
   - **REQUIRED PAUSE / CONFIRM.** Show what will be posted (both
     comments), to which sub-task, and — when the QA Service connector
     is present — the result write-back line (how many executed cases
     get a PASS/FAIL note in the suite). Post only after an explicit
     yes; the one confirmation covers Jira and QA Service.
   - **QA Service result write-back:** for every executed case, append
     the run outcome to its suite case notes — rules and exact note
     format: `qa-pipeline-docs/references/qa-service-publish.md` →
     "Result write-back". Never overwrite lifecycle `status` with a
     run result. Connector absent → skip with a note in the final
     response.
   - **Comment 1 — machine archive (for agents):** the full
     `<STORY>-code-review.md`, `<STORY>-api-testing.md`,
     `<STORY>-web-testing.md` and `<STORY>-run-report.md`, each inside
     its own fenced code block preceded by a plain `File: <name>` line —
     the same convention as the docs-phase archive comment, so agents
     can re-read the results from Jira. Do not shorten or reformat the
     file contents.
   - **Comment 2 — human summary (posted second, so it sits newest):**
     a short formatted summary per the template: overall verdict up
     top, stage-verdict table with counters, confirmed bugs (one line
     each), what needs a human, what was not tested here, and the
     run-health line. ≤30 lines, no walls of text — the detail lives
     in comment 1. Always post it, pass or fail.
   - Use comments (`addCommentToJiraIssue`, not a description
     overwrite) so nothing is lost.
   - If there is no QA sub-task (the no-sub-tasks fallback case) and
     the test cases came from files or the main issue, post both
     comments to the MAIN issue instead — same format, same confirm
     pause.
   - **Tracker note:** the connector cannot edit the docs-phase
     checkbox tracker, so it is NOT auto-ticked. The human summary is
     the source of truth for automated results; the tracker holds the
     human's manual verification. Remind the user of this in the final
     response so nobody expects ticked boxes.

7. **Offer to file the confirmed bugs** -- if the run produced confirmed
   bugs (web-testing `FAIL CONFIRMED` / api-testing `FAIL` or
   `FAIL CONFIRMED`), make ONE offer listing all the bugs; file only
   the ones the user confirms.
   - **Preferred path (knowledge-base installed):** hand the confirmed
     bugs to the `/knowledge-base` skill — it searches existing
     tickets/known issues first and creates properly routed Jira bugs;
     let its dedup check run before each creation.
   - **Default path (knowledge-base not installed):** draft each bug
     per **`references/bug-report-template.md`** (summary format,
     steps-to-reproduce from the test case, expected vs actual with
     the run evidence, environment/host, links to the story and QA
     sub-task). Search Jira for duplicates first
     (`searchJiraIssuesUsingJql` on the summary's key phrases + the
     component); show every draft to the user; create via
     `createJiraIssue` only after an explicit yes per bug. Never
     file silently.

8. **Close the loop — hand the story back.** After posting (and any
   bug filing), offer the matching Jira handoff. Never transition or
   reassign silently — show what will change and confirm first.
   - **Verdict ❌ FAIL or ⚠ PASS WITH GAPS with confirmed bugs:** offer
     to reassign the failing dev sub-tasks (or the story) back to
     their dev assignees, with a comment linking the human summary and
     the filed bug keys; apply the "back to dev" transition from
     `qa-pipeline-docs/references/publish-config.md` if one is
     configured there.
   - **Verdict ✅ PASS: the handback WAITS for the human.** Automated
     verdicts are provisional (the creator's own base rates: ~half of
     machine results wrong) — so do NOT post the "QA passed" story
     note or apply the "QA done" transition at this step by default.
     Both move to `qa-manual-results` step 4, after the manual round
     confirms the verdict. If the user explicitly wants a story note
     now, post the provisional variant — title it
     "✅ Automated QA passed — manual verification pending" (template
     note in `references/results-comment-template.md`) and apply no
     transition. A machine-only PASS must never be dressed as a final
     one.
   - Transitions are optional: when publish-config has none
     configured, skip transitions and only do the reassignment +
     comment. Before attempting any transition, verify it exists via
     `getTransitionsForJiraIssue`; if the configured name is not
     available, list the available ones and ask the user.

9. **Build the manual run sheet — run `qa-manual-runsheet` (stage 9).** Every
   ticket here is hand-tested after the machine finishes, so this is a
   real step, not an optional extra. Read
   `qa-manual-runsheet/SKILL.md` and follow it in full.

   **Why it belongs at the END of this phase, not in the docs phase.**
   The run sheet's value is that it tells the human what is *left*. It
   can only do that once the automated verdicts exist: it carries
   `Code review` / `API verdict` / `Ready?` per case, marks the
   runtime-verified Low/Medium rows as settled, turns High-risk and
   code-reading-only machine PASSes into short VERIFY (spot-check)
   rows, and leaves the tester the remainder. Run it
   after the docs phase and every verdict column is empty, so the tester
   walks all 89 cases blind — on a real ticket that was the difference
   between **89 rows and 11** (plus a handful of spot-checks).

   - **REQUIRED PAUSE.** This stage creates accounts and entities on a
     live event. Ask for the throwaway test event id and explicit
     authorisation to mutate it before provisioning anything. Never
     target an event carrying real client data, and never guess an event.
   - Runs AFTER the automated stages on purpose: 7 and 8 create their own
     ad-hoc data, so provisioning clean fixtures first would collide with
     them.
   - Feed it the verdict files from this run (`-code-review.md`,
     `-api-testing.md`, `-web-testing.md`) so settled rows are marked and
     the tester skips them.
   - Outputs `<STORY>-runsheet.xlsx`, `<STORY>-testdata.json` and
     `<STORY>-testdata-notes.md`. **These carry live credentials — they
     are git-ignored and must never be committed or attached to Jira.**
   - Report the account and entity counts, the ready / must-test /
     blocked split, and anything that could not be provisioned.

   Skip only if the user says they are not hand-testing this ticket.

   **Post-publish verification — always the last action of the run.**
   The analyzer ran at step 5, BEFORE publishing, bug filing, and the
   run sheet existed — so nothing it certified covers what steps 6–9
   actually did. Verify the final state now:
   - **Write-back landed:** connector present → `get_test_case` on a
     sample (all, if few) of the cases step 6 planned to annotate;
     confirm the run line is in `notes` and the count matches the
     plan. Connector absent → state that no durable per-case record
     exists beyond the Jira comments.
   - **Bugs traceable:** every FAIL / FAIL CONFIRMED across the three
     reports has either a filed bug key or an explicit "not filed —
     <reason>" line in the human summary. No silent FAILs.
   - **Comments exist:** both step-6 comments (archive + human
     summary) are on the sub-task — re-read, don't assume.
   - **Runsheet outputs exist** (unless the user skipped stage 9).
   Append the outcome as a `## Post-publish verification` section to
   `<STORY>-run-report.md` (✅/❌ per item) and include one line in the
   final response. A ❌ here is a real finding — fix it or tell the
   user, never bury it.

10. **Ingest the manual results — `qa-manual-results` (stage 10, deferred).**
    The human run happens after this orchestrator finishes — often days
    later, in a different chat. When the tester hands back the filled
    run sheet (or a TC/Result/Notes table), run `qa-manual-results`: it
    joins the results by TC id, reconciles them against what step 6
    published, and writes back to Jira + the suite **with explicit
    retractions** where the human overturned an automated verdict.
    End THIS run by telling the user that step exists: the published
    verdicts are provisional until the manual results are ingested.

## Between stages

- Keep chat output short: one line per hand-off.
- Each stage's own rules and templates apply unchanged.

## Final response

After posting, report: the files produced, the overall verdict and
confirmed bugs, confirmation that BOTH comments (archive + human
summary) were posted to the QA sub-task (with its key + URL), the QA
Service write-back counts (N PASS / M FAIL notes written, or "skipped —
connector not enabled") and any reconciliation changes applied at step
0, which
confirmed bugs were filed (via knowledge-base or the default path) or
listed for manual filing, and which handoff was performed (reassigned
to whom / transition applied) or that the user skipped it. In chat,
reuse the human-summary content rather than writing a third format.

Then, from step 9: the run-sheet path, how many cases the tester still
has to walk versus how many the machine settled, and the reminder that
the run sheet and provisioning record hold live credentials and stay out
of version control and Jira.
