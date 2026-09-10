# ep-qa-pipeline — retrospective from the EP-53767 run

**Story:** EP-53767, Global Search — Sponsored Exhibitors
**Run:** one session, 2026-08-10 to 2026-08-11, stages 5–10 (plus an unplanned opportunistic re-run)
**Scale:** 48 suite cases, 6 structural checks, 8 run-sheet rows, 6 Jira tickets touched, 1 bug filed
**Author:** the same session that ran it. Written at the plugin owner's request.

Read alongside `ep-qa-pipeline-retrospective-EP-47675.md`. That run's headline was **24 published verdicts
overturned**. This one's is **zero**. The failure mode did not disappear — it moved, and the new location
has no verification loop on it at all. That is the substance of this document.

Verdict fates below are measured from the stage reports, the suite case notes, and the stage-10
reconciliation, not from recollection.

---

## 1. Scoreboard

| Stage | Definite verdicts published | Overturned | Accuracy |
|---|---|---|---|
| 6 — code review | 14 (3 PASS · 1 FAIL · 8 N/A · 2 SPEC-DEFECT) | 0 | **100%** |
| 7 — api-testing | 1 PASS (+2 BLOCKED, both correct at the time) | 0 | **100%** |
| 8 — web-testing | 25 (24 PASS · 1 FAIL CONFIRMED) | 0 | **100%** |
| structural `[UI]` checks | **6 of 6 executed** | 0 | **100% coverage** |

Stage-10 ingestion: **11 CONFIRMS · 6 FILLS · 0 RETRACTS · 0 non-standard · 0 unmatched · 0 not run.**

Two of EP-47675's worst findings are closed by this run's evidence:

* **F3 — structural checks swallowed by an escape hatch.** Last run: 0 of 15 executed. This run: **6 of 6**,
  and 4 of them FAILED, which is how the "declared but not built" scope gap was proved empirically rather
  than inferred from a code read. The fix held.
* **F1 — web-testing generalises from a single session.** No FAIL was published from a single observation.
  Every BLOCKED was conservative and every one turned out to be genuinely unavailable at the time. The
  16 false alarms of EP-47675 did not recur.

Both BLOCKED clusters were also *correct to be conservative*: 8 of stage 8's BLOCKEDs later resolved to
6 PASS and 1 FAIL once fixtures existed, and none of them was a disguised defect.

---

## 2. Where the errors actually were

**Five errors. None of them reached a published verdict. All five were in the layer above the stages —
narrative, summary and triage — and all five were caught by the human, none by the pipeline.**

| # | Error | Origin | Caught by |
|---|---|---|---|
| E1 | `RISK-CR-5` described as "a live sponsor-billing inflation route". It is not user-reachable on this build. | stage-8 report authoring, propagated by the orchestrator into Jira | human |
| E2 | "There is no search field on the Global Search results page." There is — behind the header search icon. | orchestrator DOM probe | human |
| E3 | Proposed reclassifying TC-REQ-16.4 as SPEC-DEFECT. The case was correct; I misread which two blocks it names. | orchestrator triage | self, after re-reading the case — but only after publishing the wrong claim to Jira |
| E4 | TC-REQ-8.2 reported FAIL: "arrows rendered and enabled". They were the card's calendar and envelope buttons. | orchestrator DOM probe | human, with a screenshot |
| E5 | TC-REQ-17.3 / 25.1 answered from a session logged in as the **unrestricted** account, inverting the result. | orchestrator, reading its own probe and then the human's screenshot | human, by reading the profile name |

**Four of the five are the orchestrator, not a stage subagent.** The stage skills have accumulated real
discipline — absence-check protocol, positive/negative controls, baseline-twice, probe-before-blocking. The
orchestration layer that summarises and triages their output has none of that, and it is now the dominant
error source.

### The two shapes

**Shape A — identification by geometry instead of identity (E2, E4, E5).** Three of five errors are the same
mistake: reading UI state without establishing *which element* or *which principal* was being observed. E4
filtered buttons by `y > 550` and got the card's own action buttons, which sit exactly where the navigation
arrows would be. E5 read a page without checking who was logged in. E2 enumerated a collapsed control and
concluded it did not exist.

E4 is the most serious event in the run: **it was one step from filing a defect against a dev for behaviour
that is correct.** The human's screenshot stopped it.

**Shape B — a caveat that exists in the detail but not in the claim (E1).** Batch A recorded `OBS-3`
correctly: a guest has no search input on that page, so the soft-navigation path was driven through the
app's internal router. The impact line of the same report then asserted a live billing-inflation route
anyway. The qualifier and the claim were both written, in the same file, by the same agent, and never
reconciled.

---

## 3. Findings, worst first

