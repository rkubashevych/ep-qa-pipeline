# Consolidation proposal — subtractive pass (zero behavior change)

Replacement files mirror repo paths under `consolidation-proposal/`.
Only the 8 files below change; everything else in the repo is
untouched. Editing stance: dedupe + tighten; every incident-backed
rule retained (moved or deduped, never weakened) unless listed under
"Proposed exceptions".

## Line counts

| File | Before | After | Δ |
|---|---|---|---|
| skills/qa-pipeline-code/SKILL.md | 540 | 451 | −89 |
| skills/web-testing/SKILL.md | 539 | 354 | −185 |
| skills/api-testing/SKILL.md | 272 | 230 | −42 |
| skills/qa-pipeline-docs/SKILL.md | 241 | 209 | −32 |
| skills/qa-manual-runsheet/SKILL.md | 366 | 345 | −21 |
| skills/code-review/SKILL.md | 366 | 365 | −1 |
| skills/qa-test-cases/SKILL.md | 283 | 278 | −5 |
| skills/qa-run-analyzer/references/status-vocabulary.md | 50 | 87 | +37 (new routing-invariant home + relocated "write the doubt" rule) |
| **Total** | **2657** | **2319** | **−338 (−12.7%)** |

All seven SKILL frontmatter blocks are byte-identical to the originals
(mechanically diffed) — no `description` changed.

## The routing-invariant merge (the one authorized semantic merge)

**Before:** four constructs each carried their own routing rules —
the docs-phase channel tag + dual `[API][UI]` semantics
(qa-test-cases, ~18 lines), web-testing's "two overrides beat the
channel tag" + routed-in scope stated THREE times (Input, Step 1,
Verification), api-testing's ownership claim + "Route to web-testing"
prose, and code-review's `RE-ROUTE [UI]` rationale.

**After:** one invariant, stated once in
`qa-run-analyzer/references/status-vocabulary.md` → "Routing
invariant — one rule, four recorded forms":

> The channel tag is advisory; web-testing's scope = every QA/FAIL
> case not conclusively executed at runtime by an earlier stage, plus
> every routed-in and spot-check row; every QA/FAIL case of any
> channel appears exactly once across the run.

Each stage now states its own mechanics once and points there:
web-testing has a single "Scope — the routing invariant" section
(Step 1 and the pre-save verification refer to it; the mechanical
count check is retained verbatim in Verification); api-testing's
intro and `NOT-TESTABLE (instrumentation)` entry point to it;
code-review's `RE-ROUTE [UI]` entry keeps its definition + file+line
evidence rule and points to it; qa-test-cases keeps WHEN to dual-tag
and points to it for what later stages do.

