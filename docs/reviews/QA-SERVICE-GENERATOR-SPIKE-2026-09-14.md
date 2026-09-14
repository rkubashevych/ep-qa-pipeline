# QA Service generator vs the pipeline — the EP-55944 spike, 2026-09-14

The spike named in the 0.43.2 CHANGELOG entry ("on a throwaway suite, run
`start_generate_test_cases` … and compare its cases with stage 4's on the same
requirements; record the result here whichever way it goes"). This is that
record. Disposition: **the rejection stands, and the reason is now measured, not
assumed.**

Working artefacts (git-ignored, will not survive the workspace):
`~/.ep-qa/spikes/EP-55944/` — both raw outputs, the suite JSON, the pipeline's
own five files. This tracked copy carries the design, the scores and the
evidence.

---

# EP-55944 — side-by-side spike: inputs, blinding, and the benchmark

**Run:** 2026-09-14 · local only · nothing published to Jira
**Story:** EP-55944 "Registrant report: add paid amount, payment status columns
and completed-payment filter" · Story · component Reporting · status Staged for
Release · fixVersion Prod 2026-09-23 · reporter: the product owner · assignee: the
backend developer
**URL:** https://expoplatform.atlassian.net/browse/EP-55944

## Why this story

Picked because it is (a) finished, so there is a real human QA record to compare
against, (b) has explicit numbered acceptance criteria, (c) has product decisions
that live ONLY in a sub-task comment thread, not in the AC — the hardest thing
for any requirements extractor to catch, and (d) has no Confluence AC page, so
both sides work from the same Jira text with no external document advantage.

## The two candidates

| | Author | Inputs | Output location |
|---|---|---|---|
| **A** | `ep-qa-pipeline` docs phase (stages 1, 2, 4 + analyzer), v0.43.2, local only, publish suppressed | see below | `~/.ep-qa/runs/EP-55944/docs/` |
| **B** | QA Service `start_collect_requirements` + `start_generate_test_cases`, model Opus, on a throwaway suite (prefix ZZSPK, deleted after export) | the same text, pasted as labelled source blocks | `~/.ep-qa/spikes/EP-55944/` |

## Inputs given to BOTH (identical)

1. EP-55944 story description — the user story, "Why this isn't trivial" (the
   Registration → Account → Event → Participant → Order → Payment join), Scope
   (admin panel only, web only, event-scoped; existing Data export permission;
   statuses are `success / pending / failed / cancelled`), and AC 1–4.
2. EP-56727 `[BE]` sub-task description — join, field exposure, label mapping,
   the Paid-only filter, LEFT-join semantics, the undecided multi-Order rule,
   query performance.
3. EP-56727 comments 1–4 — the developer's five product questions and the PO's
   five answers, plus the explicit confirmation that "a separate row per payment"
   means a registrant with 3 payments becomes 3 rows with every other column
   repeated. **This is the load-bearing decision and it is nowhere in the AC.**
4. EP-56728 `[FE]` sub-task — status "Closed by reject" (the work landed
   backend-only).

## Blinded from BOTH (these are the benchmark, not input)

- **EP-56729** — the human-written QA sub-task "[QA] Registrant report…",
  authored by the QA engineer, status COMPLETE. It is candidate **C**, the human
  test plan.
- **The story comment by the QA engineer, 2026-09-07** — the human QA
  verification record ("No issues found") naming exactly what was checked on
  Alpha2 event 693. It is the *ground truth of what mattered in practice*.

Neither A nor B was allowed to read these. That is what makes the comparison a
test of design quality rather than a test of copying.

---

## Benchmark C1 — the human QA sub-task EP-56729 (test plan), verbatim

> Test coverage for AC1–AC4 of the parent story.
>
> **Scope**
>

---

# Scoring rubric — agreed before either output was read

Fixed in advance so the comparison cannot be tuned to whichever result arrived.
Each dimension is scored 0–3 against evidence quoted from the artefact.

| # | Dimension | What earns 3 | What earns 0 |
|---|---|---|---|
| D1 | **AC coverage** | every one of AC1–AC4 has at least one case whose assertion would fail if the AC were violated | an AC with no case, or a case that only restates the AC |
| D2 | **Caught the buried decision (T7)** | the one-row-per-payment rule from the comment thread is a requirement AND has a case with the 3-payments-becomes-3-rows shape | the rule is absent, or present only as "multi-order TBD" |
| D3 | **Predicted the undocumented truths (T3, T4, T8, T9)** | a case exists for the state transition (T8) and/or the absent-row case (T9); currency/decimals asserted (T3) | none of them appear |
| D4 | **Executability** | a tester who has never seen the feature can run the case: named preconditions, concrete steps, concrete data, one checkable expected result | steps are a paraphrase of the title; "verify it works" |
| D5 | **Oracle strength** | assertions name the exact value/label/absence; negative cases assert the refusal AND the unchanged state | "the report is correct" |
| D6 | **Traceability** | every case names the requirement and the AC id it verifies; no orphans | cases trace to nothing |
| D7 | **Honest uncertainty** | open questions, contradictions and risks are stated as such and not silently resolved | invented facts presented as requirements |
| D8 | **Right level / routing** | API-checkable things are API cases, UI-only things are UI cases; export-file checks routed as such | everything is one undifferentiated level |
| D9 | **Noise** | no duplicate cases, no case that cannot fail, no filler | many near-identical or untestable cases |

**Anti-invention check (pass/fail, not scored):** any statement of fact about the
product that appears in neither the story, the BE sub-task, nor its comments is
an invention. It is flagged and quoted. An explicitly-labelled inference or open
question is NOT an invention — that is D7 behaviour.

**A note on fairness.** Candidate B (QA Service) is a two-call pipeline given
pasted text. Candidate A (ep-qa-pipeline) is a three-stage pipeline with tracker
access. B was not given the ability to go and read the ticket itself, because the
MCP tool does not fetch Jira — the tool's own description says to paste content
instead. That is B's real operating mode, not a handicap I imposed.

---

# EP-55944 — the comparison

Scored against `01-SCORING-RUBRIC.md`, fixed before either output was read.
Evidence is quoted from the artefacts in this folder and in
`~/.ep-qa/runs/EP-55944/docs/`.

## What each side produced

| | A — ep-qa-pipeline 0.43.2 | B — QA Service generator | C — the human (benchmark) |
|---|---|---|---|
| Requirements | 16 (REQ-1…16) + an AC ledger of 25 ids (4 AC · 16 JD · 5 CM) | 22 (6 fr · 8 rule · 2 inv · 1 nfr · 2 risk · 1 oq · 2 disc) | none written |
| Test cases | **37** + **6 structural checks** | **23** | 9 scope bullets |
| Extra artefacts | `-recon.md` (a read of the product source), `-run-report.md`, `-open-items.md` (11 rows) | — | — |
| Levels / channels | export/email 33 · UI 3 · API 1 · struct UI 6 | AE 10 · U 9 · I 9 · Perf 1 · **E2E 0 · Manual 0** | manual, implied |
| Core markers | 15 | none | — |
| Folders | per-requirement sections | **all 23 unfoldered (General)** | — |
| Wall clock | ~12 min, 5 stages | ~9 min, two jobs | unknown |
| Independently verified | `reconcile_counts.py`: 25/25 ids mapped, 25/25 covered, 37 ids, core 15, struct 6 | service stats: 32 `satisfies` links, 0 orphans | — |

## Scores

| Dimension | A | B | Why |
|---|---|---|---|
| D1 AC coverage | **3** | **3** | Both cover AC1–AC4 with assertions that would fail if the AC were violated. A proves it mechanically (`AC ledger (test-cases): 25 of 25 covered`); B's is by inspection. |
| D2 Buried decision (T7) | **3** | **3** | Both caught one-row-per-payment from the comment thread. A: TC-7.1/7.2/7.3/7.4 (3→3 rows, columns repeat, 1→1, 0→1) plus REQ-16 for multiple Orders. B: TC-12/13/14/16 with a boundary sweep on payment count and a partial-payment split (70+50). B's TC-16 data design is the sharper of the two. |
| D3 Undocumented truths | **1** | **2** | Currency: both (A REQ-9, B TC-18/19). Amount blank on non-paid rows: **B only** (TC-08, TC-13 assert "amount blank/zero"); A never asserts it. Decimals and "incl. tax": neither. T8 and T9: **neither**. |
| D4 Executability | **3** | **2** | A's steps are what a tester does: "Open Data Export → Custom Reports. Tick the 'Paid only' checkbox. Export and open the generated file", with concrete data ("order total 150.00, received 120.00 after a partial refund"). B's are what a developer writes: "Invoke the mapper with each raw status", "Feed a registrant with an empty payments collection to the row expander", with `testData: "—"` on TC-03, TC-07 and TC-22. |
| D5 Oracle strength | **3** | **2** | A: "Exactly one of TC-REQ-3.1 / TC-REQ-3.2 can pass on one build" is a mutually exclusive oracle; TC-13.1 closes the world ("the distinct values are drawn only from…"). B is mostly strong, but TC-23 asserts "within the defined latency budget" with no budget defined, and TC-22 asserts "no new dedicated FE endpoint is required". |
| D6 Traceability | **3** | **2** | Both trace every case to a requirement with no orphans. Only A carries **AC ids** (`Covers: AC-2, CM-2`), so a failed case can name the criterion it breaks. B's `locator` is prose ("Acceptance Criteria #2 (Values correct)"). |
| D7 Honest uncertainty | **3** | **1** | The decisive dimension. See below. |
| D8 Right level / routing | **3** | **2** | A routes 33 of 37 to `[export/email]` — honest for a feature whose acceptance is "download the file and read it", though it means A's own machine stages would execute almost nothing here. B produced **zero UI and zero manual** cases, so the surface the human actually used is unrepresented, and `levelText` is empty on all 23. |
| D9 Noise | **2** | **2** | A: TC-4.2/4.3/4.4 restate what TC-4.1 covers collectively, and 2.1–2.5 are five cases for five label rows — deliberate (one check per row for a run sheet) but redundant to read. B: TC-03 is near-tautological (asserts the enum's own membership), TC-06 is the declared "negative complement" of TC-05. |
| **Total** | **24 / 27** | **19 / 27** | |

One dimension where B is plainly better and the score does not show it: B emits
**2 risk requirements** with impact and likelihood (`RISK-01` silent
mixed-currency summation, `RISK-02` duplicated rows misread as registrants). A
emits **zero** — it carries risk as a `[risk: High/Medium/Low]` attribute on each
requirement instead. B's RISK-02 in particular ("downstream consumers counting
rows as registrants would over-count") is a real consequence of the row-per-payment
ruling that A noted only in passing.

## D7 — where they genuinely diverge, and why it matters

Both found the same contradiction. AC-2 as published says the paid amount is
"**that Order's total**"; the PO's ruling of 2026-08-28 says it is "**the money
actually received**". They differ on any partially paid, over-paid or refunded
order.

**A kept both readings and refused to pick.** REQ-3 is marked
`(unresolved conflict)` and produced two cases:

> `TC-REQ-3.1 — Version A (AC-2): amount is that Order's total` … "Version A
> passes when the cell reads the Order total 150.00. If the cell reads 120.00,
> version A fails and version B holds — record which version the build
> implements; do not pass both."
>
> `TC-REQ-3.2 — Version B (CM-2): amount is the money actually received` …
> "Exactly one of TC-REQ-3.1 / TC-REQ-3.2 can pass on one build."

**B picked a winner and wrote tests to enforce it.** `PAYRPT-TC-15`:

> "Paid amount = 120 (received), not 200 (billed)."
> Notes: "**Resolves DISC-02: implementation follows per-payment money received,
> overriding AC2's 'Order total'.**"

and `PAYRPT-TC-16`:

> Notes: "**Guards against a regression back to AC2's one-Order-per-row
> interpretation.**"

Nothing in the inputs says which way the build went. B asserted it.

**The evidence says B guessed wrong.** The blinded human verification comment of
2026-09-07 reads:

> "Paid amount shows **the order total incl. tax**, 2 decimals + currency, and
> only for paid rows."

If that is what the build does, B's TC-15 and TC-16 fail on a correct build, and
running B's suite files two defects against a developer who implemented the
published acceptance criteria. A's TC-REQ-3.1 passes, TC-REQ-3.2 fails, and the
report states which version the build implements — the true state of the world.

That is the difference between a test suite and a false-defect generator, and it
is the whole reason the pipeline's grooming keeps both versions.

## Anti-invention check (pass/fail)

**A — PASS.** Every requirement carries `source:` ids. Recon findings are labelled
observations, not requirements, and the file states its own limits: the clone's
HEAD "predates the product decisions recorded on EP-56727 … so it shows the
BASELINE the change was made against — not the delivered feature."

**B — FAIL, three inventions.**

1. TC-15 note: "implementation follows per-payment money received" — a claim
   about the built system, from no source.
2. TC-22 assertion: "No new dedicated FE endpoint is required for the feature to
   function" — asserted, not sourced.
3. TC-23 note: "Budget to be captured in **the test plan §3**" — a document that
   does not exist.

## What A found that nobody else did

Not scored, because the rubric was fixed first. This is the practical payoff. A's
recon stage read the monolith source; B cannot, because its tool takes pasted text
and does not fetch anything itself.

| Finding | Evidence | Why it matters |
|---|---|---|
| **The status enum has six values, not four** — `new`, `pending`, `progress`, `success`, `failed`, `canceled` | `universal/models/Payments.php:51-57` | AC-2 maps four. `new` and `progress` have no label at all. A refused to write cases for them and marked REQ-13 "needs clarification" rather than inventing labels. |
| **The enum is spelled `canceled` (one L); the ticket writes `cancelled`** | same file, line 57 | "A label-mapping keyed on the literal `cancelled` would never match." A concrete, findable defect class that no amount of reading the ticket can produce. |
| **"Test payment" is a gateway-config property, not a per-payment flag** | `Payments.php:74-80` | CM-3 "live payments only" is testable only by configuring the event's gateway in test mode. Execution knowledge a tester needs before starting. |
| **There is no stored "amount received" distinct from `total_value`** | `Payments.php:131` | The AC-2 vs CM-2 conflict may not be two fields at all — so it needs a product decision, not a test. B assumed two fields and tested accordingly. |
| **Refunds are a payment flow with no status of their own** | `Payments.php:62` | Undefined behaviour for both new columns; raised as a question. |
| **AC-3 filters at registrant level while CM-1 makes the output per payment** | grooming REQ-4 | For a registrant with one `success` and one `failed` payment under "Paid only": only the success row, or the whole registrant with both rows? Different exports. **B did not find this**, and neither did the human QA plan. |

## What both machines missed

The two things the human found by touching the running system:

- **T8, the state transition.** "Cancel/confirm of a payment is correctly
  reflected in the export (Cancelled ↔ Paid)." Neither wrote a case that changes
  a payment's state and re-exports. Both files grepped: no hits for transition,
  re-export or after-cancel.
- **T9, the absent row.** "A declined Stripe checkout results in an account-less
  pending payment, so no registrant row is created — such incomplete payments
  correctly do not appear in the report." Neither predicted it; it is a fact about
  the system discovered by driving it.

Both also missed C's ninth bullet, **regression on existing Visitor custom report
configurations** — which matters here precisely because A's own REQ-7 shows the
change alters the row cardinality of an existing export.

## Versus the human (C)

C is nine scope bullets: correct, brief, and not executable by anyone but its
author. It defers the multi-Order rule ("once the rule is confirmed by the PO"),
which is fair — it was written on 2026-08-27, the day before the ruling. Both
machines, reading the same thread a fortnight later, resolved it.

Two things C has that A and B lack: the instinct to **cross-check totals against
the Payments report** (A matched it in TC-REQ-14.1; **B did not cover it at all**),
and the **regression** bullet neither machine wrote.

One thing both machines have that C lacks: coverage of `failed`. C's verification
comment names Paid, Pending, Cancelled and "No payment record" — not Failed —
although AC-2 requires it. A covers it in TC-REQ-2.3 and TC-REQ-4.3; B in TC-02
and TC-06. **Automation caught a gap in the human run.**

## Verdict

- **Keep authoring with the pipeline.** 24/27 against 19/27, and the gap sits in
  the dimensions that decide whether a QA artefact can be trusted: honest
  treatment of conflicting sources, executable steps, AC-level traceability.
- **The generator is better than the 0.43.2 CHANGELOG assumed.** It caught the
  buried comment-thread decision and an unwritten contradiction, its kind spread
  and trace links are correct, and it tags cases for coverage automatically. The
  entry's wording — rejected "on fit, quality unmeasured" — still holds, but
  "quality" should now read **competent at extraction, unsafe at resolution**.
- **The one thing to fix before the generator is used on any real suite:** it
  resolves contradictions by assertion. Anything it produced would need the
  keep-both-versions discipline applied on top, which is most of what stage 2
  already does.
- **Two things worth stealing from B**: separate `risk` requirements with impact
  and likelihood, and the partial-payment data design in TC-16 (one Order, two
  payments of 70 and 50) — a sharper probe of the amount conflict than A's
  two-Orders case.
- **The recon stage is the pipeline's real edge** and is out of the QA Service's
  reach entirely: five findings from the product source, two of them (the
  `canceled` spelling, the six-value enum) the kind that become a defect the week
  after release.
- **Both machines are blind to the running system.** T8 and T9 came from a human
  with an admin panel. That is what stages 8–10 exist for, and a docs-phase-only
  experiment does not exercise them.