### F1 — the orchestration layer has no verification loop (severity: critical)

Every stage skill mandates controls, probes and second reads. The orchestrator, which writes the human
summary, does the triage, decides what gets filed and answers the user's questions, mandates nothing. All
five errors above live there. `qa-run-analyzer` checks the *stages*, not the summary of them.

Cheapest effective fix: **the orchestrator must not assert a defect, a reclassification or a reachability
claim from its own single observation.** Same rule EP-47675's F1 imposed on stage 8, applied one level up.
Where it makes its own measurement — as in E2/E4/E5 — it should dispatch that measurement to a subagent
bound by the web-testing rules rather than improvising it inline.

### F2 — no rule forces a reachability qualifier into the claim it qualifies (severity: high)

E1 is not a missing observation, it is a missing propagation. Proposal: any impact statement in a report
must restate the precondition under which it holds, in the same sentence. "Sponsors are over-counted **when
the query is changed through client-side routing, which no UI control on this build does**" would have been
correct and would have prevented the wrong Jira line.

Mechanically checkable: a finding whose evidence section contains a reachability caveat but whose impact
line does not mention it is a lint failure.

### F3 — reclassifying a case without re-reading it (severity: high)

E3 proposed rewriting a P0 case on the strength of a summary of it. The case's own `goal` and
`preconditions` said plainly what it asserted, and contradicted the proposal. **Before any stage proposes
SPEC-DEFECT or a case correction, it must quote the case's goal, preconditions and assertions verbatim into
its finding.** Cheap, and it would have stopped this cold.

### F4 — stage-9 fixture claims are asserted, not verified (severity: high)

Four fixture facts in the run sheet were wrong, and each would have cost the tester real time:

| Claim | Truth |
|---|---|
| Event 6032 is a valid zero-sponsor fixture | Its own Global Search is in the EP-55910 state — an empty page proves nothing |
| Event 6032 has 15 exhibitors | 359 |
| 10 sponsor toggles produce the "all disabled" state | The pool is 15; disabling 10 promoted 5 hidden ones in (EP-55937's cap masked them) |
| `Sponsor bar Web` baseline is `#FF643F` / `#7F56D9` | `#8f6b4e` — stale in three separate places |

Stage 9 already probes *blocked reasons* (rule 5) and does it well — it disproved four. It does not probe
its own *positive* fixture claims with the same rigour. The rule should be symmetric: a fixture a row
depends on must be verified end-to-end, including the host's own health, before the row is written.

The 10-vs-15 error is the instructive one: a human following the sheet would have stopped at 10, seen
sponsors still present, and recorded a false FAIL.

### F5 — `reconcile_counts.py` has two silent defects and a self-test that passes anyway (severity: high)

* `ID_RANGE` expands any `TC-REQ-<n>.<m>` followed by a dash and a number into a range. The heading
  `## TC-REQ-20.1 — 30 characters accepted and saved` therefore parses as `20.1–20.30`, inventing **26
  phantom case ids** and reporting them as missing from two stages.
* `CASE_ID` (`TC-REQ-\d+(?:\.\d+)*`) allows no letter suffix, so `TC-REQ-12a.1`, `12b.1` and `12c.1`
  collapse into one id `TC-REQ-12`. This is a **silent under-count**: had one of the three sorting cases
  been dropped, the gate would not have noticed.

`--self-test` passes with both defects present, so it does not cover either id-parsing path. The count gate
is the pipeline's last line of defence before publication; it should not be the least tested component.
Fixes: anchor the range form to `\.\d+\s*[–-]\s*\d+\.\d+`, and use `TC-REQ-\d+[a-z]?(?:\.\d+)*`.

### F6 — the Jira archive is not byte-faithful and the pipeline did not notice (severity: medium)

Jira's markdown→ADF conversion **silently truncated** an archive comment containing nested code fences.
The retry succeeded only by de-fencing the inner blocks, so `EP-53767-web-testing.md (part 2/5)` is not
byte-identical to disk — which defeats the archive's stated purpose of letting a future agent rebuild the
reports. The truncated comment could not be deleted, so a permanent "skip 143658" instruction now rides
with the ticket.

Worse, my own caveat about it listed comment ids that do not exist (143657, 143663), needing a third
correction comment. **Post-write verification should read the comment back and compare lengths**, and the
archive convention should forbid nested fences by construction (indent inner blocks, or use a
non-backtick delimiter).

### F7 — the run sheet's routing table under-listed the manual scope (severity: medium)

`qa-run-analyzer` caught this — the table named 5 cases where the verdict sets implied 11. Credit where due:
this is the analyzer doing exactly its job, and it is the one place a downstream check caught an upstream
error in this run. The lesson is the inverse of F1: the checks that exist, work. The gap is where none
exist.

### F8 — a mutation endpoint destroyed data and only a snapshot saved it (severity: medium)

Stage-9 provisioning wiped all **930** permission-matrix pairs on event 3551 — the save endpoint expects
`relations` as a single JSON string, not form-array keys. Full recovery was possible **only** because a
snapshot had been taken first, and it verified byte-identical afterwards.

The snapshot-first discipline worked and should be promoted from good practice to a hard rule in
`provisioning-rules.md`: **no write to a collection-shaped admin endpoint without a persisted snapshot and
a verified restore path.** The later sponsor-flag work followed exactly this pattern across three
mutate/restore cycles with 0 drift each time, which is the model.

### F9 — the mandatory revert is not machine-enforced (severity: low)

The run sheet declares row 5's revert mandatory. It was waived by the QA owner, which is legitimate — but
nothing in the pipeline would have noticed had it simply been forgotten. `Sponsor bar Web` is still
`#7F56D9`. A post-run environment check comparing against the provisioning snapshot would close this.

---

## 4. What the design got right

**Suite-first case reconstruction.** The docs phase published to QA Service and posted no Jira archive, so
the code phase rebuilt requirements, checklist and 48 test cases from the suite. The channel split came out
`39 [UI] · 2 [API] · 7 [API][UI]` — matching the docs phase's own published figures exactly. This is the
0.11.2 dedup design working as intended.

**Provisional-until-stage-10, again.** Less dramatic than last run because there were no retractions, but
it is why the badge-contrast FAIL never became a dev ticket, and why the story got a decision-focused note
instead of a false handback.

**Dedup before drafting killed 3 of 4 bug candidates.** One was an exact duplicate of EP-55910; one was not
user-reachable; one was a specification question. **Only one of four candidates deserved to exist.** Without
that step this run would have filed four tickets, three of them noise, into an area that already has five
open defects.

**The highest-value case got treatment no human round would have given it.** TC-REQ-16.1 — the invariant
organisers bill on — was settled with a double-read baseline, one countable action, a re-read after a
measured ingestion lag, positive and negative controls, and gap-free WebSocket frame capture installed
before page scripts. It proved the guarantee is *structural* (the organic card emits no sponsor event at
all), which is stronger than the counter arithmetic that prompted it. A hand-tester would have watched the
rail and guessed.

**api-testing remains the most trustworthy stage per unit of cost** — the same conclusion as EP-47675. Its
refusal to infer a delta it had not observed is why the WebSocket-only transport was discovered rather than
papered over.

**Test-design reduction on the run sheet.** 9 unverified cases and ~24 spot-check candidates compressed to
**8 rows**, via decision-table collapse on a mutually-exclusive pair, multi-assertion single observations,
equivalence partitioning that turned a destructive fixture into a read-only check, and fixture chaining.
The tester walked it in under an hour. This is the single biggest human-time saving in the run and it came
from applying test design rather than from tooling.

---

## 5. What this run cost

~2.9M subagent tokens across 13 dispatched agents, plus the orchestrator. Roughly: stages 5–8 consumed
~1.2M, stage 9 provisioning ~0.34M, the opportunistic re-run ~0.17M, publication and write-back ~0.53M.

The expensive stages were the two that produced the run's best evidence (8B statistics, 9 provisioning) and
the one that produced its worst error (8B's impact line). Cost is not the lever here — E1–E5 were all cheap
mistakes in cheap places.

---

## 6. Errors made by this session, for symmetry

All five in section 2 are mine. Four were caught by the human within one exchange, one by myself only after
publishing the wrong claim.

Beyond those: I stated 17 suite write-backs when 16 were enumerated (the subagent caught it and refused to
invent a 17th, correctly); I published an archive id list that was wrong; and I spent three tool calls
trying to screenshot from the container before recognising the sandbox proxy blocks browser traffic to that
host — my own escalation rule says stop and reassess after three, and I only just honoured it.

The human corrected me five times and was right five times. That is the same trust problem EP-47675 named,
relocated from the stages to the layer above them.

---

## 7. The one-line conclusion

**The stage skills have become a good verdict engine; the orchestration layer has become the bad one.**
EP-47675's fixes worked — 0 retractions, 100% structural coverage, no single-observation FAILs. But the
errors moved up a level, into summarising, triaging and answering, where no control, probe or second read
is required of anything.

Ranked by value per unit of effort: **F1** (no orchestrator claim from a single observation, and dispatch
its own measurements to rule-bound subagents), **F5** (fix the count gate and test its id parsing), **F4**
(verify positive fixture claims as rigorously as blocked reasons), then **F2** and **F3**.
