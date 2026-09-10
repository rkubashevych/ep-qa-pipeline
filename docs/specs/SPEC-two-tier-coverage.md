# SPEC — Two-tier coverage: machine-depth generation, human-core selection

Status: **draft for review — nothing implemented yet.**
Author: pipeline review session, 2026-08-14.
Decision needed from: Roman.

## 1. Goal

One test-case corpus, two execution views.

- **Machine view (stages 6–8):** a deeper set than today — test-design
  techniques applied at risk-scaled depth, so the machine can flag
  things a human walk would not. Published whole to the QA Service
  suite and the Jira tracker comment, exactly as today.
- **Human view (stage 9):** a short sheet that still touches every
  behavioural requirement of the ticket — one `core` representative
  per REQ plus everything the machine flagged or could not settle.

Never two authored sets. Stage 10 (`qa-manual-results`) joins human
verdicts to machine verdicts **by TC ID**; two independently written
sets break reconciliation and drift apart. The human set is a
*selection*, made at generation time via a `[core]` marker.

## 2. Design decisions

- **D1 — one corpus, two views.** The only new artifact is a marker,
  never a second file of cases.
- **D2 — machine depth is risk-scaled, not maximal.** Exhaustive
  expansion is rejected (token/time cost). Depth increases only where
  risk is High; Low-risk requirements get *less* than today.
- **D3 — `[core]` is assigned by stage 4,** not chosen ad hoc at
  runsheet time: exactly one core case per behavioural REQ — the case
  whose partition carries the most risk (riskiest invalid partition or
  conflict-side preferred; happy path when nothing outranks it).
- **D4 — the human sheet walks every behavioural REQ.** Today's
  coverage gate (runsheet step 2a item 3) lets a machine verdict cover
  a REQ with no human row. That changes: the core case always gets a
  row. When the machine verdict on it is a runtime-verified clean PASS
  and risk is Low/Medium, the row is short-form (VERIFY-style: fastest
  action that would expose a wrong PASS), so the sheet stays short.
- **D5 — the grounding rule does not move.** Extra depth still derives
  only from values, states and conditions present in the requirement
  text. Depth never invents behaviour.

## 3. File-by-file changes

> Edit with host-side file tools only (CLAUDE.md: no shell writes
> through the Cowork mount).

### 3.1 `skills/qa-test-cases/references/test-case-design-rules.md`

Replace the **"Coverage levels"** section (Standard/Extended) with a
risk-scaled table:

| Requirement risk | Depth (machine default) |
|---|---|
| High | Standard + 3-value BVA + invalid state transitions (where states exist) + collapsed decision table (where 2+ conditions combine) + pairwise 2-wise (where 3+ parameters interact) |
| Medium | Standard, as defined today (happy path, invalid partitions, 2-value BVA, described alt/exception flows, valid transitions) |
| Low | Happy path + only explicitly stated constraints |

Keep an **"Extended on request"** paragraph: the user can still force
full extended depth for the whole ticket.

Keep unchanged, and state explicitly they hold at every depth:
- EP one-representative-per-class (depth comes from more techniques,
  never from duplicate cases in the same class);
- BVA only where constraints are written;
- the pairwise no-exhaustive-enumeration rule;
- all anti-patterns.

Add a **"Core selection rule"** section: one core case per behavioural
REQ; selection preference order = riskiest invalid partition →
conflict version-A case → boundary case at the stated limit → happy
path. A structural REQ (checklist-only) has no core case.

### 3.2 `skills/qa-test-cases/SKILL.md`

- **Test-case building method:** state that depth follows the REQ's
  `[risk: …]` marker per the table in design-rules (the marker is
  already read from the checklist — no new input needed).
- **New marker:** the chosen core case's heading gains ` [core]` after
  the channel tag: `### TC-REQ-3.1 — <name>  [UI] [core]`.
- **Verification before saving**, two new checks:
  - every behavioural REQ has exactly ONE `[core]` case — zero or two
    is an error;
  - every High-risk REQ group's `Applied techniques:` line names at
    least one extended technique **or** a one-line reason why none
    applies (e.g. "no numeric constraints, no states, 2 parameters").
- **Statistics block**, one new line (derived mechanically, same rule
  as the rest): `Core cases: <N> (= behavioural requirements)`.

### 3.3 `skills/qa-test-cases/references/output-template.md`

- Show the ` [core]` marker in the Structure block.
- Add the `Core cases:` line to the Statistics section.

### 3.4 `skills/qa-manual-runsheet/SKILL.md` — step 2a only

