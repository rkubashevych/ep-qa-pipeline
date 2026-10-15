---
name: api-testing
disable-model-invocation: true
description: >
  Stage 7 of the QA pipeline: the [API] cases run against the test
  environment over HTTP (<KEY>-api-testing.md). Usually run by
  qa-pipeline-code.
---

# API Testing

Executes the `[API]` test cases against the running REST API. In the
orchestrated flow this stage runs BEFORE web-testing and owns all
`[API]` items; what it cannot measure it routes onward per the routing
invariant (`../qa-run-analyzer/references/status-vocabulary.md` →
"Routing invariant"). Input: the code-review and test-cases files.
Output: a detailed report keyed by TC-ID.

The full method — auth contexts, token flows, route discovery, the
response envelope, test-data discovery, write-safety, and the frontend /
exhibitor-token cases — lives in **`references/api-testing-reference.md`**.
Read it before running; this SKILL.md is the stage contract. Also read
**`references/absence-check-protocol.md`** — binding on every verdict
this stage records on counters / leads / analytics / statistics /
notifications / dashboards, and on every absence check.

## Input

1. `<ISSUEKEY>-code-review.md` — which cases to run (`[API]` items
   with status QA / FAIL).
2. `<ISSUEKEY>-test-cases.md` — steps, test data, expected results.
3. **Environment config** — read at runtime from
   `$EP_QA_HOME/.env.qa-agents` (resolution and variables:
   `../qa-pipeline/references/environment.md`; `scripts/load-env.sh`),
   including **`ALLOWED_HOSTS`** — the only hosts this stage may call.
