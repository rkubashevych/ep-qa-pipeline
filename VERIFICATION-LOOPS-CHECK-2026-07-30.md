# Verification-loops check — 2026-07-30

**Yardstick:** "Building verification loops in Claude Code with skills"
(claude.com/blog, 2026-07-22, Delba de Oliveira). **Subject:** the
`ep-qa-pipeline` plugin at version 0.18.2. Cold check, drafted before
reading the four prior review docs; reconciliation at the end.

## 1. What the article actually recommends

The post is short (~5 min). Its concrete, checkable recommendations:

**Built-in loops (try these first):**
- B1. `/verify` skill — build, run, observe the changes in your app.
- B2. Toolchain signals — Claude acts on linter/test/type-checker
  errors; *"a good practice is to list your exact build and test
  commands in CLAUDE.md so Claude doesn't have to infer them."*
- B3. Code Review (research preview) — managed multi-agent PR review;
  close the loop by commenting `@claude` (GitHub).
- B4. GitHub Actions — run a verification skill on every push/PR.
- B5. Spec validation — verify each change against a markdown spec.
- B6. Rubrics in Managed Agents — separate grader agent, failures loop
  back automatically.

**Writing custom loops:**
- C1. When you make the same small corrections after every feature,
  write the procedure down in plain English and encode it as a skill.
- C2. Pro tip: deterministic project-specific rules qualify ("reject
  any migration that drops a column without a backfill") — anything
  you keep enforcing by hand.
- C3. Make it a skill (skill-creator interview, or hand-written
  SKILL.md); verify the loop actually fires by invoking it on a fresh
  task.

**Four placements:**
- P1. Standalone — invoked deliberately; for cross-cutting checks.
  Signal you've outgrown it: you run it after every change.
- P2. Embedded — fires as part of the producing skill; only for
  skills you can edit; skip for cross-workflow checks.
- P3. Chained — one skill calls another at its end (Anthropic's own
  `/code-review` → `/simplify` → `/verify` → `/design`); wrapper
  skills for skills you can't modify; costs tokens, trades
  flexibility for automation.
- P4. On every PR — team infrastructure; hold off while the chain is
  still in flux.

**Closing process:** pick the most frequent manual follow-up → try
`/verify` → write it in plain English → make it a skill → confirm it
fires → chain.

## 2. Classification against the plugin

### 2a. Already implemented

The plugin is, structurally, a 13-skill implementation of this
article's thesis. Mapping to the article's vocabulary:

| Article item | Where in the plugin | Placement (article term) |
|---|---|---|
| C1/C2 — manual corrections encoded as deterministic loops | `skills/qa-run-analyzer/scripts/reconcile_counts.py` — every counting rule in its docstring "fixes a real defect from the EP-53978 run report"; `--selftest` gates trust in the script itself (the analyzer is instructed to distrust it and recount by hand if the self-test fails). Count gates: code-review TC count == test-cases TC count, executed == QA+FAIL+routed-in. | Toolchain-style deterministic signal inside a chained loop |
| P2 — embedded self-checks | "Before finishing, verify/check" sections in `task-context` (L338), `qa-checklist` (L167), `qa-test-cases` (L250), `web-testing` (L503); `qa-manual-runsheet` Step 4 (verify every fixture + baseline) and Step 7 (self-check before handover); api-testing/web-testing's BLOCKED-requires-`Probe:` rule (0.18.0); the see→locate→act→verify browser pattern. | Embedded |
| P2 — post-publish verification | `qa-pipeline-code` step 9's "Post-publish verification — always the last action of the run": re-read the Jira comments (don't assume), `get_test_case` sample of the write-back, no silent FAILs, ✅/❌ appended to the run report. | Embedded (in the orchestrator) |
| P3 — chained verification | `qa-run-analyzer` auto-called at the end of BOTH orchestrators — the exact analog of the article's `/code-review` → `/verify` chain, including its read-only grader character. The 13-stage pipeline itself is "several verified handoffs run end-to-end". `qa-manual-results` (stage 10) is a chained return-leg that goes *beyond* the article: the human's verdicts retract the machine's, with explicit SUPERSEDES lines. | Chained |
| P1 — standalone | `qa-run-analyzer` on demand ("analyze the run"); `reconcile_counts.py --selftest`; `fixtures/EP-0000-context.md` smoke test; `evals/triggering.md` walk. The latter two are standalone *manual recipes*, not encoded loops — see 2b. | Standalone |
| B5 — spec validation | `qa-run-analyzer/references/status-vocabulary.md` is the single spec the three verdict stages, the templates, and the counting script defer to; the fixture file ends with an explicit expectations block ("if any of that breaks after a skill edit, the edit regressed the pipeline"); the analyzer checks outputs against each stage's output-template. | Chained/standalone |
| B6 — grader agent | `qa-run-analyzer` *is* a grader agent for pipeline runs: read-only meta-review, 🔴/🟡/🟢 severities, three-bucket rubric (Pipeline/Input/Product), findings loop back via the MAINTAINERS "consume the last run's findings first — load-bearing" rule, which forces implement-or-record-rejection in the CHANGELOG. Self-hosted, not the managed service, but functionally the same loop. | Chained |
| B1 — build/run/observe the app | For the thing the pipeline exists to verify (ExpoPlatform product changes), stages 7–8 (`api-testing`, `web-testing`) are exactly this: execute the cases against the running system and observe. | Chained |
| C3 — confirm the loop fires on a fresh task | `evals/triggering.md` (0.18.2): should-fire / must-not-fire queries for all 13 skills, required after any description edit. | Standalone (manual) |

