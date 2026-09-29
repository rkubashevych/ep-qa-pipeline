# <ISSUEKEY> - Requirements

Context: <path to the context file>
Generated: <YYYY-MM-DD>

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

AC coverage: <n>/<N> AC items mapped< · SB <n>/<N> — only when the context has SB-n items> · JD <n>/<N> · CM <n>/<N><; uncovered: AC-<k> — <reason>>