**Outcome identity:** the browser still receives exactly — QA/FAIL
`[UI]` and `[API][UI]` cases, api-testing's "Route to web-testing"
rows, code-review `RE-ROUTE [UI]` cases; `[API]` cases are referenced
to the stage-7 report (or "Not executed here" when it doesn't exist);
`[mobile]`/`[export/email]` go to "Not executed here" (api-testing's
HTTP-fetchable-export exception unchanged). Construct names are
preserved everywhere; templates and `reconcile_counts.py` untouched;
the analyzer's routing-integrity checks (untouched file) still match
the section names.

## Per-cut ledger

Classes: `duplicate (home: …)` · `judgment-restating` ·
`merged into routing invariant` · `superseded by <rule>`.

### qa-manual-runsheet/SKILL.md
1. Entire second retest section ("Retest runs — detect, don't
   assume") → **duplicate (home: the file's own "Retest runs — detect,
   do not wait to be told")**. The two sections were near-identical
   (0.18.3 legacy); merged, keeping every unique clause: scope comes
   from qa-pipeline-code retest mode, retired-accounts-only use of
   prior testdata.json, abandoned-fixtures cleanup note, "short by
   design".
2. "If a verdict recorded in the suite is later found wrong…"
   standalone paragraph → **duplicate (home: merged into the
   Source-of-truth bullet it repeats)**.
3. Input item 5's retest note → **duplicate (home: merged retest
   section)**.

### web-testing/SKILL.md
4. Env-credential search order (Step 4 Cowork note) →
   **duplicate (home: `api-testing/references/api-testing-reference.md`
   §0)**; the never-paste/never-print secret rule stays inline (hard
   rule, one sentence).
5. Routed-in scope rules stated 3× (Input ¶, Step 1 ¶, Verification ¶)
   → **merged into routing invariant** (one "Scope" section +
   pointers; Verification's mechanical completeness check kept).
6. navigation_paths.json structure + save format (Steps 3 & 7) →
   **duplicate (home: `references/browser-rules.md` → "Navigation
   memory")**.
7. Login step branching, USER_NAVIGATION_STEPS bookkeeping, Step 2
   prose, per-file "in the same chat it is available automatically"
   boilerplate, Step 8 bullet expansion, Output-file "one top-level
   heading" checklist → **judgment-restating** (behaviors kept in one
   sentence each: ask-on-placeholder, IS_NEW_PATH, single-latest-run
   file).
8. "Browser tool: see Execution backends" rule bullet →
   **duplicate (home: the Execution backends section two paragraphs
   down)**.
9. "If you write the doubt, you must classify it" full paragraph →
   **duplicate (home: status-vocabulary cross-stage rules — moved
   there; one-line statement + pointer kept in the stage)**.

### api-testing/SKILL.md
10. "owns all [API] items / web-testing will point at this report"
    intro → **merged into routing invariant**.
11. "If you write the doubt" full paragraph → **duplicate (home:
    status-vocabulary)** — same as #9.
12. Status-entry prose that restated status-vocabulary rows
    (NOT EXECUTED, BLOCKED probe mechanics) → **duplicate (home:
    status-vocabulary table)**; unique incident cites kept ("nine
    across two runs", `photoSave`).
13. Scope-extension rationale prose → **judgment-restating** (rules +
    one-line provenance kept).

### qa-pipeline-code/SKILL.md
14. Header note "Stage 7 runs the [API] cases; stage 8 runs the [UI]
    cases" → **merged into routing invariant** (stage bullets name
    their scope already).
15. Stage 3/4 bullets restating stage internals (read-only default,
    snapshot-and-revert, admin REST/legacy/exhibitor coverage) →
    **duplicate (home: the stage SKILL.md files, which the
    orchestrator must read in full)**. Pauses kept verbatim.
16. `.env` variable enumeration in Input → **duplicate (home:
    api-testing SKILL / reference §0)**.
17. Wave-2 rationale, step-9 "why at the end" rationale, step-8
    decision-question rationale → **judgment-restating compression**
    (each rule kept with its one-line incident cite: PROVISIONAL
    prevented nothing / 89-vs-11 rows / 3-of-4 answered decisions;
    full narratives live in CHANGELOG 0.19.0-G, 0.13.0, 0.19.0-F).
18. Final response line "confirmation that BOTH comments (archive +
    human summary) were posted" → **superseded by the two-wave rule
    (0.19.0 G)**. This was a live contradiction: step 6 and the
    post-publish verification forbid posting the human summary, while
    the final response claimed it was posted. Corrected to "wave-1
    comments posted; human summary written but deliberately NOT
    posted". This is the only substantive text change in the pass —
    it aligns the file with its own binding rule.

### qa-pipeline-docs/SKILL.md
19. Measured-savings narratives in the publish step (99.3%/15k/45k
    chars) → **judgment-restating compression** (numbers kept as
    parenthetical citations; every gate/rule kept: count gate, fence
    lengths + read-back, ~32K split, supersede comment, bare-URL
    rule, structural-checks-only block).
20. Stage bullets 1/3/4 boilerplate → **judgment-restating** (the
    no-pause defaults and output names kept).

### code-review/SKILL.md
21. `RE-ROUTE [UI]` entry's routing rationale (tag assigned blind /
    docs phase) → **merged into routing invariant** (definition,
    evidence rule, "replaces QA never PASS/FAIL" kept). Nothing else
    changed in this file.

### qa-test-cases/SKILL.md
22. Dual-tag downstream semantics ("web-testing takes dual-tagged
    cases into scope; api-testing may run the API half but may not
    record the final PASS; code review may RE-ROUTE and the re-route
    wins") → **merged into routing invariant** (WHEN to dual-tag, the
    counting rule, and the both-headings formatting rule stay here
    untouched).

