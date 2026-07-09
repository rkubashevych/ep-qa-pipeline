---
name: code-review
description: >
  Sixth stage of task processing. Takes the test cases created by
  the qa-test-cases skill and the PR summary created by the
  pr-summary skill, checks each test case against the PR code and
  builds a compact results file with statuses and findings for the
  problem items. Use when the user says "code review",
  "check the implementation", "go through the code", or after the
  PR summary is finished.
---

# Code Review

Checks each test case against the PR code. The output is a
compact results table with findings for the FAIL items.

## Input

From the user you need:
1. The test-cases file `<ISSUEKEY>-test-cases.md` created
   by the qa-test-cases skill. In the same chat the file is available
   in the working directory automatically. If the chat is new —
   the user uploads the file into the chat.
2. The PR summary file `<ISSUEKEY>-pr-summary.md` created by
   the pr-summary skill. In the same chat it is available automatically.
3. One or more PR URLs or branch names. A Story usually has several
   sub-task PRs (backend + frontend); accept all of them. Review each
   test case against whichever PR implements it — backend test cases
   against the backend PR, frontend against the frontend PR(s). Record
   which PR each finding came from. The pr-summary file may already
   cover several PRs grouped by sub-task; use it as the navigation map.

The PR system is Bitbucket Cloud. Both the frontend and the backend
repos are on Bitbucket, so a PR may be either. The PR URL format is
`https://bitbucket.org/{workspace}/{repo}/pull-requests/{id}`,
for example `https://bitbucket.org/expoplatform/backend/pull-requests/123`.
Note that `{workspace}` and `{repo}` may be human-readable slugs OR
UUIDs in braces (e.g.
`https://bitbucket.org/%7B9274fcef-...%7D/%7B880a8c6f-...%7D/pull-requests/6966`);
parse and use whichever form the URL contains. The backend is a
PHP/Phalcon monolith; the frontend is the `portal-ui` repo (Next.js +
React, TypeScript, Material UI). The issue key follows the Jira format
`PROJECT-123` (for example `EP-1234`).

If any file is not provided — ask before starting.
If neither a PR URL nor a branch name is provided — ask.

If the user gives a branch name instead of a PR — work
with the branch directly via the git CLI or the Bitbucket API.
Do not search for a PR by branch.

Data sources for this skill:
- the test-cases file — the source of checks
- the pr-summary file — navigation through the PR
- the PR code via CLI or API — the source of evidence

All files are read-only.
Do not change, rewrite, or clean up their content.

If the test-cases file is missing — stop and tell
the user that the qa-test-cases skill must be run first.

If the pr-summary file is missing — work without it.
Look for the test-case implementations in the PR directly via CLI or API.

Do not go to the tracker, do not use external tools,
do not search the internet, do not use the browser.

## Rules

- All communication and the entire content of the output file are in English.
- Keep chat messages short.
- Read-only: do not change code, do not create commits, do not push,
  do not create PR comments, reviews, labels or statuses.
- Work only within the PR branch or the specified branch.
  Do not take code from main, the base branch, other branches
  or the general repository context.
- Check only the test cases from the file. Do not invent
  or interpret requirements yourself.
- Do not assess code quality, style, architecture, naming,
  tests, CI or refactoring — unless it is described
  in a test case.
- Do not look for bugs unrelated to the test cases.
- Do not analyze pre-existing code that was not changed in the PR.
- If a test case cannot be checked against the code —
  mark it QA, do not invent a result.

## Code access

The PR system is Bitbucket Cloud. Access the PR and the code
through the git CLI or the Bitbucket Cloud REST API.

- **Bitbucket Cloud → git CLI + REST API:** clone or fetch the
  branch with `git`, and use the Bitbucket REST API
  (`https://api.bitbucket.org/2.0/...`) for PR metadata and diffs.

> **Default to branch mode** — the branch name is the issue key (e.g.
> `EP-54610`). Token scopes, auth setup, repo names, and why PR-URL /
> REST mode usually 403s: see
> **`../pr-summary/references/bitbucket-access.md`** (the shared source
> of truth for Bitbucket access — edit it there, not inline here).

### Recommended flow

