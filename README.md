# ExpoPlatform QA Pipeline — Claude Skills

An end-to-end QA pipeline built from chained Claude skills, adapted from the DOU Live "AI pipeline for testing tasks" templates (Anna Kurkotova, iSpeedtoLead). Each skill takes the previous skill's output file as its input, so a task flows from a Jira ticket all the way through to a browser-verified test report. The orchestrators auto-advance with default decisions and pause for a human at the points that write outside the run folder — the publish to QA Service and Jira, a login or event-auth step, filing a bug — while the human round (stages 9–10) is where a person walks the cases and settles the verdicts.

## Configuration applied

These skills were adapted for ExpoPlatform's stack:

- **Tracker:** Jira (Atlassian Cloud), via the connected Atlassian tools. Ticket keys use the `PROJECT-123` format, e.g. `EP-1234` (`https://expoplatform.atlassian.net/browse/EP-1234`).
- **Code/PRs:** Bitbucket Cloud — **both** the backend (PHP/Phalcon monolith) and the frontend (`portal-ui`: Next.js + React, TypeScript, Material UI) are on Bitbucket. A story is split into separate frontend and backend sub-tasks, each with its own branch (named after the issue key) and PR, so the pipeline runs per sub-task. PR URLs use `https://bitbucket.org/{workspace}/{repo}/pull-requests/{id}` (workspace/repo may be slugs or UUIDs). Branch-based work uses git CLI / the Bitbucket REST API; base branch is `master`. API access uses a Bitbucket **API token** (`BB_EMAIL` + `BB_API_TOKEN`) — app passwords are deprecated and disabled as of June 9, 2026.
- **Language:** all skill instructions translated to English.

## Pipeline stages

| # | Skill | Input | Output |
|---|-------|-------|--------|
| 1 | `task-context` | Jira ticket key/URL | `<KEY>-context.md` |
| 2 | `requirements-grooming` | `<KEY>-context.md` | `<KEY>-requirements.md` |
| 4 | `qa-test-cases` | `<KEY>-requirements.md` | `<KEY>-test-cases.md` |
| 5 | `pr-summary` | PR URL / branch | `<KEY>-pr-summary.md` |
| 6 | `code-review` | test-cases + pr-summary | `<KEY>-code-review.md` |
| 7 | `api-testing` | code-review + test-cases (+ `.env.qa-agents`) | `<KEY>-api-testing.md` |
| 8 | `web-testing` | code-review + test-cases | `<KEY>-web-testing.md` |
| 9 | `qa-manual-runsheet` | verdicts from 6/7/8 + test cases | `<KEY>-walk-plan.md` + `-testdata.json` (+ `-runsheet.xlsx` on request) |
| 10a | `qa-manual-walk` | `<KEY>-walk-plan.md` + the tester, live | `<KEY>-walk-results.md` (+ `-walk-state.json` for resume) |
| 10b | `qa-manual-results` | walk results, or a completed runsheet (Result/Notes) | `<KEY>-manual-results.md` + Jira/suite write-back |

> Stage 3 (`qa-checklist`) was folded into stage 4 in 0.40.0: the decomposition into checks is qa-test-cases' first working step, and the structural checks it yields are a section of the test-cases file. Stage numbers 4–10 are unchanged. Run each orchestrator (`qa-pipeline-docs`, `qa-pipeline-code`) with one model setting for the whole run — with subagent dispatch, heavy stages get fresh context anyway.

> **Stage 7 = `api-testing`.** Executes the `[API]` test cases directly against the ExpoPlatform REST API (curl / HTTP, no browser), so API cases are verified instead of routed out. Credentials are read at runtime from `~/.ep-qa/.env.qa-agents` — never hardcoded — and only hosts in its `ALLOWED_HOSTS` are called. Stage 8 (`web-testing`) then runs only `[UI]` cases; `[mobile]` / `[export/email]` remain routed out. See `skills/api-testing/references/api-testing-reference.md` for the full method (auth contexts, route discovery, write-safety, frontend/exhibitor-token cases).

