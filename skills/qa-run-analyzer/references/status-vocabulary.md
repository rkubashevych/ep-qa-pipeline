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
| `FAIL` | CR, API, WEB | Concrete expected-vs-actual discrepancy, for a case that arrived as QA. | Always: where, expected, actual. CR adds file+line; WEB adds screenshot. |
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
| `SKIPPED` | MR (human) | Human chose not to run the row. | — |

Source markers (not statuses — never counted as verdicts):
- `PASS(code)` — Source column value in api-testing for deliberately
  executed code-review-PASS cases. The script tallies it separately.
- `code-review risk <n>` — Source of a `RISK-CR-<n>` risk-chasing row.

Row identifiers: `TC-REQ-N.M` (regular cases) and `RISK-<TAG>-<n>`
(risk rows — legal, reported by the script as "ids NOT in test-cases").

Cross-stage rules that live with the vocabulary:
- Prefer BLOCKED / NOT-TESTABLE / QA over a doubtful PASS — a false
  pass is worse than a failure because nobody investigates it.
- A case that arrived as FAIL from code review exits stages 7/8 only
  as FAIL CONFIRMED or FAIL REJECTED.
- Manual results (stage 10) use PASS / FAIL / BLOCKED / SKIPPED; any
  other human entry is recorded verbatim as a non-standard verdict,
  never coerced.
