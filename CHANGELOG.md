# Changelog

All notable changes to the `ep-qa-pipeline` plugin. Versions follow
semver; bump BOTH `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` — the marketplace manifest is what
signals an update to installed copies.

## 0.11.2 — 2026-07-29

De-duplication of what the docs phase writes to Jira, after measuring a
real ticket (EP-55646: **188,063 characters across 10 posts**).

- **The fenced machine archive is no longer posted when a QA Service
  suite was published.** The 89 test cases were being written to Jira
  twice — the human checkbox tracker and the machine archive were
  measured 99.3% identical (76 of 89 case blocks byte-identical after
  normalising rendering). The code phase now rebuilds its working files
  from the suite; the archive is posted only when there is no suite
  (connector absent or user declined), which is exactly when the code
  phase still needs it. **−45,767 chars/ticket.**
- **The checkbox tracker is one line per case** — id, name, channel tag
  and the QA Service case id — instead of carrying Pre/Steps/Exp inline.
  The steps live in the suite and the local file. **−14,931
  chars/ticket** (−63% of the tracker).
- **The standalone TC-REQ → stableId map is gone.** It cost ~2,000 chars
  and went stale the first time stableIds were corrected; the case id
  now travels on the tracker line it belongs to.
- **Structural checks are still posted.** The checklist's `[UI]`
  presence / label / field-type checks deliberately have no test case,
  so they exist neither in the suite nor in the tracker — and stage 8
  (web-testing) executes them. They are posted as a short
  `(structural checks only)` fenced block; the rest of the checklist,
  which the cases already cover, is not.
- `qa-pipeline-code` step 0 documents the source order explicitly:
  suite first (+ the structural-checks block), fenced archive as
  fallback, otherwise ask.

Net effect: ~32% less text per ticket, one authoritative copy of each
test case, and the code phase reads structured data instead of
re-parsing markdown out of comments.

## 0.11.1 — 2026-07-29

- **QA Service publishing is back to on-by-default.** The 0.10.5
  ask/always/never switch and its step-0 question are removed — the
  write-API gaps that motivated opting out are fixed, so publishing is
  part of a normal run again. The user can still decline at the step-6
  confirmation or when invoking the pipeline.
- **Audit of the mapping against the real tool schemas — three bugs in
  our own instructions fixed:**
  - `create_test_case` takes the case's FULL content in one call
    (levels, levelText, status, priority, type, techniques,
    traceability, folderName, detail). The old "create bare, then
    `edit_test_case`" instruction doubled the calls and left cases
    briefly empty. Same for `create_requirement`, which accepts
    `detail` and `priority` directly.
  - **`status: "deprecated"` was invalid** and would have been rejected
    — the case vocabulary is `planned`/`partial`/`implemented`/
    `deferred`/`na`. Superseded cases are now retired as `na` with a
    note; superseded requirements use `edit_requirement`
    `status: "retired"`.
  - `create_suite` has always accepted `summary`/`status`/`owner`/
    `lastReviewed`; the pipeline simply never passed them. The header is
    now set at creation, not patched afterwards with `edit_suite`
    (which is kept for refreshing an existing suite).
- **Tagging is one bulk `apply_auto_tags` call** (`perCase` array, up to
  400) instead of a `tag_case` per case; unknown tag names are created
  as PENDING automatically, so `propose_tag` is not needed in the flow.
- Obsolete "requirements are immutable, publish a `-FR-NNb` revision"
  guidance removed — changed requirements are edited in place.

## 0.11.0 — 2026-07-29

The QA Service write-API gaps from EP-55653 were fixed by the QA
Service team overnight. Verified against the live PRIVFAV suite, and
the mapping updated to use everything that is now writable.

- **Requirement `detail` and `priority` are now published.** New
  `edit_requirement` (kind, title, summary, priority, status, detail,
  stableId — merge semantics) means requirements carry their structured
  model: `type` / `statement` / `rationale` / `scope` / `source`,
  per-kind fields (`actor`/`trigger`/`outcome`, `metric`/`target`,
  `impact`/`likelihood`/`mitigation`), and the cross-link lists
  `related` / `enforces` / `threatens` / `implements` / `constrainedBy`
  that become trace-graph edges. Risk ratings now map to `priority`
  (High→P0, Medium→P1, Low→P2) instead of living only in prose.
