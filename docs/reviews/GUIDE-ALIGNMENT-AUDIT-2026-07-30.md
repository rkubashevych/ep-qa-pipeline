# Guide-Alignment Audit — ep-qa-pipeline vs "The Complete Guide to Building Skills for Claude"

**Date:** 2026-07-30
**Rubric source:** `The-Complete-Guide-to-Building-Skill-for-Claude.pdf` (33 pp., read in full; only rubric for §1–§3)
**Subject:** all 13 skills under `skills/`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, sampled `references/` and `scripts/`.
**Excluded:** `.git/`, `.playwright-mcp/`, root `EP-*` run artifacts.
**Method note:** findings in §3 were written before opening `SKILL-BEST-PRACTICES-AUDIT-2026-07-30.md`; §4 reconciles the two afterwards.

---

## 1. The rubric extracted from the PDF

Concrete, checkable criteria the guide actually states (page refs are PDF pages):

**Structure & naming (pp. 5, 10)**
- R1. Skill = folder with `SKILL.md` (required, exact case) + optional `scripts/`, `references/`, `assets/`.
- R2. Folder name kebab-case: no spaces, underscores, capitals; `name` field should match folder name.
- R3. No `README.md` inside the skill folder ("all documentation goes in SKILL.md or references/"); a repo-level README for humans is expected instead (p. 19).

**Frontmatter (pp. 10–11, Ref. B p. 31)**
- R4. `name` required: kebab-case; not prefixed "claude"/"anthropic" (reserved).
- R5. `description` required: MUST state both WHAT the skill does and WHEN to use it (trigger conditions); under 1,024 chars; include specific phrases users might say; mention file types if relevant.
- R6. **No XML angle brackets (`<` `>`) in frontmatter** — stated twice, as a security restriction ("Frontmatter appears in Claude's system prompt"). The Quick Checklist (p. 30) says "No XML tags (< >) anywhere"; the stated rationale binds frontmatter only.
- R7. Optional fields: `license`, `compatibility` (1–500 chars, "environment requirements: intended product, required system packages, network access"), `metadata` (suggested: author, version, mcp-server), `allowed-tools`.

**Description quality & triggering (pp. 11, 25–26)**
- R8. Structure: [What it does] + [When to use it] + [Key capabilities]; bad = vague ("Helps with projects"), missing triggers, too technical.
- R9. Over-triggering remedies: **add negative triggers** ("Do NOT use for X (use Y skill instead)"), be more specific, clarify scope. Under-triggering remedy: add keywords/detail.

