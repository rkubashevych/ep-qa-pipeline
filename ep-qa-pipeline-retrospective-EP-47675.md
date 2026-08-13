# ep-qa-pipeline — retrospective from the EP-47675 run

**Story:** EP-47675, Unified Global Search page
**Run:** three sessions, 2026-08-04 to 2026-08-05, stages 5–10
**Scale:** 118 run-sheet rows, 108 suite cases, 9 Jira tickets touched
**Author of this note:** the stage-10 session. Written at the plugin owner's request.

Everything below is measured from the run sheet's `Machine verdicts` archive sheet, which preserves each
stage's original verdict, compared against the final adjudicated verdict. It is not recollection.

---

## 1. Scoreboard

| Stage | Verdicts published | Correct | Accuracy |
|---|---|---|---|
| 6 — code review | 17 | 12 | 71% |
| 7 — api-testing | 10 | 7 | 70% |
| 8 — web-testing | 37 | 20 | **54%** |
| structural `[UI]` checks | 0 of 15 executed | — | **0% coverage** |

Stage 10 ingestion result: **75 CONFIRMS, 24 RETRACTS, 14 FILLS, 3 non-standard, 2 not run.**

### Every stage errs in the same direction

Stage 8's 17 errors:

| Wrong call | Count |
|---|---|
| FAIL → actually PASS | 12 |
| BLOCKED → actually PASS | 3 |
| FAIL → actually PARTIAL | 1 |
| BLOCKED → actually FAIL | 1 |

**Sixteen of seventeen were false alarms.** Stage 6 shows the same asymmetry: 4 of 4 PASS predictions
survived runtime, but only 8 of 13 FAIL predictions did.

This is the single most important number in this document. A pipeline that misses defects is dangerous.
A pipeline that invents them burns human time and teaches the human to distrust it. In this run the human
overrode the machine nine times and was right nine times. That is a trust problem, and it is a design
problem, not a model problem.

---

## 2. What the design got right

**Provisional-until-stage-10 is correct and it saved the run.** 24 published verdicts were overturned. If
the code phase had posted a final handback at step 8, the record would today assert 15 failures that do
not exist and the story would have been routed on that basis.

**Archiving machine verdicts in a separate sheet from the human's column.** This is the quiet hero. It is
the only reason the accuracy table above can be computed at all. Had stage 8 written into the column the
human uses, the evidence of its own error rate would have been destroyed on contact. Keep this. Consider
making it explicit in the runsheet skill that the machine column is **immutable after publication** — the
day-3 session overwrote parts of it, which cost real effort to reconstruct.

**api-testing is the most trustworthy stage per unit of cost.** All three of its errors were conservatism:
`BLOCKED` or `PARTIAL` where the truth was more definite. That is the correct way to be wrong.

**Join-by-TC-id in stage 10.** 118 rows, zero unmatched. The hard rule against joining on row position is
doing real work.

---

## 3. Findings, worst first

### F1 — web-testing generalises from a single session (severity: critical)

Stage 8's entire browser pass ran in one session whose `pagesOptions` array was empty. With zero options
the header component renders no select, `searchPage` stays undefined, and the submit handler falls through
to `/marketplace`. **Every one of its nine entry-point observations was a correct description of that
broken session.** The error was not observation, it was generalisation without a control.

Fifteen wrong verdicts, one root cause, three sessions of downstream damage.

> **Proposed change — `web-testing/SKILL.md`, Hard rules:**
> *Before recording FAIL or FAIL CONFIRMED on any case that depends on a shared page element (header,
> nav, selector, global control), re-observe it in a second fresh session — new tab, cleared state, and
> once as guest if the case permits. If the two sessions disagree, the verdict is BLOCKED (intermittent),
> never FAIL. Record both observations.*

Cost: one page reload per FAIL. It would have prevented 15 of the 17 errors.

### F2 — stages corroborate each other's bias and report it as confirmation (severity: high)

Stage 8's report states: *"no stage-6 FAIL was rejected — all 11 reproduced."* It presents that as
strengthening the result. Both stages share the same prior, so agreement carries almost no information.
Eight of those 11 survived; three did not.

> **Proposed change — `web-testing/SKILL.md` and `qa-run-analyzer`:**
> Forbid agreement-with-an-earlier-stage from being reported as corroboration. Where stage 8 confirms a
> stage-6 FAIL, the report line must state what was *independently observed at runtime*, not that the
> prediction matched.

### F3 — the structural `[UI]` checks have an escape hatch that swallowed all 15 (severity: high)

`web-testing/SKILL.md` step 6 currently says:

> *Do not navigate to extra pages only for structural checks — cover the ones on the pages the run already
> visits; list the rest as not visited.*

Reasonable in intent, but in practice 15 of 15 checks covering REQ-1, 8, 23, 26, 37 and 40 were listed as
not visited and then carried unexecuted through three sessions. No later stage claims them. They were run
for the first time on day 3, by hand, and produced one genuine finding.

> **Proposed change:** keep the no-detour rule, but make unexecuted structural checks a **named blocker in
> the stage-8 report header** with an owner, and have `qa-manual-runsheet` emit them as first-class rows
> rather than a footnote. If a structural check is still unexecuted at stage 10, it must appear in the
> "Not run" section, not vanish.

### F4 — nothing contains cascade failures (severity: high)

The human marked 30 rows `Failed by TC-REQ-5.1`. Entirely reasonable behaviour. But the run sheet has no
way to express "this row's verdict is contingent on that row", so when TC-REQ-5.1 was overturned, 30 rows
had to be unwound by hand and re-derived one at a time.

> **Proposed change — `qa-manual-runsheet`:** add a `Depends on` column. When a row names an upstream TC
> and that TC's verdict changes, stage 10 flags every dependent row for re-derivation automatically
> instead of leaving it to whoever notices.

