# Decomposing requirements into checks — reference

**Contents:** Why this is a working step, not a file · What a check is ·
Quality attributes · Wording rules · Decomposing a requirement ·
Behavioural vs structural · Sufficiency criterion · Base set for
typical elements · Provenance-sensitive checks (dual tag) · Filtering
out unnecessary checks · Anti-patterns

Sources: ISTQB CTFL v4.0, ISTQB CTAL-TA v4.0, and commonly accepted
requirements-based testing practices.

## Why this is a working step, not a file

Until 0.40.0 this decomposition was its own stage (qa-checklist) with
its own file (`<ISSUEKEY>-checklist.md`), its own pause and its own
budget. Nothing downstream read that file for anything but its `[UI]`
structural lines: the test cases restated the behavioural checks, the
publish step turned the structural ones into STRUCT cases, and the
analyzer counted both. So the decomposition is now the **first working
step of qa-test-cases** — done in full, kept in the head (or a scratch
note), and written out as two things only: **test cases** for the
behavioural checks and the **Structural checks** section for the
structural ones. Nothing else survives to the file, and nothing is
lost — every check ends up in one of the two.

## What a check is

By ISTQB, a test condition is an aspect or event of a component or
system that can be verified by one or more test cases. A check is an
atomic test condition with an unambiguous expected result.

A check answers "what to check and what result is expected". A test
case answers "how to check". A structural check needs no "how" — it is
its own test case ("the label reads *State*").

## Quality attributes of a check

### Atomicity
One check = one pass/fail. "The button is visible and clickable" is
two checks. If a check can be "partially pass", break it down further.

### Traceability
Each check has a REQ-ID. Each requirement has at least one check.
There are no checks without a source and no requirements without any
check.

### Unambiguity
One interpretation. Any two people reading the check must reach the
same pass/fail conclusion.

### Self-containment
The check is understandable without opening the requirements file and
without the context of other checks.

### Independence
A check can be verified on its own. Not "after REQ-1.2 is done the
results update", but "when a state is selected the results update".

### No duplication
The same check is not repeated under different REQ-IDs or in other
words.

### Consistency
Elements of the same type get an identical base set of checks. The
difference is only in the specific checks on top of the base set.

## Wording rules

A check consists of two parts:
- What is being checked (element, state, behaviour)
- What the expected result is (value, state, text)

Both parts are mandatory. A check without an expected result is not a
check.

### Forbidden words

These make a check ambiguous — do not use them:
- "correctly", "properly", "in the appropriate way"
- "appropriate", "adequate", "acceptable"
- "as needed", "if necessary"
- "several", "some", "enough"
- "fast", "smoothly", "conveniently"
- "looks good", "works fine"

Instead, use a concrete value, state, text, or number.

## Decomposing a requirement

### The process by ISTQB

Test Analysis: requirement → test conditions (the aspects that need to
be checked). Each test condition becomes a check.

For each requirement, determine in order:
1. Which elements or states the requirement describes
2. Which actions or behaviours the requirement describes
3. Which conditions or constraints the requirement describes
4. Whether there are dependencies on other requirements

Each item from steps 1–4 that has an unambiguous pass/fail becomes a
check. Number them under the requirement — `REQ-3` → checks 3.1, 3.2 …
— so the test cases and the structural lines that follow inherit the
same REQ.

### Types of checks

Not every type applies to every requirement — generate only those that
follow from the specific requirement.

**Positive scenario** — the main behaviour works as described (happy
path). Always applicable.

**Negative scenario** — behaviour on invalid actions or data. Only when
the requirement describes interactivity.

**Boundary values** — behaviour at the boundaries. Only when the
requirement describes numeric or text constraints.

**Default state** — the initial state before user action. Only when the
requirement describes an element with an initial state.

**Element states** — visibility, being active, depending on
conditions. Only when the requirement describes conditional behaviour.

**State transitions** — a change of state on an action. Only when the
requirement describes a state change.

**Reset** — returning to the initial state. Only when the requirement
describes a reset or clearing.

**Validation** — rules and messages. Only when the requirement
describes validation.

**Data** — fields, formats, mappings. Only when the requirement
describes specific fields or data formats.

**Combinations of conditions** — behaviour under different
combinations. Only when the requirement contains several independent
conditions.

**UI conformance** — labels, texts, placement. Only when the
requirement describes a specific text or position.

### Checks at the seams between requirements

After decomposing each requirement on its own, check groups of related
requirements. At the seams between requirements there can be checks
that are not visible when decomposing a single requirement:
dependencies, conflicts, shared states.

