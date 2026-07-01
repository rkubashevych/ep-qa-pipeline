# <ISSUEKEY> - Code Review

Test cases: <path to the test-cases file>
PR: <URL>
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

## Findings

### FAIL: TC-REQ-1.2 — <scenario name>

- **File:** <path>, line <N>
- **Expected:** <expected result from the test case>
- **Actual:** <what the code does>

### N/A: TC-REQ-2.1 — <scenario name>

- **Reason:** <why it does not apply — what exactly is absent from the PR>

---

Section rules:
- Results — a table of all test cases in the order from the test-cases file.
- Findings — only for FAIL and N/A. PASS and QA need no explanation.
- Every FAIL has a file, a line, and expected/actual.
- Every N/A has a reason why the item does not apply to the PR.
- If there are no FAIL and no N/A — the Findings section is not created.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | <N>   |
| FAIL   | <N>   |
| QA     | <N>   |
| N/A    | <N>   |
| Total  | <N>   |
