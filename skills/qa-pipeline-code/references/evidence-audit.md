# Evidence audit — the tester does not grade its own proof

Step 5 of `qa-pipeline-code`, between web-testing (stage 8) and the
analyzer. It is a separate, read-only pass that decides whether the
evidence stages 7–8 left behind is enough to believe their verdicts.

**Why (0.47.0).** Until this step, the agent that ran a case was also
the only one that ever looked at its proof. The web-testing template
said "PASS needs no explanation", and no evidence was captured for a
PASS at all. So a PASS taken on an expired session could be recorded
and then carried into the walk plan as "machine already checked this":
- the screenshot, had there been one, would have shown the login page;
- or the badge on a different exhibitor than the case named.

The analyzer checks that a FAIL has `Source:` + `Clause:`; it never
opened a PASS's proof. "~half of unverified machine PASSes are
historically wrong" is already the runsheet's premise (VERIFY cards).
This step makes that judgement per case, from the artifacts, before
anything is recorded.

**Source.** Borrowed from qa-service's `uat-evidence-auditor` agent
spec (`.claude/agents/uat-evidence-auditor.md`). qa-service ships that
spec and never runs it: its worker relabels the UAT agent's own verdict
as the audit (`worker-stub/server.mjs`). **Here it runs, as its own
subagent, every code-phase pass that has runtime verdicts.**

## How it is dispatched

- **A fresh subagent** (the Agent / Task tool), given this file's
  "Brief" section verbatim plus the file paths below, and nothing from
  the testing conversation. Independence is the point. An auditor that
  saw the stage run inherits its conclusions.
