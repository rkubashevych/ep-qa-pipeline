---
name: qa-test-cases
description: >
  The last docs stage of task processing (stage 4; stage 3 — the
  standalone checklist — was folded into it in 0.40.0). Takes the
  groomed requirements file, decomposes every requirement into atomic
  checks, and writes the two things the pipeline actually reads:
  test cases with concrete steps, data and expected results for the
  behavioural checks, and a Structural checks section for the
  presence / label / field-type checks — the input for the QA Service
  publish, code review and the manual round. Use it when the user
  says "write test cases", "generate test cases", "test cases for the
  requirements", "build a checklist" / "make the QA checklist" (the
  checks are this stage's working step), or after requirements
  grooming is complete. Do NOT use to create cases in QA Service
  directly or outside the pipeline's requirements file — the publish
  step of qa-pipeline-docs does that from this stage's output.
---

# QA Test Cases

Turns the groomed requirements into test cases and structural checks.

Two working steps, one file. First **decompose** every requirement
into atomic checks (what to check, expected result) — the method in
`references/check-decomposition.md`. Then **write**: each behavioural
check becomes a test case ("how to check": a concrete scenario with
concrete actions and data); each structural check (presence, label,
type, default state) becomes one line in the Structural checks
section. The intermediate check list is not saved — every check lands
in one of the two.

## Input

The input is the `<ISSUEKEY>-requirements.md` file created by the
requirements-grooming skill.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

`<ISSUEKEY>` is a Jira (Atlassian Cloud) ticket key in the
`PROJECT-123` format, for example `EP-1234`.

From the requirements file, the skill takes:
- The numbered requirements — the only source of behaviour. Each
  `REQ-N` (or `REQ-Na` sub-item) becomes a group in the output.
- Each requirement's `source:` line — the AC-ledger ids (`AC-n` /
  `JD-n` / `CM-n`) it was built from. Copy them onto the group's
  `Covers:` line, so every test case and structural line is traceable
  to the acceptance criterion it verifies, and the Statistics block can
  state `AC coverage` mechanically.
- The `[risk: High|Medium|Low]` marker on each requirement — copy it
  unchanged onto the `## REQ-N` group heading; it scales coverage
  depth here and the executing stages run High-risk cases first.
- The "Notes" block under the Goal (for example a "⚠️ No Confluence
  acceptance-criteria page linked" warning or unresolved-conflict
  flags) — copy it into the test-cases file's Notes line so a manual
  tester knows the input was weaker than ideal.
- A requirement marked "(unresolved conflict)" with two contradictory
  versions — decompose and write each version separately, labelled
  ("version A — Confluence" / "version B — Jira"), and count the
  requirement under "needing clarification" in the statistics. Never
  silently pick one side.

Additional source:
- The user's answers to questions asked before generation.

First, read the requirements file in full. If anything is unclear or
ambiguous for building checks or cases, ask the user before you start
generating. Do not start generating while there are unresolved
questions. (Under the `qa-pipeline-docs` orchestrator this stage does
not pause: it builds on what is there and marks the ambiguity as
"needs clarification" — the orchestrator says so.)

Do not go to the tracker, do not use external tools, do not search
the internet, do not inspect code.

The requirements file is read-only. Do not change, rewrite, or clean up
its content.

If the requirements file is missing, empty, or corrupted, stop and tell
the user that the requirements-grooming skill must be run first.

## Rules

- All communication and all output file content is in English.
- Chat messages are short.
- Checks and test cases are built only from what is in the
  requirements file. Do not assume, do not add to it, do not interpret
  requirements on your own. Do not invent routes, selectors, roles,
  states, data, or expected behaviour that is not in the requirements.
- Do not change the meaning or wording of requirements. The
  requirements file is final. The skill has no right to change or
  rephrase anything in it.
- If a requirement describes a concrete value (a number, text, label,
  field name, state), the check and the test case use exactly that
  value. Do not replace it with another, do not generalise.
- If a requirement does NOT describe a concrete value but the test
  case needs test data, use realistic examples and mark them as
  `[test data]`.
- If a requirement was left unchanged after grooming (the user skipped
  the question in stage 2), build on what is there. Do not skip such a
  requirement and do not mark it as incomplete.
- Do not add general QA advice that is not tied to a specific
  requirement of the task.
- After the file is saved, stop. Do not continue into code review,
  PR summary, publishing, or planning.

## Step 1 — Decompose every requirement into checks

Read `references/check-decomposition.md` before you start. For each
requirement, in the order of the requirements file: elements and
states → actions and behaviours → conditions and constraints →
dependencies; every item with an unambiguous pass/fail is a check.
Then the seams between requirements. Then the filter for unnecessary
checks.

