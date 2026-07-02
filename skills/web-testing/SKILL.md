---
name: web-testing
description: >
  Eighth stage of task processing. Takes the QA items and FAIL items
  from code review and the test cases, executes them in the browser
  via a Chrome extension, checks the expected results, and builds a
  detailed report. Use when the user says "web testing",
  "test in the browser", "run the QA checks", "manual testing",
  or after code review is finished.
---

# Web Testing

Executes the QA and FAIL test cases in a real browser.
QA — items that cannot be checked against the code.
FAIL — items that code review flagged as problematic;
they need confirmation in the UI that the bug really exists.
The input is the code-review and test-cases files. The output is
a detailed report with the result of each test case
executed in the UI.

## Input

From the user you need:
1. The code-review file `<ISSUEKEY>-code-review.md` created
   by the code-review skill. In the same chat the file is available
   in the working directory automatically. If the chat is new —
   the user uploads the file into the chat.
2. The test-cases file `<ISSUEKEY>-test-cases.md` created
   by the qa-test-cases skill. In the same chat it is available automatically.

Optional input:
- A checklist file `<ISSUEKEY>-checklist.md` — for structural
  checks that did not make it into the test cases.
- A per-task **base URL / test host**. Many tasks are tested on a
  task-specific alpha host (e.g. an `*alphanext*.expoplatform.net`
  host named in the QA sub-task or a dev-QA-guide comment), not the
  default site in `login-config.md`. If the test-cases/code-review
  files or the user provide such a host, use it as the base for all
  navigation and login, overriding the default. If none is given, fall
  back to the `login-config.md` default and tell the user which host
  you are testing against.

Only `[UI]` test cases are executable in the browser. Test cases tagged
`[API]`, `[mobile]`, or `[export/email]` cannot be run by this skill —
list them in the report's "Not executed here" section with their tag,
so they are visibly routed to API tools / mobile / manual rather than
silently dropped.

The issue key follows the Jira format `PROJECT-123` (for example `EP-1234`).

If the code-review file is not provided — ask before starting.
If the test-cases file is not provided — ask before starting.
If any file is empty or corrupted — stop
and notify the user.

Data sources for this skill:
- the code-review file — the source of QA and FAIL items
- the test-cases file — the source of steps, test data
  and expected results
- the checklist file (optional) — structural checks
- the product UI via the Chrome extension — the source of actual
  results
- navigation_paths.json — the memory of navigation paths
- references/login-config.md — login instructions

All input files are read-only.
Do not change, rewrite, or clean up their content.

Do not go to the tracker, do not use external tools,
do not inspect code.

## Rules

- All communication and the entire content of the output file are in English.
- Keep chat messages short.
- Browser tool: the Claude in Chrome extension.
  Do not use the Playwright MCP.
- Test cases with PASS and N/A statuses in code review
  are not executed in the browser. Only QA and FAIL are executed.
- Do not change data in the system without an explicit test-case step
  that requires that change. If a step says "enter a value" —
  enter it. If it does not say so — do not enter it. Do not create records,
  do not delete data, do not change settings unless that is
  an explicit step of the test case.
- Test data is taken from the test case's `[data: ...]` annotations
  in the steps (older files may use a "Test data" column instead).
  If a concrete value is there — use it literally. If it is marked
  `[test data]` with a realistic example — use that example.
  Do not invent test data yourself.
- After saving the file — stop. Do not continue
  into later skills or planning.

## Chrome extension tools

To work with the browser, use these tools:

- **navigate** — go to a URL.
- **find** — find an element on the page by a natural-language
  description. The primary way to locate elements.
- **read_page** — get the page structure (accessibility
  tree). With `filter: "interactive"` — only the interactive
  elements (buttons, fields, links).
- **computer** with `action: "screenshot"` — take a screenshot.
  Use it only as evidence for FAIL
  and FAIL CONFIRMED. Do not take screenshots for PASS.
- **computer** with `action: "left_click"` — click an element.
- **computer** with `action: "type"` — enter text.
- **computer** with `action: "key"` — press a key.
- **computer** with `action: "scroll"` — scroll the page.
- **form_input** — set the value of a form field by ref.
- **get_page_text** — get the page text.
- **tabs_context_mcp** — get the list of tabs.

The full interaction rules are in references/browser-rules.md.

## Workflow

### Step 1 — Collect the scope

Read `<ISSUEKEY>-code-review.md`. If it (or the test-cases file) has a
"Notes" line — a warning or unresolved-conflict flag carried from
earlier stages — copy it into the report's Notes line. Find all test
cases with the status `QA` or `FAIL` in the results table.
This is the working list to execute in the browser.

- `QA` — needs manual verification because code review
  could not verify it against the code.
- `FAIL` — code review found a problem against the code,
  it needs to be confirmed or refuted in the UI.

Test cases with the statuses `PASS` and `N/A` in code review
are not included in the scope — they are already checked against the code.

Then read `<ISSUEKEY>-test-cases.md`. For each
QA and FAIL test case, extract the full data:
- Precondition
- The steps (numbered actions with `[data: ...]`) and the `Exp:`
  block (older files may use a steps table instead)