- **Case `levels` codes are now sent** alongside `levelText`
  (`[API]`→`AE`, `[UI]`→`E2E`, `[mobile]`/`[export/email]`→`M`), so the
  Coverage-by-level table is populated and cases are eligible for the
  implement workflow. Verified: backfilling 88 existing cases moved
  `byLevel` from all-zero to 60 AE / 24 E2E / 5 M = 89.
- **Suite header is set at publish** via `edit_suite` (summary, status,
  owner, lastReviewed) — no more bare-title suites.
- **Nothing published is frozen any more.** New "Correcting an existing
  suite" section: fix `kind`/`stableId` in place (renaming a stableId
  rewrites every reference to it), fill thin requirements, retire
  obsolete ones (`status: retired`). The "supersede with `-FR-NNb`"
  workaround is removed as obsolete.
- **`traceLinks` now materialize** from case `traceability` and
  requirement cross-links — 0 → 89 `satisfies` links on the verified
  suite. Publish verification and `qa-run-analyzer` check for an empty
  graph, a zeroed level table and a bare header, and fix what is
  fixable instead of reporting it.
- Unchanged: never call `summarize_requirement` (still destructive).
  New caveat: setting `levels` auto-creates a placeholder
  `implementations` entry (`ref: ""`), so a non-empty `implementations`
  array does not mean a real test is linked.

## 0.10.5 — 2026-07-28

- **QA Service publishing is now opt-in per run.** New switch in
  `qa-pipeline-docs/references/qa-service-publish.md`: `ask` (default),
  `always`, or `never`. Under `ask`, the docs orchestrator puts one
  question at the START of the run (step 0, bundled with the
  session-rename suggestion) — "publish to a QA Service suite as well
  as the Jira QA sub-task? yes / no — Jira-only" — so declining costs
  nothing instead of being decided after all the work. A preference
  stated when invoking the pipeline ("no QA Service") is honoured
  without asking; the answer is restated in the step-6 preview and can
  still be flipped there.
- Declining is a normal outcome, not a degraded run: `qa-run-analyzer`
  records "publishing declined by the user" instead of flagging a gap,
  and `qa-pipeline-code` skips reconciliation + result write-back
  silently when no suite was published or the switch is `never`.
- A "no" disables WRITES only — reading an existing feature suite for
  grooming comparison (stage 1) has no side effects and stays on unless
  the user asks to skip QA Service entirely.

  Rationale: the write-API gaps in EP-55653 (empty `levels`, no
  `edit_requirement`) mean some teams will want Jira-only runs until
  those land. Set the switch to `never` for that.

## 0.10.4 — 2026-07-28

