# Checklist-building rules — reference

Sources: ISTQB CTFL v4.0, ISTQB CTAL-TA v4.0, and commonly
accepted requirements-based testing practices.

## What a checklist item is

By ISTQB, a test condition is an aspect or event of a component or
system that can be verified by one or more test cases. A checklist
item is an atomic test condition with an unambiguous expected result.

A checklist item answers the question: "what to check and what result
is expected". A test case (the next skill) answers "how to check".

## Quality attributes of an item

### Atomicity
One item = one check with one pass/fail.
"The button is visible and clickable" is two items.
If an item can be "partially pass", break it down further.

### Traceability
Each item has a REQ-ID. Each requirement has at least one item.
There are no items without a source and no requirements without
any check.

### Unambiguity
One interpretation. Any two people reading the item must reach the
same pass/fail conclusion.

### Self-containment
The item is understandable without opening the requirements file
and without the context of other items.

### Independence
An item can be checked on its own. Not "after REQ-1.2 is done the
results update", but "when a state is selected the results update".

### No duplication
The same check is not repeated across different items, even under
different REQ-IDs.

### Consistency
Elements of the same type get an identical base set of checks. The
difference is only in the specific checks on top of the base set.

## Wording rules

An item consists of two parts:
- What is being checked (element, state, behaviour)
- What the expected result is (value, state, text)

Both parts are mandatory. An item without an expected result is not
a check.

### Forbidden words

These make a check ambiguous — do not use them:
- "correctly", "properly", "in the appropriate way"
- "appropriate", "adequate", "acceptable"
- "as needed", "if necessary"
- "several", "some", "enough"
- "fast", "smoothly", "conveniently"
- "looks good", "works fine"

Instead, use a concrete value, state, text, or number.

## Decomposing a requirement into items

### The process by ISTQB

Test Analysis: requirement → test conditions (the aspects that need
to be checked). Each test condition becomes a checklist item.

For each requirement, determine in order:
1. Which elements or states the requirement describes
2. Which actions or behaviours the requirement describes
3. Which conditions or constraints the requirement describes
4. Whether there are dependencies on other requirements

Each item from steps 1-4 that has an unambiguous pass/fail becomes
a checklist item.

### Types of checks

Not every type applies to every requirement — generate only those
that follow from the specific requirement.

**Positive scenario** — the main behaviour works as described
(happy path). Always applicable.

**Negative scenario** — behaviour on invalid actions or data.
Only when the requirement describes interactivity.

**Boundary values** — behaviour at the boundaries. Only when the
requirement describes numeric or text constraints.

**Default state** — the initial state before user action. Only when
the requirement describes an element with an initial state.

**Element states** — visibility, being active, depending on
conditions. Only when the requirement describes conditional behaviour.

**State transitions** — a change of state on an action. Only when
the requirement describes a state change.

**Reset** — returning to the initial state. Only when the
requirement describes a reset or clearing.

**Validation** — rules and messages. Only when the requirement
describes validation.

**Data** — fields, formats, mappings. Only when the requirement
describes specific fields or data formats.

**Combinations of conditions** — behaviour under different
combinations. Only when the requirement contains several
independent conditions.

**UI conformance** — labels, texts, placement. Only when the
requirement describes a specific text or position.

### Checks at the seams between requirements

After decomposing each requirement on its own, check groups of
related requirements. At the seams between requirements there can
be checks that are not visible when decomposing a single requirement:
dependencies, conflicts, shared states.

## Sufficiency criterion

### Sufficient when
- Every requirement has at least one check
- Every item has exactly one pass/fail
- Every item is understandable without the context of other items
- Elements of the same type have the same base set

### Excessive when
- Items duplicate one another in other words
- 10+ items for a simple requirement with one element and one behaviour
- An item checks a detail that is not in the requirement

## Base set for typical elements

The minimal scope for typical UI elements. Use it as a starting
point — generate only the items that follow from the specific
requirement.

**Select:** presence → element type → options → default state →
main action → reset

**Input field:** presence → field type → label → placeholder
(if any) → default value (if any) → validation (if described) →
constraints (if described)

**Button:** presence → text → action on click → states and
transition conditions

**Table / list:** presence → columns/fields → data is displayed →
sorting (if any) → pagination (if any) → empty state

## Filtering out unnecessary checks

Do not generate checks for:
- standard browser or platform behaviour
- implementation details (architecture, cache, libraries)
- general infrastructure (server errors, timeouts)
- boundary values where the requirement describes no constraints
- negative scenarios for requirements without interactivity
- UX details (animations, timings, hover) not described in the requirement
- checks for behaviour that is not in the requirements

## Anti-patterns

**Duplication through rephrasing.**
"The Save button is present" and "The Save button is displayed" —
one item twice. Remove the duplicate.

**Implementation instead of behaviour.**
"The API returns 200", "The component uses useEffect" — the checklist
checks behaviour for the user, not implementation details.

**Non-atomic item.**
"The filter is present and when selected filters the results" —
two items: presence + filtering. Break it down.

**Dependent item.**
"After REQ-1.2 is done the results update" — the item must be
self-contained.

**Invented check.**
"The list loads in 2 seconds" — if the requirement does not describe
performance, there should be no such item.

**Ambiguous wording.**
"Filtering works correctly" — what does "correctly" mean? Instead:
"Selecting the state California displays only leads from the state
California".
