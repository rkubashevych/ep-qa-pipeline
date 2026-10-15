# ep-qa-pipeline — regression review, 0.59.1 → 0.69.0 (2026-10-15)

Written against the git checkout at `C:\media-files\Coding\qa-pipeline-skill`: commit `4ac5934` (0.69.0, HEAD) diffed against commit `71f4418` (0.59.1), both exported with `git archive`. The installed copy in this Cowork session was compared with HEAD byte for byte: identical except the YAML folding of ten `description:` fields (the sync normalises `>` blocks to one quoted string; same text). Review only — nothing under `skills/`, `scripts/`, `evals/` or the manifests was touched. Line numbers are those of HEAD.

The burst, from the CHANGELOG headings: **ten releases dated 2026-10-15** (`0.60.0` … `0.69.0`), 46 files, +2,130 / −1,478 lines; 1,478 lines left the SKILL.md files and ~900 entered new or existing references. Most of the burst is the Part B / Part C programme of `docs/reviews/WRITING-FOR-AGENTS-REVIEW-2026-10-15.md`; 0.62.0, 0.68.0 and 0.69.0 are contract fixes.

---

## 1. Method and scope

**Mechanical gate first.** `python3 scripts/verify_plugin.py --no-git` on HEAD: **13 ok · 0 warn · 0 fail** (versions, 19 frontmatters, 93 text files, wiring incl. the new commands table, references, vocabulary, all six script self-tests, tree). Everything the gate checks is taken as verified and not re-derived below.

**Rule-by-rule diff, four groups, four independent readers** (docs stages; code stages; manual round + analyzer + qa-api-tests; orchestrators + dispatcher + triggering), each reading the 0.69.0 files in full, the per-skill diffs in full, and the 0.59.1 text wherever a hunk was removed. The question asked of every removed hunk: *does the rule still exist somewhere the agent running that stage will read at the moment it needs it?* A pointer counts only if the target exists, holds the full rule, and the pointer says what it decides. Stages 5–7 run as subagents that see only their SKILL.md plus the files it names, so a rule the SKILL.md no longer names is invisible to them.

**Every CHANGELOG claim for 0.60–0.69 was checked against the files** (≈75 claims). Every finding below was re-verified by the lead against the file before it was written; quotes are verbatim.

**Not done:** a live run. No EP-56001 artefacts are in the trees, so the 0.69.0 statement "0.68.0 showed no regression" is the author's own A/B and is not re-verified here. No fixture exercises the code stages or the manual round; those groups were reviewed statically.

---

## 2. Verdict in six lines

1. **No rule was lost in the moves.** Every hunk removed from a SKILL.md in 0.60–0.67 was found again, in full, in the reference the SKILL.md now points to — with one thinner landing (F16) and one marginal loss (N8). The pruning programme did what it said.
2. **The regressions are in the fixes, not the moves.** Five of the six 🔴 items were introduced by 0.62.0, 0.68.0 and 0.69.0: each fixed one copy of a rule and left the other copies, or added a rule without its producer/consumer. The worst (F1) is a 0.69.0 half-fix that turns every clean machine pass into a walk that refuses to start.
3. **The 0.61.0 slash-only change is sound mechanically** — nothing chains stages through the Skill tool — but five descriptions and two eval lines still redirect to skill names a session can no longer see, and the `commands` skill that would explain this is itself hidden (F11).
4. **The pipeline's own gate cannot see any of the 🔴 items.** `verify_plugin.py` checks files and vocabulary tokens, not cross-file rule agreement; `reconcile_counts.py` is itself the cause of F4; the EP-0000 fixture has no Bug, no Risk REQ, no run and no walk.
5. **Nine of the eleven 🟡 items pre-date 0.59.1** and were carried through the burst unchanged — three of them sit in text that 0.66.0/0.67.0 moved and "verified" without reading the rule against its siblings (F8, F9, F10).
6. The CHANGELOG is honest about what it did; where it is wrong it is over-optimistic about reach (seven claims PARTIAL, §5), never false about the edit itself.

---

## 3. Findings ranked by consequence

Legend: 🔴 produces a wrong outcome on a run the pipeline is designed for · 🟡 a contradiction or gap a run can trip on · **Introduced** names the release; "pre-0.59.1" = in both versions. "Caught?" = would the pipeline as written catch it, or does it depend on a human noticing.