Sort every check into one of two bins (`check-decomposition.md` →
"Behavioural vs structural"):

- **structural** — a static property of the surface: presence, label
  or placeholder text, element type, default state, relative position.
  `[UI]` by nature. Goes to the Structural checks section.
- **behavioural** — everything else. Goes to a test case.

Channel-tag every check: `[UI]` (admin panel or frontend web UI —
browser-testable), `[API]` (an API response/contract check — verified
with API tools, not the browser), `[mobile]` (Android/iOS), or
`[export/email]` (XLS/CSV exports, emails, integration push-back). A
requirement that spans channels produces separate checks per channel.
**Provenance-sensitive exception — dual tag:** when the expected
result reads a counter / lead / analytics / statistics / notification
/ dashboard surface, the endpoint alone cannot prove the behaviour
(API-created actions often skip client-side tracking), so such a check
and its case carry `[API][UI]` — "the call is API-shaped, but the
verdict needs the browser". The tag is an ADVISORY routing hint made
at the docs phase, blind — the binding routing rule, and what the
later stages do with the tags, is the routing invariant in
`../qa-run-analyzer/references/status-vocabulary.md`.

## Step 2 — Write the test cases (behavioural checks)

### Numbering

Test cases inherit the requirement IDs. Each `## REQ-N` group opens
with a `Covers:` line naming the ledger ids from the requirement's
`source:` line (`Covers: AC-2` / `Covers: AC-3, JD-1`); a requirement
with a structural line and no case still gets its `Covers:` in the
Structural checks section (the line's REQ id resolves it). A single requirement can
produce several test cases: TC-REQ-3.1, TC-REQ-3.2. The main REQ-*
number does not change — it is the same as in the requirements file
and onward in code review and the suite. A requirement with sub-items
(REQ-5a, REQ-5b) is numbered per sub-item: TC-REQ-5a.1, TC-REQ-5b.1.
The order of requirement groups in the file matches the order in the
requirements file.

### Scope

Every requirement is covered: behavioural ones by test cases,
structural ones by the Structural checks section. Every behavioural
requirement gets at least one test case; a structural requirement gets
none (its lines are its verification). Who later executes a case — a
code review agent over the code, an API call, a browser, or a human in
the UI — is a matter for the next stages, not for this skill.

### Method

For each behavioural requirement, determine which test-design
technique applies. The choice of technique, the coverage criteria, and
the application rules are in `references/test-case-design-rules.md`.
Not every technique applies to every requirement — apply only those
that follow from the specific requirement. The technique is stated
once in the heading of the test-case group, not in each test case.

Coverage depth is risk-scaled: the `[risk: …]` marker selects the
depth per the "Coverage levels" table in
`references/test-case-design-rules.md` (High = extended techniques,
Medium = standard, Low = reduced). The full extended level for every
requirement is only used if the user explicitly asks.

For every behavioural requirement, mark exactly one case as the core
case — ` [core]` on its heading, after the channel tag — per the "Core
selection rule" in `references/test-case-design-rules.md`. The core
case is the card the manual walk (stage 10a) always presents, so the
human touches every requirement even when the machine settled it.

**Combinatorial requirements (3+ interacting parameters).** If a
requirement's behaviour depends on the combination of three or more
parameters (role × event type × setting), do not hand-derive the
combinations: build a model and generate a pairwise set with
`scripts/generate_pict_cases.py`, following
`references/combinatorial-testing.md`. Parameter values come only from
the requirement text. Each generated row becomes a normal TC block and
must still pass the grounding rule; state the technique as "Pairwise
(PICT)" with the model on a `Model:` line in the group heading.

### Grounding rule

Each test case is tied to a concrete behaviour described in the
requirement. If a test case contains an expected result, that result
must follow from the requirement text; if it cannot be determined from
the text, do not generate the case — mark that the requirement needs
clarification. A concrete value in the requirement is used literally;
a value the requirement does not give is `[test data]` with a
realistic example.

### Filtering out unnecessary test cases

Do not generate test cases for: standard browser or platform behaviour
(scrolling, focus, opening a tab) unless the requirement describes
custom behaviour; implementation details (cache, performance,
architecture) not written in the requirement; general infrastructure
(server errors, timeouts, network failures) unless the ticket is about
it; boundary values where the requirement describes no constraints; UX
details (animations, timings, hover) not in the requirement; scenarios
whose expected result cannot be determined from the requirement text.
The anti-patterns are in `references/check-decomposition.md` and
`references/test-case-design-rules.md`.

## Step 3 — Write the Structural checks section

One line per structural check, grouped by requirement in requirement
order, id `REQ-N/struct-k` where k counts from 1 under each REQ:

```
- [ ] REQ-3/struct-1 [UI] The "State" label is displayed above the State select
```

The id is what the publish step writes as the STRUCT case's
`detail.pipelineId` and what the code phase rebuilds the line from
(`../qa-pipeline-docs/references/qa-service-publish.md` → "Structural
checks"). The text is the check verbatim — element + expected property,
no scenario. Omit the section only when there is not one structural
check in the whole ticket; say so in the final response.

## Verification before saving

After generating and before saving the file:

1. Run the cases and the structural lines through the filters for
   unnecessary items.
2. Verify:

- Every requirement from the requirements file has at least one test
  case or one structural line. Nothing without a REQ-ID.
- The order of requirement groups matches the requirements file.
- No duplication: the same scenario does not appear twice (two test
  cases from the same equivalence class are a duplicate); no structural
  line restates a test case or another line.
- Each test case has a precondition, steps, test data, and an expected
  result. If any part is empty, delete or complete it.
- The expected result of each test case follows from the requirement
  text, and is not made up.
- Expected results and structural lines contain no ambiguous words:
  "correctly", "properly", "appropriate", "as needed". Use a concrete
  value, state, or behaviour.
- Test data is realistic and marked where it is not from the
  requirement.
- **The statistics block is derived mechanically, never tallied by
  hand.** Count the `### TC-REQ` headings, their channel tags, the
  `[core]` markers and the `- [ ] REQ-N/struct-k` lines grep-style over
  the generated text — where a shell is available,
  `python3 ../qa-run-analyzer/scripts/reconcile_counts.py <ISSUEKEY>`
  prints exactly these counts for the file. Hand tallies of this file
  have produced three different answers for the same 89 headings — and
  the numbers get copied into the suite. Dual-tagged `[API][UI]` cases
  are counted once, under their own row. The totals row equals the
  number of headings exactly; structural checks have their own row and
  are not in the total.
- Every behavioural requirement has exactly ONE case marked `[core]`
  on its heading — zero or two is an error. Structural requirements
  have none. The core count equals the number of behavioural
  requirements.
- **AC coverage is complete:** every `AC-n` in the requirements file's
  `source:` lines appears on a `Covers:` line of a group that has at
  least one test case or structural line. `reconcile_counts.py` prints
  the ledger sets; the Statistics `AC coverage:` line states
  `<n>/<N>` and names any uncovered id with the reason grooming gave.
  An AC item with no case and no structural line is a 🔴 for the
  analyzer — the whole point of the ledger.
- Every High-risk REQ group's `Applied techniques:` line names at
  least one extended technique (3-value BVA, Decision Table, invalid
  transitions, Pairwise) OR carries a one-line reason none applies
  (e.g. "no constraints, no states, 2 parameters").

If a problem is found, fix it before saving.

## Output file

Create `<ISSUEKEY>-test-cases.md` in the run folder
(`runs/<ISSUEKEY>/docs/`) and report its path. The next stage picks
it up from there.

If the file already exists, delete it completely and create a new one.
The output is always a single file with the result of the last run. Do
not merge with the previous version, do not append, do not keep data
from the previous write.

Before finishing, verify: one top-level heading; one coherent document
with no duplicated sections; the Structural checks section (if any)
sits after the last `## REQ-N` group and before Statistics.

The file structure template is in `references/output-template.md`. An
example of the level of detail is in `references/test-cases-example.md`.
The rules for techniques and coverage are in
`references/test-case-design-rules.md`; the decomposition method in
`references/check-decomposition.md`.

## Formatting (scan-friendly)

The test-cases file is read by the code phase (which maps each block to
a QA Service case) and rendered card by card in the manual walk. Format
for easy scanning in both:

- Do NOT use wide markdown tables (`| # | Step | ... |`). Wide rows do
  not survive the mapping to a case's `detail.steps` or a chat card.
- Use a vertical block layout per test case (the exact shape is in
  `references/output-template.md`): a `### TC-REQ-N.M — <name>` heading,
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
- Channel tags go on BOTH the requirement group heading — the union of
  its cases' tags (`## REQ-N — <label>  [UI] [API]`) — and on each
  test-case heading with exactly ONE tag
  (`### TC-REQ-N.M — <name>  [UI]`), with the single exception of
  provenance-sensitive cases, which carry the dual `[API][UI]` tag
  (Step 1). The per-case tag is what the executing stages route on.
- The core case's heading carries ` [core]` after its channel tag
  (`### TC-REQ-N.M — <name>  [UI] [core]`). `[core]` is a selection
  marker for stage 9, not a channel — routing ignores it.

## Final response

After the file is saved, report: the path; the counts from the
statistics block (cases, per channel, core, structural checks,
requirements needing clarification); and any requirement that was
written in two versions.
