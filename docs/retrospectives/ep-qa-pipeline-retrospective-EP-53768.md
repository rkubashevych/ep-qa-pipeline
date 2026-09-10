# ep-qa-pipeline — retrospective from the EP-53768 run

**Story:** EP-53768, Global Search — Sponsored Products
**Run:** one session, 2026-08-11, stages 5–10 complete (plus a test-design pass and two machine re-executions the skill does not define)
**Scale:** 66 suite cases, 21 structural checks, 4 repos probed, 9 Jira comments posted, 1 bug filed, 1 bug re-prioritised, 4 new suite cases created
**Author:** the same session that ran it. Written at the plugin owner's request.

Read alongside `ep-qa-pipeline-retrospective-EP-47675.md` (24 verdicts overturned) and
`ep-qa-pipeline-retrospective-EP-53767.md` (zero overturned). This run sits between them and closer to
the first: **22 of 66 published verdicts changed after publication.** Every single correction came from
the human, none from the pipeline.

All numbers below are computed from the stage reports, the suite case notes, the Jira comment history
and the live re-measurements — not from recollection. The comparison baseline is the human-summary
comment as published (`143917`), against the final state after stage 10.

---

## 1. Scoreboard

| Stage | Definite verdicts published | Overturned | Accuracy |
|---|---|---|---|
| 5 — pr-summary | n/a (map, not verdicts) | — | code under test correctly identified with no dev sub-tasks to guide it |
| 6 — code review | 13 (1 FAIL · 12 NOT IMPLEMENTED) | **7** | **46%** |
| 7 — api-testing | 1 FAIL | 0 | **100%** |
| 8 — web-testing | 34 (28 PASS · 5 FAIL · 1 FAIL CONFIRMED) | **4** | **88%** |
| 8 — BLOCKED calls | 12 | **10 avoidable** | **17%** appropriate |
| structural `[UI]` checks | 21 of 21 executed | 0 retracted, 1 never confirmed | **100% coverage** |

**Stage-10 ingestion: 31 CONFIRMS · 9 RETRACTS · 0 unmatched · 0 not run.**

### The 22 changed verdicts, by shape

| Shape | Count | What it means |
|---|---|---|
| BLOCKED → PASS | 9 | The case was executable all along |
| NOT IMPLEMENTED → PASS | 6 | The feature exists; the run said it did not |
| FAIL → PASS | 3 | False alarm on a real requirement |
| FAIL CONFIRMED → `na` | 1 | Defect reported against a non-requirement |
| PASS → `na` | 1 | A pass that was never real coverage |
| BLOCKED → OBSERVED / BLOCKED-DEFECT | 2 | Right call, wrong stated reason |

Of 7 defects reported to the business: **1 confirmed and filed, 3 withdrawn, 3 never verified.**

### What EP-53767's fixes did and did not carry over