### 🔴 F1 — A clean machine pass completes the QA Service run, and everything downstream still assumes `running` until stage 10 — **introduced 0.69.0 (half-fix)**

0.69.0 learned on EP-56001 that the service auto-completes a run once no `not_run` row remains, and changed the wave-1 line to say so — but only in the template. `qa-pipeline-code/references/results-comment-template.md:24-26`: *"open" only when `get_test_run` still reads `running` after the recording. With no `not_run` row left the service auto-completes the run: the line then reads `QA Service run <id> completed`.* Everything else still says the opposite:

- `qa-pipeline-code/SKILL.md:275-277` quotes the comment verbatim and unconditionally: *"… QA Service run <id> open. Results published after the manual round."*; `:324-325`: *"the run stays `running` for stage 10"*.
- `qa-pipeline/references/test-runs.md:156-158`: *"the wave-1 status comment says so (`… run <id> open`)"*.
- `qa-manual-walk/SKILL.md:214-217`: *"If the state file's run id no longer matches an open run (`get_test_run` → `completed` or `closed`), say so and stop: the round was already written back"*.
- `qa-pipeline/SKILL.md:54-55`: *"A run in status `completed` or `closed` is done"*; `test-runs.md:193-195`: every reader treats `completed` as done.

Stage 9 builds cards on every ticket regardless of the machine result (`qa-manual-runsheet/SKILL.md:276-286`: the `[core]` of every REQ, High-risk spot-checks). So on an all-PASS pass with nothing held back — the pass that should be the easy one — the orchestrator posts "open" for a run the service has already completed; "continue the walk" stops with a false "already written back"; the dispatcher reads the run as done and proposes nothing; only `qa-manual-results/SKILL.md:245-246` (`reopen_test_run` on `completed`) handles the state correctly, and it runs last. **Caught?** No — post-publish verification checks that exactly one status comment exists (`wave1-and-verification.md:79-84`), not its wording; the walk stops before anything runs. **Fix shape:** one rule in `test-runs.md` ("a run reads `completed` while cards remain → the walk reopens it / stage 10 reopens it; `completed` is 'done' only when `-walk-results.md` exists"), then the walk, the dispatcher row and the orchestrator's inline quote follow it.

### 🔴 F2 — task-context now skips the AC-page ask in "an orchestrator's auto-default run", and both orchestrators still expect that pause — **introduced 0.69.0**

`task-context/SKILL.md:192-195`: *"Ask the user once for the Confluence URL (or page) — except when nobody can answer (an orchestrator's auto-default run, a subagent): then skip the ask and continue."* 0.59.1 (`task-context/SKILL.md:306`) was unconditional. The consumers: `qa-pipeline-docs/SKILL.md:78-80` *"task-context — pause only if it needs you (attachments to upload, a Confluence access / missing-AC issue)"*; `qa-refinement/SKILL.md:49-52` *"It pauses only for its own blockers: an unreachable AC page, or attachments to upload."* "Auto-default" is the orchestrators' default grooming mode (`qa-pipeline-docs:83`, `qa-refinement:54`), so every orchestrated run reads as "an orchestrator's auto-default run" — the condition is undefined and the two sides disagree. A Story whose AC page sits in a comment or was never linked gets *"⚠️ No Confluence acceptance-criteria page linked"* and Description-only requirements while the user is in the chat and could paste the URL. The second sentence (*"A Bug usually has no AC page; that is expected, not a gap"*) changes nothing downstream: `:196-199` still writes the warning, grooming still grooms "more aggressively" (`requirements-grooming:43-47`), the analyzer still raises it (`qa-run-analyzer:175`). **Caught?** No — the analyzer flags the missing page, not the skipped ask. **Fix shape:** "nobody can answer" = the stage was dispatched as a subagent, full stop; an orchestrator running it inline asks once, as its own step 1 says.

### 🔴 F3 — web-testing's rewritten doubt rule names two statuses the vocabulary forbids for WEB — **introduced 0.62.0 (A1)**

