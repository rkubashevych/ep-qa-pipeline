---
name: web-testing
description: >
  Eighth stage of task processing. Takes the QA items and FAIL items
  from code review and the test cases, executes them in the browser
  via a Chrome extension, checks the expected results, and builds a
  detailed report. Use when the user says "web testing",
  "test in the browser", "run the QA checks", "browser testing",
  or after code review is finished. NOT for hand-testing by the user:
  the manual run sheet is qa-manual-runsheet (stage 9) and ingesting
  the human's results is qa-manual-results (stage 10).
---

# Web Testing

Executes the QA and FAIL test cases in a real browser: QA = items code
review could not settle against the code; FAIL = code-review findings
that need runtime confirmation. Input: the code-review and test-cases
files. Output: a detailed per-case report.

## Input

1. `<ISSUEKEY>-code-review.md` (from code-review). Present in the
   working directory in the same chat; in a new chat the user uploads
   it.
2. `<ISSUEKEY>-test-cases.md` (from qa-test-cases) — same availability.
3. `<ISSUEKEY>-checklist.md` — source of the `[UI]` structural checks
   (presence / type / label) that deliberately have no test case.
   Execute them for the pages you visit and report them in the
   "Structural checks" section. If genuinely unavailable, note that in
   the report's Notes line and continue with test cases only.

Optional: a per-task **base URL / test host**. Many tasks are tested
on a task-specific alpha host (e.g. an `*alphanext*.expoplatform.net`
host named in the QA sub-task or a dev-QA-guide comment). If the
files or the user name one, use it for all navigation and login,
overriding the `login-config.md` default; otherwise use the default
and tell the user which host you are testing against.

If the code-review or test-cases file is not provided — ask before
starting. If any file is empty or corrupted — stop and notify the
user. The issue key follows the Jira format `PROJECT-123` (e.g.
`EP-1234`).

### Scope — the routing invariant

This stage's scope follows the routing invariant
(`../qa-run-analyzer/references/status-vocabulary.md` → "Routing
invariant"): **every QA/FAIL case no earlier stage conclusively
executed at runtime, plus every routed-in case** — api-testing's
"Route to web-testing" section and code-review's `RE-ROUTE [UI]`
cases join the working list regardless of their channel tag, with
their origin noted. In practice:

- `[UI]` QA/FAIL cases (and dual `[API][UI]` cases) — execute here.
- `[API]` cases — executed by api-testing (stage 7, which runs first
  in the orchestrated flow): if `<ISSUEKEY>-api-testing.md` exists,
  add one line — "[API] cases executed by api-testing (stage 7), see
  <ISSUEKEY>-api-testing.md" — instead of re-listing them; only when
  it does not exist do they go into "Not executed here".
- `[mobile]` / `[export/email]` — always "Not executed here" with
  their tag, so they are visibly routed rather than silently dropped.

Data sources: the code-review file (QA/FAIL items), the test-cases
file (steps, data, expected results), the checklist (structural
checks), the product UI via the browser backend,
`navigation_paths.json` (navigation memory), and
`references/login-config.md`. All input files are read-only. Do not go
to the tracker, do not use external tools, do not inspect code.

## Rules

- All communication and the entire output file are in English. Keep
  chat messages short.
- Test cases with PASS and N/A in code review are not executed —
  only QA and FAIL (plus routed-in cases).
- Do not change data in the system without an explicit test-case step
  that requires it: no creating records, deleting data, or changing
  settings unless a step says so.
- Test data comes from the case's `[data: ...]` annotations (older
  files: a "Test data" column). Concrete values are used literally;
  `[test data]` examples are used as given. Do not invent test data.
- After saving the file — stop. Do not continue into later skills.

## Execution backends

Pick the backend at the start of the run and say which one is used:

1. **Playwright MCP (preferred)** — when its tools are in the session.
   Own headless browser (no focus/interference breakage), scripted
   login from `.env.qa-agents` (no login pause), screenshot + console
   errors on every FAIL. Rules: **references/playwright-executor.md**.
