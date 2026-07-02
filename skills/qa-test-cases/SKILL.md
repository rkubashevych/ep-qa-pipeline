---
name: qa-test-cases
description: >
  The fourth stage of task processing. Takes the checklist created
  by the qa-checklist skill, generates test cases with concrete
  steps, input data, and expected results — the input for code
  review and for manual testing.
  Use it when the user says "write test cases", "generate test cases",
  "test cases for the requirements", or after the checklist is complete.
---

# QA Test Cases

Generates test cases with concrete steps, input data, and expected
results based on the checklist.

Test cases are not a checklist. The checklist says "what to check".
A test case says "how to check": a concrete scenario with concrete
actions and concrete data.

## Input

The input is the `<ISSUEKEY>-checklist.md` file created by the
qa-checklist skill. In the same chat the file is available in the
working directory automatically. If the chat is new, the user
uploads the file to the chat.

`<ISSUEKEY>` is a Jira (Atlassian Cloud) ticket key in the
`PROJECT-123` format, for example `EP-1234`.

From the checklist, the skill takes:
- The requirement text from the heading of each section — to
  generate test cases and to ground the expected results.
- The decomposition into checks — to determine scope: if the checks
  are only about the presence, type, or label of an element, the
  requirement is structural and no test case is needed.
- The REQ-ID — for traceability.
- The channel tag on each check (`[UI]`, `[API]`, `[mobile]`,
  `[export/email]`) — carry it onto the test case. It tells later
  stages how the test case is executed: only `[UI]` test cases are
  runnable by the browser-based web-testing skill; `[API]`, `[mobile]`,
  and `[export/email]` need other tools or manual checking. Show the
  channel in each test-case group heading.

Additional source:
- The user's answers to questions asked before generation.

First, read the checklist file in full, including any "Notes" line
(for example a "⚠️ No Confluence acceptance-criteria page linked"
warning carried from earlier stages). If a Notes line is present, copy
it into the test-cases file's Notes line. If the checklist contains
checks labelled with contradictory versions ("version A — Confluence"
/ "version B — Jira"), generate test cases for each version separately
with the same labels, and count the requirement under "needing
clarification" in the statistics. If anything in the requirements is
unclear or ambiguous for building test cases, ask the user before you
start generating. Do not start generating while there are unresolved
questions.

Do not go to the tracker, do not use external tools, do not search
the internet, do not inspect code.

The checklist file is read-only.
Do not change, rewrite, or clean up its content.

If the checklist file is missing, empty, or corrupted, stop and tell
the user that the qa-checklist skill must be run first.

## Rules

- All communication and all output file content is in English.
- Chat messages are short.
- Test cases are built only from what is in the checklist file. Do
  not assume, do not add to it, do not interpret requirements on your
  own. Do not invent routes, selectors, roles, states, data, or
  expected behaviour that is not in the requirements.
- Do not change the meaning or wording of requirements. The checklist
  file is final. The skill has no right to change or rephrase
  anything in it.
- If a requirement describes a concrete value (a number, text, label,
  field name, state), the test case uses exactly that value. Do not
  replace it with another, do not generalise.
- If a requirement does NOT describe a concrete value but the test
  case needs test data, use realistic examples and mark them as
  `[test data]`.
- If a requirement was left unchanged after grooming (the user
  skipped the question in skill 2), build the test cases on what is
  there. Do not skip such a requirement and do not mark it as
  incomplete. The checklist file is final.
- Do not add general QA advice that is not tied to a specific
  requirement of the task.
- After the file is saved, stop. Do not continue into code review,
  PR summary, or planning.

## Numbering

Test cases inherit the requirement IDs from the checklist file.

The order of requirements in the test cases file must match the order
of requirements in the checklist file. Do not change, reorder, or
group requirements any differently than they appear in the file.

A single requirement can produce several test cases. Each test case
gets a sub-number: TC-REQ-3.1, TC-REQ-3.2.

The main REQ-* number does not change — it is the same as in the
checklist file and onward in code review.

If a requirement already has sub-items (REQ-5a, REQ-5b), each
sub-item is numbered separately: TC-REQ-5a.1, TC-REQ-5a.2.

## Test-case scope