`web-testing/SKILL.md:325-328`: *"A doubt is classified, not rounded to a verdict: BLOCKED / NOT-TESTABLE / QA over a doubtful PASS …"*. `status-vocabulary.md:22`: `QA` is *"CR only … never an output of theirs"*; `:31-32`: `NOT-TESTABLE` / `NOT-TESTABLE (instrumentation)` are *API*. The stage's own emit list (`:280-317`) and its statistics table (`references/output-template.md:126-138`) have neither. 0.59.1's "prefer FAIL" was also against the vocabulary, but FAIL is a legal WEB output that stays `not_run` and gets a walk card. A `NOT-TESTABLE` written by web-testing is accepted by `reconcile_counts.STATUSES`, recorded as `skipped` by `test-runs.md:113`, and passes the partition check arithmetically — the doubtful case stops being a row the human must walk. A `QA` has no mapping at all. **Caught?** No — verify check 6 tests vocabulary→STATUSES, not per-stage legality; the audit does not audit NOT-TESTABLE rows (`evidence-audit.md:79`). **Fix shape:** the web rule names its own legal set — BLOCKED (with `Probe:`), PARTIAL, SPEC-DEFECT, or FAIL with the discrepancy.

### 🔴 F4 — `reconcile_counts.py` now reports a case-less `Risk:` REQ's criterion as MISSING, and two consumers turn that into a 🔴 / a publish block — **introduced 0.69.0**

`qa-run-analyzer/scripts/reconcile_counts.py:279-297`: a `## REQ-N` group with no `### TC-` heading and no `REQ-N/struct-k` line contributes nothing from its `Covers:` line. `qa-test-cases/SKILL.md:56-67`: a Risk REQ whose consequence is not observable *"gets **no test case** … It is not an uncovered requirement and the analyzer does not count it as an orphan"*. `qa-run-analyzer/SKILL.md:111-113`: 🔴 when *"an `AC-n` is on no `Covers:` line of a group with a case or structural line"* — no exception; `qa-pipeline-docs/SKILL.md:170-172`: an uncovered `AC-n` *"is fixed before anything is published"*. Grooming says a risk REQ's source ids are "usually" the ones its mitigation also cites (`requirements-grooming:352-353`) — the valuable case, *"a hazard the material names but nothing mitigates"* (`:368-369`), has no second group. On such a ticket the script prints `MISSING: AC-n`, the count gate blocks the publish and the analyzer raises a 🔴 for a group the test-cases rule says is correct. **Caught?** Partly — the script prints the id; nothing says it is a judgement call, and no self-test or fixture has a case-less Risk group. **Fix shape:** the script exempts a group whose heading carries `Risk: … no observable consequence` (or the analyzer rule names the exemption), and a self-test case for it.

### 🔴 F5 — "Open findings": grooming's template and qa-test-cases define "needing clarification" in opposite ways — **introduced 0.68.0**

`requirements-grooming/references/output-template.md:40-44`: *"Not requirements: stage 4 reads them only to mark "needs clarification"."* `qa-test-cases/SKILL.md:46-50`: *"An open finding alone does not put a REQ under "needing clarification" — that count is for unresolved conflicts and REQs marked "(needs clarification)"."* Both texts are 0.68.0's; the CHANGELOG records only the qa-test-cases side. `Requirements needing clarification: N` goes into the sub-task description and is read by the analyzer (`qa-run-analyzer:177`); in auto-default mode most REQs carry an open finding, so the count is either ~0 or ~all depending on which file the stage-4 agent trusts. **Caught?** No — on the fixture REQ-2's only open finding is also an unresolved conflict, so the count is 1 either way (and the fixture lists no "Open findings" expectation at all, N1).

### 🔴 F6 — The new "Bug tickets" grooming rule has no producer and no consumer — **introduced 0.69.0**

`requirements-grooming/SKILL.md:92-97`: the repro steps and actual result *"become that REQ's case — the steps as its steps, the actual result as "must no longer occur" — so their `JD-n` ids go on that one REQ's `source:` line."* task-context has no rule to ledger a Bug's steps / actual / expected as separate `JD-n` bullets (`references/output-template.md:31` gives one shape; `field-maps.md:35` only says the Description holds "steps to reproduce"); grooming "does not write cases" and its template has no slot for the steps; qa-test-cases has no Bug rule (zero hits) and may not invent *"routes, selectors, roles, states, data"* (`:98-101`). On the exact case 0.69.0 was written for, either the `JD-n` the rule names do not exist, or stage 4 cannot reconstruct the repro — the one behaviour the Bug exists to retest. **Caught?** No — the script reports whatever ids stage 1 chose to write as mapped.

### 🟡 F7 — `FRONTEND_HOST` and the "no visitor-login variable" rule were added to the environment and never wired into the stage that needs them — **introduced 0.69.0**