2. **Claude in Chrome extension (fallback)** — the interactive path.
   Tools, the see→locate→act→verify pattern, waiting, element finding,
   data entry, and MUI notes: **references/browser-rules.md** — read
   it before executing any test case.

The workflow below is backend-neutral — "PAUSE for login" applies to
the extension path only. Screenshots on both backends: only as
evidence for FAIL / FAIL CONFIRMED, never for PASS.

## Workflow

### Step 1 — Collect the scope

Read `<ISSUEKEY>-code-review.md`. If it (or the test-cases file) has a
"Notes" line, copy it into the report's Notes line. Collect every
QA and FAIL case, then apply the Scope section above: add the
routed-in cases (api-testing's "Route to web-testing", code-review
`RE-ROUTE [UI]`), keep `[UI]`/dual-tagged cases, route the rest. Each
case carries its own tag on the `### TC-REQ-N.M` heading; older files
may tag only the requirement heading — then that tag applies to all
its cases.

From `<ISSUEKEY>-test-cases.md` extract each in-scope case's
precondition, steps (numbered actions with `[data: ...]`), `Exp:`
block, and postcondition. For FAIL items also extract the code-review
finding (file, line, expected vs actual) — it says exactly what to
check in the UI. For routed-in preconditions, follow the provenance
rule in Step 6.

If there are no QA/FAIL items (all PASS/N/A) — notify the user there
is nothing for web testing and stop. Otherwise notify briefly:

```
Scope: [N] test cases to execute in the browser.
- QA (verify in the UI): [N]
- FAIL (confirm the bug): [N]
Starting.
```

### Step 2 — Determine the target pages

From preconditions and case names, determine which pages the cases
touch and group the cases by page; groups are executed sequentially.
For the first (or only) group, set `TARGET_PAGE_NAME`.

### Step 3 — Check the navigation memory

Read `navigation_paths.json` (format and rules:
references/browser-rules.md → "Navigation memory"); if it does not
exist, create `{"navigation_paths": {}}`. If `TARGET_PAGE_NAME` has an
entry, use its `url` / `login_required` / `navigation_steps`
(`PATH_EXISTS = true`); otherwise `PATH_EXISTS = false`.

> **Persistence note.** In Cowork the working directory is per-session
> scratch. If a persistent folder is mounted (the `qa-pipeline-skill`
> repo keeps a git-ignored copy under `skills/web-testing/`, or the
> e2e project folder), read and write `navigation_paths.json` THERE so
> the memory survives across sessions; fall back to the working
> directory only when nothing persistent is mounted.

### Step 4 — Login (if needed)

**Playwright backend:** log in scripted per
references/playwright-executor.md ("Login") — ask the user only if the
login fails. The rest of this step is the extension path.

Read `references/login-config.md`. It reads credentials from
environment variables, which a Cowork session usually lacks — get them
from a mounted env file instead (search order:
`../api-testing/references/api-testing-reference.md` §0 —
`.env.qa-agents` in the qa-pipeline-skill repo, then the e2e `.env`).
Never ask the user to paste passwords into chat, and never print the
values. If no mounted file provides them, ask the user to log in
manually in the browser tab and continue from the logged-in state.

If login-config.md is filled in, perform the login per its
instructions (rules: browser-rules.md → "Login"). If it still has
placeholders or is missing, ask the user for the login URL, the
fields, the submit button, and the credential source, then log in per
their instructions.

### Step 5 — Navigate to the target page

`PATH_EXISTS = true`: execute the memorised `navigation_steps` per
browser-rules.md. If a step no longer works (element not found, page
changed) — ask the user for a new path and update the entry.

`PATH_EXISTS = false`: ask the user to describe step by step how to
reach `TARGET_PAGE_NAME`, execute their steps, and set
`IS_NEW_PATH = true` (they are saved in Step 7).

