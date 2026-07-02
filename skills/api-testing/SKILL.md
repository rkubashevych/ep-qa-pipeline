---
name: api-testing
description: >
  Seventh stage of task processing. Takes the QA / FAIL / not-executed
  [API] test cases from code review and the test cases, executes them
  directly against the ExpoPlatform REST API (curl / HTTP — no browser),
  checks the expected results, and builds a detailed report. Use when
  the user says "api testing", "test the API", "run the API checks",
  "hit the endpoints", or after code review / alongside web testing.
  Covers admin REST, legacy admin-panel, and exhibitor/visitor-token
  (frontend) cases. Credentials come from .env — never hardcoded.
---

# API Testing

Executes the `[API]` test cases against the running REST API, so the
`[API]` items that web-testing cannot run (it only does `[UI]`) are
actually verified instead of being dropped into "Not executed here".
The input is the code-review and test-cases files; the output is a
detailed report with the result of each `[API]` case, keyed by TC-ID.

The full method — auth contexts, token flows, route discovery, the
response envelope, test-data discovery, write-safety, and the frontend /
exhibitor-token cases — lives in **`references/api-testing-reference.md`**.
Read it before running. This SKILL.md is the stage contract; the
reference is the how-to.

## Input

From the user / working directory you need:
1. `<ISSUEKEY>-code-review.md` — the source of which cases to run
   (`[API]` items with status QA / FAIL, and any `[API]` routed to
   "Not executed here" by web-testing). In the same chat it is present
   automatically; in a new chat the user uploads it.
2. `<ISSUEKEY>-test-cases.md` — the steps, test data and expected
   results.
3. **Environment config** — read at runtime from the e2e project `.env`
   (see the reference §0): `ADMIN_BASE_URL`, `ADMIN_USERNAME` /
   `ADMIN_PASSWORD`, `ORGANIZER_API_KEY`, `EVENT_ID`, `BASE_URL` /
   `BASE_PATH`.
4. For any frontend / exhibitor-token case: the **per-event frontend
   host** and an **exhibitor login** (username + password). The frontend
   host is per-event and **not discoverable** via the API/admin/DB — it
   must be supplied (reference §11.1).

Optional: `<ISSUEKEY>-checklist.md` for `[API]` structural checks that
did not become test cases.

If the code-review file or the test-cases file is missing — ask before
starting. If `.env` (or the required variables) is missing — **pause and
ask** for the values; do not guess and do not proceed unauthenticated.
If a frontend case needs a host/exhibitor login that was not supplied —
pause and ask (reference §11.1).

Data sources for this skill:
- the code-review file — which cases to run
- the test-cases file — steps / data / expected results
- the running REST API via curl / HTTP — the source of actual results
- `references/api-testing-reference.md` — the method
- `.env` — credentials (read at runtime, never printed)

All input files are read-only. Do not go to the browser (that is
web-testing) and do not inspect code (that is code-review).

## Rules

- All communication and the entire content of the output file are in English.
- Keep chat messages short.
- **Secrets:** read every credential from `.env` at runtime. Never
  hardcode, never echo a token/password/API key into chat, the report,
  or a file. Redact tokens in any pasted response.
- **Scope:** run only `[API]` test cases (and `[API]`-verifiable
  frontend-restriction cases). Leave `[mobile]` / `[export/email]` in a
  "Not executed here" section. Do not run `[UI]` cases — those are
  web-testing's.
  - Exception: an `[export/email]` case whose artifact is fetchable
    over HTTP (an XLS/CSV export endpoint) MAY be executed here —
    download the file with the right auth context and verify its
    contents (unzip/parse, check the expected columns/values). Report
    it under a clearly-labelled "[export/email] executed via API"
    group so the run-analyzer's reconciliation is not confused. Email
    sends and external integration pushes stay in "Not executed here".
- **Read-only by default.** Only perform a write (`saveSettings`, `set`,
  `photoSave`/`profileSave`, create/delete) when a test case's steps
  require it. Every write must snapshot-and-revert or use a throwaway
  entity (reference §9, §12) — never leave orphaned state on a shared env.
- Take test data (ids, values) from the test case's `[data: ...]`
  annotations (older files may use a "Test data" column);
  when a ticket's ids are from another environment, resolve the real
  ids on the target event (reference §7). Do not invent data.
