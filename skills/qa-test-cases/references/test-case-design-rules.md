# Test-case building rules — reference

## Choosing a technique by requirement type

| Nature of the requirement | Technique | Coverage criterion |
|---------------------------|-----------|--------------------|
| Ranges, limits, numeric constraints | EP + BVA | Every partition + every boundary value covered |
| Categories of input data without numeric bounds | EP | Every partition (valid and invalid) covered |
| Several conditions → different actions | Decision Table | Every rule (combination of conditions) covered |
| An object with statuses/modes | State Transition | Every valid transition covered |
| A full user scenario | Use Case | Main + alternative + exception scenarios |
| Many parameters with different values | Pairwise | Every pair of values of any two parameters covered |

Techniques combine: one requirement may need both a Use Case (for the
flow), EP+BVA (for input fields), and State Transition (for statuses).

## Coverage levels

**Standard (the default for every task):**
- The main scenario (happy path)
- Invalid partitions (where present in the requirements)
- Boundary values, 2-value BVA (where there are constraints in the
  requirements)
- Alternative and exception scenarios (where described)
- Valid state transitions (where there are states)

**Extended (only if the user explicitly asks):**
- 3-value BVA
- Decision Table for complex business logic
- Invalid state transitions
- Pairwise for forms with 3+ parameters

## Mandatory attributes of each test case

- Identifier (TC-REQ-N.N)
- Scenario name
- Precondition
- Steps with input data
- Expected result for each meaningful step
- Postcondition — only if the system state changes

The test-design technique is stated once in the heading of the
test-case group for the requirement, not in each test case separately.

## Quality rules

**Precision.** One interpretation. Forbidden words in expected
results: "correctly", "properly", "appropriate", "as needed",
"in the appropriate way", "several". Instead, use a concrete value,
state, or behaviour.

**Completeness.** A test case without an expected result is not a
test case. Do not generate it.

**Traceability.** Each test case is tied to a REQ-ID. Each
behavioural requirement has at least one test case.

**Conciseness.** One test case = one scenario with one verification
focus. Do not combine several independent checks into one test case.

## EP rules

- One representative from each class is sufficient. Do not generate
  several test cases from the same class.
- Each invalid partition is a separate test case. Do not combine
  several invalid values in one case.

## BVA rules

- Apply only when the requirement has explicit numeric or text
  constraints (min/max, length, count).
- By default 2-value: the boundary + the nearest neighbour from the
  adjacent partition.
- Do not generate BVA if the requirement has no constraints.

## State Transition rules

- A transition test case = a sequence of events that leads through
  several states. One test case can cover several transitions.
- Test invalid transitions only if the requirement explicitly
  describes forbidden transitions.

## Decision Table rules

- Use a collapsed (simplified) table: if the value of a condition
  does not affect the action, merge the rules.
- Do not generate a full enumeration if some combinations produce
  the same behaviour.

## Anti-patterns (prohibited)

- Test case without an expected result → do not generate
- Ambiguous wording in the requirement → do not generate a test
  case, mark that the requirement needs clarification
- Two test cases from the same EP class → remove the duplicate
- Test case for behaviour not present in the requirement → do not generate
- Test case without a REQ-ID → do not generate