**Body & progressive disclosure (pp. 5, 12–13, 27)**
- R10. Three-level disclosure; keep SKILL.md focused on core instructions, move detail to `references/` and link.
- R11. **Keep SKILL.md under 5,000 words.**
- R12. Be specific and actionable (exact commands, concrete failure lists); no ambiguous language ("validate things properly").
- R13. Include error handling ("Common Issues": error/cause/solution).
- R14. Include examples (user says → actions → result).
- R15. Reference bundled resources clearly ("Before writing queries, consult `references/api-patterns.md` for: …").
- R16. Critical instructions at the top; use `## Important`/`## Critical`; repeat key points if needed.
- R17. Advanced technique: bundle scripts for critical validations — "Code is deterministic; language interpretation isn't."
- R18. Verify MCP tool names against server docs; names are case-sensitive. (The guide's own pattern examples use bare tool names, e.g. `create_customer`.)

**Design principles (pp. 5–9)**
- R19. Composability: work alongside other skills, don't assume you're the only capability.
- R20. Portability: work across Claude.ai / Claude Code / API, "provided the environment supports any dependencies" — declare env needs via `compatibility`.
- R21. Start from 2–3 concrete use cases (trigger → steps → result) before building.
- R22. Define success criteria: quantitative (triggers on ~90% of relevant queries; tool-call/token count vs baseline; 0 failed API calls) and qualitative (no user redirection; consistent output across 3–5 runs).

**Testing & iteration (pp. 15–17)**
- R23. Triggering tests: should-trigger (obvious + paraphrased) AND should-NOT-trigger lists.
- R24. Functional tests: valid outputs, API calls succeed, error handling, edge cases.
- R25. Performance comparison vs no-skill baseline.
- R26. Rigor scales with audience: "A skill used internally by a small team has different testing needs than one deployed to thousands of enterprise users."
- R27. Iterate from observed failures; update version in metadata after iterating.

**Patterns (pp. 22–24)** — R28. Sequential workflow orchestration; multi-MCP coordination; iterative refinement; context-aware tool selection; domain-specific intelligence (compliance-before-action, audit trail).

**Distribution (pp. 19–20)** — R29. GitHub repo with clear README, installation instructions, example usage and screenshots; position by outcomes, not mechanics.

**Context economy (p. 27)** — R30. If slow/degraded: shrink SKILL.md, move docs to references; mind total enabled-skill count (frontmatter of every skill is always loaded).

---

## 2. Compliance table

### 2a. Per-skill mechanical checks

| Skill | name=folder, kebab (R2/R4) | desc len (R5 ≤1024) | `<`/`>` in frontmatter (R6) | words (R11 <5,000) | refs linked (R15) |
|---|---|---|---|---|---|
| task-context | ✅ | 411 ✅ | ✅ none | 2,482 ✅ | ✅ |
| requirements-grooming | ✅ | 508 ✅ | ✅ none | 1,867 ✅ | ✅ |
| qa-checklist | ✅ | 376 ✅ | ✅ none | 1,153 ✅ | ✅ |
| qa-test-cases | ✅ | 358 ✅ | ✅ none | 2,055 ✅ | ✅ |
| pr-summary | ✅ | 293 ✅ | ✅ none | 1,370 ✅ | ✅ |
| code-review | ✅ | 391 ✅ | ✅ none | 2,310 ✅ | ✅ |
| api-testing | ✅ | 540 ✅ | ✅ none | 2,102 ✅ | ✅ exemplary |
| web-testing | ✅ | 504 ✅ | ✅ none | 3,627 ✅ | ✅ |
| qa-manual-runsheet | ✅ | 735 ✅ | ✅ none | 2,051 ✅ | ✅ |
| qa-manual-results | ✅ | 688 ✅ | ✅ none | 1,068 ✅ | ✅ |
| qa-run-analyzer | ✅ | 564 ✅ | ✅ none | 1,718 ✅ | ✅ |
| qa-pipeline-docs | ✅ | 853 ✅ | ❌ `->` ×3 | 2,005 ✅ | ✅ |
| qa-pipeline-code | ✅ | 960 ✅ | ❌ `->` ×5 | 3,857 ✅ | ✅ |

All 13: `SKILL.md` exact-case present (R1); no README.md inside any skill folder (R3 — but see the `setup-guide.md` caveat, §4); no "claude"/"anthropic" names (R4); every description states WHAT + WHEN with quoted trigger phrases (R5/R8).

### 2b. Per-criterion verdicts (plugin-wide)

| Criterion | Verdict | Evidence |
|---|---|---|
| R1–R4 structure/naming | **Compliant** | 13/13; optional dirs used correctly (`references/` ×13, `scripts/` ×4). |
| R5/R8 descriptions | **Compliant** | e.g. qa-manual-results names the artifact form it accepts ("uploads/pastes a filled run sheet or TC/Result/Notes table") — the guide's "mention file types" point done properly. |
| R6 no `<`/`>` in frontmatter | **Violation ×2** | `qa-pipeline-docs/SKILL.md:5–6`, `qa-pipeline-code/SKILL.md:7–8`: ASCII arrows `task-context -> requirements-grooming -> …` put literal `>` into the YAML that lands in the system prompt. See finding N1. |
| R7 optional fields | **Partial (by choice)** | No skill uses `compatibility`/`metadata`/`license`; env requirements live only in body text. See N4 and contradiction C1. |
| R9 negative triggers | **Partial** | web-testing models it ("NOT for hand-testing by the user: the manual run sheet is qa-manual-runsheet…"); code-review, pr-summary, qa-checklist, task-context carry generic triggers with no scope guard. See N2. |
| R10/R11 progressive disclosure & size | **Compliant** | Max 3,857 words (qa-pipeline-code); 33 reference files; method/templates/examples consistently pushed down. (Fails the *official* doc's stricter 500-line bar in one place — see C2.) |
| R12 specific & actionable | **Compliant** | Exact commands throughout (`python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <KEY>`); qa-test-cases even bans the guide's exact ambiguous words: "no 'correctly', 'properly', 'appropriate'". |
| R13 error handling | **Compliant** | Every stage has fallbacks, BLOCKED/escalation rules ("after 3 failed attempts… stop and reassess"), and connector-absent paths. Shape differs from the guide's Error/Cause/Solution blocks but substance exceeds it. |
| R14 worked examples | **Partial** | qa-checklist and qa-test-cases bundle `*-example.md` references; output templates serve as output examples everywhere. No SKILL.md has a "user says → actions → result" block. Low impact (see N6). |
| R15 clear reference pointers | **Compliant** | api-testing: "Read it before running. This SKILL.md is the stage contract; the reference is the how-to" — textbook R15. Contents lines added to all 100+-line refs in 0.18.1. |
| R16 critical-first | **Compliant** | Binding rules sit in top sections (qa-manual-runsheet: "Source of truth — read this before anything else"); repetition used deliberately (absence-check protocol restated at every consuming stage). |
| R17 scripts for determinism | **Compliant, exceeds** | `reconcile_counts.py` (with `--selftest`), `generate_pict_cases.py`, `extract_archive.py`, `load-env.sh`; qa-test-cases: "The statistics block is derived mechanically, never tallied by hand." This is the guide's p. 26 "Advanced technique" implemented before the guide asked. |
| R18 MCP tool-name hygiene | **Compliant** | 0.18.1 mapping notes ("bare names = Atlassian MCP connector… match by tool name on the server that provides it") satisfy the PDF, whose own examples use bare names. |
| R19 composability | **Tension, handled** | Stages assume each other by design (it is a pipeline) but degrade gracefully: every stage accepts uploaded files in a fresh chat, and orchestrators integrate *other* plugins conditionally ("via the `/knowledge-base` skill when installed, else…"). Flagged, not excused: generic trigger phrases are where composability actually leaks (N2). |
| R20 portability / env deps | **Partial** | Cowork/Claude Code branching is handled in-body ("Split runs (Claude Code ↔ Cowork)", Playwright vs extension backends) — better than most skills — but nothing is declared where the guide puts it (`compatibility`). See N4. |
| R21 use-case-first design | **Compliant** | Each SKILL.md opens with trigger→steps→result in effect; README table maps input→output per stage. |
| R22 success criteria | **Partial** | No written metric targets, but measured decisions are cited inline ("inlining them duplicated the machine archive by 99.3% and cost ~15,000 characters per ticket"; "89 rows and 11"). Culture present, artifact absent. |
| R23 triggering tests | **Violation** | No should-trigger / should-NOT-trigger lists exist anywhere. See N3. |
| R24/R25 functional tests & baseline | **Partial, recorded** | Only `fixtures/EP-0000-context.md` (docs-phase smoke test). Known and deferred (CHANGELOG 0.18.1 "Not done"). The PDF's R26 makes this deferral more defensible than the official doc did — see C5. |
| R27 iterate + version | **Compliant** | CHANGELOG discipline is strong; version bumped in both manifests per iteration. |
| R28 patterns | **Compliant** | Pattern 1 (sequential orchestration with validation gates) = both orchestrators; Pattern 2 (multi-MCP: Atlassian + QA Service + Playwright/browser + git) = qa-pipeline-code; Pattern 3 (iterative refinement w/ validation scripts) = count gate + "Verification before saving" ×13; Pattern 5 (compliance-before-action + audit trail) = REQUIRED PAUSE blocks, snapshot-and-revert, retraction convention. |
| R29 distribution | **Compliant (minor gap)** | Repo README with "Installing the skills" section, plugin + marketplace manifests. No screenshots/example-usage captures (guide asks for them; optional for an internal tool). |
| R30 context economy | **Partial** | 13 always-loaded descriptions total ~7,181 chars (~1.8k tokens in every session, every chat). The two orchestrators (960 + 853) carry body-level detail. See N5. |

**Packaging:** `plugin.json` and `marketplace.json` valid and consistent (name, version 0.18.1 in both, keyword-rich descriptions). The guide's zip-upload flow is superseded by the plugin/marketplace mechanism the repo correctly uses (see C4).

---

## 3. NET-NEW findings (things this PDF asks for that the official-doc audit did not), ranked by impact

### N1 — `>` characters inside frontmatter descriptions (2 skills) — violation of the guide's security rule

The PDF forbids the characters `<` `>` in frontmatter twice (p. 11 "No XML tags (< or >)"; p. 31 "Forbidden: XML angle brackets (< >) — security restriction"), with the rationale that frontmatter is injected into the system prompt. The prior audit checked for XML *tags* and passed everything; the PDF's phrasing is character-level, and the two orchestrators fail it:

- `skills/qa-pipeline-docs/SKILL.md:5–6` — `runs task-context -> requirements-grooming -> qa-checklist -> qa-test-cases`
- `skills/qa-pipeline-code/SKILL.md:7–8` — `runs pr-summary -> code-review -> api-testing -> web-testing -> run-analyzer`

Real risk: a strict upload/marketplace validator implementing the character rule rejects exactly the two entry-point skills. Cost of fix: zero behaviour change.

**Fix:** in both descriptions replace ASCII `->` with the Unicode arrow `→` (already used throughout the repo's body text) or the word "then". Nothing else in any frontmatter contains `<` or `>`. (Body-text `<ISSUEKEY>` placeholders are fine — the security rationale binds frontmatter only; the p. 30 checklist's "anywhere" is sloppier than its own rationale.)

### N2 — No negative triggers on the four skills with generic trigger phrases — over-triggering risk the PDF explicitly treats

The PDF's over-triggering remedy list (p. 25–26) is net-new relative to the official doc: *add negative triggers, be more specific, clarify scope*, with the example format "Do NOT use for simple data exploration (use data-viz skill instead)." Four descriptions carry triggers generic enough to fire on unrelated requests — and in real sessions this plugin coexists with a generic `/code-review` command, `review-pr`, and `security-review` (all present in the authoring environment today):

- **code-review**: triggers `"code review"`, `"check the implementation"`, `"go through the code"` — indistinguishable from a request to review any code. This skill must *not* win when the user pastes a random PR: it only checks test cases against a diff.
- **pr-summary**: triggers `"read the PR"`, `"look at the PR"`, `"what's in the PR"` — fires on any casual PR question.
- **qa-checklist**: triggers `"build a checklist"`, `"make a checklist"` — fires on grocery lists and release checklists alike.
- **task-context**: `"process the ticket"` — fires on any Jira ticket request that has nothing to do with QA.

web-testing already models the fix in-repo: *"NOT for hand-testing by the user: the manual run sheet is qa-manual-runsheet (stage 9)…"*.

**Fix (one clause per description):**
- `code-review/SKILL.md`: append "Checks QA test cases against PR code only — do NOT use for general code review of a branch or PR outside the QA pipeline."
- `pr-summary/SKILL.md`: append "Builds the pipeline's PR map — not for general PR discussion or review outside the QA pipeline."
- `qa-checklist/SKILL.md`: append "Only for QA checklists built from a groomed requirements file — not for general/other checklists."
- `task-context/SKILL.md`: append "For the QA pipeline's context stage — not for general ticket lookups or edits."

### N3 — No triggering-test suite — the cheap tier of the deferred eval work, with no excuse to defer

The PDF splits testing into three tiers and the first — triggering tests (p. 15): 10–20 queries per skill in *should trigger / should NOT trigger* lists, including paraphrases — needs no fixtures, no environment, no credentials. The recorded deferral of "eval sets" (prior audit item 5, CHANGELOG 0.18.1) covers the expensive functional tier; nothing covers this free tier, and N2 is precisely the class of defect it catches.

**Fix:** add `evals/triggering.md`: per skill, ~5 should-trigger (copy from the descriptions, plus paraphrases like "can you sanity-check what changed in this pull request" for pr-summary) and ~5 should-NOT-trigger (the N2 collision cases: "review my code", "make me a packing checklist", "what's in PR #6941 generally"). Run manually per the PDF's debugging method ("Ask Claude: when would you use the [skill name] skill?") whenever a description changes.

### N4 — No `compatibility` declarations despite hard, per-skill environment requirements

The PDF's `compatibility` field (1–500 chars: "intended product, required system packages, network access needs") exists for exactly this plugin's shape — the official doc's rubric had no such field (see C1). Today every environment constraint lives in body text, discovered only after the skill loads: web-testing needs a browser backend (Playwright MCP or the Chrome extension); api-testing needs shell + curl + network + `.env` credentials; task-context, the orchestrators, qa-run-analyzer and qa-manual-results need the Atlassian (and optionally QA Service) MCP connectors; pr-summary/code-review need git or Bitbucket API tokens.

**Fix (optional, decide once):** add one-line `compatibility:` frontmatter to the env-dependent skills, e.g. api-testing: `compatibility: Needs shell + network (curl) and .env credentials; designed for Claude Code / Cowork with a mounted repo.` If the team prefers the official doc's minimal frontmatter (see C1), the alternative is a one-line "Requires:" opener at the top of each body — either way the requirement should be visible before a run fails mid-stage. (qa-pipeline-code's step-0 "Environment check first" already mitigates at runtime; this is about declaring it at the standard's designated slot.)

### N5 — Always-loaded description footprint: ~7.2k chars, with the two orchestrators carrying body detail

The PDF is the source that stresses level-1 cost ("Provides just enough information… without loading all of it into context") and warns about many-skills sessions (p. 27). All 13 descriptions load into every session of every user of this plugin: 7,181 chars (~1.8k tokens). The orchestrator descriptions (960 and 853 chars — 3–4× the PDF's good examples) narrate mechanics that belong in the body: qa-pipeline-code's description explains PROVISIONAL marking, retest mode, three pause points, and the stage-10 deferral; qa-pipeline-docs's explains connector-conditional publishing and interactive-mode toggles.

**Fix:** trim both to WHAT + WHEN + triggers + the one routing fact that matters at selection time ("run in a FRESH chat after qa-pipeline-docs"), target ≤500 chars each. Everything cut already exists in the bodies. Saves ~900 always-loaded chars and makes the trigger phrases easier for the selector to see. (Do NOT trim the stage-N routing sentences from the single-stage skills — pipeline position is genuine trigger signal, a justified deviation from the PDF's standalone-skill model.)

### N6 — Template-shape gaps: no worked Examples, no consolidated Troubleshooting (low priority)

The PDF's recommended SKILL.md template (p. 12) includes an `Examples` section ("User says → Actions → Result") and a `Troubleshooting` section (Error/Cause/Solution). No SKILL.md has either *as a section*. Substance is largely present — error handling is embedded per step and per stage, and qa-checklist/qa-test-cases ship example reference files — so this is shape, not content. Where it is cheap and real: the orchestrators would benefit from one 5-line worked example each (user gives `EP-1234` → stages run → what lands where), and api-testing/web-testing could consolidate their scattered failure guidance under one `## Troubleshooting` heading for findability. Flagged honestly: for input-file→output-file pipeline stages, `references/output-template.md` *is* the example, and forcing dialog-style examples into all 13 would add tokens for little behaviour change.

---

## 4. Reconciliation with `SKILL-BEST-PRACTICES-AUDIT-2026-07-30.md`

### 4a. Overlap — already fixed in 0.18.1 (not re-reported above)

| Prior finding | PDF equivalent | Status |
|---|---|---|
| F1 bare MCP tool names | R18 (weaker in PDF — its own examples are bare) | Fixed via mapping notes; **satisfies both docs** |
| F2 broken `../` paths | R15 | Fixed |
| F3 missing reference TOCs | R15/R10 | Fixed (Contents lines verified present) |
| F6 stale descriptions ("manual testing" trigger, "Stage 4.5") | R5/R9 | Fixed; web-testing's new "NOT for hand-testing" line is the repo's first negative trigger |

### 4b. Overlap — reported earlier, still open, and the PDF agrees (not counted as net-new)

- **F9 orphaned `setup-guide.md` ×8** — the PDF sharpens this: R3 says all docs go in SKILL.md or `references/`; a human-facing `setup-guide.md` at skill root is a README by another name, and no SKILL.md links it. The prior audit's fix (failure-path pointer) stands; the PDF adds the option of moving them to `references/setup.md` with a "when adapting this plugin, read…" line.
- **F5 web-testing size** — passes the PDF (3,627 words < 5,000) but has *grown* to 519 lines since the prior audit measured 507, moving further past the official doc's 500-line bar. See C2 for which bar to follow.
- **F7 no functional evals** — still open, still recorded. The PDF changes its weight (see C5) and N3 splits off the free tier.
- **F10 war-story length, F11 naming prefix inconsistency, F12 `navigation_paths.json` at skill root** — unchanged; nothing in the PDF alters those verdicts. (F12 sub-question resolved during this audit: the file is confirmed git-ignored and untracked — `git ls-files skills/web-testing/` does not list it.)

### 4c. Contradictions between the PDF and the official best-practices doc — and which wins

- **C1 — Frontmatter fields.** Official doc (per prior audit rubric #4): frontmatter is *exactly* `name` + `description`. PDF: optional `license`, `compatibility`, `metadata`, `allowed-tools` are part of the standard. **No true conflict — the PDF documents the open Agent Skills standard's superset; the official doc states the required floor.** Recommendation: the current minimal frontmatter complies with both and should stay the default; if anything is added, add only `compatibility` where it changes run expectations (N4), and never let optional fields grow the always-loaded footprint they were meant to protect.
- **C2 — Size budget.** Official: SKILL.md under **500 lines**. PDF: under **5,000 words**. web-testing (519 lines / 3,627 words) fails the first, passes the second. **The official doc wins:** it is newer, surface-specific (Claude Code, this plugin's actual target), and lines-of-instructions is the tighter proxy for what degrades attention. Keep the prior audit's F5 extraction plan (persistence note, Cowork credentials note, classification prose → references).
- **C3 — MCP tool naming.** Official: always fully qualified `ServerName:tool_name`. PDF: verify names, case-sensitive — but its own Pattern 1 example calls bare `create_customer`. **Synthesis already shipped (0.18.1 mapping notes) and is the right answer for install-varying prefixes; follow the official doc's intent, not its letter.** No action.
- **C4 — Distribution model.** PDF (January 2026): zip + upload to Claude.ai settings, GitHub repo with README/screenshots. Official ecosystem: plugin + marketplace manifests, which this repo uses. **The plugin route wins; the PDF's README requirements are satisfied** (`README.md` § "Installing the skills"). The PDF's screenshots ask is unmet and optional for an internal tool.
- **C5 — Testing rigor.** Official: "create evaluations BEFORE writing extensive documentation… at least three." PDF: choose the rigor "that matches your quality requirements and the visibility of your skill"; internal small-team skills have lighter needs; the pro-tip endorses iterating on a single hard task first — which is exactly this repo's documented practice (CHANGELOG rules citing real-run failures). **The PDF wins for this internal plugin: the recorded deferral of functional evals is legitimate under it.** The exception is N3 — triggering tests are free under either doc and should not ride the deferral.
- **C6 — "No XML anywhere".** The PDF's own checklist (p. 30) says no `< >` *anywhere*, which would ban the body's ubiquitous `<ISSUEKEY>` placeholders; its security section binds frontmatter only. **Follow the rationale, not the checklist wording:** frontmatter must be clean (N1), body placeholders stay.

### 4d. Where the PDF adds nothing the repo needs

The PDF's Chapter 5 patterns are all already instantiated (see R28); its MCP-enhancement framing (Category 3) matches the plugin's design; its "focus on outcomes" positioning advice is already how README.md is written. The PDF's success-criteria template (R22) is the only wholly unimplemented artifact besides tests — worth a 10-line block in MAINTAINERS.md if the team ever wants regression thresholds, not a SKILL.md change.

---

## 5. Verdict

Against this guide the plugin is **substantially compliant and in several places ahead of it** — progressive disclosure, deterministic scripts, error handling, and the orchestration patterns read like the guide's own case studies. The PDF adds a thinner layer of net-new obligations than the official doc did, and they are concentrated in discovery and packaging rather than behaviour: two frontmatter blocks containing forbidden `>` characters (N1 — trivial, fix now), four descriptions missing the negative triggers the PDF prescribes for exactly their kind of generic phrasing (N2), a free triggering-test tier that should not have ridden the eval deferral (N3), undeclared environment requirements where the standard provides a slot (N4), and ~900 chars of trimmable always-loaded orchestrator description (N5). N1+N2+N5 are one small frontmatter-only pass; N3 is an hour; N4 is a team decision. Nothing in the PDF challenges the pipeline's architecture, and where the two source documents disagree, the disagreements are resolvable (§4c) — the only one requiring action is the 500-line vs 5,000-word budget, where the official doc's stricter line budget should govern and web-testing remains the one file over it.
