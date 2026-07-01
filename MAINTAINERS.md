# Maintaining the `ep-qa-pipeline` plugin

The one doc to read before changing anything. If you're a fresh Claude
session: **this repo is the single source of truth.** Read this file,
then the README, then the specific `skills/<stage>/SKILL.md`.

## Golden rule — where the real skill lives

- **Edit here:** `D:\Coding\qa-pipeline-skill` (this repo). This is what
  gets published and installed.
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
  qa-run-analyzer/             # run-health check (both phases)
  qa-pipeline-docs/            # orchestrator: stages 1-4 + Jira publish
  qa-pipeline-code/            # orchestrator: stages 5-6-7-8 + analyzer + Jira post
```

Each stage folder is the same shape:
- `SKILL.md` — the contract. Frontmatter `name` + `description` (the
  `description` is the trigger — it decides when the skill fires).
- `references/` — the detail: `output-template.md` (report shape) plus
  any method docs (e.g. `api-testing/references/api-testing-reference.md`,
  `web-testing/references/browser-rules.md` + `login-config.md`).
- `setup-guide.md` — team-specific values to confirm before running.

Data flows between stages as files in the working directory, named
`<ISSUEKEY>-<stage>.md` (e.g. `EP-44730-code-review.md`). Each stage
reads the previous stage's file. These outputs are git-ignored.

## Pipeline order & channel routing

`task-context → requirements-grooming → qa-checklist → qa-test-cases`
(docs) then `pr-summary → code-review → api-testing → web-testing`
(code), with `qa-run-analyzer` at the end of each phase.

Every checklist item / test case carries a channel tag that decides who
runs it:
- `[UI]` → **web-testing** (browser, Chrome extension)
- `[API]` → **api-testing** (REST/curl, creds from `.env`)
- `[mobile]` / `[export/email]` → routed to "Not executed here" (manual
  / device / export tooling)

## How to update — recipe

1. **Change the relevant `SKILL.md` / `references/`.** Keep `SKILL.md`
   lean; put heavy detail in `references/`.
2. **If you added or renamed a stage, wire it into the orchestrator and
   analyzer** (this is the step people forget):
   - `skills/qa-pipeline-code/SKILL.md` — the title `(stages …)`, the
     numbered "How it runs" list, the Jira-comment contents, and the
     "Final response" line.
   - `skills/qa-run-analyzer/SKILL.md` + its `references/output-template.md`
     — the input file list, the counts-reconcile check, and the
     findings-summary line.
   - `README.md` — the stage table + the "How the flow works" list.
3. **Bump the version** in `.claude-plugin/plugin.json` (semver).
4. **Commit** (run git locally — see gotcha below):
   `git add -A && git commit -m "…"` then push.
5. **Publish / update the installed plugin** (see below), and remove any
   duplicate standalone install of the changed skill.

## Where to look when something's off

| Symptom | Look here |
|---|---|
| A skill doesn't trigger / triggers wrongly | its `SKILL.md` frontmatter `description` |
| Report format wrong | that stage's `references/output-template.md` |
| API auth / route discovery / write-safety | `skills/api-testing/references/api-testing-reference.md` |
| Browser interaction rules | `skills/web-testing/references/browser-rules.md` |
| Test login / host | `skills/web-testing/references/login-config.md` |
| Jira custom-field / AC source | `skills/task-context/references/field-maps.md` |
| Bitbucket auth (token/scopes, branch vs PR mode) | README + `pr-summary`/`code-review` `SKILL.md` |
| "Feature/toggle not visible on env X" | **deployment**, not the skill — confirm the branch is deployed to that host (feature branches ≠ master/alpha2) |

## Gotchas

- **Installed cache is read-only** — edit here, re-publish. (Rule #1.)
- **Git won't run on the Cowork network mount** — its `.git/config`
  gets corrupted on write. Commit from a normal local terminal.
- **Windows PowerShell** doesn't accept `&&`; run git lines separately
  or use `;`.
- **Don't commit secrets or run outputs** — `.gitignore` covers `.env`,
  the `<KEY>-*.md` pipeline outputs, `*.diff`, and `navigation_paths.json`.
- **api-testing pauses** if `.env` or a per-event frontend host is
  missing (the frontend host is per-event and not discoverable).

## Publishing / updating the installed plugin

This repo is a Claude plugin. To ship a new version:
1. Push this repo to its remote (the marketplace/git repo it's served
   from).
2. Update the plugin in the app so the cache refreshes to the new
   version (Settings › Capabilities / your plugin marketplace).
3. Verify the installed version matches `plugin.json` and remove any
   stray standalone skill copies.
