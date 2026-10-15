# QA Service sync — the run checks and the suite-structure checks

Part of § 4 "QA Service sync" in `../SKILL.md`, read when the suite
exists.

## The run (code phase)

**Post-run:** in the orchestrated code flow the analyzer runs before
step 6 records the run, so the orchestrator's own post-publish
verification does these checks there
(`../../qa-pipeline/references/test-runs.md` → "Verification"). Run
them here on an on-demand analysis or a later round's analysis.

`list_test_runs` on the suite, find this pass's run by title
(`../../qa-pipeline/references/test-runs.md`).

- 🔴 **no run** — verdicts exist in stage reports and none reached
  the system of record; every "still stands" statement in this
  ticket's history is about markdown files (EP-53978: five passes,
  `verified: 0`).
- 🔴 **partition mismatch** — `get_test_run` `progress` does not
  match the stage statistics under the mapping table (`pass` = PASS +
  FAIL REJECTED **minus the rows the evidence audit held back**,
  `blocked`, `skipped` = NOT EXECUTED + NOT-TESTABLE + SPEC-DEFECT,
  `known_defect` = keyed FAIL CONFIRMED the audit rated SUFFICIENT,
  `not_run` = the FAIL / PARTIAL rows awaiting the human **+ the
  held-back rows + any `BLOCKED (quota)` rows**), or roster count ≠
  scope. A held-back or quota row showing as `not_run` is correct,
  not a mismatch — never "fix" it by recording it (the same list as
  `../../qa-pipeline-code/references/wave1-and-verification.md` →
  "Post-publish verification"; read `<KEY>-evidence-audit.md` for the
  held-back rows before comparing).
- 🔴 **machine `fail` outside the narrow exception** — a `fail`
  recorded with `source: machine` whose case is not runtime-confirmed
  + evidenced + rated SUFFICIENT + blocking: it filed a Jira defect
  before the human round (`run_defects` shows the key).
- 🟡 **SPEC-DEFECT as `known_defect`**, or a human-executed row with
  `source: machine`, or a machine verdict with a person as principal
  — the two mapping errors the 2026-09-02 off-book run made.
- 🟡 **stale run** — status `running` (`stale: true`) with
  `not_run` rows and no `<KEY>-manual-results.md`: the manual round
  was never ingested; the ticket's verdicts are still provisional.
  Same finding as §5's "manual results never ingested", seen from the
  service side — report it once, under §5. `completed` and `closed`
  are both "done" only together with a `-manual-results.md`
  (`-walk-results.md` alone = ingestion pending; `test-runs.md` → "Run
  lifecycle"): a `completed`
  run after stage 10 is correct, not a missed close; a `completed` run
  with a walk plan and no results file is a clean machine pass whose
  human round is still open — say so, never "written back".
- 🟡 **[Environment] no release for the fixVersion** — the ticket
  carries a `fixVersion` and `list_releases` has no release for it, so
  the run was created without `releaseId` and its verdicts cannot be
  scoped by release. Name the fixVersion; the fix is upstream (a
  release owner creates it), not in the pipeline.
- 🟡 **evidence links missing** — a `fail` / `blocked` /
  `known_defect` row whose note names a Jira key or comment while its
  `evidence[]` is empty (`test-runs.md` → evidence).
- `executed_coverage(suiteId[, releaseId])` is reported in the
  findings summary as two numbers — machine and manual — never one
  percentage.

## Suite structure

Whenever the suite exists — including the code phase's analyzer run,
which comes after the docs publish.

- 🔴 **zeroed status buckets** — every case-status bucket reads 0
  against a non-zero total: the cases were written with a `status`
  outside `planned/implemented/partial/deferred/na` (e.g. `draft`).
  Fixable with a re-`edit_test_case` pass, not a re-publish.
- 🔴 **collapsed requirement kinds** — 0 rules AND 0 invariants AND 0
  risks among the suite's requirements: everything was filed as `fr`.
  Fixable in place with `edit_requirement` (`kind` + corrected
  `stableId`, which rewrites references).
- 🔴 **zeroed level table** — `stats.byLevel` sums to 0 against a
  non-zero case total: the cases were written without the `levels` code
  array (`AE`/`E2E`/`M`/`U`/`I`/`C`…). Those cases are also invisible to
  the implement workflow. Fixable with a re-`edit_test_case` pass.
- 🟡 **empty trace graph** — `traceLinks` is `[]` while cases carry
  `traceability`: the links never materialized; re-sending
  `traceability` on a case rebuilds the suite's edges.
- 🔴 **no owner / no ticket** — `teams: []` ("No team" in the web UI)
  or `jiraKeys` without `<KEY>`, on a suite created OR appended to
  (EP-55889). Give the call: `edit_suite {suiteId, teams,
  jiraKeys: [<existing…>, "<KEY>"]}`.
- 🟡 **bare suite header** — no `summary` / `owner` / `status` /
  `lastReviewed`. Fixable with `edit_suite`.
- 🟡 **foreign prefix** — this ticket's stableIds not starting with the
  suite's `prefix` (EP-55889: `MEETING-EXPORT-*` in `MEXP`); fix with
  `edit_requirement` / `edit_test_case` `stableId`.