### Step 6 — Execute the test cases

Order: start with the page(s) whose cases carry `[risk: High]`, and
within a page run higher-risk cases first — so a cut-short session has
already covered what matters. Keep grouping by page (no ping-ponging
between pages for strict risk order); with no risk markers, use
test-cases order. The report still lists cases in test-cases order.

For each test case in the scope:

1. **Check the precondition:**
   - A page state ("the form is open") — verify the current state
     matches; if not, navigate or act to reach it.
   - Required data ("a record of type Individual exists") that is not
     in the system — ask the user how to prepare it. Do not create
     data yourself without instructions.
   - **Provenance rule (routed-in and instrumented-surface cases):**
     if the case asserts on a counter / lead / analytics / statistics /
     notification / dashboard surface, its precondition must be created
     **through the UI in this run** — an API-created fixture is invalid
     evidence (`../api-testing/references/absence-check-protocol.md`).
     If the no-unrequested-writes rule forbids creating it, PAUSE and
     ask the user to perform the setup by hand, then continue. Never
     silently skip, and never read the surface against an API-created
     fixture and call it a verdict.
   - If the next case needs a different page — go to it (memory or
     ask).
2. **Execute the steps** — interpret each numbered step as a browser
   action and verify its result per browser-rules.md →
   "Interpreting test-case steps" (see → locate → act → verify,
   checked against the per-step expectation or the case's `Exp:`
   block).
3. **Classify** per the "Classification" section.
4. **If FAIL or FAIL CONFIRMED** — take a screenshot as evidence. No
   screenshots for PASS, BLOCKED, FAIL REJECTED.
5. **Continue to the next case** without stopping.
6. **Structural checks for the page:** after a page group's cases,
   run the checklist's `[UI]` structural checks belonging to that
   page and record PASS / FAIL per check ID (REQ-N.M) for the
   "Structural checks" section. Do not navigate to extra pages only
   for structural checks — cover the pages the run already visits;
   list the rest as not visited.

### Step 7 — Save the navigation path (if new)