> **Stage 9 = `qa-manual-runsheet`.** The last step of `qa-pipeline-code`, because it needs the automated verdicts to know what is left for a human. Provisions and verifies fixture data on a throwaway test event and builds the **walk plan**: plain-language cards grouped by login account — *as <who>, do <this>, you should see <that>* — with the machine's evidence, caveats and any request the agent will run kept in a per-card backstage block (`references/walk-plan-format.md`). A spreadsheet (`references/runsheet-format.md`) can be exported from the plan for a tester who works from a file. It reads the cases from the **QA Service suite** (the machine's source of truth) and writes any correction back there — the plan is a view and is **never** an input to an automated stage. Its `references/provisioning-rules.md` carries the pipeline-wide false-pass traps (UI-only preconditions, analytics ingestion lag, instruments that report capability as state).

> **Stage 10a = `qa-manual-walk`.** The live half of the human round: "walk me through EP-1234" and the agent presents the plan one card at a time, asks *what happened?* (never *did it pass?*), answers questions from backstage, re-probes blocked cards, runs the API / harness cards itself while the tester supplies only what a human can (a token from an email, a phone in hand), and keeps a resumable state file. It records nothing — it writes `<KEY>-walk-results.md` with the tester's words verbatim and hands it to stage 10b.

> **Stage 10b = `qa-manual-results`.** The write-back: from the walk results (or a filled run sheet / TC-Result-Notes table), this stage joins the results **by TC id, never row position**, reconciles them against the machine verdicts on the pass's **QA Service test run**, shows every `fail` about to be recorded, and on the tester's yes records the human verdicts into the same run (`source: manual`, the tester as principal; agent-run cards stay `source: machine`; a re-record supersedes and keeps history — that is the **retraction**), closes the run, applies case corrections to the suite, and posts the first human-facing summary. A retraction of a verdict that reached a Jira comment is also posted on the ticket where it was published. Until stage 10b runs, the machine verdicts are provisional and the run stays open. See `skills/qa-pipeline/references/test-runs.md`.

> **Memory across rounds.** `<KEY>-open-items.md` (`skills/qa-pipeline/references/open-items-ledger.md`) carries what a round left undecided — risk rows, in/out rulings, findings with no case and no key — into the next round's scope confirmation; the analyzer writes it, stage 10 closes rows, and an item carried two rounds with no decision is a 🔴.

> Two one-command orchestrators wrap these: **`qa-pipeline-docs`** (stages 1–4 + Jira publish) and **`qa-pipeline-code`** (stages 5 → 6 → 7 → 8 + `qa-run-analyzer` + Jira post + stage 9 walk plan, with the walk and the write-back run on demand when the tester is ready). And one front door wraps the orchestrators: **`qa-pipeline`** — give it any ticket ("qa this ticket EP-1234") and it reads the ticket's state, proposes the route (docs / code / bug-fix / retest / walk / ingest results), and invokes it on your confirmation. Direct invocation of any orchestrator or mode still works exactly as before.

## How the flow works

