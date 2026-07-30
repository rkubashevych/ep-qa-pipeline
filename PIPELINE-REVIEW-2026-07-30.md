# Pipeline review — ep-qa-pipeline v0.13.0

Date: 2026-07-30. Reviewed cold, as an unknown author's work: README, MAINTAINERS,
CHANGELOG, both manifests, all 13 skills with references/scripts, hooks, fixtures,
.gitignore, `.env.qa-agents` (presence and key names only), `.claude/settings.local.json`,
the full EP-53978 artifact set, and samples of the ten older runs. Every claim below was
checked against the files; where I verified a prior document's claim, I say so.

**Severity counts: 5 Critical · 5 High · 6 Medium · 1 Low.**

---

## The narrative, corrected first

Three things the repo's own story gets wrong, and they frame everything below:

1. **CHANGELOG 0.12.0 says the run's anti-false-pass rules "apply to the whole pipeline
   and not just to it." They do not apply to the pipeline at all.** They exist only in
   `qa-manual-runsheet/references/provisioning-rules.md`. Verified by grep: neither
   `api-testing/SKILL.md`, `web-testing/SKILL.md`, their references, nor
   `qa-run-analyzer/SKILL.md` contains any rule about UI-created preconditions, ingestion
   lag, positive controls, or probing blockers. The stages that *produce the verdicts*
   are unchanged since the run that produced the false pass.

2. **CHANGELOG 0.13.0 says wiring `qa-manual-runsheet` in as stage 9 fixed "a stage
   nobody invokes." It moved the stage; it did not move the knowledge.** Stage 9 runs
   *after* step 6 has already posted results to Jira and written PASS/FAIL notes into the
   QA Service suite. Anything the runsheet stage (or the human walking it) then discovers
   corrects a record that has already been published, in a system with no retraction
   convention (Finding 2).

3. **This repo already contains a 20-gap adversarial review of itself
   (`EP-53978-flow-gap-analysis.md`, five Critical), and essentially none of it has been
   implemented.** Verified point by point: no `Probe:` field in any template, no
   `Completeness:` header, no `INCONCLUSIVE`/`VACUOUS`/`SPEC-DEFECT`/`RE-ROUTE` statuses,
   no `secret-handling.md`, no clone-URL rule in `bitbucket-access.md`,
   `reconcile_counts.py` still has all three defects the run report named on 2026-07-28,
   no retraction convention in `qa-service-publish.md`, no evidence-quality bucket in the
   analyzer, MAINTAINERS still omits the stage from its repo-layout tree and still points
   at `D:\Coding\...`. The review itself is git-ignored (`*-flow-gap-analysis.md`), so the
   most valuable document in the working tree is invisible to version control, to the
   plugin, and to the next session. The pipeline's failure is no longer "it doesn't know" —
   it is "it knows, in files it is configured to forget."

---

## Findings, ranked by consequence

### 1. CRITICAL — The verdict-producing stages still cannot tell a false pass from a pass

**What breaks.** `api-testing` creates preconditions over the API (it is the only stage
allowed to write), asserts absence on analytics-backed surfaces immediately, and records
PASS. On EP-53978 that produced the run's central false pass: TC-REQ-37.1 ("zero records
attributable anywhere", the story's core privacy claim) PASSed while the organizer Lead
dashboard was naming the opted-out user — because a curl-created favourite never enters
client-side tracking, and no organizer-side surface was in the sweep. The run report
*endorsed* it ("that claim is properly earned"); the triage reversed it a day later.

**Would the pipeline catch it next time? No.** The rules that would (UI-provenance for
counter/lead/analytics assertions, measured ingestion lag, positive control on absence
checks, one role-per-surface enumeration on "anywhere" claims) live only in
`qa-manual-runsheet/references/provisioning-rules.md` and `runsheet-format.md` — read by a
stage that runs after the verdicts are published. `web-testing`'s only waiting rule
(`browser-rules.md` "Waiting": never a fixed wait, always wait for an element) is exactly
backwards for an absence check — you cannot wait for an element that must never appear.