## Behavioural vs structural — where each check goes

Sort every check into one of two bins. The bin decides what it becomes
in the file.

**Structural** — the check reads a static property of the surface and
needs no scenario to verify: an element is present, its label or
placeholder text, its type (select / input / button), its default
state before any action, its position relative to another element. It
becomes **one line in the `## Structural checks` section** —
`- [ ] REQ-N/struct-k [UI] <check>` — and, at publish, one
`<PREFIX>-STRUCT-NN` case in the suite. No `TC-` block, no `[core]`.

**Behavioural** — everything else: an action produces a result, a
state changes, a rule filters or validates, a field is returned with a
value, a limit is enforced. It becomes **one or more test cases**
(`### TC-REQ-N.M`) per the techniques in `test-case-design-rules.md`.

A requirement whose checks are *all* structural (REQ-3 "the label is
displayed above the select") is a structural requirement: it has lines
in the Structural checks section and no test-case group. A requirement
that mixes both (a toggle that exists, defaults to OFF, and when ON
shows a badge) has both — its structural lines under its REQ id in the
section, its behavioural cases in its `## REQ-N` group. Only
behavioural requirements get a `[core]` case; the "core count =
behavioural requirements" rule in the statistics counts on it.

Structural checks are `[UI]` by nature. An `[API]` "the field is
present in the response" check is behavioural — it needs a call — and
becomes a test case.

## Sufficiency criterion

### Sufficient when
- Every requirement has at least one check
- Every check has exactly one pass/fail
- Every check is understandable without the context of other checks
- Elements of the same type have the same base set

### Excessive when
- Checks duplicate one another in other words
- 10+ checks for a simple requirement with one element and one behaviour
- A check verifies a detail that is not in the requirement

## Base set for typical elements

The minimal scope for typical UI elements. Use it as a starting point —
generate only the checks that follow from the specific requirement.
The first items of each set (presence, type, label, default) are the
structural ones; the rest are behavioural.

**Select:** presence → element type → options → default state →
main action → reset

**Input field:** presence → field type → label → placeholder (if any)
→ default value (if any) → validation (if described) → constraints
(if described)

**Button:** presence → text → action on click → states and transition
conditions

**Table / list:** presence → columns/fields → data is displayed →
sorting (if any) → pagination (if any) → empty state

## Provenance-sensitive checks — when one channel tag is not enough

A check whose expected result reads a **counter, lead, analytics,
statistics, notification, or dashboard** surface cannot be proven by an
API call alone: actions performed over the API frequently never enter
client-side tracking, so the surface stays clean whether the feature
works or not (this produced a false pass on a privacy requirement in a
real run). For these checks:

- Tag them `[API][UI]` (dual tag) rather than forcing a single channel.
  The API half can exercise the call; only the browser half can read
  the instrumented surface against UI-created data.
- For absence checks ("nothing appears", "count stays 0"), word the
  check so it names its positive control — the thing that proves the
  surface CAN show data ("counter reads 1 for the public favourite AND
  0 for the private one"), not a bare "nothing appears".
- Remember the tag is assigned blind (this stage must not inspect code
  or system). It is a routing hint, not a verdict about where the
  behaviour lives — code review may re-route it after seeing the code.

## Filtering out unnecessary checks

Do not generate checks for:
- standard browser or platform behaviour
- implementation details (architecture, cache, libraries)
- general infrastructure (server errors, timeouts)
- boundary values where the requirement describes no constraints
- negative scenarios for requirements without interactivity
- UX details (animations, timings, hover) not described in the requirement
- behaviour that is not in the requirements

## Anti-patterns

**Duplication through rephrasing.**
"The Save button is present" and "The Save button is displayed" — one
check twice. Remove the duplicate.

**Implementation instead of behaviour.**
"The API returns 200", "The component uses useEffect" — a check
verifies behaviour for the user, not implementation details.

**Non-atomic check.**
"The filter is present and when selected filters the results" — two
checks: presence (structural) + filtering (behavioural). Break it down.

**Dependent check.**
"After REQ-1.2 is done the results update" — the check must be
self-contained.

**Invented check.**
"The list loads in 2 seconds" — if the requirement does not describe
performance, there should be no such check.

**Ambiguous wording.**
"Filtering works correctly" — what does "correctly" mean? Instead:
"Selecting the state California displays only leads from the state
California".

**A structural check dressed as a scenario.**
"TC: open the page, locate the State select, verify the label reads
State" — three steps to read one static property. It is a structural
line, not a test case; writing it as a case inflates the count and
gives stage 9 a card nobody needs to walk.