- **Hard rule: never call `summarize_requirement`** (or advise clicking
  the UI's Regenerate / "Generate missing summaries" buttons) on a suite
  the pipeline published. Tested on one requirement: it rewrote `title`
  from the requirement's testable text to a 3-word label, produced a
  summary contradicting the suite's own invariant, and dropped the
  `[risk: …]` marker — irreversibly, since there is no
  `edit_requirement`. Replaces the earlier (harmful) advice to use those
  buttons for enrichment. `apply_auto_tags` stays recommended (additive);
  `start_collect_requirements` / `start_import_docs` are marked
  UNVERIFIED on populated suites (may duplicate by stableId, no delete).

## 0.10.3 — 2026-07-28

Two write-semantics assumptions settled by direct experiment on a live
suite; instructions corrected accordingly.

- **`edit_test_case` MERGES** (verified): an edit sending only
  `status` + `levelText` preserved `detail` (all keys), `techniques`,
  `priority`, `type`, `traceability` and attached tags byte-identical.
  The result write-back no longer re-sends the whole `detail` object —
  only `notes`, sent complete.
- **`levels` is not derivable from `levelText`** (verified): setting the
  exact canonical `API-E2E` left `levels: []` and `stats.byLevel` at
  zero. Publish verification and `qa-run-analyzer` no longer treat an
  empty `byLevel` as a defect — it is a connector gap (no `levels`
  parameter) and chasing it would have sent the pipeline into a loop
  trying to fix something unfixable. Zeroed *status* buckets and
  collapsed requirement kinds remain real 🔴 findings.

## 0.10.2 — 2026-07-28

Field mapping rewritten after diffing the first pipeline-published
suite against an importer-built reference suite (ACINT). The first run
produced a structurally poor suite: every level/status dashboard read
zero, requirement kinds collapsed, 89 cases in one folder.

- **Controlled vocabularies are now mandatory.** Case `levelText` must
  be an exact canonical label (`API-E2E`, `E2E (UI)`, `Manual`, `Unit`,
  `Integration`, `Contract`, …) — invented labels (`API`,
  `E2E (mobile)`) leave the case with no level, so `stats.byLevel` read
  0/89. Case `status` is `planned` (vocab
  `planned/implemented/partial/deferred/na`); `draft` is not a bucket
  and zeroed the readiness dashboard.
- **Requirement kinds must be classified**, not defaulted to `fr`:
  rule / invariant / risk / nfr / fr / oq / discrepancy, with
  kind-matching stableId segments (`-RULE-`, `-INV-`, `-R-`, `-NFR-`,
  `-FR-`, `-OQ-`, `-DISC-`). Previously 33/41 were `fr` and an
  invariant was filed as `-FR-37`. 0 rules + 0 invariants + 0 risks is
  now treated as a mis-classification signal.
- **Requirement `summary` carries the requirement text**, verbatim and
  self-contained, with the risk tag appended at the end — previously
  11 requirements had a summary of literally `[risk: Medium]`.
- **Case IDs and folders carry meaning:** `<PREFIX>-<SEG>-NN` aspect
  segments instead of flat `<PREFIX>-01…89`, and 4–8 behaviour-area
  folders instead of a single "General".
- **`detail.testData` and `detail.tagPlan` always populated**;
  `traceability` lists every requirement a case verifies, not just its
  parent.
- **Publish verification now checks the dashboards**, not just counts:
  a suite whose own level/status charts read zero must be fixed with an
  `edit_test_case` pass before the run finishes. `qa-run-analyzer`
  gained a matching 🔴 "zeroed dashboards" verdict.
- **Known MCP gaps documented instead of faked:** requirement `detail`
  and `priority` (no `edit_requirement`), case `levels` and
  `implementations`, suite `summary`/`status`/`owner`, and the
  `traceLinks` graph cannot be set through the connector — the pipeline
  reports them and points at the UI's server-side enrichment buttons.

## 0.10.1 — 2026-07-28

- **Suite links in Jira: bare URL only.** The Atlassian connector's
  markdown→ADF conversion drops `[text](url)` hyperlinks, so the suite
  link arrived in Jira as unclickable text. Every reference (sub-task
  description, human summary, story note) now writes the full bare URL,
  which Jira auto-links.

- **QA Service suite selection: append by default.** One suite per
  FEATURE, not per ticket. A feature-extension story now appends its
  requirements and cases to the feature's existing suite (previously
  only bugs and re-runs did; stories always created a sibling suite,
  splitting one feature's test design across suites). A new suite is
  created only when the feature has no suite yet — named after the
  feature, never the ticket key. Ambiguous matches are surfaced in the
  publish preview with both candidates and a recommendation instead of
  being guessed; empty failed-import suites (`0r · 0t`) count as the
  feature's suite and get appended to. The preview now states
  append-vs-create, the reason, duplicates skipped, and the runner-up
  candidate, so the target can be redirected before anything is
  written.

## 0.10.0 — 2026-07-27

- **QA Service publishing (qa-pipeline-docs step 6).** The docs phase
  now dual-writes: alongside the Jira QA sub-task it publishes the
  groomed requirements and test cases into a QA Service suite via the
  QA Service MCP connector — the team's permanent, traceable system of
  record. One suite per ticket (`role/feature-area/slug`), requirements
  as `fr`/`oq`/`discrepancy` with `<PREFIX>-FR-NN` stableIds, cases
  created + edited with traceability, priority (risk→P0/P1/P2),
  levelText (channel tag), techniques, and the Pre/Steps/Exp/Post
  content mapped to detail fields. Re-runs append to the existing suite
  (no duplicates; superseded cases → `status: deprecated` — QA Service
  has no delete). Bug tickets never get their own suite: their
  regression cases are appended to the existing feature suite (bug key
  in the case notes), continuing that suite's prefix and numbering.
  Same single publish pause covers Jira + QA Service;
  if the connector is not enabled the step is skipped with a note,
  never blocking the Jira publish. Config + full field mapping:
  `skills/qa-pipeline-docs/references/qa-service-publish.md`.
- **QA Service read-side (task-context + requirements-grooming).**
  Stage 1 pulls the touched feature's existing suite (requirements,
  risks, open questions, known-bug cases) into a new "Existing QA
  Service suite" context section; stage 2 grooms the ticket against it
  — a ticket requirement contradicting an established one is a
  Contradiction finding citing both sides. Comparison material only;
  suite items are never imported as requirements.
