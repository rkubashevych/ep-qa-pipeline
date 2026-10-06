# Jira writing style — the single home

Applies to EVERY human-facing text this pipeline writes into Jira:
bug descriptions, the human summary comment, story notes (QA passed /
QA failed), the grooming open-questions comment, stage-10 manual-result
write-backs, and any status line. (Nothing machine-only is written to
Jira since 0.33.0 — there is no exempt text.)

Templates own their SHAPE (which sections, which order — see
`bug-report-template.md` and `results-comment-template.md`). This file
owns the WORDS and the LIMITS. When a template and this file disagree
on tone or length, this file wins; on CONTENT (which sections exist and
what goes in them) the template wins.

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
- **Expected result:** the register clause the build violates, quoted
  verbatim and led by its `AC-<n>` (`bug-report-template.md`). Never
  the test case's `Exp:` block — a test case is not a source of record;
  its `Exp:` goes in the Source section.
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

## Grooming open-questions comment — questions only (0.45.0)

This comment comes from `qa-pipeline-docs` step 2 and from
`qa-refinement`. Its readers are the PM and the devs, and they answer
questions. The evidence behind each question is for QA and already
lives in the run folder (`-recon.md`, `-requirements.md`).

The shape is closed:
- **One intro line:** `QA questions before <estimation | test design>
  (<QA sub-task key if any>):`.
- **A numbered list**, one question per item, one line each. It holds
  at most a short clause of context that names the two sides:
  "(AC) or … (FE)?", "Confluence §3 still says no."
- **No** section headers, file:line references, recon narrative,
  "checked on alpha" provenance, or wrap-up line.
- The 5-item list cap does not apply, because each item is one
  sentence. Past 15 items, cut the least testable ones rather than
  group them.

The first version on EP-56227 (2026-09-29) had four headed sections
and two-line evidence per item. The user replaced it with "post the
questions without the noise, just questions". The comment was edited
in place (150682).

**What earns a place: only a question that blocks a test case.** A
question belongs in the comment only when its answer changes an
expected result, a precondition, or whether a case exists. Name the
REQ it blocks in `<KEY>-open-questions.md` (not in the comment); an
item with no REQ to name is cut.

Never ask:
- **Planning:** environment, dates, owners, who estimates. EP-56227 Q15
  ("which environment and date") was, in the user's words, "not
  needed".
- **What the spec already answers.** Q14 asked whether QA covers the
  API and admin Display Filters, when the AC has sections for both.
  Read the AC first.
- **Meta-requests:** "please fill in the description", "confirm the
  above". Q11 got "Answered above". Ask the questions themselves.

**Write it so a PM can answer it without opening the code.** Of the 15
EP-56227 questions, one was answered as a different question and two
came back as "not clear" or bounced to QA. All three used words only
the pipeline knew.

1. **One decision per question**, with the two outcomes spelled out as
   something the attendee or organiser would see: "should results show
   only items on the hall itself, or the hall plus all its stands?"
   Every question built that way came back with a clean answer.
2. **Name every setting by where it lives and what it does today.**
   Write `Categorisation → "Search Within Filters" (today, category
   filters show search only when it's on)`, never a bare setting name.
   Q3 bounced back to QA for exactly this.
3. **Give a mismatch a concrete example of what the user sees.** Say
   what shows, where, and when: "with X off, the card shows 'Office' but
   the filter doesn't list 'Office'". Q12 used only the internal terms
   and got "Question is not clear".
4. **No pipeline or code vocabulary:** "free-text", "parent rows",
   "indeterminate", "scope", field names. Use the words on the screen.
   A comment id (150524) is fine as a pointer, but never as the only
   context. Q9 said "free-text custom locations" and was answered as a
   question about something else.

**Every name in the comment is a checked name (0.47.1).** Rules 2 and
4 say to use the words on the screen. Without a check, a draft still
borrows names from the spec, the code or an RFC. On EP-55996
(2026-10-06), the first draft of the re-validated comment had four
wrong names, and every one came from a source other than the product:
- "Matchmaking sorting on Marketplace" under Registration Settings →
  Exhibitor → Additional Settings: copied from the spec. The page has
  no such toggle. The real one is Networking & Matchmaking →
  Matchmaking → 'Use "Recommendation For You" by default on the
  Marketplace and Delegate pages'.
- "Exhibitor categories": also from the spec. The page is Registration
  Settings → Exhibitor → Participant Categories, column "Search
  Weight".
- "search with ElasticSearch off": the page's own help text says
  "regular search".
- "weak matches": the RFC's word, with no example.

The 10 Sep original of the same comment said "the switch's screen" and
"the existing AI switch". The story's EM answered it with "which
screen? if it's settings, say so". Only a browser pass found the
errors.

So `<KEY>-open-questions.md` carries a **`## Names`** table, one row
per page, menu path, tab, toggle, field, button, column or message the
draft names:

| Name as written | What it is | Source |
|---|---|---|
| Networking & Matchmaking → Search | sidebar section → page | screen, api-alpha2, 2026-10-06 |
| "Use ElasticSearch" | toggle on that page | label, monolith `backend/admin/views/search/main.volt:16` |

- **Source is one of two kinds:**
  - `screen <host> <date>`: seen in the running product during
    recon;
  - `label <repo> <file:line>`: the view or translation file that
    renders the text, on the integration branch. A label is enough
    for a single control on a known page. A menu path, or a setting
    that two views render, needs `screen`.
- **A spec, an RFC, a ticket or a Confluence page is never a source
  for a name.** They are sources of intent, and they get labels
  wrong. Write `spec only` and check it before posting:
  - a recon labels pass (`../../qa-pipeline/references/recon.md` →
    "Labels pass"), or a label-file lookup;
  - or describe the thing by what the user sees ("the number on the
    Exhibitors tab") instead of naming it.
- **A thing the product does not have yet** has no on-screen name. An
  example is a setting an RFC proposes. Call it what the proposal
  calls it, attribute it ("RFC-0010 proposes a dropdown …"), and give
  its row the source `proposed — <doc>`.
- **The path counts as well as the label.** "Exhibitor categories"
  was the right idea on the wrong page. Record the whole path, section
  → page → tab, the way the sidebar and tab strip show it.
- **Pre-post check:** every bolded or quoted name in the draft has a
  row. No row says `spec only`. Every RFC or contract word that
  appears nowhere on screen ("weak", "engine", "index", "reader") is
  explained with an example of what the user would see.

**Answers come back in two places.** Read both before calling anything
open:
- replies under the comment;
- edits to the ticket description. EP-56227's PM answered inline in
  the description and left only "Answered in description" as a
  comment.

Classify each answer in `<KEY>-answers.md` as one of:
- **answered**;
- **partial**;
- **answered a different question** — record what can be inferred and
  mark it "inferred";
- **not clear to them**;
- **not needed**.

Only "not clear" and the unanswered part of a "partial" answer go into
a follow-up, rewritten by the four rules above. Never re-ask an
answered question.

**Re-runs.**
- When nobody has answered yet, edit the comment in place. Keep its id
  on the `Comment:` line of `<KEY>-open-questions.md`.
- Once answers exist (as replies or in the description), post a new
  comment with only the follow-ups (`Follow-up on the QA questions —
  rephrased:`) and leave the original alone.

## Self-check before posting (delete, then send)

1. First line states the defect / verdict — not context.
2. Every cap above holds; no section outside the skeleton.
3. No filler phrase from the Voice list survives.
4. A reader who reads ONLY the first line and the section headings
   still knows what broke and where.
5. Credentials/tokens redacted; screenshots clean.
