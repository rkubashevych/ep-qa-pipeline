---
name: pr-summary
description: >
  Fifth stage of task processing. Reads a PR via CLI or API
  and builds a structured summary of the changes — a PR map
  for the code-review skill. Use when the user says "read the PR",
  "look at the PR", "PR summary", "what's in the PR", or after
  the test cases are finished and before code review.
---

# PR Summary

Reads a PR via CLI or API and builds a structured summary
of the changes: which files were changed, which components
are affected, what was added, removed and modified.

The summary is a navigation map for the code-review skill.
Code review uses it to know where in the PR to look for
the implementation of each test case.

## Input

From the user you need:
- One or more PR URLs or branch names.

A single ExpoPlatform Story is split into several sub-tasks (backend +
one or more frontend), each with its own PR/branch. When the work spans
several sub-tasks, accept all of them in one run and produce one
combined summary, with the changed files **grouped by PR/sub-task**
(label each group with its issue key/branch, e.g. `EP-47975 (backend)`,
`EP-54610 (frontend)`). Use the issue key as the `<ISSUEKEY>` in the
filename — the parent Story key if given, otherwise ask which key to
use for the combined file.

The PR system is Bitbucket Cloud. Both the frontend and the backend
repos are on Bitbucket, so a PR may be either. The PR URL format is
`https://bitbucket.org/{workspace}/{repo}/pull-requests/{id}`,
for example `https://bitbucket.org/expoplatform/backend/pull-requests/123`.
Note that `{workspace}` and `{repo}` may be human-readable slugs OR
UUIDs in braces (e.g.
`https://bitbucket.org/%7B9274fcef-...%7D/%7B880a8c6f-...%7D/pull-requests/6966`);
parse and use whichever form the URL contains. The backend is a
PHP/Phalcon monolith; the frontend is the `portal-ui` repo (Next.js +
React, TypeScript, Material UI).

If neither a PR URL nor a branch name is provided — ask
before starting work.

If the user gives a branch name instead of a PR — work
with the branch directly via the git CLI or the Bitbucket API.
Do not search for a PR by branch.

This skill does not read the tracker, so derive the issue key for the
output filename from what you already have: look for a `PROJECT-123`
pattern (e.g. `EP-1234`) in the source branch name (e.g.
`feature/EP-1234-...`) or the PR title. If you find one, use it as
`<ISSUEKEY>`. If you cannot find an issue key, ask the user for it
before saving.

Data sources for this skill:
- The PR via CLI or API — the only source.

Do not go to the tracker, do not use external tools,
do not search the internet, do not use the browser.
Do not read requirements, checklist or test-case files —
this skill works only with code.

## Rules

- All communication and the entire content of the output file are in English.
- Keep chat messages short.
- Read-only: do not change code, do not create commits, do not push,
  do not create PR comments, reviews, labels or statuses.
- Work only within the PR branch or the specified branch.
  Do not take code from main, the base branch, or other branches.
- Describe what was changed, not how it was changed. Do not comment
  on code quality, style, architecture or naming.
- Do not compare the changes against the task requirements. The skill
  does not know the requirements — it only sees the code.
- After saving the file — stop. Do not continue
  into code review or analysis.

## Code access

The PR system is Bitbucket Cloud. Access the PR through the
git CLI or the Bitbucket Cloud REST API.

- **Bitbucket Cloud → git CLI + REST API:** clone or fetch the
  branch with `git`, and use the Bitbucket REST API
  (`https://api.bitbucket.org/2.0/...`) for PR metadata and diffs.

> **Default to branch mode** — the branch name is the issue key (e.g.
> `EP-54610`). Token scopes, auth setup, repo names, and why PR-URL /
> REST mode usually 403s: see **references/bitbucket-access.md** (the
> shared source of truth for Bitbucket access — code-review points to
> the same file; edit it there, not inline here).

### Workflow

Use the shared command workflows in
**references/bitbucket-access.md** ("Command workflows" section):

- **PR mode:** parse the URL → metadata → diffstat → per-file diff →
  full file from the head branch when the diff is not enough. Read
  file by file, not the whole diff at once.
- **Branch mode:** `git fetch` + `git diff --name-only` for the file
  list, per-file `git diff`, `git show` for full content.

Read files only from the head branch of the PR. Do not read files from
the base branch, master or other branches. Do not take code from the
general repository context.

### Large PRs

If more than 20 files were changed — do not read every diff.
Read the diff only for the key files (components, logic,
API). Configs, styles, tests — describe by file name
without a diff.

### If authenticated access is unavailable

Stop and tell the user to set up the auth (git credentials,
`BB_EMAIL`/`BB_API_TOKEN`, token scopes, the app-password deprecation
— all in references/bitbucket-access.md). Authenticated curl against
the Bitbucket REST API is a supported path; what is forbidden is
working around missing auth (the browser, scraping, other sources).

## What to describe for each file

For each changed file determine:

- **Category:** component, API/endpoint, model/type,
  utility, style, config, test, migration, or other.
- **What changed:** briefly — what was added, removed or
  modified. Do not rewrite the code, describe the essence of
  the change. State the specific names of functions, components,
  hooks, endpoints that were changed or added.

If several files change one entity (a component +
its styles + its test) — group them under that entity.

## Blast radius (shared files)

The ticket-scoped pipeline does not do regression testing, so this is
the one place a regression risk can be made visible. While reading the
diffs, flag any changed file that is **shared** — consumed by flows
beyond this ticket:

- Backend: shared services, base models/traits, ACL/permission classes,
  helpers used across controllers, DB migrations, response envelopes.
- Frontend: shared components/hooks/utils, API client modules,
  types/contracts imported by multiple pages, theme/config.

List them in the "Shared / high blast-radius files" section of the
output, each with one line naming what else consumes it — based only on
what the code shows (imports, usages, table names). Do not speculate,
do not analyze unchanged code beyond identifying consumers. If nothing
shared was touched, write "None".

## Verification before saving

Before saving, check:

- Every changed file from the PR is present in the summary.
  Compare the number of files in the change list with the number
  of files in the summary.
- A category is assigned to every file.
- The change descriptions are short and specific — not "changed
  the file", but "added a region parameter to the filterLeads function".

## Output file

Create the file `<ISSUEKEY>-pr-summary.md` in the working
directory and hand it to the user for download. The issue key
follows the Jira format `PROJECT-123` (for example `EP-1234`).

The file stays in the working directory — the next skill
in the same chat picks it up automatically.

If the file already exists — delete it completely and create a new one.

The file structure template is in references/output-template.md.

## Final answer

After saving the file, report:
- The path to the saved file
- The number of changed files
- The number of shared / high blast-radius files flagged (or "none")