# Status vocabulary — the single home

Every status any verdict stage may emit, in one place. The stage
SKILL.md files, the output templates, the analyzer, and
`scripts/reconcile_counts.py` all defer to THIS file: when a status is
added or changed, it lands here first, then in the emitting stage's
Classification section, the template example rows, and the script's
`STATUSES` tuple + self-test. A status that exists in only some of
those places is a defect (it becomes invisible to counting or
unrepresentable in reports).

Legend for "Emitted by": CR = code-review (stage 6), API = api-testing
(stage 7), WEB = web-testing (stage 8), MR = qa-manual-results
(stage 10, ingesting human results).

| Status | Emitted by | Meaning | Evidence required |
|---|---|---|---|
| `PASS` | CR, API, WEB | Expected result confirmed. CR: only when fully determined by the code TEXT — runtime observables are QA. API/WEB: subject to the absence-check protocol on instrumented surfaces. | CR: file+behaviour. API: endpoint + observed value. WEB: steps executed. |
| `FAIL` | CR, API, WEB | Concrete expected-vs-actual discrepancy, for a case that arrived as QA. | Always: where, expected, actual. CR adds file+line; WEB adds a `web-evidence.md §n` reading (URL, quoted DOM/text, console lines) and a screenshot where the backend can write one (`playwright-executor.md` → Evidence). |
| `FAIL CONFIRMED` | API, WEB, MR | A code-review FAIL confirmed at runtime (or by the human). Never plain PASS/FAIL for arrived-as-FAIL cases. | The CR finding + what was observed. |
| `FAIL REJECTED` | API, WEB | A code-review FAIL that runtime disproves — compensated elsewhere or CR was wrong. Counted as a pass in human summaries. | The CR finding + the correct observed behaviour. |
| `QA` | CR only | Cannot be verified against code text; needs runtime. INPUT status for stages 7/8 — never an output of theirs. | — |
| `N/A` | CR | The case does not apply to this PR (code absent from it). | Reason in Findings. |
| `RE-ROUTE [UI]` | CR | Channel tag is wrong: the assertion originates in client-side code. Web-testing takes the case regardless of tag. Replaces QA for that case. | File+line of the client-side behaviour. |
| `SPEC-DEFECT` | CR, API, WEB | The CASE (premise or expected result) is wrong, not the code. Feeds "Requirements to correct" + a `discrepancy` suite note. | What the case says vs what the spec/behaviour is. |
| `PARTIAL` | API, WEB | Some steps/surfaces pass, others do not (or are unreachable — e.g. an "anywhere" claim with unenumerated roles). | Which passed, which did not/could not. |
| `BLOCKED` | API, WEB | Tried and could not execute: missing auth/host/data, unreachable precondition. Not a FAIL. | The reason + a recorded `Probe:` (verbatim call/check + response) proving the blocker is real. |
| `BLOCKED (unverified)` | API, WEB | BLOCKED with NO probe recorded. A distinct statistics row; the analyzer flags 🔴 if it survives to the final verdict — wrong blockers keep being accepted (9 across two runs dissolved on one probe each). | The unprobed reason + what would verify it. |
| `NOT EXECUTED` | API, WEB | In scope but not attempted, for a stated environmental reason (no such event/endpoint/host). Distinct from BLOCKED (which means tried). Counts toward `Completeness: partial`. | The environmental reason. |
| `NOT-TESTABLE` | API | The case cannot be validated as written — endpoint mapping wrong/ambiguous. | The correct endpoint + what it actually does. |
| `NOT-TESTABLE (instrumentation)` | API | This stage's instrument cannot measure the claim (instrumented surface + API-created precondition, or absence check with no positive control). Always also listed under "Route to web-testing". | Why the instrument cannot measure it (protocol reference). |
| `OBSERVATION` | WEB | Case passed, but an out-of-scope anomaly was noticed. Never a substitute for FAIL. | What was seen. |
| `OBSERVATION (no source checked)` | CR, API, WEB | A real thing seen or measured, with NO clause in any source of record saying it is wrong. Honest output and often worth fixing — but never a FAIL, never a bug candidate, never listed among defects, and phrased as a question not a verdict. Converts to a defect only by finding the clause, or to a product question by being raised with the docs-phase owner. | What was seen + which sources were checked and came back empty. |
| `SKIPPED` | MR (human) | Human chose not to run the row. | — |

Arrival markers (the "Arrived as" column — "Source" before 0.38; not
statuses, never counted as verdicts; a finding's `Source:` line is the
register row, a different thing):
- `PASS(code)` — api-testing's marker for deliberately executed
  code-review-PASS cases. The script tallies it separately.
- `code-review risk <n>` — arrival marker of a `RISK-CR-<n>` risk-chasing row.