4. For any frontend / exhibitor-token case: the **per-event frontend
   host** and an **exhibitor login**. The host is per-event and not
   discoverable by API: take `FRONTEND_HOST` from `.env.qa-agents`
   when it is set for `EVENT_ID`'s event (it must be in
   `ALLOWED_HOSTS`); only when it is empty, or the case is on another
   event, must it be supplied (reference §11.1). The login is test
   data, never a variable (`environment.md` → "No variable for a
   visitor or exhibitor login"): the case's `[data: …]`, else a
   throwaway created under the write-safety rules (§12), else — when
   this run may not write — the case is NOT EXECUTED with that reason.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
— run folder, then the suite; a new chat is no reason to ask.

Missing code-review or test-cases file — ask before starting. Missing
`.env.qa-agents` values — **pause and ask**; never guess, never proceed
unauthenticated. Frontend host for a frontend case: `FRONTEND_HOST`
empty and none supplied — pause and ask (reference §11.1). Exhibitor
login: never a pause — test data, a throwaway, or NOT EXECUTED (input
4 above).

All input files are read-only. Instrument: HTTP only — the browser is
web-testing's, the code is code-review's.

## Rules

- All communication and the entire output file are in English. Keep
  chat messages short.
- **Secrets:** read every credential from `.env.qa-agents` at runtime. Never
  hardcode, never echo a token/password/API key into chat, the report,
  or a file. Redact tokens in any pasted response.
- **Scope:** run only `[API]` test cases (and `[API]`-verifiable
  frontend-restriction cases). A dual-tagged `[API][UI]` case is
  provenance-sensitive (`status-vocabulary.md` → Routing invariant):
  run its API half. A concrete API-side discrepancy is a FAIL (or
  FAIL CONFIRMED) like any other. An API half that behaves is never a
  PASS here — the verdict is web-testing's: the row is `NOT-TESTABLE
  (instrumentation)` with the API reading in its Comment, and the
  case is listed under "Route to web-testing" either way. `[mobile]` / `[export/email]` go to
  "Not executed here"; `[UI]` cases are web-testing's.
  - Exception: an `[export/email]` case whose artifact is fetchable
    over HTTP (an XLS/CSV export endpoint) MAY be executed here —
    download with the right auth context and verify the contents:
    **headers AND values** (`../qa-pipeline/references/export-checks.md`)
    — the header row, the case's named cells (`--expect`) and the
    per-column fill profile, all from `scripts/export_profile.py`, whose
    output goes into the case's evidence. Read each named cell's
    expected value from the entity before exporting. A header-only
    read exits `PARTIAL — structure only`, never PASS; a column empty on
    every row is a finding until the fixture explains it. Report it
    under a clearly-labelled "[export/email] executed via
    API" group so reconciliation is not confused. Email sends and
    external integration pushes stay in "Not executed here".
- **Read-only by default.** Perform a write (`saveSettings`, `set`,
  `photoSave`/`profileSave`, create/delete) only when a case's steps
  require it, and every write snapshots-and-reverts or uses a
  throwaway entity (reference §9, §12) — never leave orphaned state on
  a shared env.
- Test data comes from the case's `[data: ...]` annotations (older
  files: a "Test data" column); when a ticket's ids are from another
  environment, resolve the real ids on the target event (reference
  §7). Do not invent data.
- **Verify the endpoint actually does what the ticket claims** before
  logging a result. A ticket's endpoint mapping can be *wrong*, not
  just shorthand (reference §11.3 — the `photoSave` lesson). If the
  mapped endpoint does not exercise the behaviour, mark NOT-TESTABLE
  with the correct endpoint recorded, not FAIL.
- Escalation: after 3 failed attempts at the same goal (auth, route
  probing, data resolution) with different approaches — stop and
  reassess the failed assumption (wrong env? wrong endpoint mapping?
  missing data?), then ask the user or mark BLOCKED with what was
  tried.
- After saving the file — stop. Do not continue into later skills.

## Workflow

### Step 1 — Collect the scope
Read `<ISSUEKEY>-code-review.md`; copy any "Notes" line forward.
Collect every `[API]` case with status QA or FAIL. (Standalone runs
only: if web-testing already ran and lists `[API]` cases under "Not
executed here", include those too.) Read each case's full data from
`<ISSUEKEY>-test-cases.md`; for FAIL items also pull the code-review
finding. Split anything non-`[API]` into "Not executed here". No
`[API]` items — tell the user and stop.

Two deliberate scope extensions (both produced a real run's two most
important product findings):
- **Code-review-PASS cases** MAY be executed when cheap and adjacent
  to an identified hazard (same endpoint/entity as a case already
  running). Record them with Source `PASS(code)`. Never a gap to skip
  them; never a replacement for the QA/FAIL scope.
- **Risk-chasing rows:** for a code-review risk with NO covering case,
  you MAY add a `RISK-CR-<n>` row (name = the risk, source =
  `code-review risk <n>`) and execute it like a case. A FAIL CONFIRMED
  on a risk row is a confirmed bug, and orchestrator step 6 proposes
  the row as a permanent suite case.

Notify briefly:
```
API scope: [N] cases.  QA: [N] · FAIL (confirm): [N].
Env: <ADMIN_BASE_URL> event <EVENT_ID>. Starting.
```

### Step 2 — Load config & authenticate
Read `.env.qa-agents` (reference §0). Confirm `ADMIN_BASE_URL`,
`ORGANIZER_API_KEY` and `EVENT_ID` match the target environment — if
they point at a different alpha, pause and confirm. **Allow-list
check, before the first request:** every host this run will call
(`ADMIN_BASE_URL`, `BASE_URL`, `FRONTEND_HOST` or the supplied
per-event frontend host) must
match `ALLOWED_HOSTS` (`load-env.sh --host-allowed HOST`; rule in
`../qa-pipeline/references/environment.md`). Not listed, list missing, or a production host →
**PAUSE** naming the host; never add it yourself, never "just read".
Say the checked hosts once in the run's first line. Get an admin token
(§2); an admin-panel session only if a `/admin/...` case needs it
(§3); an exhibitor token only for frontend cases (§4 / §11.2), which
also need the supplied per-event frontend host.

### Step 3 — Resolve the real routes & test data
For each distinct endpoint, confirm the real `/api/v1|v2/...` path by
probing and reading the error message (§6). Resolve real category /
exhibitor ids on the target event (§7). Group cases by endpoint so
each is called once where possible.

### Step 4 — Execute each case
`[risk: High]` first, then Medium, then Low (test-cases order within a
rating and when there are no markers); the report still lists cases in
test-cases order.
1. Check the precondition. If a needed state does not exist, set it
   via a safe revertible write (§9/§12) or mark BLOCKED with the
   reason. **Provenance gate first:** if the assertion reads an
   instrumented surface (counter / lead / analytics / statistics /
   notification / dashboard) and the precondition would be API-created,
   do NOT execute-and-pass — classify
   `NOT-TESTABLE (instrumentation)` per
   `references/absence-check-protocol.md` and list it under "Route to
   web-testing". API-created data frequently never enters client-side
   tracking, so a clean read proves nothing.
2. Perform the call(s) with the correct auth context and headers (§1,
   §2, §11.2). Writes: snapshot first, write, revert in teardown.
3. Read the actual value from the response envelope (`.data`, §5) and
   compare to the expected result.
4. Classify (below). Capture endpoint + observed field as evidence
   (redact tokens) in the Results row. **Also write a
   `§<n>` of `<ISSUEKEY>-api-evidence.md`** for every PASS, FAIL,
   FAIL CONFIRMED, FAIL REJECTED and PARTIAL row: the method + path +
   auth context (the role, never the token), the request body's
   relevant keys, the HTTP status, and the response excerpt that
   decides the verdict, quoted from `.data`. Name it in the row's
   Comment. The step-5 evidence audit rates the row from this section
   (`../qa-pipeline-code/references/evidence-audit.md`); it can
   re-issue only a GET that needs no login, never a write, so for
   everything else this section is the proof that survives the run.

### Step 5 — Build the report
Create `<ISSUEKEY>-api-testing.md` per `references/output-template.md`.

## Classification

Canonical definitions, evidence requirements, and the routing
invariant: `../qa-run-analyzer/references/status-vocabulary.md` — new
or changed statuses land there first. This stage emits:

- `PASS` — response matches the expected result.
- `FAIL` — concrete discrepancy, for a case that arrived as QA.
- `FAIL CONFIRMED` / `FAIL REJECTED` — for arrived-as-FAIL cases: the
  API confirms (or refutes) the code-review bug.
- `PARTIAL` — some steps/surfaces pass, others do not (record which).
- `BLOCKED` — tried and could not execute. **Needs a recorded
  `Probe:`** — the verbatim call/check proving the blocker is real,
  plus its response. No probe possible → `BLOCKED (unverified)` with
  what would verify it (wrong blockers silently remove cases from
  testing; nine across two runs dissolved on a single probe each).
- `BLOCKED (quota)` — stopped by OUR tooling's limit (a Claude usage
  or session limit, an MCP / connector rate limit, HTTP 429), not by
  the product or the environment. Record the limit's error text
  verbatim; the report is `Completeness: partial` and the stage
  resumes after the reset for exactly these rows
  (`../qa-run-analyzer/references/status-vocabulary.md`).
- `NOT-TESTABLE` — the ticket's endpoint mapping is wrong or
  ambiguous; record the correct endpoint and what it actually does
  (§11.3). (Older reports used `QA` for this — do not: `QA` is an
  INPUT status, never an output of this stage.)
- `NOT-TESTABLE (instrumentation)` — this stage's instrument cannot
  measure the claim (instrumented surface + API-created precondition,
  or absence check with no positive control — protocol reference).
  Always also listed under **"Route to web-testing"**; web-testing
  picks those up regardless of channel tag.
- `NOT EXECUTED` — in scope but not attempted, for a stated
  environmental reason. Distinct from BLOCKED (which means tried);
  counts toward the Completeness header's "partial — N of M".
- `SPEC-DEFECT` — executing the case showed its PREMISE or expected
  result is wrong (the assumed setting does not exist, the expected
  value contradicts the ticket's own spec). Not a product FAIL, not a
  PASS: feeds a case-correction line in the human summary's "To do" and a
  `discrepancy` note on the suite case. **If you write the doubt, you
  must classify it** (status-vocabulary, cross-stage rules): a finding
  that blames the case's wording IS a SPEC-DEFECT, not a FAIL.
- `OBSERVATION (no source checked)` — a real measurement, with no
  clause in any source of record saying it is wrong. Phrase it as a
  question, never a verdict; keep it out of every defect list; not a bug
  candidate. Rules and the register:
  `../qa-pipeline/references/sources-of-record.md`.

Rules: prefer BLOCKED/NOT-TESTABLE over a false PASS; never PASS with
doubt; every FAIL/PARTIAL needs endpoint + observed vs expected;
arrived-as-FAIL cases exit only as FAIL CONFIRMED / FAIL REJECTED.
**Every FAIL and every `RISK-CR-*` row carries its `Source:` and
`Clause:`** — the register row, the verbatim sentence the build
contradicts, and the criterion's ledger id (`· AC-<n>`, from the case's
`Covers:` line) when the clause is an acceptance criterion. Check the as-built document as well as the brief: a
behaviour the as-built page records as deliberate is not a defect,
however wrong the measurement looks. No clause in any source →
`OBSERVATION (no source checked)`.
Absence checks and instrumented-surface assertions follow
`references/absence-check-protocol.md` — no PASS without provenance,
positive control, and the post-lag second read; "anywhere" claims
enumerate surfaces per role or cap at PARTIAL.

## Verification before saving
- Every `[API]` QA/FAIL case from code review appears in the results
  table (order matches the test-cases file).
- Every `NOT-TESTABLE (instrumentation)` case also appears in "Route
  to web-testing" with the precondition the browser run must create
  through the UI.
- No PASS/PARTIAL sits on an instrumented-surface assertion with an
  API-created precondition; no absence-check PASS lacks its positive
  control + post-lag second read.
- Every FAIL / FAIL CONFIRMED / FAIL REJECTED / PARTIAL / BLOCKED /
  NOT-TESTABLE has evidence (endpoint + observed vs expected, or the
  reason).
- No secrets/tokens anywhere in the file.
- Every write has a documented revert (or throwaway-entity cleanup).

## Output file
Create `<ISSUEKEY>-api-testing.md` in the run folder per
`references/output-template.md`. If it already exists — delete it and
create a new one (single latest run, no append).

## Final answer
After saving, report: the path; the PASS / FAIL / FAIL CONFIRMED /
FAIL REJECTED / PARTIAL / BLOCKED / NOT-TESTABLE counters; the overall
verdict; any confirmed bugs; any endpoint-mapping corrections; what
was routed to web-testing; what was left for `[mobile]` /
`[export/email]`.
