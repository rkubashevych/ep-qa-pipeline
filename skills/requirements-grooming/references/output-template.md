# <ISSUEKEY> - Requirements

Context: <path to the context file>
Ticket type: <Story | Task | Bug | Sub-task — from the context file's Fields section>
Generated: <YYYY-MM-DD>
Skill: <the line `skill_stamp.py requirements-grooming` prints>

## Goal
<short expected outcome of the task — from the context file, unchanged>

> Notes (optional): carry forward any warning from the context file
> (e.g. "⚠️ No Confluence acceptance-criteria page linked") or any
> conflict left unresolved during grooming. Omit if there are none.

## Requirements

- REQ-1: [risk: Medium] <requirement text>
  - source: AC-1
- REQ-2: [risk: High] <requirement text>
  - source: AC-2, JD-1 — <document containing the whole statement>
- REQ-3: [risk: Low] <requirement text — mark "(unresolved conflict)"
  if it still holds two contradictory versions>
  - source: AC-3
- REQ-4: [risk: Medium] <core clause every source states>
  - source: AC-4 — <spec of record>
  - ⚠ extra clause "<the clause>" — stated ONLY in <source>. Not in
    <spec of record>. Testable as a pass/fail only if <owner> confirms
    it.
- REQ-5: [risk: Low] <comment-derived requirement>
  - source: CM-1
- REQ-6: [risk: High] Risk: <the consequence the material names, e.g.
  "amounts in different currencies are silently added into one
  meaningless total"> — only when the material names the hazard; see
  SKILL "Risk requirements"
  - source: CM-5
  - mitigated by: REQ-4

AC coverage: <n>/<N> AC items mapped< · SB <n>/<N> — only when the context has SB-n items>< · TS <n>/<N> — only when it has TS-n items> · JD <n>/<N> · CM <n>/<N><; uncovered: AC-<k> — <reason>>

## Open findings
> The findings the user did not settle (skipped, or auto-default mode),
> one line each in the "Finding codes" line shape, grouped under the
> chat categories. Not requirements and never a source of cases: stage
> 4 reads them only to know which REQs carry an open question (its
> Notes line). An open finding alone does NOT make a REQ "needing
> clarification" — that count is for unresolved conflicts and REQs
> marked "(needs clarification)" above. Omit the section when every
> finding was settled.

### Questions
- REQ-3 AMBIGUOUS (SPEC): <essence> — a tester reading this would <consequence> → <what is needed>
