# ep-qa-pipeline — external review, 2026-09-07 (v0.29.0 + working tree)

Scope of what was read: MAINTAINERS.md, CLAUDE.md, README stage table, CHANGELOG 0.26–0.29, all 14 SKILL.md frontmatters, the full bodies of `qa-pipeline-code`, `code-review`, `web-testing`, `qa-manual-results`, `qa-run-analyzer`, the shared references `sources-of-record.md`, `status-vocabulary.md`, `playwright-executor.md`, the `qa-service-publish.md` write-back section, `reconcile_counts.py` (run: self-test + live on EP-56197 and EP-56133-retest3), `evals/triggering.md`, `hooks/hooks.json`, the two most recent run reports (EP-56197 round 3, EP-56133 retest 3), and the git history/diff. Docs-phase skills (grooming, checklist, test-cases) were skimmed for structure and technique coverage, not read line by line.

---

## 1. Verdict — is it OK for QA testing?

**Yes. This is a serious, above-average QA pipeline — not a prompt collection.** The things that make it sound are the ones most home-grown "AI QA" setups never get to:

- **A single status vocabulary** with evidence requirements per status, and a mechanical count gate (`reconcile_counts.py`) that refuses to publish on a mismatch.
- **The routing invariant** — every QA/FAIL case appears exactly once across the run, with four explicit re-routing forms. This is the rule that stops cases silently vanishing between API and UI stages.
- **"Prefer BLOCKED over a false PASS"** enforced with teeth: `BLOCKED` needs a `Probe:`, absence checks need a positive control and a post-lag second read, code-review PASS only when fully determined by code text, code-read FAILs are claims until runtime confirms them.
- **Source-of-record discipline** (0.28) — no defect without a quoted clause, as-built documentation ranked as a source, precedent tickets explicitly not a source.
- **Two-wave publishing** — nothing human-facing leaves until a human has walked the sheet; retractions are a first-class, listed-first concept.
- **Risk-scaled depth** with named techniques (BVA, decision tables, invalid transitions, PICT pairwise) and a `[core]` human tier per behavioural requirement.
- **Incident-driven rules with the incident recorded** — CHANGELOG entries explain the paid-for failure behind each rule, and MAINTAINERS forbids deleting one without reading that entry.

Where it is weaker (detail in §4): the system-of-record write-back is the pipeline's softest joint — verdicts are appended as free text into case notes instead of using QA Service's run/verdict API; there is no memory across retest rounds except git-ignored run reports, so the same 🟡 items were carried three rounds in a row; and a few rules in `code-review` forbid exactly the reads that produced the last run's best finding.

---

## 2. The latest updates vs the holes you found

Holes as recorded in the two newest run reports and the CHANGELOG. "Fixed" means the fix is in a tracked file at HEAD; I verified each by reading the file or running the script, not from the CHANGELOG text.

