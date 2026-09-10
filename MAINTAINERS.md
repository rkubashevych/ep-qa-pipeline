# Maintaining the `ep-qa-pipeline` plugin

The one doc to read before changing anything. If you're a fresh Claude
session: **this repo is the single source of truth.** Read this file,
then the README, then the specific `skills/<stage>/SKILL.md`.

## Golden rule — where the real skill lives

- **Edit here:** `C:\media-files\Coding\qa-pipeline-skill` (this repo).
  This is what gets published and installed.
- **Never edit the installed copy.** When a plugin is installed, Claude
  loads it from a read-only cache (e.g. `…/.remote-plugins/plugin_XXX/`
  or `…/.claude/skills/`). Editing that cache does nothing — changes
  don't persist and create drift. If you ever find yourself editing a
  path with `plugin_` or `.remote-plugins` or `rpm` in it, stop: make
  the change here and re-publish instead.
- **One copy only.** Don't also install individual stages as standalone
  personal skills — that's how you end up with two `api-testing`s that
  disagree. Everything ships together as this one plugin.

## Repo layout

```
.claude-plugin/plugin.json     # plugin manifest: name, version, description
README.md                      # what the pipeline is + stage table
MAINTAINERS.md                 # this file
skills/
  task-context/                # stage 1  (docs phase)
  requirements-grooming/       # stage 2
  qa-checklist/                # stage 3
  qa-test-cases/               # stage 4
  pr-summary/                  # stage 5  (code phase)
  code-review/                 # stage 6
  api-testing/                 # stage 7  — [API] cases, REST/curl
  web-testing/                 # stage 8  — [UI] cases, browser
  qa-manual-runsheet/          # stage 9  — fixture provisioning + the walk plan (sheet = optional export)
  qa-manual-walk/              # stage 10a — the live, card-by-card manual session in chat
  qa-manual-results/           # stage 10b — write back walk results / a completed sheet, retract wrong verdicts
  qa-run-analyzer/             # run-health check (both phases)
  qa-pipeline/                 # dispatcher: reads ticket state, routes to a mode
  qa-pipeline-docs/            # orchestrator: stages 1-4 + Jira publish
  qa-pipeline-code/            # orchestrator: stages 5-9 + analyzer + Jira post
runs/                          # git-ignored RUN WORKSPACE (0.32.0): runs/<KEY>/docs/, runs/<KEY>/r<N>/
                               # — every artefact a stage writes; nothing goes in the repo root any more
```

Each stage folder is the same shape:
- `SKILL.md` — the contract. Frontmatter `name` + `description` (the
  `description` is the trigger — it decides when the skill fires).
- `references/` — the detail: `output-template.md` (report shape) plus
  any method docs (e.g. `api-testing/references/api-testing-reference.md`,
  `web-testing/references/browser-rules.md` + `login-config.md`).
- `setup-guide.md` — team-specific values to confirm before running.

Data flows between stages as files in the run folder —
`runs/<ISSUEKEY>/docs/` for stages 1–4, `runs/<ISSUEKEY>/r<N>/` per
code-phase pass — named `<ISSUEKEY>-<stage>.md` (e.g.
`EP-44730-code-review.md`). Each stage reads the previous stage's file.
The layout, the round rule and the resolution order live in ONE place:
`skills/qa-pipeline/references/data-locations.md`. `runs/` is
git-ignored as a whole. Files from before 0.32.0 sit in the repo root
and stay readable; nothing new is written there.

## Pipeline order & channel routing

`task-context → requirements-grooming → qa-checklist → qa-test-cases`
(docs) then `pr-summary → code-review → api-testing → web-testing`
(code), with `qa-run-analyzer` at the end of each phase.

Every checklist item / test case carries a channel tag that decides who
runs it:
- `[UI]` → **web-testing** (browser — Playwright MCP by default, Chrome extension fallback)
- `[API]` → **api-testing** (REST/curl, creds from `.env`)
- `[mobile]` / `[export/email]` → routed to "Not executed here" (manual
  / device / export tooling)

## Where to run each stage — Cowork vs Claude Code

The stages need different things, so they run in different places:

