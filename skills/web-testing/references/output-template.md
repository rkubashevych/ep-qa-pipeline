# <ISSUEKEY> - Web Testing

Code review: <path to the code-review file>
Test cases: <path to the test-cases file>
Host: <the base URL / test host actually used>
Notes: <carry forward any warning/unresolved-conflict note from the code-review or test-cases file; omit the line if none>
Date: <YYYY-MM-DD>

## Scope

[UI] test cases executed in the browser: <N>
- QA (verify in the UI): <N>
- FAIL (confirm the bug): <N>

## Not executed here
> [mobile] / [export/email] test cases this browser-based skill cannot
> run — plus [API] cases ONLY if api-testing has not run. When
> `<ISSUEKEY>-api-testing.md` exists, do not list [API] cases here;
> add one line instead: "[API] cases executed by api-testing (stage
> 7), see <ISSUEKEY>-api-testing.md". Omit the section if none.

| TC | Name | Channel | Why not executable here |
|----|------|---------|-------------------------|
| TC-REQ-6.3 | <scenario name> | [mobile] | mobile app — verify on Android/iOS |
| TC-REQ-6.2 | <scenario name> | [API] | api-testing did not run in this flow — verify with API tooling |

## Structural checks (from the checklist)
> `[UI]` presence/type/label checks that have no test case, executed on
> the pages this run visited. Checks on pages not visited are listed as
> "not visited". Omit the section only if the checklist itself was
> unavailable (then explain on the Notes line).

| Check | Description | Status |
|-------|-------------|--------|
| REQ-3.1 | "State" label above the State select | PASS |
| REQ-7.2 | Reset button has type "button" | not visited (settings page) |

## Results

| TC | Name | Source | Status | Comment |
|----|------|--------|--------|---------|
| TC-REQ-1.1 | <scenario name> | QA | PASS | — |
| TC-REQ-1.2 | <scenario name> | QA | FAIL | Step 3: expected "X", actual "Y" |
| TC-REQ-2.1 | <scenario name> | FAIL | FAIL CONFIRMED | UI confirms the bug |
| TC-REQ-2.2 | <scenario name> | FAIL | FAIL REJECTED | UI works correctly |
| TC-REQ-3.1 | <scenario name> | QA | BLOCKED | Element not found |
| TC-REQ-4.1 | <scenario name> | QA | PASS | OBSERVATION: <what was noticed> |

## Findings

### FAIL: TC-REQ-1.2 — <scenario name>

- **Source:** QA
- **Step:** #3 — <step description from the test case>
- **Test data:** <what was entered>
- **Expected:** <expected result from the test case>
- **Actual:** <what the agent saw on the page>

### FAIL CONFIRMED: TC-REQ-2.1 — <scenario name>

- **Source:** FAIL (code review)
- **Code-review finding:** <file, line, problem description from code review>
- **Step:** #<N> — <step description>
- **Expected:** <expected result>
- **Actual:** <what the agent saw — confirms the bug>

### FAIL REJECTED: TC-REQ-2.2 — <scenario name>

- **Source:** FAIL (code review)
- **Code-review finding:** <file, line, problem description from code review>
- **Actual in the UI:** <what the agent saw — works correctly>
- **Conclusion:** <why the bug does not show in the UI>

### BLOCKED: TC-REQ-3.1 — <scenario name>

- **Source:** QA
- **Reason:** <why it could not be executed>
- **Page state:** <what the agent saw at the moment of blocking>

---

Section rules:
- Results — a table of all QA and FAIL test cases in the order from the test-cases file.
- Source column: QA or FAIL — where the test case came from in code review.
- Comment column: for PASS — a dash or OBSERVATION. For FAIL — a short description. For BLOCKED — the reason. For FAIL CONFIRMED/REJECTED — a short description.
- Findings — for FAIL, FAIL CONFIRMED, FAIL REJECTED and BLOCKED.
- PASS needs no explanation.
- FAIL REJECTED also has a finding — so it is clear what exactly was refuted.
- If there are no findings — the section is not created.

## Observations

Additional defects or anomalies noticed while executing
the test cases that are not covered by the requirements:

- <OBS-1>: <what was noticed, where, under what conditions>
- <OBS-2>: <what was noticed, where, under what conditions>

If there are no observations — the section is not created.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | <N>   |
| FAIL   | <N>   |
| FAIL CONFIRMED | <N> |
| FAIL REJECTED  | <N> |
| BLOCKED | <N>  |
| OBSERVATION | <N> |
| Total  | <N>   |

Verdict: <Web testing successful (all PASS and FAIL REJECTED) / Web testing unsuccessful — there are N FAIL, N FAIL CONFIRMED>