Use the shared command workflows in
**`../pr-summary/references/bitbucket-access.md`** ("Command
workflows" section) — PR mode (metadata → per-file diff → full file)
or branch mode (`git diff` / `git show`). In both modes, use the PR
summary to determine where to look and read the diff or full file
only for the files relevant to the test case at hand.

Read files only from the head branch of the PR.
Do not read files from the base branch, master or other branches.

### The PR summary as navigation

The PR summary shows which files were changed and what is in them.
Use it to quickly find where in the PR a specific test case
is implemented.

If you cannot find the implementation of a test case
in the files listed in the PR summary — look in the PR directly
via CLI or API. The PR summary may be incomplete — that is
not a reason to mark FAIL.

### If authenticated access is unavailable

Stop and tell the user to set up the auth (git credentials,
`BB_EMAIL`/`BB_API_TOKEN`, token scopes, the app-password deprecation
— all in `../pr-summary/references/bitbucket-access.md`).
Authenticated curl against the Bitbucket REST API is a supported
path; what is forbidden is working around missing auth (the browser,
scraping, other sources).

### Large PRs

If more than 20 files were changed:
- Use the PR summary as a navigation map —
  do not read files blindly.
- Group test cases by file: read a file once
  and check all the test cases that touch it.
  Do not re-read a file for each test case.
- Configs, styles, tests — read only if there is
  a direct test case for them.

## Review process

For each test case (TC-REQ-X.Y):

1. **Understand** — which scenario the test case describes:
   precondition, steps, expected result.
2. **Locate** — use the PR summary to determine which files
   are relevant. Read the diff or the full file.
3. **Assess** — whether the code implements the behavior
   described in the test case. Compare the expected result
   of each step with what the code does.
4. **Classify** — assign a status.

### What to look for in the code

ExpoPlatform splits a story into separate frontend and backend
sub-tasks, each with its own Bitbucket PR. First determine which kind
of PR you are reviewing — from the sub-task type, the repo, or the
files in the PR summary (PHP/Phalcon vs frontend sources) — then apply
the matching list. A PR may occasionally touch both.

**Backend (PHP/Phalcon monolith):**
- Presence of elements: controllers and actions, service methods,
  model fields, Volt view variables/labels, response payload fields,
  messages.
- Conditional logic: if/else, switch, guard clauses, ACL/permission
  checks, feature flags.
- States: default, active, disabled, error, empty — as represented in
  model attributes, status fields, or response flags.
- Validations: Phalcon validators, rules, messages, triggers, boundary
  values.
- Data: model fields, column types, formats, mappings, API/response
  contracts, DB migrations.
- Binding: whether the logic is wired to the correct route, controller
  action, DI service, model, or Volt template.

**Frontend (`portal-ui` — Next.js + React, TypeScript, Material UI):**
- Presence of elements: React components (incl. MUI components like
  Button, TextField, Dialog), fields, labels, texts, messages,
  tooltips, icons.
- Conditional logic: conditional rendering (`&&`, ternaries), hooks
  (`useState`, `useEffect`, `useMemo`), guards, permission/role checks,
  feature flags.
- States: default, active, disabled, error, loading, empty — as held
  in component state, context, or props; check `disabled`/`readOnly`
  props where behaviour depends on them.
- Validations: react-hook-form rules and resolvers, validation
  messages, triggers, boundary values.
- Data: request/response field names and formats, API contracts,
  mapping/transform logic (e.g. reading the correct key like
  `settings.logo` vs `do_not_allow_logo`, inverting a boolean),
  prepareData/transform helpers, TypeScript types.
- Binding: whether the element is wired to the correct Next.js
  route/page, component, and API endpoint.

**Both:**
- Removals: whether what should have been removed was actually removed
  (e.g. an old field/key no longer read or written anywhere).

### FAIL vs absence from the diff

The absence of code in the diff ≠ an automatic FAIL.
The code may already exist in the branch unchanged.
Before marking FAIL — check the full file
from the PR branch via CLI or API.

FAIL only when there is concrete evidence:
- the code does something other than what the test case expects
- the code removes or breaks something that should work

## Classification

Each test case gets one status:

- `PASS` — the code confirms that the behavior described
  in the test case is implemented.
- `FAIL` — the code shows that the behavior is not implemented,
  is implemented incorrectly, or contradicts the expectations.
- `QA` — cannot be checked against the code. Requires
  manual verification: runtime behavior, visual
  layout, real data, integrations, permissions.
- `N/A` — the item does not apply to this PR.
  The code related to this requirement is absent from the PR.

Rules:
- Do not mark PASS if there is any doubt — prefer QA.
- Do not mark FAIL without concrete evidence from the code.
- Do not mark N/A without concrete evidence from the code.
- QA is a normal status. Many UI/UX and runtime
  checks cannot be confirmed from code alone.

## Output file

Create the file `<ISSUEKEY>-code-review.md` in the working
directory and hand it to the user for download.

The file stays in the working directory — the next skill
in the same chat picks it up automatically.

If the file already exists — delete it completely and create a new one.

The file structure template is in references/output-template.md.

## Verification before saving

Before saving, check:

- The number of test cases in the results table equals
  the number of TC-REQ items in the test-cases file. If it does not match —
  find the missing ones and add them before saving.
- The order of the test cases in the table matches the order
  in the test-cases file.
- Every FAIL has a corresponding entry in Findings
  with a concrete file and line.
- Every N/A has a corresponding entry in Findings with a reason.
- There is no FAIL without evidence from the code.
- There is no N/A without evidence from the code.

## Final answer

After saving the file, report:
- The path to the saved file
- PASS / FAIL / QA / N/A counters
