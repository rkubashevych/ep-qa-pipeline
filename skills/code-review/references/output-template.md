# <ISSUEKEY> - Code Review

Test cases: <path to the test-cases file>
PR: <URL>
Completeness: <complete | partial — N of M cases not reviewed: <reason>>
Notes: <carry forward any warning/unresolved-conflict note from the test-cases file; omit the line if none>

## Results

PR column = which sub-task PR the test case was checked against
(omit the column if there is only one PR).

| TC | Name | PR | Status |
|----|------|----|--------|
| TC-REQ-1.1 | <scenario name> | EP-47975 (BE) | PASS |
| TC-REQ-1.2 | <scenario name> | EP-54610 (FE) | FAIL |
| TC-REQ-1.3 | <scenario name> | EP-54610 (FE) | QA |
| TC-REQ-2.1 | <scenario name> | — | N/A |
| TC-REQ-3.1 | <scenario name> | EP-54610 (FE) | RE-ROUTE [UI] |

## Findings

### FAIL: TC-REQ-1.2 — <scenario name>

- **File:** <path>, line <N>
- **Expected:** <expected result from the test case>
- **Actual:** <what the code does>

### N/A: TC-REQ-2.1 — <scenario name>

- **Reason:** <why it does not apply — what exactly is absent from the PR>

### RE-ROUTE [UI]: TC-REQ-3.1 — <scenario name>

- **Tagged:** [API]
- **File:** <client-side path>, line <N>
- **Why:** <the asserted behaviour is implemented client-side — what the
  API path would miss (e.g. cache clear only on the legacy web edit path)>
- **For web-testing:** <what the browser run must exercise>

---

## Risks
> Hazards seen in the code that NO test case covers — numbered, so
> stages 7/8 can chase them as `RISK-CR-<n>` rows and step 6 can
> propose them as permanent suite cases. Omit if none.

- **RISK-CR-1:** <file+line — what could go wrong, on which surface> — no covering case
- **RISK-CR-2:** <…> — no covering case

---

Section rules:
- Results — a table of all test cases in the order from the test-cases file.
- Findings — only for FAIL, N/A, RE-ROUTE and SPEC-DEFECT. PASS and QA need no explanation.
- Every FAIL has a file, a line, and expected/actual.
- Every N/A has a reason why the item does not apply to the PR.
- Every RE-ROUTE has the overridden tag + the client-side file/line.
- If there are no FAIL, N/A or RE-ROUTE — the Findings section is not created.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | <N>   |
| FAIL   | <N>   |
| QA     | <N>   |
| RE-ROUTE | <N> |
| N/A    | <N>   |
| Total  | <N>   |