### F5 — no environment capability check before testing starts (severity: high)

Two sessions ran before anyone established that AI Search does not serve on alpha2. Three ran before
anyone discovered a third environment, `real-alpha2`, existed — a discovery that overturned four verdicts
and turned "unverifiable" into "verified" for the whole buyers family.

The two available environments turned out to be broken in mirror image: alpha2 has no AI ranking,
demoalpha has a dead keyword index. Several requirements are therefore uncoverable on either host. Nobody
knew that until day 3, and it changes how the whole run should have been planned.

> **Proposed change — `qa-pipeline-code`, before stage 6:** a short **environment capability probe**. Ask
> the user to list every candidate host. For each, record `data-version`, the module flags the story
> depends on, and one smoke query. Publish the matrix at the top of the run. Then add a standing rule:
> *before recording BLOCKED, NOT TESTABLE or UNVERIFIABLE, check the case on every host in the matrix.*

This one probe would have prevented the two most embarrassing wrong conclusions of the run.

### F6 — the verdict vocabulary is too loose to join on (severity: medium)

In circulation across the run: `PASS`, `FAIL`, `FAIL CONFIRMED`, `FAIL REJECTED`, `BLOCKED`, `PARTIAL`,
`NOT TESTABLE`, `QA`, `SPEC-DEFECT`, `n/a`, plus free-text like `PASS (weak)`, `PASS (human)`,
`PASS (scoped)` and the deliberate version-sibling failures which are FAILs that must never be filed.

Stage 10 had to hand-author a classifier to collapse this into something joinable. That is a signal the
vocabulary is doing too many jobs at once: it mixes *outcome*, *confidence*, *who judged it*, and
*whether it is actionable*.

> **Proposed change:** split into three orthogonal fields — `verdict` (PASS / FAIL / BLOCKED / PARTIAL /
> NOT RUN), `actionable` (yes / no — "no" covers expected version-sibling failures and spec defects), and
> `judged by` (stage 6 / 7 / 8 / human / adjudication). `status-vocabulary.md` already exists; it should
> own this split.

### F7 — version-sibling pairs need a both-failed detector (severity: medium)

Contested requirements are written as A/B siblings where exactly one is expected to fail. When **both**
fail, the build matches neither documented reading, which is a real defect — that is exactly how EP-55937
was found, and by accident.

> **Proposed change:** stage 10 should assert this mechanically. For every sibling pair, if both siblings
> are FAIL, raise it. If one is FAIL and the other is BLOCKED, flag it as *unconfirmed which version is
> built* — which is the state REQ-14 is in right now and nobody would have noticed without looking.

### F8 — stage 10's own workload is unbounded (severity: low)

Writing back 71 suite cases took four parallel subagents. Fine here, but the skill gives no guidance on
batching, and a 500-case suite would be unpleasant.

> **Proposed change:** document the batching pattern in `qa-manual-results/SKILL.md`, and note that the
> write-back must be **verified by re-reading the suite**, not trusted from the tool's success responses.
> One subagent in this run reported a count that did not match its manifest; the re-read caught it.

---

## 4. Errors made by this session, for symmetry

The stage-10 session made four, and they are the same species as the machine's:

1. Rejected the previous session's `q` vs `query` parameter theory. The theory was right. My reasoning was
   bad — I argued that two hosts treating `query` differently made the theory unsupportable, which does
   not follow. Retracted in EP-55860 comment 143292.
2. Recorded TC-REQ-38.2 as blocked by EP-55925 by over-generalising that defect to a case it does not
   touch. Corrected to PASS.
3. Declared the buyers family unverifiable without asking whether another environment existed. It did.
4. Gave the human an unfalsifiable instruction ("find a bucket above 10" when the counter caps at 10),
   which nearly produced a false bug report.

Two of the four were caught by the human, not by me. Which is the same failure mode as F1: confident
generalisation from one observation.

---

## 5. The one-line conclusion

**The machine stages are a good defect-suggestion engine and a poor verdict engine.** The architecture
already assumes this — that is what provisional-until-stage-10 means — and it should lean into it harder.
Concretely: no stage upstream of 10 should be permitted to publish a FAIL from a single observation.

Ranked by value per unit of effort, the changes worth making are **F1** (second observation before any
FAIL), **F5** (environment capability probe), then **F3** and **F4**.

---

## 6. Forward-looking proposals (owner's asks, 2026-08-05)

Two changes requested by the plugin owner after this run, specified in full in
the companion file `ep-qa-pipeline-proposed-edits.md`:

**A. Emit the manual sheet BEFORE the machine stages, not after.** Motivated as a
parallelism win, but the stronger argument is evidential: today the human sees
`FAIL CONFIRMED` before touching the page, so their observation is not
independent. Given the 54% UI accuracy measured in §1, the machine's verdicts are
worth less as a filter than an unprimed human walk is worth as evidence. Splits
the runsheet skill into walk-sheet mode (stage 5.5) and reconciliation mode
(stage 9). This also subsumes F5, since the walk sheet needs the environment
matrix and fixtures up front.

**B. Progress reporting.** Heartbeat every 10 items or 5 minutes, a rewritten
`<STORY>-progress.md`, and a live task list where the host supports one. Includes
a `Blocked on you` line, which is the single most useful thing for a user
returning to an idle session. Ready-to-drop reference file supplied as
`progress-protocol.md`.

Plus eight cosmetic items (C1-C8), of which **C5** — a confidence field on machine
verdicts — is the one that matters. At 54% accuracy, "observed once" and
"reproduced three times across two sessions" must not render identically on the
page. C5 makes F1 self-enforcing: a stage that can only write `observed once`
cannot publish a FAIL.