- **Structural checks (that run's F3): held.** 21 of 21 executed and reported. The escape hatch stayed shut.
- **Count reconciliation: held.** All three stage reports were internally consistent, Scope matched
  Statistics, and the count gate passed before publication. The three "phantom" ids the checker flagged
  were verified as its own regex artifacts rather than suppressed.
- **"Do not generalise from one session" (that run's F1): did NOT hold.** It regressed in a new form —
  see F1 below.

---

## 2. Where the errors actually were

**Nineteen wrong verdicts, in three clusters, each with a single distinct cause. None was caught by the
pipeline. All were caught by the human — three of them by two screenshots and one sceptical question.**

### Cluster A — absence asserted without the control the case demanded (5 verdicts)

TC-REQ-17.1, 18.2, 10.3, 32.1, 32.2.

Every one of these cases carries an explicit instruction in its own `notes` requiring a positive control
or a scope confirmation *before* recording a negative. The instructions were read, restated in the
report, and then not honoured:

- TC-REQ-17.1 / 18.2: step 1 *is* the Marketplace positive control. It emitted no event, so the
  same-report comparison the case asks for was never made. The run substituted a code-level observation
  about event typing and published FAIL. The counters were incrementing correctly the whole time.
- TC-REQ-10.3: no proof rotation was alive. Re-measured with a control: 0 changes in 30 s of held focus
  versus 11 changes in 30.5 s without. The original "advanced 3× in 15.5 s" came from a browser that
  something else was navigating.
- TC-REQ-32.1: the case says *"confirm it is in scope before recording a FAIL."* The run recorded one
  without confirming. REQ-32 exists only in a design comment and was never adopted.

### Cluster B — scope concluded from code absence without opening the product (6 verdicts)

TC-REQ-13.1, 13.2, 14.1, 14.2, 15.1, 15.2.

The run reasoned: no `admin-ui` branch exists, `SponsorsController.php` is untouched, EP-54829 lists
sorting as out of scope, therefore sorting is not implemented. Each premise was true. The conclusion was
false. **`sponsor_products_sort_type` was sitting in Admin → Sponsors → Settings the whole time** —
"Sponsors sorting in Products list", three radio options — and the human confirmed switching modes does
change the rail order.

Six cases were reported to the business as "not implemented, out of scope, not a defect". That is worse
than a false FAIL: a false FAIL gets investigated, whereas "out of scope" invites the team to stop
looking.

### Cluster C — BLOCKED as the default for "I could not set this up" (10 of 12)

Stage 8 blocked 12 cases. Only **two** were genuinely blocked:

| Genuinely blocked | Avoidable |
|---|---|
| TC-REQ-22.2 (blocked by EP-53449 itself) · TC-REQ-21.2 (blocked by an admin defect discovered later) | 6 needed **one admin field** — `product_search_limit`, which stage 9 itself found hours later · 3 needed a human hand (colour publish, embedded report, second event) · 1 (10.4) depended on the wrong FAIL in cluster A |

Six of those ten were cleared by this session in about fifteen minutes once the field was known. The
information was inside the run's own artifacts before the block was published — stage 9's fixture work
identified `product_search_limit` and proved it at 1 and 2 products. Nothing propagated that back.

---

## 3. Findings, worst first

### F1 — the positive-control rule is written into every case and enforced nowhere (severity: critical)

This is the same failure as EP-47675's F1, mutated. The docs phase now writes excellent per-case
guardrails — *"step 1 is the mandatory positive control"*, *"confirm it is in scope before recording a
FAIL"*, *"without it a report that shows nothing for any source would read as a FAIL of the block rather
than of the instrumentation"*. The execution stages quote those sentences into their reports and then
publish verdicts that violate them.

Nothing in the pipeline can tell the difference between "control passed, then the assertion failed" and
"control produced nothing, and I called it a failure anyway". Both render as `FAIL` in the results table.

**Fix:** make the control a required, separately-recorded field. A `FAIL` or an absence-`PASS` on a case
whose notes contain a control instruction must carry a `control:` line stating what the control produced,
in the same report row. Absent or empty → the stage must emit `BLOCKED — control unavailable`, and the
count gate must refuse to publish. This is mechanically checkable today: the instruction strings are
already in the case notes, so a script can list which rows require a control line and diff that against
which rows have one.

### F2 — "NOT IMPLEMENTED" can be published from a code read alone (severity: critical)

Twelve cases were classified from repository evidence. Six were wrong. The classification is
*attractive* precisely because it feels safe — it reports no defect and blames nobody — so it gets less
scrutiny than a FAIL, while carrying more consequence: it tells the business to stop testing.

**Fix:** `NOT IMPLEMENTED` must require a runtime observation of the actual surface, recorded as such.
For an admin-panel setting that means one screenshot or one field enumeration of the settings page, not
four branch probes. Code absence downgrades to `QA — suspected not implemented, needs a look at the
running product`. Note the run *did* have the tool: stage 8 drives a browser and could have opened the
page in one call.

### F3 — BLOCKED has no cost and no cross-stage learning (severity: high)

10 of 12 blocks were avoidable, and 6 of them were unblocked by information that **the same run
discovered one stage later**. Stage 9 found `product_search_limit`, proved it at 1 and 2 products, wrote
the recipe into the run sheet — and stage 8's BLOCKED verdicts stayed published as-is. There is no
mechanism for a later stage to revisit an earlier stage's blocks.

**Fix, two parts.** (1) Before publishing any `BLOCKED`, the stage must name the *specific* setting or
fixture that is missing and state that it searched the admin surface for it — "needs an event with 1
product" is not sufficient when a global field controls exactly that. (2) Stage 9 must diff its own
fixture capabilities against stage 8's block list and re-dispatch anything it can now create. That is a
cheap, well-defined loop and it would have recovered 6 cases automatically here.

### F4 — a non-exclusive browser silently invalidates timing verdicts, and the run published anyway (severity: high)

Stage 8 detected the problem, described it accurately — the page's query string changed itself three
times, a stray tab kept counting views — recorded it in its evidence-quality notes, and then published
timing FAILs measured in that environment. The disclosure was honest and completely ineffective, because
nothing downstream treats it as disqualifying.

**Fix:** browser exclusivity is a precondition, not a caveat. On detecting an unexpected navigation or
URL change mid-stage, every timing and animation assertion in that session must be voided and re-run,
not annotated. The stage already has the detection; it lacks the consequence.

### F5 — the "reported defects" list is a narrative artifact with no verification gate (severity: high)

Seven defects reached the business. Three were withdrawn, three were never verified at all, one was
real. The three unverified ones — view re-counting, `place` always `search`, the stale setting
description — were written into the human summary and the story note with the same voice and confidence
as the one that had been reproduced twice with controls.

**Fix:** each defect line in the human summary must carry its evidence class explicitly:
`reproduced-with-control`, `observed-once`, or `inferred-from-code`. A defect that is not
`reproduced-with-control` may not be listed as confirmed, and must not appear in the story note's
defect groups.

### F6 — design-comment statements were treated as requirements (severity: medium)

REQ-32 (badge contrast) existed only in an EP-54156 comment, never in the acceptance criteria. The docs
phase noticed, asked the question, got no answer, and generated two cases anyway. The code phase then
published a FAIL CONFIRMED against it and drafted a bug. **The identical mistake had already been made
and rejected on the sibling EP-53767 run.**

**Fix, agreed with the owner during this run:** statements that appear only in a design comment and
never reach the acceptance criteria are excluded from test design. Record them as open questions on the
requirements file; do not mint cases from them.

### F7 — no FAIL in this run had image evidence (severity: medium)

The Playwright MCP screenshot root is not a Cowork-connected folder on this host, so no screenshot could
be collected for any finding. Disclosed rather than faked, which is right — but it also means every
retraction argument in this run was conducted in prose, and the human had to produce their own
screenshots to overturn two verdicts.

**Fix:** treat a collectable screenshot path as an environment precondition, checked at step 0 alongside
credentials. If it is unavailable, say so before stage 8 runs, and mark every FAIL in the report
`text-evidence-only` so the reader knows what they are weighing.

### F8 — no stage reconciles a later discovery against an earlier published claim (severity: medium)

This run made four discoveries that contradicted earlier published output: the sorting field, the
`product_search_limit` field, the `api_total` inconsistency, and the toggle-persistence defect. All four
were found after the claims they contradicted had been posted to Jira. Every reconciliation was done by
hand, in conversation, by the human noticing.

**Fix:** add a cheap final pass that re-reads the published human summary against the final artifact set
and lists contradictions. The pipeline already has a post-publish verification step; it currently checks
*delivery* (did the comment land, did the write-back land) but not *consistency*.

### F9 — the verdict map was built by regex over report prose (severity: medium, self-inflicted)

I built `EP-53768-verdicts.json` by pattern-matching status words across each report row. Two PASS rows
that happened to mention a FAIL risk were mislabelled `FAIL`. The error was caught only because stage 9
independently cross-checked the file against the write-back plan and flagged the contradiction.

The suite write-back used the correct file, so nothing wrong was published — but the near-miss is the
finding. Derive verdict maps once, from explicit per-status id lists, never by scraping prose.

**Credit where due:** stage 9 caught this. It is the one cross-stage verification that worked, and it
worked because it compared two independently-derived artifacts rather than trusting one.

### F10 — I published an inaccurate correction count (severity: low, self-inflicted)

The story note on EP-53768 says *"4 were withdrawn under scrutiny"*. The correct split is **3 withdrawn
and 3 never verified**. Withdrawing and never-verifying are materially different — the first is a
retraction, the second is an open question — and collapsing them understates how much of the original
report was unproven. Corrected on the ticket.

---

## 4. What the design got right

Worth stating plainly, because six of these are why the errors were recoverable at all.

- **The suite as source of truth.** The docs phase published no Jira case archive, and the code phase
  rebuilt all 66 cases, their traceability and the REQ-N ↔ stableId mapping from the QA Service suite
  alone. Counts reconciled exactly against the tracker: 66 = 66 = 66, channel split 58/7/1 confirmed.
- **The retraction convention is excellent and it held under real load.** Three retraction rounds plus a
  40-case stage-10 ingestion, all with `⚠ CURRENT VERDICT` first lines and `SUPERSEDES` history. Across
  ~100 note writes, **no case lost its original text and every `TC-REQ` id still leads its block.** The
  audit trail of this run's own mistakes is complete and readable — which is the whole point.
- **The count gate.** Every report's Scope agreed with its Statistics and with the mechanical count
  before anything was posted. It also correctly surfaced ids that needed judgement rather than silently
  passing them.
- **The archive convention, once the fence bug was fixed.** Reports contain fenced code blocks, so
  three-backtick wrapping truncated `api-testing.md` at its first internal fence. Switching to dynamic
  fence length and then verifying the round-trip **through the pipeline's own `extract_archive.py`**
  proved all four files byte-identical. That verification step should be mandatory, not incidental.
- **Stage 7's endpoint discovery.** `getUserStatistics` with `target=product_search` was not in the
  ticket, and it is the instrument that made per-account statistics assertions possible at all. It also
  correctly established that statistics are written over a WebSocket and therefore cannot be
  API-exercised — a genuinely load-bearing negative result.
- **Stage 9's restore discipline.** It captured `product_search_limit` before touching it, restored it,
  and verified the restore. This session followed the same pattern for the sponsor toggles and it is the
  only reason a half-completed M9 was recoverable: 10 named companies captured, 4 flipped, all 10 verified
  restored, and the rail confirmed back to its exact 13-id baseline.
- **`SPECIAL ATTENTION` in the QA sub-task description.** It correctly predicted the profile-photo dialog
  hazard, EP-53449, EP-51440, the shared-`SponsoredSlider` blast radius, and the one-card conflict. Where
  the run followed it, the run was right.

---

## 5. Two things the skill does not define, and should

**A test-design minimisation pass.** The stage-9 run sheet had 32 rows organised per case. Reorganising
by fixture state and applying equivalence partitioning on product count, boundary analysis on 0/1/2/3,
co-observable bundling, and dependency collapse produced **14 rows with identical coverage**, then 11
after the machine executed three. That is a 66% reduction in human time for no loss, and it is currently
not part of stage 9 at all — it only happened because the owner asked for it.

The insight generalises: **the cost unit of manual QA is fixture setup, not observation.** Six of the
final rows needed no setup whatsoever and carried 25 cases between them. Stage 9 should group by state
and prove coverage, exactly as `EP-53768-minimal-design-rationale.md` does.

**Machine re-execution of blocked rows.** Once the fixture mechanism is known, rows like "one product →
no arrows" are better done by machine than by hand: deterministic, controlled, and with the cache waits
absorbed by something that does not mind waiting. This session executed M7 and M8 that way and cleared
five cases. There is no stage for it.

---

## 6. What this run cost

| | |
|---|---|
| Wall clock | ~5.5 hours, one session |
| Subagents | 7 (pr-summary, code-review, api-testing, web-testing, archive post, write-back ×2, verification, stage 9) |
| Transient infrastructure failures | 3 — one 529 mid-stage-8 (resumed from transcript, no evidence lost), one 502 on a tool call, one device-bridge disconnect that left the event mid-mutation |
| Jira comments posted | 9 across 3 issues |
| Suite writes | ~100 note edits, 4 new cases created, 2 cases set `na` |
| Human interventions that changed the outcome | **5** — two screenshots, one "is he really restricted?", one "is this frontend or backend?", one "all cases pass" |

The device-bridge disconnect deserves a line of its own: it dropped while `product_search_limit` was set
to 1, leaving event 3551 in a state that would silently corrupt anyone else's testing. The container had
no working admin session to fix it. **Any stage that mutates shared state should write its restore
recipe to a file before the first mutation**, so a different session can complete the restore. This
session did that for the sponsor toggles only after the near-miss.

---

## 7. Errors made by this session, for symmetry

1. Built the verdict map by regex over prose (F9). Two mislabels; caught by stage 9, not by me.
2. Published "4 withdrawn" when the truth was 3 withdrawn and 3 unproven (F10).
3. Typed into the count field without clearing it, producing "20" instead of "2". Caught by reading the
   value back before saving — which is why reading back before saving is not optional.
4. Flipped 10 sponsor toggles with a 700 ms wait, of which 6 silently reverted. Retried at 2500 ms, same
   6 reverted. Should have verified persistence on the *first* toggle before batching the other nine.
5. Asked the user to log into the admin panel before establishing that the Playwright browser had its own
   cookie jar separate from their Chrome profile — wasted a round trip.
6. Wrote three consecutive walls of text after being told twice that the answers were too long.

---

## 8. The one-line conclusion

**The pipeline's stages are now good at producing evidence and still unable to judge whether their own
evidence supports the verdict they publish** — 22 of 66 verdicts changed, and the pipeline caught none of
them. Every fix in section 3 is a variation on one theme: make the verdict carry its warrant, and refuse
to publish when the warrant is missing.

The single highest-value change is **F1** — require a recorded `control:` line on every negative verdict
and let the existing count gate reject the report without one. It would have prevented 5 of the 22
changed verdicts and 3 of the 4 withdrawn defects, and it costs one column in a table.
