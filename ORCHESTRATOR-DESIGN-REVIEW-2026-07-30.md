# Orchestrator design review — 2026-07-30

Cold design review of the two orchestrators (`qa-pipeline-docs`, `qa-pipeline-code`)
and every stage skill they invoke, at v0.17.0, judged against the creator's stated
intent — a start-to-finish shift-left QA process in which **the human is the final
arbiter and AI verdicts are provisional by architecture** ("around half of
AI-reported results turn out not to be true, and about half of the real bugs are
missed"). Read in full: both orchestrator SKILL.md files + references, all eleven
stage SKILL.md files, the load-bearing references (absence-check-protocol,
qa-service-publish, results-comment-template, publish-config, bug-report-template),
README, MAINTAINERS, CHANGELOG 0.11.2–0.17.0, and the EP-53978 run artifacts as a
reality check. `PIPELINE-REVIEW-2026-07-30.md` was read **last**; reconciliation is
the final section.

Findings are ranked **W1 (highest consequence to the intent) … W12**. Each carries
cost / evidence / fix.

---

## Executive view

**Verdict: yes, with one architectural contradiction.** The pipeline as written
implements every step of the creator's stated process — task learning, doc
gathering, gap analysis, AC decomposition into machine- and human-readable cases,
code-vs-cases review, API and browser execution, per-scenario fixture provisioning,
and a return leg for human results with explicit retractions. The stage contracts
are unusually disciplined (grounding rules, evidence provenance, count gates,
append-only retraction history). Most of what a lesser pipeline gets wrong — false
passes from API-created data, hand-tallied numbers, silent verdict drift — this one
has already been burned by and has written defenses for.

**The contradiction:** the creator's core constraint is that AI verdicts are
provisional until a human confirms them — yet the *choreography* still lets machine
verdicts become settled truth without a human ever looking. Three mechanisms do it:

1. **Step 8 hands the story back before any human has tested.** The "✅ QA passed"
   story note and the "QA done" transition are offered at code-phase step 8, on
   automated verdicts alone — one step *before* the run sheet is even built (step 9)
   and two before manual results exist (step 10). The pipeline's own step 10 says
   "the published verdicts are provisional until the manual results are ingested",
   but by then the story may already carry a QA-passed note and a workflow
   transition. (W1)
2. **The run sheet tells the tester to skip what the machine settled.** The
   89-rows-vs-11 optimisation (`qa-pipeline-code` step 9) is built on trusting
   machine PASSes — the exact thing the creator says he does not do. A code-review
   PASS (a diff reading, never executed) marks a row ALREADY SETTLED and the human
   walks past it. Under the creator's own base rates, ~half of those skipped rows
   are wrong. (W2)
3. **"Provisional" lives in a chat message, not in the record.** Nothing in the
   published Jira human summary, the tracker, or the suite marks automated verdicts
   as pending human confirmation, and nothing ever checks whether stage 10 was run
   at all. A ticket whose tester never hands the sheet back is permanently "settled"
   by machine verdicts. (W3)

**Second divergence:** "analyse gaps" runs, by default, as a notification rather
than a step. Auto-default grooming presents findings and continues; open questions
reach the ticket only *bundled with the publish confirmation*, after checklist and
test cases were already generated on the unresolved text. On EP-53978, five
unanswered grooming questions each became a blocked or contested case downstream —
the run report's Input category was 🔴 for exactly this. (W4)

**Third divergence:** "find gaps between code and requirements" is implemented in
one direction only. Code-review checks requirement→code (per test case); nothing
checks code→requirement — changed behaviour with no covering REQ is invisible by
construction, and pr-summary is explicitly forbidden from comparing code to
requirements. (W5)

**The three highest-value changes:**

1. **Gate the settle-the-truth actions on human verification** — move the "QA
   passed" story note / transition offer after stage-10 ingestion (or label it
   "automated only — pending manual verification"), and stamp the step-6 human
   summary with a `Provisional — N cases pending manual verification` line. (W1+W3;
   edits: `qa-pipeline-code/SKILL.md` step 8, `results-comment-template.md`.)
2. **Stop skipping machine-settled High-risk rows in the run sheet** — every
   `[risk: High]` case with a machine-only PASS gets a VERIFY row (short-form
   re-check), not an ALREADY SETTLED skip. This is the cheapest way to make the
   "half of AI results are wrong" premise load-bearing instead of aspirational. (W2;
   edits: `qa-manual-runsheet/SKILL.md` step 2, `runsheet-format.md`.)
