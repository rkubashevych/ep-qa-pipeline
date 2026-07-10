---
name: qa-pipeline-code
description: >
  Orchestrator for the code + UI half of the QA pipeline (stages 5, 6,
  7, 8). Given a Story key, reads the test cases from the story's QA
  sub-task (published by qa-pipeline-docs) and derives the dev branches
  from the backend/frontend sub-tasks, then runs pr-summary ->
  code-review -> api-testing -> web-testing -> run-analyzer, and posts the results back
  to the QA sub-task. Auto-advances, pausing only for the browser login
  and the Jira write confirmation. Use it when the user says "run the QA
  code pipeline", "review the PRs and test in the browser", "do code
  review and UI testing for a ticket". Run in a FRESH chat after
  qa-pipeline-docs.
---

# QA Pipeline -- Code & UI (stages 5, 6, 7, 8)

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
and the e2e `.env` (stage 7). Before running anything, check they are
reachable (a mounted folder holding them, or the env vars set). If
they are not, say so NOW and ask the user to either mount the folder
that has them or run this phase from Claude Code (see MAINTAINERS
"Where to run each stage") — do not discover this mid-run at stage 5.

**Same-session shortcut:** if the `<STORY>-test-cases.md` (and
checklist) files are already in the working directory — e.g. you ran
`qa-pipeline-docs` in this same chat — use them directly and skip the
Jira read-back below. Only pull from Jira when the files are not present
(the fresh-chat case).

Otherwise, using the Atlassian connector and the Story key:

1. **Test cases / checklist.** Find the story's QA sub-task created by
   the docs phase: `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype = "QA sub-task"` (prefer the newest
   with label `qa-pipeline` or a `[QA-PIPELINE]` summary). Read its
   description (and comments) and extract the fenced code blocks holding
   the checklist and test cases. Write them back to the working
   directory as `<STORY>-checklist.md` and `<STORY>-test-cases.md` so
   the stage skills can consume them.
   - If no pipeline QA sub-task exists, tell the user to run
     `qa-pipeline-docs` first (or to attach the test-cases file).
   - **Resume mode:** if the sub-task also has a results **archive
     comment** from an earlier partial run (fenced blocks labeled
     `File: <STORY>-code-review.md` etc. — see
     `references/results-comment-template.md`), extract those files to
     the working directory too. A stage whose report file exists is
     done — skip it and continue from the first missing stage
     (typically web-testing in Cowork after 5–7 ran in Claude Code),
     unless the user asks to re-run. Tell the user which stages were
     restored vs pending before continuing.
2. **Dev branches.** `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype in ("Backend sub-task","Frontend
   sub-task")`. Each dev sub-task's **key is its branch name** (e.g.
   `EP-47975`, `EP-54610`). Use these as the branches for branch mode —
   no PR URLs needed. List them for the user before starting.

## Split runs (Claude Code ↔ Cowork)

Stages 5–7 need repo/API creds (Claude Code); stage 8 needs the Chrome
extension (Cowork). When the current environment cannot run everything:
run what it can, post the two step-6 comments marked **PARTIAL** (per
the template — name the pending stages), then start a fresh chat in the
other environment with the same Story key. Step 0's resume mode
restores the finished reports from the archive comment, and the last
environment posts the final archive + summary as a NEW pair — existing
comments are never edited.

## How it runs

Execute each stage by reading its `SKILL.md` and following it in full.

1. **pr-summary** -- run on the derived branches (branch mode; the
   repository-scoped token is enough). Groups changes per sub-task.
   Produces `<STORY>-pr-summary.md`.

2. **code-review** -- run on the test-cases + pr-summary across all the
   branches. Keys results by REQ-ID with a PR/branch column.
   Produces `<STORY>-code-review.md`.

3. **api-testing** -- run on the code-review + test-cases. Executes the
   `[API]` cases (status QA/FAIL) against the REST API via curl using
   `.env` credentials; covers admin REST, legacy admin-panel and
   exhibitor-token (frontend) cases. Read-only by default; any write
   snapshots-and-reverts or uses a throwaway entity.
   - **PAUSE** if `.env` (ADMIN_BASE_URL, ORGANIZER_API_KEY, EVENT_ID,
     admin creds) or a per-event frontend host is missing.
   - Produces `<STORY>-api-testing.md`.

4. **web-testing** -- run on the code-review + test-cases.
   - Executes only `[UI]` test cases. `[API]` cases are handled by
     stage 3 (api-testing); only `[mobile]`/`[export/email]` remain
     under "Not executed here".
   - **PAUSE** for browser login (per `login-config.md`, or the per-task
     host) and any unknown navigation path.
   - Produces `<STORY>-web-testing.md`.

5. **qa-run-analyzer** -- run automatically; also reads
   `<STORY>-api-testing.md`. Writes `<STORY>-run-report.md`.

6. **Post results back to the QA sub-task** -- TWO comments, per
   **`references/results-comment-template.md`** (formats live there,
   not here):
   - **REQUIRED PAUSE / CONFIRM.** Show what will be posted (both
     comments) and to which sub-task; post only after an explicit yes.
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
   - **Tracker note:** the connector cannot edit the docs-phase
     checkbox tracker, so it is NOT auto-ticked. The human summary is
     the source of truth for automated results; the tracker holds the
     human's manual verification. Remind the user of this in the final
     response so nobody expects ticked boxes.

7. **Offer to file the confirmed bugs** -- if the run produced confirmed
   bugs (web-testing `FAIL CONFIRMED` / api-testing `FAIL` or
   `FAIL CONFIRMED`), offer to hand them to the `/knowledge-base` skill,
   which searches for existing tickets/known issues first and then
   creates properly routed Jira bugs. One offer listing all the bugs;
   file only the ones the user confirms, and let knowledge-base's own
   dedup check run before each creation. If the knowledge-base skill is
   not installed, just list the bugs with their evidence so the user can
   file them manually. Do not create bug tickets directly from this
   orchestrator.

## Between stages

- Keep chat output short: one line per hand-off.
- Each stage's own rules and templates apply unchanged.

## Final response

After posting, report: the files produced, the overall verdict and
confirmed bugs, confirmation that BOTH comments (archive + human
summary) were posted to the QA sub-task (with its key + URL), and
which confirmed bugs were filed via knowledge-base (or listed for
manual filing). In chat, reuse the human-summary content rather than
writing a third format.
