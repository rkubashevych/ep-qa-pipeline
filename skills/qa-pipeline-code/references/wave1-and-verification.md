# Wave 1 and the post-publish verification (qa-pipeline-code steps 6 and 9)

**Contents:** Why two waves · Why no archive comments · The post-publish
verification list

The SKILL.md keeps the procedure (count gate → publication gate →
REQUIRED PAUSE → create run → record → draft summary → status line).
This file holds the reasoning behind it and the full verification list
that closes every run. Moved here verbatim in 0.41.0.

## Why two waves — and why "provisional" labels do not work

**Wave 2 — after `qa-manual-results` (stage 10), never now.** The
human summary, the story comment, the stage-verdict table, and any
request for a product decision — by then every verdict is
human-confirmed or retracted. (Real-run rationale: a PROVISIONAL
label prevented nothing — a mis-typed bug, three already-answered
"product decisions", two retractions in 24h. Marking output
tentative does not make readers treat it tentatively; withholding
it does.)

The exception, and it is narrow: a finding may publish in wave 1 only if
ALL of: confirmed at RUNTIME (not a code read); evidence attached; and it
blocks the manual round from proceeding. A code-read FAIL never qualifies.

## Why no archive comments

**No archive comments — retired in 0.33.0.** Until then wave 1 also
pasted every stage report into fenced blocks on the QA sub-task
("Comment 1 — machine archive"). Why it is gone: the run is the
per-case record (0.30.0), the run folder is the reports' home
(0.32.0), and the dumps ran to three to five unreadable comments
per pass — on EP-56380 three of them landed on a Defect's face,
which is what produced the 0.26.0 target rule. A fenced file dump
on ANY ticket is now a ❌ in the post-publish check. One ticket's
run never writes into another ticket's thread; **the one sanctioned
cross-ticket comment is a retraction** (stage 10, `test-runs.md` →
"Retraction target rule"): ≤ 6 lines correcting a verdict, posted
where that verdict was published.

The reports are local-only, and step 0 guards it: a resume rebuilds from
`runs/<STORY>/r<N>/`; on a different machine step 0 pauses rather than
silently re-running or proceeding empty (`run-modes.md` → Resume). The
verdicts themselves are always recoverable from the run.

## Post-publish verification — always the last action of the run

**Post-publish verification — always the last action of the run.**
The analyzer ran at step 5, BEFORE steps 6–9 — nothing it certified
covers what they actually did. Verify the final state now:
- **Write-back landed:** connector present → `get_test_run` on the
  run step 6 created: roster count == the step-0 scope count, and
  the `progress` partition matches the stage reports under the
  `test-runs.md` mapping (`pass` = PASS + FAIL REJECTED, `blocked`,
  `skipped` = NOT EXECUTED + NOT-TESTABLE + SPEC-DEFECT,
  `known_defect` = keyed FAIL CONFIRMED, `not_run` = the FAIL /
  PARTIAL rows the human will walk). Then
  `executed_coverage(suiteId)`: `neverExecuted` fell by the recorded
  count. A mismatch is a count-gate ❌ — fix it now. Connector absent
  → state that no durable per-case record exists beyond the Jira
  comments.
- **Findings traceable:** every FAIL / FAIL CONFIRMED across the
  three reports has a walk-plan card awaiting the tester (and a
  `not_run` roster row), a narrow-exception bug key, or an explicit
  "not carried — <reason>" line in the drafted human summary. No
  silent FAILs. Every 🔴/🟡 the analyzer left unsettled has a row in
  `<STORY>-open-items.md` (`open-items-ledger.md`).
- **Wave-1 comment exists, on the right ticket, and nothing else
  does:** exactly one status comment (QA sub-task when there is one,
  else the ticket under test) — re-read, don't assume. A fenced file
  dump found on ANY ticket is a ❌ (archives retired 0.33.0). The
  human summary must NOT be posted yet — finding it posted early is
  a ❌.
- **Reports are on disk:** every stage report the run produced is
  present in the run folder. They are the ONLY copy of the evidence
  — a missing one is a ❌, not a formality.
- **Walk-plan outputs exist** — `<STORY>-walk-plan.md` and
  `-testdata.json` (unless stage 9 was skipped), and every card in
  the plan passed stage 9's voice check (no HTTP verb, curl line or
  caveat in a card body outside an AGENT-RUNS `run:` key).
- **Everything is in the run folder:** every file this pass wrote is
  under `runs/<STORY>/r<N>/` (ledger one level up), and **no
  `<STORY>-*` file was written to the repo root**. One in the root is
  a ❌ — move it and say so.
Append the outcome as `## Post-publish verification` (✅/❌ per
item) to `<STORY>-run-report.md` and include one line in the final
response. A ❌ here is a real finding — fix it or tell the user,
never bury it.