Step 2a (select-the-manual-set) already does technique-based reduction
with `Covers:` merging. Two changes:

- **Item 1 (must-walk)** additionally includes: the `[core]` case of
  every behavioural REQ, even when machine-settled. Machine-settled
  clean-PASS core cases at Low/Medium risk enter in short form
  (VERIFY-style row).
- **Item 3 (coverage gate)** tightens from "walked row **or**
  runtime-verified machine verdict" to: every behavioural REQ has a
  **walked row**. Print stays: "N cases → M rows, covering R/R
  requirements".

Everything else in stage 9 (retest scoping, fixtures, classification,
provisioning) is untouched.

### 3.5 `skills/qa-manual-runsheet/references/runsheet-format.md`

- Case-index rows for core cases carry `core` in the existing Notes /
  reference material, so the tester sees why a machine-passed row is
  on the sheet.
- Reference tab: unselected cases keep today's wording ("delegated to
  machine verdict (<status>)").

### 3.6 `skills/qa-run-analyzer/SKILL.md` — section 1 additions

- 🔴 a behavioural REQ with zero or multiple `[core]` cases.
- 🔴 a runsheet exists for the ticket but a behavioural REQ has no
  walked row (gate regression).
- 🟡 a High-risk REQ group whose `Applied techniques:` names no
  extended technique and no reason (advisory — depth conformance).

### 3.7 `skills/qa-run-analyzer/scripts/reconcile_counts.py`

- Count ` [core]` occurrences on `### TC-REQ` headings in the
  test-cases file; print `core=<N>` on that stage's line.
- Self-test: add a heading with `[core]` and one without; expect the
  count. (`[core]` sits on headings, not table cells, so the
  status-cell parser is unaffected — the channel-suffix guard in
  `cell_status` never sees it.)

### 3.8 `skills/qa-pipeline-docs/SKILL.md` — publish step

- Tracker-comment case line gains the marker:
  `- [ ] TC-REQ-N.M — <name>  [<channel>] [core] · <PREFIX>-<SEG>-NN`.
- Count gate: also recount `[core]` and require it to equal the
  behavioural-REQ count before posting.

### 3.9 `skills/qa-pipeline-docs/references/qa-service-publish.md`

- Case `detail` gains `core: yes` on core cases (detail is free-form —
  no tag-approval dependency).
- Step 4 (`apply_auto_tags`): additionally propose a `core` tag where
  the tag catalogue allows; pending approval is fine and already
  handled by the existing flow.

## 4. What does NOT change

Grounding rule; EP dedup; channel tags and the routing invariant
(status-vocabulary.md); stages 5–8 run ALL cases in scope, as now;
stage 10 join-by-TC-ID and retraction logic; retest mode; fixture
rules; suite as system of record.

## 5. Cost estimate

- Generation (stage 4): +10–30% tokens — only High-risk REQs deepen,
  Low-risk REQs shrink.
- Machine execution (stages 6–8): set grows ~1.3–1.8× on a typical
  ticket (most REQs are Medium and unchanged). Biggest cost is
  web-testing browser time on the new High-risk cases — this is the
  price of "machine flags what I wouldn't", and High-first ordering
  already protects truncated runs.
- Human run: roughly today's sheet + a handful of short-form core
  rows. On a 66-case ticket like EP-53768 (30 behavioural REQs):
  expect ~30 walked rows where the old gate might have produced ~20,
  most of the extra being 30-second spot-checks.

## 6. Release checklist (from CLAUDE.md / MAINTAINERS.md discipline)

1. Implement 3.1–3.9 with host-side file tools.
2. `python3 skills/qa-run-analyzer/scripts/reconcile_counts.py --selftest`.
3. Docs-stage smoke test: run `fixtures/EP-0000-context.md` through
   grooming → checklist → test-cases; **update the fixture's
   expectations foot** for the new core marker + statistics line.
4. No frontmatter `description` edits are needed for 3.1–3.9 — if any
   sneak in, walk `evals/triggering.md`.
5. Bump `.claude-plugin/plugin.json` AND `marketplace.json`; add a
   CHANGELOG entry referencing this spec.
6. Secret scan before commit; explicit paths only.

## 7. Out of scope (separate decisions, not forgotten)

- Authoring invariants at grooming time (today they only get kinds at
  publish). Separate small spec if wanted.
- Exhaustive machine expansion of pairwise models — rejected for cost.
- Experience-based / error-guessing case section fed by bug history —
  worth considering later; interacts with the grounding rule, so it
  needs its own discussion.