**Ledger totals:** duplicate 10 · judgment-restating 6 · merged into
routing invariant 5 · superseded 1. Zero rules deleted outright; two
rules relocated to a single home (env search order → reference §0
pointer; "write the doubt" → status-vocabulary).

## Proposed exceptions (owner to decide — not applied)

1. **`skills/qa-pipeline-code/references/progress-protocol.md`
   (87 lines) — delete.** It shipped with retro proposal B (progress
   heartbeats), which 0.19.0 explicitly REJECTED ("process noise for
   a solo operator"), and it is referenced by no skill, template, or
   doc (verified by grep). It is not an incident-backed rule; it is
   the artifact of a rejected one. Repo files were not touched, so
   this is a recommendation only.
2. **"~half of machine PASSes are historically wrong" rationale**
   appears in qa-pipeline-code step 8, qa-manual-runsheet VERIFY, and
   results-comment-template. Kept in all three this pass (it is
   rationale, cheap, and each spot is a decision point), but it is a
   candidate for a single home (status-vocabulary or the template) if
   a further pass is wanted.
3. **Retro-evidenced deletion candidates: none found.** The rules the
   five retro runs violated (positive control, second observation,
   probe-before-BLOCKED, code-read-is-a-claim) were all strengthened
   in 0.19.0, not obsoleted — they are the opposite of deletion
   candidates. Rules the runs credited (retraction convention, count
   gate, join-by-TC-id, dynamic fences + read-back, SPECIAL
   ATTENTION, stage-9 restore discipline) are all retained verbatim.

## Deliberately untouched

- The checklist→test-cases fold (deferred until it causes a failure)
  and the suite-vs-archive transport (0.18.0 chose the pre-flight
  check — kept as-is in step 0).
- `reconcile_counts.py`, every `references/output-template.md`, and
  every frontmatter `description`.
- Two-wave publish, retraction convention, absence-check protocol,
  provisioning-rules, secret rules, count gates — substance unchanged
  everywhere they appear.
- qa-run-analyzer/SKILL.md (its checks reference section names that
  all still exist), pr-summary, task-context, requirements-grooming,
  qa-checklist, qa-manual-results, all other references,
  MAINTAINERS.md, CLAUDE.md, README.md, evals/triggering.md,
  fixtures.

## Verification results

- **Frontmatter:** all 7 changed SKILL.md frontmatter blocks are
  byte-identical to the originals (mechanical diff) → every ✅/❌ line
  in `evals/triggering.md` routes exactly as before, since discovery
  sees only the descriptions. Walked the list against the unchanged
  descriptions: no change in any should-fire / must-not-fire outcome.
- **Cross-references:** all 25 distinct `references/…`, `../…` and
  `scripts/…` paths appearing in the replacement files resolve to
  existing repo files (mechanical check). Inbound anchors still
  exist: "Split runs" (MAINTAINERS→qa-pipeline-code), "Structural
  checks", "Route to web-testing", "Not executed here", "Unmapped
  changes" (analyzer→stage reports/SKILLs), "Writing rules", "Result
  write-back", "Code phase — suite as the case source", "Retraction
  convention", "Navigation memory".
- **Docs-stage smoke (fixtures/EP-0000-context.md):** grooming and
  checklist skills are untouched; the qa-test-cases changes preserve
  numbering, grounding, BVA/technique selection, channel tagging
  (incl. dual-tag mechanics and counting) and the statistics gate —
  all five fixture-foot expectations (~6 REQs, badge-label
  Contradiction, BVA at 10/11, [UI]/[API] tag split, REQ-ID
  traceability) remain satisfiable from the consolidated text.
- **Behavior invariants spot-checked in the replacements:** every
  REQUIRED PAUSE retained (browser login, Jira write confirm,
  test-event authorisation, missing `.env`, missing frontend host,
  suite-named-but-no-connector pre-flight, retest full-vs-retest
  question, prior-run detection); count gates retained in both
  orchestrators; two-wave rule + narrow exception + source gate
  retained; resume completeness rule retained; retest three-tier
  scope retained; post-publish verification's four items retained;
  stage-9 secret scan retained.
