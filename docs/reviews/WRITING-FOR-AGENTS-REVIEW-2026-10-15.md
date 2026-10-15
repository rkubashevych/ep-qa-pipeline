# Writing-for-agents review — 2026-10-15

All 19 SKILL.md files reviewed against Matt Pocock's `writing-for-agents`
guide (mattpocock/skills): single source of truth, no-ops, sediment,
progressive disclosure, positive phrasing, leading words. Four read-only
reviewers, one per group; the defects in Part A and the cross-skill
counts were re-checked by hand against the files.

**Rule for every cut:** a rule that traces to a CHANGELOG incident is
moved or reworded, never deleted. Hard guardrails (credentials,
`ALLOWED_HOSTS`, production refusal, confirm-before-write, fresh
fixtures, join by TC id, git add rules, secret scan) stay where they are,
even where they repeat a reference.

**Size:** 6,205 SKILL.md lines → about 4,910 (−1,300, −21%).

| Group | Skills | Now | After |
|---|---|---|---|
| Orchestrators / modes | qa-pipeline, qa-pipeline-docs, qa-pipeline-code, qa-refinement, qa-rc-smoke | 1,275 | ~1,013 |
| Docs stages | task-context, requirements-grooming, qa-test-cases, qa-service-watch, commands | 1,577 | ~1,222 |
| Code stages | pr-summary, code-review, api-testing, web-testing | 1,372 | ~1,060 |
| Manual round | qa-manual-runsheet, qa-manual-walk, qa-manual-results, qa-run-analyzer, qa-api-tests | 1,981 | ~1,615 |

---

## Part A — defects (fix regardless of pruning) — all verified

| # | Where | Defect | Fix |
|---|---|---|---|
| A1 | `web-testing/SKILL.md:340` | "Do not mark PASS if there is any doubt — **prefer FAIL**". The vocabulary (`qa-run-analyzer/references/status-vocabulary.md:94`) says prefer BLOCKED / NOT-TESTABLE / QA over a doubtful PASS, and a doubt is classified (`:109`). No CHANGELOG entry backs "prefer FAIL". | Point to the vocabulary rule; FAIL only with a concrete discrepancy. |
| A2 | `qa-pipeline-code/SKILL.md:315-317` | The wave-1 narrow exception omits "rated SUFFICIENT by the evidence audit", which `references/wave1-and-verification.md:22-25` requires (0.47.0). | Restore the condition, or replace the inline copy with the pointer. |
| A3 | `task-context/SKILL.md:44-52` vs `:487` | Tells the agent to write a "⚠️ Suspicious content" note, but the output template has no such section and `:487` forbids sections not in the template. | Add the section to `references/output-template.md`. |
| A4 | `requirements-grooming/SKILL.md:28-29` | "if it is not in the run folder, task-context has not run" contradicts `data-locations.md:152` "Never read a missing file as 'that stage never ran'". | Replace with the pointer to the resolution order. |
| A5 | `qa-manual-runsheet/SKILL.md:257, 312` | "Step 2a" comes before "Step 2", and 2a uses Step 2's classification. | Reorder and renumber. |
| A6 | `api-testing`, `web-testing` | `BLOCKED (quota)` is in the vocabulary (0.47.0) for API and WEB but in neither stage's list of statuses it emits. | Add it to both lists (a pointer line). |

## Part B — plugin-wide sweeps (cheap, low risk)