- **QA Service as case source (qa-pipeline-code step 0).** With the
  connector present, extracted test cases are reconciled against the
  suite: UI-edited cases win, `deprecated` cases are dropped from
  execution, team-added cases are picked up and executed. Jira archive
  remains the fallback when the connector is absent.
- **Result write-back (qa-pipeline-code step 6).** Executed cases get
  their PASS/FAIL outcome appended to the suite case notes (with date,
  story key, and filed-bug keys), inside the same posting confirmation.
  Lifecycle `status` is never overwritten by run results.
- **Coverage tagging (publish step).** Created cases get existing
  feature @tags via `tag_case` (new ones via `propose_tag`, pending
  approval), so pipeline cases show up in `get_coverage`.
- **Independent publish verification (qa-run-analyzer).** New "QA
  Service sync" check: when the connector is present, the analyzer
  compares the suite against the requirements/test-cases files and
  reports in-sync / not-published-yet / mismatch (with missing IDs) /
  write-back-missing — a fresh-instructions re-check so a silently
  skipped or partial publish surfaces in the run report.
- **QA Service line in results (templates).** The human summary
  comment and the "QA passed" story note now carry a "Test docs: QA
  Service suite <path>" line (clickable once the Web UI base URL is
  configured in qa-service-publish.md), so anyone reading Jira can
  jump to the created documentation.

## 0.9.0 — 2026-07-23

- **Main-issue PR fallback (qa-pipeline-code step 0).** Tickets with no
  Backend/Frontend sub-tasks (Bugs, small Stories/Tasks) no longer
  stall: branches/PRs are discovered on the main issue — remote/dev
  links → PR URLs in description/comments → the issue key as branch
  name → ask the user. In this case step 6 posts results to the main
  issue instead of a QA sub-task.
- **"QA passed" story note (step 8).** On ✅ PASS the pipeline now
  offers to post a ≤10-line plain-language summary (what was tested,
  environment, coverage, result, link to the full reports) to the
  PARENT story, so managers and devs see the outcome without opening
  the QA sub-task. Template: results-comment-template.md → "Story
  note — QA passed".
- **Shift-left guidance (qa-pipeline-docs).** New "When to run" section:
  run the docs phase at refinement / before dev completes, so grooming
  findings prevent bugs instead of catching them.
- **Grooming findings → ticket (qa-pipeline-docs stage 2).** After the
  grooming pause, offer to post the still-open questions /
  contradictions / gaps as one confirm-first comment on the ticket, so
  PM/dev resolve them before the code is written.
- **Risk-based prioritization (ISTQB TA Ch. 2).** Grooming now rates
  each requirement High/Medium/Low (impact × likelihood); the marker
  flows requirements → checklist → test-case group headings, and
  api-testing/web-testing execute High-risk cases first — a truncated
  or split run covers what matters most. Reports keep file order.
  Markers are optional: files without them behave as before.
- **CRUD completeness lens (grooming).** "Where can this break?" now
  checks entity lifecycle coverage — create/edit/delete effects on
  read, list, and export views.
- **Playwright backend for web-testing (preferred).** The Playwright
  MCP, when available, replaces the Chrome extension as the executor:
  headless own browser (no active-window breakage), scripted login
  from `.env.qa-agents` (no login pause), screenshot + console errors
  captured on every FAIL. Extension stays as fallback; report format
  unchanged. Promoted references/playwright-executor-draft.md →
  playwright-executor.md. Stage 8 can now run in Claude Code too —
  single-environment code-phase runs possible.
