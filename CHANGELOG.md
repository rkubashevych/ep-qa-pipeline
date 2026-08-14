# Changelog

All notable changes to the `ep-qa-pipeline` plugin. Versions follow
semver; bump BOTH `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` — the marketplace manifest is what
signals an update to installed copies.

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