| # | Hole (where recorded) | Release | Status | Evidence |
|---|---|---|---|---|
| 1 | Code phase read no source of record; false "Groups renders nowhere" defect nearly filed (EP-56133 r3) | 0.28.0 | ✅ Fixed | `sources-of-record.md` §1–6; register built in step 0 in every mode; `Source:`/`Clause:` required on every FAIL / FAIL CONFIRMED / `RISK-CR-*` in CR/API/WEB; new status wired into status-vocabulary; analyzer §7 checks the register |
| 2 | Labels lost when a report is compressed into a Jira comment — "True matches" column (EP-56197 r3) | 0.29.0 | ✅ Fixed | `sources-of-record.md` §7 (publication gate, incl. the column-header rule); wired into `qa-pipeline-code` step 6 and `qa-manual-results` step 4 |
| 3 | `reconcile_counts.py` blind to flat `TC-N` ids — count gate silently absent in bug-fix mode (EP-56289, EP-56197 r1–r3) | 0.27.0 → shipped 0.29.0 | ✅ Fixed & verified | Self-test passes with two fixtures; live run on EP-56197 now reports `test-cases: 12 distinct case ids` (was 0) |
| 4 | Archive walls on Bug/Defect faces (EP-56380) | 0.26.0 | ✅ Fixed | Archive target rule + post-publish check treats an archive on a Story face/Bug/Defect as ❌ |
| 5 | "New chat → ask for upload" instruction wrong in six skills | 0.26.0 | ✅ Fixed | `data-locations.md` wired into 12 skills |
| 6 | 🔴 **Durable per-case record does not exist — 0/42 suite cases carry a verdict after five passes** (EP-56133 r3 #1) | — | ❌ **Open** | No CHANGELOG entry; write-back still = append text to `detail.notes` (`qa-service-publish.md` → Result write-back). See §4.1 — this is the most important open item |
| 7 | 🔴 **Retraction has nowhere to land** — FAIL CONFIRMED published on EP-56109, retest passes on EP-56133 which has no QA sub-task; 0.26 rule forbids the walk-up (EP-56133 r3 #2) | — | ❌ **Open** | 0.29 holds retractions to the *publication gate*, but no rule says *where* a retraction of a verdict published on another ticket goes. Step 6 still says "Do **not** improvise a walk-up" with no exception |
| 8 | 🟡 `reconcile_counts.py` harvests statuses from the "Not executed here" table's *Last verdict* column and ids from prose; OBSERVATIONs under-counted (EP-56133 r3 #5) | — | ❌ **Open** | Re-ran the shipped script on `EP-56133-retest3`: code-review still `FAIL=6 · PASS=16` (the report documents 3 real FAILs, 0 real PASS rows in Results). 0.27/0.29 fixed id *shapes*, not *section scoping* |
| 9 | 🟡 Playwright backend refuses to write screenshots outside its sandbox root; `playwright-executor.md` instructs an impossible save path (EP-56197 r3, r2 rec #7 re-diagnosed) | — | ❌ **Open** | `playwright-executor.md` → Evidence still says "save as `<ISSUEKEY>-<TC-ID>-fail.png` in the working directory"; no mention of the sandbox or of `-web-evidence.md` as the documented equivalent. Every Playwright FAIL is currently non-compliant with its own skill |
| 10 | 🟡 Zero `[core]` markers in an older test-cases file; stage 9 has nothing to select from (EP-56133 r3 #6) | — | ⚠ Partial | `qa-manual-runsheet` line ~238 already says "from an older suite without `[core]` markers, pick a representative" — but nothing records the nomination back, so the next round starts blind again |
| 11 | 🟡 RISK-CR-1/2/3, unmapped changes, 6 EP-56287 behaviours "carried a third round, still open" (EP-56197 r3) | — | ❌ **Open (structural)** | No skill has a cross-round carry-forward mechanism; grep for "carried forward / ledger / open items" in `skills/` finds only the docs-phase grooming questions. See §4.2 |
| 12 | Retest-mode file naming: `EP-56133-retest3-*` reports exist but the case file is `EP-47678-test-cases.md`; the script prints `test-cases: file not present` | — | ❌ Open (minor) | The count gate cannot reconcile a retest run against its case list unless the key is passed twice by hand |

**Bottom line:** the two holes you turned into releases today (source register, publication gate) are closed properly and the flat-id fix is finally shipped and working. But **the two 🔴 [Pipeline] items from EP-56133 retest 3 (#6, #7 above) have no CHANGELOG entry — neither implemented nor rejected.** By your own MAINTAINERS step 1, those are open defects of the plugin, and #6 is now the longest-standing 🔴 in the repo's history.

---

## 3. Skill-standard compliance (Anthropic skill authoring guidance)

| Check | Result |
|---|---|
| `name`: lowercase, hyphens, ≤64 chars, matches folder | ✅ all 14 |
| `description`: ≤1024 chars, third person, says what + when, includes negative triggers | ✅ all 14 (range 359–984 chars). `qa-pipeline-code` at 984 is near the ceiling — the next edit will overflow |
| SKILL.md body kept lean (guidance: <500 lines, detail in `references/`) | ⚠ `qa-pipeline-code` is **652 lines / 5.6k words**. Everything else ≤400 lines. `code-review` (393), `web-testing` (369), `qa-manual-runsheet` (357), `task-context` (355) are healthy but at the upper end |
| Progressive disclosure (references one level deep, named from SKILL.md) | ✅ consistently; `output-template.md` + method docs per stage |
| Scripts are real, tested, invoked from SKILL.md | ✅ `reconcile_counts.py` has a self-test; `extract_archive.py`, `generate_pict_cases.py`, `load-env.sh` present |
| Triggering evals | ✅ `evals/triggering.md` with ✅/❌ pairs per skill — manual but real. Better than most plugins |
| hooks.json shape (`{"hooks": {"Stop": [...]}}`), cross-platform command | ✅ |
| Manifests: plugin.json + marketplace.json versions agree, CHANGELOG top entry matches | ✅ 0.29.0 / 0.29.0 / 0.29.0 |
| Description ↔ body drift | ⚠ `web-testing` description says "executes them in the browser via a Chrome extension"; body says Playwright MCP is the preferred backend. `qa-run-analyzer` description lists inputs without api-testing / manual-results. Both harmless for triggering, both stale |
| Incident narratives inside SKILL.md | ⚠ Many "Real case: … / On one run …" paragraphs live in SKILL.md bodies (the orchestrator alone has ~10). Good for the CHANGELOG, expensive in the context window of every run. The guidance is: rule in SKILL.md, rationale in references |
| File hygiene | ⚠ **Working tree: 5 skill files + `.gitignore` rewritten with CRLF, zero content change** (`git diff --ignore-all-space` is empty). Something opened them on Windows and saved with CRLF. No `.gitattributes` exists, so this will keep happening and will hide real diffs. Two tracked files lack a trailing newline (`pr-summary/SKILL.md`, `qa-test-cases/references/output-template.md`). No NUL bytes anywhere — the old truncation bug is not present |
| Secret hygiene | ✅ Pattern scan over tracked files clean; `.env.qa-agents` and all `EP-*` caches ignored. One untracked, un-ignored scratch file: `_mw_login.js` (11 bytes, harmless) — the `_s9_*` / `_ep53978_*` patterns added in 0.29 are still per-name; a single `_*` rule would close the class |
| `verify_plugin.py` | ❌ Parked since 0.18.2 (commit message says so) and still absent. The 0.27 fix "written after EP-56289 and never committed" for two rounds is exactly what a pre-commit verifier catches |

Overall: **well above the bar for a Claude plugin.** The frontmatter is exemplary, the reference layout is right, the eval list exists. The two real deviations are the orchestrator's size and the CRLF churn.

---

## 4. Gaps and proposals (ordered by value)

### 4.1 Use QA Service's run/verdict API instead of appending text to notes — highest value

The connector in this session exposes `create_test_run` (fixed roster, `releaseId`, `env`, `principal`), `record_case_result` (verdict `pass|fail|blocked|known_defect|skipped|flaky`, `source: manual|machine`, `note` required on fail/blocked, evidence URLs, **re-recording supersedes instead of overwriting**, **a fail auto-files one deduplicated defect**), `close_test_run` (`closed` never invents verdicts for unrun cases), `case_execution_history`, `executed_coverage` (split by manual vs machine) and `run_defects`. None of these appear anywhere in `skills/`.

The pipeline currently re-implements all of that by hand in `detail.notes`: the `Run <date> (<source>) — SUPERSEDES …` line, the `⚠ CURRENT VERDICT:` first-line convention, the "machine vs human" distinction, the retraction convention. That is why after five passes on EP-56133 the suite still reads `requirementCoverage.verified: 0` — text in notes is invisible to every coverage read.

Proposal (one release, mostly in `qa-service-publish.md` → "Result write-back", `qa-pipeline-code` step 6, `qa-manual-results` step 4, analyzer §4):

- Step 6 wave 1: `create_test_run` titled `<KEY> <mode> <date> — machine`, roster = the in-scope case ids from step 0 (this also **fixes the retest-scope problem for free** — the roster *is* the scope file), `principal` = "ep-qa-pipeline (<user email>)", `env` = the alpha host, `releaseId` when known. `record_case_result` per executed case with `source: machine`; keep PASS / FAIL CONFIRMED → `pass`/`fail`, BLOCKED → `blocked`, NOT EXECUTED / NOT-TESTABLE → leave `not_run` (the API distinguishes not-run from not-selected — do not map these to `skipped`). `FAIL REJECTED` → `pass` with the CR finding in the note. `OBSERVATION (no source checked)` → **no verdict**, note only — the API's `fail` auto-files a defect, which is exactly what the 0.28 gate forbids for observations.
- Stage 10: a second run `— manual`, `source: manual`. A RETRACTS row is simply a `record_case_result` on the same case — supersession is native and `case_execution_history` shows old → new with principal and timestamp. The notes convention can stay as a human-readable mirror for one release, then go.
- Analyzer §4: replace the "write-back missing" prose check with `executed_coverage(suiteId, releaseId)` → 🔴 when `neverExecuted` equals the in-scope count after step 6.
- Post-publish verification: `get_test_run` instead of sampling `get_test_case` notes.

Two things to confirm against the live connector before writing the rule: whether `known_defect` should carry `FAIL CONFIRMED` on a case whose bug already exists (avoids a duplicate auto-filed defect), and whether the auto-defect filing can be suppressed for `fail` — if not, every machine `fail` will create a ticket before the human round, which contradicts the two-wave rule; in that case record machine FAILs as `blocked` + note in wave 1 and let stage 10 record the `fail`.

### 4.2 A cross-round ledger — nothing remembers what was carried forward

EP-56197 r3 says "carried a third round, still open" four times. The only place an open item lives is the run report, which is git-ignored, per-round, and re-derived by each analyzer run from scratch. Nothing makes round N+1 answer for round N's 🟡s.

Proposal: `<KEY>-open-items.md` (or a fenced block in the suite's `summary`, which *is* durable) with one row per unresolved 🔴/🟡 [Pipeline]/[Product] item: id, first seen (round/date), owner, decision. Step 0 of retest mode reads it and lists it in the scope confirmation; the analyzer flags 🔴 any item with `first seen` ≥ 2 rounds ago and no decision; stage 10 is the only place a row is closed. Same file absorbs the `[core]` nominations from #10 and the "decide in/out in writing" items (`GSTOP-WDTH-05`). The MAINTAINERS step-1 rule then has a machine-readable input instead of "read the last run report".

### 4.3 Retraction target rule (closes 🔴 #7)

Add one sentence to the archive-target rule and the retraction convention: **a retraction is posted where the verdict it retracts was published**, whatever ticket that is — and nothing else goes there. That keeps the 0.26 principle (one ticket's run does not colonise another's archive) while letting the three stale FAIL CONFIRMEDs on EP-56109 be corrected. Stage 10 needs a "published-elsewhere" column in its reconciliation: for each RETRACTS row, the comment id + ticket where the old verdict lives (already recorded in the retest-scope files — make it a required field).

### 4.4 `reconcile_counts.py` — scope status harvesting to `## Results` (closes 🟡 #8)

Concrete: count statuses only between `## Results` and the next `## ` heading; report ids found only in prose on a separate line (`prose-only ids: …`); count `OBS-<n>` / `OBSERVATION (no source checked)` bullets or make the templates put observations in an id-first row; accept a `--cases <file>` override (or read the `Test cases:` line from the report header) so a `-retest3-` run can reconcile against `EP-47678-test-cases.md`. Add a carried-forward-table fixture to the self-test — the 0.27 lesson was that a single fixture let a whole run shape parse as empty; this is the same lesson for sections.

### 4.5 `playwright-executor.md` — say what the backend can actually do (closes 🟡 #9)

Replace "save as `<ISSUEKEY>-<TC-ID>-fail.png` in the working directory" with: screenshot into the sandbox root, then copy via host-side file tools when available; otherwise the documented FAIL evidence is `<KEY>-web-evidence.md` (DOM/text readings, URL, console lines captured *before* navigation). Make the analyzer accept either form. Right now every Playwright FAIL fails §5 evidence audit on a technicality.

### 4.6 `code-review` rules vs what the good runs actually do

Three rules — "Work only within the PR branch. Do not take code from main, the base branch, other branches", "Do not analyze pre-existing code that was not changed in the PR", "Check only the test cases from the file" — are contradicted by the run's most valuable outputs: `RISK-5018-2` (the fix is absent on `master`) came from reading `master`; `RISK-CR-3` came from reading an unchanged load-bearing file; `RISK-CR-*` rows are by definition not test cases. The stage is doing the right thing and breaking its own contract. Proposal: keep the *default* narrow, add a bounded "release-line and dependency check" section: (a) for a bug-fix/retest run, confirm the fix hunk is present on every release line the ticket's `fixVersion` names — absent → 🔴 [Product], graded N/A never; (b) an unchanged file may be read when the pr-summary's blast-radius section names it. Also: the classification list omits `OBSERVATION (no source checked)` (it is only in the source-fidelity section) and the final-answer counters omit SPEC-DEFECT — the vocabulary says every emitted status must appear in the Classification section.

### 4.7 Rename `OBSERVATION (no source checked)` → `OBSERVATION (no clause found)`

The label was chosen today; it is worth changing before it spreads to Jira. "No source checked" reads to a developer or PM as *QA did not check*. The actual meaning is *QA checked every register source and none has a clause*. The status-vocabulary row even says "which sources were checked and came back empty". `no clause found` (or `unsourced`) says that. A one-line sed across 6 files plus the script's `STATUSES` tuple, and the triggering evals need no re-walk.

### 4.8 Independence of the last check

Analyzer §4 explains that it exists as an *independent* check because "the publish step verifies itself". But in the orchestrated flow the analyzer runs at step 5, before publish, and the post-publish verification is done by the orchestrator — the publisher checking its own work. Five passes with no write-back went through that self-check. Make the final action a light analyzer re-run (§4 + §5 only, `--post-publish`) rather than an orchestrator checklist.

### 4.9 Ship `verify_plugin.py` (parked since 0.18.2)

Checks it should do in ~80 lines: both manifest versions equal and equal to the CHANGELOG's top heading; every `description` ≤1024 and every `name` matches its folder; every SKILL.md ≤500 lines (warn) and ends with a newline; LF-only, no NUL; every `skills/*/` folder is named in README's stage table and in an orchestrator; every status in `status-vocabulary.md` appears in `STATUSES`; `reconcile_counts.py --selftest` passes; `git diff --cached --name-only` contains no path matching the run-artifact patterns. Wire it as a `PreToolUse` hook on `git commit` or just as MAINTAINERS step 6.0. This is the check that would have caught "fix written, never committed" in 0.27.

### 4.10 Small hygiene

- Add `.gitattributes`: `* text=auto eol=lf` (and `*.xlsx binary`, `*.pptx binary`, `*.png binary`). Then `git add --renormalize .` once — with explicit paths, per your rule. Until then, discard the current CRLF-only working-tree changes; they are not edits.
- `.gitignore`: replace `_s9_*` / `_ep53978_*` with `_*` (nothing tracked starts with `_`).
- Fix the two missing trailing newlines.
- `web-testing` and `qa-run-analyzer` descriptions: one-clause updates (backend, input list). Then walk `evals/triggering.md` for those two.
- Move the orchestrator's "Real case / On one run" paragraphs to `qa-pipeline-code/references/incidents.md` (one line each) and link once. Target: SKILL.md under 450 lines with zero behaviour change — the 0.20.0 consolidation precedent.
- `qa-pipeline-code` description is 984/1024 chars: trim the "Run in a FRESH chat" sentence into the body now, before the next edit forces it.

---

## 5. Suggested release plan

**0.30.0 — "the record"**: §4.1 (runs API) + §4.3 (retraction target) + §4.2 (ledger). Closes both open 🔴s and the structural carry-forward hole. CHANGELOG must explicitly close EP-56133 r3 #1 and #2.

**0.30.1 — "the gate works on retests"**: §4.4 script section scoping + `--cases` + fixture, §4.5 Playwright evidence, §4.7 status rename, §4.6 code-review bounded rules. Self-test + triggering walk.

**0.31.0 — "maintainability"**: §4.9 `verify_plugin.py`, §4.10 hygiene, orchestrator diet, §4.8 analyzer post-publish mode.

Nothing here weakens a rule that an incident created; every proposal adds a place for an existing rule to land or makes an existing check mechanical.
