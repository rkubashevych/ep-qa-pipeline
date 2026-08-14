# Jira writing style — the single home

Applies to EVERY human-facing text this pipeline writes into Jira:
bug descriptions, the human summary comment, story notes (QA passed /
QA failed), the grooming open-questions comment, stage-10 manual-result
write-backs, and any status line. Machine archives (fenced file dumps
for agents) are exempt — they are verbatim by design.

Templates own their SHAPE (which sections, which order — see
`bug-report-template.md` and `results-comment-template.md`). This file
owns the WORDS and the LIMITS. When a template and this file disagree
on tone or length, this file wins.

## Voice

- Verdict or point first, support after. Never restate the context
  before getting to it.
- Write for a PM/dev skimming Jira: plain words, no pipeline jargon
  ("checked against the code", not "stage 6").
- No filler: "it's worth noting", "importantly", "at its core",
  "when it comes to", "plays a crucial role".
- No fake-insight structures: "it's not just X — it's Y",
  "this isn't about X, it's about Y".
- Never the "**Bold term:** explanation" list pattern — say the thing
  in a sentence.
- No summary wrap-up at the end; end on the last piece of substance.
  When the text asks for something, end with the one concrete next
  step and nothing after it.
- Vary sentence length; use contractions; at most one em dash per
  comment.
- If a sentence would fit in a press release, rewrite it.
- Anything a reader must DO (repro steps, fix verification) is a
  numbered list. Cap any list at 5 items — past that, group or cut.
  (Repro steps are the one exception: up to 8.)

## Hard caps — what stops the wall of text

- **Bug summary field:** ≤ 120 characters, shape
  `[<area>] <symptom — what breaks, where>`. No trailing detail.
- **Steps to reproduce:** ≤ 8 numbered steps, one action each. Concrete
  data inline as `[data: …]`. More than 8 means the precondition
  belongs in Environment, not the steps.
- **Expected result:** the test case's `Exp:` block, verbatim. Nothing
  added.
- **Actual result:** ≤ 5 lines of what was OBSERVED (surface, value,
  screenshot reference). Code paths, file:line render chains and
  PR archaeology go in `Source` (≤ 2 lines) — a dev opens the code
  from there; the description is for recognising the defect.
- **Priority / any field cell:** one line. A trade-off worth
  explaining ("Low if X, Medium if Y") is one sentence, not a
  paragraph.
- **Comment paragraphs:** ≤ 4 lines each. Two short paragraphs beat
  one dense one.

## Section discipline — the skeleton is closed

- A bug description contains EXACTLY the skeleton's h3 sections
  (Environment · Steps to reproduce · Expected result · Actual
  result · Source) — no ad-hoc extras ("Secondary defect", "Note for
  triage", "Additional context").
- A second defect discovered while drafting = a second draft (one bug
  per root symptom, as ever), or — when it is genuinely the same
  root cause — one line inside Actual result, not its own section.
- A triage decision the team must make ("copy fix vs case fix") is
  ONE line at the end of Actual result, phrased as the choice.
- Same for comments: only the sections the template defines, and any
  section that would be empty is omitted, never filled with "none".

## Self-check before posting (delete, then send)

1. First line states the defect / verdict — not context.
2. Every cap above holds; no section outside the skeleton.
3. No filler phrase from the Voice list survives.
4. A reader who reads ONLY the first line and the section headings
   still knows what broke and where.
5. Credentials/tokens redacted; screenshots clean.