Verdict on this bucket: the article's core content — turn manual
checks into loops, prefer deterministic scripts, chain a verifier
after the producer — is not merely present but implemented more
rigorously than the article's own examples (the article has no
equivalent of "validate the validator" or human-retracts-machine).

### 2b. Applicable and missing

Only two items survive honest weighing. Both are for maintaining the
*plugin repo itself* — the pipeline's own runs are already saturated
with loops.

**G1 — No CLAUDE.md listing the exact verify commands (article B2,
its most specific actionable line).**
The repo has no `CLAUDE.md` (only `.claude/settings.local.json`). The
verify commands exist but live in MAINTAINERS.md prose, reached via a
README pointer — a fresh Claude session in this repo has to *infer or
be told* to find them, which is precisely what B2 says to eliminate.
The author's manual follow-ups that this would anchor: run
`python3 skills/qa-run-analyzer/scripts/reconcile_counts.py --selftest`,
run the `fixtures/EP-0000-context.md` smoke recipe, walk
`evals/triggering.md`, bump BOTH manifests, never `git add -A`, never
write skill files through the shell mount.
*Minimal fix:* a ~15-line root `CLAUDE.md`: "Read MAINTAINERS.md
before changing anything" + the four verify commands verbatim + the
two banned operations. Zero ongoing maintenance (it points, it
doesn't duplicate). Worth it for a solo operator: yes — it is the
cheapest item in the whole article and removes reliance on session
memory of the README chain.

**G2 — The repo's recorded defect classes have no deterministic
gate (article C2 applied to the plugin repo).**
Three defect classes that *actually occurred* are still enforced only
by prose gotchas and manual audit:
1. Dual-manifest version drift — plugin.json bumped, marketplace.json
   not → Update button silently dead (MAINTAINERS recipe step 5).
2. Broken cross-skill relative paths — three `../`-less references
   shipped until a manual audit caught them (fixed 0.18.1).
3. Shell-mount truncation / NUL padding — cut three files mid-sentence,
   twice ("verify every touched file still ends with its final
   section" is currently a human instruction).
All three are deterministic, token-free checks. A scan run for this
review found the tree currently clean: manifests agree at 0.18.2, no
NUL bytes, and one prose near-miss only
(`skills/api-testing/references/absence-check-protocol.md:13` names
`references/provisioning-rules.md`, which lives under
qa-manual-runsheet — correct in context, invisible to a naive
linter). So the gate is preventive, not curative — but each check
corresponds to a defect that has already happened here, which is the
article's exact bar for capture ("anything you keep having to enforce
by hand").
*Minimal fix:* one `scripts/verify_plugin.py` (~80 lines, no deps):
(a) plugin.json version == marketplace.json version; (b) every
`references/…` / `scripts/…` / `../<skill>/…` path mentioned in a
SKILL.md resolves; (c) no NUL bytes, every .md ends with a newline-
terminated non-blank tail; (d) frontmatter has exactly name +
description, no `<`/`>` (the 0.18.2 rule). Add one line to
MAINTAINERS recipe step 4 next to the selftest. Not a 14th skill —
a script, per the repo's own degrees-of-freedom convention.

### 2c. Applicable but deliberately not worth it

- **Automating the fixture smoke test** (making recipe step 4 an
  encoded loop). The three docs stages are LLM stages: automating
  means burning a full pipeline run plus a judge on every edit. The
  manual recipe at solo cadence is proportionate, and per-skill
  functional evals are already deferred twice with recorded reasons
  (CHANGELOG 0.18.1 "Not done"; 0.18.2 "rigor scales with audience").
  The article adds no argument that reverses that record.
- **skill-creator interview / hand-write a SKILL.md** — the skills
  exist; nothing to do.
- **Graduating the standalone recipes to embedded** — the article's
  "you run it after every change" signal has not fired: the smoke
  test and evals walk run per *release*, not per change. Standalone
  (as documented recipes) is the correct placement today.

### 2d. Not applicable

- **B3 Code Review (research preview) + `@claude` comments** —
  GitHub-only. Product code is on Bitbucket (both monolith and
  portal-ui); the plugin repo is a local personal git with no remote
  PR flow. Nothing to attach it to.
- **B4 GitHub Actions on every push/PR** — same, and the repo can't
  even run git on the Cowork mount. For product code, the pipeline
  *itself* is the per-PR gate, human-invoked — which matches the
  Bitbucket + human-in-the-loop reality better than a CI gate would.
- **P4 on-every-PR placement** — this is the article's "team
  infrastructure" tier; the plugin has one user, and the article
  itself says to hold off while the chain is in flux. Correctly
  absent.
- **B6 Managed Agents rubrics (the managed service)** — no managed
  agents in use; the analyzer already plays the grader role
  self-hosted. Adopting the service would duplicate it.
- **B1 `/verify` for the repo itself** — there is nothing to build or
  run: the plugin is markdown plus four small scripts whose only
  runnable check (`--selftest`) already exists.

## 3. Reconciliation with the prior reviews (read after drafting)

- **No contradictions.** The two skill audits already graded this
  ground: SKILL-BEST-PRACTICES-AUDIT's feedback-loop column and its
  praise list ("deterministic validators with self-tests … validates
  the validator"), and GUIDE-ALIGNMENT's R17 verdict ("Compliant,
  exceeds … implemented before the guide asked"). Section 2a agrees
  independently.
- **G2's link check is adjacent to, but not proposed by, prior work.**
  The best-practices audit found the three broken paths and proposed a
  path *convention* (its item 5, fixed in 0.18.1); no prior doc
  proposed automating the class. Same for the manifest-parity and
  truncation checks — both are recorded gotchas, neither has a gate.
- **G1 (CLAUDE.md) appears in no prior review** — all four reviewed
  the skills and orchestrators, not the repo-maintenance loop. Net-new
  from this article.
- **The eval-set deferral stands.** Recorded in 0.18.1 and re-affirmed
  in 0.18.2; section 2c independently reaches the same conclusion.
- **Consolidation-stance compatibility.** ORCHESTRATOR-DESIGN-REVIEW's
  closing position — the pipeline "added a large amount of rule-mass
  in one day … the next release should be a consolidation" — cuts
  against adding prose rules. G1 adds a pointer file, G2 replaces
  three human checklist items with one script; neither adds rule-mass
  to any SKILL.md. Both fit.

## 4. Bottom line

This article adds little to this repo — and that is a finding, not a
failure of the check. The plugin already implements the article's
thesis (encode manual checks; deterministic scripts for deterministic
rules; chain a grader after the producer; embedded self-checks) more
thoroughly than the article's own examples, and its GitHub-centric
built-ins (Code Review preview, Actions, on-every-PR gates) are
structurally inapplicable to a solo-maintained Bitbucket-adjacent
plugin. Of the article's ~12 concrete recommendations: ~7 already
implemented (several exceeded), ~4 not applicable, 2 real gaps —
both about verifying *the plugin repo* rather than pipeline runs,
both small: a ~15-line CLAUDE.md (G1) and one ~80-line deterministic
repo-lint script covering the three defect classes the repo has
already paid for (G2). Nothing here justifies new skills, new rules,
or reopening the recorded eval-set deferral.