| # | Sweep | Where | Saves |
|---|---|---|---|
| B1 | "Where to find inputs" paragraph with the pre-0.33 Jira-archive history → one pointer line to `data-locations.md` that keeps "a new chat is no reason to ask" | 9 SKILL.md | ~30 |
| B2 | "Tool names — prefixes vary per install" blockquote → one line, or a shared reference | 9 SKILL.md | ~25 |
| B3 | Version tags that only mark arrival ("(0.47.0)", "Since 0.33.0", "as before 0.50.0", "used to carry") — strip; keep a tag only where the rule would read as arbitrary without it | all | ~30 |
| B4 | Origin stories / incident narratives in the contract (EP-56227 refinement origin, RC "run by hand three times", MEXP/PR #5624, EP-57310) → one clause; the story stays in the CHANGELOG | 6 skills | ~35 |
| B5 | "Do not merge with the previous version, do not append…" + "the next skill in the same chat picks it up" → **"Overwrite it."** | 5 skills | ~15 |
| B6 | Slash-only stage descriptions (0.61.0) still carry trigger phrases and "Do NOT use" clauses → one line for the `/` menu | 7 skills | ~45 |
| B7 | "After 3 failed attempts… stop and reassess" written twice → one shared rule named **three-strikes** | api-testing, web-testing | ~8 |
| B8 | Status definitions restated in each executing stage (RE-ROUTE, SPEC-DEFECT, OBSERVATION, N/A, NOT EXECUTED, BLOCKED rationale, Source/Clause block) → one line each + pointer to `status-vocabulary.md`, which calls itself the single home | code-review, api-testing, web-testing | ~41 |

## Part C — the big moves (disclose or de-duplicate)

Ranked by lines saved. "Move" = to `references/` behind a one-line pointer; the meaning is kept.

| # | Skill | Lines | Action | Saves | Risk | CHANGELOG |
|---|---|---|---|---|---|---|
| C1 | task-context | 124-207 | Move the impact scan and the existing/dev-suite scan (background, never blocks) to `references/background-scans.md`; keep the SCOUT `ALLOWED_HOSTS` check inline | ~72 | med | 0.49.0 |
| C2 | qa-run-analyzer | 227-299 | Move §4's run sub-checks (duplicate `test-runs.md` → Verification) and suite-structure checks to `qa-service-first-checks.md`; keep in-sync / mismatch / not-published inline | ~55 | med | 0.43.x, 0.50.0 |
| C3 | pr-summary + code-review | 95-138; 104-161 | Bitbucket access, URL format, branch mode, head-branch-only → pointers to `bitbucket-access.md` ("edit HERE, not in the skills") | ~55 | low | 0.43.0 (head-branch, kept once) |
| C4 | task-context + requirements-grooming | 266-401; 124-148 | One shared `tech-spec.md` for the TS-n branch; keep detection and the never-print-the-download-link guardrail inline | ~52 | med | 0.57.0 |
| C5 | qa-pipeline-code | 129-185 | Suite-first extraction/reconcile restates `qa-service-publish.md` → "Code phase — suite as the case source"; keep a ~6-line core | ~32 | med | 0.34.0, 0.50.0 |
| C6 | qa-pipeline-docs | 54-79; 227-243 | Disclose "After a refinement run" and "Adopt a human QA sub-task" (rare branches) | ~32 | low-med | 0.45.0 |
| C7 | code-review | 245-281; 163-174 | "What to look for" (one branch per PR, mostly default) → reference; delete the Understand/Locate/Assess/Classify no-op | ~44 | low | — |
| C8 | qa-manual-results | 347-381 | Disclose Step 4d (register the PR's tests); settle who owns `link_implemented_tests` mechanics vs qa-api-tests Step 2 | ~30 | med | 0.49.0 |
| C9 | qa-test-cases | 403-434 | "Formatting" copies `output-template.md` Format rules; move the one missing fact (Adopted:/Level: stay off headings — the count script reads them) into the template first | ~28 | low | — |
| C10 | qa-pipeline-docs | 261-301 | Retired archive (0.33.0) and tracker (0.34.0) sections → two positive lines | ~27 | low | 0.33.0, 0.34.0 |
| C11 | task-context | 313-347 | Field-maps restated → "read the one table in `field-maps.md`" | ~27 | low | — |
| C12 | qa-manual-runsheet | 177-246, 407-421 | Six rules, three traps, self-check → one line each + pointers to `walk-plan-format.md` / `provisioning-rules.md`; keep the EP-48506 export clause and the secret-scan bullet inline | ~34 | med | EP-48506, 0.30.0 |

Smaller per-skill findings (NEG rewrites, local duplicates, CACHE lines)
are in the appendix.

## Questions before execution

1. **B8 / C5 / C12 pointers.** The guide says: if inline text was added
   because a pointer did not fire, sharpen the pointer before cutting. I
   found no CHANGELOG entry saying so for these, but you may remember one.
2. **C8.** Which skill owns `link_implemented_tests` — `qa-manual-results`
   Step 4d or `qa-api-tests` Step 2?
3. **qa-pipeline L82.** Is any pre-0.52 ticket still in flight that needs
   the "API cases still `planned`" route? If not, it is pure sediment.

## Proposed release plan

1. **0.62.0 — Part A** (six defects). Behaviour fixes, small diff.
2. **0.63.0 — Part B** (sweeps). Mechanical, low risk; walk the evals
   only for B6.
3. **0.64.0+ — Part C**, one group per release (docs stages first, with
   the `EP-0000` smoke test; then code stages; manual round;
   orchestrators). `verify_plugin.py` checks the moved `references/`
   links each time.

---

## Appendix — per-skill findings

Format: lines · category · action · saves · risk · CHANGELOG.

### Orchestrators / modes

**qa-pipeline (111 → ~96)**
- 48-56 · SEDIMENT · cut archive history; keep `search` before `list_suites` · 3 · low · 0.43.2
- 62-65 · DUP · → B1 · 3 · low
- 42-47 · DUP · keep "match on the label" once, same words as qa-pipeline-code 124-127; drop HV/EP detail · 3 · low · 0.43.5
- 101-102 · DUP · merge with the "explicit yes" at 88 · 2 · low
- 108-111 · DUP · table row 75 already routes a QA sub-task · 2 · low · 0.45.0
- 82 · SEDIMENT · "API cases still `planned`" (question 3) · 1 · low · 0.52.0

**qa-pipeline-docs (321 → ~226)**
- 279-301, 261-269 · SEDIMENT · → C10 · 27 · low
- 54-79, 227-243 · DISCLOSE · → C6 · 32 · low-med
- 117-128 · CACHE · recon sources live in `recon.md` · 6 · low · 0.45.0
- 129-146 · DUP · comment shape lives in `jira-writing-style.md`; keep the timing rule · 6 · low
- 174-180 + 270-278 · DUP · merge two count gates into one · 6 · low · 0.42.0
- 185-203 · DUP · publish procedure in `qa-service-publish.md` · 6 · low · 0.50.x
- 81-89 · NOOP · one line: "dev not started → findings are in time" · 6 · low
- 158-160 · SEDIMENT · delete · 3 · low
- 24-27 · NOOP · "sequences, does not reimplement" — 100-101 says it · 3 · low

**qa-pipeline-code (494 → ~400)**
- 129-185 · DUP · → C5 · 32 · med
- 230-242 · DISCLOSE · "Split runs" → `run-modes.md` · 10 · low
- 389-413 · DUP · step 8 is mostly "stage 10 does it" · 10 · med · 0.19.0
- 434-446 · DUP · verification list lives in `wave1-and-verification.md` · 8 · low · 0.47.0
- 195-207 · DUP · retest tiers live in `run-modes.md` · 8 · med
- 448-459 · DUP · retells downstream skills · 7 · low
- 315-317 · LEAD + drift · → A2; name it **narrow exception** once · 4 · med · 0.47.0
- 167-175 · DUP · bug-fix rules live in `run-modes.md`; keep the pause · 4 · low

**qa-refinement (202 → ~165)**
- 86-110 · DUP · question rules live in `jira-writing-style.md`; keep the `spec only` gate · 14 · med · 0.45.0, 0.47.1
- 129-137, 184-186 · CACHE · `sizing-template.md` has these sections · 8 · low
- 30-33, 172-174 · SEDIMENT · origin story, baseline numbers · 7 · low
- 178-183 · DUP · "no test cases" said three times · 4 · low
- 124-127 · NEG · "The post carries only the questions" · 2 · low

**qa-rc-smoke (147 → ~126)**
- 36-39 · SEDIMENT · origin story · 4 · low
- 113-118 · DUP · setting changes covered by Step 1 and the method · 4 · low
- 123-126 · DUP · "instrument proves itself first" said twice · 4 · low · 0.46.0
- 84-88, 105-107 · CACHE · bundle grep and comment shape live in the method · 5 · low
- 132-136 · NEG · "A smoke FAIL becomes a bug only after the user has seen it" · 1 · low

### Docs stages

**task-context (500 → ~330)**
- 124-207 · DISCLOSE · → C1 · 72 · med
- 266-401 · DISCLOSE · → C4 · 30 · med
- 313-347 · DUP · → C11 · 27 · low
- 102-122 · DUP · saved-sources detail lives in `sources-of-record.md` §8 · 13 · low · 0.47.0
- 437-454 · NEG · nine "Do not"s → one positive carry-verbatim list, every item kept · 8 · med
- 57-78, 423-435 · DUP · connector and comments rules said twice · 14 · low
- 456-489 · DUP · two pre-save checklists → one · 5 · low
- 44-52 · conflict · → A3

**requirements-grooming (464 → ~385)**
- 124-148 · DISCLOSE · → C4 · 22 · med
- 407-425 · LEAD · the finding line shape written five times → once · 10 · low
- 52-79 et al. · DUP/NEG · "no artificial findings" three times → one positive target · 12 · low
- 426-436 · DUP · auto-default mode is the orchestrator's to own · 6 · low
- 337-346 · SEDIMENT · EP-55944 rationale → one sentence · 6 · low
- 251-256 · DUP · source-support rule three times → one · 4 · med
- 26-29 · conflict · → A4

**qa-test-cases (441 → ~350)**
- 403-434 · DUP · → C9 · 28 · low
- 295-306 · DUP · filtering lives in `check-decomposition.md` · 10 · low
- 162-174 · DUP · exports: keep 3 lines incl. EP-48506 · 9 · med
- 152-160 · DUP · dual tag: keep the definition line · 7 · low
- 332-346 · DUP · quality rules live in `test-case-design-rules.md` · 6 · low

**qa-service-watch (111 → ~98)** — 21-28 sediment; 101-111 duplicates of the read-only and short-report rules · 13 · low

**commands (61 → ~59)** — 11-12 NEG → "Printing the section is the whole task" · 1 · low

### Code stages

**pr-summary (238 → ~195)**
- 95-138 · DUP · → C3 · 18 · low
- 39-55 · DUP · URL format, branch mode → pointer · 13 · low
- 64-85 · NEG · "Source: the PR's code only; requirements and cases belong to code-review" · 7 · low · 0.18.0

**code-review (447 → ~335)**
- 245-281, 163-174 · DISCLOSE/NOOP · → C7 · 44 · low
- 104-161 · DUP · → C3 · 23 · low
- 217-230, 320-375 · DUP · → B8 · 24 · low · 0.14.0, 0.19.0
- 83-130 · DUP · head-branch-only said four times → once · 8 · low · 0.43.0
- 335-342 · DUP · export tracing → pointer to `export-checks.md` (move, incident-backed) · 6 · low · EP-48506
- 376-397 · DUP/NEG · "PASS only on code text; FAIL/N/A only with file+line"; keep the 6-of-12 rule verbatim · 8 · med
- 60-75, 178-182 · NEG · tracker read-only, for source fidelity only · 6 · low · 0.19.0

**api-testing (267 → ~215)**
- 194-240 · DUP · → B8 · 23 · low
- 69-81 · DISCLOSE · export branch → `export-checks.md` · 8 · low-med · 0.44.0
- 171-181 · SEDIMENT · evidence rationale lives in `evidence-audit.md` · 4 · low
- 96-100 · DUP · → B7 · 4 · low
- 37-41 · CACHE · variable list lives in `environment.md`; name only `ALLOWED_HOSTS` · 3 · low

**web-testing (420 → ~315)**
- 295-369 · DUP · → B8; keep the 16-of-17 second-observation rule verbatim · 27 · low
- 187-204 · DISCLOSE · extension-only login → `browser-rules.md` "Login" · 11 · low · 0.35.0
- 249-267, 128-133 · DUP · evidence rules live in `playwright-executor.md`; third copy · 13 · low · 0.47.0
- 29-41, 179-185 · SEDIMENT · pre-0.40 checklist, pre-0.39 cache location · 12 · low
- 208-214, 277-281 · DUP · navigation-memory steps → one step + pointer · 6 · low
- 340 · conflict · → A1

### Manual round

**qa-manual-runsheet (460 → ~375)**
- 177-246, 407-421 · DUP · → C12 · 34 · med
- 119-127 · DUP · Non-goals section repeats the description · 9 · low
- 26-78 · SEDIMENT · 0.30/0.31 history · 10 · low
- 168-175 · DUP · sheet columns live in `runsheet-format.md` · 6 · low
- 347-365 · DUP · fixture defaults; keep random-password and `throwaway:true` · 6 · low
- 436-440 · DUP · production gate twice → keep one (Rules) · 3 · low
- 90-117 · DISCLOSE (optional) · retest handling; keep detection + fresh fixtures inline · ~20 · med
- 257/312 · order · → A5

**qa-manual-walk (237 → ~190)**
- 182-219 · DUP · Rules restate Steps 1-3 / `walk-session-rules.md`; keep production, `ALLOWED_HOSTS`, never-provisions, language · 15 · low
- 27-38 · DUP · "why a plan" lives in `walk-plan-format.md` · 8 · low
- 124-151 · DUP · word → verdict mapping and principal string live in the rules file; keep positive-control and the run-it confirm · 10 · low
- 174-180 · CACHE · retells qa-manual-results · 4 · low

**qa-manual-results (442 → ~350)**
- 347-381 · DISCLOSE · → C8 · 30 · med
- 225-237, 385-403 · DUP · bug-first order lives in `test-runs.md` · 14 · med · 0.43.6
- 281-291 · DUP · ledger rules live in `open-items-ledger.md` · 7 · low
- 252-280 · DUP/SEDIMENT · run lifecycle, retired archive · 12 · low
- 98-104 vs 239-244 · DUP · principal mapping twice → once · 6 · low
- 167-191 · co-location · sign-off check sits before the step it follows · 8 · low

**qa-run-analyzer (498 → ~405)**
- 227-299 · DISCLOSE/DUP · → C2 · 55 · med
- 225-328 · LEAD · "runs before publish, so the orchestrator owns it" three times → tag **post-publish** once · 10 · low
- 479-488 · DUP · ledger "what goes in" · 6 · low
- 248-254 vs 379-387 · DUP · "manual results never ingested" in §4 and §5 → §5 · 5 · low

**qa-api-tests (344 → ~295)**
- 24-33, 246-270, 100-106 · SEDIMENT · EP-57310 / MEXP / PR #5624 stories → one clause each; both rules kept · 18 · low · 0.59.x
- 271-292 · DISCLOSE · Bitbucket-token and CI detail → `local-harness.md` · 8 · low
- 333-344 · DUP · Rules restate Steps 1-3; keep the tools listed only there · 9 · low
- 153-168 · NEG · "the monolith is the only live home; teststone is reference reading", one "never" kept · 5 · med · 0.58.0
- 179-203 · co-location · two half-lists → one decision table · 4 · low