- **Inputs (paths only):**
  - `<KEY>-api-testing.md`, `<KEY>-api-evidence.md`;
  - `<KEY>-web-testing.md`, `<KEY>-web-evidence.md`;
  - the screenshots under `$EP_QA_HOME/evidence/<KEY>-r<N>-*`;
  - `<KEY>-test-cases.md` (the claims' expected results);
  - `<KEY>-sources.md`;
  - `$EP_QA_HOME/.env.qa-agents`, only for the GET re-checks.
- **Output:** `r<N>/<KEY>-evidence-audit.md`, plus a ≤ 10-line return:
  counts, the downgraded case ids, and blockers.
- **No subagent available:** run it inline after stage 8. Write
  `Independent: no — inline` in the header. The analyzer raises that as
  a 🟡. Still better than no audit; worse than a fresh reader.
- **Skip it** only when stages 7–8 produced no runtime verdict (a
  code-review-only pass). Say so on the run report's step line.

## Brief (hand this to the subagent verbatim)

You are the **evidence auditor** for one QA pipeline pass. You judge
whether the evidence on disk is enough to believe each runtime verdict.
You do **not** judge whether the feature works.

**Hard constraints — read-only.**
- The only file you write is `<KEY>-evidence-audit.md`. Never edit a
  stage report, the test cases, or any evidence file.
- Never change system state:
  - no browser;
  - no POST, PUT, PATCH or DELETE;
  - no QA Service or Jira writes.

  The only network action allowed is re-issuing a **GET** that a report
  cites, to a host in `ALLOWED_HOSTS`, with credentials loaded by
  `<plugin>/skills/api-testing/scripts/load-env.sh`. Never print a
  token. A GET that needs a login step first (exhibitor or visitor
  tokens, the legacy admin panel) is **not** re-issued: the login is a
  POST. Rate that row from its `api-evidence §n`. No shell at all
  (Cowork) → no re-issues; rate every API row from its section and say
  `Re-checks: none — no shell` in the header.
- Never capture new evidence or backfill a gap. You report gaps; the
  manual round closes them.

**What to audit — every row, none skipped:**
- every `PASS`, `FAIL`, `FAIL CONFIRMED`, `FAIL REJECTED` and `PARTIAL`
  row in the Results of `-api-testing.md` and `-web-testing.md`;
- every structural-check `PASS` / `FAIL` line in `-web-testing.md`.

Rows you do **not** audit:
- `BLOCKED`, `NOT EXECUTED`, `NOT-TESTABLE`, `SPEC-DEFECT`: the analyzer
  owns their probes;
- code-review `PASS(code)`: stage 9's VERIFY cards own those.

Coverage is mandatory. End the table with `Rows audited: N of N`.

**Per row, exactly one verdict:**

| Verdict | When |
|---|---|
| **SUFFICIENT** | A primary artifact you checked yourself shows the claim. Any one of: <br>• a `web-evidence §n` reading whose URL, signed-in role, entity and quoted text match the case's expected result; <br>• a screenshot you opened that depicts it; <br>• an `api-evidence §n` request/response excerpt (method, path, role, status, the deciding `.data` value) that shows the expected value; <br>• a cited GET you re-issued that returns it now. <br>An absence claim also needs its `Control:` line (`../../api-testing/references/absence-check-protocol.md`). |
| **INSUFFICIENT** | The artifact exists but does not show the claim: <br>• the login page, an error page or toast, a blank or cropped image (note the byte size; under 5 KB is suspect); <br>• a different entity, role or event than the case names; <br>• a value other than the expected one; <br>• a timestamp outside this pass; <br>• a reading that is a paraphrase of the expectation rather than a quote of the page. <br>Also INSUFFICIENT: resting on inference ("should", "presumably", "the code does X"), or an absence verdict with no control. |
| **UNVERIFIABLE** | There is no artifact for the row (no `§n`, no screenshot, no endpoint + observed value), or the artifact is unreadable. Also a GET that now differs where the run's own "Writes performed" cannot explain the difference. |

**GET re-checks.**
- Re-issue the GETs behind PASS rows whose claim is about state.
- A value that differs now is not automatically a contradiction. A
  write the run made and reverted (the api-testing "Writes performed"
  table) explains a difference; say so and keep your verdict.
- A difference nothing explains → UNVERIFIABLE, with both values.

**Also produce:**
- **Contradiction ledger:**
  - the same surface or reading used as conclusive evidence in one row
    and dismissed in another;
  - a report that corrected itself but left the stale statement
    standing in its prose.
- **Orphans and missing:**
  - orphans: evidence files on disk that no row cites;
  - missing: files a row cites that are not on disk. A missing file is
    automatically UNVERIFIABLE for its row.
- **Remediation:** for each INSUFFICIENT / UNVERIFIABLE row, the one
  artifact that would settle it, in words a tester can act on ("open
  the exhibitor list as the visitor account and look for the Featured
  badge on exhibitor 'Acme'"). It becomes the walk card's backstage
  `why:` line.

Be a hard grader. A plausible story is not evidence. A feature can work
perfectly and still be insufficiently evidenced; say exactly that when
it is true.

## The audit file

```markdown
# <KEY> - Evidence audit

Skill: qa-pipeline-code <version> · sha <7>
Audited: <KEY>-api-testing.md · <KEY>-web-testing.md (+ evidence files)
Independent: yes — fresh subagent | no — inline
Bar: strict (every row needs a primary artifact the auditor checked)
Re-checks: <N GETs re-issued | none — no shell | none — every GET needed a login>
Date: <YYYY-MM-DD>

Counts: <S> sufficient · <I> insufficient · <U> unverifiable · rows audited <N> of <N>

## Per-row verdicts

| TC | Stage | Claimed | Evidence cited | Checked | Re-check | AUDIT | Reason |
|----|-------|---------|----------------|---------|----------|-------|--------|
| TC-REQ-3.1 | web | PASS | web-evidence §4 + evidence/EP-1-r1-TC-REQ-3.1-pass.png | png 212 KB, shows login page | — | INSUFFICIENT | screenshot is the sign-in page, not the exhibitor list |
| TC-REQ-2.2 | api | PASS | GET /api/v1/exhibitorCategories/get → logo.enabled=true | row + re-issued GET | same | SUFFICIENT | — |

## Contradiction ledger
- <none | row A vs row B — what conflicts>

## Orphans and missing
- Orphans: <files>
- Missing: <files> → UNVERIFIABLE on <rows>

## Remediation
- TC-REQ-3.1 — <the one artifact that settles it>
```

## What the orchestrator does with it

The audit changes what is **recorded**. It never edits a stage report.
The audit file supersedes the reports for the rows it downgrades,
exactly as `-manual-results.md` supersedes them for human verdicts.

| Claimed | Audit | Recorded in wave 1 (`../../qa-pipeline/references/test-runs.md`) | Stage 9 |
|---|---|---|---|
| PASS / FAIL REJECTED / structural PASS | SUFFICIENT | `pass`, per the mapping | settled or VERIFY, as before |
| PASS / FAIL REJECTED / structural PASS | INSUFFICIENT or UNVERIFIABLE | **nothing — stays `not_run`** | **must-walk** (a WALK card in full form, never "settled"); the remediation line is its backstage `why:` |
| FAIL CONFIRMED with an open Jira key (the mapping's `known_defect` row) | SUFFICIENT | `known_defect`, per the mapping | card as before |
| FAIL CONFIRMED with an open Jira key | INSUFFICIENT or UNVERIFIABLE | **nothing — stays `not_run`**: the bug is open, but this pass did not show it again | card; backstage says so |
| FAIL / FAIL CONFIRMED / PARTIAL | SUFFICIENT | `not_run` (unchanged); eligible for the narrow wave-1 exception | card as before |
| FAIL / FAIL CONFIRMED / PARTIAL | INSUFFICIENT or UNVERIFIABLE | `not_run`; **never** the narrow wave-1 exception | card; its backstage says the machine's evidence did not hold |

- The step-6 preview names every downgraded row:
  `Held back by the evidence audit: N rows (TC-…) — not recorded, sent
  to the walk`.
- The run report's findings summary carries the audit counts beside the
  stage counts, so "34 PASS" never reads as 34 settled when 6 of them
  are held back.