| Stage(s) | Needs | Run in |
|---|---|---|
| 1–4 docs (`task-context` … `qa-test-cases`) + `qa-pipeline-docs` | Jira/Confluence only (+ QA Service connector for the suite publish) | **Cowork** (or Claude Code) |
| code-phase step 0 (case rebuild) | the **QA Service connector** — the suite is the record of the cases (no Jira archive is posted since 0.33.0); without it only this machine's `runs/<KEY>/docs/` can supply them, and no run can be written | wherever `qa-pipeline-code` starts |
| 5–6 `pr-summary`, `code-review` | the code: a **backend/portal-ui repo clone** OR a Bitbucket **API token** (`BB_EMAIL`+`BB_API_TOKEN`) | **Claude Code** |
| 7 `api-testing` | the e2e **`.env`** (API creds) + a per-event frontend host | **Claude Code** |
| 8 `web-testing` | the **Playwright MCP** tools + `.env.qa-agents` for the scripted login (default); else a connected Chrome + logged-in test env (extension fallback) | **either** with Playwright; **Cowork** for the extension |
| 9–10 `qa-manual-runsheet`, `qa-manual-walk`, `qa-manual-results` | QA Service connector (suite read/write-back) + `.env` for provisioning and for the walk's AGENT-RUNS cards | either, connector present (the walk needs `.env` only if the plan has AGENT-RUNS cards) |

**Why:** Cowork has no repo clone, no `BB_API_TOKEN`, and no `.env`, so
5–7 can't authenticate there — `api-testing` will pause ("no .env"),
and `code-review`/`pr-summary` can't reach a private Bitbucket PR. Those
three are **Claude Code** stages. Run `qa-pipeline-code` from Claude Code
in the repo that has the `.env`; with the Playwright MCP present, stage 8
runs there too and the whole code phase is one environment. Keep Cowork
for the docs half and for the Chrome-extension fallback.

**Split runs are supported:** run 5–7 in Claude Code, post the step-6
status line marked PARTIAL, then resume in Cowork with the same Story
key — `qa-pipeline-code` Step 0 restores the finished stage reports
from the run folder `runs/<KEY>/r<N>/` (see "Split runs" in its
SKILL.md). Both environments mount this repo, so no files need to be
carried between them; the QA Service run carries the verdicts anyway.

## Where things live

- **Credentials (`.env`)** — in the **`e2e-testing` repo** (git-ignored).
  Holds `ADMIN_BASE_URL`, `ADMIN_USERNAME`/`ADMIN_PASSWORD`,
  `ORGANIZER_API_KEY`, `EVENT_ID`, `BASE_URL`. `api-testing` reads it at
  runtime — never paste these into chat. Point it at the target env
  before running (e.g. `ADMIN_BASE_URL=https://api-alpha2.expoplatform.net`).
- **Bitbucket auth** — `BB_EMAIL` + `BB_API_TOKEN` env vars (repository
  read; add `read:pullrequest` for PR-URL mode). Branch mode uses the
  branch = issue key.
- **Code repos** — Bitbucket `expoplatform` workspace: backend monolith
  = `expoplatform-main-ira`, frontend = `portal-ui`, admin = `admin-ui`.
- **Per-event frontend host** — not discoverable; supply it per event
  (see `skills/api-testing/references/api-testing-reference.md` §11.1).
- **Pipeline output files** (`<KEY>-context.md` … `<KEY>-run-report.md`)
  — written to the **run folder** `runs/<KEY>/…` inside the mounted
  repo (`data-locations.md`); the next stage reads them from there,
  in this session or the next. They are git-ignored, not committed.
- **Hand-off between docs and code** — docs publishes requirements,
  test cases and structural checks to the **QA Service suite**;
  `qa-pipeline-code` reads them back from there (or from
  `runs/<KEY>/docs/` on the same machine), so you don't carry files
  between sessions — you only need the same ticket key. Nothing is
  pasted into Jira any more (0.33.0); pre-0.33 tickets still carry the
  old archive comments, which `extract_archive.py` can read.

## How to update — recipe

1. **Consume the last run's findings first — this rule is load-bearing.**
   If the most recent `<KEY>-run-report.md` (or a triage /
   flow-gap-analysis file from that run) contains a 🔴 item tagged
   [Pipeline] or [Pipeline/skill], you must do one of two things before
   or with your change: implement it (with a CHANGELOG entry), or record
   the rejection and its reason in the CHANGELOG. **A run-report
   recommendation with neither is an open defect of the plugin.** Run
   outputs are git-ignored working files — they do not survive the
   workspace. The CHANGELOG is where their lessons become permanent;
   a lesson that never reaches a tracked file was never learned.
   The machine-readable input to this rule is the per-ticket ledger
   `<KEY>-open-items.md` (`skills/qa-pipeline/references/open-items-ledger.md`):
   grep the latest ledgers for `[Pipeline]` rows with no Decision — each
   one carried two rounds is a 🔴 the analyzer has already raised.
