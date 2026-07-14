# <ISSUEKEY> - API Testing

Code review: <path to the code-review file>
Test cases: <path to the test-cases file>
Environment: <ADMIN_BASE_URL> · event <EVENT_ID> · frontend host <FE host, if used>
Notes: <carry forward any warning/unresolved-conflict note from the code-review or test-cases file; omit if none>
Date: <YYYY-MM-DD>

## Scope

[API] test cases executed against the REST API: <N>
- QA (verify against the API): <N>
- FAIL (confirm the bug): <N>

## Not executed here
> [mobile] / [export/email] cases this API skill cannot run. Routed to the right tool / owner. Omit if none.

| TC | Name | Channel | Why not executable here |
|----|------|---------|-------------------------|
| TC-REQ-14.2 | <scenario name> | [mobile] | Mobile app — verify on Android/iOS |
| TC-REQ-33.1 | <scenario name> | [export/email] | XLS/email — verify via export/MailDev |

## Results

| TC | Name | Source | Status | Endpoint | Comment |
|----|------|--------|--------|----------|---------|
| TC-REQ-2.2 | <scenario name> | QA | PASS | GET /api/v1/exhibitorCategories/get | data.settings.logo.enabled = true |
| TC-REQ-24.2 | <scenario name> | QA | FAIL | GET /api/v1/exhibitorSettings/get/{id} | expected logo.enabled=false, got true |
| TC-REQ-32.2 | <scenario name> | QA | PARTIAL | GET /api/v2/exhibitor/get | parent suppressed, child not |
| TC-REQ-22.1 | <scenario name> | QA | NOT-TESTABLE | POST /profile/photoSave | endpoint mapping wrong — see Findings |
| TC-REQ-30.1 | <scenario name> | QA | BLOCKED | — | precondition unreachable |

## Findings
> For every FAIL / FAIL CONFIRMED / FAIL REJECTED / PARTIAL / BLOCKED / NOT-TESTABLE. PASS needs no entry.

### FAIL: TC-REQ-24.2 — <scenario name>
- **Source:** QA
- **Endpoint:** <method + path + auth context>
- **Request:** <params / body — tokens redacted>
- **Expected:** <expected field/value>
- **Actual:** <observed field/value from .data>

### NOT-TESTABLE (endpoint-mapping correction): TC-REQ-22.1 — <scenario name>
- **Source:** QA
- **Ticket mapping:** <endpoint the ticket named>
- **Reality:** <what that endpoint actually does + the correct endpoint>
- **Consequence:** <why the case can't be validated as written; how to fix the test case>

### BLOCKED: TC-REQ-30.1 — <scenario name>
- **Source:** QA
- **Reason:** <missing auth/host/data, unreachable precondition, etc.>

---

Section rules:
- Results — all [API] QA/FAIL cases in the order from the test-cases file.
- Source column: QA or FAIL (from code review).
- Writes performed must note their revert in the finding (or a Teardown line).
- No secrets/tokens anywhere in this file.

## Writes performed (audit)
> Every mutating call + how it was reverted. Omit if the run was read-only.

| Endpoint | Entity | Before | After write | Reverted to |
|----------|--------|--------|-------------|-------------|
| POST /api/v1/exhibitorSettings/set/{id} | exhibitor {id} | logo enabled=true isCustom=false | enabled=false isCustom=true | enabled=true isCustom=false |

## Statistics

| Status | Count |
|--------|-------|
| PASS   | <N>   |
| FAIL   | <N>   |
| FAIL CONFIRMED | <N> |
| FAIL REJECTED  | <N> |
| PARTIAL | <N>  |
| BLOCKED | <N>  |
| NOT-TESTABLE (mapping) | <N> |
| Total  | <N>   |

Verdict: <API testing successful (all PASS / FAIL REJECTED) / unsuccessful — N FAIL, N FAIL CONFIRMED / incomplete — N BLOCKED>