`environment.md:77` and `api-testing-reference.md:45` define `FRONTEND_HOST`; nothing reads it: `api-testing/SKILL.md:36-38` *"not discoverable — it must be supplied (reference §11.1)"*, `:45-46` *"pause and ask"*, `:128-130` lists the hosts to check without it; `api-testing-reference.md:254-260` (§11.1) never names the variable; `qa-pipeline-code/SKILL.md:36-39` *"must be supplied… api-testing pauses and asks if missing"*. Only stage 9 uses it (`provisioning-rules.md:139`). `environment.md:81-85` says a missing exhibitor login is test data and *"a run that may not write marks such cases NOT EXECUTED"*; `api-testing/SKILL.md:45-46` says pause and ask, and never points at that paragraph. `BASE_URL` already names the same host (`api-testing-reference.md:44, 87, 132`) with no precedence rule. An api-testing subagent (which cannot ask, `qa-pipeline-code:231-234`) returns a blocker for a login the file says is test data. **Caught?** No.

### 🟡 F8 — Analyzer §4's "🟢 not published yet" outcome has been impossible since stage 3 creates the suite — **pre-0.59.1 (0.50.0); moved unchanged in 0.66.0**

`qa-run-analyzer/SKILL.md:222-224`: 🟢 *"no suite found AND this analyzer run is inside the docs orchestrator"*; `:251-256`: *"at that point there is nothing to sync against — report `🟢 not published yet` and stop."* But `qa-pipeline-docs/SKILL.md:114-124` (step 3) creates the suite, its header, the requirements and the generated cases before step 5, and `qa-service-sync-checks.md:54-55` runs the suite-structure checks *"whenever the suite exists"*. At docs step 5 a suite IS found and stage 4's cases are not in it, so the only matching outcome is 🔴 "publish incomplete / mismatch". Every docs-phase run report's QA-sync row is wrong or improvised. **Caught?** No — both smoke tests ran with no network.

### 🟡 F9 — The analyzer's partition check still omits held-back and quota rows; 0.67.0 fixed the orchestrator's copy only — **pre-0.59.1; one of two copies fixed**

`qa-service-sync-checks.md:21-25` (and `test-runs.md:294-300`): 🔴 when `not_run` ≠ *"the FAIL / PARTIAL rows awaiting the human"*. `wave1-and-verification.md:52-61` (0.67.0): `not_run` = those *"+ the held-back rows + any `BLOCKED (quota)` rows. A held-back or quota row showing as `not_run` is correct, not a mismatch. Never "fix" it by recording it."* CHANGELOG 0.67.0 says the orchestrator's copy "lacked the held-back and quota rows" — the analyzer's and test-runs' copies still do. An on-demand or later-round analysis on a pass with audit-held PASS rows reports a 🔴 the orchestrator says is correct; an agent "fixing" it records the held-back rows, which is the false pass 0.47.0 exists to prevent. **Caught?** No — this IS the check.

### 🟡 F10 — `BLOCKED (quota)` and `PARTIAL` are still missing from web-testing's statistics table — **pre-0.59.1; 0.62.0 A6 and 0.69.0 fixed the api side only**

`web-testing/SKILL.md:295-300` emits `BLOCKED (quota)`; `status-vocabulary.md:26, 29` assign `PARTIAL` and `BLOCKED (quota)` to WEB; `web-testing/references/output-template.md:126-138` has neither row; `playwright-executor.md:22-23` still lists the classification as *"PASS / FAIL / FAIL CONFIRMED / FAIL REJECTED / BLOCKED / OBSERVATION"*. `status-vocabulary.md:8-10`: *"A status that exists in only some of those places is a defect."* **Caught?** No — verify_plugin does not read templates.

### 🟡 F11 — Redirects to slash-only skills point at names a session cannot see — **introduced 0.61.0**