2. **Change the relevant `SKILL.md` / `references/`.** Keep `SKILL.md`
   lean; put heavy detail in `references/`.
3. **If you added or renamed a stage, wire it into the orchestrator and
   analyzer** (this is the step people forget):
   - `skills/qa-pipeline-code/SKILL.md` — the title `(stages …)`, the
     numbered "How it runs" list, the Jira-comment contents, and the
     "Final response" line.
   - `skills/qa-run-analyzer/SKILL.md` + its `references/output-template.md`
     — the input file list, the counts-reconcile check, and the
     findings-summary line.
   - `README.md` — the stage table + the "How the flow works" list.
4. **Smoke-test the docs stages** if you touched them: run
   `fixtures/EP-0000-context.md` through grooming → checklist →
   test-cases (skip the Jira publish) and check the expectations listed
   at the bottom of the fixture still hold. If you touched
   `reconcile_counts.py`, run `python3 skills/qa-run-analyzer/scripts/reconcile_counts.py --selftest`.
   If you touched ANY skill's frontmatter `description`, walk
   `evals/triggering.md` — every ✅ query must still route to that
   skill and every ❌ must not; update the list when triggers
   legitimately change.
5. **Bump the version in BOTH manifests** — `.claude-plugin/plugin.json`
   AND `.claude-plugin/marketplace.json` (the plugin entry's `version`).
   The app decides update availability from the **marketplace** manifest;
   if only plugin.json is bumped, the Update button stays inactive and
   reinstalls keep serving the old version. Add a `CHANGELOG.md` entry.
6. **Secret-scan, then commit — explicit paths only** (run git locally —
   see gotcha below). **Never `git add -A` or `git add .` in this repo**:
   the working tree doubles as a run workspace holding live-credential
   artifacts (`.env.qa-agents`, testdata packs, runsheets), and the
   ignore list is a backstop, not a guarantee. The steps are:
   1. `git status --short` — every untracked file must be either in your
      change set or a run artifact you can explain. An untracked run
      artifact that is not ignored means the `.gitignore` broad rules
      have a hole — fix the pattern before committing.
   2. Run a secret scan over the working tree (the `secret-leak-scan`
      skill, or `gitleaks protect --staged` after staging).
   3. `git add <the specific files you changed>` — e.g.
      `git add skills/ README.md MAINTAINERS.md CHANGELOG.md .claude-plugin/ .gitignore`
   4. `git commit -m "…"` then push.
7. **Publish / update the installed plugin** (see below), and remove any
   duplicate standalone install of the changed skill.

## Where to look when something's off

| Symptom | Look here |
|---|---|
| A skill doesn't trigger / triggers wrongly | its `SKILL.md` frontmatter `description` |
| Report format wrong | that stage's `references/output-template.md` |
| API auth / route discovery / write-safety | `skills/api-testing/references/api-testing-reference.md` |
| Walk plan format (sessions, cards, backstage keys, voice rules) | `skills/qa-manual-runsheet/references/walk-plan-format.md` |
| The walk itself (turn shape, words → verdict mapping, positive-control question, card kinds, resume) | `skills/qa-manual-walk/references/walk-session-rules.md`; results file: `.../walk-results-format.md` |
| Manual run-sheet format (the optional export: columns, row states) | `skills/qa-manual-runsheet/references/runsheet-format.md` |
| Fixture provisioning rules + false-pass traps (UI-only, ingestion lag, unreliable instruments) | `skills/qa-manual-runsheet/references/provisioning-rules.md` |
| Browser interaction rules | `skills/web-testing/references/browser-rules.md` |
| Test login / host | `skills/web-testing/references/login-config.md` |
| Jira custom-field / AC source | `skills/task-context/references/field-maps.md` |
| Bitbucket auth (token/scopes, branch vs PR mode) + the curl/git command workflows | `skills/pr-summary/references/bitbucket-access.md` (shared source of truth — pr-summary and code-review both point here) |
| Jira publish values (project, issue type id, assignee, label) | `skills/qa-pipeline-docs/references/publish-config.md` |
| Results-comment format (wave-1 status line, wave-2 human summary, story notes) | `skills/qa-pipeline-code/references/results-comment-template.md` |
| Structural checks in the suite (`-STRUCT-` cases), bug-fix mini suite | `skills/qa-pipeline-docs/references/qa-service-publish.md` |
| Per-case verdicts in QA Service (test run per pass, status → verdict mapping, what stays `not_run`, retractions, retraction target rule) | `skills/qa-pipeline/references/test-runs.md` |
| What earlier rounds left open (carried risk rows, in/out rulings, `[core]` nominations) | `skills/qa-pipeline/references/open-items-ledger.md` → `<KEY>-open-items.md` |
| Regression after a skill edit | run `fixtures/EP-0000-context.md` through the docs stages (see the recipe) |
| "Feature/toggle not visible on env X" | **deployment**, not the skill — confirm the branch is deployed to that host (feature branches ≠ master/alpha2) |

## Gotchas

- **Installed cache is read-only** — edit here, re-publish. (Rule #1.)
- **NEVER write skill files through the Cowork shell mount** — writes
  through `/sessions/.../mnt/...` (bash/python/sed) can be silently
  truncated mid-file or padded with NUL bytes. This is what originally
  cut off `qa-test-cases/SKILL.md`, `qa-pipeline-docs/SKILL.md`, and
  the qa-test-cases output-template mid-sentence, and it happened again
  during the v0.5.0 cleanup. Edit files with Claude's host-side file
  tools (Read/Write/Edit) or a local editor only; after any bulk change,
  verify every touched file still ends with its final section.
- **Git won't run on the Cowork network mount** — its `.git/config`
  gets corrupted on write. Commit from a normal local terminal.
- **Windows PowerShell** doesn't accept `&&`; run git lines separately
  or use `;`.
- **Don't commit secrets or run outputs** — `.gitignore` ignores run
  artifacts by BROAD rule (`EP-*`, `build_*.py`, `*-testdata*`,
  `*-walk-*`, `*runsheet*.xlsx`, the `<KEY>-<stage>.md` patterns,
  `.env*`). If you
  create a run artifact whose name escapes those patterns, widen the
  pattern — do not add one filename. And commit explicit paths only;
  `git add -A` is banned in this repo (recipe step 6). On one run, 84
  live account passwords were one `git add -A` away from being committed.
- **`.env.qa-agents` lives in this repo root by design** (the skills
  read it from the mounted plugin folder). That co-locates live
  credentials with the distributable: if you ever publish this folder by
  copy (loose `.plugin` bundle, zip, local-path marketplace that copies
  rather than clones), verify the env file is not inside the artifact —
  `git archive` respects the index (safe), raw folder copies do not.
- **api-testing pauses** if `.env` or a per-event frontend host is
  missing (the frontend host is per-event and not discoverable).

## Publishing / updating — the no-drag way (marketplace)

This repo is BOTH a plugin (`.claude-plugin/plugin.json`) and a
one-plugin **marketplace** (`.claude-plugin/marketplace.json`). Installing
via the marketplace — not a loose `.plugin` file — is what makes updates
automatic (no packaging, no drag-and-drop).

**One-time setup (do once):**
1. Make sure the repo is a git repo with a commit (it is).
2. Add this folder as a marketplace:
   - Claude Code CLI: `/plugin marketplace add C:\media-files\Coding\qa-pipeline-skill`
   - Cowork: Settings › Capabilities → add/manage marketplaces → point at
     this folder (local path) or its git URL.
3. Install `ep-qa-pipeline` from the `expoplatform-qa` marketplace.
4. Enable auto-update so it refreshes on startup — in `settings.json`
   set the marketplace source `"autoUpdate": true` (local marketplaces
   default to false; official Anthropic ones default to true).
5. Remove any standalone copy of a skill that now ships in the plugin.

**Every update after that:**
1. Edit the skill/reference files here.
2. Bump `version` in `.claude-plugin/plugin.json` (semver) — the version
   bump is what signals an update.
3. Secret-scan, then `git add <changed files>` and commit — never
   `git add -A` (see the update recipe, step 6). Push too if the
   marketplace is a remote.
4. That's it — with `autoUpdate` on, the app pulls it on next startup;
   or force it now: `/plugin marketplace update expoplatform-qa` (CLI) /
   the "update" action in Cowork's marketplace UI.

No searching folders, no `git archive`, no dragging `.plugin` files.

> A loose `.plugin` bundle (`git archive … -o x.plugin`) is still handy
> for a one-off hand-off to someone who hasn't added the marketplace —
> but for your own machine, use the marketplace + autoUpdate.
