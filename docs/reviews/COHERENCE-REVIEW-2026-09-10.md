# ep-qa-pipeline — coherence, streamlining and currency review, 2026-09-10 (v0.42.0)

Written against the working tree at `C:\media-files\Coding\qa-pipeline-skill` as of 2026-09-10 ~11:30 UTC (CHANGELOG mtime) and the run workspace at `C:\Users\kubas\.ep-qa`. Review only; nothing under `skills/`, `scripts/`, `hooks/`, `evals/` or the manifests was touched. Line numbers are those of the files as staged today.

The burst, confirmed from the CHANGELOG headings, not from the brief: **twelve releases dated 2026-09-10** (`0.31.0` … `0.42.0`), preceded by three on 2026-09-07 (`0.28.0`–`0.30.0`) — fifteen releases in four days. Every finding below was verified against a file; where a file is quoted, the quote is verbatim.

---

## 1. Scope actually read

**Read in full, line by line:** `CLAUDE.md`, `MAINTAINERS.md`, `README.md`, `CHANGELOG.md` (all 2,517 lines — 0.28.0→0.42.0 read closely, 0.5.0→0.27.0 read for the origin of every retired concept), `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `hooks/hooks.json`, `scripts/notify.py`, `scripts/verify_plugin.py` (structure + ran it), `.gitignore`, `.gitattributes`, `.claude/settings.local.json`, `evals/triggering.md`, `fixtures/EP-0000-context.md`, all 14 `skills/*/SKILL.md`, all 38 files under `skills/*/references/` and `skills/*/scripts/` (including `reconcile_counts.py` in full, `load-env.sh`, `extract_archive.py`, `generate_pict_cases.py` skimmed — pure generator), `skills/web-testing/navigation_paths.json.bak` (keys only), `docs/reviews/PIPELINE-REVIEW-2026-09-07.md`, `docs/reviews/SKILL-BEST-PRACTICES-AUDIT-2026-07-30.md`.

**Skimmed:** the other files under `docs/` (reviews, retrospectives, specs, prompts — history, not contract), the four root `EP-*.md` investigation notes and `EP-QA-ENVIRONMENT-RECORD.md` (untracked, ignored by `EP-*`), `COHERENCE-REVIEW-PROMPT.md`.

**Not read:** `ep-qa-pipeline-interactive.html` (2.3 MB), `ep-qa-pipeline-overview.pptx`, `EP-GS-smoke-prod459.xlsx`, `__pycache__/`, `.playwright-mcp/` (307 files), `.git/`.

**Run artefacts read (the "newest complete run" and its neighbours):** there is no `runs/<KEY>/docs/` or `runs/<KEY>/r<N>/` anywhere on the machine — `~/.ep-qa/runs/` holds one flat folder, `legacy/`, with 1,047 files for 47 tickets (see Surprises). So the newest complete runs are flat-named: **EP-56197 round 4** (2026-09-09: pr-summary, code-review, api-testing, web-testing, web-evidence, sources, retest-scope, run-report, human-summary, manual-results, open-items, test-cases — read in full), **EP-56740 round 2** (2026-09-10 06:44–07:20 UTC, the newest run on the machine: api-testing-r2, web-testing-r2, run-report-r2, human-summary-r2, retest-scope, sources, open-items — read in full), **EP-48506** (2026-09-08/09: the newest run with a docs phase — context, requirements, test-cases, checklist, recon, docs-run-report, sources, pr-summary, code-review, api-testing, web-testing, run-report, human-summary, manual-results, open-items — read in full), **EP-56998** (2026-09-08 bug-fix: run-report, open-items, human-summary, manual-results, test-cases, sources, code-review, api-testing, web-testing — read in full), plus the `EP-56268` and `EP-56418` ledgers and `EP-56268-retest3-run-report.md`. The 1,047-file listing itself was analysed by shape (suffix histogram, folder layout, mtimes).

**Tools compared:** the QA Service MCP connector's 118 tools as exposed in this session, the Playwright MCP tool set as exposed in this session (`mcp__remote-devices__playwright__*`) plus the upstream README fetched today, and the current Claude Code docs (skills, hooks, plugins, marketplaces, sub-agents, MCP, `claude plugin eval`).

`python3 scripts/verify_plugin.py` (run on the staged copy, no `.git`): **8 ok · 1 warn · 0 fail** — the warn is `staged: not a git repo (or git failed) — staged-paths check skipped`, an artefact of the snapshot, not of the tree. Everything the script checks is taken as verified below and not re-derived.

---

## 2. Verdict in five lines

1. The design is coherent at the level of intent and mostly coherent at the level of rules; the burst broke it at the level of **references between files** — 40 surviving mentions of retired concepts that mislead (26 stale, 14 contradicting a current rule), and 7 rule pairs a single run cannot obey at once (the worst: `jira-writing-style.md` still says a bug's Expected result is the test case's `Exp:` block verbatim, which 0.38 forbade).
2. **Nothing shipped since 0.30.0 has been exercised by a run.** Not one `runs/<KEY>/r<N>/` folder exists; not one walk plan, walk state or walk results file exists; not one QA Service test run was ever created by a pipeline run; no report uses `Arrived as:`; no report mentions `ALLOWED_HOSTS`; no docs-phase file carries an `AC-n`. Twelve releases of behaviour rest on the author's dry-runs alone.
3. The fixture the smoke test compares against (`fixtures/EP-0000-context.md`) does not itself carry the 0.42.0 AC ledger it claims stage 1 produces, so the one regression test the plugin has cannot pass the check 0.42.0 added.
4. The two mechanisms that demonstrably earn their keep in the run artefacts are `OBSERVATION (no source checked)` + the `Source:`/`Clause:` gate (used 3–14 times per report, and they changed outcomes) and `reconcile_counts.py` (ran and reconciled on every run read). Two mechanisms are demonstrably dead weight: the wave-1 Jira status comment (declined by the user in all five newest runs) and the code-orchestrator run clock (no trace in any artefact, budgets never recalibrated).
5. The prior reviews were mostly honoured, but four 2026-09-07 proposals were **silently dropped after being promised for "0.30.1"** (§4.4 script section-scoping, §4.6 code-review base-branch rules, §4.7 the OBSERVATION rename, §4.8 analyzer post-publish mode) — a MAINTAINERS-rule breach the CHANGELOG's own words create.

---

## 3. Retired-concept census (1a)

Method: every concept the burst (0.28.0–0.42.0) retired, renamed or demoted was listed from the CHANGELOG, then the whole tracked tree (skills, references, scripts, README, MAINTAINERS, CLAUDE.md, evals, manifests, hooks, fixture, `.gitignore`) was grepped for each. `docs/` and the CHANGELOG itself are excluded (history). **Mentions examined: ~230 grep hits across 30 retired terms (hits that are only a current skill's name, e.g. `qa-manual-runsheet`, excluded) · (i) correctly marked legacy/read-only: ~190 · (ii) stale and misleading: 26 · (iii) contradicting a current rule: 14** (12 in the table below plus F1 and F4). Only (ii) and (iii) are tabled.

| # | Retired concept (release) | Surviving mention · file:line | Class | What it should say now |
|---|---|---|---|---|
| 1 | Stage 3 / `qa-checklist` (0.40.0) | `.claude-plugin/plugin.json:4` — "turns a Jira ticket into groomed requirements, a channel-tagged checklist, and test cases" | (ii) | "…groomed requirements and test cases (with a structural-checks section)"; the checklist is no longer a deliverable. This is the text discovery/marketplace users read. |
| 2 | Stage 3 (0.40.0) | `.claude-plugin/marketplace.json:14` — "Jira ticket -> groomed requirements -> checklist -> test cases -> PR review …" | (ii) | Drop "checklist"; also drop the `->` arrows (0.18.2 removed them from descriptions for the upload validator — the marketplace description is the same kind of field). |
| 3 | Stage 3 (0.40.0) | `skills/qa-pipeline-docs/SKILL.md:143` — "On yes, post before stage 3; the run continues either way." | (ii) | "post before stage 4". |
| 4 | Stage 3 (0.40.0) | `skills/qa-pipeline-docs/SKILL.md:83` — "`⏱ Stage <n>/6 done — <stage name> …`"; budgets at :85–87 list five stages | (ii) | `/5`. |
| 5 | Stage 3 (0.40.0) | `skills/qa-pipeline-docs/SKILL.md:264` — "The paths of the four stage files + the run report" | (ii) | "three stage files (context, requirements, test-cases; recon when it ran)". |
| 6 | Checklist as a count unit (0.40.0) | `skills/qa-run-analyzer/references/output-template.md:76` — "N requirements → N checks → N test cases"; :55 "requirement/check/test-case counts" | (ii) | "N requirements → N test cases + S structural checks". |
| 7 | `<KEY>-checklist.md` (0.40.0) | `.gitignore:30` — `*-checklist.md` | (i)→(ii) | Keep only if the legacy comment covers it; today it sits under "stage outputs for non-EP ticket keys" as if still produced. Move under a "legacy shapes" comment or delete. |
| 8 | Machine archive / two-comment wave 1 (0.33.0) | `skills/qa-pipeline-code/references/run-modes.md:168–169` — "Post results as a normal comment pair with the verdict line prefixed `RETEST:`." | (iii) | "Wave 1 posts the one status line (`RETEST:` prefix); the human summary follows at stage 10." A "comment pair" is exactly what 0.33 retired. |
| 9 | Run sheet as the deliverable (0.31.0) | `run-modes.md:174–175` — "Stage 10 ingests the retest sheet like a first run." | (ii) | "…the retest walk results (or an exported sheet)…". |
| 10 | Run sheet as the deliverable (0.31.0) | `skills/qa-test-cases/references/test-case-design-rules.md:62–63` — "The core case is the row a human always walks in the stage-9 run sheet" | (ii) | "…the card the walk (stage 10a) always presents". |
| 11 | Walk = stage 10a, not 9 (0.31.0) | `skills/qa-test-cases/SKILL.md:186` — "the card the manual walk (stage 9) always presents"; `skills/qa-pipeline-docs/references/qa-service-publish.md:122` — "the human-tier representative that stage 9 always walks" | (ii) | Stage 9 builds the plan; stage 10a walks it. Say "stage 10a" or "the walk". |
| 12 | Run sheet as the deliverable (0.31.0) | `skills/qa-manual-results/SKILL.md:34–35` — "before the human walks the run sheet" | (ii) | "before the human round". |
| 13 | Run sheet as the deliverable (0.31.0) | `skills/qa-pipeline-docs/SKILL.md:274–275` — "Do NOT run `qa-manual-runsheet` here — the run sheet needs the automated verdicts" | (ii) | "the walk plan needs…". |
| 14 | Reference tab (0.34.0 said both leftovers were fixed) | `skills/qa-manual-results/SKILL.md:93–94` — "(its Coverage section; an exported sheet's Reference tab)" | (i) | Correct as written (the export still has one) — listed because 0.34.0 claimed the term was gone; it is not, and need not be. |
| 15 | Chrome extension as the executor (0.35.0) | `skills/web-testing/references/browser-rules.md:9–11` — "The skill uses the Claude in Chrome extension for all browser actions. These rules are mandatory for every interaction with the page." | (iii) | "These rules are written for the Chrome-extension fallback; on the Playwright backend the tool names differ (`playwright-executor.md`) but the see→locate→act→verify pattern, waiting and MUI notes apply unchanged." The file is named from `web-testing/SKILL.md:117` as required reading. |
| 16 | "save in the working directory" (0.35.0) | `skills/qa-run-analyzer/SKILL.md:269–271` — "(the Playwright backend cannot always write the file — `playwright-executor.md` → Evidence)" | (ii) | Now false against the current Playwright MCP (`--output-dir`, see §8); should read "when the backend's output dir is not the run folder". |
| 17 | `Source:` as arrival column (0.38.0) | `skills/code-review/references/output-template.md:86–96` — Statistics table has no `OBSERVATION (no source checked)` row although 0.38.0 says the row was "added … (all three)" and code-review emits the status (`SKILL.md:217–218`) | (iii) | Add the row; `status-vocabulary.md:8–10` calls a status missing from one place "a defect". |
| 18 | "no delete tools" (0.37.0) | `qa-service-publish.md:296–297` — "There are no delete tools — never try to remove superseded items"; `:195` — "(there is still no delete)"; `:246` — "and there is no delete" | (iii) | 0.37.0 corrected the same file's Preconditions (`:30–34`: "The connector DOES expose destructive tools — `delete_suite`, …"). The three older sentences must read "the pipeline never deletes" — a rule, not a fact about the connector. |
| 19 | "requirements are immutable / `-FR-NNb` revision" (0.11.1) | `qa-service-publish.md:275` — "Apply the requirement-immutability and case-dedup rules below." | (iii) | There is no immutability rule below (`:303–306` says the opposite: "Changed requirements are edited in place"). Delete the phrase. |
| 20 | STRUCT cases (0.33.0) | `qa-service-publish.md:538–539` — "they had no suite case until STRUCT cases (0.35)" | (ii) | "(0.33)". |
| 21 | Checkbox tracker lifetime (0.34.0) | `qa-service-publish.md:530` — "Checkbox tracker (0.26 – 0.33)" | (ii) | The tracker existed from 0.7.0 (one line per case since 0.11.2) and was retired in 0.34.0: "(0.7 – 0.33)". |
| 22 | e2e `.env` / `VISITOR_*` credentials (0.39.0; login-config calls them legacy) | `README.md:60` — "reading credentials from `~/.ep-qa/.env.qa-agents` (`VISITOR_EMAIL`/`VISITOR_PASSWORD`, `ADMIN_USERNAME`/`ADMIN_PASSWORD`)" | (iii) | `login-config.md:34–35` says `VISITOR_EMAIL` / `VISITOR_PASSWORD` are "Legacy … no longer required" and `:25–33` makes admin + impersonation the single credential set. README must match. |
| 23 | Manual visitor account (login-config's own legacy note) | `skills/web-testing/references/login-config.md:66–67` — "use the shared manual visitor account above" | (iii) | The account "above" is the legacy one the same file retires at :34–35. "…use admin impersonation (above)". |
| 24 | Per-name scratch patterns (0.30.0: "`_*` replaces the per-name `_s9_*` / `_ep53978_*` patterns"; 0.39.0 narrowed to `_[!_]*`) | `.gitignore:76–77` — `_s9_*`, `_ep53978_*` | (ii) | Delete both; `_[!_]*` at :85 covers them. Two CHANGELOG entries say they are gone. |
| 25 | Data pack (0.13.0 replaced it with the run sheet) | `.gitignore:65` — `*-manual-test-data-pack.xlsx` | (ii) | Legacy shape; move under a legacy comment or drop. |
| 26 | `-run-analyzer.md` (never a produced name — the report is `-run-report.md`) | `.gitignore:37` — `*-run-analyzer.md` | (ii) | Delete. |
| 27 | "working directory" (0.32.0: replaced across 21 files) | `fixtures/EP-0000-context.md:52` — "Copy this file into a chat's working directory." | (ii) | "into `~/.ep-qa/runs/EP-0000/docs/`". |
| 28 | `ALLOWED_HOSTS` example (0.39.0) | `skills/qa-pipeline/references/environment.md:89` — `ALLOWED_HOSTS=api-alpha2.expoplatform.net,ennies-alpha2.expoplatform.net,*.rc.expoplatform.net` | (ii) | The host today's run actually used is `canyon2026-rc.expoplatform.net` (`EP-56740-run-report-r2.md`, stage 8 row) — `*.rc.expoplatform.net` does not match it (`-rc`, not `.rc.`), nor the `*alphanext*` hosts of EP-48506. Give an example that matches the hosts the runs use, or say "one entry per host — wildcards match label boundaries only". |
| 29 | Playwright MCP sandbox claim (0.35.0) | `skills/web-testing/references/playwright-executor.md:69–71` — "The Playwright MCP backend writes only inside its own sandbox root and refuses any other path" | (ii) | Stale against the current server: files may land in `--output-dir` or the workspace root (README, fetched today; §8). Point the output dir at `runs/<KEY>/r<N>/evidence/` and the copy step disappears. |
| 30 | Analyzer inputs (0.31.0/0.38.0 added six files) | `skills/qa-run-analyzer/SKILL.md:4–7` (description) — "Reads whatever pipeline output files are present (context, requirements, test-cases, pr-summary, code-review, api-testing, web-testing)" vs body `:34–46` reading 17 file kinds | (ii) | Description: "…the stage reports, the source register, the evidence file, the walk plan/results, the manual results and the open-items ledger". This is the discovery field; the 09-07 review asked for this and 0.35 fixed only web-testing's. |
| 31 | Fixture as stage-1 output (0.42.0) | `fixtures/EP-0000-context.md:17–31` — five bare bullets, no `AC-n`, no `AC items on the page … captured …` line, while `:62–64` promises "the five requirement bullets numbered `AC-1…AC-5` and the comment `CM-1` by stage 1" | (iii) | The fixture IS the stage-1 output (the smoke test runs grooming → test-cases on it, `:53`). Rewrite its Requirements section in the 0.42 shape or the expected output `test-cases-example.md` (`Covers: AC-1`…) can never be reproduced from it. `reconcile_counts.py EP-0000` on the fixture prints "no ids anywhere — a pre-0.42 ticket". |
| 32 | Legacy tidy-up target (0.32.0 / 0.39.0) | `data-locations.md:74–77` — "move them into `$EP_QA_HOME/runs/<ISSUEKEY>/legacy/` (root files)" vs `MAINTAINERS.md:271–272` — "move them to `~/.ep-qa/runs/legacy/` when convenient" | (iii) | Two documents, two layouts. The machine followed MAINTAINERS (one flat `runs/legacy/`, 1,047 files). `reconcile_counts.py` resolves neither (`:202–224` looks for `runs/<KEY>/r<N>` then falls to the cwd). Pick one, and teach the script and `data-locations.md` resolution step 2 that shape. |
| 33 | "Not executed here" as an api-testing input (0.8.0 removed the ordering fossil) | `skills/api-testing/SKILL.md:99–101` — "(Standalone runs only: if web-testing already ran and lists `[API]` cases under 'Not executed here', include those too.)" | (i) | Correctly scoped to standalone runs; listed because it is the last trace of the reversed order. Harmless. |
| 34 | `-retestN-` suffix (0.32.0) | `data-locations.md:50,66` | (i) | Correct (explains the retirement). The **runs**, however, still use suffixes today: `EP-56740-run-report-r2.md` (2026-09-10 06:48) — see §11. |
| 35 | Jira archive (0.33.0) | 62 mentions across 22 files | (i) | All marked legacy / "retired 0.33.0" / "no archive since". Fine, but see §7 (the retirement is explained in nine places). |
| 36 | `known_defect` for SPEC-DEFECT (0.30.0) | 14 mentions | (i) | All as "never `known_defect`". Fine. |
| 37 | `⚠ CURRENT VERDICT:` / `SUPERSEDES` notes (0.30.0) | 9 mentions | (i) | All as "retired / pre-0.30 history". Fine. `qa-pipeline-code/SKILL.md:199` uses "SUPERSEDES" for the manual-results file precedence — different sense, but the same token; reword to "overrides". |
| 38 | `PROVISIONAL` status line (0.19.0 → 0.38.0 `DRAFT`) | `results-comment-template.md:200` — "include the `Status: PROVISIONAL` line" (the step-8 story-note variant) | (ii) | The template's own header rule (`:123–128`) now uses `DRAFT — awaiting stage 10`. One vocabulary: `PROVISIONAL` only on the story-note variant, or rename it too. |
| 39 | Stage 4.5 / Suggested settings / `Test12345!` / operator accountId / `build_data_pack` (0.18.1 / 0.40 / 0.39 / 0.39 / 0.38) | none in the tree | — | Clean. (`build_data_pack.py` does exist in `~/.ep-qa/runs/legacy/` — 0.38.0's "never existed" is wrong about the workspace, right about the repo.) |
| 40 | "process the ticket" → dispatcher, "run the QA checks" → orchestrator (0.38.0) | `evals/triggering.md:15,60` | (i) | Correct. |
| 41 | `Source: QA` arrival column (0.38.0) | api/web templates use `Arrived as` | (i) | Correct in the templates; **no run report yet uses it** (§11). |

Two more classified (iii) because they collide with a current rule rather than name a retired one — they are in §4 as findings F1 and F4: `jira-writing-style.md:43–44` (Expected result = `Exp:` verbatim) and `bitbucket-access.md:115–121` (base branch `master`).

---

## 4. Findings ranked by consequence

Severity: 🔴 would route a tester to a retired flow, produce a wrong record, or leave a paid-for rule unenforceable · 🟡 contradiction or drift a careful agent can still resolve · ⚪ tidiness. Counts: **🔴 9 · 🟡 14 · ⚪ 6**.

### 🔴 F1 — A bug's Expected result is defined two incompatible ways, and the file that loses says it wins

`skills/qa-pipeline-code/references/jira-writing-style.md:43–44`: "**Expected result:** the test case's `Exp:` block, verbatim. Nothing added." — and `:9–12`: "When a template and this file disagree on tone or length, this file wins."
`skills/qa-pipeline-code/references/bug-report-template.md:45–52` (0.38.0): "h3. Expected result — AC-<n>: "<the register clause — the acceptance criterion the build contradicts, quoted verbatim>" … Never the test case's Exp: block — a test case is not a source of record".
The 0.38.0 change ("Bug report `Expected result` = the register clause, not the test case's `Exp:` block") was made in the template and not in the style guide the template tells the drafter to read first (`bug-report-template.md:7–8`). An agent obeying the style guide's precedence clause writes the pre-0.38 bug. This also weakens the 0.28.0 source-of-record gate, an incident-born rule (EP-56133).
**Fix:** `jira-writing-style.md:43–44` → "**Expected result:** the register clause the build violates, quoted, led by its `AC-<n>` (`bug-report-template.md`); the case's `Exp:` goes in Source." And narrow `:11–12` to "on tone or length" only (it already says so — add "never on content").

### 🔴 F2 — Twelve releases, zero runs: the run-folder layout, the walk, the test run and the AC ledger have never been exercised

Evidence from `~/.ep-qa/runs/`: 1,047 files, all under one flat `legacy/`; zero `docs/` or `r<N>/` directories; zero files matching `-walk-plan`, `-walk-state`, `-walk-results` (one `EP-47675-walk-sheet.xlsx` from July); zero run reports naming a QA Service run id (grep `create_test_run|run id|Run: [0-9a-f]{8}` → none); zero reports with `Arrived as` (0.38); zero with `ALLOWED_HOSTS` (0.39); zero docs-phase files with an `AC-n` (0.42). The newest run on the machine, EP-56740 round 2 (`EP-56740-run-report-r2.md`, 2026-09-10 06:48–07:20 UTC), writes flat `-r2` suffixed files and says "working directory `qa-pipeline-skill`" — neither the pre-0.32 `-retestN-` convention nor the 0.32 folder. The only QA Service run ever recorded is the 2026-09-02 off-book one cited in `test-runs.md:26–31`.
This is not a stale sentence; it is the whole design after 0.30 resting on dry-runs. §11 lists what each release changed that nothing has exercised.
**Fix:** before the next release, run one real Story end to end (docs → publish → code → run → walk → results) and let the analyzer and the post-publish check fire on it; every 🔴 the run raises against 0.31–0.42 becomes the 0.43 CHANGELOG. Until then, mark 0.31–0.42 features "unexercised" in the README's stage table (one word per row) so a colleague installing the plugin knows.

### 🔴 F3 — The smoke-test fixture cannot pass the check 0.42.0 added, and its expected output cannot be produced from it

`fixtures/EP-0000-context.md:17–31` — Requirements are five bare bullets ("- The exhibitor settings page in the admin panel shows a "Featured" toggle …") with no `AC-n (Confluence §…):` ids and no `AC items on the page: N · captured: N` line. `:53` says the smoke test runs "`requirements-grooming` → `qa-test-cases` on it" — i.e. the fixture is the stage-1 output — yet `:62–64` expects "the five requirement bullets numbered `AC-1…AC-5` … by stage 1". Stage 1 never runs in the smoke test. `skills/qa-test-cases/references/test-cases-example.md:18–19,52,85…` carries `Covers: AC-1` etc. and `AC coverage: 5/5`. `reconcile_counts.py EP-0000` on the fixture prints "AC ledger: no ids anywhere — a pre-0.42 ticket" (`reconcile_counts.py:285`). 0.42.0 says "Fixture expectations … updated" — the expectations were, the body was not.
**Fix:** rewrite `fixtures/EP-0000-context.md:17–39` in the 0.42 shape (`- AC-1 (Confluence §2.1): …` ×5, `- CM-1 (comment 2026-07-01): …`, `AC items on the page: 5 · captured: 5`) and change `:52` "working directory" → the run folder. Then run the smoke test once and diff against the example.

### 🔴 F4 — The shared Bitbucket reference tells the code phase to diff against the wrong base branch in its own command block

`skills/pr-summary/references/bitbucket-access.md:34–37` (0.25.1): "**Base branch is PER REPO — this matters:** `expoplatform-main-ira` (the monolith) branches from **`alpha`** … Diffing a monolith branch against `master` produces a wrong diff." Same file, `:115–117`: "**Branch mode (branch name, no PR):** … base branch is `master` unless the user says otherwise." and `:121`: `git fetch origin {branch} && git diff --name-only origin/master...origin/{branch}`. The command an agent copies is the one 0.25.1 says produces wrong diffs. `EP-48506-open-items.md` row 15 records exactly this class of trap ("code phase must diff against the merge-base, not master").
**Fix:** `:115–128` → "base = the repo's default branch (`git remote show origin | grep HEAD`; monolith `alpha`, `portal-ui`/`admin-ui` `master`)" and parametrise the commands with `{base}`; add "diff against the merge-base (`origin/{base}...origin/{branch}` is already three-dot — say so)".

### 🔴 F5 — `code-review` forbids the reads that produce its best findings; the fix was promised for 0.30.1 and never made

`skills/code-review/SKILL.md:82–84`: "Work only within the PR branch or the specified branch. Do not take code from main, the base branch, other branches or the general repository context." `:91`: "Do not analyze pre-existing code that was not changed in the PR." `:119–120`: "Do not read files from the base branch, master or other branches."
Versus `bitbucket-access.md:133–146` (0.25.1): "What it enables beyond the diff: find every CALLER of a changed method (`git grep` …); … trace shared helpers across `backend` / `frontend` / `universal`. … the wider tree is for callers/blast radius" — and `run-modes.md:125–126` (retest tier 2): "cases sharing the fixed code path". CHANGELOG 0.30.0 (`:986–989`): "`code-review`'s "never read the base branch" rule contradicts the `master` check that produced that run's top 🔴. Planned for 0.30.1." No 0.30.1 exists; no later entry rejects it. `EP-56197-open-items.md` row 2 (`RISK-5018-2 — master still unfixed`) is the finding that only a forbidden read could make.
**Fix:** as the 09-07 review §4.6 proposed: keep the default narrow, add a bounded "release-line and dependency check" — (a) in bug-fix/retest mode confirm the fix hunk is present on every release line `fixVersion` names (absent → 🔴 [Product]); (b) an unchanged file may be read when pr-summary's blast-radius section names it or a `git grep` for callers lands on it — file+line evidence, labelled "outside the diff". Record the decision in the CHANGELOG either way.

### 🔴 F6 — 0.42.0 publishes `detail.ac` and nothing ever reads it back; the AC-ledger check cannot run in the code phase

`qa-service-publish.md:91`: "`detail.ac` = the same string, verbatim (0.42.0) — the acceptance-criterion ids this requirement covers". The only mention of `detail.ac` in the tree is that line. `qa-pipeline-code/SKILL.md:167–171` rebuilds `<STORY>-requirements.md` "from the suite's requirements (`detail.pipelineId` → REQ-N)" and says nothing about restoring `source:` lines from `detail.ac`; `qa-service-publish.md:369–399` ("Code phase — suite as the case source") does not mention `Covers:` or `detail.ac` either. So in retest/bug-fix mode — "most code-phase runs" (`sources-of-record.md:14–16`) — the rebuilt files carry no ids and the analyzer's §1 AC check (`qa-run-analyzer/SKILL.md:79–93`) reports the false "pre-0.42 ticket". Compounding it: `reconcile_counts.py:289–294` reads context/requirements only from `docs/` or the cwd, while step 0 writes the rebuilt requirements into the pass folder (`qa-pipeline-code/SKILL.md:82–83`: "Every stage this orchestrator dispatches writes there and nowhere else").
**Fix:** (1) `qa-pipeline-code/SKILL.md:167–171`: "…rebuild each REQ with its `source:` line from `detail.ac` and each case group's `Covers:` from its requirement's `detail.ac`"; (2) `qa-service-publish.md` Code-phase section: one bullet for the same; (3) `reconcile_counts.py:read_docs_file`: also look in the pass folder `d`.

### 🔴 F7 — The legacy run location is defined twice, differently, and the script resolves neither

Quoted in census row 32. Consequence today: `python3 reconcile_counts.py EP-56740` with `~/.ep-qa` present resolves `~/.ep-qa/runs/EP-56740/` (absent) → falls back to `.` (`reconcile_counts.py:224`) → "file not present" for every stage unless the cwd happens to be `~/.ep-qa/runs/legacy`. The analyzer's count gate is therefore silently absent on every ticket on this machine — the exact failure mode 0.27.0 and 0.29.0 fixed once already for id shapes.
**Fix:** one sentence in `data-locations.md:74–77` and `MAINTAINERS.md:271–272` naming the same target (the flat `runs/legacy/` that exists), and ten lines in `resolve_run_dir`: when `runs/<KEY>/` is absent and `runs/legacy/<KEY>-test-cases.md` exists, return `runs/legacy` with a one-line "legacy flat layout" notice.

### 🔴 F8 — The walk plan's export spec instructs the opposite of the voice rule it renders from

`qa-manual-runsheet/references/runsheet-format.md:17–18`: "**Do** = the card's Do; **Expect** = the card's You should see" — and `:61–74` ("Can a human even run it? Put it in Do, not a column"): "open the **Do** cell with a one-line marker: … *"This click IS the case — the card sends POST /profile/connect {type:visitor, id:…}"* … *"⚠ Clicking twice will NOT work, the star toggles. Trigger it, then DevTools → Network → Copy as fetch → re-run."*"
`walk-plan-format.md:173–176` (0.31.0), voice rule 5: "**No HTTP verbs, endpoints, status codes, curl, DevTools recipes, or file paths in a human card.** If the case is that, it is AGENT-RUNS." The 0.31.0 CHANGELOG (`:790–795`) says the sheet "stays as the rendering spec … and now opens with the rendering rule" — the old section survived under it and prescribes the EP-56998 cells 0.31 was written to abolish.
**Fix:** move `runsheet-format.md:61–84` under a `### REJECTED — …` heading (the file already has the pattern at `:173`) with one line: "superseded by AGENT-RUNS cards; the export prints the `run:` line after Expect, never inside Do".

### 🔴 F9 — Credential exposure recurred after the rule that forbids it, and the rule is still prose

`bitbucket-access.md:53–82` ("Credential handling — hard rules", 0.13.2) forbids a token in a URL and gives the one-shot helper. `EP-48506-run-report.md:344–349` (2026-09-08): "🔴 [Pipeline] **Credential exposure — rotate `BB_API_TOKEN`.** … a failed `git clone` at step 0 echoed the clone URL with the token embedded into the session transcript … Second fix, in the skill: step 0's environment check does not probe git auth before a stage needs it; a `git ls-remote` probe would have caught this without ever constructing a URL. Ledger row 30." `EP-56418-open-items.md:18` (same day) lists "the `BB_API_TOKEN` rotation" as an action. Neither the incident nor the proposed `ls-remote` probe has a CHANGELOG line (grep `ls-remote|EP-48506|rotat` → only the 0.39 "nobody rotated" sentence). The rule failed twice in one day; MAINTAINERS step 1 requires an answer.
**Fix:** ship the rule as code, as `load-env.sh` did for the same class: `skills/pr-summary/scripts/bb-git.sh` (≤30 lines) wrapping `git -c credential.helper=… ` with `x-token-auth`, plus `--probe` = `git ls-remote` on each repo; step 0's environment check calls `--probe`. Record EP-48506 row 30 in the CHANGELOG.

### 🟡 F10 — Four 2026-09-07 proposals were promised for 0.30.1 and then dropped without a rejection

CHANGELOG `0.30.0:982–989`: "Not done in this release, still open … `reconcile_counts.py` still harvests statuses from the "Not executed here" table … `code-review`'s "never read the base branch" rule contradicts … Planned for 0.30.1." `0.31.0:862–864`: "EP-56197 #17 — `NOT-A-DEFECT (stated exclusion…)` is an invented status token: **DEFERRED** to the status-vocabulary release with §4.7 (the `OBSERVATION` rename); the two belong together." No 0.30.1; no status-vocabulary release; no rejection. §10 has the full table. Under `CLAUDE.md:44–45` ("Run-report 🔴 items and review findings are implemented or explicitly rejected in the CHANGELOG — never silently dropped") these are open defects of the plugin by its own definition.
**Fix:** one CHANGELOG paragraph in 0.43 dispositioning §4.4, §4.6, §4.7, §4.8 and EP-56197 #17 — implement or reject each in a sentence.

### 🟡 F11 — `browser-rules.md` still declares the extension the executor

Census row 15. `web-testing/SKILL.md:114–119` names the file as mandatory reading for the fallback only, but the file's first sentence and its tool table (`:27–43`) describe the extension as *the* backend, and its Error handling (`:169`) has no Playwright equivalent. An agent on the Playwright backend reading it as instructed ("MUI notes from browser-rules.md still apply", `playwright-executor.md:46`) meets a contradiction on line 9.
**Fix:** `browser-rules.md:9–11` → the two-backend sentence in census row 15; add a `Playwright equivalent` column to the tool table (the mapping already exists in `playwright-executor.md:34–45` — merge the two tables into one, in one file; see §7).

### 🟡 F12 — Same-session shortcut lets a stale local file override the suite

`qa-pipeline-code/SKILL.md:135–137`: "**Same-session shortcut:** if `<STORY>-test-cases.md` is already in the run folder, use it and skip the Jira read-back below." `qa-service-publish.md:371–373`: "the suite — not any local file — is the source of truth for case CONTENT (the team may have fixed cases in the web UI between phases)"; `data-locations.md:98–100`: "On divergence the suite wins." The shortcut predates the suite (0.7.0) and skips the reconciliation that 0.24.0's real run showed matters ("the suite had gained a P0 requirement and two P0 cases … a file-derived scope missed both", `run-modes.md:153–157`).
**Fix:** "…use it, but still `get_suite` and reconcile (suite wins); skip only the Jira sub-task lookup."

### 🟡 F13 — The QA Service test run is created by a pause that has been answered "no" five times running

`qa-pipeline-code/SKILL.md:337–353`: the run is created "After the yes" of the wave-1 REQUIRED PAUSE, in the same yes as the status comment. In the five newest runs the user declined wave 1 every time (`EP-56197-run-report.md` post-publish table: "Wave-1 Jira comments — ✅ deliberately NOT posted. The user ruled "post nothing yet""; `EP-56998-run-report.md`: "The user declined the wave-1 Jira write"; `EP-56268-retest3-run-report.md`: "Roman declined the wave-1 status comment at the confirm pause"; `EP-56740-run-report-r2.md`: "User elected to hold wave 1"; `EP-48506`: docs publish declined). Four of the five had no suite anyway, but the coupling means that on a suite-bearing ticket a "no" to a Jira comment also withholds the durable record 0.30.0 exists for.
**Fix:** split the yes: "(1) create the run and record — QA Service only, no Jira; (2) post the status comment?" Two questions, or one preview with two checkboxes. The record should never depend on whether a comment is wanted.

### 🟡 F14 — The open-items ledger has three column shapes across six tickets, so nothing can parse it

Spec `open-items-ledger.md:31–32`: `| # | Item | Class | First seen | Last seen | Owner | Decision | Closed |`. `EP-56197`, `EP-48506`, `EP-56418` follow it; `EP-56268-open-items.md:7` uses `| id | Item | Opened | Source | Decision | Status |`; `EP-56740-open-items.md:6` uses `| Id | Raised | Item | Status | Decision |`. MAINTAINERS step 1 tells the maintainer to "grep the latest ledgers for `[Pipeline]` rows with no Decision" — impossible across shapes, and `Class` (the `[Pipeline]` tag) is absent from two of them. Row length: 52 of 70 `EP-48506` items and 21 of 26 `EP-56197` items exceed 200 characters against "`Item` — one line" (`:39`). Decisions filled: 10 of the 122 spec-shaped rows; rows closed: 0 of 122 (stage 10 ran on three of these tickets) — the one ledger that closes anything (EP-56268, two rows "closed as retracted") is the one in its own shape.
**Fix:** make the ledger the third thing `reconcile_counts.py` (or a 30-line `ledger.py`) parses: header shape check, `[Pipeline]` rows with `Decision = —` older than two rounds, item length > 200 → 🟡. The analyzer then reads a number, not a table.

### 🟡 F15 — `code-review` emits `OBSERVATION (no source checked)` in a section its Classification list and Statistics table do not know

`code-review/SKILL.md:217–218`: "A finding with no clause in any source is `OBSERVATION (no source checked)`, never FAIL"; Classification (`:290–325`) lists PASS, FAIL, QA, N/A, RE-ROUTE, SPEC-DEFECT; `references/output-template.md:86–96` Statistics has no OBSERVATION row; Final answer (`:395`) omits SPEC-DEFECT and OBSERVATION. `status-vocabulary.md:33` says CR emits it. Real reports carry it (`EP-48506-code-review.md`: 14 occurrences; `EP-56998-code-review.md`: 6) — so the count gate cannot see them. This is 09-07 §4.6's last sentence, unaddressed.
**Fix:** add the status to Classification and the Statistics row; add SPEC-DEFECT + OBSERVATION to the Final-answer counters.

### 🟡 F16 — Analyzer description ↔ body drift (routing field)

Census row 30. The description is what discovery sees; it omits the six inputs that 0.31, 0.38 and 0.30 added (walk plan, walk results, web-evidence, sources, manual-results, ledger). A model deciding whether to fire the analyzer after a walk sees a skill that reads "context … web-testing".
**Fix:** rewrite the description's parenthesis as in census row 30; walk `evals/triggering.md` § qa-run-analyzer.

### 🟡 F17 — `qa-service-publish.md` Contents line is stale and the file is the plugin's largest

`:3–7` lists eight sections; the file has eleven (`## Structural checks …` at :126, `## Bug-fix mode …` at :401, `## Legacy formats …` at :525 are unlisted). 560 lines, read by the docs orchestrator's publish, the code orchestrator's step 0 and stage 9. The 0.18.1 rationale for Contents lines ("so a partial reader knows what exists before deciding what to skip") is defeated on the file that needs it most.
**Fix:** regenerate the line; see §7 for the split.

### 🟡 F18 — Run-modes still describes a "comment pair" and a "retest sheet"

Census rows 8–9. `run-modes.md` is the 0.41 verbatim move of pre-0.33 text; the move preserved two retired mechanisms into a file the CHANGELOG calls current ("No rule changed").

### 🟡 F19 — `login-config.md` contradicts itself and the README about which credentials exist

Census rows 22–23. A first-time adopter following README :60 provisions `VISITOR_*` variables nothing reads.

### 🟡 F20 — `environment.md`'s allow-list example would refuse today's host

Census row 28. The rule is incident-born (0.39, "never target production"); an example that does not match the hosts the runs use trains people to widen it to `*.expoplatform.net`, which defeats the point.

### 🟡 F21 — The dispatcher's state table cannot see code-phase results any more

`qa-pipeline/SKILL.md:57–58`: "QA sub-task/suite exists, no code-phase results → Code phase"; "Code-phase results exist, newest summary ❌ …". Since 0.33 the code phase leaves one status line, and since the runs above show wave 1 declined every time, Jira carries nothing; step 1.3 (`:36–40`) does say to check the run folder and `list_test_runs`, but the routing table's rows are still phrased in Jira terms and no row covers "run folder has `r<N>/` with a partial report" (resume) or "run exists, `running`, walk plan exists" (walk).
**Fix:** re-key the table on the three stores in `data-locations.md` order: run folder state → QA Service run state → Jira comments; add the resume row.

### 🟡 F22 — MAINTAINERS' repo layout omits half the tracked tree

`MAINTAINERS.md:23–49` lists `.claude-plugin/plugin.json`, README, MAINTAINERS, `skills/`, `fixtures/`, `docs/`, `~/.ep-qa`. Absent: `CLAUDE.md`, `CHANGELOG.md`, `.claude-plugin/marketplace.json`, `hooks/`, `scripts/verify_plugin.py` + `notify.py`, `evals/`, `.gitattributes`. Recipe step 3 (`:164–172`) says what to wire when adding a stage but not `evals/triggering.md`, which step 4 then requires.

### 🟡 F23 — `qa-manual-results` template promises a list it has no section for

`qa-manual-results/references/output-template.md:6`: "Case corrections applied to the suite: <N> (listed under Ledger)"; `:68–71` "## Ledger" defines only closed/carried rows. A field written by the header, read nowhere.
**Fix:** add a `## Case corrections applied` table (TC · what changed · tool) or drop "(listed under Ledger)".

### ⚪ F24 — Version numbers as control flow in always-loaded bodies

48 version tokens in `skills/*/SKILL.md` (10 in `qa-pipeline-docs`, 7 each in analyzer/code/results), 80 more in references. The 07-30 audit F8 called this the doc's anti-pattern; the burst quadrupled it ("since 0.33.0", "(0.42.0)", "retired in 0.34.0"). Each is a fossil the next release must maintain. Keep versions in the CHANGELOG and in a single "Legacy formats" section; state current behaviour plainly elsewhere.

### ⚪ F25 — Description-opener inconsistency (07-30 F6.3, undispositioned)

"The second stage of task processing" / "Fifth stage of task processing" / "Stage 9 of task processing" / "The last docs stage" / "Post-run health check". Harmless for routing; one pass.

### ⚪ F26 — `test-runs.md` `FAIL CONFIRMED` "Emitted by … MR"

`status-vocabulary.md:20` says MR emits `FAIL CONFIRMED`; `:116–118` and `qa-manual-results/SKILL.md:109–112` normalise human results to PASS / FAIL / BLOCKED / SKIPPED only. Remove "MR" from that row.

### ⚪ F27 — `results-comment-template.md:1` heading says "step 6 = wave 1 · stage 10 = wave 2" while the file's own title in Contents (`:3–6`) still lists "Comment — human summary" as if it were a second wave-1 comment. Cosmetic.

### ⚪ F28 — `qa-pipeline-code/SKILL.md:199` reuses `SUPERSEDES` (a retired notes token) for file precedence; `:37` and `:303` call `wave1-and-verification.md` "the closing checklist" one line after 0.40 retired "checklist" as a pipeline term. Word choice only.

### ⚪ F29 — `settings.local.json:6–7` still grants `Read(//c/Users/kubas/**)` — the 0.18.0 "narrowed manually by the user" note (`CHANGELOG:1752–1753`) is contradicted by the file; it is user-local and ignored (`.gitignore:46`), so this is a note for the user, not the plugin.

---

## 5. Deletion ledger (2a)

Verdicts: **KEEP** (with one line of proof that something reads it) · **MERGE INTO <file>** · **DEMOTE TO LEGACY** · **DELETE**. "Reads it" = a skill names it, a script imports it, or a run artefact shows it fired. Tracking status is inferred from `.gitignore` (the review snapshot has no `.git`): root `EP-*`, `*.bak`, `.claude/` are ignored and untracked. For DELETE/MERGE the incident-born rule (CHANGELOG entry) that depends on the item is named; where one does, the verdict is KEEP and the fix is to enforce it somewhere cheaper.

### 5a. Files

| File | Verdict | Proof / what is lost |
|---|---|---|
| `CLAUDE.md` | KEEP | Auto-loaded by Claude Code (0.19.4); carries the `git add -A` ban (incident: 84 passwords one command from a commit, 0.13.1). |
| `MAINTAINERS.md` | KEEP | Named by `CLAUDE.md:5`, README:89. Fix F22. |
| `README.md` | KEEP | `verify_plugin.py` check 4 reads it (wiring). Fix census 22. |
| `CHANGELOG.md` | KEEP | `verify_plugin.py` check 1 reads the top heading; it is the plugin's ledger. |
| `.gitattributes` | KEEP | Incident-born (0.30.0: five files rewritten CRLF). |
| `.gitignore` | KEEP; DELETE lines 30, 37, 65, 76, 77 (census 7, 24–26) | Broad rules are incident-born (0.13.1). The five named lines are shapes that can no longer be produced or are covered by `_[!_]*`. |
| `.claude-plugin/plugin.json` | KEEP | Manifest. Fix census 1. |
| `.claude-plugin/marketplace.json` | KEEP | Update signal (`MAINTAINERS:186–190`). Fix census 2. |
| `.claude/settings.local.json` | (untracked) | User-local; F29. |
| `hooks/hooks.json` + `scripts/notify.py` | DEMOTE TO LEGACY (or DELETE) | Nothing in any run artefact or CHANGELOG since 0.19.4 shows a notification fired; opt-in via `QA_PIPELINE_NOTIFY=1`, Claude Code only, and the `Stop`/`Notification` events fire on *every* session end in the profile, not only pipeline runs (`MAINTAINERS:276–278` admits "global to that Claude Code profile"). No incident-born rule depends on it. Lost: a bell. If kept, see §8 (a `SubagentStop`/`Stop` hook that runs `verify_plugin.py --staged` would be worth more). |
| `scripts/verify_plugin.py` | KEEP | Ran today; incident-born (0.36.0: "every defect class it catches actually happened"). §12 lists what to add. |
| `evals/triggering.md` | KEEP; DEMOTE to the seed of a runnable suite | `verify_plugin.py` check 4 reads it; MAINTAINERS step 4 walks it. Every ✅/❌ phrase still exists in a description (checked). Lost if deleted: the only trigger regression test. §8 says how it becomes `claude plugin eval` cases. |
| `fixtures/EP-0000-context.md` | KEEP; fix F3 | MAINTAINERS smoke test; `verify_plugin.py --selftest` lists it as allowed. |
| `COHERENCE-REVIEW-PROMPT.md` | MERGE INTO `docs/reviews/` | A prompt file in the root; `docs/reviews/*-PROMPT.md` is where its siblings live (0.39.0 moved them). |
| `ep-qa-pipeline-interactive.html`, `ep-qa-pipeline-overview.pptx` | MERGE INTO `docs/` (or DELETE) | 3.3 MB of presentation material in the plugin root; on Windows git both match `EP-*` case-insensitively (`.gitignore:22–23` warns about exactly this) so they are probably untracked and invisible. Nothing reads them. |
| `EP-CODE-ACCESS-SETUP.md`, `EP-GDPRFAV-*.md`, `EP-QA-ENVIRONMENT-RECORD.md`, `EP-RC-gdpr-event-scan.md`, `EP-GS-smoke-prod459.xlsx` | DEMOTE TO LEGACY — move to `~/.ep-qa/runs/legacy/` | Untracked (ignored `EP-*`); `verify_plugin.py` check 9 counts them as a WARN; `EP-CODE-ACCESS-SETUP.md` duplicates `bitbucket-access.md` → Local clone (compare its content before moving). |
| `docs/reviews/*.md` (10), `docs/retrospectives/*.md` (5), `docs/specs/*.md` (5) | KEEP | "history, not contract" (`MAINTAINERS:43`); the CHANGELOG cites them by name (0.19.0, 0.20.0, 0.23.0, 0.30.0). |
| `skills/qa-pipeline/SKILL.md` | KEEP | Dispatcher; evals § qa-pipeline; README:40. Fix F21. |
| `skills/qa-pipeline/references/data-locations.md` | KEEP | Named by 11 SKILL.md files ("Where to find inputs" boilerplate). Fix F7. |
| `skills/qa-pipeline/references/environment.md` | KEEP | Named by 9 files; `load-env.sh` implements it. Fix F20. |
| `skills/qa-pipeline/references/open-items-ledger.md` | KEEP | Analyzer §8, code step 0, stage 9, stage 10 name it; six ledgers exist. Fix F14. |
| `skills/qa-pipeline/references/sources-of-record.md` | KEEP | Named by code, CR, API, WEB, results, analyzer; `Source:`/`Clause:` appear in every newest stage report. Add a Contents line (199 lines, none). |
| `skills/qa-pipeline/references/test-runs.md` | KEEP (unexercised) | Named by 8 files. No run has ever created a test run through the pipeline (F2). |
| `skills/task-context/SKILL.md` | KEEP | Docs orchestrator step 1; evals. |
| `skills/task-context/references/output-template.md` | KEEP | `SKILL.md:376,380`. |
| `skills/task-context/references/field-maps.md` | MERGE INTO `SKILL.md` "Task types and fields" | 46 lines after 0.40 collapsed it to one table; `SKILL.md:241–243` already says "one table for all types". A nine-row table does not need its own file and a "Do not reopen the field maps every time" rule (`:244–245`). Zero behaviour change. |
| `skills/requirements-grooming/SKILL.md` + `references/output-template.md` | KEEP | Step 2; template named `:332`. |
| `skills/qa-test-cases/SKILL.md` | KEEP | Step 4. Fix census 11. |
| `…/references/check-decomposition.md` | KEEP | `SKILL.md:112,219,309`; 0.40 folded stage 3 here. |
| `…/references/test-case-design-rules.md` | KEEP | `SKILL.md:172,220`. Fix census 10. |
| `…/references/combinatorial-testing.md` + `scripts/generate_pict_cases.py` | KEEP (no run evidence) | `SKILL.md:193–194`. No run artefact shows a `Model:` line or PICT use (grep across the 50 staged files: none). Not dead — pairwise only fires on 3+-parameter REQs — but unproven since 0.8.0. |
| `…/references/output-template.md`, `test-cases-example.md` | KEEP | Template `:305`; example is the fixture's expected output (F3). |
| `skills/pr-summary/SKILL.md`, `references/output-template.md` | KEEP | Step 5. |
| `skills/pr-summary/references/bitbucket-access.md` | KEEP | Shared by pr-summary + code-review (`MAINTAINERS:232`). Fix F4, F9. |
| `skills/code-review/SKILL.md`, `references/output-template.md` | KEEP | Step 6. Fix F5, F15. |
| `skills/api-testing/SKILL.md` | KEEP | Step 7. |
| `…/references/api-testing-reference.md` | KEEP | `SKILL.md:25`; §11.3 `photoSave` lesson is incident-born. |
| `…/references/absence-check-protocol.md` | KEEP | Binding on 7/8, audited by analyzer §5; incident EP-55701/EP-55715 (0.12.0/0.14.0). |
| `…/references/output-template.md` | KEEP | `SKILL.md:166`. |
| `…/scripts/load-env.sh` | KEEP | `environment.md:60–63`, `api-testing/SKILL.md:38,130`, stage 9 `:338`. Model for F9's fix. |
| `skills/web-testing/SKILL.md` | KEEP | Step 8. |
| `…/references/browser-rules.md` | KEEP; MERGE its tool table with `playwright-executor.md`'s mapping (§7) | `SKILL.md:117`. Fix F11. |
| `…/references/playwright-executor.md` | KEEP; rewrite Evidence and Tool mapping against the current server (§8) | `SKILL.md:112`. |
| `…/references/login-config.md` | KEEP | `SKILL.md:189`. Fix F19. |
| `…/references/output-template.md` | KEEP | `SKILL.md:269`. |
| `skills/web-testing/navigation_paths.json.bak` | DELETE | Ignored (`*.bak`), 14 alpha2 navigation entries from July–August; the live file is at `~/.ep-qa/cache/` (0.39). A `.bak` in a distributable is exactly what 0.39.0 moved out. Lost: nothing (it is a copy). |
| `skills/qa-manual-runsheet/SKILL.md` | KEEP | Step 9. 454 lines — the second-largest body; §7. |
| `…/references/walk-plan-format.md` | KEEP (unexercised) | Named by runsheet, walk, analyzer. No plan exists yet (F2). |
| `…/references/runsheet-format.md` | DEMOTE TO LEGACY (keep only "Status since 0.31.0", Sheet 1 columns, palette, Credentials) | 286 lines for an "on request only" export nobody has requested since 0.31 (no `-runsheet.xlsx` newer than 2026-09-09, and those were pre-walk). Its REJECTED sections are incident-born (0.18.0 finding #15 — keep those four lines). Fix F8 either way. |
| `…/references/provisioning-rules.md` | KEEP | Named by runsheet, absence-check-protocol, results 4c; every trap is incident-born (0.12.0, 0.19.0). |
| `skills/qa-manual-walk/SKILL.md`, `references/walk-session-rules.md`, `references/walk-results-format.md` | KEEP (unexercised) | Stage 10a; zero walks recorded (F2). |
| `skills/qa-manual-results/SKILL.md`, `references/output-template.md` | KEEP | Stage 10b; three `-manual-results.md` written this month. Fix F23. |
| `skills/qa-run-analyzer/SKILL.md` | KEEP | Both orchestrators call it; seven run reports this month. 394 lines; §7. |
| `…/references/output-template.md` | KEEP | Fix census 6. |
| `…/references/status-vocabulary.md` | KEEP | `verify_plugin.py` check 6 reads it; every verdict stage points to it. |
| `…/scripts/reconcile_counts.py` | KEEP | Ran in every run read; self-test gates commits. Fix F6, F7, F14. |
| `skills/qa-pipeline-docs/SKILL.md` | KEEP | Fix census 3–5. |
| `…/references/publish-config.md` | KEEP | `SKILL.md:194–195`; results step 4b. |
| `…/references/qa-service-publish.md` | KEEP; split (§7) | Read by docs step 6, code step 0, stage 9, results. Fix census 18–21, F17. |
| `skills/qa-pipeline-code/SKILL.md` | KEEP | Fix F12, F13. |
| `…/references/run-modes.md`, `wave1-and-verification.md` | KEEP | 0.41 extraction; named `SKILL.md:35–38`. Fix F18. |
| `…/references/results-comment-template.md` | KEEP | Named by code, results, publish-config. |
| `…/references/bug-report-template.md`, `jira-writing-style.md` | KEEP | Fix F1. |
| `…/scripts/extract_archive.py` | DEMOTE TO LEGACY (already) — KEEP | Named by data-locations step 4, run-modes, publish "Legacy formats"; pre-0.33 tickets exist (EP-53978 five passes). Delete when the last pre-0.33 ticket closes. |

### 5b. Mechanisms inside the SKILL.md files

| Mechanism (where) | Verdict | Proof / what is lost |
|---|---|---|
| **Dispatcher** state table (`qa-pipeline`) | KEEP; re-key (F21) | Only entry point that reads ticket state; no run artefact shows it fired (the newest runs were invoked by mode). |
| Session-rename reminder (both orchestrators, 0.7.0) | DELETE | "manual — Claude/skills cannot rename sessions programmatically" (0.7.0); Claude Code has `/rename` now but the reminder is one more line per run with no artefact. Lost: nothing enforceable. |
| Run clock `⏱` (both orchestrators, 0.25.0) | REMOVE (see §6) | Zero `⏱` lines in any of the 50 artefacts (it is chat-only, unverifiable); budgets unchanged since 0.25.0. |
| Recommended settings line "Opus · High · thinking on" (both) | DELETE (or move to README) | Cowork has no per-stage model choice (0.40.0 removed the column for that reason); the orchestrator cannot act on it. |
| Tool-names note (6 skills) | MERGE INTO one line in `data-locations.md` or `CLAUDE.md` | 0.18.1 F1 fix; correct, but six copies of the same paragraph. |
| "Where to find inputs" boilerplate (9 skills) | KEEP as one line; MERGE the parenthesis into `data-locations.md` | 0.26.0 fix ("new chat is not a reason to ask for an upload" — incident: six skills said the opposite). The 4-line parenthesis is identical in 9 places; the pointer is the mechanism. |
| Docs: auto-default grooming / interactive mode | KEEP | 0.9.0; `EP-48506-docs-run-report.md` shows findings presented and skipped. |
| Docs: recon step (0.21.0) | KEEP | `EP-48506-recon.md` exists (13 KB) and grooming consumed it. |
| Docs: "open items → ticket NOW" yes/no | KEEP BUT NARROW | Incident-born (0.18.0 W4); no artefact shows the answer. Fold into the publish preview when the run is < 30 min old. |
| Docs: publish REQUIRED PAUSE + count gate | KEEP | 0.16.0; `EP-48506-docs-run-report.md` shows the recount. |
| Docs: publish-only mode (0.38) | KEEP (unexercised) | Eval arrow depends on it. |
| Docs: "No checkbox tracker" and "No machine-readable archive" explanatory blocks (`qa-pipeline-docs/SKILL.md:219–259`) | MERGE INTO `qa-service-publish.md` → Legacy formats | 41 lines explaining two retired mechanisms in an always-loaded body; the rule is one line ("post nothing but the description"). |
| Code step 0: run-folder resolution + print | KEEP (unexercised) | 0.32; F2. |
| Code step 0: environment check incl. `ALLOWED_HOSTS` | KEEP (unexercised) | 0.39; F9 asks for a git-auth probe here. |
| Code step 0: source register (every mode) | KEEP | 0.28; `-sources.md` in EP-56197, EP-56740, EP-48506, EP-56998 — fired and mattered (EP-56740 r2 "S-2 re-fetched — it changed on 07 Sep"). |
| Code step 0: same-session shortcut | KEEP BUT NARROW (F12) | |
| Code step 0: QA Service reconciliation / scope by `detail.ticket` | KEEP (unexercised) | 0.34. |
| Code step 0: bug-fix mode mini-suite publish + own PAUSE | KEEP (unexercised) | 0.33/0.37; every bug-fix run this month had no connector product for the suite. |
| Code step 0: resume mode + Completeness header | KEEP | 0.17; `EP-48506-run-report.md` "Supersedes the 11:20 verification block" shows a resume. |
| Code step 0: retest mode three tiers + ledger read | KEEP | 0.18.3/0.30; `EP-56740-retest-scope.md`, `EP-56197-retest-scope.md` exist; ledger read is visible in EP-56740 r2 ("ruling R-1 confirmed"). |
| Split runs section | DEMOTE TO LEGACY | With Playwright the code phase is one environment (0.35.0 says so); the section describes a Cowork-extension split no run this month used. Keep two lines. |
| Stage isolation (subagents for 5–7) | KEEP | 0.8.0; `EP-56740-run-report-r2.md` header shows subagent/inline choice recorded. |
| Step 6 count gate | KEEP | Every newest run report cites `reconcile_counts.py` output. |
| Step 6 publication gate (§7) | KEEP | 0.29; EP-56197 r4 post-publish table "Publication safety 8" shows it applied. |
| Step 6 REQUIRED PAUSE (wave 1) | KEEP BUT SPLIT (F13) | Answered "no" 5/5. |
| Step 6 "human summary written, not posted" | KEEP | `-human-summary.md` exists on all five; status DRAFT rule 0.38. |
| Step 7 bug filing (knowledge-base / template) | KEEP | No bug filed this month by the pipeline (all deferred to stage 10 by rule). |
| Step 8 handback | KEEP (unexercised) | 0.18 W1. |
| Step 9 event-authorisation PAUSE | KEEP | `EP-56998-run-report.md:420` "authorised by the user"; incident-born (0.13.0). |
| Post-publish verification | KEEP | Present in seven run reports; caught a real ❌ (EP-56998 "The decisive question is unanswered"). |
| Step 10 deferral paragraph | KEEP | |
| "Between stages" — orchestrator never asserts a product claim | KEEP | 0.19.0; `EP-56998-run-report.md` post-publish "⚠️ Correction recorded. An orchestrator claim made in chat … was wrong" — the rule caught itself. |
| pr-summary Behaviours touched + code-review Unmapped changes | KEEP BUT NARROW (§6) | Fires every run; never decided (29 entries on EP-48506, 6 on EP-56197, 5 on EP-56998, all `Decision —`). |
| pr-summary Blast radius | KEEP | 🟡 on every run; EP-56197 r4 used it to name `AbstractReader.php` (27 readers). |
| code-review Source fidelity (per-case) | KEEP | 0.19/0.28; SPEC-DEFECT appears in 13 artefacts. |
| code-review RE-ROUTE [UI] | KEEP | 7 artefacts carry it. |
| code-review "FAIL from code reading is a CLAIM" | KEEP | Incident-born (6 of 12 wrong, 0.19.0). |
| api-testing provenance gate / Route to web-testing | KEEP | 0.14; EP-48506 api-testing routes 4 cases. |
| api-testing PASS(code) extras + RISK-CR rows | KEEP | EP-48506 api-testing carries RISK-CR-1/2/6. |
| api/web 3-failures escalation | KEEP | 0.8.0; no artefact evidence either way — cheap. |
| web-testing Execution backends rule | KEEP | `Backend:` line present in all four newest web reports (Playwright every time). |
| web-testing navigation memory (Steps 3, 7) | DEMOTE TO WARN | Playwright deep-links; `playwright-executor.md:95–96` calls it "less critical"; the live file has 14 entries, last July–August. Keep one line: "read if present, write on a new path". |
| web-testing PAUSE for login (extension only) | KEEP (dormant) | Backend rule scopes it. |
| web-testing second observation on shared elements | KEEP | Incident-born (16 of 17 false alarms, 0.19.0); `EP-56998-web-testing.md` shows one re-observation. |
| web-testing `Control:` line on negatives | KEEP | Positive-control text present in 3 of 4 newest web reports. |
| web-testing structural checks per page | KEEP (shape changed 0.40, unexercised) | |
| web-testing `-web-evidence.md` §n | KEEP | `EP-56197-web-evidence.md` exists and both WEB FAILs cite it (run report). |
| Stage 9 retest detection PAUSE | KEEP | Incident-born (0.18.3 phantom like / counter at 15). |
| Stage 9 step 2a minimum-cards selection + coverage floor | KEEP | 0.19.2 (32→14, 33→8 rows); EP-48506 "62 rows covering all 57 case ids". |
| Stage 9 step 6 suite-corrections preview | KEEP (unexercised) | 0.37. |
| Stage 9 step 7 secret scan | KEEP | 0.13.1; EP-56998 post-publish "All four confirmed `.gitignore`d". |
| Walk: pre-flight, one-card turn, positive-control question, AGENT-RUNS confirm-before-write, BLOCKED re-probe, state file, resume | KEEP (all unexercised) | 0.31/0.37; F2. |
| Results: join by TC id, Covers expansion, RETRACTS first, publication gate, ledger close, 4b handback, 4c fixture retirement, step 5 unfiled bugs | KEEP | Three manual-results files this month; retirement (0.39) unexercised. |
| Analyzer §1–§8 (see §6 for per-flag verdicts) | KEEP | Seven run reports. |
| Analyzer chat-summary format | KEEP | 0.7.0. |
| Statuses: `NOT-TESTABLE (instrumentation)`, `BLOCKED (unverified)`, `SPEC-DEFECT`, `RE-ROUTE [UI]`, `OBSERVATION (no source checked)`, `FAIL REJECTED`, `NOT EXECUTED` | KEEP | All appear in this month's reports. `OBSERVATION` (plain, WEB) — KEEP BUT NARROW: the sourced form has taken over (dozens of uses vs two plain ones in the newest reports); define plain `OBSERVATION` as "sourced form not yet checked" or fold the two. |
| Eval sections (14) | KEEP | Every ✅/❌ phrase verified present in the descriptions it names. |
| Hooks `Stop`, `Notification` | DEMOTE TO LEGACY | See 5a. |

---

## 6. Mechanisms that make things worse (2b)

Evidence base: the five newest complete runs — EP-56197 r4 (09-09), EP-48506 (09-08/09), EP-56998 (09-08), EP-56268 r3 (09-09), EP-56740 r2 (09-10) — plus their ledgers. "Runs checked" names the artefacts read. The skills' own claims were not used as evidence.

| Mechanism | Runs checked | What the artefacts show | Verdict |
|---|---|---|---|
| **Wave-1 REQUIRED PAUSE → status comment** (`qa-pipeline-code` step 6) | all five | Declined every time: "The user ruled "post nothing yet"" (EP-56197 r4), "The user declined the wave-1 Jira write" (EP-56998), "Roman declined the wave-1 status comment at the confirm pause" (EP-56268 r3), "User elected to hold wave 1" (EP-56740 r2), docs publish declined (EP-48506). A pause answered "no" 5/5 is a cost with no decision behind it — and because the run creation shares the same yes (F13), the record was withheld too. | **KEEP BUT NARROW** — decouple the run from the comment; make the comment opt-in ("post the status line? default no"). |
| **Run clock `⏱ Stage n/N`** (both orchestrators, 0.25.0) | all five + all 50 staged artefacts | Zero `⏱` lines anywhere; the mechanism is chat-only, so no artefact can show it ran, and its budgets (docs 8/12/15/5/12, code 8/15/30/25/45/8/10/30 min) have not been touched since 0.25.0 despite 0.40 removing a stage and 0.31 replacing stage 9. A mechanism nobody can verify and nobody recalibrates. | **REMOVE** (or keep the one-line "elapsed" stamp at stage boundaries, no forecast). |
| **`OBSERVATION (no source checked)` + `Source:`/`Clause:` gate** (0.28/0.29) | all five | 3–14 uses per stage report; EP-56740 r2 graded TC-14-class findings as observations instead of defects; EP-56197 r4's top 🔴 carries "Source: register row 9. Clause: *real matches always kept, extras cut off.*"; EP-48506 code-review has 14 sourced observations. Changed outcomes on every run. | **KEEP** — earned its place. |
| **Source register in every mode** (0.28) | EP-56197 r4, EP-56740 r2, EP-48506, EP-56998 | Present on all four; EP-56740 r2 detected a source that changed between rounds ("S-2 re-fetched — it changed on 07 Sep"), which produced ledger OI-5. | **KEEP**. |
| **Count gate / `reconcile_counts.py`** (0.13.2/0.16) | all five | Run on every one; EP-48506: "`reconcile_counts.py EP-48506` reported … 35 ids "MISSING from"" drove the 🔴 coverage finding; EP-56197 r4 used it to falsify ledger row #11. | **KEEP** — but F7 means it is currently blind on this machine's layout. |
| **Unmapped changes** (0.18.0 W5) | EP-56197 r4, EP-48506, EP-56998 | 6, 29 and 5 entries; every one became a ledger row with `Decision —`; none decided across rounds (EP-56197 ledger rows 5, 6, 20 carried r3→r4). 29 undecided rows on one ticket is noise that trains the reader to skip the section. | **KEEP BUT NARROW** — cap at the five highest blast-radius entries in the report, list the rest by count; a ledger row only for entries a human ruled on. |
| **Blast-radius 🟡** (0.14/0.18) | EP-56197 r4, EP-48506, EP-56998 | 🟡 on every run; EP-56197 r4 used it substantively (`AbstractReader.php` base class of 27 readers → the only cross-feature regression argument in the run). | **KEEP**. |
| **Carried-item 🔴 (two rounds, no decision)** (0.30) | EP-56197 r4 (5 rows flagged), EP-48506 (0 — first round), EP-56268 r3 | Fired on EP-56197 exactly as designed; three of the five flagged rows are `[Pipeline] risk row` items whose "decision" is a product/PM matter — the 🔴 reaches the run report but nobody outside QA reads run reports. It changed nothing in three rounds. | **KEEP BUT NARROW** — a carried `[Pipeline]` row must name the person and be posted as a one-line question on the ticket at stage 10 (the only human-facing surface), or the flag is decorative. |
| **Ledger row verbosity** (0.30) | all six ledgers | 73 of 122 spec-shaped items exceed 200 chars against "one line"; three column shapes (F14); 0 spec-shaped rows closed (EP-56268's own-shape ledger closes two). A ledger that stage 10 never closes and no script can read is a second run report. | **KEEP BUT NARROW** — enforce the shape and length by script (F14). |
| **BLOCKED needs `Probe:`** (0.18) | EP-56197, EP-48506, EP-56998, EP-56740 api/web | api-testing reports carry `Probe:` lines (2/4/3); web-testing reports carry none as a labelled line but EP-48506-web has "Probes this stage ran…" prose for 12 BLOCKED rows. The rule is followed in substance in API, loosely in WEB. No `BLOCKED (unverified)` in any newest report — either every blocker was probed or the qualifier is not being used. | **KEEP**; make the web template's BLOCKED skeleton carry `Probe:` like the API one (it has `Page state:` instead — `web-testing/references/output-template.md:90–94`). |
| **Second observation before FAILing shared elements** | four web reports | One re-observation recorded (EP-56998); zero FAIL on a shared element in the others, so the rule did not fire. Cheap. | **KEEP**. |
| **Positive control on absence checks** | four web reports, EP-56197 api | Present in 3 of 4 web reports; EP-56998 stage 8 records a positive control for TC-11. Incident-born (EP-55701/55715). | **KEEP**. |
| **Recon step** (0.21) | EP-48506 | `EP-48506-recon.md` (13.5 KB) produced; docs-run-report shows open questions reduced. Only one docs run this month, so one data point. | **KEEP**. |
| **Post-publish verification** | all five | Present on all; on EP-56998 it recorded "❌ The decisive question is unanswered. No stage exercised the code PR #5023 changed" — a real ❌ the analyzer had missed; on EP-56998 it also recorded an orchestrator chat claim as wrong. | **KEEP** — fired and mattered. |
| **Stage-9 event authorisation PAUSE** | EP-56998, EP-48506, EP-56197 r4 | Authorised each time ("authorised by the user"); provisioning wrote 5 entities on EP-56998. Answered "yes" every time — but it is the gate before a live write and 0.13.0/0.39 make it incident-born. | **KEEP** (a yes-every-time gate before a write is a receipt, not theatre). |
| **`Completeness:` header** (0.17) | all stage reports | Present on every one read; EP-56740 r2 marks stages 5–6 "⛔ not executable" instead of hiding them. | **KEEP**. |
| **Session-rename reminder** | — | No artefact can show it; nothing depends on it. | **REMOVE**. |
| **Hooks (`Stop`/`Notification` → notify.py)** | — | Nothing in any run or CHANGELOG since 0.19.4 shows a notification; opt-in never mentioned in a run. | **REMOVE or DEMOTE** (see §8 for a hook that would matter). |
| **Analyzer §4 "not published yet"** (0.40 clarified) | EP-48506-docs-run-report | Reports the expected `not published yet`; the real sync check has never run because no suite-bearing ticket ran the code phase this month. | **KEEP**; it is honest about when it runs. |
| **Analyzer §5 evidence 🔴 "neither reading nor screenshot"** (0.35) | EP-56197 r4 | Fired correctly on the Playwright sandbox limitation (ledger #12) — and the limitation is now stale (§8). | **KEEP**, update the text (census 16). |
| **Analyzer §8 "ledger missing on a retest" 🟡** | EP-56268 r3, EP-56740 r2 | Both retests have a ledger. Did not fire; cheap. | **KEEP**. |
| **`[core]` one-per-REQ rule** (0.23) | EP-48506 test-cases ("57 cases, 17 core"), EP-56998 (🟡 "No `[core]` marker") | Fired as a 🟡 on the bug-fix run where it cannot apply (bug-fix cases have no REQ groups; `run-modes.md:34–43` says TC-1 is core). | **KEEP BUT NARROW** — skip the check in bug-fix mode; the SKILL already says TC-1 is core. |
| **Structural checks → STRUCT cases** (0.33/0.40) | EP-48506 (pre-0.40 checklist, 3 REQ-15 structural checks in the runsheet) | Only pre-0.40 shape seen. | **KEEP (unproven)**. |
| **Verbosity that pushed a finding below the fold** | EP-48506-run-report (34 KB), EP-56197-run-report (48 KB) | Both run reports exceed the human summary by 8–10×; the 🔴 credential exposure on EP-48506 is the fourth 🔴 at line 344 of 420. `open-items-ledger.md:39` asks for one-line items; the analyzer template asks for nothing about length. | **KEEP BUT NARROW** — cap "Issues worth fixing" at 🔴s + five 🟡s in the report body; move the rest to the ledger (which then needs F14). |

---

## 7. Streamlining proposals (2c)

Token estimates use ~4 characters per token. The orchestrator bodies (`qa-pipeline-code` 28.6 KB ≈ 7.1k tok; `qa-pipeline-docs` 15.5 KB ≈ 3.9k tok) load on every phase run; a stage SKILL.md loads once per stage; a reference loads when named. "Behaviour" = what an agent following the text would do differently.

| # | Proposal | Files | Tokens saved per code-phase run (≈) | Behaviour change |
|---|---|---|---|---|
| S1 | **Collapse the nine "Where to find inputs" parentheses to the pointer.** The 4-line parenthesis "(run folder first — a new chat is not a reason to ask for an upload; then the suite; asking the user is the last resort, not the first — Jira archive comments are legacy, read only on pre-0.33 tickets)" is byte-identical in 9 SKILL.md files; the sentence it paraphrases is `data-locations.md:83–108`. Keep "**Where to find inputs:** `../qa-pipeline/references/data-locations.md`." | 9 SKILL.md | ~65 tok × 6 skills loaded per code run ≈ **400** | None — the pointer is the rule; `data-locations.md` "wins" by its own line 5. The 0.26 incident sentence stays in the target file. |
| S2 | **Move the two retirement essays out of the docs orchestrator.** `qa-pipeline-docs/SKILL.md:219–259` (41 lines: "No checkbox tracker comment — retired in 0.34.0 …", "No machine-readable archive — retired in 0.33.0 …") → `qa-service-publish.md` → "Legacy formats" (already exists at :525). Keep one line: "The description is all that is posted; nothing else (`qa-service-publish.md` → Legacy formats)." | qa-pipeline-docs/SKILL.md | ~700 per docs run | None. |
| S3 | **One tool-names note.** Six identical "> **Tool names:** … prefixes vary per install — match by tool name" blocks → one sentence in `CLAUDE.md` (always loaded in Claude Code) and one in `data-locations.md` (always pointed at). | 6 SKILL.md | ~60 × 4 ≈ **240** | None. |
| S4 | **`qa-pipeline-code` step 0 case-source block** (`:139–219`, 80 lines) already ends every bullet with "Full rules: `references/run-modes.md` → …". Cut each mode to its entry condition + pointer (as 0.41 intended) — the retest paragraph alone restates three tiers, the ledger read, the scope file and the suite diff that `run-modes.md:113–175` carries verbatim. | qa-pipeline-code/SKILL.md | ~500 | None if the pointer is followed; the SKILL keeps entry conditions. |
| S5 | **Merge the two browser tool tables.** `browser-rules.md:27–43` (extension tools) and `playwright-executor.md:34–45` (extension → Playwright mapping) describe the same actions from two angles; neither names the actual Playwright MCP tools (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_take_screenshot`, `browser_console_messages`, `browser_network_requests`). One table, three columns (action · extension tool · Playwright MCP tool), in `browser-rules.md`; `playwright-executor.md` keeps Mode, Login, Evidence, Risks. States plainly that `browser-rules.md` is authoritative for interaction, `playwright-executor.md` for evidence and login. | 2 refs | ~200 per web stage | Named change: the Playwright column is new (today an agent guesses tool names). |
| S6 | **Split `qa-service-publish.md` (560 lines) by reader.** Docs publish (Preconditions, Config, Mapping, Suite selection, Procedure, Preview additions ≈ 330 lines) stays; "Code phase — suite as the case source" + "Bug-fix mode" (≈ 75 lines) → `qa-pipeline-code/references/suite-as-source.md`; "Result write-back / Retraction convention" (≈ 80 lines) is already a summary of `test-runs.md` — replace with a 6-line pointer; "Legacy formats" stays. Regenerate Contents (F17). | 1→2 refs | ~1,000 for the code phase (which reads only its 75 lines instead of 560) | None; the moved sections say "the single home is `test-runs.md`" already. |
| S7 | **Rationale out of the always-loaded bodies.** 22 "real run / on one run / historically / measured base rate" paragraphs remain in SKILL.md bodies (`qa-manual-runsheet` 6, `code-review` 4, `requirements-grooming` 3, `api-testing` 3, …); each is 2–5 lines. Rule: one clause inline ("— nine wrong blockers dissolved on one probe each"), story in the reference or CHANGELOG (the 07-30 audit F10 recommendation, applied to the orchestrator in 0.41 only). | 8 SKILL.md | ~600 across a full code run | None — the rules stay; the anecdotes move. |
| S8 | **`qa-manual-runsheet/SKILL.md` (454 lines)**: "The six rules that make a card usable" (`:182–226`) and "Traps that produce false passes" (`:228–244`) restate `walk-plan-format.md` voice rules and `provisioning-rules.md` traps, both of which the SKILL requires reading (`:230`, `:366`). Keep the six rule headings (one line each) and the pointer. | 1 SKILL.md | ~700 per stage 9 | None. |
| S9 | **`results-comment-template.md` "The retired archive (0.33.0)" (`:26–65`, 40 lines)** explains a retired mechanism at length in a template read at every step 6 and stage 10; the surviving rules (`:40–57`, the target table + retraction exception) are 18 lines. Move the explanation to `wave1-and-verification.md` → "Why no archive comments" (already there, `:26–44`). | 1 ref | ~300 | None. |
| S10 | **Version tokens as control flow** (F24): 48 in SKILL bodies. Replace "since 0.33.0 …", "(0.42.0)", "retired in 0.34.0" with plain present tense; one "Legacy formats" section holds the dates. | 14 SKILL.md | ~150 | None. |
| S11 | **`field-maps.md` → SKILL.md** (5a). | 1 ref | ~0 (loaded rarely) | None. |
| S12 | **Run clock + session-rename** removal (§6). | 2 SKILL.md | ~450 per run (docs 150 + code 300) | Named change: no forecast lines in chat. |
| S13 | **Two files describe the same artefact from two angles without saying which is authoritative:** `runsheet-format.md` (rendering spec, 286 lines) vs `walk-plan-format.md` (plan spec, 231 lines). The first says "rendered from the plan" (`:14`) but then prescribes cell content (`:61–84`, F8). State on line 1 of `runsheet-format.md`: "This file governs column layout and palette only; every word in a cell comes from the plan." | 1 ref | ~800 per stage 9 (after §5a's demotion) | None once F8 is applied. |

Top five by tokens per run: **S6 (~1,000) · S8 (~700) · S2 (~700 docs) · S7 (~600) · S4 (~500)** — roughly 3.5k tokens off a code-phase run's fixed load (≈12–15% of what the orchestrator + its references cost before any stage report is read), with zero behaviour change except the two named.

---

## 8. Currency table (Part 3)

Checked today against the live docs (code.claude.com/docs — skills, hooks, plugins-reference, plugin-marketplaces, sub-agents, mcp), the Playwright MCP README on `main`, the QA Service connector's tool list in this session, and 2025–26 QA-methodology sources (ISTQB CT-GenAI v1.0, MoT, arXiv 2606.09863 on false success, mutation-testing-of-LLM-tests write-ups). Each row names the file that would change.

### 8a. Claude Code plugin & skill conventions

| Item | Today | Verdict | What changes |
|---|---|---|---|
| Skill frontmatter: only `name` + `description` used | Docs list `allowed-tools`, `disallowed-tools`, `context: fork`, `agent`, `model`, `effort`, `disable-model-invocation`, `user-invocable`, `paths`, `hooks`, `metadata`, `license`, `compatibility` | **ADOPT NOW** — `disable-model-invocation: true` on `qa-pipeline-code`, `qa-pipeline-docs`, `qa-manual-results` (they write to production systems; the user should invoke them or the dispatcher should — the dispatcher is the model-invocable front door). `allowed-tools` on `requirements-grooming` and `qa-test-cases` (they "do not go to the tracker … do not inspect code": deny `mcp__Atlassian*`, `Bash`) — turns a prose rule into an enforced one. `context: fork` + `agent: general-purpose` on `pr-summary`, `code-review`, `api-testing` replaces the hand-written "Stage isolation" paragraph (`qa-pipeline-code/SKILL.md:255–272`) with a platform mechanism. Low risk: no incident-born rule weakens; the orchestrator's "resolve pauses before dispatch" sentence stays. |
| `disable-model-invocation` for the docs/code orchestrators | absent | ADOPT NOW (above) — also fixes the eval concern that "run the QA checks" might fire the wrong skill. |
| Hooks: `Stop` + `Notification` → bell | 30+ events exist; `PreToolUse` with matcher `Bash` and a decision JSON can deny | **ADOPT NOW** — replace the notify hook with a `PreToolUse` hook (matcher `Bash`) whose script denies `git add -A`, `git add .` and any `git commit` while `verify_plugin.py --staged` fails (≤40 lines; the script already exists). This is the enforcement `CLAUDE.md:11–13` and MAINTAINERS step 6 ask for in prose, and it is Claude Code only exactly like today's hook. No `PreCommit` event exists; `PreToolUse` on the Bash tool is the documented route. |
| Runnable evals | `claude plugin eval` exists (early access, YAML+markdown cases under `evals/`, graders `regex|tool_used|tool_order|file_exists|llm|baseline`, `--json` report); `skill-creator` plugin generates `evals/evals.json` with trigger and near-miss cases; `/skill-doctor` reports never-invoked skills | **CONSIDER** — spike: convert the 14 sections of `evals/triggering.md` into `evals/<skill>/prompt.md` + a `tool_used` grader per ✅ line and a negative grader per ❌; run once. Early access may not be enabled for this org — check first; if not, keep the hand-walk and add the near-miss discipline ("queries that share keywords but need something different") which the current ❌ lines only partly follow. |
| Plugin manifest fields | `homepage`, `repository`, `license`, `displayName`, `userConfig` exist | ADOPT NOW — `license` (none declared anywhere; see §9's licence discipline), `repository`. `userConfig` could prompt for `EP_QA_HOME` on install instead of the MAINTAINERS migration paragraph — CONSIDER. |
| Sub-agent definitions (`agents/*.md` with `tools`, `model`, `maxTurns`, `memory`) | plugin has none; stages are dispatched by prose | CONSIDER — a `agents/qa-stage-runner.md` with `tools` restricted to Read/Write/Bash/Bitbucket would make "Subagents cannot ask the user" (`:266`) a property rather than a warning. |
| MCP names `mcp__<server>__<tool>`; `allowed-tools` accepts `mcp__.*` patterns | skills use bare names + a mapping note | KEEP the bare-name convention (0.18.1 decision; server prefixes differ between Cowork and Claude Code — `mcp__QA_Service__…` here vs `mcp__remote-devices__playwright__…` for the browser) — but the note should give the two observed prefixes as examples. |
| Skill line budget < 500 | met everywhere (max 498) | KEEP; S4/S8 give headroom. |
| Descriptions ≤ 1024; `when_to_use` exists; combined truncation at 1,536 | `qa-manual-runsheet` 1013, `qa-pipeline-code` 995, `qa-manual-walk` 965 | ADOPT NOW — move the "Do NOT use …" clauses into `when_to_use` (a separate field) so descriptions drop under ~700 and the next edit does not overflow. |

### 8b. The QA Service connector

118 tools exposed; the skills name 39. Relevant unused tools and what each duplicates or closes:

| Tool(s) | Duplicated hand-rolled mechanism / gap closed | Verdict |
|---|---|---|
| `discover_tests {suiteId, pathPrefixes, apply}`, `link_implemented_tests`, `plan_link_tests`, `list_repositories`, `register_repository` | `bitbucket-access.md:139–141` "check whether a test already exists for the changed path (… `git grep`)" and EP-48506's 180-second `git grep` timeout (ledger row 32). The server's own instructions: "`discover_tests {suiteId, pathPrefixes: [the files the PR touched]}` previews and writes nothing". code-review could ask which suite cases the PR's own tests already implement, and pr-summary's Behaviours-touched could be joined to implemented cases. | **ADOPT NOW** in `code-review/SKILL.md` "Closing step" as a read-only preview (never `apply: true` without the yes). |
| `get_suite_tree` | `qa-service-publish.md:349–351` folder-distribution check ("no case in "General", no folder over ~10") done by reading `get_suite`. | ADOPT NOW — one tool call replaces arithmetic. |
| `coverage_report`, `product_coverage`, `get_coverage` (named once) | Analyzer §4 "in sync" by hand-counting `detail.ticket` items; README:74 "coverage is a query rather than a claim". | ADOPT NOW in analyzer §4: report `coverage_report` alongside the file counts. |
| `get_release`, `list_releases` (named once) | `test-runs.md:47–51` `releaseId` from `fixVersion` — the lookup is described but no tool call is named for reading the release's checklist (`ensure_release_checklist`). | CONSIDER. |
| `list_uat_runs`, `get_uat_run` | The service has a first-class UAT-run object. The walk (stage 10a) keeps its own `-walk-state.json` and hands verdicts to stage 10b. If a UAT run can hold per-card human verdicts with a principal, the walk's state file could be the service's record instead of a JSON nothing else reads. | **CONSIDER** — spike: read the help topic for UAT runs; if per-case manual verdicts with resume exist, the 0.31 state file becomes a cache. Do not adopt blind: 0.37's "the state file can rebuild the results file" is incident-born (EP-56197 #24). |
| `list_help_topics`, `get_help_topic`, `get_authoring_skill` | `qa-service-publish.md` carries the controlled vocabularies (`levelText`, `status`, kinds, techniques) as constants calibrated in July (0.10.2/0.11). The server documents itself; a vocabulary drift would silently zero the dashboards again. | ADOPT NOW — one line in the publish Procedure: "read `get_help_topic "test case fields"` once per run and diff against the Mapping table; on drift, pause". Keep the table (it carries the incident rationale). |
| `start_generate_test_cases`, `start_collect_requirements`, `start_import_docs` | Service-side generation competes with stages 2–4. | **REJECT** for the pipeline's cases: the pipeline's cases carry `AC-n` provenance, `[core]`, channel tags and the grounding rule; 0.10.4 recorded that `summarize_requirement` destroyed pipeline text, and `qa-service-publish.md:240–247` marks these UNVERIFIED on populated suites. Keep the prohibition. |
| `sync_ci_report`, `ci_run_status`, `backfill_ci_reports`, `sweep_ci_dispatches` | No CI stage exists; `EP-56197` ledger #21 ("no CI status of any kind") was discovered by curl. | CONSIDER — a read-only `ci_run_status` line in pr-summary's header. |
| `search` | Dispatcher and task-context find the suite by `list_suites` + keyword matching (`task-context/SKILL.md:130–133`); the server instructions name `search` first. | ADOPT NOW — `search` before `list_suites`. |
| `remove_run_cases`, `untag_case`, rename/move folders, `merge_duplicate_case`, `delete_*` | Forbidden or unneeded by rule. | KEEP forbidden (0.37). |

### 8c. Browser and API execution

| Assumption in the plugin | Playwright MCP today (README on `main`, 2026-09-10) | Verdict |
|---|---|---|
| `playwright-executor.md:69–71`: "writes only inside its own sandbox root and refuses any other path" → screenshot then copy with host tools | `--output-dir <path>` "path to the directory for output files"; allowed roots = output dir ∪ workspace root; `--allow-unrestricted-file-access` lifts it; default `<cwd>/.playwright-mcp` — which is exactly the `.playwright-mcp/` folder with 307 files sitting in the plugin checkout today | **ADOPT NOW** — configure the server with `--output-dir ~/.ep-qa/runs/<KEY>/r<N>/evidence` (or at least `~/.ep-qa/cache/playwright`) in the MCP config; rewrite Evidence step 1; delete the "copy with host-side file tools" clause; add `.playwright-mcp/` to the tree check in `verify_plugin.py` (it is git-ignored but it is 307 files of screenshots inside the distributable — the 0.39 principle). |
| Tool mapping in Python-API terms (`page.goto`, `get_by_role`, `locator.fill`) | Tools are `browser_navigate`, `browser_snapshot` ("better than screenshot"), `browser_find` (cheaper than a full snapshot), `browser_click` (ref or selector), `browser_type`, `browser_fill_form`, `browser_take_screenshot` (`filename`, `fullPage`, `type`), `browser_console_messages` (`level`, `all`), `browser_network_requests` / `browser_network_request` (full body by index), `browser_evaluate`, `browser_run_code_unsafe` (RCE-equivalent — gate it), `browser_wait_for` (`text`/`textGone`) | ADOPT NOW — S5's three-column table with the real names; `browser_wait_for textGone` is the absence-check wait the protocol needs (`absence-check-protocol.md:89–96`); `browser_snapshot filename:` is the "documented equivalent" `-web-evidence.md` asks for, machine-written. |
| "trace if available" | Tracing only with `--caps=devtools` (`browser_start_tracing`/`stop_tracing`; `--save-trace` no longer exists) | CONSIDER — enable `devtools` cap; a trace per FAIL is stronger evidence than a screenshot and lands in `output-dir/traces`. |
| "Persist auth state per host when the MCP supports it" | Default persistent profile per workspace (`~/.cache/ms-playwright/mcp-…`), or `--isolated` + `--storage-state <file>`; `--caps=storage` adds `browser_storage_state` / `browser_set_storage_state` | ADOPT NOW — one storage-state file per host under `~/.ep-qa/cache/`, loaded at launch; the Login section then applies only when the state is absent or expired. Note the persistent-profile default changes what "fresh session" means — the same objection the SKILL raises against the built-in browser (`web-testing/SKILL.md:121–125`) applies to Playwright's default; use `--isolated`. |
| No mention of network evidence | `browser_network_requests` is core (no cap) | ADOPT NOW — the evidence bundle for a FAIL = a11y snapshot (`browser_snapshot filename`) + screenshot + `browser_network_requests filter:` for the case's endpoint. This closes the "screenshot as proof" failure mode in §8d. |
| `--caps=testing`: `browser_verify_element_visible`, `browser_verify_text_visible`, `browser_verify_value`, `browser_generate_locator` | absent from the plugin | **CONSIDER** — machine-checked oracles for structural checks (`REQ-N/struct-k` "label reads X" → `browser_verify_text_visible`). Spike on one ticket's STRUCT cases. Do not use for absence checks (they verify presence only; the positive-control rule stands). |
| Host allow-list | `--allowed-origins`/`--blocked-origins` exist ("does not serve as a security boundary"); `--allowed-hosts` is the server bind check, not a page allow-list | CONSIDER — pass `ALLOWED_HOSTS` through as `--allowed-origins` as a belt to the 0.39 braces; keep the pre-navigation check (it is the incident-born one). |
| Extension fallback | Playwright MCP itself has `--extension` (connect to the user's running Chrome via the Playwright Extension) and `--cdp-endpoint` | CONSIDER — the "third browser" problem 0.35 named could collapse to one server with two modes; the Claude in Chrome extension path then becomes the fallback of last resort. |
| API harness | curl via `load-env.sh`; no schema/contract check | REJECT changing the harness: the reference's §5 envelope + §6 route probing are incident-born (`photoSave`, 0.6.0/§11.3) and the connector's `api-test-suite`-style generators surveyed in §9 add nothing here. One ADOPT: record request+response pairs to `<KEY>-api-evidence.json` as EP-56740 r2 already did off-book (216 KB file exists) — make it the template's `Evidence:` line like web-testing's. |

### 8d. QA methodology — LLM test-artefact failure modes against the pipeline

| Practice / failure mode (source) | Encoded? | Where / what would change |
|---|---|---|
| Hallucinated oracles — invented expected results (ISTQB CT-GenAI §3.1.1; arXiv 2607.10277 "should not rely on LLM-generated oracles as a substitute for manually reviewed assertions") | **Yes** | `qa-test-cases/SKILL.md:199–207` grounding rule; `sources-of-record.md` §3 gate; bug Expected = register clause (0.38). Nothing to add except F1 (the style guide contradicts it). |
| Verdict inflation / false success — agent claims done, state disagrees (arXiv 2606.09863: 75.8% for coding agents with explicit status claims; "assert on concrete evidence, never on self-assessment") | **Yes, strongest in the field** | "FAIL from code reading is a CLAIM" (`code-review:330–337`), two-wave publish, `Completeness:` header, post-publish re-read ("re-read, don't assume"). Partial gap: the machine PASS is still the model's own reading of a snapshot — `browser_verify_*` (8c) would make PASS a tool result, not an opinion. |
| Self-grading bias (arXiv 2604.22891 "Machiavellian Judges") | Partial | The analyzer is the same model re-reading its own reports in the same run (09-07 §4.8's point; `qa-run-analyzer/SKILL.md:241–249` admits the publish "verifies itself"). What changes: run the analyzer as a `context: fork` sub-agent with `model: sonnet` or a cold prompt — a different context is the cheapest independence. |
| Over-confident absence checks — no source states the "positive control" rule verbatim; nearest is the false-success taxonomy ("read-heavy patterns without writes") | **Yes — ahead of the field** | `absence-check-protocol.md` (0.14); walk's BLOCKED-not-FAIL on a failed control (0.37). Protect it (§9 inverse list). |
| Requirement paraphrase drift / unsubstantiated coverage claims (MoT club thread; CT-GenAI HO-2.2 "verifies that each acceptance criterion is covered") | **Yes** (0.42) | AC ledger + `reconcile_counts.py` set difference. Gap F6: unreadable in retest mode. |
| Coverage theatre — many cases, same partition; mutation score as the honest metric (augmentcode mutation guide; MoT "regression bloat") | Partial | EP one-per-class rule (`test-case-design-rules.md:107–110`) and "structural check dressed as a scenario" anti-pattern. Missing: nothing measures whether a case would catch a fault. What changes: `code-review` could grade each PASS with "which line, if reverted, would make this case fail" — the mutation question as a one-line field on High-risk cases only. CONSIDER. |
| Tautological/mocked-away assertions (qaskills 2026 checklist) | N/A | The pipeline does not write automated tests; `pr-summary`'s "does a test already exist" is where `discover_tests` (8b) lands. |
| Flaky handling — "retries are a treatment, not a cure"; quarantine with ticket + max age; classify timing/data/infra/non-determinism/ordering (scrolltest 2026; petrkindlmann `test-reliability`) | Partial | `test-runs.md:95–96`: "`flaky` is never written by the pipeline: a verdict that changed between two reads is a `blocked` with both reads in the note, or a defect." Sound. Missing: a classification of *why* two reads differed (EP-56197 r4 found the environment redeployed mid-run — ledger #23 — and had no status for "environment moved"). What changes: `status-vocabulary.md` gains one qualifier `BLOCKED (environment changed)` with the two build ids in the note; analyzer 🟡 when any host's build id changed between the run's first and last request. |
| Screenshot-as-proof (Playwright's own "use browser_snapshot for actions … better than screenshot") | **Yes** (0.35 `-web-evidence.md` DOM reading) | Make the reading a `browser_snapshot filename:` output (8c). |
| Prompt injection through page/ticket content (Unit 42 2026; OWASP LLM01) | **Yes** | `task-context/SKILL.md:43–50`, `browser-rules.md:19–23`. Gap: `pr-summary`/`code-review` read PR descriptions and code comments with no equivalent sentence; `qa-manual-walk` reads tester-pasted text (redacted for secrets, not for directives). Add the one sentence to both. |
| Defect triage — severity × likelihood, dedup before advancing, reproducibility gate (TestMu 2026; GitHub duplicate detection) | **Yes** | Risk rating at grooming; `bug-report-template.md:15–21` duplicate search; run-filed defects dedup by stable id (`test-runs.md:144–147`). |
| Regression scoping by blast radius / test-impact analysis (Datadog TIA, Launchable, MoT 98% cut) | Partial | Three-tier retest scope (`run-modes.md:122–129`) and blast-radius flag are judgement-based; there is no per-case "files this case exercises" map, so tier 2 cannot be computed. What changes: `discover_tests` + `link_implemented_tests` (8b) give the suite a case↔path map for the automated cases; for pipeline cases, `code-review` already writes file+line per verdict — write it as a `Touches:` line the retest scope can grep. CONSIDER. |
| Evidence standards — evidence = DOM text + screenshot + network; traces for failures | Partial | DOM + screenshot yes; network no (8c). |
| Human-in-the-loop — ask one thing at a time with a recommended default; only the human-only input (fugazi grill-me-qa; mattpocock "confirm seams with the user") | **Yes** | The walk's one-card-one-question and AGENT-RUNS "the tester supplies only what a human can" are the field's best version of this (§9). |

---

## 9. Field survey — what the best public QA skills do (Part 5)

Fetched live today; star counts read from the repo pages, licences from `LICENSE` files. The ten marked ★ had their `SKILL.md` and references read; the rest were read from README/index only.

### 9a. Candidates

| # | Repo · skill(s) | URL | Stars | Licence | One line |
|---|---|---|---|---|---|
| 1★ | anthropics/skills → `webapp-testing`, `skill-creator` | github.com/anthropics/skills | 168.9k | Apache-2.0 | Anthropic's public skills; Playwright-script toolkit + the eval/trigger-test harness |
| 2★ | anthropics/claude-plugins-official → `code-review`, `pr-review-toolkit`, `playwright`, `hookify` | github.com/anthropics/claude-plugins-official | 36.1k | Apache-2.0 | Official marketplace; `code-review` = 5 parallel reviewers + confidence scoring; `playwright` wraps the MS MCP with no procedure |
| 3★ | obra/superpowers → `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `writing-skills` | github.com/obra/superpowers | 282.6k | MIT | Discipline skills ("Iron Law", rationalization tables) |
| 4★ | mattpocock/skills → `tdd`, `diagnosing-bugs`, `to-spec` | github.com/mattpocock/skills | 252.6k | MIT | Spec → ticket → TDD → debug loop |
| 5★ | petrkindlmann/qa-skills (50 skills) | github.com/petrkindlmann/qa-skills | 64 | MIT | The only pure-QA library: test-case-management, agentic-browser-testing, ai-bug-triage, test-reliability, bug-reproduction, exploratory-testing |
| 6★ | fugazi/test-automation-skills-agents | github.com/fugazi/test-automation-skills-agents | 217 | MIT | qa-manual-istqb, playwright-regression-testing, grill-me-qa |
| 7 | wshobson/agents → `test-automator`, `api-testing-observability` | github.com/wshobson/agents | ~33k | MIT | Capability-list agents; thin on procedure |
| 8★ | VoltAgent/awesome-claude-code-subagents → `qa-expert`, `ui-ux-tester` | github.com/VoltAgent/awesome-claude-code-subagents | 22.9k | MIT | 100+ subagent prompts; `ui-ux-tester` drives Chrome MCP from documented flows |
| 9 | alirezarezvani/claude-skills → `senior-qa`, `playwright-pro` | github.com/alirezarezvani/claude-skills | 24.8k | MIT | Script generators (coverage analyzer, e2e scaffolder); no QA-process mechanism |
| 10 | davila7/claude-code-templates → `testing/generate-tests` | github.com/davila7/claude-code-templates | 28.2k | MIT | Catalogue; no dedicated QA procedure |
| 11★ | softaworks/agent-toolkit → `qa-test-planner` | github.com/softaworks/agent-toolkit | 2.2k | MIT | Test plan / TC / bug / run-report templates |
| 12★ | danashby/Exploratory-Testing-Skill | github.com/danashby/Exploratory-Testing-Skill | 1 | MIT | Heuristic catalogue (FEW HICCUPPS, SFDIPOT, RCRCRC, RIMGEA) + MCOASTER report |
| 13 | jeremylongshore/claude-code-plugins-plus-skills | github.com/jeremylongshore/claude-code-plugins-plus-skills | 2.7k | MIT | 471-plugin marketplace, 28 "Testing" plugins (not read) |
| 14 | hesreallyhim/awesome-claude-code | github.com/hesreallyhim/awesome-claude-code | 53.1k | CC BY-NC-ND 4.0 | Curated list — cite only, never lift text |
| 15 | ComposioHQ/awesome-claude-skills | github.com/ComposioHQ/awesome-claude-skills | 74.4k | Apache-2.0 | Curated list; QA entries = webapp-testing, pypict, superpowers TDD |
| 16★ | PramodDutta/qaskills (qaskills.sh) | github.com/PramodDutta/qaskills | 199 | MIT | QA-only directory (test plan, bug report, Playwright API) |

Licence discipline: everything proposed for lifting below is MIT or Apache-2.0 (attribution + licence text). `hesreallyhim` is NC-ND — cite, do not reuse. This plugin declares **no licence** (`plugin.json` has no `license` field, no `LICENSE` file) — add one before lifting anything.

### 9b. Mechanisms, judged against this plugin

**ALREADY HERE**

| Mechanism (source) | Where this plugin does it | Does the public version do it better? |
|---|---|---|
| "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE … If you haven't run the verification command in this message, you cannot claim it passes." (superpowers `verification-before-completion/SKILL.md`, MIT) | Post-publish verification "re-read, don't assume"; code-read FAIL is a CLAIM; two-wave publish | No — this plugin's is stronger (a *record* withheld, not just a claim). |
| "Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec." (mattpocock `tdd/SKILL.md`, MIT) | Grounding rule; `Source:`/`Clause:` gate; bug Expected = register clause | Equivalent; theirs is one sentence — S7 could borrow the brevity. |
| "An expected result must be deterministically checkable. A second human (or a machine) must be able to agree on pass/fail without guessing." + "Link to the requirement at creation time, not as a back-fill" (petrkindlmann `test-case-management/SKILL.md`, MIT) | `check-decomposition.md` Unambiguity; `Covers: AC-n` at creation (0.42) | Equivalent. |
| "The oracle lives outside the agent. Never let the LLM self-grade 'looks good.' … VERDICT: harness emits {"passed": true|false}; the LLM does not decide." (petrkindlmann `agentic-browser-testing`) | Partially: `Control:` line, DOM reading, count gate | **Theirs is better on the browser PASS** — the machine PASS here is still the model's reading. `browser_verify_*` (8c) is the route. |
| Flaky quarantine DETECT→TAG→ISOLATE→DIAGNOSE→FIX→VERIFY(50×)→RELEASE, max age 14 days, ticket per entry (petrkindlmann `test-reliability`) | `flaky` never written; changed reads → `blocked` with both reads | Theirs is a full protocol for automated suites; not a fit for a human-in-the-loop pipeline beyond the one qualifier proposed in 8d. |
| "One question at a time… Provide a recommended answer for every question… Explore before asking" (fugazi `grill-me-qa`, MIT) | Walk: one card, one question; recon before asking BEHAVIOUR questions (0.21) | Equivalent; theirs adds "recommended answer" — see ADOPT. |
| Charter "Explore [target] with [resources] to discover [information]"; "A bug you can't reproduce is a note, not a filed defect." (danashby, petrkindlmann `exploratory-testing`) | `OBSERVATION (no source checked)`; web-testing "Additional checks (exploratory)" | Equivalent in effect. |
| Router skill + "Not for:" exclusions (petrkindlmann `qa-do`: "Output at most two skills"; fugazi "Do NOT Use For") | `qa-pipeline` dispatcher; "Do NOT use" clauses in every description (0.18.2) | Equivalent. |
| Lean SKILL.md + `references/` + "read X first" (anthropics skill-creator: "Keep SKILL.md under 500 lines"; superpowers writing-skills: "Frequently-loaded skills: <200 words total") | Progressive disclosure throughout | Superpowers' 200-word budget for always-loaded skills is far stricter than this plugin's 5–7k-token orchestrators — see S1–S12. |
| Eligibility gate first and last (official `code-review`: PR "(a) is closed, (b) is a draft … (d) already has a code review from you") | Dispatcher state read; stage-9 retest detection | Equivalent. |
| Cite and link every finding (official `code-review`: "You must cite and link each bug" with full-sha permalinks) | file+line on every FAIL; `Source:`/`Clause:` | Equivalent; permalinks to Bitbucket would be an ADOPT if the reports ever leave the run folder. |

**ADOPT** (lands in a named file; none weakens an incident-born rule)

| Mechanism (source, licence) | Lands in | What it replaces/adds | Why no incident rule weakens |
|---|---|---|---|
| **Self-lint on own output by grep**: "`grep -niE "verify it works|looks right|is fine|wait a bit|no problems|everything works" cases.*` must return nothing." with a lint table `Step # | Smell(s) | Original expected | Rewritten action | Rewritten expected` (petrkindlmann `test-case-management/references/linting.md`, MIT) | `qa-test-cases/SKILL.md` "Verification before saving" + 10 lines in `reconcile_counts.py` (`forbidden=N` with the offending lines) | The forbidden-word list already exists in prose (`check-decomposition.md:76–86`, `test-case-design-rules.md:91–94`); today nothing counts them. Mechanises an existing rule. | Adds enforcement only. |
| **Confidence-scored findings with a hard filter**: "Filter out any issues with a score less than 80. If there are no issues that meet this criteria, do not proceed." and the explicit false-positive list ("Pre-existing issues… Issues that a linter… would catch… Real issues, but on lines that the user did not modify") (official `code-review`, Apache-2.0) | `code-review/references/output-template.md` Risks section: one `confidence:` (0/25/50/75/100 with the official rubric wording) per `RISK-CR-n`; api/web chase rows ≥ 75 only | Today every risk row is chased or carried; EP-48506 had six, EP-56197 four, with three carried three rounds. A confidence score is the missing input to "decide or execute". | Strengthens 0.17.0's risk rows; does not touch FAIL handling. |
| **Recommended answer on every question to the human**: "Provide a recommended answer for every question" (fugazi `grill-me-qa`, MIT) | `qa-pipeline-docs/SKILL.md` grooming-questions comment; `qa-pipeline-code` retest-scope confirmation ("decide or carry each") | The 10 undecided EP-48506 ledger questions and the 3 EP-56197 rows carried three rounds all lack a proposed default; a question with a recommended answer gets answered. | Adds text to a pause; changes no gate. |
| **Regression-test proof by revert**: "Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)" (superpowers `test-driven-development`, MIT; also petrkindlmann `bug-reproduction`: "Green isn't done — revert-to-verify is") | `run-modes.md` Bug-fix mode, TC-1 | For the reproduction case only: when a local clone exists, `git stash`/checkout the base and confirm TC-1 FAILS there before it PASSES on the fix branch. EP-56998's 🔴 "The fix was never executed. Zero runtime coverage" is the failure this catches. | Adds a read-only check inside the existing read-only rule (`code-review:80–81`); execution stays in stages 7–8. |
| **Near-miss negatives in trigger evals**: "negatives must be near-misses — queries that share keywords with the skill but actually need something different" (anthropics `skill-creator/SKILL.md`, Apache-2.0) | `evals/triggering.md` | Half the current ❌ lines are far-misses ("write unit tests for this function", "analyze this log file"); near-misses ("write the test cases into QA Service now" → docs publish-only, not qa-test-cases) are the ones that break. | Eval hygiene only. |
| **Unique debug-log prefix for cleanup**: "Tag every debug log with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep." (mattpocock `diagnosing-bugs`, MIT) | `provisioning-rules.md` Fixtures: every throwaway account/entity name carries the run token (`zz-<KEY>-r<N>-…`) so stage 10's retirement (4c) is one filter | Today `-testdata.json` is the only map; a name prefix survives even when the file is lost. | Strengthens 0.39's retirement rule. |

**ADAPT**

| Mechanism (source) | Adapted form |
|---|---|
| Structured log-fingerprint triage: normalise timestamps/UUIDs/ports → cluster → classify `test bug | application bug | environment issue | flaky test | build failure` + confidence; "No automated action without review. The pipeline suggests; humans decide." (petrkindlmann `ai-bug-triage`) | Different record: apply the five-way class to the walk's BLOCKED reasons and the analyzer's environment findings (EP-56197 #23 "environment moved", EP-48506 #27 "designated environment unreachable") as a `class:` on the ledger row, so §6's carried-item flag can route environment rows to DevOps instead of QA. |
| MCOASTER session report (Mission, Coverage, Obstacles, Audience, Status, Techniques, Environment, Risks) (danashby) | The walk results file already has Summary/Verdicts/Not run/Blocked/Observations; add one `Obstacles` line (what slowed the tester) — it is the only field the tester's experience is recorded in, and 0.31 was born from that experience. |
| "Agentic video receipt" — `screencast.webm` of the repair run (petrkindlmann `test-reliability`) | For AGENT-RUNS cards only: the redacted call + result already shown in ≤5 lines; a Playwright `--caps=devtools` video for the one FAIL a tester disputes. Not for PASSes (evidence-noise rule, `playwright-executor.md:88–89`). |
| Tiered regression (Smoke → Sanity → Selective → Full) with "exactly one [tag] per test" (fugazi `playwright-regression-testing`) | The pipeline has no owned automated suite; the tiers map onto stage 9's card kinds (SPOT-CHECK = smoke, WALK = selective) — already the case. Record the mapping in `walk-plan-format.md` Card kinds; nothing else. |
| Spec template with explicit "Out of Scope" and `ready-for-agent` label (mattpocock `to-spec`) | `requirements-grooming` output has no Out-of-scope section; the fixture context has "Out of scope" but grooming drops it. Add one `## Out of scope (from the ticket)` block to `requirements-grooming/references/output-template.md` so scope rulings (EP-56740 R-1 re-scoping AC#2) have a home before the ledger. |

**REJECT**

| Mechanism (source) | Would break | Rule and CHANGELOG entry |
|---|---|---|
| Service/LLM-generated test cases from requirements (`start_generate_test_cases`; alirezarezvani suite generators) | Provenance: cases without `AC-n`, `[core]`, channel tags, grounding | 0.42.0 AC ledger; 0.23.0 two-tier coverage; 0.10.4 `summarize_requirement` incident |
| Release verdict by threshold "PASS: All P0 tests pass, 90%+ P1" (softaworks `qa-test-planner`) | A percentage verdict is exactly what 0.19.0 G and 0.30.0 removed: a human confirms every verdict; machine PASSes are provisional | 0.19.0 "ACCEPTED — G (two-wave publish)"; 0.30.0 "what stays `not_run` in wave 1" |
| Auto-repair of failing tests with confidence bands (≥0.9 auto) (petrkindlmann `test-reliability`) | The pipeline edits no product code and no product tests; "Never edit the plan to make a case pass" | 0.31.0 walk rules; 0.37.0 "Never delete" |
| Retry-on-flake defaults (Playwright `retries: 2` in fugazi/petrkindlmann configs) | A verdict that changed between reads is a `blocked` with both reads or a defect — never averaged | 0.30.0 `test-runs.md:95–96` |
| Percent-coverage claims in summaries (softaworks coverage matrix "%"; VoltAgent "14/14") | `executed_coverage` "reported as two numbers — machine and manual — never one percentage" | 0.30.0 `test-runs.md:208–210` |
| Persona-style capability lists (wshobson, VoltAgent `qa-expert`) | Nothing to break — no mechanism to lift | — |

### 9c. Direct competitor in shape?

None of the sixteen chains ticket → requirements → cases → PR review against cases → API + browser execution → human walk → write-back with retractions. The closest partials, side by side:

| Capability | ep-qa-pipeline | petrkindlmann/qa-skills | fugazi qa-manual-istqb | softaworks qa-test-planner | official code-review |
|---|---|---|---|---|---|
| Ticket → requirements with ids | AC ledger (0.42) | story/AC → cases (no ledger) | test basis → conditions | ANALYZE stage | — |
| Cases with technique + grounding | yes (`[core]`, channel, `[risk]`) | yes (deterministic oracle, lint) | yes (ISTQB techniques) | templates | — |
| PR review **against the cases** | yes (stage 6, RE-ROUTE, SPEC-DEFECT) | — | — | — | review of the PR, not against cases; confidence scoring |
| API execution with write-safety | yes | (harness contract) | — | — | — |
| Browser execution with evidence rule | yes (DOM + screenshot) | yes (harness verdict, a11y first) | Playwright scaffold per TC id | — | — |
| Human round | guided walk, agent runs API cards | — | manual templates | manual | — |
| Record write-back | QA Service run, machine/manual principals, retractions | TestRail/Xray/Zephyr/Qase, coverage gaps | traceability CSV | — | — |
| Cross-round memory | open-items ledger | — | — | — | — |
| Source-of-record gate | yes | (requirement link at creation) | traceability red flag | — | — |
| Self-check on own output | verification sections, count gate | grep lint | — | VALIDATE stage | eligibility re-check |
| Runnable evals | hand-walked | — | — | — | — |

### 9d. What this plugin does that none of the surveyed skills do — protect these during any adoption

1. **Explicit RETRACTIONS of published verdicts, posted where the wrong verdict was published** (`test-runs.md` → Retraction target rule; `qa-manual-results` "the most important rows of this stage"). No surveyed skill has a concept of correcting a record it already wrote.
2. **Machine verdicts recorded as provisional (`not_run` for FAIL/PARTIAL) in a system of record before the human round, with the human's principal on the human rows** — the field's best is "don't self-grade"; nobody separates *who* recorded a verdict in the record.
3. **The guided walk with the machine's evidence backstage, AGENT-RUNS cards, and "what happened?" never "did it pass?"** — the only human-in-the-loop mechanism in the survey that is designed around the tester's attention rather than the agent's convenience (fugazi's grill-me-qa is the nearest, for planning not execution).
4. **The open-items ledger across retest rounds** and **the source-of-record gate with an as-built document ranked above the brief** — both born of named incidents (EP-56197, EP-56133) and absent everywhere else.

---

## 10. Prior-review disposition table

Status today for every proposal in `PIPELINE-REVIEW-2026-09-07.md` (§4.x) and `SKILL-BEST-PRACTICES-AUDIT-2026-07-30.md` (F1–F12). "Silently dropped" = neither implemented nor rejected in the CHANGELOG — a finding under `CLAUDE.md:44–45`.

| Proposal | Status | Evidence |
|---|---|---|
| 09-07 §4.1 QA Service run/verdict API | ✅ Implemented 0.30.0 | `test-runs.md`; **but never exercised by a run (F2)** |
| 09-07 §4.2 cross-round ledger | ✅ Implemented 0.30.0 | six ledgers exist; shape drift F14 |
| 09-07 §4.3 retraction target rule | ✅ Implemented 0.30.0 | `test-runs.md:165–188` |
| 09-07 §4.4 `reconcile_counts.py`: scope statuses to `## Results`, `--cases` override, count OBSERVATION bullets, section fixture | ❌ **Silently dropped** | 0.30.0: "Planned for 0.30.1"; no 0.30.1; script still counts any id-first table row (`:171–187`), no `--cases`, no OBSERVATION count; 0.32's folder resolution partly covers `--cases` |
| 09-07 §4.5 Playwright evidence path | ✅ Implemented 0.35.0 | `playwright-executor.md` Evidence; now stale again (8c) |
| 09-07 §4.6 code-review bounded base-branch/dependency reads; Classification lists OBSERVATION; Final answer lists SPEC-DEFECT | ❌ **Silently dropped** | 0.30.0 "Planned for 0.30.1"; `code-review/SKILL.md:82–84,91,119–120` unchanged; F5, F15 |
| 09-07 §4.7 rename `OBSERVATION (no source checked)` → `(no clause found)` | ❌ **Silently dropped after deferral** | 0.31.0: "DEFERRED to the status-vocabulary release with §4.7"; no such release; token unchanged in 14 files |
| 09-07 §4.8 analyzer `--post-publish` mode instead of orchestrator self-check | ❌ **Silently dropped** | 0.41 moved the checklist to a reference; still the orchestrator checking itself (`qa-run-analyzer/SKILL.md:241–249` admits it) |
| 09-07 §4.9 `verify_plugin.py` | ✅ Implemented 0.36.0/0.36.1 | ran today |
| 09-07 §4.10 `.gitattributes` | ✅ 0.30.0 | file exists |
| 09-07 §4.10 `_*` ignore rule | ✅ 0.30.0/0.39.0 | `_[!_]*`; per-name lines still present (census 24) |
| 09-07 §4.10 trailing newlines | ✅ 0.36.0 check 3 | |
| 09-07 §4.10 web-testing description | ✅ 0.35.0 | |
| 09-07 §4.10 analyzer description input list | ⚠ **Partial / not done** | api-testing is listed; manual-results, walk files, sources, evidence are not (F16) |
| 09-07 §4.10 orchestrator rationale → `incidents.md`, < 450 lines | ⚠ Partial | 0.41: 763 → 498 lines via two references; rationale remains in 8 other bodies (S7); 498 ≠ < 450 |
| 09-07 §4.10 trim `qa-pipeline-code` description | ⚠ Not done | 995 chars today (0.33 said 989) |
| 09-07 §5 release plan "0.30.1 — the gate works on retests" | ❌ Never shipped | the four ❌ rows above are its contents |
| 09-07 §2 #6 durable record 🔴 | ✅ 0.30.0 | |
| 09-07 §2 #7 retraction nowhere to land 🔴 | ✅ 0.30.0 | |
| 09-07 §2 #8 statuses harvested from "Not executed here" | ⚠ Moot-but-undocumented | current templates have no status cell in that table, so nothing is harvested; not recorded anywhere |
| 09-07 §2 #10 `[core]` nominations recorded | ✅ 0.30.0 (ledger class `nomination`) | |
| 09-07 §2 #12 retest file naming | ✅ 0.32.0 (folders) | unexercised (F2) |
| 09-07 §3 description↔body drift (web-testing, analyzer) | ✅ / ❌ | web-testing fixed 0.35; analyzer open (F16) |
| 09-07 §3 incident narratives in bodies | ⚠ Partial | S7 |
| 09-07 §3 CRLF churn | ✅ 0.30.0 | |
| 07-30 F1 bare MCP names | ✅ 0.18.1 (mapping note) | six copies (S3) |
| 07-30 F2 broken `../` paths | ✅ 0.18.1; guarded by verify check 5 | |
| 07-30 F3 Contents in 100+ line references | ✅ 0.18.1 for the then-13 files; ❌ **not applied to five newer/grown files**: `sources-of-record.md` (199), `data-locations.md` (142), `status-vocabulary.md` (127), `qa-test-cases/references/output-template.md` (105), `playwright-executor.md` (101) | verified by scan |
| 07-30 F4 cross-skill references | ✅ Recorded deviation; verify check 5 accepts `../` forms | |
| 07-30 F5 web-testing > 500 lines; orchestrator extraction | ✅ 0.20.0; ✅ 0.41.0 | |
| 07-30 F6.1 "manual testing" trigger; F6.2 "Stage 4.5" | ✅ 0.18.1 | |
| 07-30 F6.3 description-opener normalisation | ❌ **Silently dropped** | F25 |
| 07-30 F7 evaluations | ⚠ Recorded deferral (0.18.2 "rigor scales with audience") — still open; platform now has `claude plugin eval` (8a) | |
| 07-30 F8 time-sensitive version conditionals | ❌ **Silently dropped — and regressed** | 48 version tokens in SKILL bodies today vs 3 cited then (F24) |
| 07-30 F9 setup-guide signalling | ✅ Resolved differently — deleted 0.40.0 | recorded |
| 07-30 F10 war-story compression | ⚠ Partial (0.20.0, 0.41.0) | S7 |
| 07-30 F11 `qa-` naming consistency | ❌ **Silently dropped** | no CHANGELOG line; low urgency then and now, but undispositioned |
| 07-30 F12 `navigation_paths.json` at skill root | ✅ 0.39.0 (moved to `~/.ep-qa/cache/`) | a `.bak` copy remains in the tree (5a) |

**Still undispositioned (needs a CHANGELOG line, implement or reject):** 09-07 §4.4, §4.6, §4.7, §4.8; 09-07 §4.10 analyzer description; 07-30 F6.3, F8, F11; run-report items EP-48506 row 30 (`git ls-remote` probe / token exposure), EP-56197 #17 (`NOT-A-DEFECT` token — deferred to a release that never came), EP-56197 #1/#3/#7 (carried `[Pipeline]` risk/scope rows — the analyzer itself says "MAINTAINERS step 1 requires a CHANGELOG answer for each"), EP-56998 #1 ("Build under test unidentifiable" — no mechanism records the deployed build id, and EP-56197 #23 hit the same gap a day later).

---

## 11. What is shipped but unproven (Part 4)

Nothing released after 0.30.0 has been exercised by a run, an eval, an analyzer check on a real artefact, or a run report. Per release, the change and the evidence that would prove it:

| Release | Shipped | Would be proven by | Evidence today |
|---|---|---|---|
| 0.31.0 | `qa-manual-walk`; walk plan / state / results; AGENT-RUNS cards; runsheet as export | one `-walk-plan.md`, `-walk-state.json`, `-walk-results.md` | **none exist** (1,047 files searched) |
| 0.32.0 | `runs/<KEY>/docs/` + `r<N>/`; `reconcile_counts.py` folder resolution | one `r1/` folder | **none exist**; newest run (EP-56740 r2, today) is flat `-r2` suffixed in `runs/legacy/` |
| 0.33.0 | no archive; STRUCT cases; bug-fix mini-suite publish | a suite with `-STRUCT-` cases; a bug-fix run with a roster | no suite-bearing code-phase run since |
| 0.34.0 | `detail.ticket` / `detail.pipelineId` scoping; no tracker comment | a code-phase step 0 scoped by `detail.ticket` | none |
| 0.35.0 | Playwright default; `-web-evidence.md` in the contract; `evidence/` copy | `Backend:` line (✅ present in 4 reports — the one 0.35 item proven by pre-existing practice); an `evidence/` folder (none) | partial |
| 0.36.x | verify gate | its own run | ✅ proven (8 ok today) |
| 0.37.0 | walk BLOCKED-not-FAIL, state schema, confirm-before-write, `Completeness: complete (N declared not run)`, STRUCT stableId join, bug-fix PAUSE, "never delete", stage-9 corrections preview | a walk; a STRUCT verdict on a run | none |
| 0.38.0 | `Arrived as:`; Statistics rows; `Status: DRAFT`; publish-only mode; step-6 order | one stage report with `Arrived as` (grep: none); one `-human-summary.md` with `Status: DRAFT` (none — EP-56740 r2's summary predates) | none |
| 0.39.0 | `EP_QA_HOME`; `ALLOWED_HOSTS` check; secrets-in-chat; throwaway retirement | a run report naming the checked hosts (grep `ALLOWED_HOSTS`: none); a stage-10 retirement | `~/.ep-qa` exists (the migration was done); nothing else |
| 0.40.0 | stage 3 folded; Structural checks section; `struct=` count | a test-cases file with `## Structural checks` | none (EP-48506 is pre-0.40 with a checklist) |
| 0.41.0 | references extraction | no behaviour to prove | n/a |
| 0.42.0 | AC ledger end to end; `detail.ac` | a context file with `AC-n`; `AC coverage:` in statistics; a bug naming `AC-<n>` | none; the fixture cannot produce it (F3); `detail.ac` is never read (F6) |

**Run-report 🔴/🟡 [Pipeline] items from the newest runs with no CHANGELOG disposition** (in addition to §10's list): EP-48506 — "Coverage: 35 of 57 cases never reached a running system" (🔴; the ticket has no suite so 0.30's `not_run` accounting cannot show it — a `[Pipeline]` gap: coverage of an unpublished ticket is invisible to the record), "The published state of this ticket is now false" (🔴; wave-1 comment stale after stages 7–8 ran — no rule says a PARTIAL status line must be superseded when the pending stages complete in the same round), row 40 "three `RISK-CR-*` rows were recorded `FAIL REJECTED`" (a status the vocabulary reserves for arrived-as-FAIL cases — a vocabulary hole the count gate cannot see), row 56 "Stage-9 runsheet defect pattern, 3 rows in one day" (cards pointing at instruments that 403 their own data source — a provisioning-rules candidate); EP-56998 — 🔴 "Build under test unidentifiable", 🟡 "A SPEC-DEFECT finding is invisible to the count gate" (SPEC-DEFECT written in prose, not a status cell); EP-56197 r4 — 🟡 #2 decorated status cells `*not executed here*` (0.27's rule, still being broken — the analyzer flags it, nothing prevents it), 🟡 #8 stale unsuffixed artefacts (0.31 answered half; the other half — "round-suffixing every manual-results artefact" — was "deferred to the count-gate release", i.e. 0.36, which did not do it; 0.32's folders would make it moot, once used).

---

## 12. Proposed `verify_plugin.py` checks (each ≤ 40 lines, mechanical, would have caught a finding above)

| # | Check | Reads | Catches |
|---|---|---|---|
| V10 | **Retired-term scan**: a list of `(regex, allowed-context regex)` pairs — e.g. `checklist` allowed only within 200 chars of `0.40|legacy|Structural checks|folded`; `Chrome extension for all`; `comment pair`; `working directory`; `Stage <n>/6`; `no delete` — WARN with file:line | tracked `*.md`, manifests | census rows 1–13, 15, 18, 27 |
| V11 | **Status parity across the four places** the vocabulary names: every status token in `status-vocabulary.md` must appear in the emitting stage's Classification section *and* in that stage's template Statistics table (`Emitted by` column → files) | vocabulary + 3 SKILL.md + 3 templates | F15 (code-review lacks OBSERVATION) |
| V12 | **Contents line on every reference > 100 lines** (`**Contents:**` or the template's `> Sections of the generated` form) | `skills/*/references/*.md` | five files in §10 |
| V13 | **Description/`when_to_use` length budget** and a `->`/angle-bracket check on *all* description fields including `marketplace.json` | frontmatter + manifests | census 2; 8a truncation risk |
| V14 | **Fixture shape**: `fixtures/EP-0000-context.md` must contain `^- AC-\d+ \(` bullets and an `AC items on the page: N · captured: N` line, and `reconcile_counts.py EP-0000 fixtures` must not print "pre-0.42" | fixture | F3 |
| V15 | **Eval phrases exist**: every quoted "…" in a ✅ line of `evals/triggering.md` appears verbatim (case-insensitive) in that skill's description; every ❌ arrow names an existing skill or "chat" | evals + frontmatter | eval rot after a description edit (none today — keeps it so) |
| V16 | **Cross-reference sections exist**: for every `` `file.md` → "Heading" `` pointer, the heading exists in the target (the tree uses this form ~60 times) | all `*.md` | the 09-07 review found three broken paths; this catches the *section* level 0.36 does not |
| V17 | **Legacy shapes in `.gitignore`** must sit under a comment containing `legacy`; a pattern that never matched any name in `runs/` (when reachable) is a WARN | `.gitignore`, optional `runs/` | census 24–26 |
| V18 | **Ledger shape** (when `$EP_QA_HOME` is reachable, WARN-only): every `*-open-items.md` header equals the spec's 8 columns; item cells ≤ 200 chars; count of `[Pipeline]` rows with `Decision = —` older than two rounds | `~/.ep-qa/runs/**/*-open-items.md` | F14; gives MAINTAINERS step 1 its "machine-readable input" |
| V19 | **Publish/consume pairs**: a list of `detail.*` keys the publish reference writes; each must be named by at least one consumer file (`qa-pipeline-code`, `qa-service-publish` Code-phase section, analyzer) | `qa-service-publish.md` + 3 files | F6 (`detail.ac` written, never read) |
| V20 | **`.playwright-mcp/` or any `*.png` in the checkout** → WARN with a count (the 0.39 principle applied to the browser's default output dir) | tree | 307 files today |
| V21 | **CHANGELOG disposition of "Planned for" / "DEFERRED to"**: every such phrase in an older entry must be followed by a later entry naming the same item (`§4.4`, `#17`, …) | CHANGELOG | F10 |

---

## 13. What the plugin demonstrably gets right that most plugins do not (load-bearing only)

- **Every rule has its incident, and the incident is in a tracked file.** No surveyed plugin can say why a rule exists; here the CHANGELOG can, and MAINTAINERS forbids deleting a rule without reading it. This is why the deletion ledger above has so few DELETEs.
- **The verdict record separates who said what.** `source: machine | manual`, principal on every row, `not_run` for the unconfirmed, retractions as re-records posted where the wrong verdict was published — nothing in the field does this.
- **The gates that fired changed outcomes.** `OBSERVATION (no source checked)`, the source register, the count gate and the post-publish verification each caught something real in this month's runs (§6). The plugin's best mechanisms are its cheapest ones — a status token and a re-read.
- **Prompt-injection and secrets discipline are first-class**, not afterthoughts (`task-context`, `browser-rules`, `environment.md`, `load-env.sh`), and the secrets rules were tightened after each of the three incidents that tested them.
- **The human round is designed around the tester's attention** (0.31), on the tester's own testimony. That is rarer than any technical mechanism in §9.

---

## 14. Surprises — where the documentation and the tree came apart

1. **The run workspace is not the layout any document describes.** Three documents give three layouts (`runs/<KEY>/docs/`+`r<N>/` in `data-locations.md`; `runs/<KEY>/legacy/` for old root files in the same file; `runs/legacy/` in MAINTAINERS). The machine has the third, flat, for everything — including runs written this morning, after every one of the twelve releases was dated. The script that gates publishing cannot find a single ticket on it.
2. **`build_data_pack.py` exists.** 0.38.0 says the palette is "the one every `build_runsheet_<KEY>.py` ships — `build_data_pack.py` never existed"; `~/.ep-qa/runs/legacy/build_data_pack.py` (2026-07-15) and `build_data_pack_EP53978.py` (2026-07-29) exist. Right about the repo, wrong about the workspace the sentence was written from.
3. **Eight rules in the walk-plan era, zero walks.** The most elaborate new mechanism (0.31 + 0.37: card kinds, backstage keys, voice rules, verdict mapping table, state schema) was designed from one tester quote and has not met a tester.
4. **The style guide beats the template on the one field the burst changed** (F1) — 0.38's most consequential content change landed in the file that declares itself subordinate.
5. **The count gate has been "verified live" on every run and cannot run on this machine's layout** (F7). Both statements are true because the runs passed an explicit directory argument (`reconcile_counts.py EP-48506 .` in EP-48506's run report) from inside the folder that held the files — the documented default resolution has never been the path used.
6. **The token-in-URL incident recurred on 2026-09-08**, five releases after the rule and three days before a release titled "the tree is clean" — and left no CHANGELOG trace.
7. **The fixture that every skill edit is supposed to be smoke-tested against is itself pre-0.42**, so the smoke test has been unrunnable-as-specified since the last release of the burst, and the CHANGELOG says it was updated.
8. **Analyzer §1's AC-ledger 🔴 would fire on every retest**, because nothing restores the ids the code phase rebuilds (F6) — the newest, most-emphasised check produces a guaranteed false alarm in the most common mode.
9. **Every wave-1 pause this month was answered "no"** — the plugin's most-defended publication point is, in practice, a pause the operator uses to *not* publish; the record that was supposed to be created regardless never was.
10. `.playwright-mcp/` holds 307 files inside the plugin checkout — the browser backend's default output dir is the distributable, exactly the class of thing 0.39.0 moved out, and the default is the reason the "sandbox" rule was written.