3. **Post grooming's open questions to the ticket immediately after stage 2**, not
   bundled with the publish preview — the auto-run continues regardless, but the PM
   clock starts four stages earlier, which is the entire point of shift-left. (W4;
   edit: `qa-pipeline-docs/SKILL.md` step 2.)

**Over-engineering, one line:** the dual-path case transport (QA Service suite vs
fenced Jira archive, with the structural-checks-only exception block and a
connector-absent dead end) is the most rule-dense, most fragile subsystem in the
plugin and exists to save Jira characters; one canonical transport would delete
roughly a fifth of the orchestrators' text. (W6, section F.)

---

## A. Structure and step ordering

### Actual sequences (as written)

**qa-pipeline-docs:** session-name nudge → 1 task-context → 2 requirements-grooming
(auto-default: present findings, continue) → 3 qa-checklist → 4 qa-test-cases →
5 qa-run-analyzer → 6 publish (ONE confirm: new QA sub-task + checkbox tracker
comment + QA Service suite; archive comment only when no suite; open grooming
questions drafted as an opt-out story comment inside the same preview).

**qa-pipeline-code:** step 0 gather/restore (env check, same-session shortcut, suite
→ rebuild test-cases/checklist/requirements, archive fallback, resume mode with
Completeness headers, branch derivation with 4-level fallback) → 1 pr-summary →
2 code-review → 3 api-testing → 4 web-testing → 5 qa-run-analyzer → 6 post results
(count gate → confirm → two comments + suite write-back) → 7 offer bug filing →
8 hand the story back (reassign / story note / transition) → 9 qa-manual-runsheet
(pause for throwaway event) → post-publish verification (always last) → 10
qa-manual-results (deferred, separate session).

### Assessment

The docs order is coherent and genuinely shift-left-capable: it needs only the
ticket, and the "When to run (shift-left)" section is honest that running at QA
time is "strictly worse". The code order is also mostly right, and two previously
wrong orderings were fixed for the right reasons: the run sheet moved to the end of
the code phase (89 rows vs 11 — `qa-pipeline-code` step 9 explains it), and the
analyzer-before-publish gap is now patched by the mandatory post-publish
verification (0.16.0).

Where the label outruns the reality: **the code phase is testing-after-the-fact by
nature — fine — but the docs phase's shift-left value depends entirely on grooming
answers reaching a human early, and the default mode defers that to the publish
confirmation** (see W4). "Shift-left" holds for *when the pipeline can run*; it
does not yet hold for *when its questions get asked*.

**W1 — the handback precedes human verification (rank 1).**
- *Cost:* a story can be transitioned "QA done" and carry a "✅ QA passed" note on
  verdicts the architecture itself calls provisional. If ~half of AI PASSes are
  wrong, this ships wrong "done" signals to managers and devs as the pipeline's
  default choreography — the exact failure the creator built stages 9/10 to prevent.