- Postcondition (if any)

For FAIL items, additionally extract the finding from code review:
the file, the line, what was expected, what is actually in the code.
This information helps to understand exactly what to check in the UI.

Split the QA/FAIL scope by channel tag. Only `[UI]` test cases are
executed in the browser. Put `[API]`, `[mobile]`, and `[export/email]`
test cases in the report's "Not executed here" section (with their tag
and why), so they are routed to the right tool/owner instead of being
lost.

If there are no QA and FAIL items (all PASS/N/A) — notify
the user that there are no items for web testing and stop.

Notify the user briefly:
```
Scope: [N] test cases to execute in the browser.
- QA (verify in the UI): [N]
- FAIL (confirm the bug): [N]
Starting.
```

### Step 2 — Determine the target pages

From the test cases, determine which pages or sections of the product
you need to go to. This is usually visible from the preconditions or
the test-case names.

Group the test cases by page. If all the test cases
relate to one page — one group. If they relate to different
pages — several groups, executed sequentially group by group.

For the first (or only) group, extract `TARGET_PAGE_NAME`.

### Step 3 — Check the navigation memory

Read `navigation_paths.json` from the working directory.

> **Persistence note.** In Cowork the working directory is per-session
> scratch, so a `navigation_paths.json` created there is lost when the
> chat ends. If a persistent folder is mounted (e.g. the
> `qa-pipeline-skill` repo, which keeps a git-ignored copy under
> `skills/web-testing/`, or the e2e project folder), read and write
> `navigation_paths.json` THERE instead, so the memory survives across
> sessions. Only fall back to the working directory when no persistent
> folder is available — and expect to rebuild the memory next session.

If the file does not exist — create an empty structure:
```json
{"navigation_paths": {}}
```

Look for `TARGET_PAGE_NAME` as a key in `navigation_paths`.

**If found:**
- Extract `url` — the direct URL if any.
- Extract `login_required` — whether a login is needed.
- Extract `navigation_steps` — the array of navigation steps.
- Set `PATH_EXISTS = true`.

**If not found:**
- Set `PATH_EXISTS = false`.

### Step 4 — Login (if needed)

Read `references/login-config.md` from the skill directory.

**If the file is filled in** (contains a URL, field descriptions,
the source of the credentials):
- Perform the login according to the instructions in the file.
- The login rules are in references/browser-rules.md,
  the "Login" section.

**If the file is not filled in** (contains placeholders
`<LOGIN_URL>`, `<how to find the field>`, etc.)
or the file is missing:
- Ask the user: the login URL, where the username
  and password fields are, which is the submit button, where the
  credentials come from.
- Perform the login according to the user's instructions.

### Step 5 — Navigate to the target page

**If `PATH_EXISTS = true`:**
Execute each step from `navigation_steps` sequentially,
following the rules in references/browser-rules.md.

If a step from memory does not work (element not found,
page changed) — ask the user for a new path
and update the entry in `navigation_paths.json`.

**If `PATH_EXISTS = false`:**
Ask the user:
```
The path to "[TARGET_PAGE_NAME]" was not found in memory.
Describe step by step how to get to this page:
1. [First step]
2. [Second step]
3. ...
```

Wait for the answer. Execute the user's steps.
Save the steps as `USER_NAVIGATION_STEPS`.
Set `IS_NEW_PATH = true`.

### Step 6 — Execute the test cases

For each test case in the scope:

1. **Check the precondition:**
   - If the precondition describes a page state (for example
     "the form is open", "the list is loaded") — verify
     that the current state matches. If not — go
     to the required page or perform the actions to reach
     that state.
   - If the precondition describes the presence of data (for example
     "there is a record of type Individual") and that data does not exist
     in the system — ask the user how to prepare
     the data: where to create it, which values to set, whether there is
     a ready record that can be used. Do not create
     data yourself without instructions from the user.
   - If the next test case requires a different
     page — go to it (check the memory
     or ask the user).

2. **Execute the steps** — for each numbered step of the test
   case, interpreting the step as a browser action:

   **How to interpret the steps:**
   - "Open [page/form/modal]" → `navigate`
     to a URL or `find` + `computer click` on the element
     that opens it.
   - "Enter [value] into [field]" → `find` the field
     by description → `form_input` or `computer type`.
   - "Click [button]" → `find` the button by text
     → `computer left_click`.
   - "Select [option] in [dropdown]" → `find` the dropdown
     → `computer left_click` → `find` the option
     → `computer left_click`. Or `form_input` with the value.
   - "Check that [element/text] is displayed"
     → `find` the element or `get_page_text` and look for the text.
   - "Scroll to [element]" → `computer scroll`
     or `find` + `computer scroll_to`.

   **For each step:**
   a. `read_page` or `find` — see the current state.
   b. Find the target element.
   c. Perform the action.
   d. Verify the expected result — the per-step expected result if
      the step has one, otherwise the case's `Exp:` block after the
      final step: look for the text, element or state on the page via
      `find`, `read_page` or `get_page_text`.
   e. Record the result of the step: it matches
      or it does not match.

