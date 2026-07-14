# ExpoPlatform QA Pipeline — Claude Skills

An end-to-end QA pipeline built from chained Claude skills, adapted from the DOU Live "AI pipeline for testing tasks" templates (Anna Kurkotova, iSpeedtoLead). Each skill takes the previous skill's output file as its input, so a task flows from a Jira ticket all the way through to a browser-verified test report. A human reviews and confirms the output of each stage before it feeds the next (human-in-the-loop).

## Configuration applied

These skills were adapted for ExpoPlatform's stack:

- **Tracker:** Jira (Atlassian Cloud), via the connected Atlassian tools. Ticket keys use the `PROJECT-123` format, e.g. `EP-1234` (`https://expoplatform.atlassian.net/browse/EP-1234`).
- **Code/PRs:** Bitbucket Cloud — **both** the backend (PHP/Phalcon monolith) and the frontend (`portal-ui`: Next.js + React, TypeScript, Material UI) are on Bitbucket. A story is split into separate frontend and backend sub-tasks, each with its own branch (named after the issue key) and PR, so the pipeline runs per sub-task. PR URLs use `https://bitbucket.org/{workspace}/{repo}/pull-requests/{id}` (workspace/repo may be slugs or UUIDs). Branch-based work uses git CLI / the Bitbucket REST API; base branch is `master`. API access uses a Bitbucket **API token** (`BB_EMAIL` + `BB_API_TOKEN`) — app passwords are deprecated and disabled as of June 9, 2026.
- **Language:** all skill instructions translated to English.

## Pipeline stages

| # | Skill | Input | Output | Suggested settings |
|---|-------|-------|--------|--------------------|
| 1 | `task-context` | Jira ticket key/URL | `<KEY>-context.md` | Sonnet · Medium |
| 2 | `requirements-grooming` | `<KEY>-context.md` | `<KEY>-requirements.md` | Opus · High · thinking on |
| 3 | `qa-checklist` | `<KEY>-requirements.md` | `<KEY>-checklist.md` | Sonnet · Medium |
| 4 | `qa-test-cases` | `<KEY>-checklist.md` | `<KEY>-test-cases.md` | Sonnet · High |
| 5 | `pr-summary` | PR URL / branch | `<KEY>-pr-summary.md` | Sonnet · Medium |
| 6 | `code-review` | test-cases + pr-summary | `<KEY>-code-review.md` | Opus · High · thinking on |
| 7 | `api-testing` | code-review + test-cases (+ `.env`) | `<KEY>-api-testing.md` | Sonnet · High |
| 8 | `web-testing` | code-review + test-cases | `<KEY>-web-testing.md` | Sonnet · High |

> Per-stage settings apply when running a stage on its own. The orchestrators (`qa-pipeline-docs`, `qa-pipeline-code`) instead recommend one setting for the whole run (Opus · High · thinking on) to avoid switching models mid-run — with subagent dispatch, heavy stages get fresh context anyway.

> **Stage 7 = `api-testing`.** Executes the `[API]` test cases directly against the ExpoPlatform REST API (curl / HTTP, no browser), so API cases are verified instead of routed out. Credentials are read at runtime from the e2e `.env` — never hardcoded. Stage 8 (`web-testing`) then runs only `[UI]` cases; `[mobile]` / `[export/email]` remain routed out. See `skills/api-testing/references/api-testing-reference.md` for the full method (auth contexts, route discovery, write-safety, frontend/exhibitor-token cases).

> Two one-command orchestrators wrap these: **`qa-pipeline-docs`** (stages 1–4 + Jira publish) and **`qa-pipeline-code`** (stages 5 → 6 → 7 → 8 + `qa-run-analyzer` + Jira post).

## How the flow works

1. **task-context** — pulls the Jira ticket (description, acceptance criteria, comments, attachments, links) and consolidates it into one enriched Markdown file: the single source of truth for everything downstream.
2. **requirements-grooming** — reviews those requirements with a QA grooming eye (coverage, clarity, contradictions, risks, missing detail), numbers them, and produces a clean requirements file. Reads only the context file — no tracker, no internet.
3. **qa-checklist** — decomposes each numbered requirement into atomic checks.
4. **qa-test-cases** — turns the checklist into concrete test cases (steps, inputs, expected results). The checklist says *what* to check; the test case says *how*.
5. **pr-summary** — reads the Bitbucket PR (or branch) and builds a navigation map of the changes for the reviewer.
6. **code-review** — verifies each test case against the PR code and produces a compact pass/fail table with findings for failures.
7. **api-testing** — executes the `[API]` cases (code-review QA/FAIL items) against the running REST API via curl using `.env` credentials; covers admin REST, legacy admin-panel, and exhibitor-token (frontend) cases. Read-only by default; any write snapshots-and-reverts or uses a throwaway entity. Pauses if `.env` / a per-event frontend host is missing.
8. **web-testing** — executes the `[UI]` QA items and any failed code-review items in a real browser (Chrome extension), confirming bugs in the UI, and writes a detailed report.