- *Evidence:* `qa-pipeline-code/SKILL.md` step 8 ("Verdict ✅ PASS: offer to post
  the short 'QA passed' note to the PARENT story … and to apply the 'QA done'
  transition") runs before step 9 (run sheet) and step 10, which itself states "the
  published verdicts are provisional until the manual results are ingested."
- *Fix:* in `qa-pipeline-code/SKILL.md`, split step 8: on FAIL, keep the reassign
  offer where it is (a machine-confirmed FAIL is actionable immediately); on PASS,
  defer the story note + transition offer to `qa-manual-results` step 4 (it already
  posts to Jira with a confirm pause), or — if the user insists at step 8 — title
  the note "✅ Automated QA passed (manual verification pending)". Mirror in
  `results-comment-template.md` ("Story note — QA passed").

**W7 — step/stage numbering is three different schemes (rank 10).**
- *Cost:* pure reader tax, but on the file the model must follow mid-run: the code
  orchestrator's title says "stages 5, 6, 7, 8, 9", its "How it runs" list numbers
  1–10 where item 3 is stage 7, and step 9 contains an unnumbered "always the last
  action" block plus step 10. The docs SKILL.md also carries a duplicated-line
  editing artifact ("in a fresh / chat. / chat. `qa-pipeline-code` ends…", lines
  218–220) — evidence the file has been truncation-damaged before (MAINTAINERS
  gotcha) and nobody re-read the ending.
- *Fix:* renumber "How it runs" to the stage numbers (5–10 + lettered orchestration
  steps), fix the duplicated line in `qa-pipeline-docs/SKILL.md` Final response.

---

## B. Coverage of the intended process

| Intent point | Where | Verdict |
|---|---|---|
| Learn the task | `task-context` (fields per type, comments mandatory, sub-task folding, impact scan, injection quarantine) | **Well implemented** |
| Gather all relevant documentation | `task-context` AC-on-Confluence as required step; attachments; existing-suite pull | **Implemented, one weak edge** (attachments depend on the user uploading; video unprocessed — recorded honestly) |
| Analyse gaps | `requirements-grooming` 4-question method, seam checks, suite contradictions | **Method strong; default mode weak** (W4) |
| Cover ALL the AC | checklist/test-cases "every requirement has ≥1 check/case" self-checks + analyzer orphan check + `reconcile_counts.py` | **Enforced from REQ-1 down; unverified above it** (W8) |
| Machine- and human-readable cases | md file + QA Service suite (machine); checkbox tracker + runsheet (human) | **Well implemented — arguably four copies, see F** |
| Code-vs-requirements gap detection | `code-review` per test case | **Half implemented** — requirement→code only (W5) |
| API testing | `api-testing` + absence-check-protocol | **Well implemented** (strongest stage contract in the repo) |
| Browser testing | `web-testing`, Playwright/extension backends, routed-in cases | **Well implemented** |
| Per-scenario test data for manual checks | `qa-manual-runsheet` (provision → verify → baseline → sheet) | **Well implemented** — clearly born of real pain |
| Human as final arbiter | stages 9+10, retraction convention, ⚠ CURRENT VERDICT | **Machinery exists; choreography undermines it** (W1–W3) |

**W4 — gap analysis is a notification, not a step, in the default mode (rank 4).**
- *Cost:* checklist and test cases are generated on requirements known to be
  ambiguous or contradictory; each unanswered question becomes blocked/contested
  cases downstream. EP-53978: Input quality 🔴, "five docs-phase clarification
  questions were never answered and each one turned into a blocked or contested
  case downstream" (`EP-53978-run-report.md`). The PM sees the questions only when
  the user confirms the publish — after all four stages have run.
- *Evidence:* `qa-pipeline-docs/SKILL.md` step 2: "**Auto-default (no pause).**
  Present the grooming findings … then continue WITHOUT waiting — treat every
  finding as 'skip'… Open items → ticket (shift-left), **bundled with publish**."
- *Fix:* in `qa-pipeline-docs/SKILL.md` step 2, post the drafted open-items comment
  to the ticket **immediately after grooming** (it is a comment on the user's own
  ticket — a low-risk write; if a confirm is still wanted, make it a 30-second
  inline yes/no at step 2, not a bundle at step 6). Keep the regenerate-from-stage-2
  path as is. The pipeline keeps its autonomy; the PM clock starts 4 stages earlier.

**W8 — the "all AC covered" guarantee starts at REQ-1, not at the AC page (rank 7).**
- *Cost:* the enforced coverage chain (REQ → checks → cases → verdicts) is only as
  complete as the AC→REQ extraction, and that seam is verified by nothing except
  the same agent that wrote it ("Verification before saving" in `task-context` is a
  self-check, and grooming/checklist are forbidden to consult the tracker). An AC
  bullet dropped at stage 1 is invisible to every later check — the analyzer's
  traceability check begins at the requirements file.
- *Evidence:* `qa-run-analyzer/SKILL.md` §1 checks "Every REQ-N in the requirements
  file has ≥1 checklist item" — no check reaches back to `<KEY>-context.md`'s
  Requirements section or the Confluence AC. `requirements-grooming/SKILL.md`: "Do
  not go to the tracker… The context file is the only source of truth."
- *Fix:* cheap version: `qa-run-analyzer/SKILL.md` §1 gains one check — when
  `<KEY>-context.md` is present, every numbered/bulleted item in its Requirements +
  "Additional requirements (from comments)" sections must map to a REQ-N (grooming
  already numbers "in the order the items appear", so this is a count/ordering
  comparison, mechanisable in `reconcile_counts.py`).

**W5 — no reverse (code→requirements) gap detection (rank 5).**
- *Cost:* the creator's "find gaps between code and requirements" also means "the
  PR does things no requirement sanctioned" — scope creep, side effects, shipped
  behaviours with no case. As wired, those are invisible: code-review "Do not look
  for bugs unrelated to the test cases. Do not analyze pre-existing code that was
  not changed in the PR"; pr-summary "Do not compare the changes against the task
  requirements." EP-53978's two most important product defects (RISK-CR-2/3) were
  found only because stage 7 improvised risk-chasing rows — since legalised, but
  risk rows come from *code-review findings*, which are themselves case-driven.
- *Evidence:* quotes above; `EP-53978-flow-gap-analysis.md` G6 ("the coverage check
  is ID-shaped: it cannot see a behaviour that has no REQ id").
- *Fix:* smallest sufficient change: `pr-summary/SKILL.md` gains a required
  "Behaviours touched" list (from the diff only — endpoints/settings/state fields
  changed, one line each; it already does 90% of this per file), and
  `code-review/SKILL.md` gains a closing step: any pr-summary behaviour that no
  test case exercises is listed under "Unmapped changes" in the report; the
  analyzer flags a non-empty list 🟡. No new stage needed.

---

## C. Integration seams

| Seam | Contract | Validated? | Degraded mode |
|---|---|---|---|
| Working-dir files | explicit (`<KEY>-<stage>.md`, delete-and-recreate) | analyzer + reconcile script + Completeness headers | fresh chat → rebuild from Jira/suite; **good** |
| Jira QA sub-task | `publish-config.md` (label, type id, JQL, supersede rule) | count gate before posting; post-publish verification re-reads | no sub-task → clear instruction; **good** |
| QA Service suite | `qa-service-publish.md` (very thorough, empirically calibrated) | `get_suite` verify pass + analyzer bucket 4 | connector absent → "silently-but-visibly" skip — **but see W6** |
| `.env` credentials | search order stated identically in step 0 / api-testing / web-testing | step-0 environment check up front | pause-and-ask; **good** |
| Cowork ↔ Claude Code | MAINTAINERS table + split-run PARTIAL protocol | resume mode + completeness headers | works, at high rule cost (see F) |
| Subagent dispatch | stages 5–7 isolated; ≤10-line returns; pauses pre-resolved | — | inline fallback stated; **good** |

One place that tells a newcomer how a ticket flows end to end: README "How the flow
works" + MAINTAINERS "Where to run each stage" — together they do the job and match
the skills. (Minor drift: the *installed* plugin descriptions lag the repo — e.g.
the installed `qa-pipeline-code` description omits stage 9's pause and says "stages
5, 6, 7, 8" — consistent with the read-only-cache model, but worth a republish.)

**W6 — the suite-or-archive dual path has a dead end, and the environment matrix
never mentions the QA Service connector (rank 3).**
- *Cost:* since 0.11.2, when the docs phase publishes a suite it does **not** post
  the fenced archive. The code phase's fallback chain assumes archive-exists-iff-
  no-suite. So: suite published, and the code-phase session (Claude Code, where
  stages 5–7 must run per MAINTAINERS) *doesn't have the QA Service connector* →
  no suite access AND no archive → step 0's own terminal branch: "neither available
  → tell the user to re-run `qa-pipeline-docs` (or attach the files)". A full docs
  re-run (or manual file ferrying — the thing the design exists to eliminate) is
  the recovery path for a merely-missing connector. And MAINTAINERS' "Where to run
  each stage" table lists Jira, BB token, `.env`, Chrome — but never the QA Service
  connector as a per-environment requirement, so the dead end is undocumented.
- *Evidence:* `qa-pipeline-code/SKILL.md` step 0 ("no suite line, or no connector →
  fall back to the fenced archive comments, which the docs phase posts in exactly
  that case"; "neither available → tell the user to re-run qa-pipeline-docs");
  `qa-pipeline-docs/SKILL.md` step 6 ("QA Service suite published → skip the
  archive comment"); `MAINTAINERS.md` environment table.
- *Fix:* either (a) always post the archive (accept the ~45k chars — it is one
  comment on a working ticket, and it removes an entire failure mode plus half of
  step 0's branching), or (b) keep the dedup but add the QA Service connector to
  MAINTAINERS' environment table as required-for-code-phase and make step 0's
  environment check verify it *up front* alongside `.env` — not at extraction time.
  (a) is the lean choice; see section F.

---

## D. Best practices

### QA engineering lens

- **Traceability:** exemplary. Stable REQ-IDs across five files, suite trace-graph
  edges, count gates, a mechanical reconcile script with a self-test. Keep.
- **Risk-based prioritisation:** present and threaded (impact×likelihood at
  grooming, informed by bug history; High-first execution in stages 7/8 so a
  truncated run covers what matters). Keep. One gap: risk never influences *depth*
  (a High-risk requirement gets the same standard coverage level as a Low one —
  `test-case-design-rules` extended level is user-opt-in only).
- **Entry/exit criteria:** every stage validates inputs and has "verification
  before saving"; Completeness headers (0.17.0) give resume real exit criteria.
  Good.
- **Test data management:** strong at stage 9 (explicit attributes, per-counter
  fixtures, verified baselines, credential hygiene); adequate in stage 7
  (snapshot-and-revert, throwaway entities).
- **Defect lifecycle — found→filed is solid; filed→retested does not exist (W9).**
  - *Cost:* after step 8 reassigns a failing story to dev, no skill defines what
    happens when the fix comes back. The next action is presumably a full re-run of
    `qa-pipeline-code`, which re-executes everything rather than the failed cases —
    workable but wasteful, and nothing says even that much. The bug's `qa-pipeline`
    label and the suite's `bug <KEY>` note lines are the raw material for a retest
    scope; nothing consumes them.
  - *Evidence:* `qa-pipeline-code/SKILL.md` step 8 ends at the reassignment;
    no skill's triggers mention "retest"/"verify the fix".
  - *Fix:* a paragraph, not a stage: in `qa-pipeline-code` step 0, add a "retest
    mode" — when the QA sub-task's newest human summary is ❌ FAIL and the user says
    the fix landed, scope the run to the FAIL/FAIL CONFIRMED cases + their REQ
    siblings, and post results under the same conventions. (Reuses everything that
    exists.)
- **Regression strategy:** deliberately out of scope ("the ticket-scoped pipeline
  does not do regression testing" — pr-summary), made visible via blast-radius +
  analyzer 🟡, and partially compensated by the per-feature suite accumulating
  regression cases. Honest and acceptable for a solo operator; do not add more.
- **Independence of verification:** the analyzer re-checks with fresh instructions;
  post-publish verification re-reads Jira; api/web independently confirm/reject
  code-review FAILs (FAIL CONFIRMED/REJECTED is a genuinely good pattern). The
  remaining hole is one-sided: **FAILs get a second opinion, PASSes don't** — a
  code-review PASS is a single-agent verdict that removes the case from all runtime
  execution *and* marks the runsheet row settled (W2 below).

### Agent/skill design lens

- **Context economy:** code phase — good (subagents for 5–7, ≤10-line returns,
  suite/archive so nothing is pasted through chat). Docs phase — weaker: stages 1–4
  + publish all run inline in one chat with Opus/high/thinking recommended
  throughout; stages 3–4 are mechanical enough to dispatch the same way. Minor.
- **Determinism:** templates for every output; scripts where counting or parsing
  matters (`reconcile_counts.py --selftest`, `extract_archive.py`,
  `generate_pict_cases.py`). This is the right instinct consistently applied. Keep.
- **Pause points:** well chosen — every tracker/suite/live-event write is gated;
  everything else auto-advances. The publish previews say exactly what will be
  written. Keep.
- **Idempotency/re-runs:** thought through (new sub-task + supersede comment,
  delete-and-recreate files, append-with-dedup in the suite, newest-pair-wins
  comments). Keep.
- **Failure modes:** resume mode with completeness derivation is genuinely good
  post-0.17.0. The one crash-shaped gap: a stage that dies mid-write leaves a
  half-file that "delete completely and create a new one" masks on re-run — the
  Completeness header covers reports, not the docs-phase files (a truncated
  test-cases file would be caught only by the count gate; acceptable).
- **Self-verification:** every stage self-checks, the analyzer cross-checks, the
  orchestrator post-publish-verifies. If anything, there are now three layers doing
  overlapping arithmetic — see F.

**W10 — one internal contradiction the last fix round left behind (rank 9).**
- *Cost:* the model executing `qa-test-cases` gets two direct orders that conflict;
  whichever it reads last wins, and the loser silently shapes routing.
- *Evidence:* `skills/qa-test-cases/SKILL.md` — Input section (0.14.0): "such a
  case may carry `[API][UI]`… dual tag allowed"; Formatting section (pre-0.14.0
  text, still live): "on each test-case heading with exactly ONE tag
  (`### TC-REQ-N.M — <name>  [UI]`)."
- *Fix:* one-line edit to the Formatting bullet: "exactly one tag, or the dual
  `[API][UI]` tag where the provenance exception applies."

---

## E. The trust model

Trace of an automated verdict, creation → final record:

1. Born in a stage report (code-review / api-testing / web-testing) — with real
   defenses now: PASS-only-if-code-determined, absence protocol (provenance,
   positive control, lag, enumerate-or-downgrade), FAIL CONFIRMED/REJECTED
   discipline, evidence requirements, count gates.
2. Published at step 6: suite note line (`Run <date>: PASS|FAIL`), archive comment,
   human summary. Confirmed by the user — but the user is confirming *that the
   posting is correct*, not *that the verdicts are true*.
3. Step 8 may convert the aggregate into a story-level "QA passed" + transition
   (W1).
4. Step 9 converts per-case verdicts into ALREADY SETTLED runsheet rows the human
   is told to skip (W2).
5. Step 10 — **if and only if** the tester hands the sheet back and someone invokes
   it — reconciles, retracts (SUPERSEDES + ⚠ CURRENT VERDICT), and corrects Jira +
   suite. The retraction machinery itself is excellent.

So: the *disagreement loop is load-bearing when it runs, and optional in whether it
runs*. What forces human confirmation before a verdict becomes truth? Nothing
structural — only the user's habit, which is exactly what the creator said the
architecture should not rely on.

**Share of cases that can settle with no human ever looking:** all code-review
PASSes (post-0.17.0 narrowed, but still a single reading of a diff — on EP-53978
this class was 58/89 before the narrowing; expect it to remain the largest bucket),
plus all api-/web-testing PASSes that satisfy the protocol, plus N/A. The runsheet
skips them; stage 10 ingests only walked rows; no counter anywhere reports "N
machine PASSes never human-verified" (the 0.17.0 summary line covers code-reading
PASSes only, not runtime PASSes). Realistically **half to two-thirds of a run's
cases can become settled truth machine-only** — under the creator's stated error
rates, that is the pipeline's largest remaining exposure.

**W2 — the runsheet optimises against the trust model (rank 2).**
- *Cost:* the tester's attention is directed away from machine PASSes — the
  population the creator says is ~50% wrong. The 89→11 gain is real, but it is
  purchased with exactly the trust the intent forbids, and High-risk cases get no
  exception.
- *Evidence:* `qa-pipeline-code/SKILL.md` step 9 ("marks the rows the machine
  already settled, and leaves the tester the remainder");
  `qa-manual-runsheet/SKILL.md` step 2 ("ALREADY SETTLED — an existing verdict file
  already answers it. Carry the verdict and its source so the human skips it.").
- *Fix:* in `qa-manual-runsheet/SKILL.md` step 2 + `runsheet-format.md`: ALREADY
  SETTLED splits into SETTLED (runtime-verified PASS with protocol-grade evidence,
  Low/Medium risk → skip) and **VERIFY (spot-check)** — mandatory for machine
  PASSes on `[risk: High]` requirements and for all code-review-only PASSes, as a
  one-line short-form row. The sheet stays lean (on EP-53978 this adds roughly the
  High-risk PASS count, not 78 rows) and the human's effort lands where his own
  error model says the lies are.

**W3 — nothing marks or tracks "provisional" in the record (rank 2, tied).**
- *Cost:* a ticket whose sheet never comes back looks identical to a fully
  human-verified one — in Jira, in the suite, and to the next run's step-0
  reconciliation. The trust model exists only in the transcript of a finished chat.
- *Evidence:* `results-comment-template.md` human summary has no
  pending-manual-verification line; `qa-pipeline-code` step 10 only says to "end
  THIS run by telling the user that step exists"; no skill or check ever asks
  "was qa-manual-results run for this ticket?" (the analyzer's retraction-integrity
  check fires only when contradicting artifacts already exist).
- *Fix:* two small edits. (1) `results-comment-template.md`: add one line to
  Comment 2, above the health line — `Status: PROVISIONAL — automated verdicts;
  manual verification pending (N cases on the run sheet)`, which stage 10's
  summary then supersedes by saying so. (2) `qa-run-analyzer/SKILL.md` §1: when
  runsheet outputs exist but no `<KEY>-manual-results.md` does, report 🟡 "manual
  results never ingested" instead of silence.

---

## F. What is over-engineered

The inverse ledger. Everything below works; the question is maintenance cost for a
solo operator versus what it buys. Ranked by deletable mass.

**W6 (again) — the dual-path case transport.** Suite-first with archive fallback,
the structural-checks-only fenced block (which exists *only* because the checklist
is a separate artifact from the cases), 32k splitting with part re-joining,
`extract_archive.py`, supersede comments, and a reconciliation pass whose rules
live in a third file. This subsystem exists to save ~45k Jira characters per
ticket. It costs: the W6 dead end, ~120 lines across the two orchestrators, and a
step 0 that is now the hardest part of the plugin to follow. **Simplification:**
always post the archive (one transport, suite remains the system of record for
content), or accept the connector as a hard code-phase dependency and delete the
fallback entirely. Lost: some Jira tidiness. Gained: one failure mode and one
branching tree gone.

**The qa-checklist stage as a separate artifact.** The checklist's unique payload
is (a) structural presence/label checks and (b) atomic decomposition discipline.
Its cost: a fifth file, a dedicated Jira exception block, "rebuild the checklist
from the suite PLUS the structural block" logic in step 0, and a checklist↔cases
delta no check reconciles. A lean version folds structural checks into the
test-cases file as a `## Structural checks` section (they are already executed by
web-testing from a list, not from case blocks) and lets qa-test-cases decompose
directly from requirements. Lost: the standalone checklist as a manual-testing
reference (the runsheet has superseded that role) and fidelity to the original DOU
template. This is the biggest single simplification available; it touches many
files, so do it only when the current shape next causes a real failure.

**Three stacked routing-override mechanisms.** Channel tag → dual `[API][UI]` tag →
code-review `RE-ROUTE [UI]` → api-testing "Route to web-testing" — each added in
response to a real incident, and each individually justified; together the routing
model needs an analyzer integrity check just to confirm cases didn't vanish between
mechanisms. A simpler invariant would subsume them: *the tag is advisory;
web-testing's scope = everything QA/FAIL not conclusively executed by an earlier
stage*. Candidate for the next consolidation pass, not urgent.

**Status vocabulary sprawl.** Across the three verdict stages there are now ~14
statuses (PASS, FAIL, FAIL CONFIRMED, FAIL REJECTED, QA, N/A, PARTIAL, BLOCKED,
BLOCKED (unverified), NOT-TESTABLE, NOT-TESTABLE (instrumentation), NOT EXECUTED,
SPEC-DEFECT, OBSERVATION, RE-ROUTE [UI]) with per-stage semantics ("QA is an INPUT
status, never an output"). Every one is defensible; the set has no single home —
it lives in three Classification sections plus templates plus the script's regex.
**Fix at zero behaviour change:** one shared `references/status-vocabulary.md`
(definitions + which stage may emit which), pointed to by all three stages, the
analyzer, and `reconcile_counts.py`'s comment header — so the next status lands in
one place.

**Small pure-noise items:** the session-rename ritual in both orchestrators (two
paragraphs to ask the user to rename a chat); the model-settings banners
(recommendations, fine, but repeated per orchestrator and README); the
docs-orchestrator's duplicated final-response line (W7). Cheap deletions.

**What is *not* over-engineered despite its bulk:** `qa-service-publish.md` (every
rule is empirically calibrated against a measured failure — this is what a
reference should look like); the absence-check protocol; the resume/Completeness
machinery; the secret-hygiene rules in MAINTAINERS and runsheet step 7 (84
passwords were once one `git add -A` from a commit; the paranoia is priced
correctly).

---

## What to keep exactly as is

- **The grounding/anti-invention chain** (task-context prohibitions → grooming
  "do not turn ambiguity into fact" → test-cases grounding rule + no-vague-words).
  It demonstrably held on real runs and is the hard part of generated test design.
- **`absence-check-protocol.md`** — provenance, positive control, measured lag,
  enumerate-or-downgrade. The best distillation of a false-pass lesson in the repo.
- **FAIL CONFIRMED / FAIL REJECTED** as the code-review→runtime handshake, and the
  rule that FAILs need evidence while doubt prefers QA/BLOCKED over PASS.
- **The retraction convention** (append-only SUPERSEDES + single ⚠ CURRENT VERDICT
  first line) and stage 10's join-by-TC-id-never-position rule.
- **Count gates + `reconcile_counts.py --selftest`** and the refuse-to-post rule.
- **Write safety** (snapshot-and-revert, throwaway entities, never target real
  client data, the stage-9 authorisation pause).
- **The prompt-injection quarantine** in task-context, binding downstream.
- **`publish-config.md` as the only place team-specific values live.**
- **MAINTAINERS' update-recipe step 1** (a run-report 🔴 with neither an
  implementation nor a recorded rejection is an open defect) — the improvement
  loop, made enforceable.
- **The runsheet's six rules** (one login per row, Expect per row, name the
  surface, positive control, probe every blocker, no shared counter fixtures).

---

## Reconciliation vs PIPELINE-REVIEW-2026-07-30.md

Read after the above was written.

**Confirmed by my independent pass.** Findings 1–10 are genuinely fixed in the
text as of 0.13.1–0.17.0 — I verified while reading, without knowing the list: the
absence protocol exists and binds stages 7/8 + analyzer (F1); `qa-manual-results` +
retraction convention exist and are wired (F2); `RE-ROUTE [UI]` + dual tags +
routed-in scope exist (F3, though see W10 — the "exactly one tag" amendment its fix
prescribed only half-landed); MAINTAINERS step 1 closes the loop (F4); broad
`.gitignore` + explicit-path commits + runsheet secret scan (F5); post-publish
verification (F6); satisfiable web-testing check + mechanical counts + count gates
(F7); narrowed code-review PASS + Completeness headers + resume re-dispatch (F8);
legalised improvisation + SPEC-DEFECT (F9); requirements restore (F10). Of the open
findings 11–17, I independently converged on 16 (auto-default grooming — my W4
extends it: don't just annotate the publish preview, move the ticket comment to
stage 2), on the substance of 14 (authority juggling — my W6 found a concrete dead
end its text implies but does not name: suite-published + connector-absent code
phase has *neither* source), and on 12 (my W5 is the same blind spot with a
smaller fix: an "Unmapped changes" closing step in code-review rather than a new
analyzer diff).

**What I found that it did not.**
- **W1** — the step-8 handback ("QA passed" note + transition) fires on automated
  verdicts *before* the run sheet and manual results exist. The prior review fixed
  how wrong verdicts get corrected; it did not notice the pipeline still
  *broadcasts* them to the story first.
- **W2** — the runsheet's ALREADY SETTLED skip logic contradicts the creator's own
  error model; no High-risk spot-check exception exists.
- **W3** — "provisional" is a chat utterance, not a record property; nothing ever
  detects that stage 10 was never run for a ticket.
- **W6's dead end** and the missing QA Service connector row in MAINTAINERS'
  environment matrix.
- **W9** — no filed→retested leg in the defect lifecycle.
- **W10** — the intra-file dual-tag contradiction left by the F3 fix itself.
- The whole of section F: the prior review ran one direction only (what is
  missing); nobody had asked what should be *removed*.

**Where I disagree with it.**
- **Finding 14's proposed `<KEY>-verdicts.tsv` ledger:** I would not build it. It
  adds a fifth verdict surface to a system whose problem is already too many
  half-authoritative surfaces; the 0.15.0 ⚠ CURRENT VERDICT line plus my W3
  provisional marker cover the same need inside surfaces that already exist. If
  contradictions still slip through after that, revisit.
- **Direction of travel:** the review's fixes were all additive, and 0.13.1–0.17.0
  added a large amount of rule-mass in one day. Each addition is individually
  correct; cumulatively the orchestrators are approaching the size where the
  executing model's compliance — the thing every rule depends on — degrades. The
  next release after the intent-critical items (W1–W4) should be a *consolidation*
  release (W6 transport choice, status vocabulary home, routing invariant), not
  another additive one. The prior review's own Finding 4 ("lessons must reach
  tracked files") is right; the corollary it missed is that a lesson can also be
  paid for by deleting the rule it obsoletes.