**Fix.**
- `api-testing/SKILL.md` (Classification + Step 4): a case whose assertion reads a
  counter / lead / analytics / statistics / notification / dashboard surface may not be
  PASS or PARTIAL if its precondition was created over the API — classify
  `NOT-TESTABLE (instrumentation)` and list it in a "Route to web-testing" section.
- `web-testing/SKILL.md` Step 1: accept those routed cases into scope regardless of
  channel tag, pausing for the user to perform the precondition by hand where the no-write
  rule forbids it.
- New plugin-root `references/absence-check-protocol.md` (positive control + lag measured
  this run + second read after the lag + provenance), referenced from both executing
  stages; add the ingestion carve-out to `browser-rules.md` "Waiting".
- `qa-run-analyzer/SKILL.md`: a fourth bucket, Evidence quality — 🔴 for any absence-PASS
  with no positive control, any PASS on a counter assertion with API-only provenance, and
  any surface cited as conclusive in one case and unmeasurable in another in the same run
  (EP-53978 had nine PASSes and one BLOCKED riding on the same "No data to show" read).

### 2. CRITICAL — The system of record asserts verdicts everyone now knows are wrong, and nothing can correct it

**What breaks.** Step 6 wrote `Run 2026-07-28 … PASS` into suite case notes and posted the
Jira comment pair before the triage and the human run existed. The triage
(`EP-53978-remaining-cases-triage.md`) then overturned at least eight verdicts (37.1
PASS→FAIL, 27.6 PASS→FAIL, 21.1→FAIL, 16.3 false-PASS identified…), and the human tester's
actual results live in `EP-53978-preserved-entries.tsv` — TC / Result / Notes with the
filed bug keys (EP-55691…EP-55702). **No skill defines, reads, or writes back either
file.** `qa-service-publish.md` → "Result write-back" has no supersede/retraction wording
(the only such wording is a paragraph in `qa-manual-runsheet/SKILL.md`, which governs a
different writer). Jira comments are append-only by design and nothing marks the old
summary stale.

**Would the pipeline catch it next time? No.** There is no stage that ingests manual
results, and the analyzer's 🟡 "write-back missing" check can never fire in the
orchestrated flow (Finding 6). The next code-phase run will reconcile its cases from a
suite whose notes say PASS on a violated privacy requirement.

**Fix.**
- `qa-service-publish.md` → "Result write-back": add the retraction convention — a new
  verdict contradicting a prior run line writes
  `Run <date> — SUPERSEDES <prior> (<old> → <new>): <reason>` plus a single
  `⚠ CURRENT VERDICT:` line at the top of `notes`.
- Add a stage (or a step 10 in `qa-pipeline-code`) `qa-manual-results`: read the completed
  run sheet's Result/Notes columns (the format already mandates a
  PASS/FAIL/BLOCKED/SKIPPED dropdown), join **on the TC column, never position**, and
  perform the same Jira comment + suite write-back as step 6, with the retraction rule.
- Make `<KEY>-remaining-cases-triage.md` and the tester-results TSV first-class: name them
  in `qa-run-analyzer/SKILL.md` Input, in `qa-pipeline-code` step 0's restore set, and in
  the archive comment file list.

### 3. CRITICAL — The channel tag is still an irreversible routing decision made blind, and dual-surface hazards still fall between stages

**What breaks.** Stage 3 assigns exactly one of `[UI]`/`[API]`/`[mobile]`/`[export/email]`
per case while forbidden from inspecting code or system; stages 7/8 route on it absolutely.
No later stage may change it: code-review's vocabulary (PASS/FAIL/QA/N/A) has no "wrong
channel" verdict. EP-53978 evidence: TC-REQ-16.3 (`[API]`) was PASSed by stage 7 via the
client API while stage 7's own comment said "Legacy-web edit path (the known gap) is
`[UI]`" — and stage 8 never received it, because scope selection reads only `[UI]` QA/FAIL
items from code review. The exact hazard that made the case QA (stage 6 risk 4, missing
`clearGDPRCache()` on the legacy edit path) was never exercised, and the requirement reads
PASS. Same mechanism barred TC-REQ-37.1 from the only surface that could have failed it.