1. **task-context** — pulls the Jira ticket (description, acceptance criteria, comments, attachments, links) and consolidates it into one enriched Markdown file: the single source of truth for everything downstream.
2. **requirements-grooming** — reviews those requirements with a QA grooming eye (coverage, clarity, contradictions, risks, missing detail), numbers them, and produces a clean requirements file. Reads only the context file — no tracker, no internet.
4. **qa-test-cases** — decomposes each numbered requirement into atomic checks (the former stage 3, now a working step), then writes the behavioural ones as concrete test cases (steps, inputs, expected results) and the structural ones (presence, label, type, default) as a Structural checks section. The check says *what* to verify; the test case says *how*.
5. **pr-summary** — reads the Bitbucket PR (or branch) and builds a navigation map of the changes for the reviewer.
6. **code-review** — verifies each test case against the PR code and produces a compact pass/fail table with findings for failures.
7. **api-testing** — executes the `[API]` cases (code-review QA/FAIL items) against the running REST API via curl using `.env` credentials; covers admin REST, legacy admin-panel, and exhibitor-token (frontend) cases. Read-only by default; any write snapshots-and-reverts or uses a throwaway entity. Pauses if `.env` / a per-event frontend host is missing.
8. **web-testing** — executes the `[UI]` QA items and any failed code-review items in a browser it drives itself (Playwright MCP by default, the Chrome extension as fallback), confirming bugs in the UI, and writes a detailed report.
9. **qa-manual-runsheet** — provisions fixture data on a throwaway event and builds the walk plan — plain-language cards grouped by login, rigour kept backstage — so the human tests only what is left, in words a person can act on.
10. **qa-manual-walk** → **qa-manual-results** — the agent walks the tester through the plan one card at a time, running the API cards itself and collecting verdicts in the tester's own words; then the write-back joins by TC id and corrects the published record with explicit retractions where the human proved a verdict wrong.

## Before you run

The team-specific choices to confirm before a first run (the per-skill `setup-guide.md` files were retired in 0.40.0 — everything they said is here, in `skills/qa-pipeline/references/environment.md`, or in the reference the bullet names):

- **Confluence access** — Acceptance Criteria live on Confluence pages linked from the ticket, so the Atlassian connector must have **Confluence enabled**, not just Jira. (No custom-field ID needed — stage 1 reads the linked Confluence page directly.)
- **Bitbucket API token** — set `BB_EMAIL` (your Atlassian email) and `BB_API_TOKEN`. App passwords no longer work (disabled June 9, 2026). A `read:repository`-scoped token (like the existing `bitbucket-git-cli`) is enough for **branch mode** (give the skill the branch = issue key, e.g. `EP-54610`). **PR-URL mode** also needs `read:pullrequest:bitbucket` — add it via a new "with scopes" token, or just use branch mode. Workspace/repo in PR URLs may be slugs or UUIDs — both are handled.
- **web-testing login** — `web-testing/references/login-config.md` ships filled in for the ExpoPlatform e2e alpha (`e2e-testing-alpha2`), reading credentials from `~/.ep-qa/.env.qa-agents` (`ADMIN_USERNAME`/`ADMIN_PASSWORD` — the admin login, plus admin impersonation for visitor/exhibitor roles) — never inline them, never commit them. Adopting for another product: replace the URLs and field descriptions with yours.
- **Playwright MCP output folder** — start the Playwright MCP server with `--output-dir` pointing at `~/.ep-qa/evidence` so FAIL screenshots land next to the runs instead of in a per-session temp folder: `claude mcp add playwright -- npx @playwright/mcp@latest --output-dir ~/.ep-qa/evidence` (Windows: `--output-dir %USERPROFILE%\.ep-qa\evidence`). `web-testing/references/playwright-executor.md` → Evidence.
- **Trigger phrases** — adjust the `description` frontmatter in each `SKILL.md` to match how your team naturally phrases requests.
- **Credentials and the allow-list** — one file, `~/.ep-qa/.env.qa-agents` (or wherever `EP_QA_HOME` points), holds every credential plus `ALLOWED_HOSTS`, the hosts a stage may call; a run does not start without the list, and production (`*.expoplatform.com`) is refused even when listed. Nothing a run writes lands in this checkout — `skills/qa-pipeline/references/environment.md`.

## Where to run each stage

