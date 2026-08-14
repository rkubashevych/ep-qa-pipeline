# Test-case building rules — reference

**Contents:** Choosing a technique by requirement type · Coverage
levels (risk-scaled) · Core selection rule · Mandatory attributes ·
Quality rules · EP rules · BVA rules · State Transition rules ·
Decision Table rules · Pairwise rules · Anti-patterns

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

## Coverage levels — risk-scaled (machine default)

Depth follows the requirement's `[risk: …]` marker (assigned at
grooming, carried on the checklist heading). The machine stages run
every generated case; the human walks a selection (see "Core selection
rule") — so depth is spent where risk lives, not everywhere.

**Standard — the baseline; applies to Medium-risk requirements:**
- The main scenario (happy path)
- Invalid partitions (where present in the requirements)
- Boundary values, 2-value BVA (where there are constraints in the
  requirements)
- Alternative and exception scenarios (where described)
- Valid state transitions (where there are states)

**High risk — Standard plus** (each item only where its precondition
exists in the requirement text; the grounding rule always applies):
- 3-value BVA (where there are constraints)
- Invalid state transitions (where states exist)
- Collapsed Decision Table (where 2+ conditions combine)
- Pairwise, 2-wise (where 3+ closed-set parameters interact — per
  combinatorial-testing.md, never exhaustive)

**Low risk — reduced:**
- The main scenario (happy path)
- Explicitly stated constraints only (a written limit still gets its
  boundary case); no alternative-flow or transition cases

**Extended (only if the user explicitly asks):** the High-risk depth
applied to every requirement regardless of risk.

Rules that hold at EVERY depth: EP one-representative-per-class (depth
comes from more techniques, never from duplicate cases in one class);
BVA only where constraints are written; pairwise is generated, never
enumerated exhaustively; every anti-pattern below.

## Core selection rule (the human tier)

Mark exactly ONE test case per behavioural requirement as the core
case: append ` [core]` to its `### TC-REQ-N.M` heading, after the
channel tag. The core case is the row a human always walks in the
stage-9 run sheet — even when the machine settled the requirement —
so the manual run touches every AC. Pick the case whose failure would
hurt most, in this preference order:

1. the riskiest invalid partition or denial path, if one exists;
2. else the version-A case of an unresolved conflict;
3. else the boundary case at a stated limit;
4. else the happy path.

Structural requirements (checklist-only, no test case) have no core
case. Zero or two `[core]` cases on one requirement is an error — the
verification step counts them. `[core]` is a selection marker, not a
channel: api-/web-testing routing ignores it.

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

## Pairwise rules

- Use for 3+ interacting parameters with closed value sets named in
  the requirement. Generate with the skill's
  `scripts/generate_pict_cases.py` (see
  references/combinatorial-testing.md) — do not hand-derive and do
  not enumerate exhaustively.
- Every generated combination still needs a grounded expected result;
  a row whose expected result cannot be determined from the
  requirement is dropped and the requirement flagged for
  clarification.
- Record the model on a `Model:` line in the requirement group
  heading so the set is reproducible.

## Anti-patterns (prohibited)

- Test case without an expected result → do not generate
- Ambiguous wording in the requirement → do not generate a test
  case, mark that the requirement needs clarification
- Two test cases from the same EP class → remove the duplicate
- Test case for behaviour not present in the requirement → do not generate
- Test case without a REQ-ID → do not generate
