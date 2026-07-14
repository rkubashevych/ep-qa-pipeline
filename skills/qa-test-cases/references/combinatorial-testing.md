# Combinatorial (pairwise) test generation

When a behavioural requirement depends on the COMBINATION of three or
more parameters (role × event type × setting is the classic EP shape),
do not hand-derive the combinations and do not enumerate all of them.
Generate a pairwise set with `scripts/generate_pict_cases.py`.

## When to use

- The requirement names 3+ parameters whose values interact (the
  expected behaviour changes depending on the combination, not just on
  each parameter independently).
- Each parameter has a small closed set of values that comes FROM THE
  REQUIREMENT TEXT (roles, event types, toggles, plan tiers, locales).

When NOT to use:

- 2 parameters — a decision table or plain EP cases are cheaper.
- Values not named in the requirement — do not invent axes. If a
  needed value set is missing from the requirement, that is a
  clarification question, not a modelling decision.
- Continuous ranges — that is BVA, not pairwise.

## How

1. Build a model file. One line per parameter, values comma-separated,
   only values grounded in the requirement (anything illustrative is
   marked `[test data]` later, in the TC itself):

   ```
   # REQ-5 — badge printing availability
   Role: Admin, Organizer, Exhibitor
   EventType: Hybrid, Virtual, InPerson
   Printing: On, Off
   ```

2. Run the script (no dependencies; uses the `pict` binary
   automatically when installed, needed only for constraint lines):

   ```
   python3 <skill dir>/scripts/generate_pict_cases.py model.txt
   ```

3. Turn each output row into one `### TC-REQ-N.M` block. The row's
   values go into `Pre:`/`Steps:` `[data: ...]`; the `Exp:` must
   follow from the requirement for THAT combination. If the expected
   result for a combination cannot be determined from the requirement
   text — drop that row and record the requirement as needing
   clarification (grounding rule, as usual).
4. Invalid combinations (e.g. a setting that cannot exist for a
   role): either add PICT constraint lines (requires the `pict`
   binary) or delete those rows manually and say so under the group
   heading.
5. In the group heading state the technique as
   `Applied techniques: Pairwise (PICT)` and add one line:
   `Model: <parameters> — N pairwise cases (exhaustive would be M)`.

## Rules

- The generated table is scaffolding, not the deliverable — the
  deliverable is still normal TC blocks that pass every rule in
  test-case-design-rules.md (grounding, no ambiguous words, one
  scenario per TC).
- Keep the model in the group heading's `Model:` line so a reviewer
  can regenerate the set.
- Default order is 2-wise. Use `--order 3` only when the requirement
  explicitly describes three-way interaction, and say why.