Every file a stage writes lands in the **run folder** — `~/.ep-qa/runs/<KEY>/docs/` for the docs phase, `~/.ep-qa/runs/<KEY>/r<N>/` for each code-phase pass (first run `r1`, first retest `r2`, …), the open-items ledger one level up — never in this checkout (`EP_QA_HOME` moves the home; `environment.md`); the layout and resolution order are defined once in `skills/qa-pipeline/references/data-locations.md`. Stages 1–4 (ticket → context → requirements → checklist → test cases) chain naturally in **one chat**, since each output file stays in the run folder for the next skill. Stage 5 (`pr-summary`) switches from reading the ticket to reading code; the recommended practice is to **start a fresh chat there** — no files need carrying: `qa-pipeline-code` Step 0 reads the test cases from the QA Service suite and, on resume, the earlier stage reports from the run folder. Nothing is pasted into Jira as an archive any more (0.33.0). Runs can be **split across environments** (5–7 in Claude Code, 8 in Cowork): both mount this repo, so the second resumes from the same run folder; the first posts a PARTIAL status line, the second the final one.

## Multi-surface, multi-PR features

ExpoPlatform features span more than one surface and one repo, so the pipeline accounts for that:

- **Sub-task gathering** — fed a parent Story, stage 1 pulls the child sub-tasks (backend / frontend / QA) and folds their detail in, since the concrete specs live there.
- **The AC ledger** — stage 1 keeps every acceptance criterion as its own `AC-n` bullet (verbatim, with the page section) and counts the page's items against what it captured; stage 2 maps each REQ to its ids; stage 4 carries them on every case group; `reconcile_counts.py` prints the set difference, and the analyzer fails the run on an uncovered criterion. Bugs, walk cards and the human summary name the `AC-n` that fails.
- **Channel tags** — every test case and structural check is tagged `[UI]`, `[API]`, `[mobile]`, or `[export/email]`. `[UI]` items run in the browser (web-testing); `[API]` items run against the REST API (api-testing); `[mobile]` / `[export/email]` are explicitly routed under "Not executed here" rather than dropped (exception: an `[export/email]` artifact fetchable over HTTP, like an XLS/CSV export endpoint, may be executed by api-testing).
- **Multi-PR review** — stages 5–6 accept several sub-task PRs (one backend + one or more frontend) for a single Story and produce a combined review keyed by REQ-ID, with a PR column showing which PR each result came from.
- **Per-task host** — web-testing accepts a task-specific test host (e.g. an alpha host named in the QA sub-task), overriding the default site in `login-config.md`.
- **Blast radius** — stage 5 flags changed **shared** files ("Shared / high blast-radius files" in the pr-summary) and the run-analyzer surfaces them as a 🟡 regression-risk note, since the pipeline itself is strictly ticket-scoped.
- **Bug filing** — after the code phase, `qa-pipeline-code` offers to file confirmed bugs: via the `/knowledge-base` skill when installed (dedup + routed Jira bugs), otherwise directly per `references/bug-report-template.md` (dedup search → draft → user confirms → `createJiraIssue`). Never silently. The handoff — reassign to dev on FAIL / "QA done" transition on PASS (configurable in publish-config.md) — is offered by `qa-manual-results` after the walk, once the verdicts are human-confirmed; `qa-pipeline-code` step 8 escalates early only for a runtime-confirmed, evidenced, blocking fault.

Mobile (Android/iOS) and non-HTTP outputs (exports, emails, integrations) are generated and tracked as test cases but are **not** auto-executed — they surface as routed work for the right tool or owner. (`[API]` cases are auto-executed by stage 7, `api-testing`.)

## Installing the skills

This repo is a Claude **plugin** (`.claude-plugin/plugin.json`); each folder under `skills/` is one skill. Install the whole plugin (Settings → Capabilities / your plugin marketplace) so every stage plus the `qa-pipeline-docs` and `qa-pipeline-code` orchestrators arrive together. They run in sequence within a chat, each output file staying in the run folder for the next stage.

## Maintaining / updating

**This repo is the single source of truth** — the installed copy is a read-only cache; never edit it. To change, add, or wire a stage, and to publish a new version, follow **[MAINTAINERS.md](MAINTAINERS.md)** (it also has a "where to look when something's off" map and the known gotchas). Any fresh session should read that file first.