- **Verify the endpoint actually does what the ticket claims** before
  logging a result. A ticket's endpoint mapping can be *wrong*, not just
  shorthand (reference §11.3 — the `photoSave` lesson). If the mapped
  endpoint does not exercise the behaviour, mark the case QA with a note,
  not FAIL, and record the correct endpoint.
- After saving the file — stop. Do not continue into later skills.

## Workflow

### Step 1 — Collect the scope
Read `<ISSUEKEY>-code-review.md`. Copy any "Notes" line forward. Collect
every test case that is `[API]` and has status QA or FAIL, plus any
`[API]` case web-testing listed under "Not executed here". Read the full
data for each from `<ISSUEKEY>-test-cases.md` (precondition, steps,
expected result, test data). For FAIL items, also pull the code-review
finding.

Split anything non-`[API]` (`[mobile]`, `[export/email]`) into the
report's "Not executed here" section. If there are no `[API]` items —
tell the user there is nothing to run and stop.

Notify briefly:
```
API scope: [N] cases.  QA: [N] · FAIL (confirm): [N].
Env: <ADMIN_BASE_URL> event <EVENT_ID>. Starting.
```

### Step 2 — Load config & authenticate
Read `.env` (reference §0). Confirm `ADMIN_BASE_URL`, `ORGANIZER_API_KEY`
and `EVENT_ID` match the target environment — if they point at a
different alpha, pause and confirm. Get an admin token (reference §2);
get an admin-panel session only if a `/admin/...` case needs it (§3);
get an exhibitor token only for frontend cases (§4 / §11.2), which also
need the supplied per-event frontend host.

### Step 3 — Resolve the real routes & test data
For each distinct endpoint, confirm the real `/api/v1|v2/...` path by
probing and reading the error message (reference §6). Resolve real
category / exhibitor ids on the target event (§7). Group cases by
endpoint so each is called once where possible.

### Step 4 — Execute each case
For each `[API]` case, in test-cases order:
1. Check the precondition (data state). If it needs a state that does
   not exist, either set it via a safe, revertible write (§9/§12) or, if
   that is not possible, mark BLOCKED with the reason.
2. Perform the call(s) with the correct auth context and headers
   (reference §1, §2, §11.2). For writes: snapshot first, write, then
   revert in teardown.
3. Read the actual value from the response envelope (`.data`, §5) and
   compare to the expected result.
4. Classify (below). Capture the endpoint + observed field as evidence
   (redact tokens).

### Step 5 — Build the report
Create `<ISSUEKEY>-api-testing.md` per `references/output-template.md`.

## Classification

- `PASS` — the API response matches the expected result.
- `FAIL` — a concrete discrepancy between expected and actual (for a
  case that arrived as QA from code review).
- `FAIL CONFIRMED` / `FAIL REJECTED` — for cases that arrived as FAIL
  from code review: the API confirms (or refutes) the code-review bug.
- `PARTIAL` — some steps/surfaces pass, others do not (record which).
- `BLOCKED` — could not be executed: missing auth/host/data, endpoint
  unreachable, or an unrevertible precondition.
- `QA` — the case cannot be validated as written because the ticket's
  endpoint mapping is wrong or ambiguous; record the correct endpoint
  and what it actually does (reference §11.3).

Rules: prefer BLOCKED/QA over a false PASS; never PASS with doubt; every
FAIL/PARTIAL needs the endpoint + observed vs expected; for code-review
FAIL items use FAIL CONFIRMED / FAIL REJECTED, not plain PASS/FAIL.

## Verification before saving
- Every `[API]` QA/FAIL case from code review appears in the results
  table (order matches the test-cases file).
- Every FAIL / FAIL CONFIRMED / FAIL REJECTED / PARTIAL / BLOCKED / QA
  has evidence (endpoint + observed vs expected, or the reason).
- No secrets/tokens anywhere in the file.
- Every write has a documented revert (or throwaway-entity cleanup).

## Output file
Create `<ISSUEKEY>-api-testing.md` in the working directory. If it
already exists — delete it and create a new one (single latest run, no
append). The template is in `references/output-template.md`.

## Final answer
After saving, report: the path, the PASS / FAIL / FAIL CONFIRMED / FAIL
REJECTED / PARTIAL / BLOCKED / QA counters, the overall verdict, any
confirmed bugs, any endpoint-mapping corrections found, and what was
left for `[mobile]` / `[export/email]`.
