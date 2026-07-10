# Changelog

All notable changes to the `ep-qa-pipeline` plugin. Versions follow
semver; bump BOTH `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` — the marketplace manifest is what
signals an update to installed copies.

## 0.7.0 — 2026-07-10

- **qa-pipeline-code step 6 redesigned — results now posted as TWO
  comments** (new `references/results-comment-template.md`):
  - **Comment 1 — machine archive (agents):** the full code-review,
    api-testing, web-testing and run-report files verbatim in labeled
    fenced code blocks (`File: <name>` + block) — same convention the
    docs phase already uses, machine-parseable, zero information loss.
  - **Comment 2 — human summary (people):** ≤30 lines, posted second so
    it sits newest: overall verdict (✅ PASS / ⚠ PASS WITH GAPS /
    ❌ FAIL / ⛔ BLOCKED), stage-verdict table with counters, confirmed
    bugs one line each, "Needs a human", "Not tested in this run", and
    a run-health line. Always posted, pass or fail. Replaces the old
    freeform single comment (the wall of text humans had to read).
  - Final chat response now reuses the human summary instead of
    inventing a third format.
- **Split-run / resume support (qa-pipeline-code):** Step 0 now also
  restores finished stage reports from a results archive comment
  (resume mode), and a new "Split runs" section + PARTIAL comment
  variant let 5–7 run in Claude Code and web-testing resume in Cowork
  with only the Story key — no files carried between environments.
  README + MAINTAINERS updated to match.
- **Tracker/results drift fixed by role separation:** the docs-phase
  checkbox tracker is now explicitly the manual-testing status; the
  code phase documents that the connector cannot tick checkboxes and
  points humans at the summary comment for automated results.
- **Session-naming reminder:** both orchestrators now suggest renaming
  the session to `QA-pipeline <KEY> — docs/code` at start (manual —
  Claude/skills cannot rename sessions programmatically yet).
- **qa-run-analyzer chat summary templated:** new "Chat summary format"
  section in its output-template.md (≤10 lines: health line, top-3
  issues, counters line) — the last freeform output is now specced.

## 0.6.1 — 2026-07-09

- **Shell-safety fix for credentials with special characters** (`;`,
  `?`, `!`, `$`…): values in the env file are now single-quoted, and
  the api-testing reference §0 explains how to load them safely —
  never retype a secret inline into a shell command, never `export`
  it unquoted (a `;` in a password silently truncates the value and
  breaks login). Fixes agents failing to authenticate with the admin
  password.

## 0.6.0 — 2026-07-09

Maintainability / portability pass (no behaviour changes to the
pipeline stages themselves):

- **qa-pipeline-docs:** the Jira publishing values (project key, issue
  type id, assignee, summary format, label) moved out of SKILL.md into
  `skills/qa-pipeline-docs/references/publish-config.md` — edit that
  file to adopt the plugin for another operator/project.
- **web-testing:** SKILL.md slimmed (~90 lines); the step-interpretation
  guide and browser error handling moved into
  `references/browser-rules.md` (new "Interpreting test-case steps" and
  "Error handling" sections).
- **pr-summary / code-review:** the duplicated PR-mode/branch-mode curl
  and git command blocks consolidated into
  `skills/pr-summary/references/bitbucket-access.md` ("Command
  workflows" section); both SKILL.md files now point there. Clarified
  the misleading "curl as a substitute" rule: authenticated curl IS a
  supported path; working around missing auth is not.
- **api-testing:** the reference now labels which sections are stable
  method (§0–§7, §9, §10) vs dated worked-example data (§8, §11.1,
  §11.3, ids in §12 — recorded on alpha2/event 3551, 2026-06), with a
  re-resolve-before-use warning.
- **New:** `fixtures/EP-0000-context.md` — a golden mini-context for
  smoke-testing the docs stages after skill edits.
- **New:** this CHANGELOG.
- **.gitignore:** now covers `.env.*` (e.g. `.env.qa-agents`) and
  un-ignores `fixtures/`.
- **Publishing gotcha found & documented:** the version must be bumped
  in `marketplace.json` too, not just `plugin.json` — the app decides
  update availability from the marketplace manifest.

## 0.5.0 — 2026-07-02

- api-testing stage (stage 7) for `[API]` cases; two orchestrators
  (qa-pipeline-docs, qa-pipeline-code); qa-run-analyzer; Jira QA
  sub-task publishing; marketplace-based publishing. (Retroactive
  summary — see git history for detail.)
