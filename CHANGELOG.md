# Changelog

All notable changes to the `ep-qa-pipeline` plugin. Versions follow
semver; bump BOTH `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` — the marketplace manifest is what
signals an update to installed copies.

## 0.40.0 — 2026-09-10 — the docs phase loses a stage

The docs-phase half of the same-day cold review of 0.36.0 ("three
changes that would most improve the docs phase for a weekly QA
engineer"). One structural change and a set of dead weight removed.

**Stage 3 (`qa-checklist`) is folded into stage 4 (`qa-test-cases`).**

- Nothing downstream read `<KEY>-checklist.md` for anything but its
  `[UI]` structural lines: the test cases restated every behavioural
  check, the publish turned the structural ones into STRUCT cases, the
  analyzer counted both. So the decomposition into checks is now the
  **first working step of qa-test-cases** — done in full, method
  unchanged (`references/check-decomposition.md`, the former
  checklist-design-rules with a "Behavioural vs structural — where each
  check goes" section) — and only two things are written: **test
  cases** for the behavioural checks and a **`## Structural checks`
  section** at the end of the test-cases file for the structural ones,
  one line each: `- [ ] REQ-N/struct-k [UI] <check>`. The id is the one
  STRUCT cases already carried as `detail.pipelineId`, so the publish
  mapping and the code phase's rebuild (`REQ-N/struct-k ·
  <PREFIX>-STRUCT-NN`) change source file, not shape.
- One fewer file, stage, pause and budget; the docs orchestrator runs
  1 → 2 → 4 → analyzer → publish. **Stage numbers 4–10 are unchanged**
  so every cross-reference in the plugin still holds; stage 3 is listed
  as retired where the sequence is spelled out. `skills/qa-checklist/`
  is deleted; its trigger phrases ("build a checklist", "make the QA
  checklist") route to qa-test-cases. `<KEY>-checklist.md` is read-only
  legacy on tickets run before 0.40.0 (web-testing, the analyzer,
  data-locations say so).
- Every consumer re-pointed: qa-service-publish (STRUCT source table,
  `detail.notes`, the rebuild line, the legacy-format appendix),
  qa-pipeline-code step 0 (rebuilds the section, not a file),
  web-testing (input 3, data sources, step 6.6, the report section
  header), playwright-executor, api-testing (its optional checklist
  input is gone — `[API]` "field present" checks are cases), pr-summary,
  qa-manual-runsheet, the analyzer (§1 coverage, traceability,
  structural presence, §3 tags, §4 STRUCT count), status-vocabulary,
  requirements-grooming, test-case-design-rules, the fixture, evals,
  README, MAINTAINERS, CLAUDE.md.
- `reconcile_counts.py` now prints, for the test-cases file, the
  **channel-tag histogram** (`[API][UI]` counted once, under its own
  key; `untagged=` when a heading has none) and the **structural-line
  count** (`struct=`), so the Statistics block and the publish count
  gate are mechanical, not a hand tally — the SKILL's verification
  step and the template point at it. Self-test covers both, including
  a rebuilt line with a stableId and a legacy `REQ-99.1:` line that
  must not count.

**One ExpoPlatform calibration example instead of two leads-CRM ones.**

- `qa-test-cases/references/test-cases-example.md` is now the expected
  docs-phase output for the tracked fixture `fixtures/EP-0000-context.md`
  (the "Featured exhibitor" toggle): six REQs with `[risk]`, `[UI]` /
  `[API]` tags, one `[core]` per behavioural REQ, the 3-value BVA the
  High-risk limit demands, both versions of the unresolved badge text
  asserted, a Structural checks section and a Statistics block that
  `reconcile_counts.py EP-0000` reproduces (10 cases, 6 core, 3
  structural). MAINTAINERS' smoke test compares against it.
  `checklist-example.md` went with its folder.

**Dead weight removed.**

- The eight per-skill `setup-guide.md` files (task-context,
  requirements-grooming, qa-checklist, qa-test-cases, pr-summary,
  code-review, api-testing, web-testing) — DOU-template "how to adapt
  for your tracker" text that nothing read, half of it stale (rules
  called "ISTQB, fully universal" now carried ExpoPlatform-specific
  provenance / `[core]` / PICT rules; two said `.env` lived in the e2e
  repo). Everything still true is in README → "Before you run",
  `environment.md`, or the reference the bullet names.
- README's per-stage "Suggested settings" column — stages 1–4 run in
  Cowork where no per-stage model choice exists, and both orchestrators
  override it; the one-line orchestrator note stays.
- `task-context/references/field-maps.md`: one table instead of the
  same table five times (the types differ in one cell and one row's
  weight).
- "give it to the user for download" (task-context,
  requirements-grooming, web-testing) → "report its path" — the files
  live in the run folder, not in a chat download.
- requirements-grooming's input boilerplate no longer says a context
  file may come from "the suite" — it never can.
- The analyzer's § 4 says when it actually runs: at the docs phase's
  step 5 there is no suite yet, so it reports `not published yet` and
  the real sync check is the code phase's step 0 or an on-demand run.

**Not in this release:** `qa-pipeline-code/SKILL.md` is still 762
lines (the gate's one WARN) — moving its step-0 and step-6 detail into
references is the next, purely mechanical release. The analyzer's
"Legacy tickets" appendix and the `[core]` ↔ `detail.core` / STRUCT
title ↔ check text diffs in § 4 stay on the list.

## 0.39.0 — 2026-09-10 — the tree is clean

The security half of the same-day cold review of 0.36.0. One idea:
**the plugin checkout holds skills and nothing else.** Secrets and runs
move out; every host a stage may touch is named in advance; a password
from the credentials file is never spoken.

**Layout — `EP_QA_HOME` (new: `skills/qa-pipeline/references/environment.md`).**

- `.env.qa-agents`, `runs/` and web-testing's `navigation_paths.json`
  live in `$EP_QA_HOME`, default `~/.ep-qa/` (`%USERPROFILE%\.ep-qa\`
  on Windows). Resolution, the same for every stage and for the two
  scripts: `EP_QA_HOME` → `~/.ep-qa` → the checkout's own copies
  (legacy, **read-only**) → PAUSE. Nothing is ever written into the
  checkout again; a run that cannot reach a home asks, it does not
  fall back. Every `runs/<KEY>/…` path in the plugin is now relative
  to `$EP_QA_HOME`; the file names and the round layout are unchanged
  (`data-locations.md`), so `Move-Item runs\* ~\.ep-qa\runs\` is the
  whole migration. Why: `.gitignore` protected git and nothing else —
  the folder every Cowork session mounts, every installed skill can
  read and the marketplace serves from held ~700 credential-bearing
  files and an API key.
- The e2e project's `.env` is no longer a fallback anywhere — two files
  with the same variables gave two answers on which alpha was under
  test (api-testing-reference §0, login-config, MAINTAINERS, the walk,
  stage 9, both orchestrators now name one file).
- `scripts/load-env.sh` gained `ep_qa_home`, `ep_qa_env_file` and
  `host_allowed` (and `--home` / `--env-file` / `--host-allowed HOST`
  modes); `reconcile_counts.py` resolves `runs/` under the same home
  (self-test covers `EP_QA_HOME` winning over the cwd, with `~`
  isolated so a real `~/.ep-qa` cannot leak into the test).
- `verify_plugin.py` **check 9 — tree**: FAIL while a `.env*` file or a
  `runs/` folder is inside the checkout; WARN with a count for legacy
  root artefacts (`EP-*`, `GS-*`, `build_*`, `_*`). Check 3 now walks
  `git ls-files` (so `hooks/`, `fixtures/`, `docs/` are covered and an
  untracked runtime file is not), check 4 requires the backtick form
  (`qa-pipeline` is a substring of `qa-pipeline-docs`), and the
  frontmatter parser accepts `>-` / `|` block scalars.
- `.gitignore`: `_*` → `_[!_]*` so a package's `__init__.py` can ship;
  the `fixtures/` negation is back (below); the header says what the
  rules are now — a second line of defence, not the workspace.

**`ALLOWED_HOSTS` — "never target production" is now a check.**

- `ALLOWED_HOSTS=` in `.env.qa-agents`: comma-separated hostnames,
  `*.suffix` wildcards. Before its first request, api-testing (login),
  web-testing (first navigation), stage 9 (provisioning), the walk
  (AGENT-RUNS pre-flight) and the code orchestrator's step 0 take every
  host they are about to use and check each against the list. Not
  listed → PAUSE naming the host; the stage never adds it and never
  "just reads". List missing → the run does not start. **Hosts ending
  in `expoplatform.com` are refused even when listed** — production is
  never a target (the QA Service and Jira are connectors, not targets).
  The test-event authorisation stays as the second, separate gate:
  that one asks *which event*, this one asks *which machine*.

**Secrets in chat.**

- A `.env.qa-agents` value is never spoken, printed or hinted at — the
  walk's "Which account again?" answer and the plan's session line for
  an admin/organiser account read "the admin account from your
  `.env.qa-agents`". Only stage-9 **throwaway** accounts may have their
  password in the plan and in chat: they exist for one run, get a
  **random password each** (`secrets.token_urlsafe`; the reference §12
  example no longer uses a fixed `Test12345!`), are recorded in
  `-testdata.json` with `"throwaway": true`, and are **retired at
  stage 10** — new `qa-manual-results` step 4c lists them and offers
  the deactivation in one confirmation (or writes "retire N test
  accounts" into Needs a human where the environment has no path).
  Until now nobody owned teardown; alpha accounts from every run were
  live credentials nobody rotated.
- The admin-token example in the api-testing reference §2 builds its
  JSON body with `python3` from the environment instead of
  interpolating `$ADMIN_PASSWORD` into a string — a quote in the
  password no longer breaks the body, and `bash -x` no longer echoes it
  (§0 already said so; §2 contradicted it).
- Identities out of documentation: `publish-config.md` no longer
  carries the operator's e-mail and Atlassian accountId — the assignee
  is `QA_OPERATOR_EMAIL` from `.env.qa-agents`, resolved at run time
  (the walk uses the same variable as the default tester principal).
  The internal database host named in the reference §11.1 is gone.

**Repo hygiene.**

- **0.38 was wrong about `fixtures/`:** `fixtures/EP-0000-context.md`
  exists and is tracked — the review snapshot simply did not include
  it. The `.gitignore` negation lines are restored, MAINTAINERS' smoke
  test names the fixture again, and `verify_plugin.py --selftest`
  already listed it as allowed.
- `docs/` is the home for the review, retrospective, spec and prompt
  files that sat in the root (MAINTAINERS layout tree); the move is a
  `git mv`, tracked history intact. README and MAINTAINERS say hooks
  are Claude Code only.

**Migration (once, by hand):** create `~/.ep-qa`, move `.env.qa-agents`
and `runs/` into it, add `ALLOWED_HOSTS=` and `QA_OPERATOR_EMAIL=` to
the file, mount `~/.ep-qa` in Cowork sessions that need to write.
`verify_plugin.py` tells you what is still in the tree.

**Deliberately not in this release:** `TEST_EVENT_IDS` (the event
authorisation pause covers it for now — revisit if a wrong event is
ever named); the docs-phase diet (next).

## 0.38.0 — 2026-09-10 — the seams

The rest of the same-day cold review of 0.36.0: the 🟡 items that do
not change what is recorded but where two files disagreed, or a
template contradicted the rule its SKILL states. None of these is a
new mechanism; each is one document brought in line with the one that
was already right.

**Templates now say what the SKILLs require.**

- **`Source:` meant two things.** In the code-review, api-testing and
  web-testing FAIL skeletons `Source: QA` was the *arrival* status,
  while the SKILLs, `sources-of-record.md` and the analyzer's § 7 gate
  require `Source: <register row>` + `Clause:` on every FAIL and
  `RISK-CR-*` row — an agent following the template failed the gate
  every run. The arrival field is now **`Arrived as:`** (the Results
  column too, in api- and web-testing; `reconcile_counts.py` reads
  statuses by token, not by header, so nothing parses differently),
  and every FAIL / FAIL CONFIRMED / RISK skeleton carries `Source:` and
  `Clause:`. `status-vocabulary.md` calls `PASS(code)` and
  `code-review risk <n>` *arrival markers*.
- **Statistics tables carry every status the SKILLs emit** — added
  SPEC-DEFECT (all three), BLOCKED (unverified), NOT EXECUTED,
  NOT-TESTABLE (instrumentation), OBSERVATION (no source checked); a
  zero row may be omitted, a status present in Results may not.
- **web-testing evidence is in the contract, not only in the
  executor note.** Step 6.4 writes `<KEY>-web-evidence.md §<n>` for
  each FAIL / FAIL CONFIRMED (both backends), step 8 puts it in the
  report, and the template gained `Backend:` and `Evidence:` header
  lines plus an `Evidence:` line per FAIL — what qa-pipeline-code step
  6 and the analyzer have required since 0.35.
- **Bug report `Expected result` = the register clause**, not the test
  case's `Exp:` block (a test case is not a source of record); the
  `Exp:` moves to the Source section beside the register row, and the
  bug carries its evidence pointer. The "add the bug keys to the
  sub-task as a short comment" rule is gone — it contradicted the
  two-comment rule; keys go in the human summary's Confirmed bugs.
- **Story notes:** "full reports on QA sub-task <KEY>" pointed readers
  at a place that has held nothing since 0.33; both notes now name the
  QA Service run and the run folder. Both are labelled as posted by
  `qa-manual-results` step 4b; `publish-config.md` and the orchestrator
  say the same instead of "step 8" / "step 4". `jira-writing-style.md`
  no longer exempts "machine archives".
- **`-human-summary.md` written at step 6 carries `Status: DRAFT —
  awaiting stage 10`** — the template's `VERIFIED` line cannot be true
  before the human round; stage 10 rewrites it.
- **Step 6 post-yes order is numbered:** create run → record → write
  the draft summary → post the status comment (which quotes the run id
  — it cannot go first).

**Run and suite mechanics.**

- `test-runs.md`: `<mode>` in the run title is `first run` / `retest
  <k>` / `bug-fix` — the first run's title was a guess.
- `qa-pipeline-code` step 0: if `get_suite` returns summaries without
  `detail`, `get_test_case` each in-scope id. A retraction is "a
  re-record (test-runs.md → Retractions)", not "the supersede
  convention" (retired 0.30).
- `qa-service-publish.md` gained **Legacy formats** — the pre-0.34
  tracker line, the structural-checks comment and the pre-0.33 archive
  shape in five lines — so step 0's fallbacks name a documented shape
  instead of "the tracker lines". "Until 0.33" → "Until 0.34".
- Dual-tagged `[API][UI]` cases: the test-cases Statistics block has
  its row (the SKILL already demanded one) and publish maps it to
  `levels: ["AE", "E2E"]` — one case, two levels.
- `walk-plan-format.md`: sessions run in product-role order (admin →
  organiser → exhibitor → visitor — set-up before its effect); the
  `machine:` example uses the vocabulary it claims to use
  (`CR PASS · API — · WEB NOT EXECUTED`).
- `runsheet-format.md`: the export spec's column letters agree with
  its own twelve-column table (A–G dim, H–J work, K–L tester's, tint
  A–J, Covers = M); the palette is "the one every
  `build_runsheet_<KEY>.py` ships" — `build_data_pack.py` never existed.

**Routing and docs.**

- `qa-pipeline-docs` **publish-only mode**: "add these cases to QA
  Service" / "publish the test cases" with the docs files already in
  `runs/<KEY>/docs/` runs steps 5–6 only. The eval arrow that pointed
  at a route which could not fire now can.
- Triggers: "process the ticket" is the dispatcher's, not
  task-context's; "run the QA checks" is the code orchestrator's, not
  web-testing's. Descriptions and `evals/triggering.md` agree.
- `playwright-executor.md` defers to SKILL → Scope (the routing
  invariant) instead of restating a narrower rule.
- Analyzer Input lists `<KEY>-web-evidence.md` and `<KEY>-sources.md`
  (§ 5 and § 7 audit them); the report gains a **Source fidelity**
  health row.
- Leftovers: "working directory" (code-review, pr-summary,
  qa-pipeline-docs) → run folder; qa-test-cases "published into a Jira
  comment" → read by the code phase and rendered on cards; the stale
  "why PR-URL / REST mode usually 403s" clause dropped (the reference
  says the opposite); api-testing "alongside web testing" → before;
  `data-locations.md` "where no archive was posted" → the only copy,
  full stop; README no longer claims a human confirms every stage —
  it names the pauses; the README handoff sentence and the
  orchestrator heading say stages 5–9 hand off to stage 10 (10a walk,
  10b results). MAINTAINERS' smoke test no longer names
  `fixtures/EP-0000-context.md` (never committed; `.gitignore`
  un-ignore lines removed) — use a recent ticket's context file. Two
  relative paths that pointed one directory too shallow
  (`data-locations.md` → results-comment-template, `status-vocabulary.md`
  → sources-of-record) now resolve; the api-testing Statistics row
  `NOT-TESTABLE (mapping)` uses the vocabulary's bare `NOT-TESTABLE`.

**Deliberately not in this release** (next two): the security layout
(`EP_QA_HOME`, allowed hosts, `.env` outside the tree, a verify check
for it) and the docs-phase diet (fold stage 3 into 4, drop the
setup-guides, ExpoPlatform calibration example, orchestrator < 500
lines).

## 0.37.0 — 2026-09-10 — the record cannot lie

Implements the record-affecting findings of the same-day cold review
(four readers: consistency, executability dry-run on a fictional
EP-57000, docs-phase quality, security) of 0.36.0. Each item below
would have produced a *wrong record* with no rule violated. The stale
one-liners the same review found are the next release; the layout
and docs-phase items after that.

- **Walk: a failed positive control is BLOCKED, not FAIL.** An absence
  check answered "the list is empty… and the counter reads 0" mapped to
  FAIL, which at stage 10 files a Jira defect — for a fixture that was
  never there (the tracking trap of `provisioning-rules.md`). New row in
  the verdict table: BLOCKED (`fixture not proven`), unless the control
  is the case's own assertion.
- **Walk: "deferred twice" is not run, never SKIPPED** — two files
  said different things and stage 10 records them differently
  (`skipped` vs untouched `not_run`).
- **Walk: the state file can rebuild the results file.** Schema gains
  `verdicts` (per-case split of a `covers` list), `half`/`restsOn`,
  `history` (every earlier answer; a changed verdict never overwrites),
  `run` (AGENT-RUNS call + result, redacted), `blocked` (reason, probe
  time, unblock), `observations`; `position` = the next card. Tokens,
  codes and passwords the tester pastes are written as
  `<token supplied>` — the one edit ever made to the tester's words.
- **Walk: writes are confirmed before, not after.** An AGENT-RUNS call
  whose write class is snapshot-revert or throwaway is shown and runs
  only on "run it"; re-probing a BLOCKED card uses read-only means
  only; pre-flight checks `.env` when the plan has AGENT-RUNS cards
  (absent → those cards BLOCKED up front, not discovered at card 7).
- **Walk → stage 10 seam.** `Completeness: complete (N cards declared
  not run)` for a walk the tester ends for good — stage 10 writes it
  back without asking; `stopped early` still means "resume later".
  Stage 10's write-back bullet no longer says `source: manual` for
  every row — it follows the row (`manual` → tester; `machine
  (witnessed)` → agent label), and a `Half` row's note carries
  ` · Half: rests on <machine verdict>`. `-walk-state.json` is kept as
  the audit trail. A one-line "the fix works" verdict is accepted as a
  per-case TC/Result/Notes row (bug-fix mode).
- **STRUCT cases join by stableId, end to end.** Step 0 rebuilds each
  structural check as `- [ ] REQ-N/struct-k · <PREFIX>-STRUCT-NN [UI]
  <check>`; web-testing's Structural checks table gains a `Case` column
  and uses the vocabulary (`NOT EXECUTED — page not visited`, never a
  bare "not visited"); step 6 records them per the mapping; scope is
  reported `M + S` and roster count = M + S in the post-publish check.
  Without this, 0.33's STRUCT verdicts could not reach the run.
- **Bug-fix mode publishes behind its own REQUIRED PAUSE.** 0.33 said
  "the same single confirm as step 0" — step 0 has none in normal mode,
  so a shared-production write had no yes. Now: derive → preview (suite,
  requirement, each case) → yes → publish → stages 5–8 → run. Later
  regression cases go through the same preview; `add_run_cases` only
  for a case learned after the run exists.
- **Never delete.** `qa-service-publish.md` claimed "there are no
  delete tools"; the connector has `delete_suite`, `delete_test_cases`,
  `delete_requirements`, two folder deletes and `merge_duplicate_case`.
  Named, and forbidden to every stage: correct, retire (`status: na` +
  `discrepancy:`), or leave to a human — never delete or merge.
- **Stage 9 suite corrections get one preview + yes** (they were the
  only unconfirmed writes to the suite left); retest detection ignores
  the run this pass's step 6 just created and looks for prior artefacts
  in earlier `r*` folders (both fired on every first run otherwise);
  the coverage floor in retest mode applies to the scoped REQs only.
- **Orchestrator:** an explicit retest / fix-landed / bug-fix request
  always creates a new pass folder — the resume signals never override
  the user. **Stage 10 appends ledger rows** for what its summary
  reports as unsettled, since no analyzer pass follows it.

## 0.36.1 — 2026-09-10 — the gate bites the right thing

Hotfix from the same-day cold review of 0.36.0 (security lens), before
the gate blocked its first legitimate commit.

- **False positive that would have taught bypass.** The staged-artefact
  guard matched its patterns against the whole path, so `-runsheet`
  fired on `skills/qa-manual-runsheet/SKILL.md` and every commit
  touching that skill would FAIL — the only way past being `--no-git`,
  which switches off exactly the check that guards credentials. Now
  judged on the path's first segment (`runs/`) and its **basename**
  only; `fixtures/` always allowed. Patterns extended to the names
  `.gitignore` already knows (`navigation_paths.json`, `*.bak`,
  `*.diff`, `*-preserved-entries`, `*-open-items.md`,
  `*-manual-results.md`, `*-human-summary.md`, `*-web-evidence.md`).
- **`--selftest`** for the guard itself: 10 paths it must catch, 9 it
  must allow (the skill folders among them). Run it after any pattern
  edit.
- **Windows:** files read as `utf-8-sig` (PowerShell 5.1's BOM made
  check 2 report "name None"); `git diff -z` with NUL splitting (paths
  with spaces or non-ASCII stayed whole); subprocess and stdout forced
  to UTF-8 with replacement so a ⚠/🔴 in the output cannot crash the
  report on a cp1252 console. Docstring step reference fixed (6.4).

## 0.36.0 — 2026-09-10 — the gate

**`scripts/verify_plugin.py` ships** — parked since 0.18.2 (review
§4.9), written today after two days in which every defect class it
catches actually happened: two skill descriptions over the 1024-char
discovery ceiling (caught by hand, after the fact), the 0.27 fix
"written and never committed" for two rounds, CRLF churn on five files,
two files without a trailing newline. Fifth and last of the "old beside
new" clean-ups agreed on 2026-09-10 — the one that keeps the other four
from regressing.

Eight checks, a few seconds, non-zero exit on any FAIL:
versions (plugin.json = marketplace.json = CHANGELOG top heading);
skills (frontmatter `name` = folder, description ≤ 1024, > 500 lines
WARN); text (LF, no NUL, trailing newline on every tracked text file);
wiring (every skill named in README and has a `## <name>` eval
section); references (every `references/*.md` a skill names exists —
same-skill, `<skill>/references/` and `../<skill>/references/` forms);
vocabulary (every status in `status-vocabulary.md` has its base token
in `reconcile_counts.py` STATUSES); selftest (`reconcile_counts.py
--selftest`); staged (`git diff --cached` contains no run artefact —
the `git add -A` guard, verified to fire on `runs/…`, `EP-*` and `_*`
paths and clear on a clean stage). `--root X` checks another checkout,
`--no-git` skips the staged check.

Its first run against the real tree found three broken cross-references
(an "its `references/…`" in `absence-check-protocol.md` and
`data-locations.md`, a `skill/references/…` form in the analyzer):
fixed, and the checker accepts the last form. Wired into MAINTAINERS
recipe step 6.4 and the where-to-look table, and into CLAUDE.md's verify
commands as "before every commit". Known WARN left standing:
`qa-pipeline-code/SKILL.md` at 735 lines — the orchestrator diet is the
review's §4.10, a separate release.

## 0.35.0 — 2026-09-10 — one browser

**web-testing has one default backend — Playwright MCP — and one
fallback — the Claude in Chrome extension.** The description said
"via a Chrome extension" while the body said "Playwright MCP
(preferred)" (the September review's description↔body drift), and a
third browser (Claude's built-in pane) had appeared with no rules at
all. Fourth of the five "old beside new" clean-ups agreed on
2026-09-10; also closes the Playwright evidence-path item carried since
EP-56197 r2 (open-items #12, review §4.5).

- **Backend rule** (`web-testing` "Execution backends"): Playwright
  whenever its tools are in the session; the extension only when they
  are absent; neither → PAUSE. The built-in browser is named and
  explicitly *not* a backend until rules exist (no scripted login; a
  persistent profile changes what a fresh session means). The report
  header and chat say which backend ran. Description rewritten (683
  chars); "browser testing" / "test in the browser" / "run the QA
  checks" still route — no eval change needed.
- **Evidence a Playwright FAIL can actually produce**
  (`playwright-executor.md` → Evidence): the MCP backend writes only
  inside its sandbox root and refused the documented "save in the
  working directory" path — every Playwright-backed FAIL was
  non-compliant with its own skill for two rounds. Now: screenshot into
  the sandbox and copy to `runs/<KEY>/r<N>/evidence/` when host-side
  file tools exist; **always** write `<KEY>-web-evidence.md §n` (URL,
  quoted DOM/text reading, console lines captured before navigating
  away) and cite `§n` from the report row and the run's roster note.
  `status-vocabulary.md` FAIL row and a new analyzer 🔴 ("neither
  reading nor screenshot = a claim") accept either form.
- **Wiring:** `qa-pipeline-code` stage-8 dispatch and the split-runs
  note (Playwright makes the code phase a single-environment run);
  README flow item 8; MAINTAINERS channel routing and environment
  matrix (stage 8 now "either" with Playwright).

## 0.34.0 — 2026-09-10 — the run is the tracker

**The checkbox-tracker comment on the QA sub-task is retired.** It was
one `- [ ] TC-REQ-N.M — <name> [channel] · <stableId>` line per case,
meant to be ticked by hand. Nobody ticked it: the connector cannot, the
human's verdicts go to the QA Service run (0.30.0), and the orchestrator
carried a standing reminder that "checkboxes are manual-only" — the
sign of a mechanism kept alive by instruction rather than use. Third of
the five "old beside new" clean-ups agreed on 2026-09-10.

The tracker did carry two things the code phase needed, and both now
live on the items themselves in QA Service (verified against the
connector's schema: `detail` is free-form on cases and requirements,
and requirements have a native `sources[]` with `kind: jira`):

- **Per-ticket scope inside a per-feature suite** — every case
  published for a ticket gets `detail.ticket = <KEY>`; every
  requirement gets `sources: [{kind: jira, label: <KEY>, url}]` (plus
  its Confluence source with `anchorUrl`). Step 0 executes the cases
  whose `detail.ticket` is this run's key, plus team-added cases
  tracing to this run's requirements. Feature tags were considered and
  rejected for this: the tag catalogue is the platform-feature
  vocabulary and each tag needs approval.
- **The REQ-N / TC-REQ-N.M ↔ stableId map** — `detail.pipelineId` on
  every requirement (`REQ-3`), case (`TC-REQ-3.2`) and STRUCT case
  (`REQ-3/struct-1`). The map lives on the item it belongs to and
  cannot go stale on its own; the publish reference's rule against a
  standalone map block stands.

Wiring: `qa-pipeline-docs` step 6 (tracker comment removed; the count
gate is kept and attached to the publish preview; the "How to use this
ticket" note now says there is nothing to tick — the suite and its runs
are the record, the ticket gets one status line and one summary);
`qa-service-publish.md` mapping tables and "Code phase — suite as the
case source" (scope by `detail.ticket`, join by `detail.pipelineId`,
legacy fallbacks named); `qa-pipeline-code` step 0 scope + REQ-N
rebuild, the "Tracker note" bullet and the final-response reminder
removed, description now says the cases come from the suite (986
chars); `test-runs.md` roster definition; `data-locations.md` Jira
row; the analyzer's sync check compares only this ticket's marked
items. Pre-0.34 suites carry neither marker: step 0 falls back to the
legacy tracker-line ids, then to title match.

Also fixed on the way: two sheet-era leftovers from 0.31 ("Reference-tab
coverage map" in the analyzer, "delegated … (Reference tab)" in stage
10) now name the walk plan's Coverage section.

## 0.33.0 — 2026-09-10 — one record

**Jira archive comments are retired. The QA Service suite + run and the
run folder are the record; Jira gets one status line and one human
summary per pass.** The archive was a text-in-comments data store built
before the suite existed: fenced dumps of the checklist, test cases and
every stage report, re-joined by a script, split into parts above
30,000 characters, silently truncated by Jira's markdown→ADF at least
once, and running to three to five unreadable comments per pass — the
0.11.2 dedup, the 0.26.0 target rule and the 0.30.0 run were each a
step away from it. Second of the five "old beside new" clean-ups agreed
on 2026-09-10; closes EP-56998 open-items #13.

- **Docs phase posts no fenced file into Jira.** `qa-pipeline-docs`
  step 6: the "no suite → full archive" branch and the "structural
  checks only" block are gone. The QA sub-task keeps its description
  and the one-line-per-case tracker comment. No suite (connector absent
  / declined) → nothing is posted in its place; `runs/<KEY>/docs/` is
  the only copy and the code phase reads it on this machine.
- **Structural checks become suite cases.** The checklist's `[UI]`
  presence / label / field-type checks — no test case by stage 4's
  rule, executed by stage 8 — used to live only in a fenced block on
  the sub-task, so their verdicts never reached the run. They are now
  `<PREFIX>-STRUCT-NN` cases (`levels: ["E2E"]`, `techniques:
  ["UI-CONF"]`, folder `<REQ area> — structure`, traced to the REQ;
  `qa-service-publish.md` → "Structural checks"). Not counted in the
  test-cases statistics; the publish preview reports "N cases + S
  structural checks"; the analyzer's sync check expects exactly S
  extras. Step 0 rebuilds the checklist's structural section from them;
  stage 8 reports each with its stable id and its verdict goes on the
  run.
- **Bug-fix mode gets a record.** A standalone Bug / Defect had no suite,
  no run and no durable verdict (EP-56998 #13). Step 0 now publishes
  the 2–4 mini cases to the FEATURE's suite before stage 5 — append
  when the feature has one, create it when not, named after the
  feature per the existing "Suite selection" rule — with one
  requirement carrying the ticket's own expected result verbatim
  (`detail.source: Bug <KEY>`), `Regression for <KEY>` in each case's
  notes, TC-1 as `core`, and later regression cases added via
  `add_run_cases`. Same single step-0 confirm. Connector absent → PAUSE
  and say what is lost (`qa-service-publish.md` → "Bug-fix mode").
- **Code phase wave 1 = the run + one status line.** "Comment 1 —
  machine archive" is removed from `qa-pipeline-code` step 6 and from
  `results-comment-template.md` (whose head is rewritten; the 0.26.0
  target table survives as "which ticket gets the status line and
  summary" — the answer is now "every ticket, and nothing else"). The
  post-publish check: exactly one wave-1 comment, and **a fenced file
  dump on ANY ticket is a ❌** — the QA sub-task included. Split runs:
  both environments read the same `runs/<KEY>/r<N>/` (they mount the
  same repo); the run carries the verdicts regardless.
- **Stage 10 posts no archive of `-manual-results.md`** either; a resume
  or reconciliation on another machine takes the machine verdicts from
  `get_test_run` and says the report prose is unavailable, instead of
  reconciling against nothing.
- **Resume order** (step 0): run folder → the QA Service run for
  verdicts → PAUSE. `extract_archive.py` stays as a **legacy reader**
  for pre-0.33 tickets and says so in its docstring; the shared
  input-resolution boilerplate in 11 skills now names the archive as
  legacy only. `data-locations.md` Jira row and resolution step 4,
  `test-runs.md` retraction section ("the one sanctioned cross-ticket
  comment"), `open-items-ledger.md` durable-copy paragraph, MAINTAINERS
  environment matrix / split-run note / hand-off bullet / lookup table,
  README, dispatcher, web-testing input 3 and the analyzer (new 🟡
  "archive posted") updated to match. Descriptions: qa-pipeline-code
  989, qa-pipeline-docs 788 chars.
- **What was not weakened:** the two-wave rule, the retraction target
  rule, the "no walk-up" rule, the 0.11.2 one-copy principle (now
  literally one copy), the source-of-record gate for bug-fix expected
  results.
- **Deliberately not changed:** the checkbox tracker comment on the QA
  sub-task (item 3 of the review — next release), and stage 4's rule
  that structural checks get no TC in the test-cases file (the suite
  holds them; the file's register is unchanged).

## 0.32.0 — 2026-09-10 — the run folder

**Run artefacts move out of the repo root into `runs/<KEY>/`.** When
this was written the root held 688 `EP-*` files, 17 `build_*` /
`repro_*` scripts and every walk plan and testdata pack with live
passwords, beside the distributable. Every MAINTAINERS gotcha about
`git add -A` — including the run where 84 account passwords were one
command from a commit — exists because the repo doubled as the run
workspace with no structure. `.gitignore` had anticipated the fix
since 0.13 ("future layout: per-run folders — `runs/`") and nothing
ever used it. First of the five "old beside new" clean-ups agreed on
2026-09-10.

- **Layout, defined once** in `qa-pipeline/references/data-locations.md`
  (which already outranks every skill's Input/Output section by its own
  rule): `runs/<KEY>/docs/` for stages 1–4, `runs/<KEY>/r<N>/` for
  each code-phase pass, `runs/<KEY>/<KEY>-open-items.md` for the ledger.
  **File names do not change** — `<KEY>-<stage>.md` stays, so every
  script, regex and archive label keeps working; only the directory
  changes.
- **Rounds are folders, not suffixes.** `r1` is the first pass, `r2`
  the first retest (the QA Service run titled `retest k` is `r<k+1>`).
  The `-retestN-` file-name convention is retired. This closes two
  recorded items at once: the stale-artefact trap (EP-56197 r4
  open-items #24 — a round-3 results file read as round 4's; a folder
  cannot be mistaken for another round) and review item #12
  (`reconcile_counts.py` could not find a retest's case file without
  being told the key twice).
- **Who decides the folder:** `qa-pipeline-code` step 0 lists
  `runs/<KEY>/r*` first thing — a resume continues in the newest
  folder, anything else creates `r<max+1>` — and prints it. The
  post-publish check gains "everything is in the run folder; a
  `<KEY>-*` file in the repo root is a ❌". `qa-pipeline-docs` writes to
  `docs/` and says so once. A stage invoked bare uses the newest round
  or asks.
- **`reconcile_counts.py`** resolves the run folder itself (newest
  `r<N>`, numeric not lexical; legacy cwd when none exists), looks for
  the test-cases file in the pass folder, then `docs/`, then the cwd,
  and never takes a stage report from anywhere but the pass folder. New
  self-test fixture `check_run_folder` covers all of that — the 0.27
  lesson (one fixture let a whole run shape parse as empty) applied to
  directories. `--selftest` passes.
- **"working directory" → "run folder"** across 21 files (skills, README,
  MAINTAINERS); the web-testing persistence note now says plainly that
  `navigation_paths.json` is cross-ticket memory and does not live in a
  run folder. The ledger reference and analyzer §8 lose their
  `-retestN-` examples. MAINTAINERS layout, data-flow and "where things
  live" updated; `.gitignore` reorders so `runs/` is the rule and `EP-*`
  in the root is documented as legacy.
- **Legacy is read-only, not migrated.** Pre-0.32 artefacts in the root
  stay readable as resolution step 2; nothing is written beside them
  again. Optional tidy-up by hand: `runs/<KEY>/legacy/`. No automatic
  move — 688 files with credentials are not something a skill should
  shuffle unattended.
- **Deliberately not changed:** the archive comments, the checkbox
  tracker and the `.env.qa-agents` location — items 2, 3 and the
  housekeeping note of the same review; each gets its own release.

## 0.31.0 — 2026-09-10 — the walk

**The manual round is a guided session, not a spreadsheet.** The run
sheet was designed as "one login, one action, one expected result per
row" (0.12.0) and had drifted into something the person it was built
for could not concentrate on. On EP-56998 the real sheet carried Do /
Expect cells of 500–1500 characters each — harness commands with host
prefixes, WHY THIS IS FIRST, MUST NOT HAPPEN (quoted), HALF-OBSERVABLE
stated plainly, SCOPE — STATE THIS WHEN REPORTING — across twelve
columns of which seven were machine state, on five sheets. Every one
of those fragments was a correct rule (probe the blocker, positive
control, half-verified is not verified, source clause) applied in the
wrong place: the cell, because nobody was there to answer a question.
Nine of the eleven rows handed the tester a curl line. The tester's own
report: "hard to track cases, everything shown in the face, hard to
concentrate; the cases feel robotic; I liked walking them with you one
by one and asking questions." So that is now the stage.

- **New skill `qa-manual-walk` — stage 10a, the live half of the human
  round.** "Walk me through EP-1234": the agent presents the stage-9
  plan one card at a time — who / do / you should see — asks *what
  happened?* (never *did it pass?*), answers questions from the card's
  backstage block, re-probes BLOCKED cards live, and **runs the API /
  harness cards itself** while the tester supplies only what a human
  can (the token from the MORE link, the phone). The tester's words are
  saved verbatim as the note; absence checks and half-observable cards
  get the positive-control question before any verdict; a resumable
  `<KEY>-walk-state.json` survives a chat break. **It records nothing**
  — it writes `<KEY>-walk-results.md` and hands it to
  `qa-manual-results`, whose fail-by-fail confirm and write-back are
  unchanged (`references/walk-session-rules.md`,
  `references/walk-results-format.md`).
- **`qa-manual-runsheet` now emits a walk plan** (`<KEY>-walk-plan.md`,
  new `references/walk-plan-format.md`): cards grouped into login
  sessions in the order a tester moves through the product, each with
  a fixed-key **backstage** block (`machine`, `why-walked`, `source`,
  `positive-control`, `half-observable`, `covers`, `entity`, `wait`,
  `scope`, `say-first`, `retest`, `how-to`, `run`, `blocked`) that the
  agent reads and the tester never sees unasked. Card kinds: WALK,
  SPOT-CHECK, **AGENT-RUNS** (anything with an HTTP verb — the agent
  executes it), BLOCKED (probed), DEVICE. **Voice rules** with a test —
  could a colleague who never read the ticket do this card and tell you
  pass or fail from what they saw? Step 5 is now explicitly a
  *translation* from the stage-4 register (correct for stages 6–8 and
  the count gate, wrong on a card); the self-check gains a voice check.
  All six usability rules, every provisioning rule and trap, the
  selection method (2a), the coverage floor and the retest detection
  are unchanged — they moved from the cell to the backstage.
- **The spreadsheet is an export, on request.** `runsheet-format.md`
  stays as the rendering spec (its REJECTED sections included) and now
  opens with the rendering rule: one row per card, Expect = the card's
  "You should see" plus the backstage lines a tester without an agent
  still needs. Rendered from the plan, never edited on its own. A filled
  sheet is still ingested by stage 10 exactly as before.
- **`qa-manual-results` (stage 10b)** accepts `<KEY>-walk-results.md`
  as its primary input; honours its `source` column (an agent-run,
  witnessed card is recorded `source: machine` with a witnessed
  principal — the 0.30.0 mislabel rule cuts both ways); treats `Half`
  rows as half a verdict; applies the walk's **Case corrections** to
  the suite under the same confirm and never records a `fail` for a
  case whose premise was wrong; reports **Observations** as
  `OBSERVATION (no source checked)` questions; refuses to write back a
  `stopped early` file as a round. New: it must check the results
  file's `Run:` line against the run it is writing to — see the
  open-items answer below.
- **Wiring:** `qa-pipeline-code` steps 9 and 10, the post-publish
  check ("walk-plan outputs exist", voice check), the final response
  and the run-clock label; `qa-pipeline` dispatcher gains the "Guided
  walk" route and reads `-walk-state.json` as a walk in flight;
  `qa-run-analyzer` reads the plan and the walk results, flags 🟡 for a
  plan that fails the voice check, for a walk stopped mid-way, and for
  a source mislabel; `data-locations.md`, README (stage table 9 / 10a /
  10b, flow), MAINTAINERS (layout, environment matrix, where-to-look),
  `evals/triggering.md` (new section + the ❌ arrows on web-testing,
  runsheet, results, dispatcher), `.gitignore` (`*-walk-*` under
  SECRETS — the plan carries passwords by design).
- **Trigger walk (MAINTAINERS step 4), done by a cold reader on the
  descriptions alone.** It found one hard miss that predates this
  release — `qa-manual-runsheet` quoted `"retest"` / `"the fix landed"`
  verbatim, tying with `qa-pipeline-code`'s retest mode — and two
  risks: "walk me through the PR" pulling toward the new skill, and
  `web-testing`'s NOT clause still naming only stages 9 and 10. Fixed
  in the three descriptions (`web-testing` gains "run the cases
  yourself in the browser" so the runsheet ❌ arrow has a claimant;
  `qa-manual-results` gains the "what were the results?" exclusion).
  All descriptions ≤ 1024 chars (walk 965, runsheet 1013, code 983).
- **Deliberately not changed:** `qa-test-cases`. The "robotic" register
  originates there and is *correct* there — `Pre:`/`Steps:`/`Exp:`,
  `[data: …]`, channel tags and forbidden-word discipline feed
  code-review, api-testing and `reconcile_counts.py`. Translation
  happens once, at stage 9, keyed by the case id. Changing the docs
  stages would have required the fixture smoke test and re-walking
  the gate for no gain to the tester.

**Open `[Pipeline]` / `[Pipeline/skill]` items answered (MAINTAINERS
step 1)**, from the newest ledgers and run reports (EP-56197 r4,
EP-56998 r1, EP-56740):

- EP-56197 #24 — stale unsuffixed round-3 results files read as
  current by stage 10 / the analyzer: **implemented in part** — the walk
  results file carries `Run:` and `Round:` in its header, stage 10 must
  match the `Run:` line to the run it writes to and stop on mismatch,
  and the analyzer flags a results file whose run is not this round's.
  The remaining half (round-suffixing every manual-results artefact)
  is deferred to the count-gate release.
- EP-56197 #25 — round-4 verdicts machine-only, TC-11 a standing
  spot-check: **addressed by design** — a SPOT-CHECK card is presented
  like any other and cannot be skipped silently (one sentence of
  pushback, then SKIPPED with reason, never dropped).
- EP-56998 #6 — TC-12 / TC-13 device half is the ticket's only
  decisive instrument: **addressed by design** — the DEVICE card kind,
  platform recorded per answer.
- EP-56998 #2 — the meeting token leaves the platform only by email:
  **addressed by design** — AGENT-RUNS cards name the one human-only
  input (`how-to:`) and the agent runs the rest; the tester never
  pastes a harness line.
- EP-56197 #12 — Playwright FAIL evidence path impossible under the MCP
  sandbox (`playwright-executor.md`): **DEFERRED** to the next release
  with §4.5 of `PIPELINE-REVIEW-2026-09-07.md`; not a manual-round
  change, and this release already changes three stages.
- EP-56197 #17 — `NOT-A-DEFECT (stated exclusion…)` is an invented
  status token: **DEFERRED** to the status-vocabulary release with
  §4.7 (the `OBSERVATION` rename); the two belong together.
- EP-56197 #18 — a falsified process claim reached two published stage
  reports: **no repo change** — the correction is recorded in the
  ledger row; the process fix is `verify_plugin.py` (§4.9, still
  parked).
- EP-56998 #13 — no durable record for a standalone Bug's verdicts:
  **not changed, made visible** — the walk state and results files are
  working-directory-only like every other artefact of a suite-less
  ticket; the results header says so (`Run: no run — <why>`).
- EP-56740 OI-6 — DS repo outside the Bitbucket workspace: **not a
  plugin defect**; raise with the DS team as the ledger says.

## 0.30.0 — 2026-09-07 — the record

**Verdicts are now QA Service test runs, not text in case notes.** On
EP-53978 five verification passes (2026-07-29 → 2026-09-07) each
appended their verdicts to `detail.notes` exactly as the write-back rule
said, and the suite read `requirementCoverage.verified: 0` for all 42
cases after every one of them — text in notes is invisible to every
coverage read, so each pass reconstructed the previous state by hand
from markdown. Recorded as 🔴 [Pipeline] #1 on EP-56133 retest 3
("the durable per-case record does not exist") and left with no
CHANGELOG answer until now — the longest-standing 🔴 in this repo.

QA Service has a first-class run model and the rest of the team already
records through it (`create_test_run`, `record_case_result` with native
supersede, `source: manual | machine`, `principal`, `close_test_run`,
`executed_coverage`, `case_execution_history`, `run_defects`). A
pipeline session even used it once, off-book, on 2026-09-02 (run
`7c3e1ab5…`, "EP-53978 retest 3", 51 cases). That run is the evidence
behind the mapping — including the two mistakes it made, which the rule
now forbids: SPEC-DEFECT recorded as `known_defect`, and human-executed
rows recorded as `source: machine`.

- **New shared reference `qa-pipeline/references/test-runs.md`** — one
  run per pass (title `<KEY> <mode> <date> — <env>`, roster = the step-0
  scope, `principal` on every verdict), the status → verdict mapping
  table (single home; `status-vocabulary.md` points to it), stage 10's
  manual pass into the same run, retractions as re-records, the
  verification reads.
- **A machine `fail` files a Jira defect at record time** — verified:
  the 2026-09-02 run's one `fail` created EP-56912 immediately, and
  nothing in `record_case_result` suppresses it. So **FAIL / PARTIAL
  rows stay `not_run` in wave 1** and the run stays `running` until
  stage 10 records the human verdict. `blocked` was considered for
  those rows and rejected: in the executed tier the whole team reads it
  says "the environment prevented execution", which would hide a defect
  behind an environment problem. `not_run` is the honest state — no
  confirmed verdict yet — and it is exactly what the run sheet already
  means by "the human must walk this row". Narrow wave-1 exception
  (runtime-confirmed + evidenced + blocking) → `fail`, named case by
  case in the confirmation preview: recording it is the filing.
- **For roster cases, the run is the bug-filing path.** A human `fail`
  at stage 10 files one deduplicated defect per case (`created: false`
  when an open issue already references the stable id). The per-case
  `fail` list in the stage-10 preview is the per-bug yes; the
  template-and-`createJiraIssue` path is now for findings with no
  roster case (unpromoted `RISK-CR-*` rows, confirmed observations).
- `qa-service-publish.md` → "Result write-back" and "Retraction
  convention" rewritten around the run. The `Run <date> …` note lines
  and the `⚠ CURRENT VERDICT:` first line are **retired**: they
  re-implemented what the service does natively. Notes keep the
  `discrepancy:` line (a property of the case) and pre-0.30 history.
- `qa-pipeline-code` step 6: run preview in the confirm pause (title,
  env, release or `none`, roster count = scope count, per-verdict
  counts, `not_run` count, each narrow-exception `fail` by case);
  post-publish verification reads `get_test_run` (roster == scope,
  partition == report statistics under the mapping) and
  `executed_coverage`; resume mode records into the existing run,
  never a second one. `qa-manual-results`: step 2 reads the run
  (`get_test_run` / `case_execution_history`) instead of notes; step 4
  records `source: manual` with the tester as principal,
  `reopen_test_run` if needed, `close_test_run` when fully ingested.
- `qa-run-analyzer` §4: 🔴 no run for a pass that produced verdicts;
  🔴 partition mismatch; 🔴 machine `fail` outside the narrow
  exception; 🟡 SPEC-DEFECT as `known_defect` / human row as machine;
  🟡 stale run with `not_run` rows and no manual-results file.

**Retraction target rule — the one exception to the archive target
rule.** 🔴 [Pipeline] #2 on EP-56133 retest 3: three cases published as
FAIL CONFIRMED in comments on **EP-56109** (2026-08-12) passed on the
EP-56133 retest, and 0.26.0's "no walk-up" rule left the correction
with nowhere to land — a reader of EP-56109 kept seeing three confirmed
failures that were fixed. Now: **a retraction is posted where the
verdict it retracts was published**, whatever ticket that is — ≤ 6
lines (run id, `<case> — <old> → <new>`, reason, where the new verdict
was established), no dumps. It is a correction, not an archive; the
archive target rule stands for everything else. Stage 10's
reconciliation therefore records, per RETRACTS row, where the old
verdict was published (`output-template.md` gains a "Where published"
column; the retest-scope file carries the ticket + comment id).

**The open-items ledger — memory across rounds.** EP-56197 round 3 said
"carried a third round, still open" four times (RISK-CR-1/2/3, six
uncovered EP-56287 behaviours); EP-53978 pass 5 spent its whole scope
file reconstructing what passes 1–4 left undecided. Nothing remembered
an open item except that round's git-ignored run report. New shared
reference `qa-pipeline/references/open-items-ledger.md` →
`<KEY>-open-items.md`, per ticket, no round suffix. The analyzer writes
it (every 🔴/🟡 the run did not settle; new §8 "Carried items", 🔴 for
any row two or more rounds old with no decision); `qa-pipeline-code`
step 0 reads it in retest / bug-fix / resume mode and puts the open rows
in the scope confirmation; `qa-manual-runsheet` records its `[core]`
nominations there (EP-56133 r3 🟡 #6 — the nomination now survives to
the next round); **`qa-manual-results` is the only stage that closes a
row** and lists the still-open ones under "Carried forward" at the end
of the human summary. Archived with the reports where a QA sub-task
exists. MAINTAINERS step 1 names it as the machine-readable input to
"consume the last run's findings first".

Also: `README.md` stage-10 paragraph and a "Memory across rounds"
paragraph; `data-locations.md` (runs as the verdict store, ledger in the
working directory, retraction exception); `MAINTAINERS.md` where-to-look
rows; `.gitattributes` (`* text=auto eol=lf`) — five skill files had been
rewritten CRLF with zero content change and the whole-file diffs hid
everything; `.gitignore` `_*` replaces the per-name `_s9_*` / `_ep53978_*`
patterns (an `_mw_login.js` had already escaped them).

Not done in this release, still open from the two run reports, each
tracked in the review file `PIPELINE-REVIEW-2026-09-07.md`:
`reconcile_counts.py` still harvests statuses from the "Not executed
here" table and cannot find a retest round's case file (EP-56133 r3
🟡 #5); `playwright-executor.md` still instructs a screenshot path the
sandboxed backend cannot write (EP-56197 r3); `code-review`'s
"never read the base branch" rule contradicts the `master` check that
produced that run's top 🔴. Planned for 0.30.1.

No skill frontmatter description changed, so `evals/triggering.md` needs
no re-walk. `reconcile_counts.py` untouched — self-test still passes.

## 0.29.0 — 2026-09-07

**The gate covered every surface except the one that publishes.** 0.28.0
made "no defect without a quoted clause" binding on stage reports, bug
drafts, run-sheet rows and chat. It said nothing about the step where a
report is compressed into an outgoing Jira comment — and compression is
what drops labels.

On EP-56197 (round 3) the web-testing report recorded four readings as
`OBSERVATION (no source checked)` and stated "not a new defect", because
the DS contract says so in terms: *"`items` is the ranked set and can be
longer than `total` — `total` counts matches, while `items` also carries
the semantic tail marked with `item_weak`."* The drafted Jira comment
then presented those same readings as a table with a **"True matches"**
column under **"Still broken — the number is wrong in both directions"**.
Numbers correct, labels gone, one confirmation away from a developer's
ticket. The tester caught it by asking which document required the
rendered count to equal the match count. None did. One of five rows
survived the check.

- **New: `sources-of-record.md` § 7 — the publication gate.** Line by
  line on the drafted comment: register row + verbatim clause, or the
  `OBSERVATION (no source checked)` label and a question, or cut. A
  correctly labelled observation may not reappear as a defect — not as a
  bullet under a "not fixed" heading, not as a row in a failure table,
  and **not under a column header that implies a requirement** ("true
  matches", "expected"): a column asserts as loudly as a sentence.
  Sourced defects and unsourced observations get separate headings. A
  defect owned by another ticket names that key on its line. Final check:
  read it as the assignee — would a line send a developer hunting a bug
  no document requires them to fix?
- `qa-pipeline-code` step 6: the gate runs on the wave-1 comment BEFORE
  the confirmation preview, alongside the existing count gate.
- `qa-manual-results` step 4: the gate runs on the human summary, which
  is the first and often only thing a person reads; retractions are held
  to the same standard.
- **Shipped at last: `reconcile_counts.py` recognises flat `TC-<n>` ids.**
  The fix was written after EP-56289 and never committed, so no installed
  copy had it: bug-fix and standalone-Bug runs number their cases
  `TC-1..TC-N`, the pattern matched only `TC-REQ-*`, and the script
  printed `0 distinct case ids · no status rows` while the self-test
  passed — a silently absent count gate on exactly the runs that have no
  suite and no Jira archive to fall back on. Third consecutive run
  (EP-56197 rounds 1-3) reconciled by hand because of it. A flat range
  needs `TC-` on both sides; a bare number after a dash stays prose.
- `.gitignore`: stage-9 scratch patterns (`_s9_*`, `_ep53978_*`),
  `__pycache__/`, and the `_to_delete/` quarantine folder — the first two
  carry live credentials.

## 0.28.0 — 2026-09-07

**The code phase read no source of record at all.** Zero Confluence
references across `qa-pipeline-code`, `code-review`, `api-testing` and
`web-testing`. Only `task-context` (stage 1) fetched the acceptance
criteria — and stage 1 does not run in retest or bug-fix mode, which is
most code-phase runs. So those runs judged the product against
test-case text written days earlier by another phase, and nothing
upstream of bug-drafting ever opened a spec.

Found on **EP-56133** retest 3, where the run produced three
"findings" that were not defects. One — *"a matching Group renders
nowhere on the Global Search results page"* — reached the point of
being drafted as a Bug, with a closed ticket cited as precedent. The
as-built front-end documentation (Confluence FRON 1885732888) names
`groups` as its own example of a type the front end **deliberately does
not render**. The observation was true; the defect claim was false. The
tester caught it by asking "are you sure these are issues? can you
check AC?" — the pipeline had no gate that would have.

Two structural holes, not one lapse:

1. **No register.** Nothing collected the governing documents, so
   nothing could be checked against them.
2. **Only briefs were ever in scope.** Briefs say what should exist.
   **As-built documents say what deliberately does not** — and that is
   the document class that defeats a false defect. The EP-56133 suite
   summary even cited the as-built page by id; no stage opened it.

And the existing source gate fired last, after a finding had already
been written into a report, a chat summary and a run sheet as settled.

- **New shared reference `qa-pipeline/references/sources-of-record.md`**
  — the four source kinds in precedence order (product brief → as-built
  doc → implementing sub-task's AC → the ticket under test), the
  register format, the gate, and what is explicitly *not* a source: a
  test case, a suite requirement, an earlier run's verdict, a
  developer's comment about intent, a closed precedent ticket.
- **`qa-pipeline-code` step 0 builds the register in EVERY mode**, and
  writes `<KEY>-sources.md`. Fetching the as-built document is not
  optional; absent one, the row is recorded `NONE FOUND` and flagged in
  the run report. Four documented ways to find it, since it is rarely
  linked from the ticket. The same-session shortcut no longer skips it —
  test cases are derived artifacts and never substitute for a source.
- **The gate moved upstream.** Every FAIL, FAIL CONFIRMED and
  `RISK-CR-*` row in `code-review`, `api-testing` and `web-testing` now
  carries `Source:` (register row) + `Clause:` (the verbatim sentence
  the build contradicts). Risk rows are covered too — a risk is a claim
  about the product like any other. Previously only FAIL-bound and
  High-risk *test cases* were checked, and only for their own wording.
- **New status `OBSERVATION (no source checked)`** (CR/API/WEB) — a real
  thing seen with no clause saying it is wrong. Honest output, often
  worth fixing, and barred from every defect list, from
  `/knowledge-base` and from `createJiraIssue`. Phrased as a question,
  never a verdict. Three of the four EP-56133 findings were this.
- **Chat is a publication surface.** The orchestrator's "never asserts a
  product claim" rule now says so explicitly: findings stated to the
  user carry their `Source:`/`Clause:`, and unsourced observations
  carry their label. Listing them in one numbered run beside verified
  failures grants equal authority — on EP-56133 the reports labelled
  all three correctly and the chat summary was what lost the labels.
- **A closed ticket is not a source.** EP-55923 ("Round tables results
  are found and permitted but never render", COMPLETE) was cited as
  precedent for the Groups finding. It failed: Round Tables *is* one of
  the 12 entities the as-built doc lists, so that was a real defect;
  Groups is not, so the precedent did not transfer.
- **`qa-run-analyzer` §7 checks the register** — 🔴 no register, 🔴 no
  as-built row, 🔴 any defect row missing its `Source:`/`Clause:`,
  🟡 an unsourced observation presented as a defect, 🟡 a defect resting
  on a precedent ticket instead of a clause.

No skill frontmatter description changed, so `evals/triggering.md` needs
no re-walk.

## 0.27.0 — 2026-09-03

**The count gate now works in bug-fix mode.** `reconcile_counts.py`
recognised only `TC-REQ-N.M` ids, but bug-fix mode and standalone-Bug
runs number their derived cases `TC-1..TC-N` — they have no
requirements file to group them under. So every such run printed
`test-cases: 0 distinct case ids · no status rows` while `--selftest`
kept passing, and the count gate was silently absent.

Worst where it mattered most: those are exactly the runs with no QA
sub-task and therefore (since 0.26.0's archive target rule) no Jira
archive and usually no QA Service suite — the local files are the only
record, and nothing was checking that they agreed. Found on EP-56289,
where the counts had to be reconciled by hand.

- `CASE_ID` accepts flat `TC-<n>` / `TC-<n>a` alongside `TC-REQ-*` and
  `RISK-<TAG>-<n>`. The `TC-REQ-` alternative stays first; the shapes
  cannot cross-match.
- New `FLAT_RANGE` expands flat spans (`TC-1..TC-7`, `TC-1–TC-7`).
  Both sides must carry the `TC-` prefix, the same guard `ID_RANGE`
  already applies to dotted ranges — a bare number after a dash is
  prose, and that trap once invented 26 phantom ids.
- `CORE_MARK` accepts `## ` as well as `### `, and both id shapes.
- `--selftest` now runs TWO fixtures — the existing docs-phase
  regression document and a new bug-fix-mode one covering flat ids,
  flat spans, `## ` headings, statistics-table exclusion and the
  phantom-range guard. A single-fixture self-test is what let this
  survive: it passed on every release while a whole run shape parsed
  as empty.

**status-vocabulary.md: flat ids declared, and decorated status cells
called out.** The vocabulary's "Row identifiers" line named only
`TC-REQ-N.M` and `RISK-<TAG>-<n>`, so bug-fix mode's ids were
undeclared in the one file that is supposed to be their single home.
Added — together with an explicit rule that a status cell carries a
status and nothing else: `QA → stage 7`, `PASS (not reachable)` and
`NOT EXECUTED HERE — orchestrator` all parse as NO status and drop the
row out of the counts silently. Routing and qualifiers belong in the
Comment column, and a case another stage owns is recorded the way the
routing invariant already prescribes.

## 0.26.0 — 2026-08-28

**Archive target rule: the results archive goes to the QA sub-task and
nowhere else.** A Story face, a Bug or a Defect now receives exactly two
comments across a whole run — the wave-1 status line and the wave-2
human summary — and no fenced file dumps at all.

Why: step 6 had a "No QA sub-task → post the wave-1 comments to the MAIN
issue" fallback, and three to five comments of unreadable archive walls
landed on tickets developers and PMs read daily. It was worst exactly
where it was least noticed: a **Defect is itself a sub-task and can
never own a QA sub-task**, so every bug-fix run dumped onto the ticket
face by construction. Observed on EP-56380 — three archive comments on
the Defect, while `PRIVFAV-98` in the QA Service suite already held the
full run record.

A QA sub-task is a machine artefact ticket that nobody reads for status,
so the archive keeps its home there, and cross-machine resume keeps
working for the Story runs where resume actually matters.

Explicitly NOT done: no walk-up to the parent story's QA sub-task for a
Bug or Defect. One ticket's run does not belong in another ticket's
archive, and a resume looking for `<BUG>-code-review.md` should not find
it filed under a story.

The cost where no archive is posted, guarded rather than hidden:

- `qa-pipeline-code` step 0 resume mode now has an explicit order —
  working directory, then the archive comment on the QA sub-task when
  one exists, then **PAUSE**. It says plainly that tickets without a QA
  sub-task carry no archive by design and asks whether this is the
  machine the earlier run used. A missing file must not be read as
  "that stage never ran": on another machine it means "cannot see it
  from here", and silently re-running a 45-minute browser stage is
  exactly the waste this prevents.
- Split Claude Code ↔ Cowork runs: with a QA sub-task the partial
  archive bridges the environments as before; **without one they must
  see the same working directory.** Stated up front instead of
  discovered at step 0.
- Post-publish verification now checks the archive is on the sub-task
  where one exists, treats an archive found on a Story face / Bug /
  Defect as a ❌, and checks every stage report is on disk.

**New: `qa-pipeline/references/data-locations.md`** — one home for a
fact eleven skills each stated differently, and six stated wrongly. It
gives the three stores (working directory / QA Service suite / Jira),
one resolution order for any input file, and two named failure modes:
never read a missing file as "that stage never ran" (on another machine
it means "cannot see it from here"), and never read file existence as
stage completion. It also corrects a wrong instruction that was in six
skills — *"if the chat is new, the user uploads the file"*. The folder
is mounted and every previous run's files are still in it: **a new chat
is not a reason to ask for an upload.** Wired into requirements-grooming,
qa-checklist, qa-test-cases, code-review, api-testing, web-testing,
qa-run-analyzer, qa-manual-runsheet, qa-manual-results, qa-pipeline,
qa-pipeline-docs and qa-pipeline-code.

Changed: `qa-pipeline-code/SKILL.md` (wave 1, comment-1 bullet, confirm
pause, main-issue fallback, bug-fix mode, resume mode, split runs,
post-publish verification, final response), `qa-manual-results/SKILL.md`
(input source, step 4), `qa-pipeline/SKILL.md` (state detection no
longer infers "did not run" from a missing archive),
`qa-pipeline-code/references/results-comment-template.md` (archive
target rule + table, Comment 1 scoped to QA sub-tasks).

Unchanged on purpose: the **docs-phase** archive (`qa-pipeline-docs`
step 6). It already self-suppresses when a suite exists, and when it
does post it lands on a QA sub-task — which is exactly where this rule
says an archive belongs.

## 0.25.3 — 2026-08-20

QA Service folders enforced (`qa-service-publish.md`). The folder rule
existed but real suites still landed in "General"; it is now a gated
part of the publish, not a preference:
- `folderName` targets **~5–8 cases per functionality folder** — split
  big REQ groups into sub-aspect folders, merge tiny ones; any case in
  "General" or a folder over ~10 cases is a mapping failure to fix
  before writing.
- The publish preview states the folder plan (folder → case count);
  step-5 verification checks the distribution and repairs in place
  (`create_test_case_folder` + `move_test_case`).
- Appending reuses the suite's existing folders; a legacy all-General
  suite gets a reorganization offer in the preview — new cases never
  join the pile.

## 0.25.2 — 2026-08-19

Windows long-path gotcha recorded in `bitbucket-access.md`:
`portal-ui`/`admin-ui` checkouts fail half-done on the 260-char limit
(hit live during first clone setup) — `git config --global
core.longpaths true` before cloning; recover with
`git restore --source=HEAD :/`.

## 0.25.1 — 2026-08-19

Local clones, and three measured corrections to `bitbucket-access.md`
(each verified against Bitbucket Cloud on 2026-08-19; each would cost
a failed run): git username for HTTPS is `x-token-auth`, not
`$BB_EMAIL` (the email works for REST and silently fails git — the
0.13.2 helper recipe carried the bug; Windows credential-store recipe
added); the token now has `read:pullrequest` (the 403 claim was
stale; branch mode stays default); base branches are per repo —
`expoplatform-main-ira` → **alpha**, `portal-ui`/`admin-ui` → master
(diffing the monolith against master produced wrong diffs).

New "Local clone — preferred when present" section: blobless clone
(shallow cannot diff branch bases), what a clone enables in stages
5–6 (callers of changed methods, does-a-test-already-exist, shared
helpers — file+line evidence, head-branch-only review rule intact),
the workspace test-repo map, and the caution that `playwright-tests`
/ `qa-tests` carry a committed `.env`. The docs-phase recon (0.21.0)
may read the clone as an observation source — a constant or threshold
is a current-behaviour fact, cited file+line. `.gitignore`: `GS-*`
run artifacts covered by broad rule.

## 0.25.0 — 2026-08-14

Run clock. Both orchestrators now show progress and time remaining
while a run is in flight: a wall-clock stamp at start and at every
stage boundary, one fixed-format line per boundary —
`⏱ Stage n/N done — <name> · elapsed E min · ~R min left`.

- Per-stage minute budgets seeded from observed run durations (docs
  ≈ 56 min total, code ≈ 2–3 h); the remaining estimate self-corrects
  by the run's own pace (elapsed ÷ finished budgets, clamped 0.5–3),
  rounded to 5 minutes.
- User-waiting pauses (publish confirmation, browser login, Jira
  write confirmation, test-event authorisation) are stamped on both
  ends and excluded — waiting is not pace. Retest / bug-fix runs
  halve the scoped-down stages' budgets. No shell → the clock is
  skipped silently.
- No frontmatter descriptions changed — triggering evals untouched.

## 0.24.0 — 2026-08-14

Jira writing style — one home. Real bug drafts (EP-47678) kept the
skeleton but ballooned inside it: ad-hoc h3 sections ("Secondary
defect", "Note for triage"), code-path dumps inside Actual result,
paragraph-long field cells. The voice rules also lived buried in
results-comment-template.md and were inherited only by pointer.

- **New `qa-pipeline-code/references/jira-writing-style.md`** — the
  single home for every human-facing Jira text the pipeline writes
  (bug descriptions, human summary, story notes, grooming questions,
  stage-10 write-backs; machine archives exempt). Voice rules moved
  there verbatim, plus hard caps: bug summary ≤ 120 chars; ≤ 8 repro
  steps; Actual result ≤ 5 observed lines with code paths relegated
  to Source (≤ 2 lines); one-line field cells; ≤ 4-line comment
  paragraphs; the h3 skeleton is CLOSED (no ad-hoc sections — a
  second defect is a second draft); a pre-post self-check.
- **bug-report-template.md** and **results-comment-template.md** now
  point at it (the voice list is no longer duplicated);
  **qa-pipeline-docs** grooming-questions comment points at it
  directly. Stage 10 inherits via the two templates it already uses.
- **qa-pipeline-code retest mode** (recovered from an earlier
  uncommitted edit): the retest scope is built from the QA Service
  SUITE, not the local test-cases file — `get_suite` first, diff
  against the file, suite-only requirements/cases are in scope by
  default and listed with an explicit in/out decision in
  `<STORY>-retest-scope.md`. Real run: the suite had gained a P0
  requirement and two P0 cases from a PM comment after the baseline;
  a file-derived scope missed both. No suite/connector → the run
  report says the scope could not be reconciled.
- No frontmatter descriptions changed — triggering evals untouched.

## 0.23.0 — 2026-08-14

Two-tier coverage: machine-depth generation, human-core selection
(design: `SPEC-two-tier-coverage.md`). One corpus, two views — never
two authored case sets (stage 10 joins human to machine verdicts by
TC ID, so the human set is a selection, not a rewrite).

- **qa-test-cases**: coverage depth is now risk-scaled instead of one
  flat Standard — High-risk requirements get extended techniques
  (3-value BVA, invalid state transitions, collapsed Decision Table,
  2-wise pairwise), Medium keeps the old Standard, Low shrinks to
  happy path + explicitly stated constraints. Exactly one case per
  behavioural REQ is marked ` [core]` on its heading (preference:
  riskiest invalid partition → conflict version-A → boundary → happy
  path). Statistics gains a mechanical `Core cases:` line;
  verification enforces one-core-per-REQ and High-risk technique
  depth (or a stated reason). Grounding rule, EP dedup and the
  no-exhaustive-pairwise rule unchanged at every depth.
- **qa-manual-runsheet** step 2a: the coverage gate tightens — every
  behavioural REQ needs a WALKED row; a machine verdict alone no
  longer covers a REQ. The `[core]` case is the default
  representative, entering short-form (VERIFY-style) where
  machine-settled at Low/Medium risk; older suites without markers
  fall back to technique-picked representatives, stated in the
  Reference tab. Coverage map may not show machine-only behavioural
  REQ lines.
- **qa-run-analyzer**: 🔴 zero/multiple `[core]` cases on a
  behavioural REQ; 🔴 runsheet coverage map with a machine-only
  behavioural REQ line; 🟡 High-risk REQ group naming no extended
  technique and no reason. `reconcile_counts.py` counts `[core]`
  headings on the test-cases file (`core=N`; selftest extended and
  passing).
- **qa-pipeline-docs**: tracker-comment case lines carry the
  ` [core]` marker; the count gate also reconciles core count =
  behavioural REQs. `qa-service-publish.md`: core cases publish
  `detail.core: yes` and propose a `core` tag in the tagging step.
- Fixture `EP-0000-context.md` expectations updated (core marker +
  statistics line). No frontmatter `description` changed — triggering
  evals untouched.

## 0.22.0 — 2026-08-13

`qa-pipeline` — the front door. A 14th, deliberately thin skill: give
it any ticket ("qa this ticket EP-1234") and it reads the state
(issuetype; pipeline QA sub-task; suite line; code-phase comments;
manual-results comment; local run artifacts), proposes the route with
one line of evidence per signal, and invokes it on confirmation:
fresh Story/Task → docs phase (code phase handed off as a fresh-chat
command); standalone Bug → bug-fix mode; docs published → code phase;
❌ + fix landed → retest; run sheet back → qa-manual-results.
Contains no testing logic; read-only until the user confirms;
conflicting signals are presented, never guessed. Direct invocation
of every orchestrator and mode is unchanged. README, MAINTAINERS
tree, and triggering evals updated.

## 0.21.0 — 2026-08-13

Recon: the docs phase now answers its own "how does the app work
today?" questions instead of posting them to a human. Formalises what
the owner improvised on EP-55889 (that run's hand-made recon file
dropped open questions to 1, vs 4–5 on comparable runs, and caught a
one-row-per-participant surprise no document mentioned).

- **Grooming classifies every open item** SPEC (intent — a human
  decision) or BEHAVIOUR (observable fact), and consumes an existing
  `<KEY>-recon.md` before raising BEHAVIOUR questions.
- **`qa-pipeline-docs` recon step** (default when env access exists,
  before the questions post): read-only observation of the running
  system into `<KEY>-recon.md`, opening with the fixed epistemic
  header — current behaviour, not requirements; divergence from AC
  stays a question; every observation evidenced; recon facts ground
  expected results only where the requirement references current
  behaviour. Only SPEC + unresolved BEHAVIOUR items reach the ticket.
- **Analyzer**: reads `<KEY>-recon.md`; 🟡 when an observable question
  was posted to a human despite available env access; 🔴 when a recon
  answer changed a case's premise without the requirement updating.

## 0.20.1 — 2026-08-13

Bug-fix mode. `qa-pipeline-code` step 0's dead end ("re-run
qa-pipeline-docs") gets a third option for standalone Bug tickets:
derive 2–4 mini cases from the bug ticket itself — the repro steps
with the fixed behaviour as the expected result (quoting the ticket:
the source-of-record rule applies), a negative sibling, and one
regression case per behaviour the fix PR touches. Written as a normal
test-cases file, so stages 5–8, all gates, the routing invariant and
the two-wave publish run unchanged; results post to the Bug ticket
(no sub-task, no suite); stage 9 shrinks to a handful of rows or the
user verifies directly and stage 10 ingests the one-line verdict.
Triggers: "test the bugfix EP-1234", or step-0 detection (issuetype
Bug, no QA sub-task, no suite → ask). Description + triggering evals
updated.

## 0.20.0 — 2026-08-13

The consolidation release — subtractive, as three reviews demanded.
Full cut ledger: `CONSOLIDATION-2026-08-13.md` (every deleted rule
with its class and new home). 2657 → 2319 lines across eight files
(−12.7%); web-testing 539→354 and qa-pipeline-code 540→451, both back
under the 500-line bar. Zero behaviour change; zero incident-backed
rules weakened; all frontmatter descriptions byte-identical.

- **Routing invariant homed** in `status-vocabulary.md`: the channel
  tag is advisory; web-testing's scope = every QA/FAIL case no earlier
  stage conclusively executed at runtime, plus routed-in and
  spot-check rows. The four recorded forms (tag, dual tag,
  RE-ROUTE [UI], Route-to-web-testing) keep their names for templates
  and the counting script; their scattered rules collapse into
  pointers.
- **Single homes extended:** env-credential search order lives only in
  api-testing-reference §0; "if you write the doubt, you must classify
  it" lives in status-vocabulary; duplicates elsewhere became
  pointers. Cut ledger: 10 duplicates, 6 judgment-restating, 5 merged
  into the invariant, 1 superseded.
- **One substantive fix:** qa-pipeline-code's Final response still
  claimed both comments (archive + human summary) were posted —
  contradicting 0.19.0's two-wave rule. Now wave-1-only.
- **Deleted:** orphaned `references/progress-protocol.md` (artifact of
  retro proposal B, rejected in 0.19.0, referenced by nothing).
- Deferred to a possible second pass: references/ dedup (~2,500 lines
  of potential), and the structural cuts that change behaviour
  (checklist folding, transport fallback, vocabulary collapse) stay
  deferred with their recorded reasons.

## 0.19.4 — 2026-08-13

Two items from the `claude doctor` run.

- **notify hook works on Windows**: `hooks/hooks.json` now falls back
  `python3` → `python` → `py -3` → silent exit. The hook had failed
  (non-blocking) on every session because Windows ships the `py`
  launcher, not `python3`. Still opt-in via `QA_PIPELINE_NOTIFY=1`.
- **`CLAUDE.md` added** (the G1 gap from the verification-loops check,
  written per the context-engineering guidance: gotchas only, no
  duplication): hard rules (no `git add -A`, no shell-mount writes,
  broad ignore patterns, credential handling), the four verify
  commands, and the change discipline — auto-loaded into every Claude
  Code session in this repo instead of waiting for someone to open
  MAINTAINERS.md.

## 0.19.3 — 2026-08-13

Voice block completed with action-shape rules (from the i-have-adhd
skill's approach): reader-actionable content is a numbered list, lists
cap at 5 items, and a comment that asks for something ends on the one
concrete next step. Applies to all human-facing Jira text via
`results-comment-template.md` → "Writing rules".

## 0.19.2 — 2026-08-13

Minimal manual set (un-defers the stage-9 minimisation from 0.19.0 —
two runs showed it as the biggest human-time saving: 32→14 rows on
EP-53768, 33→8 on EP-53767). The machine still runs every case and the
QA Service suite still stores every case; only the human's sheet
shrinks. Stage 9 now selects rows by test-design technique — one
representative per equivalence class, boundaries only where the
boundary matters, pairwise over full sweeps, shared-fixture walks
merged into one row with a `Covers:` list — under a hard floor: every
behavioural REQ is covered by a walked row or a runtime-verified
machine verdict (code reading doesn't count), with the REQ→row
coverage map printed on the Reference tab. High-risk blast-radius
cases and ⚠ SPECIAL ATTENTION items are added back on top. Unselected
cases are named as delegated, and stage 10 expands `Covers` lists on
ingestion (a note naming one case overrides for that case).

## 0.19.1 — 2026-08-13

Voice rules for human-facing Jira text. Machine artifacts stay as they
are (agents read those); everything a person reads now follows a short
anti-slop voice block in `results-comment-template.md` → "Writing
rules": point first, no filler phrases, no fake-insight structures, no
bold-term-colon lists, no wrap-up endings, varied sentence length, one
em dash max. Bug drafts and the grooming open-questions comment point
at the same block, so the voice lives in one place.

## 0.19.0 — 2026-08-13

The mileage release. Five real runs (EP-47675, EP-47678, EP-53767,
EP-53768, EP-55706) produced five retrospectives and two proposal files
(`ep-qa-pipeline-proposed-edits*.md`, sections A–G) — now tracked in
git alongside this entry. Triage per the MAINTAINERS loop rule:

**ACCEPTED — E (source fidelity, docs phase):** grooming may not merge
sources that differ in scope (split + spec-of-record ranking, E1);
"a requirement may cite only sources that support all of it" hard check
(E2); per-clause `source` attribution in qa-service-publish (E3) and
the grooming output template (E4); joint-satisfiability check against
the established suite (E5). Root cause: EP-55706 published a
requirement whose second clause existed in no acceptance criteria.

**ACCEPTED — F (source fidelity, code phase):** code-review verifies
FAIL-bound and High-risk cases against the actual source of record —
a deliberate, bounded read-only exception to "never touch the tracker"
(F1); "if you write the doubt, you must classify it" → SPEC-DEFECT in
web- and api-testing (F2 — zero cost; alone would have prevented
EP-56188); source gate quoting the violated AC sentence before any bug
draft (F3); "Unverified defect claims" heading (F4); analyzer dimension
7 "Source fidelity — is the premise true, not just consistent?" (F5).

**ACCEPTED — G (two-wave publish; raised by the owner):** step 6 posts
only the machine archive + a no-verdict status comment; the human
summary, story notes, bug filings, reassignment and decision requests
all move to stage 10, on human-confirmed verdicts. Narrow wave-1
exception: runtime-confirmed + evidenced + blocking the manual round.
Evidence: EP-55706's PROVISIONAL label prevented nothing — a mis-typed
bug, three already-answered "product decisions", two retractions in
24h. Note: the archive still publishes pre-verification — accepted, it
is agent-facing and resume depends on it. The PROVISIONAL status line
becomes wave-2 VERIFIED / PARTIALLY VERIFIED.

**ACCEPTED — cross-run items (2–3 runs each):** a code-read-only
negative verdict is a CLAIM, not a verdict — never publishable settled,
never files a bug (6 of 12 wrong on EP-53768; mirror of the 0.17.0
PASS rule). `reconcile_counts.py`: ID_RANGE no longer treats
"TC-REQ-20.1 — 30 characters" as a range (26 phantom ids on
EP-53767) and CASE_ID accepts letter suffixes (12a.1/12b.1 no longer
collapse) — both now covered by the self-test. Jira archive fidelity:
dynamic fence lengths + mandatory read-back comparison (two corrupted
archives). Provisioning: snapshot-before-collection-write with
verified restore + restore recipe written before the first mutation
(930 wiped permission pairs), reachability probe before
bulk-provisioning, positive fixture claims verified like blockers.
Web-testing: second observation before FAILing shared page elements
(16 of 17 stage-8 errors on EP-47675 were single-observation false
alarms) and negative verdicts must carry their `Control:` line.
Orchestrator never asserts product claims from its own observation
(dominant error source on EP-53767). Confirmed-bug lines carry an
evidence class (reproduced-with-control / observed-once / code-read).
`.gitignore`: retro/proposal docs explicitly un-ignored (Windows git
matches `EP-*` case-insensitively).

**REJECTED — A–D (EP-47675 proposals), reasons on record:** D3/F3/G2
rewrite the same step-7 anchor in incompatible directions — G wins
(file after the human round). D1's CANDIDATE-DEFECT vocabulary rewrite
collides with F2/F5 and expands a vocabulary two other retros say is
already too wide; its intent (human confirms every bug, one at a time)
is delivered by G2+F3. A's walk-sheet-at-stage-5.5 is internally
contradictory (forbids and requires priority sort), needs machine
facts that do not exist at 5.5 (CORE = "only evidence is code
reading"), fights three later findings (fixtures must provision AFTER
stage 8), and adds parallel record surfaces against the one-record
stance. B (progress heartbeats) is process noise for a solo operator.
C is cosmetics or already implemented (C7 = post-publish verification).

**DEFERRED (single-run suggestions, wait for recurrence):** Depends-on
column with auto re-derivation; 3-field verdict split; version-sibling
both-failed detector; stage-10 write-back batching doc; machine-verdict
column immutability; reachability-caveat lint; verbatim-quote rule
before SPEC-DEFECT proposals; blocked-vs-fixture diff re-dispatch;
design-comment exclusion; browser-exclusivity void-and-rerun;
text-evidence-only tagging; published-summary contradiction re-read;
per-status id lists over regex; stage-9 test-design minimisation;
machine re-execution of unblocked rows; closed-ticket dedup search;
guest-vs-signed-in authority; copy-only deviations as discrepancy.

## 0.18.3 — 2026-07-31

Retest mode made clean. The 0.18.0 retest paragraph half-existed: it
was triggered by inference only ("the user says the fix has landed"),
its scope stopped at stage 8 — so stage 9 would rebuild all rows and
re-provision the full fixture set on every retest — and
`qa-manual-runsheet` had no retest concept at all. Found while
planning the first real retest of EP-53978; the magic-phrase
dependency is exactly the failure pattern the earlier reviews flagged.

- **`qa-pipeline-code` retest mode rewritten:** explicit triggers
  ("retest <KEY>", "the fix landed" — now also in the description) AND
  self-detection (❌ newest summary / RETEST lines in the suite →
  ask "full run or retest?"). Scope is three tiers, confirmed by the
  user before stage 5: (1) the defects' own cases, (2) blast radius —
  REQ siblings + cases sharing the fixed code path + confirmed
  RISK rows, (3) everything that never got a real verdict. The scope
  now binds ALL stages including stage 9.
- **`qa-manual-runsheet` — "Retest runs: detect, don't assume":**
  prior-run artifacts (testdata.json, runsheet, RETEST suite lines,
  manual-results comment) → pause and ask, never a silent full
  rebuild. On retest: rows for the scoped cases only; fixtures fresh
  by default — prior fixtures are presumed contaminated for any
  counter/analytics assertion (a real run left a phantom like and a
  counter stuck at 15); reuse only stateless accounts after re-proving
  login; abandoned-as-contaminated fixtures listed for cleanup.
- `evals/triggering.md`: retest queries route to the orchestrator, not
  the bare runsheet stage.

## 0.18.2 — 2026-07-30

Net-new items from `GUIDE-ALIGNMENT-AUDIT-2026-07-30.md` (cold audit
against the author-supplied "Complete Guide to Building Skills for
Claude" PDF; ~70% of the guide overlapped ground already settled by
the 0.18.1 audit).

- **`->` removed from frontmatter descriptions** (both orchestrators)
  — the guide bans angle-bracket characters in frontmatter as an
  upload-validator/security rule; stage chains now read "…, then …".
- **Negative triggers** added to the four skills whose trigger phrases
  are generic (task-context, qa-checklist, pr-summary, code-review):
  each description now carries a "Do NOT use for…" clause so
  co-installed skills can't capture (or lose) these requests.
- **`evals/triggering.md`** — should-fire / must-not-fire query list
  for all 13 skills; MAINTAINERS recipe step 4 now requires walking it
  after any description edit. This is the free tier of the deferred
  eval-set work; the functional tier still lands with the mileage
  phase.
- Recorded from the audit's contradiction analysis: official doc wins
  on frontmatter fields (name+description only — already compliant)
  and on the <500-line SKILL.md bar (web-testing is at 519 — one more
  input to the planned consolidation release); the PDF's
  "rigor scales with audience" stance is the recorded justification
  for deferring functional eval sets while the plugin has one user.

## 0.18.1 — 2026-07-30

Skill-authoring compliance (items 1–4 of
`SKILL-BEST-PRACTICES-AUDIT-2026-07-30.md`, a cold audit against
Anthropic's official skill best-practices doc).

- **Broken cross-skill paths fixed** in `qa-pipeline-code/SKILL.md`:
  three `qa-pipeline-docs/references/…` references lacked the `../`
  prefix — in the publish/write-back/transition steps of all places.
- **Discovery misroutes fixed:** web-testing's description no longer
  claims the "manual testing" trigger (that request belongs to stages
  9/10 and now says so); qa-manual-runsheet's description no longer
  calls itself "Stage 4.5" — it is stage 9, run at the END of the code
  phase, and the description now matches the orchestrator (and
  mentions the VERIFY spot-check rows and stage 10).
- **MCP tool names disambiguated:** the five skills that call
  connector tools (task-context, qa-pipeline-docs, qa-pipeline-code,
  qa-run-analyzer, qa-manual-results) now open with a one-line mapping
  note — bare Jira/Confluence names = Atlassian MCP connector,
  suite/case tools = QA Service MCP connector; prefixes vary per
  install, match by tool name.
- **Contents lines added to all 13 reference files over 100 lines**
  (qa-service-publish, api-testing-reference, browser-rules,
  results-comment-template, runsheet-format, checklist-design-rules,
  provisioning-rules, bitbucket-access, absence-check-protocol, both
  output templates, both design-rules/example files) — so a partial
  reader knows what exists before deciding what to skip. On the two
  report templates the line is marked "do NOT reproduce in the
  report".

Not done (recorded): audit item 5 — no per-skill evaluation sets yet.
The `fixtures/EP-0000` smoke test covers the docs stages; building
eval scenarios for the code-phase stages is real work and is deferred
to the mileage phase (run real tickets first, turn the failures they
expose into the eval set).

## 0.18.0 — 2026-07-30

The trust-model release. Implements the accepted findings of
`ORCHESTRATOR-DESIGN-REVIEW-2026-07-30.md` (a cold design review of
both orchestrators against the creator's intent: human is the final
arbiter, AI verdicts are provisional by architecture) plus the last
quick items from the first review.

**W1 — the handback waits for the human.** Step 8 no longer posts
"QA passed" / applies the "QA done" transition on automated verdicts;
both move to `qa-manual-results` step 4b (new), after the manual round.
An explicit early note is titled "Automated QA passed — manual
verification pending", with no transition.

**W2 — VERIFY (spot-check) runsheet rows.** ALREADY SETTLED is now
reserved for runtime-verified Low/Medium PASSes; machine PASSes on
`[risk: High]` requirements and ALL code-reading-only PASSes become
short spot-check rows (runsheet SKILL step 2 + format reference). The
sheet stays lean; the tester's effort lands where the error model says
the lies are.

**W3 — PROVISIONAL is a record property.** The step-6 human summary
carries `Status: PROVISIONAL — manual verification pending (N rows)`;
the manual-results comment supersedes it; the analyzer flags 🟡 when
runsheet outputs exist but manual results were never ingested.

**W4 — grooming questions post at stage 2.** The open-items ticket
comment moves from the publish bundle to immediately after grooming
(one quick yes/no), so the PM clock starts four stages earlier.

**W5 — reverse gap detection.** pr-summary gains a required
"Behaviours touched" inventory (diff-only); code-review gains a
closing "Unmapped changes" step (touched behaviour no case exercises);
the analyzer flags each entry 🟡. Scope creep is now visible.

**W8 — the AC→REQ seam is checked.** Analyzer: every numbered item in
the context file's Requirements sections must map to a REQ-N; an AC
item with no REQ is 🔴. The coverage chain is now anchored at the top.

**W9 — retest mode.** `qa-pipeline-code` step 0: when the newest human
summary is ❌ and the fix landed, scope the run to the failed cases +
their REQ siblings + confirmed risk rows, post as `RETEST:` with
supersede lines, offer bug-closing comments.

**W6(b) — the suite/connector dead end is now a pre-flight check.**
Chosen over always-posting the archive (keeps the 0.11.2 dedup):
MAINTAINERS' environment matrix now lists the QA Service connector per
phase, and step 0's environment check verifies suite-vs-connector-vs-
archive availability up front instead of failing at extraction time.

**W7 — cosmetics on load-bearing files.** Fixed the duplicated line in
qa-pipeline-docs' final response (old truncation damage); "How it
runs" items now carry their stage numbers; the code orchestrator's
title/description say stages 5–10 and mention retest mode. (W10 — the
dual-tag contradiction — was fixed the same day it was found.)

**Status vocabulary home.** New
`qa-run-analyzer/references/status-vocabulary.md` — every status, its
emitting stages, meaning, and evidence requirements in one table; the
three verdict stages, the templates, and `reconcile_counts.py` defer
to it. Zero behaviour change.

**First-review leftovers #11 and #15.** BLOCKED now requires a
recorded `Probe:` in api-testing and web-testing (else
`BLOCKED (unverified)`, analyzer-flagged) — nine wrong blockers across
two runs dissolved on one probe each. The runsheet format's
contradictory muted-palette section is now an explicit "REJECTED — do
not implement" record; the saturated palette (what the generator
implements) is the only spec.

**Recorded rejections and deferrals** (per the MAINTAINERS loop rule):
- First review finding 14's `<KEY>-verdicts.tsv` ledger: REJECTED — it
  would add a fifth verdict surface when the failure mode is too many
  half-authoritative surfaces; ⚠ CURRENT VERDICT + the PROVISIONAL
  marker + the never-ingested check cover the need. Revisit only if
  contradictions still slip through.
- Design review's big consolidations (single routing invariant;
  folding qa-checklist into test-cases) and small-noise deletions:
  DEFERRED deliberately — too much rule-mass changed today already;
  next consolidation pass.
- Finding 13 (freeze-forever experiment outcome) remains a user
  action, not a repo change.
- #17 (settings.local.json wildcards) narrowed manually by the user —
  the file is outside the plugin's editable tree.

## 0.17.0 — 2026-07-30

Completeness, legalised improvisation, and requirements restore
(Findings 8, 9 and 10 of `PIPELINE-REVIEW-2026-07-30.md`).

Finding 8 — a code-review PASS removed a case from all runtime
execution (65% of EP-53978's cases never touched a running system),
and resume treated file-existence as completion:
- **code-review**: PASS only when the expected result is fully
  determined by the code text; runtime observables (counter values,
  absence on a surface, notifications, exports, cache behaviour over
  time) are QA however convincing the code.
- **`Completeness: complete | partial — N of M …` header** required in
  pr-summary, code-review, api-testing and web-testing templates.
- **Resume re-dispatches partial stages**: step 0 reads the header (or
  derives it on older reports) and never inherits "NOT EXECUTED 15" as
  done. The human summary carries "N of M verified by code reading
  only".
- **Analyzer**: 🔴 partial report feeding a final verdict; 🔴 Scope vs
  Statistics disagreement inside one report.

Finding 9 — the run's two best product findings came from stage 7
breaking its contract; the templates and script could not represent
them:
- **Legalised:** executing code-review-PASS cases (Source
  `PASS(code)`), `NOT EXECUTED` (with reason, distinct from BLOCKED),
  and risk-chasing `RISK-CR-<n>` rows for code-review risks with no
  covering case — code-review now emits a numbered "Risks" section for
  them, and step 6 proposes confirmed risk rows as permanent suite
  cases (`qa-service-publish.md`).
- **New `SPEC-DEFECT` status** (code-review, api-testing, web-testing):
  the case/requirement is wrong, not the code — feeds a "Requirements
  to correct" section in the human summary and a `discrepancy` note on
  the suite case. `reconcile_counts.py` understands it (self-test
  extended). (`VACUOUS` from the gap analysis is deliberately NOT
  added — `NOT-TESTABLE (instrumentation)` from 0.14.0 covers it.)

Finding 10 — fresh-chat code phases never restored the requirements,
so the analyzer's traceability check silently could not run in the
documented normal flow:
- **step 0 rebuilds `<STORY>-requirements.md`** from the suite's
  requirements (stableId → REQ-N via the tracker lines); the docs
  phase's no-suite archive now includes the requirements file; when
  neither exists (older tickets) the run says so once instead of
  degrading silently.

## 0.16.0 — 2026-07-30

Post-publish verification + count gates (Findings 6 and 7 of
`PIPELINE-REVIEW-2026-07-30.md`). The analyzer runs at step 5, before
publishing (6), bug filing (7) and the run sheet (9) — so its
"write-back missing" check was unreachable by construction, and no one
ever verified the run's final published state. Separately, report
numbers were hand-tallied (three counts of the same 89 headings gave
three answers) and posted to Jira unchecked.

- **`qa-pipeline-code`: mandatory post-publish verification** as the
  last action of the run: write-back notes actually landed (re-read a
  sample via `get_test_case`), every FAIL has a bug key or an explicit
  "not filed" line, both step-6 comments exist (re-read, don't
  assume), runsheet outputs exist. Result appended to the run report
  as `## Post-publish verification` and stated in the final response.
- **Count gates:** `qa-pipeline-code` step 6 refuses to post while a
  report's numbers disagree with `reconcile_counts.py` (or with the
  report's own Scope vs Statistics); `qa-pipeline-docs` step 6
  mechanically recounts the `### TC-REQ` headings before posting the
  tracker statistics; `qa-test-cases` derives its statistics block by
  counting headings, never by hand (dual-tag `[API][UI]` counted once,
  own row).
- **Analyzer** bucket 4 now states plainly where its write-back check
  can and cannot fire, pointing to the orchestrator's post-publish
  verification for the orchestrated flow.

## 0.15.0 — 2026-07-30

Verdict corrections (Finding 2 of `PIPELINE-REVIEW-2026-07-30.md`).
Step 6 publishes verdicts before the human run exists; on EP-53978 the
triage and the tester then overturned at least eight of them — and
nothing could say so: no retraction convention, and the tester's actual
results (a TC/Result/Notes TSV) were read by no skill. The system of
record kept asserting PASS on a violated privacy requirement.

- **Retraction convention** in `qa-service-publish.md` → "Result
  write-back", binding on every writer of run lines: a contradicting
  verdict appends `Run <date> — SUPERSEDES <prior> (<old> → <new>):
  <reason>` and maintains a single `⚠ CURRENT VERDICT:` first line in
  the case notes. History is append-only; the current truth is
  unmissable. Retractions are also listed first in the Jira human
  summary.
- **New stage 10: `qa-manual-results`.** Ingests the completed run
  sheet (xlsx Result/Notes) or a pasted TC/Result/Notes table or the
  triage file; **joins by TC id, never row position**; classifies each
  entry CONFIRMS / FILLS / RETRACTS (+ non-standard verdicts and
  unmatched rows, never coerced or dropped); writes
  `<KEY>-manual-results.md`; posts the archive + human-summary comment
  pair; writes suite notes under the retraction convention; offers to
  file unfiled FAIL bugs. One confirm pause before any write.
- **Wiring:** `qa-pipeline-code` gains deferred step 10 and now ends by
  saying the published verdicts are provisional until manual results
  are ingested; its resume mode restores `manual-results` and triage
  files and honours them over older stage reports. The analyzer's
  inputs now include `<KEY>-manual-results.md`,
  `<KEY>-remaining-cases-triage.md` and tester TSVs, with a 🔴
  retraction-integrity check (contradiction with no supersede line).
  README stage table/flow, MAINTAINERS repo tree (which had omitted
  stage 9 — both 9 and 10 now listed), and the plugin description
  updated.

## 0.14.0 — 2026-07-30

False-pass defenses + channel re-routing (Findings 1 and 3 of
`PIPELINE-REVIEW-2026-07-30.md`). The verdict-producing stages could
not tell a false pass from a pass — the anti-false-pass knowledge
lived only in `qa-manual-runsheet`, which runs after verdicts are
published — and the channel tag was an irreversible routing decision
made blind at the docs phase. Both mechanisms produced the EP-53978
false PASSes (TC-REQ-37.1, TC-REQ-16.3).

- **New shared reference
  `api-testing/references/absence-check-protocol.md`** — binding on
  stages 7 and 8, audited by the analyzer: (1) API-created data cannot
  prove anything on an instrumented surface (counters / leads /
  analytics / statistics / notifications / dashboards); (2) an absence
  check with no positive control is VACUOUS, not PASS; (3) measure the
  ingestion lag once per run and read absence twice — never from a
  single immediate read; (4) "anywhere" claims enumerate surfaces per
  role or cap at PARTIAL.
- **api-testing**: new status `NOT-TESTABLE (instrumentation)` + a
  "Route to web-testing" report section (provenance gate in Step 4;
  template updated). It no longer records PASS/PARTIAL on instrumented
  surfaces fed by API-created preconditions.
- **web-testing**: takes routed-in cases into scope regardless of
  channel tag (api-testing's routed section + code-review `RE-ROUTE
  [UI]`); pauses for the user to create UI preconditions where its
  no-write rule forbids it; absence checks require the positive
  control + post-lag second read. Its completeness check is now
  satisfiable: `[UI]` QA/FAIL + routed-in, and every QA/FAIL case of
  any channel must appear exactly once somewhere (also closes the
  four-cases-vanished hole from Finding 7).
- **browser-rules "Waiting"**: absence-check exception — wait for the
  positive control to appear, then read the absence (the old rule was
  backwards for absence checks).
- **code-review**: new status `RE-ROUTE [UI]` with file+line evidence
  — the first stage that sees the code can now override a blind docs-
  phase channel tag. Template + statistics updated.
- **qa-test-cases / qa-checklist**: provenance-sensitive checks may
  carry a dual `[API][UI]` tag; absence checks are worded with their
  positive control; the tag is documented as a routing hint that
  code review may override, not a verdict.
- **qa-run-analyzer**: new "Evidence quality" bucket (🔴 absence-PASS
  without positive control; 🔴 instrumented-surface PASS with API
  provenance; 🔴 same surface conclusive+unmeasurable in one run;
  🟡 single-read absence verdicts; routing integrity for routed
  cases). Health table + chat summary updated. The reconcile check no
  longer "certifies" blind routing when counts balance.
- **reconcile_counts.py**: understands `RE-ROUTE [UI]` (self-test
  extended).

Verdict semantics change: runs will report fewer automated PASSes on
analytics-backed claims and more routed/instrumentation statuses —
that is the point; those PASSes were unearned.

## 0.13.2 — 2026-07-30

The improvement loop (Finding 4 of `PIPELINE-REVIEW-2026-07-30.md`).
Run reports kept issuing 🔴 pipeline fixes that nothing consumed — the
2026-07-28 report's two named repairs were still absent two releases
later. This release closes the loop mechanism and implements both.

- **MAINTAINERS recipe, new step 1:** any 🔴 [Pipeline/skill] item in
  the latest run report / triage must be implemented (CHANGELOG entry)
  or explicitly rejected in the CHANGELOG. A recommendation with
  neither is an open defect of the plugin.
- **`reconcile_counts.py` rewritten** — the three defects the run
  report named, plus two found while fixing: statuses now count only on
  result rows (statistics tables no longer inflate counts); ids no
  longer swallow trailing periods; one status per row (adjacent-pipe
  undercount gone); bold (`**FAIL CONFIRMED**`) and qualified
  (`NOT-TESTABLE (instrumentation)`, `BLOCKED (unverified)`) statuses
  count; `PASS(code)` is tallied as a source marker, never as PASS;
  range rows (`TC-REQ-29.1–29.3`) expand; `RISK-*` ids are visible.
  Ships `--selftest`; the analyzer must run it before trusting output,
  and recount by hand + raise 🔴 if it fails. Verified against
  EP-53978: mechanical counts now match the review's hand counts
  (89 ids; code-review PASS=58/QA=28/N-A=2/FAIL=1).
- **`bitbucket-access.md` — "Credential handling — hard rules":** never
  a credential in a URL / inline in a command; one-shot credential
  helper recipe for clone/fetch; a failed command that touched a secret
  is a rotation event. (The 2026-07-28 token-echo fix, finally landed.)

Not done here (later findings): re-status of TC-REQ-1.1 and the token
rotation itself are run-side actions, not repo changes — flagged to the
maintainer; runs/<KEY>/ layout still pending.

## 0.13.1 — 2026-07-30

Secrets safety (Finding 5 of `PIPELINE-REVIEW-2026-07-30.md`). The
plugin root doubles as run workspace and credential store, and the
ignore list was per-filename whack-a-mole — five run artifacts were
sitting untracked-and-unignored while the documented commit recipe was
`git add -A`.

- **`.gitignore` rewritten to broad rules.** `EP-*` (all per-ticket
  artifacts, any extension), `build_*.py`, `*-testdata*`, all runsheet
  xlsx variants, `*-preserved-entries.tsv`, `runs/` — replacing the
  nine-per-run filename patterns. Fixtures keep their negation. A new
  artifact name can no longer leak by being new.
- **`git add -A` banned in MAINTAINERS.** Both recipes (update +
  publish) now require: `git status --short` review → secret scan
  (`secret-leak-scan` skill or gitleaks) → `git add <explicit paths>`.
- **`qa-manual-runsheet` Step 7** now ends with a mandatory secret scan
  and an ignore-coverage check over its own emitted artifacts (they
  carry live credentials by design).
- **`.env.qa-agents` co-location documented** as a deliberate risk in
  MAINTAINERS ("Gotchas"): `git archive` is safe, raw folder copies are
  not. Also fixed the stale `D:\Coding\…` repo path (now
  `C:\media-files\Coding\qa-pipeline-skill`).

Not done here (tracked as review findings): moving run outputs to
`runs/<KEY>/`, the run-report 🔴-items enforcement rule (Finding 4),
and narrowing `.claude/settings.local.json` allowlists (Finding 17).

## 0.13.0 — 2026-07-29

`qa-manual-runsheet` is now **stage 9 of `qa-pipeline-code`**, not an
optional side branch nobody invokes.

It was wired nowhere: neither orchestrator referenced it, so the stage
existed and never ran. It also belongs at the END of the code phase
rather than after the docs phase — the run sheet's whole value is telling
the human what is *left*, which it can only do once the automated
verdicts exist. On a real ticket that was the difference between handing
a tester **89 rows and 11**.

Pauses for the throwaway-event authorisation before provisioning, since
the stage creates accounts on a live environment. `qa-pipeline-docs` now
explicitly says not to run it there.

Run-sheet format settled at 12 columns after review: the old pack's
informative columns plus Log in as / Do / Expect, the palette already in
`build_data_pack.py`, per-value colour on the four verdict columns and
Result, one font throughout. A muted pastel palette and a monospace
credential column were both tried and rejected; both are recorded in
`references/runsheet-format.md` so they are not reinvented.

## 0.12.0 — 2026-07-29

New stage **`qa-manual-runsheet`** (stage 4.5): provisions and verifies
fixture data on a throwaway test event, then emits a lean run sheet a
human can work straight through — one explicit "Log in as", one action,
one expected result per row.

Added after a run where the pack was technically complete and still cost
the tester hours: it named accounts by internal fixture key, buried which
one to log in as, and shipped **no Expected-result column at all**.

The stage also carries the run's hard-won anti-false-pass rules, which
apply to the whole pipeline and not just to it:

- **UI-only conditions.** Favourite tracking fires client-side, so a
  precondition created over the API never enters the analytics pipeline.
  This produced a PARTIAL that hid a real privacy leak (EP-55701) and two
  defects filed against the wrong root cause.
- **Ingestion lag.** Analytics-backed surfaces lag 30–60 minutes; an
  immediate read returns a clean result. This produced a false PASS on a
  privacy requirement later filed as EP-55715.
- **Instruments that lie.** `getInteractions.data.acc.favourite` is a
  capability flag, not state; several precondition "verifications" built
  on it were worthless.
- **Probe every blocker.** Four cases were blocked on premises that each
  dissolved on one check.
- **Never share a fixture across counter cases**, and set every dependent
  attribute explicitly — a fixture that defaults silently invalidates
  cases quietly.

References: `skills/qa-manual-runsheet/references/runsheet-format.md`
(sheet spec) and `.../provisioning-rules.md` (traps + environment
specifics, each recorded with the cost it actually caused).

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
- **Run scoping.** Because suites are per FEATURE, `get_suite` also
  returns cases from earlier stories. The code phase executes only the
  case ids listed on this run's checkbox tracker (plus team-added cases
  tracing to this run's requirements, flagged in reconciliation) and
  reports "suite holds N cases; M in scope" — it never executes a whole
  feature suite because the response contained it.

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