With `disable-model-invocation: true` the seven stages and `commands` are absent from the session's skill list (confirmed in this session: the plugin's list shows 11 skills, not 19). Yet these descriptions still redirect to them by bare name: `qa-refinement` *"grooming into a file only (requirements-grooming)"*; `qa-api-tests` *"to execute cases on a test env (api-testing), to write test cases (qa-test-cases)"*; `qa-manual-walk` *"to run cases unattended (web-testing) … ("walk me through the PR" → pr-summary; "…the code" → code-review)"*. `evals/triggering.md:32-33, 194-195, 209-210` expect *"Claude names this slash command"*, and `:84-85` *"may point to `/ep-qa-pipeline:commands`"* — but the model has no way to learn either name: `commands` is itself slash-only, and the README is not in context. A user who says "just groom the requirements" gets a chat answer or the dispatcher, not the pointer the eval promises. **Caught?** No — the eval is walked by hand. **Fix shape:** write the slash command into the redirect (`→ /ep-qa-pipeline:requirements-grooming`) so the visible description carries the name; consider leaving `commands` model-invocable (one short description) so "what commands are there?" can be answered.

### 🟡 F12 — The analyzer's Input list omits files its own checks read, and the new "Open findings" section has no reader beyond stage 4 — **pre-0.59.1 + 0.68.0**

`qa-run-analyzer/SKILL.md:33-55` does not list `-api-tests.md` or `-claim-review.json` (read by `references/qa-service-first-checks.md:46-47` — the 0.56.0 "no claim review" checks never run from the list), `-retest-scope.md` (`:398`), `-walk-state.json` (`:328`), `-testdata.json` (`:325-326`), `-human-summary.md` (`wave1-and-verification.md:83`). MAINTAINERS recipe step 3 requires the list to be kept. §2 `:178` ("Grooming findings that were left as-is / skipped") does not name the requirements file's "Open findings" section (`requirements-grooming/references/output-template.md:39-47`), and `qa-pipeline-docs` folds recon answers into the requirements file (`:91-98`) without saying to remove the settled BEHAVIOUR findings from that section. **Caught?** No.

### 🟡 F13 — Stage 9 is told to write a `why:` backstage key the plan format does not have — **pre-0.59.1**

`qa-manual-runsheet/SKILL.md:281` *"its remediation line as the backstage `why:`"*; `evidence-audit.md:114, 161` likewise. `walk-plan-format.md:108-127` *"Fixed keys, in this order"* — the key is `why-walked` (`:115`); the walk answers "why are we checking this?" from `why-walked`. **Caught?** No — the voice check inspects card bodies.

### 🟡 F14 — The results output template models a duplicate bug as the normal path and has no header slot for `completed` — **pre-0.59.1**

`qa-manual-results/references/output-template.md:66`: *"filed by the run (`fail` recorded, `created: true`)"* as an example row; `SKILL.md:227-231, 364-369` and `test-runs.md:226-229`: `created: true` means the prefix missed and a duplicate exists. `output-template.md:5`: *"status after this stage: closed / running (why)"*; `SKILL.md:246-250`, `test-runs.md:185-191`: the end state is `completed` or `closed`. Same gap in the analyzer's `references/output-template.md:28-29`. **Caught?** No.

### 🟡 F15 — web-testing requires a `§n` for every FAIL REJECTED and gives it no home, so the audit holds every one back — **pre-0.59.1**

`web-testing/SKILL.md:230-239, 242-244`: a FAIL REJECTED is a pass claim and needs its reading. The template: header `:11` (*"every PASS, FAIL and FAIL CONFIRMED has one"*), Comment rule `:108` (*"For FAIL CONFIRMED/REJECTED — a short description"*), the FAIL REJECTED finding `:84-89` has no `Evidence:` line. The audit audits every FAIL REJECTED row (`evidence-audit.md:74`); no artifact → UNVERIFIABLE (`:91`) → `not_run` + must-walk. **Caught?** Partly — the held-back rows show in the preview; nothing names the cause.

### 🟡 F16 — task-context's saved-sources pointer lands on a thinner rule — **introduced 0.64.0**

0.59.1 `task-context/SKILL.md:107-108`: `jira-<KEY>-comments.md` *"(all comments, each with its author and date)"*; `:111` the generic fence label. 0.69.0 `task-context/SKILL.md:92-99` points to `sources-of-record.md §8`, which lists the file (`:234`) without "all comments, with author and date" and shows only the `confluence:<id>` label (`:240-241`); the generic label lives in `untrusted-content.md:39-43`, which that paragraph does not name. A comments file saved as a digest defeats `source_tools.py quotes` on `CM-n` clauses and the drift check. CHANGELOG 0.64.0 "`§8` holds both" is half true. **Caught?** No.

### ⚪ Nits (stale text, one-line fixes)