**Would the pipeline catch it next time? No.** The analyzer's reconcile check
("web-testing executed == QA+FAIL `[UI]` items") *certifies* the routing rather than
questioning it.

**Fix.** As Finding 1's routing half, plus: `code-review/SKILL.md` gets a `RE-ROUTE [UI]`
status ("the case's assertion originates in client-side code — file and line"), added to
its output template and to `web-testing`'s scope; `qa-checklist/references/checklist-design-rules.md`
gets a "provenance-sensitive checks" section allowing a second tag where the expected
result names a counter/analytics/notification surface (amending the exactly-one-tag rule
in `qa-test-cases/SKILL.md`).

### 4. CRITICAL — The improvement loop is structurally broken: run findings do not reach the plugin

**What breaks.** The run report (2026-07-28) issued 🔴 pipeline fixes: clone-URL guidance
in `bitbucket-access.md` after the token echo, fixes to `reconcile_counts.py`, re-status of
TC-REQ-1.1, token rotation. Two days and two releases later: `bitbucket-access.md` has no
clone or credential-in-URL rule (verified by grep), `reconcile_counts.py` is byte-for-byte
the buggy version (status regex matches the Statistics table; `TC-REQ-[\w][\w.]*` swallows
trailing periods; adjacent-pipe undercount), and nothing records whether the token was
rotated. The flow-gap analysis's 20 gaps are likewise unimplemented (see "narrative"
above). Meanwhile the analyzer's SKILL still instructs it to trust the script "instead of
recounting by hand" — an instrument its own last report proved wrong. Root cause: run
reports, triage, and gap analyses are git-ignored working files; MAINTAINERS' update recipe
has no step that consumes them; nothing tracks recommended actions to closure.

**Would the pipeline catch it next time? No — this is the mechanism by which nothing else
gets caught next time.**

**Fix.**
- `MAINTAINERS.md` recipe: add step — "after any run whose run-report contains a 🔴
  [Pipeline/skill] item, either implement it (CHANGELOG entry) or record the rejection in
  the CHANGELOG. A run-report recommendation with neither is an open defect of the
  plugin."
