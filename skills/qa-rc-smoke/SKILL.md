---
name: qa-rc-smoke
description: >
  The QA pipeline's release-candidate mode. Given the RC regression
  ticket ("[Regression] RC release Prod <date>", auto-generated, its
  scope items linked in the description) or a list of keys plus "are
  these on RC", it checks each item on the RC environment at smoke
  depth: the code is on the RC branch of each repo, the RC hosts serve
  that build, and the item's core behaviour holds at runtime (guest
  API first, admin UI with the user signed in, no saves). It records
  one QA Service test run (env rc) over the cases it exercised, writes
  <KEY>-rc-smoke.md and, on confirmation, one results comment on the
  RC ticket. Never a sign-off. Use when the user says "smoke test the
  RC", "check these items are on RC", "RC regression for EP-1234",
  "are the release items deployed to rc", or pastes the RC regression
  ticket. Do NOT use for a first run or retest of one ticket on alpha
  (qa-pipeline-code), a full regression suite run (CI), or checking
  production (refused — production is never a test target).
---

# QA RC Smoke — is the release candidate carrying the release?

> **Tool names:** `getJiraIssue` / `searchJiraIssuesUsingJql` /
> `addCommentToJiraIssue` are Atlassian MCP connector tools; `search` /
> `list_test_runs` / `list_releases` / `create_test_run` /
> `record_case_result` belong to the QA Service connector; `browser_*`
> are the Playwright MCP's. Prefixes vary per install — match by tool
> name.

The question this mode answers, per scope item: *is it on RC, and does
it work there?* Three layers of evidence, in this order, and the report
keeps them apart:

1. **Code** — the change is on the repo's RC branch (the fix commit is
   an ancestor, its markers are in the files, deleted files are gone).
2. **Served build** — the RC host actually serves that build (the
   portal chunk or admin bundle carries the fix's string). Code on the
   branch is not code on the host.
3. **Runtime** — the item's core cases, re-run on RC at smoke depth.

It exists because it was run by hand three times, each time without a
record anywhere but a local file and a Jira comment: EP-53978
(2026-09-04), EP-57431 (2026-09-18) and EP-57782 (2026-09-29). The
third one is the method below (CHANGELOG 0.46.0).

## Input

- **The RC regression ticket** (a Jira Task whose summary starts
  `[Regression] RC release`). Its description lists the scope items as
  links and names the release (`Prod <date>`) and a total count.
  Cross-check the count with JQL `fixVersion = "<release>"`. A
  mismatch is reported, never silently resolved: the description names
  the scope, and the fixVersion list is only a check on it.
- **Or a list of keys** from the user. Then the release comes from
  their common `fixVersion`, and the Jira comment goes to the ticket
  the user names, or nowhere.
- The run folder is `runs/<RC-KEY>/` under `$EP_QA_HOME`
  (`../qa-pipeline/references/data-locations.md`). The report is
  `<RC-KEY>-rc-smoke.md` in that folder. A second smoke of the same
  release appends a dated section; it does not overwrite.

## How it runs

Post one short line per step boundary (`Step <n>/6 done — <name>`).
The method for every step is in `references/rc-smoke-method.md`. Read
it before step 1.

0. **Read state, per item** — read-only. Type and status, the item's
   run folder (`runs/<ITEM>/r<N>/`: the pr-summary names the repos,
   PRs, fix commits and changed files, and the human summary gives the
   last verdict), its QA Service suite (`search {kinds:["suite"]}`, by
   the prefix in its case ids), its latest test run (`list_test_runs`),
   and its open-items ledger rows. **An item with no pipeline run is
   still in scope.** Its markers come from the PR itself (`pr-summary`
   in branch mode, read only). Say so in its row, and give it no
   runtime cases beyond the ticket's own repro.
1. **Plan and confirm (one pause).** Show, per item: the repos and
   markers to check, the runtime probes (named by stable id), which
   probes need the user signed in to the RC admin, and which need a
   setting changed on a shared RC event. Show the hosts, taken from the
   env file's `RC_*` block and each checked against `ALLOWED_HOSTS`
   (`../qa-pipeline/references/environment.md`).
   A production host is refused. Nothing runs before a yes. The yes
   covers reads only. **Every setting change is asked for separately,
   when it is reached.**
2. **Code on the RC branch** — discover the RC branch of each repo
   with a Bitbucket refs query every run (names drift). Record
   `branch @ commit, date` and check each marker.
3. **Served build** — fetch the RC host's bundle and grep it for the
   fix's string (portal: the page's `_next/static` chunks; admin: the
   `adminv2/assets/index-*.js` bundle that the signed-in admin page
   loads). A backend-only item has no bundle; its runtime probe is the
   evidence.
4. **Runtime smoke** — guest API probes first (no credentials). Then
   browser checks: a guest in a clean context, and admin with **the
   user signed in by hand** in the Playwright browser. No saves:
   dialogs are cancelled and pages are left unsaved. A precondition
   that needs a setting changed follows "Setting changes" in the method.
   A mocked response counts only once a positive control has shown that
   the instrument can see what it is looking for.
5. **Record** — one QA Service test run over exactly the cases step 4
   exercised (`../qa-pipeline/references/test-runs.md`, with the RC
   specifics in the method: title, `env: rc`, release, catalogue ids,
   principal). Write `<RC-KEY>-rc-smoke.md` from the template in the
   method.
6. **Publish (one pause)** — show the Jira comment (Markdown, not wiki
   markup), post it on a yes, with the QA Service run as a bare
   `Run: https://qa-service.expoplatform.com/expoplatform/test-runs/<run id>`
   line. Never
   transition the ticket and never write "signed off". The sign-off is
   the release owner's decision; this comment is the evidence for it.

## Rules

- **Read-only by default.** No fixtures, no config changes, no saves.
  A setting change on a shared RC event needs its own yes. It is made
  by the user by hand when the permission layer refuses the agent
  (EP-57782: it refused a replay of the Exhibitor settings form). Its
  precondition is verified before the check, and the restore is
  verified after it, both by a guest probe with a timestamp.
- **Three layers, never merged.** "Present" (code + build) and "works"
  (runtime) are separate columns. An item whose runtime check could
  not tell pass from fail is reported as present with runtime
  inconclusive, never as a pass.
- **The instrument proves itself first.** On EP-57782 a mocked 401/500
  on an SSR-rendered listing produced no toast, even in the control
  cases. That result meant nothing. Recording it as "no toast = pass"
  would have been a false pass.
- **Never print a URL's query string from an admin page.** The admin-ui
  iframe `src` carries a session `token`. It was echoed on EP-57509 and
  again on EP-57782. Read `frame.url()` only after stripping the query
  string. If one is printed anyway, tell the user to sign out of that
  admin.
- **No new evidence of a defect is filed from here without the user.**
  A smoke FAIL is shown, reproduced once, and offered as a bug
  (`../qa-pipeline-code/references/bug-report-template.md`). The
  `fail` verdict is recorded only after the user has seen it, because
  `record_case_result` files a Jira defect on `fail`.
- **Scope is the ticket's.** Risk rows and open questions carried from
  an item's earlier rounds are listed as "still open, unchanged". They
  are not re-run unless the user adds them.

## Final response

Two lines first: the verdict (`no blockers` / `<n> blockers`) and one
line per item (present? runtime?). Then the report path, the QA Service
run id, the Jira comment id, and anything left in a changed state
(there should be nothing; if a setting is still flipped, that is the
first line).