- **Auto-default mode (qa-pipeline-docs).** The docs pipeline no longer
  stops to ask: grooming findings are shown but treated as "skip",
  stage clarifying questions become "needs clarification" notes in the
  files, and the shift-left open-items comment is bundled into the one
  remaining pause — the Jira publish confirmation. Say "interactive
  mode" to get the grooming pause back. The open-items list is also
  duplicated into the QA sub-task description ("Open questions from
  grooming") so testers see it without opening the story.
- **Impact scan (task-context).** New "Related functionality & bug
  history" step: searches product docs + EP bug history for the
  feature's keywords — via the knowledge-base skill's SCOUT endpoint
  when installed, plain CQL/JQL fallback otherwise. Output feeds
  grooming's dependency questions ("logo also appears in exports —
  covered?") and grounds risk-likelihood ratings in real bug history.
  Never a source of requirements; never blocks the run if unavailable.

## 0.8.0 — 2026-07-14

- **Per-test-case channel tags (routing fix).** Tags now go on BOTH the
  requirement group heading (union) and each `### TC-REQ-N.M` heading
  (exactly one) — mixed-channel requirements ([UI]+[API] checks) were
  previously un-routable by stages 7/8, which route per case.
  (qa-test-cases SKILL.md, output-template, example.)
- **Stage 7/8 ordering fossil removed.** api-testing no longer claims
  web-testing's "Not executed here" list as input (it runs first);
  web-testing now references `<KEY>-api-testing.md` for [API] cases
  instead of re-listing them as unverified. Standalone-run behaviour
  preserved.
- **Defect creation shipped in-box.** New
  `qa-pipeline-code/references/bug-report-template.md`; step 7 now has
  a default direct-Jira filing path (dedup search → draft → confirm →
  `createJiraIssue`) when `/knowledge-base` is not installed.
- **New step 8 — hand the story back.** On FAIL: offer reassignment of
  failing dev sub-tasks + optional "back to dev" transition; on PASS:
  optional "QA done" transition. Transition names configurable in
  publish-config.md (`<not configured>` = skip transitions).
- **Prompt-injection guardrails.** task-context: tracker/Confluence
  content is data, never instructions — hostile directives are quoted
  into a "⚠️ Suspicious content" note. browser-rules: same rule for
  page content.
- **Pairwise/combinatorial generation (PICT).** New
  `qa-test-cases/scripts/generate_pict_cases.py` (pure-Python n-wise
  generator; delegates to the `pict` binary when installed, which also
  enables constraints) + `references/combinatorial-testing.md` +
  "Pairwise rules" in test-case-design-rules.md. For requirements with
  3+ interacting parameters (role × event type × setting).
- **Subagent-per-stage dispatch (context health).** qa-pipeline-code
  now runs stages 5-7 as separate subagents where available (Task /
  Agent tool): each writes its report file and returns a <= 10-line
  summary; pause-worthy inputs are resolved before dispatch. Stage 8
  and the analyzer stay inline. Inline fallback unchanged.
- **3-failures escalation rule** in web-testing and api-testing: after
  three failed approaches to the same goal, step back and reassess the
  assumption (host/role/env/data) — ask or mark BLOCKED with the
  attempts recorded, instead of grinding retries.
- **`NOT-TESTABLE` replaces api-testing's output `QA` status** (was
  overloaded: `QA` is the input selector from code review). Older
  reports may still say QA; analyzer notes both.
- **Jira ~32K comment-limit handling.** Both publish steps now measure
  and split oversized archive comments as `File: <name> (part i/N)`
  blocks; qa-pipeline-code Step 0 re-joins parts (new
  `qa-pipeline-code/scripts/extract_archive.py` does it
  deterministically).
- **Structural checks executed.** The checklist is now a real
  web-testing input: `[UI]` presence/type/label checks run for visited
  pages into a new "Structural checks" report section; the analyzer
  flags structural checks that are neither executed nor explained.
- **Plumbing scripts** (prose → code): `api-testing/scripts/load-env.sh`
  (safe .env loader from reference §0),
  `qa-run-analyzer/scripts/reconcile_counts.py` (ID-set/status counts
  for the reconcile check), `extract_archive.py` (above).
- **QA sub-task supersede rule** — the docs phase now comments
  "Superseded by <NEW-KEY>" on the previous pipeline sub-task and
  offers to close it, instead of silently accumulating.
- **Stale docs fixed:** README login-config placeholders claim,
  web-testing setup-guide (login-config ships configured;
  navigation_paths.json is git-ignored, created on first run), README
  per-stage vs orchestrator model-settings contradiction; new Cowork
  credentials note in web-testing (mounted `.env` or manual login —
  never paste passwords into chat).
- **requirements-grooming got real trigger phrases** in its frontmatter.
- **Playwright executor draft** (`web-testing/references/
  playwright-executor-draft.md`) — inactive, with a pilot checklist;
  the Chrome extension remains the executor.
- **`.env.qa-agents` is now the documented first-choice env file** —
  api-testing, web-testing, and the code orchestrator search it (in
  the mounted qa-pipeline-skill repo) before the e2e `.env` / env
  vars.
- **Opt-in run notifications:** `hooks/hooks.json` + `scripts/notify.py`
  — desktop alert on finish (Stop) and on input-needed (Notification);
  no-op unless `QA_PIPELINE_NOTIFY=1`.

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