Row identifiers: `TC-REQ-N.M` (regular cases), `TC-N` (bug-fix mode and
standalone-Bug runs, which derive flat-numbered cases because they have
no requirements file to group them under) and `RISK-<TAG>-<n>` (risk
rows — legal, reported by the script as "ids NOT in test-cases").

**A status cell carries a status and nothing else.** The vocabulary
above is the whole legal set, plus the parenthesised qualifiers named in
it; `reconcile_counts.py` reads the last cell that matches it exactly.
A decorated cell — `QA → stage 7`, `PASS (not reachable)`,
`NOT EXECUTED HERE — orchestrator` — parses as NO status, so the row
silently leaves the counts and the count gate under-reports without
saying why. Put the routing, the qualifier and the reasoning in the
Comment column, and record a case another stage owns the way the routing
invariant prescribes: a "Not executed here" / "Route to web-testing"
section row, or an explicit reference to the report that executed it —
never an invented status token.

## Routing invariant — one rule, four recorded forms

The docs-phase channel tag (`[UI]` / `[API]` / `[mobile]` /
`[export/email]`, including the dual `[API][UI]`) is **advisory**: it
was assigned before any stage saw the code or the running system. The
binding rule is:

> **Web-testing's scope = every QA/FAIL case that no earlier stage
> conclusively executed at runtime, plus every routed-in and
> spot-check row.** And every QA/FAIL case of ANY channel appears
> exactly once across the run: in api-testing's Results, in
> web-testing's Results, in a "Not executed here" section with its tag
> and reason, or via an explicit reference to the report that executed
> it. `[mobile]` / `[export/email]` cases land in "Not executed here"
> unless api-testing's HTTP-fetchable-export exception applies.

The four recorded forms of this one rule — keep the names; they are
what the templates and `reconcile_counts.py` parse:
- the **per-case channel tag** (qa-checklist / qa-test-cases) — the
  initial routing hint;
- the **dual `[API][UI]` tag** — provenance-sensitive cases: the call
  is API-shaped but the verdict needs the browser (absence-check
  protocol); api-testing may run the API half, never the final PASS;
- **code-review `RE-ROUTE [UI]`** — the first stage that sees the code
  overrides a wrong tag, with file+line evidence;
- **api-testing's "Route to web-testing" section** — instrumentation
  the API cannot measure (`NOT-TESTABLE (instrumentation)`).

A routed case that appears in none of web-testing's sections is a
coverage hole, not a pass (analyzer: routing integrity).

Cross-stage rules that live with the vocabulary:
- Prefer BLOCKED / NOT-TESTABLE / QA over a doubtful PASS — a false
  pass is worse than a failure because nobody investigates it.
- A case that arrived as FAIL from code review exits stages 7/8 only
  as FAIL CONFIRMED or FAIL REJECTED.
- **If you write the doubt, you must classify it.** When a stage's own
  finding says the case's WORDING is what makes it fail ("depends on
  the reading", "the spec doesn't state a limit", "would pass under
  the other interpretation"), that IS the SPEC-DEFECT definition:
  record SPEC-DEFECT, not FAIL. A verdict that needs a caveat to
  survive is the caveat's verdict.
- **No defect without a clause.** Every FAIL, FAIL CONFIRMED and
  `RISK-CR-*` row carries `Source:` (the register row) and `Clause:`
  (the verbatim sentence the build contradicts). The **as-built**
  document counts as a source alongside the brief, and it is the one
  that settles "is this deliberate?" — a behaviour it records as
  intended is not a defect however wrong it looks. No clause anywhere →
  `OBSERVATION (no source checked)`. Register and precedence:
  `../../qa-pipeline/references/sources-of-record.md`.
- **Presentation carries the label.** A status is part of the finding,
  not decoration on it. An unsourced observation listed alongside
  verified failures — in a report, a summary, or a chat message — has
  been silently promoted to a defect, which is the failure the status
  exists to prevent.
- Manual results (stage 10) use PASS / FAIL / BLOCKED / SKIPPED; any
  other human entry is recorded verbatim as a non-standard verdict,
  never coerced.
- **The QA Service run is the per-case record.** Every status above maps
  to a run verdict (`pass | fail | blocked | known_defect | skipped`) by
  exactly one table — `../../qa-pipeline/references/test-runs.md` →
  "Verdict mapping", the single home; a status added here gets its row
  there in the same change. The parts that are easy to get wrong: a
  machine `fail` files a Jira defect at record time, so FAIL / PARTIAL
  rows stay `not_run` until the human round; SPEC-DEFECT is `skipped`,
  never `known_defect`; a human result is `source: manual` with the
  tester as principal.