- **N1** `fixtures/EP-0000-context.md:63-80` lists no "Open findings" expectation; CHANGELOG 0.68.0 says the smoke test checked it. The test cannot see grooming dropping the section.
- **N2** `qa-test-cases/references/test-cases-example.md:47` `Skill: qa-test-cases 0.68.0`; `skill_stamp.py` on HEAD prints 0.69.0 — the "expected output" differs from a fresh run on its first metadata line.
- **N3** `task-context/references/background-scans.md:3` "flow steps 7–8" — both scans are step 7 (`SKILL.md:82-87`); step 8 is Saved sources.
- **N4** `qa-test-cases/SKILL.md:220` → `test-levels.md` "Two invariants": body text at `:43`, not a heading. Same class: `web-testing/SKILL.md:327` and the vocabulary cite "Cross-stage rules" (`status-vocabulary.md:93`, a lead-in sentence); `test-runs.md` "Run lifecycle" and `qa-service-publish.md` "Writing the suite link into Jira" are bold paragraphs. verify check 5 resolves files, not headings.
- **N5** `api-testing/references/output-template.md:45-53` example rows carry no `api-evidence §n` though `:56` and `SKILL.md:168-169` require it (the web template's rows do, `:53`).
- **N6** `-web-evidence.md` has no file/section shape (`playwright-executor.md:65-102` describes contents only) while 0.69.0 gave `-api-evidence.md` one.
- **N7** `browser-rules.md:204` "(SKILL.md step 4)" → the evidence rule is Step 6 item 4; `playwright-executor.md:54` "in the Scope step" → the `ALLOWED_HOSTS` check is in Input (`SKILL.md:40-44`).
- **N8** `code-review/SKILL.md:89-90` lost 0.59.1's `:170-172` *"Compare the expected result of each step with what the code does"* when the four-verb list was called a no-op; the PASS definition (`:204-208`) covers it only partly.
- **N9** Three "what runs without the docker harness" lists disagree: `qa-api-tests/SKILL.md:67-69` (Steps 2 and 4), `qa-manual-results/SKILL.md:404-406` (Steps 1, 2 and 4), and Step 1b (`:100`) is in neither.
- **N10** `test-runs.md:95-121` ("the only place the mapping lives") has no row for the witnessed principal `ep-qa-pipeline agent (<KEY> walk, witnessed by <tester>)` that `qa-manual-results:236-238` / `qa-manual-walk:142-146` prescribe.
- **N11** Arrival tags the 0.63.0 B3 sweep missed: `qa-api-tests/SKILL.md:122`, `qa-run-analyzer/SKILL.md:37, 44`; `qa-manual-results/references/output-template.md:4` still offers "legacy archive comment (pre-0.33 ticket)".
- **N12** `TS-n` is absent from the `Covers:` shape (`qa-test-cases/SKILL.md:34-35`, `output-template.md:56, 122`; `requirements-grooming/references/output-template.md:37`) though `qa-test-cases:348` and `reconcile_counts.py:674-678` require it. Caught after the fact by the count gate — a rework loop, not a loss.
- **N13** A structural-only REQ's `Covers:` has no slot in the Structural checks block (`qa-test-cases/SKILL.md:226-228` vs `output-template.md:75-95`) — the gate fires a false MISSING a human must overrule.
- **N14** Risk-row promotion "step 6 proposes it as a permanent suite case" (`api-testing:115-116`, `web-testing:321-322`, `code-review/references/output-template.md:64-65`) is not in `qa-pipeline-code` step 6; the rule is in `qa-service-publish.md:666-676`, one hop from `test-runs.md:87-90`.
- **N15** `qa-pipeline-code/SKILL.md:249-252` (stage 7 brief) does not name `-api-evidence.md`; stage 8's does.
- **N16** `qa-rc-smoke` dropped the phrase "are these on RC" (0.60.0 claims no trigger phrase was removed); "check these items are on RC" / "are the release items deployed to rc" remain and cover the eval queries.
- **N17** api-testing never mentions dual `[API][UI]` cases (`status-vocabulary.md:82-84`: it may run the API half, never the final PASS); `SKILL.md:58-60, 99` collects every heading containing `[API]`, so such a case can exit PASS and web-testing then treats it as settled (`web-testing:52-58`).

---

## 4. Checked and clean (coverage)

- **Moves verified complete, text by text:** background scans → `background-scans.md`; tech spec both halves → `tech-spec.md`; Bitbucket access rules → `bitbucket-access.md` (byte-identical to 0.59.1; UUID URL form, branch vs PR mode, auth failure, "never search for a PR by branch", command workflows, local clone all present); code-review checklist → `what-to-look-for.md` (verbatim); `link_implemented_tests` mechanics → `linking-tests.md` (ref naming, landing pr→merged, `verify: true`, id-in-file, `partial` counts for nothing, 429, `@skip`, `discover_tests` flags and configured branch), each skill keeping its decision part; analyzer §4 checks → `qa-service-sync-checks.md` (every 0.59.1 check, same severities; post-run label on run checks only); "After a refinement run" and "Adopt a QA sub-task" → `special-cases.md` with both pointers naming when to look; "Split runs" → `run-modes.md` (MAINTAINERS pointer updated); the four question rules → `jira-writing-style.md:72-136`; the sizing sections incl. "an existing estimate on the ticket" → `sizing-template.md:58`; the chat-format block, the overwrite boilerplate, the case-filter list.
- **0.67.0's own six catches** are in the files: STRUCT line shape inline (`qa-pipeline-code:137`), both edge fallbacks (`:139-140, 154-155`), the human-created sub-task lookup (`qa-pipeline-docs:199-204`), recon's one setting flip (`:96-97`), the count gate before the PAUSE (`:165-176` → `:177`), its no-shell fallback counting tags, core and ledger ids.
- **Stage contracts:** every section name, id scheme and marker consumed across the docs chain (`Covers:`, `source:`, `AC items on the page … captured`, `- [ ] REQ-N/struct-k [UI]`, `[core]`, `### TC-REQ-N.M`, `Adopted:`, `Level:`, `Code-level:`, `Skill:` header, `(conflicts with AC-n)`) is spelled identically in `qa-pipeline-docs`, `qa-service-publish.md`, the analyzer and `reconcile_counts.py`; the script's `CONTEXT_BULLET`, `SOURCE_LINE`, `COVERS_LINE`, `PAGE_COUNT`, `STRUCT_REQ` patterns match the templates. Code-stage status tokens are consistent across the four SKILL.md files, the vocabulary, `STATUSES`, the `test-runs.md` mapping and the wave-1 partition; `-api-evidence.md` §n fields match what `evidence-audit.md:89` reads; screenshot store and names agree in five files. Manual-round file names, card kinds, `Completeness:` tokens, backstage keys (except F13), verdict→status mapping, retraction forms and plan-file names agree across runsheet, walk, results, `test-runs.md`, `write-plans.md` and `data-locations.md`.
- **Fixture ↔ example ↔ script:** the example's body run with the fixture under `EP_QA_HOME` gives `AC=5 JD=1 CM=1`, 7/7 mapped and covered, 12 ids, core 6, `[UI]` 11 · `[API]` 1, struct 2 — the example's statistics block; `Levels: E2E 11 · AE 3 · I 1 · C 1` re-derives; BVA 9/10/11 is right for a boundary of 10; one `[core]` per REQ by the core rule.
- **Slash-only mechanics:** no file chains a stage through the Skill tool (`qa-pipeline-docs:74`, `qa-pipeline-code:218`, `qa-refinement:46` all read the SKILL.md); the dispatcher's route table names only model-invocable skills; `commands/SKILL.md` lists all 19 with correct invocations; `verify_plugin.py:216-221` fails a skill with no commands row. Of the 17 trigger phrases removed from the seven stage descriptions, every one has a ❌ line in `evals/triggering.md` pointing at the dispatcher or an orchestrator whose description still carries an equivalent phrase.
- **Unchanged between versions (so every pointer into them resolves to the text the inline copies came from):** `bitbucket-access.md`, `absence-check-protocol.md`, `browser-rules.md`, `login-config.md`, `playwright-executor.md`, `export-checks.md`, `untrusted-content.md`, `test-runs.md`, `evidence-audit.md`, `wave1-and-verification.md`, `status-vocabulary.md`, `walk-session-rules.md`, `walk-results-format.md`, `provisioning-rules.md`, `runsheet-format.md`, `walk-plan-format.md`, `local-harness.md`, `qa-service-first-checks.md`, `check-decomposition.md`, `combinatorial-testing.md`, `test-levels.md`, `field-maps.md`, `data-locations.md`, all scripts except `reconcile_counts.py` and `verify_plugin.py`.

---

## 5. CHANGELOG claims that are not fully true

All other 0.60–0.69 claims checked out against the files. These did not:

| Release | Claim | Verdict | Where |
|---|---|---|---|
| 0.69.0 | wave-1 line says `completed` when no `not_run` row remains | PARTIAL | template only; `qa-pipeline-code:275-277, 324-325`, `test-runs.md:156-158` still say open (F1) |
| 0.69.0 | task-context skips the AC ask when nobody can answer; a Bug with no AC page is not a gap | PARTIAL | contradicts both orchestrators; "not a gap" has no downstream effect (F2) |
| 0.69.0 | grooming's Bug rule folds repro + actual result into the case | PARTIAL | no producer, no consumer (F6) |
| 0.69.0 | `FRONTEND_HOST` listed; visitor/exhibitor logins are test data; NOT EXECUTED when the run may not write | TRUE as written, unwired | api-testing still "pause and ask" (F7) |
| 0.68.0 | "needing clarification" excludes a REQ whose only issue is an open finding | TRUE in qa-test-cases, contradicted by grooming's template | F5 |
| 0.68.0 | smoke test checked "the Open findings section" | PARTIAL | the fixture lists no such expectation (N1) |
| 0.67.0 | post-publish verification now has the held-back and quota rows | TRUE for the orchestrator; the analyzer's and test-runs' copies still lack them | F9 |
| 0.66.0 | "Verified … nothing lost" | TRUE for the moves; the moved §4 text was stale before the move (F8) |
| 0.64.0 | saved-sources naming and fence command — "`sources-of-record.md` §8 holds both" | PARTIAL | F16 |
| 0.64.0 | case-filter list → `check-decomposition.md` | PARTIAL | nothing was moved; the file is byte-identical to 0.59.1 and its pre-existing shorter list was pointed to; "(scrolling, focus, opening a tab)" and "performance" examples are gone |
| 0.64.0 | "each moved text now lives in exactly one file" | PARTIAL | the SCOUT host check is deliberately in two (`task-context:85-87`, `background-scans.md:23-28`) |
| 0.63.0 | B3 arrival tags stripped | PARTIAL | N11 |
| 0.62.0 | A1 web doubt rule now points to the vocabulary | PARTIAL | it points there and names statuses the vocabulary forbids for WEB (F3) |
| 0.62.0 | A6 `BLOCKED (quota)` added to both status lists | TRUE for the SKILL.md lists; the web template still lacks it (F10) |
| 0.60.0 | no trigger phrase was removed | PARTIAL | "are these on RC" (N16; harmless) |

---

## 6. What the gate could catch and does not

Each of these is a defect class this burst produced; none is in `verify_plugin.py`:

1. **Heading-level pointers** (N4, four cases): a check that every `→ "<heading>"` after a `.md` name matches a `#` line in the target. Cheap; same shape as check 5.
2. **Per-stage status legality** (F3, F10): for each of api-testing / web-testing / code-review, the statuses in the SKILL.md emit list, the template's statistics rows and the vocabulary's stage column must be the same set. The vocabulary already says a mismatch "is a defect".
3. **The example's `Skill:` stamp** (N2) equals the manifest version.
4. **The analyzer Input list** (F12): every `<KEY>-*.md|json` name in `data-locations.md` is either in the analyzer's Input list or in an explicit "not read" list.
5. **A fixture case for a case-less `Risk:` group** in `reconcile_counts.py --selftest` (F4) and an "Open findings" expectation in `fixtures/EP-0000-context.md` (N1).

None of these would have caught F1, F2, F5–F9 — those are cross-file rule agreement, which only a read-through finds. Item 2 of MAINTAINERS' recipe ("keep SKILL.md lean; detail in references/") now has a sibling risk the recipe does not name: **when a rule is fixed, grep for its other copies first.** Six of the sixteen findings are one copy fixed, one copy not.

---

## 7. Suggested order of repair

F1 (one run-lifecycle rule in `test-runs.md`, then three followers), F3 (one sentence), F4 (script exemption + self-test), F5 (delete one clause in the grooming template), F2 (define "nobody can answer"), F9 and F10 (copy the fixed wording to the other copies), F11 (write the slash commands into the redirects), then F6/F7 which need a design decision (where a Bug's repro steps live; whether `FRONTEND_HOST` replaces "supply the host" in api-testing). F8 and F12–F16 are text edits. Per the change discipline, each of these is implemented or rejected in the CHANGELOG, not silently dropped.