If `IS_NEW_PATH = true`, add the new entry to
`navigation_paths.json` (format: browser-rules.md → "Navigation
memory") without overwriting existing entries.

### Step 8 — Build the report

Create `<ISSUEKEY>-web-testing.md` per references/output-template.md:
a results table for every case; the "Structural checks" section (or
the Notes-line explanation); for each FAIL / FAIL CONFIRMED — which
step, expected, actually seen; for each FAIL REJECTED — the
code-review finding and why the UI works; for each BLOCKED — the
reason and what was seen; for each OBSERVATION — what was noticed;
summary statistics.

## Classification

Canonical definitions for ALL stages:
`../qa-run-analyzer/references/status-vocabulary.md` — new or changed
statuses land there first. This stage emits:

- `PASS` — UI behaviour matches the expected result; all steps
  executed.
- `FAIL` — concrete discrepancy between expected and actual, for a
  case that arrived as QA.
- `FAIL CONFIRMED` — arrived as FAIL from code review and the UI
  confirms it. Include the code-review finding + what was seen.
- `FAIL REJECTED` — arrived as FAIL but the UI behaves correctly
  (compensated elsewhere, or code review was wrong).
- `BLOCKED` — could not be executed (element not found, page did not
  load, no access, unreachable precondition). **Needs a recorded
  `Probe:`** — what was actually tried to prove the blocker is real
  and what it showed. No probe possible → `BLOCKED (unverified)` with
  what would verify it. Wrong blockers keep being accepted: "no such
  setting" existed under another name, "no brand on this event" had
  ten.
- `OBSERVATION` — the case passed, but a defect or anomaly outside
  the requirements scope was noticed.
- `SPEC-DEFECT` — executing the case showed its premise or expected
  result is wrong (the assumed UI element does not exist as described,
  the expected behaviour contradicts the ticket's own spec). Not a
  FAIL, not a PASS: the case or requirement needs correcting; feeds
  the human summary's "Requirements to correct" section. **If you
  write the doubt, you must classify it** (status-vocabulary,
  cross-stage rules): a finding that blames the case's wording IS a
  SPEC-DEFECT — do not record a FAIL and explain in the notes why it
  might not be one.

Risk-chasing rows: a code-review risk with no covering test case MAY
be exercised as a `RISK-CR-<n>` row when its surface is on a page this
run already visits — same evidence rules as a FAIL case. Step 6 of the
orchestrator proposes confirmed risk rows as permanent suite cases.

Rules:
- Do not mark PASS if there is any doubt — prefer FAIL with a
  description. Do not mark FAIL without a concrete discrepancy.
- **Second observation before FAILing a shared element.** A FAIL on a
  page-level or shared element (header, nav, global styles, a
  component reused across pages) requires a second observation in a
  fresh context — new navigation or fresh tab — before it is recorded.
  On one run, 16 of 17 browser-stage errors were single-observation
  false alarms on exactly such elements. Record both observations.
- **Negative/absence verdicts carry their `Control:`** — the evidence
  line naming the positive control observed on the same surface this
  run (absence-check protocol). A FAIL or "does not appear" with no
  control line is not publishable; the count gate treats it as missing
  evidence.
- **Absence checks** ("nothing appears", "no row", "zero count")
  follow `../api-testing/references/absence-check-protocol.md`: no
  PASS without a positive control observed on the same surface this
  run, and — on analytics-backed surfaces — a second read after the
  measured ingestion lag. A single immediate clean read is not a PASS.
- BLOCKED is not a FAIL; OBSERVATION never replaces FAIL.
- Cases that arrived as FAIL exit only as FAIL CONFIRMED or FAIL
  REJECTED — never plain PASS/FAIL — so the report shows what was a
  bug verification vs a new UI check.

## Browser error handling

Follow browser-rules.md → "Error handling" (page failures, expired
sessions, missing elements, blocking dialogs, unresponsive extension —
when to retry, re-login, or mark BLOCKED).

Escalation rule: after 3 failed attempts at the same goal (a login, a
navigation step, locating an element) using different approaches —
stop. Reassess the assumption that failed (wrong host? wrong role?
feature flag off? data missing?), then either ask the user (one
concise question listing what was tried) or mark the case BLOCKED with
the attempts recorded. Repeated failure is information, not an
obstacle to push through.

## Additional checks (exploratory)

If something suspicious not covered by the cases catches your eye
while executing them, record it in the report's "Observations"
section. Do not go looking for bugs deliberately.

## Verification before saving

- The number of cases in the report equals the QA + FAIL `[UI]` items
  from code review plus every routed-in case, and every QA/FAIL case
  of ANY channel appears exactly once somewhere (routing invariant:
  this report's Results, its "Not executed here", or the referenced
  api-testing report). A case that appears nowhere — find it and add
  it before saving.
- Case order matches the test-cases file.
- Every FAIL / FAIL CONFIRMED has: step, expected, actual. Every FAIL
  REJECTED has: the code-review finding + what the UI showed. Every
  BLOCKED has a reason AND a recorded probe (or is explicitly
  `BLOCKED (unverified)` with what would verify it).
- No case is missing a status, and arrived-as-FAIL cases use only
  FAIL CONFIRMED / FAIL REJECTED.

## Output file

Create `<ISSUEKEY>-web-testing.md` in the working directory (template:
references/output-template.md) and hand it to the user for download.
If the file already exists — delete it and create a new one: a single
coherent document with the latest run only, never merged or appended.

## Final answer

After saving, report: the file path; the PASS / FAIL / FAIL CONFIRMED /
FAIL REJECTED / BLOCKED / OBSERVATION counters; the overall verdict
(successful = all PASS and FAIL REJECTED); a brief list of any
FAILs/FAIL CONFIRMED problems, OBSERVATIONs, and BLOCKED cases with
reasons.