## Before you run

Each skill folder still has a `setup-guide.md` with the remaining team-specific choices to confirm:

- **Confluence access** — Acceptance Criteria live on Confluence pages linked from the ticket, so the Atlassian connector must have **Confluence enabled**, not just Jira. (No custom-field ID needed — stage 1 reads the linked Confluence page directly.)
- **Bitbucket API token** — set `BB_EMAIL` (your Atlassian email) and `BB_API_TOKEN`. App passwords no longer work (disabled June 9, 2026). A `read:repository`-scoped token (like the existing `bitbucket-git-cli`) is enough for **branch mode** (give the skill the branch = issue key, e.g. `EP-54610`). **PR-URL mode** also needs `read:pullrequest:bitbucket` — add it via a new "with scopes" token, or just use branch mode. Workspace/repo in PR URLs may be slugs or UUIDs — both are handled.
- **web-testing login** — `web-testing/references/login-config.md` ships filled in for the ExpoPlatform e2e alpha (`e2e-testing-alpha2`), reading credentials from env vars / the e2e `.env` (`VISITOR_EMAIL`/`VISITOR_PASSWORD`, `ADMIN_USERNAME`/`ADMIN_PASSWORD`) — never inline them, never commit them. Adopting for another product: replace the URLs and field descriptions with yours.
- **Trigger phrases** — adjust the `description` frontmatter in each `SKILL.md` to match how your team naturally phrases requests.
- **Notifications (optional)** — set `QA_PIPELINE_NOTIFY=1` in your environment to get a desktop alert when a long run finishes or pauses for input (Claude Code hooks; `hooks/hooks.json` + `scripts/notify.py`). Off by default.

## Where to run each stage

Stages 1–4 (ticket → context → requirements → checklist → test cases) chain naturally in **one chat**, since each output file stays in the working directory for the next skill. Stage 5 (`pr-summary`) switches from reading the ticket to reading code; the recommended practice is to **start a fresh chat there** — no files need carrying: `qa-pipeline-code` Step 0 reads the test cases (and, on resume, earlier stage reports) back from the QA sub-task's archive comments on Jira. Runs can be **split across environments** (5–7 in Claude Code, 8 in Cowork): the first environment posts PARTIAL results, the second resumes from them and posts the final pair.

## Multi-surface, multi-PR features

ExpoPlatform features span more than one surface and one repo, so the pipeline accounts for that:

- **Sub-task gathering** — fed a parent Story, stage 1 pulls the child sub-tasks (backend / frontend / QA) and folds their detail in, since the concrete specs live there.
- **Channel tags** — every checklist item and test case is tagged `[UI]`, `[API]`, `[mobile]`, or `[export/email]`. `[UI]` items run in the browser (web-testing); `[API]` items run against the REST API (api-testing); `[mobile]` / `[export/email]` are explicitly routed under "Not executed here" rather than dropped (exception: an `[export/email]` artifact fetchable over HTTP, like an XLS/CSV export endpoint, may be executed by api-testing).
- **Multi-PR review** — stages 5–6 accept several sub-task PRs (one backend + one or more frontend) for a single Story and produce a combined review keyed by REQ-ID, with a PR column showing which PR each result came from.
- **Per-task host** — web-testing accepts a task-specific test host (e.g. an alpha host named in the QA sub-task), overriding the default site in `login-config.md`.
- **Blast radius** — stage 5 flags changed **shared** files ("Shared / high blast-radius files" in the pr-summary) and the run-analyzer surfaces them as a 🟡 regression-risk note, since the pipeline itself is strictly ticket-scoped.
- **Bug filing** — after the code phase, `qa-pipeline-code` offers to file confirmed bugs: via the `/knowledge-base` skill when installed (dedup + routed Jira bugs), otherwise directly per `references/bug-report-template.md` (dedup search → draft → user confirms → `createJiraIssue`). Never silently. Step 8 then offers the handoff — reassign to dev on FAIL / "QA done" transition on PASS (configurable in publish-config.md).

Mobile (Android/iOS) and non-HTTP outputs (exports, emails, integrations) are generated and tracked as test cases but are **not** auto-executed — they surface as routed work for the right tool or owner. (`[API]` cases are auto-executed by stage 7, `api-testing`.)

## Installing the skills

This repo is a Claude **plugin** (`.claude-plugin/plugin.json`); each folder under `skills/` is one skill. Install the whole plugin (Settings → Capabilities / your plugin marketplace) so every stage plus the `qa-pipeline-docs` and `qa-pipeline-code` orchestrators arrive together. They run in sequence within a chat, each output file staying in the working directory for the next stage.

## Maintaining / updating

**This repo is the single source of truth** — the installed copy is a read-only cache; never edit it. To change, add, or wire a stage, and to publish a new version, follow **[MAINTAINERS.md](MAINTAINERS.md)** (it also has a "where to look when something's off" map and the known gotchas). Any fresh session should read that file first.