Every requirement from the checklist file is covered: behavioural
ones by test cases, structural ones (only presence, type, label) by
the checklist. For structural requirements no test case is generated
— the checklist is a sufficient level of verification.

Every behavioural requirement gets at least one test case.

Who later executes these test cases — a code review agent over the
code or a human in the UI — is a matter for the next stages, not for
this skill.

## Test-case building method

For each behavioural requirement, determine which test-design
technique applies. The choice of technique, the coverage criteria,
and the application rules are in references/test-case-design-rules.md.

Not every technique applies to every requirement — apply only those
that follow from the specific requirement.

The technique is stated once in the heading of the test-case group
for the requirement, not in each test case separately.

By default, use the standard coverage level (defined in
references/test-case-design-rules.md). The extended level is only
used if the user explicitly asks.

### Grounding rule

Each test case must be tied to a concrete behaviour described in the
requirement.

If a test case contains an expected result, that result must follow
from the requirement text. If the expected result for a scenario
cannot be determined from the requirement text, do not generate the
test case; mark that the requirement needs clarification.

If a test case uses a concrete value (a number, text, ID) and that
value is in the requirement, use it literally. If the value is not in
the requirement, mark it as `[test data]` and use a realistic example.

### Filtering out unnecessary test cases

Do not generate test cases for:
- standard browser or platform behaviour (scrolling, focus, opening
  a tab) if the requirement does not describe custom behaviour
- implementation details (cache, performance, architecture) if it is
  not written in the requirement
- general infrastructure (server errors, timeouts, network failures)
  if the ticket is not specifically about this
- boundary values for fields where the requirement does not describe
  constraints or ranges
- UX details (animations, timings, hover effects) if they are not
  written in the requirement
- scenarios for which the expected result cannot be determined from
  the requirement text

The full list of anti-patterns is in
references/test-case-design-rules.md, section "Anti-patterns".

## Verification before saving

After generating the test cases and before saving the file:

1. Run the test cases through the filter for unnecessary ones.
2. Go through the test cases and verify:

- Every requirement from the checklist file has at least one test case.
- There are no test cases without a REQ-ID.
- The order of requirements matches the order in the checklist file.
- There is no duplication: the same scenario does not appear twice.
  Two test cases from the same equivalence class are a duplicate.
- Each test case has a precondition, steps, test data, and an
  expected result. If any part is empty, delete or complete it.
- The expected result of each test case follows from the requirement
  text, and is not made up.
- Expected results contain no ambiguous words: "correctly",
  "properly", "appropriate", "as needed", "in the appropriate way".
  Instead, use a concrete value, state, or behaviour.
- Test data is realistic and marked where it is not from the
  requirement.

If a problem is found, fix it before saving.

## Output file

Create the `<ISSUEKEY>-test-cases.md` file in the working directory
and give it to the user to download.

The file stays in the working directory — the next skill in the same
chat picks it up automatically.

If the file already exists, delete it completely and create a new
one. The output is always a single file with the result of the last
run. Do not merge with the previous version, do not append, do not
keep data from the previous write.

Before finishing, verify:
- One top-level heading
- One coherent document with no duplicated sections

The file structure template is in references/output-template.md.
An example of the level of detail is in references/test-cases-example.md.
The rules for techniques and coverage are in
references/test-case-design-rules.md.

## Formatting (Jira-friendly)

The test-cases file is published into a Jira comment and read both by a
human and by the code phase. Format for easy human scanning:

- Do NOT use wide markdown tables (`| # | Step | ... |`). Wide rows force
  horizontal scrolling inside Jira code blocks.
- Use a vertical block layout per test case (the exact shape is in
  references/output-template.md): a `### TC-REQ-N.M — <name>` heading,
  then `Pre:` / `Steps:` / `Exp:` / `Post:` lines.
- Steps are a numbered list, one action per line. Inline short test
  data as `[data: ...]`; break it onto its own line only if it is long.
- Expected results live under a single `Exp:` block at the end of the
  case. Attach a per-step expected result only when a mid-flow check is
  essential.
- Keep every line short (aim <= ~64 characters). Wrap a long step or
  expected result onto the next indented line rather than writing one
  long row.
- `Post:` only when the system state changes; omit the line otherwise.
- Channel tags go on the requirement group heading
  (`## REQ-N — <label>  [UI]`), not on each test case.