3. **Classify the test case** according to the
   "Classification" section.

4. **If FAIL or FAIL CONFIRMED** — take a screenshot
   (`computer screenshot`) as evidence. Do not take a screenshot
   for PASS, BLOCKED, FAIL REJECTED.

5. **Continue to the next test case** without stopping.

### Step 7 — Save the navigation path (if new)

If `IS_NEW_PATH = true`:
- Read `navigation_paths.json`.
- Add a new entry:
```json
"[TARGET_PAGE_NAME]": {
  "url": "[direct URL if any]",
  "login_required": true,
  "navigation_steps": ["step 1", "step 2", "..."],
  "last_used": "[ISO timestamp]"
}
```
- Save the file without overwriting existing entries.

### Step 8 — Build the report

Create the file `<ISSUEKEY>-web-testing.md` with the results.

The template is in references/output-template.md.

The report must be detailed:
- A results table for each test case.
- For each FAIL and FAIL CONFIRMED — specifically:
  which step, what was expected, what the agent actually saw.
- For each FAIL REJECTED — what the code-review finding
  showed and why the UI works correctly.
- For each BLOCKED — the reason and what the agent saw.
- For each OBSERVATION — what exactly was noticed.
- Summary statistics.

## Classification

Each test case gets one status:

- `PASS` — the UI behavior matches the expected result
  from the test case. All steps were executed successfully.
- `FAIL` — the UI behavior does not match the expected result.
  There is a concrete discrepancy between expected and actual.
  Used for test cases that arrived with the status
  QA from code review.
- `FAIL CONFIRMED` — the test case arrived with the status FAIL
  from code review and the UI confirms it: the bug really shows
  in the interface. Include the finding from code review + what the
  agent saw in the UI.
- `FAIL REJECTED` — the test case arrived with the status FAIL
  from code review but the UI shows correct behavior. The bug found
  in the code does not show in the UI — it may be compensated by another
  mechanism, or code review was wrong.
- `BLOCKED` — the test case cannot be executed. The element
  was not found, the page did not load, there is no access,
  the precondition is unreachable.
- `OBSERVATION` — the test case passed (PASS), but a defect
  or anomaly outside the requirements scope was noticed.

Rules:
- Do not mark PASS if there is any doubt — prefer FAIL with a description.
- Do not mark FAIL without a concrete description of the discrepancy.
- BLOCKED is not a FAIL. The test did not fail, it could not
  be executed.
- OBSERVATION does not replace FAIL. If the expected result
  does not match — that is a FAIL, not an OBSERVATION.
- For items with FAIL from code review, use only
  FAIL CONFIRMED or FAIL REJECTED — not a plain FAIL/PASS.
  This makes it clear in the report what was a bug verification
  and what was a new UI check.

## Browser error handling

- The page did not load (timeout, 500, blank) —
  try reloading once via `navigate`.
  If it did not help — BLOCKED for all test cases
  of that page.
- Session expired during execution — repeat the login
  according to step 4, continue from the current test case.
- Element not found after 2 attempts (including scrolling) —
  BLOCKED for that test case with a description of what was looked for and where.
- An alert or dialog appears — read the text,
  record it, close it and continue. If the dialog
  blocks execution — BLOCKED.
- The Chrome extension does not respond — stop, notify
  the user.

## Additional checks (exploratory)

After executing all the test cases, if the agent noticed
something suspicious during navigation or while executing the steps
that is not covered by the test cases — record it in the
"Observations" section of the output file.

Do not look for bugs deliberately. Record only what
caught your eye while going through the test cases.

## Verification before saving

Before saving, check:

- The number of test cases in the report equals the number
  of QA + FAIL items from the code-review file. If it does
  not match — find the missing ones and add them.
- The order of the test cases matches the order in the test-cases file.
- Every FAIL and FAIL CONFIRMED has: which step,
  the expected result, the actual result.
- Every FAIL REJECTED has: the code-review finding and what the
  agent saw in the UI.
- Every BLOCKED has a reason.
- There are no test cases without a status.
- For items with FAIL from code review —
  FAIL CONFIRMED or FAIL REJECTED was used, not PASS/FAIL.

## Output file

Create the file `<ISSUEKEY>-web-testing.md` in the working
directory and hand it to the user for download.

The file stays in the working directory.

If the file already exists — delete it completely and create a new one.
The output is always a single file with the result of the latest run.
Do not merge with the previous version, do not append, do not keep
data from the previous entry.

Before finishing, check:
- One top-level heading
- One coherent document without duplicated sections

The template is in references/output-template.md.

## Final answer

After saving the file, report:
- The path to the saved file
- PASS / FAIL / FAIL CONFIRMED / FAIL REJECTED / BLOCKED / OBSERVATION counters
- The overall verdict: web testing successful
  (all PASS and FAIL REJECTED) or unsuccessful
  (there is a FAIL or FAIL CONFIRMED)
- If there is a FAIL or FAIL CONFIRMED — briefly list
  the problems found
- If there is an OBSERVATION — briefly list the observations
- If there is a BLOCKED — list what could not be executed and why