- Implement the two named one-day-old fixes now: clone rule in
  `skills/pr-summary/references/bitbucket-access.md` ("never a credential in a URL,
  command-line argument, or inline export; use `http.extraheader`/credential helper; a
  failed command that touched a secret is a rotation event") and the three
  `reconcile_counts.py` repairs plus a self-test against `fixtures/`.
- Stop ignoring the intelligence: move run outputs to `runs/<KEY>/` (one ignore rule for
  secrets-bearing files, tracked for the rest) or copy lessons into tracked reference
  files as part of the recipe.

### 5. CRITICAL — The plugin root doubles as run workspace and credential store, and the ignore list is losing the race

**What breaks.** The marketplace `source` is `./`, so the folder that installs as a plugin
is the same folder that holds `.env.qa-agents` (live BB token, admin password, organizer
API key — key names verified, values not read), `EP-53978-testdata.json` (plaintext
passwords for 84 live accounts — verified present), `EP-53978-freezeforever-testdata.md`
(two more credential pairs in a markdown table), runsheets, and screenshots. README even
documents `.env.qa-agents` *in the mounted plugin repo* as the first-choice env file — the
design deliberately co-locates live secrets with the distributable. Protection is a
hand-grown `.gitignore` whose history is visible whack-a-mole (nine patterns added for
this one run's new filenames). It is already leaking at the edges: `git status` today
shows **untracked, un-ignored** run artifacts — `EP-45424-web-test-data.md`,
`EP-45424-form-snapshot.json`, `EP-45424-rc-template-snapshot.txt`,
`EP-55279-alpha-evidence.md`, `build_data_pack.py` — while MAINTAINERS' documented commit
recipe is `git add -A && git commit`. One new artifact name + the documented recipe =
committed test-account material. `runsheet-format.md` itself records the near-miss: "84
account passwords were one `git add -A` from being committed."

**Would the pipeline catch it next time? No.** Nothing scans before commit; the recipe
encourages the failure.

**Fix.**
- Separate the workspace from the plugin: run outputs to `runs/<KEY>/` with `runs/` ignored
  (or an out-of-repo path the orchestrators default to), replacing the per-filename
  patterns.
- Replace `git add -A` in MAINTAINERS with an explicit-path recipe plus a pre-commit
  secret scan (the operator already has a `secret-leak-scan` skill — name it in the
  recipe).
- `qa-manual-runsheet/SKILL.md` Step 7: add "run a secret scan over every emitted artifact
  and the working tree before handing over."
- Keep `.env.qa-agents` out of the plugin folder, or document that a local-path
  marketplace install copies the directory and verify what the installer copies.

### 6. HIGH — The analyzer runs before the record exists, so its most important checks can never fire

**What breaks.** In `qa-pipeline-code`, the analyzer is step 5; Jira posting and QA Service
write-back are step 6; bug filing is step 7; the run sheet is step 9. Consequences, all
visible in EP-53978: the run report says "write-back … Expected — this analyzer runs
before the orchestrator's write-back step. Re-check after publish" — **nothing re-checks
after publish**, so the analyzer's own 🟡 "write-back missing" verdict is unreachable in
the orchestrated flow; the run report cannot list filed bug keys (they didn't exist yet);
and it never sees the runsheet/triage stage at all. The final published state of a run is
produced *after* the health check that is supposed to certify it.

**Would the pipeline catch it next time? No — by construction.**

**Fix.** `qa-pipeline-code/SKILL.md`: after step 9, re-run the analyzer's QA Service sync
check (or a light "post-publish verification" step): confirm N write-back notes landed,
every FAIL/FAIL CONFIRMED has a bug key or an explicit "not filed" line, and the runsheet
outputs exist; append the result to the run report and the human summary.

### 7. HIGH — Self-checks that cannot pass, and counts nobody derives mechanically

**What breaks.** Three instances, one run:
- `web-testing/SKILL.md` "Verification before saving" requires report count == **all**
  QA+FAIL items from code review (29 on EP-53978) — but the same skill's scope rule
  executes only `[UI]` ones (18). The check is unsatisfiable as written in any
  mixed-channel run, so it gets ignored — and with it went TC-REQ-27.1/27.2/27.3/27.5,
  which appear in neither Results nor "Not executed here" (27.5 has zero evidence in any
  stage).
- `qa-test-cases`' hand-tallied Statistics block is wrong (claims `[UI] 23 · [API] 61`;
  mechanical count of the 89 headings gives 24/60 — I verified by grep) and the docs
  orchestrator copies that block verbatim into the Jira tracker comment. Two prior
  recounts of the same file disagreed with each other, which is the proof that hand
  counting cannot be right.
- `reconcile_counts.py` — the one mechanical tool — is known-broken (Finding 4) and the
  analyzer is told to trust it over its own reading.

**Would the pipeline catch it next time? No.** The checks are prose; nothing consumes them.

**Fix.** `web-testing/SKILL.md`: change the check to "== QA+FAIL `[UI]` items, and every
case routed into this stage appears exactly once in Results or Not-executed-here."
`qa-test-cases/SKILL.md` verification: "derive the channel breakdown by counting
`### TC-REQ` heading tags; never tally by hand." Fix the script, then make the
orchestrators gate: `qa-pipeline-code` step 6 refuses to post while a count or ID-set
mismatch stands.

### 8. HIGH — Code-review PASS removes a case from all runtime execution, and resume treats file-existence as completion

**What breaks.** 58 of 89 EP-53978 cases (65%) never touched a running system because a
diff reading said PASS; REQ-3.1/3.2 were covered only "incidentally". The inverse also
fired: TC-REQ-1.1's FAIL was recorded FAIL REJECTED on evidence from a surface
(portal-ui) that cannot refute a Volt defect — the run report called the honest status
BLOCKED; the human retest later found the case FAIL for exhibitors (EP-55691). And on
resume, `qa-pipeline-code` step 0 skips any stage whose report file exists —
`EP-53978-api-testing.md` exists, contains `NOT EXECUTED 15`, and its Scope (60) and
Statistics (62) totals disagree; a resumed run inherits all of that as "done".

**Would the pipeline catch it next time? No.** The exclusions are the documented scope
rule; resume checks existence, not completeness.

**Fix.** `code-review/SKILL.md` Classification: "PASS only when the expected result is
fully determined by code text; a runtime observable (counter value, absence on a surface,
delivered notification, export contents, cache behaviour over time) is QA however
convincing the code." Every stage output template gains a required
`Completeness: complete | partial — N of M not executed` header; step 0 resume
re-dispatches `partial` stages; analyzer 🔴 on a `partial` report feeding a final verdict
and on Scope/Statistics totals disagreeing. `results-comment-template.md`: the human
summary carries "N of M verified by code reading only".

### 9. HIGH — The stages' real behaviour has outgrown their contracts, and the tooling cannot represent what they now do

**What breaks.** Stage 7 on EP-53978 ran 60 cases including code-review-PASS ones ("cheap
and adjacent to hazards"), invented two `RISK-CR-*` rows to chase code-review risks with
no test case (both FAIL CONFIRMED — the run's two most important product findings), and
used statuses (`NOT EXECUTED`, source `PASS(code)`) that exist in no template and no
regex. The triage then needed two more verdicts the pipeline lacks (`N/A — spec premise
false`, "expected result wrong — fix the case"). Good judgment, all of it — and all of it
invisible to `reconcile_counts.py`, unrepresentable in the templates, unwritable to the
suite (RISK rows have no case), and dependent on the next session's model being equally
smart.

**Would the pipeline catch it next time? Depends entirely on a human/model happening to
repeat the improvisation.**

**Fix.** Legalise what worked: add `NOT EXECUTED` and source `PASS(code)` to
`api-testing/references/output-template.md` and the script's regex; add `SPEC-DEFECT` (and
`VACUOUS`) to code-review/api-testing/web-testing classifications with the rule that a
SPEC-DEFECT triggers a "Requirements to correct" section in the human summary and an
`edit_requirement` (→ `discrepancy`) in the suite; require code-review risks with no
covering case to be emitted as proposed cases the publish step adds to the suite.

### 10. HIGH — The docs-phase files are not restored in the code phase, so the analyzer's coverage checks run blind exactly when they matter

**What breaks.** Step 0 rebuilds checklist + test-cases (from suite or archive) but not
requirements or context. EP-53978's run report states it outright: requirements/context
"were not carried into the code-phase chat… upstream traceability could not be
re-verified." The analyzer's first check ("every REQ-N has ≥1 checklist item / test case,
traceability intact") is therefore unexecutable in every fresh-chat code phase — the
documented normal flow.

**Would the pipeline catch it next time? No — it degrades silently and labels itself a
"limitation".**

**Fix.** The suite already holds the requirements (41 on EP-53978). `qa-pipeline-code`
step 0: rebuild `<STORY>-requirements.md` from the suite's requirements (stableId → REQ-N
is carried on the tracker lines) alongside the test-cases rebuild; when there is no suite,
include the requirements file in the docs-phase archive comment.

### 11. MEDIUM — BLOCKED needs no probe, and wrong blockers keep being accepted

Five EP-53978 cases were un-blocked by one later probe each (`/api/connections/add` was
live; a "nonexistent" setting existed, enabled), on top of the four from the previous run
recorded in `provisioning-rules.md`. Rule 5 exists only in the runsheet stage. **Not
caught next time** — the analyzer lists BLOCKED, never questions it. Fix: both executing
stages' templates gain a required `Probe:` field on BLOCKED (verbatim call + response);
no probe → `BLOCKED (unverified)`, a distinct statistics row the analyzer flags 🔴 if it
reaches the final verdict; `qa-pipeline-code` re-probes unverified blockers before step 6.

### 12. MEDIUM — Coverage is ID-continuity, so a changed behaviour with no requirement is invisible by construction

EP-53978: no case asserts a counter *decrement*; RISK-CR-2/3 (duplicate-on-top-of-public,
dual-typed rows) were real shipped defects with no case; the checklist has 96 items vs 89
cases, a delta no check reconciles. `pr-summary` is the one stage that sees the code and is
forbidden from comparing it to requirements. **Not caught next time.** Fix: `pr-summary`
gains a required "State & counter surfaces touched" section (from the diff only — within
its rules); the analyzer diffs that list against test-case assertions (🔴 "behaviour
changed with no case"); add checklist↔case reconciliation to the counts check; make the
return-leg (decrement to baseline) a required case in
`qa-test-cases/references/test-case-design-rules.md`.

### 13. MEDIUM — The freeze-forever experiment has no recorded outcome anywhere

`EP-53978-freezeforever-testdata.md` provisions a controlled pair to test the run's
sharpest hypothesis — a favourite stored private becoming visible to the target by name
after the actor re-opts in (read-side filter testing current state, not stored privacy).
Baseline screenshots exist (`EP-53978-ff-*.png`, 2026-07-29 17:20). No file records
whether the experiment was run or what it showed. If it was run and failed, a live privacy
defect is undocumented; if it passed, the strongest evidence in the run is unwritten; if
it was never run, a provisioned live-env fixture is drifting. **Not caught next time** —
no stage owns experiment outcomes. Fix: record the outcome now (suite note on the relevant
REQ-15/REQ-6 cases + a line in the triage or a successor file); generally, any provisioned
experiment must name the artifact its result will be written to before provisioning
(one line in `qa-manual-runsheet/SKILL.md` Step 6).

### 14. MEDIUM — Sources of truth: four declared authorities, none enforced

The suite "wins on divergence" — only when the connector is in the session; absent, the
run silently flips authority to the Jira archive and the analyzer is instructed to treat
it as normal, "never a gap or a 🔴". The checkbox tracker is "the single source of truth
for manual testing" — it is unwritable by the connector, read by nothing, and orphaned on
every re-run (docs phase always creates a NEW sub-task). The human summary is
"the source of truth for automated results" — append-only, with superseded wrong verdicts
(TC-REQ-1.1) left unmarked. Local files are deleted-and-recreated each run, so a hand
correction there is lost by design. **Disagreement between any two of these is detected
nowhere** (the sync check compares shape — stableIds, buckets — not verdicts). Fix: the
per-case verdict ledger (`<KEY>-verdicts.tsv`: case · stage · date · verdict · surface ·
source), emitted on both connector paths, included in the archive comment and step 0's
restore set; analyzer 🔴 on a case carrying two live contradictory verdicts; connector
absent becomes 🟡 "no durable per-case record", not normal.

### 15. MEDIUM — `runsheet-format.md` contradicts itself on its own spec

The file contains two palette sections: "Colour — reuse the existing palette" (saturated
fills, header `1F4E78` navy, "a muted pastel palette was tried and rejected") followed by
"Palette — muted, not alarming" (header `3E5C76` slate, pale tints) — as live, mutually
exclusive instructions. CHANGELOG 0.13.0 claims the rejected alternatives "are recorded in
references/runsheet-format.md so they are not reinvented," but the muted section is not
marked as rejected; it reads as the spec. The four `EP-53978-runsheet-*-example.xlsx`
variants in the working tree are the visible cost of re-deriving this. **Not caught next
time** — the next generator will implement whichever section it reads last. Fix: keep one
palette section; move the rejected one under an explicit "Rejected: do not implement"
heading with the rejection reason.

### 16. MEDIUM — Auto-default grooming ships known-open questions into execution with no gate

Five unanswered clarification questions each turned into blocked or contested cases
downstream (REQ-4's setting name → 2 BLOCKED on a High-risk requirement; the REQ-1/7/9
version-A/B conflicts doubled case counts and produced four FAILs possibly filed against
the wrong ticket — the frontend-scope question was never resolved). The findings
"resurface at the publish confirmation" — where the user has just watched four stages run
and confirms. **Not caught next time**: nothing distinguishes "open question on a
High-risk requirement" from noise at the only pause. Fix: `qa-pipeline-docs` step 6
preview must list open questions attached to `[risk: High]` requirements as a separate
"these will block or contaminate execution" block, with the per-question downstream cost
(N cases affected), and the code phase should refuse plain PASS/FAIL on version-A/B twin
cases until the conflict is closed — report `SPEC-PENDING` instead.

### 17. LOW — Local settings auto-approve plugin/MCP management commands

`.claude/settings.local.json` allowlists `Bash(claude plugin *)` and `Bash(claude mcp *)`
— any session in this directory can install/modify plugins and MCP servers without a
prompt. Ignored by git (fine). Given this repo is itself a marketplace, an agent editing
and republishing the plugin unprompted is a real, if local, hazard. Fix: drop the two
wildcards or narrow them (`claude plugin marketplace update expoplatform-qa`).

---

## What the pipeline demonstrably does well

- **The grounding chain holds.** 89 cases, all traceable to REQ-IDs; five requirements
  honestly marked "needs clarification" instead of papered over; the forbidden-vague-words
  rule visibly obeyed in the artifacts. This is the hard part of generated test design and
  it works.
- **Prompt-injection defence is written correctly** (tracker content is data; hostile text
  quoted into a visible note; rule binds downstream stages).
- **Write safety is real.** Both executing stages kept explicit write-audit tables;
  EP-53978's reverts were verified with diffs; the destructive TC-REQ-6.3 was refused
  independently by two stages under the same rule. Unrevertible residue is named, not
  softened.
- **`qa-service-publish.md` is empirical** — verified merge semantics, a forbidden
  destructive tool with a before/after diff, vocabulary rules derived from a measured
  failure. The 0.11.2 de-duplication was decided on byte counts, not taste.
- **The run report and testdata notes indict their own tooling** (the analyzer script's
  regex bugs, the pack's own six audited defects, the retraction of OBS-4). Self-honesty
  at this level is rare and is the raw material every fix above needs.
- **The loop's forward half worked when driven**: eleven defects (EP-55691…EP-55702)
  actually got filed from this run, with jam.dev evidence attached to the tester's
  results.

## What surprised me

1. **The repo contains its own best review and ignores it.** A five-Critical gap analysis
   sits git-ignored in the working tree while the CHANGELOG two versions later describes
   the lessons as absorbed. The gap between the repo's self-knowledge and its enforcement
   is the widest I have seen in a system this carefully documented.
2. **The freeze-forever experiment — the most serious privacy hypothesis of the run — has
   provisioning, credentials, baseline screenshots, and no recorded result.** The pipeline
   generated the question, built the apparatus, and forgot to own the answer.
3. **The most current, most correct verdicts in the whole system live in a TSV pasted from
   a spreadsheet** (`EP-53978-preserved-entries.tsv`), joined to cases by position in a
   sheet, consumed by nothing — while three declared "sources of truth" hold stale or
   false verdicts.
4. **The run's best coverage came from a stage breaking its own contract.** Stage 7's two
   off-script RISK rows found the run's two most important product defects; the contract,
   the templates, and the counting script all have no way to say so.
5. **Three counts of the same 89 headings produced three different answers** (23/61 vs
   24/60 vs a third recount) — in a pipeline that copies the number into Jira and builds
   suite levels from it. Nothing derives it mechanically; my grep agrees with the run
   report (24/60).
6. **`web-testing`'s mandatory completeness check is arithmetically impossible to satisfy
   in any mixed-channel run** — which quietly licenses ignoring it, and four cases then
   vanished without a trace in exactly that stage.
