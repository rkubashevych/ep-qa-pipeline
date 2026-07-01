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
2. **Dev branches.** `searchJiraIssuesUsingJql` with
   `parent = <STORY> AND issuetype in ("Backend sub-task","Frontend
   sub-task")`. Each dev sub-task's **key is its branch name** (e.g.
   `EP-47975`, `EP-54610`). Use these as the branches for branch mode —
   no PR URLs needed. List them for the user before starting.

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

6. **Post results back to the QA sub-task** -- 
   - **REQUIRED PAUSE / CONFIRM.** Show what will be posted and to which
     sub-task; post only after an explicit yes.
   - Add a **comment** (`addCommentToJiraIssue`) to the same QA sub-task
     used in Step 0, containing: the code-review verdict
     (PASS/FAIL/QA/N/A), the api-testing verdict (PASS/FAIL/PARTIAL/
     BLOCKED/QA + any endpoint-mapping corrections), the web-testing
     verdict and confirmed bugs, what was routed to "Not executed here",
     and the run-report summary. Use a comment (not a description
     overwrite) so nothing is lost.

## Between stages

- Keep chat output short: one line per hand-off.
- Each stage's own rules and templates apply unchanged.

## Final response

After posting, report: the files produced, the code-review, api-testing
and web-testing counters, the overall verdict and confirmed bugs, what
was routed to non-UI channels, and confirmation that the QA sub-task was
updated (with its key + URL).
