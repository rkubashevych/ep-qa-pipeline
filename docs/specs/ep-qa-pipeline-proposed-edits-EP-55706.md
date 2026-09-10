# ep-qa-pipeline — proposed edits, EP-55706 run

Companion to `ep-qa-pipeline-retrospective-EP-55706.md`. Anchored to **section headings**, not line
numbers, matching the convention of `ep-qa-pipeline-proposed-edits.md` (which uses letters A–D; this
file starts at **E** so both can be read together without collision).

Two changes: **E. source fidelity in the docs phase** — stop the error being created — and
**F. source fidelity in the code phase** — catch it if it is. E is the real fix; F is the net.

Both are small. E is one paragraph plus a field-format change. F is one lookup on a bounded subset
of cases, plus three classification lines that cost nothing at runtime.

---

## E. Stop grooming from merging sources

### The problem in one artifact

`GSRCH-RULE-18`, as published by this run:

> **statement:** Every card in the News section has the same width and height as every other News
> card, **and no News card is larger than the result cards of the other category sections on the
> same page.**
>
> **source:** Confluence P2 2018639874 item 4 **and its acceptance criteria**, and design sub-task
> EP-55708 item 2

Clause 1 is from the AC page. Clause 2 is from EP-55708 **only** — the AC page does not contain it,
and neither does EP-55973, the sub-task that was actually built. The `source` line asserts that both
sources support the whole statement. They do not, and nothing downstream can tell.

The sources here do not **contradict** — they **differ in scope**: one says strictly more than the
other. `## Grooming method` question 4 covers contradictions and has no instruction for this, so the
stage merged, which is the reasonable reading of what it was told.

### E1 — `requirements-grooming/SKILL.md`, section `## Grooming method`, question 4

Add a fifth bullet under **"4. What is not specified?"**, after the existing
*"Contradictions between requirements in the context file"* bullet:

```markdown
  - **Sources that differ in scope (not just in content).** When two sources
    describe the same requirement and one says *strictly more* than the other —
    an extra clause, a wider comparison, an added condition — this is NOT a
    contradiction and must not be resolved by merging them into one statement.
    Two sources agreeing on a core and differing on a clause is the single
    easiest way to publish a requirement the acceptance criteria do not
    contain. Split it instead:
      - the clause every source carries → the requirement;
      - each extra clause → its own numbered requirement, or an explicit
        `(unresolved conflict)` marker, attributed to the one source that
        states it;
      - and record which source is the **spec of record**. Where a Confluence
        acceptance-criteria page exists, it outranks a design sub-task and an
        implementing sub-task outranks an earlier brief, unless the ticket says
        otherwise. State the ranking you used — never leave it implied.
    A brief that was later superseded by an AC page is the classic case: its
    extra sentences are intent, not acceptance. Both are worth recording; only
    one is testable as a pass/fail.
```

### E2 — `requirements-grooming/SKILL.md`, section `### Application rules`

Add one rule at the end of the list:

```markdown
- **A requirement statement may cite only sources that support all of it.** If
  you cannot point at one document containing the whole statement, the
  statement spans sources and must be split per E1. This is a hard check, not
  a judgement call: read your own `source` string back and confirm each named
  document really contains every clause you wrote.
```

### E3 — `qa-pipeline-docs/references/qa-service-publish.md`, requirement `detail` table

The `source` field is currently specified as:

> `source` (the AC page or ticket it came from)

**Singular** — which is what invited the merge. Replace with:

```markdown
`source` — the document containing the WHOLE statement. If more than one
document is involved, attribute per clause and mark the spec of record, e.g.
`spec of record: Confluence P2 2018639874 item 4 + AC. Clause "no larger than
other result cards": design sub-task EP-55708 item 2 ONLY — not in the AC page,
not in EP-55973.` A bare list of documents joined by "and" is not acceptable:
it asserts that all of them support all of the statement.
```

### E4 — `requirements-grooming/references/output-template.md`, `## Requirements`

Extend the example list so per-clause attribution has somewhere to live:

```markdown
- REQ-1: [risk: Medium] <requirement text>
- REQ-2: [risk: High] <requirement text>
  - source: <document containing the whole statement>
- REQ-3: [risk: Low] <requirement text — mark "(unresolved conflict)"
  if it still holds two contradictory versions>
- REQ-4: [risk: Medium] <core clause every source states>
  - source: <spec of record>
  - ⚠ extra clause "<the clause>" — stated ONLY in <source>. Not in
    <spec of record>. Testable as a pass/fail only if <owner> confirms it.
```

### E5 — `requirements-grooming/SKILL.md`, section `## Grooming method`, question 4, last bullet

The established-suite comparison currently catches *"a rule flipped, a limit changed, an invariant
broken"*. It does not catch **mutual unsatisfiability**. Append:

```markdown
    Also check whether the new requirement and an established one can BOTH
    hold at once. Two rules that never contradict in wording can still be
    jointly unsatisfiable — EP-55706's REQ-20 ("no News card larger than the
    other sections' cards") against the established GSRCH-FR-08 ("each block's
    card matches that entity's listing-page card"): if every block inherits its
    listing card, the sizes are inherited and cannot be equalised. Neither rule
    is wrong; together they are impossible. Raise it as a Contradiction citing
    both sides.
```

---

## F. Catch it in the code phase if E fails

E prevents the error at creation. F assumes E will sometimes not fire — on an older ticket, a
suite requirement written before E shipped, or a case inherited from an earlier story.

### F1 — `code-review/SKILL.md`, new subsection under `## Review process`

Insert **before** `### What to look for in the code`:

```markdown
### Source fidelity — before judging the case, check the case is real

The code phase reads DERIVED test cases, never the acceptance criteria. A
requirement mis-derived upstream is therefore invisible to every later stage,
and this stage is the last one that still holds the tracker.

Before assigning FAIL — and for every `[risk: High]` case regardless of verdict
— confirm the case's asserted expectation actually appears in a source of
record:

1. Read the case's `source` / traceability (the suite requirement's `source`
   field, or the requirements file's source line).
2. Open the named acceptance-criteria page or ticket and find the sentence the
   case asserts. One fetch per distinct source, not per case — in practice a
   handful per run.
3. Also read the IMPLEMENTING sub-task's own acceptance criteria (you already
   have them from the PR/branch derivation). A clause present in the brief but
   absent from the sub-task that was built is the exact shape of the EP-55706
   defect.

If the asserted expectation is NOT in the source of record, or is present in
only one of several cited sources:
- classify the case **SPEC-DEFECT**, never FAIL;
- name which document does and does not carry the clause;
- say which version the code implements.

Scope deliberately: FAIL-bound cases and High-risk cases only. This is not a
re-grooming and you are not re-deriving requirements — you are confirming that
the sentence you are about to fail a build against exists.
```

### F2 — `web-testing/SKILL.md`, section `## Classification`, under `SPEC-DEFECT`

Stage 8 wrote the SPEC-DEFECT rationale in prose and filed FAIL anyway. Add, as a rule under the
existing `SPEC-DEFECT` definition:

```markdown
- **If you write the doubt, you must classify it.** If your own finding says
  the case's wording is what makes it fail — "the case should name the
  comparison section", "depends which element the tester picks", "the
  requirement doesn't state a maximum", "would pass under the other reading" —
  that IS the SPEC-DEFECT definition, and the row is SPEC-DEFECT, not FAIL.
  Do not record a FAIL and explain in the notes why it might not be one.
  A verdict that needs a caveat to survive is the caveat's verdict.
```

Mirror the same paragraph in `api-testing/SKILL.md` under its classification section.

### F3 — `qa-pipeline-code/SKILL.md`, step 7 (bug filing)

Add as the first bullet of step 7, before the knowledge-base / default paths:

```markdown
   - **Source gate — before drafting any bug.** For each confirmed bug, quote
     the sentence from the acceptance criteria (or the implementing sub-task)
     that the build violates, and put it in the draft's "Expected result". If
     you cannot find that sentence in a source of record, the finding is a
     SPEC-DEFECT or a product question — retract the FAIL per the supersede
     convention and raise it to the docs-phase owner instead of filing a Bug
     against a dev. Filing a defect against a requirement the team never agreed
     costs the dev's time and the QA function's credibility.
     If you find yourself drafting a "you may get pushed back on this" caveat
     into the bug, stop and run this gate — that caveat is the gate firing.
```

### F4 — `qa-pipeline-code/SKILL.md`, step 6 (human summary) and the results template

A code-read FAIL that never reached runtime confirmation is currently reported as BLOCKED, which
reads as "environment problem" rather than "unverified defect claim". Add to
`references/results-comment-template.md`, human-summary section:

```markdown
**Unverified defect claims** — list every case that arrived FAIL from code
review and ended BLOCKED, one line each, under this exact heading. These are
NOT blocked cases in the ordinary sense: a defect has been asserted from a code
read and never confirmed against the product. Say so plainly, and say what
would confirm it. Omit the section only when there are none.
```

Rationale: EP-53768 overturned **6 of 12** verdicts asserted from a code read alone. The base rate
is bad enough that these claims deserve their own heading rather than burial under "needs a human".

### F5 — `qa-run-analyzer/SKILL.md`, section `## What to check`

Add a seventh dimension after `### 6. Findings summary (Product)`:

```markdown
### 7. Source fidelity (Input) — is the premise true, not just consistent?

Every other check in this skill is a CONSISTENCY check: do the counts agree, is
traceability intact, does each case map to a requirement. Consistency cannot
detect a wrong premise propagated uniformly — it is the one property such an
error preserves. This dimension is the only one that looks outward.

For every FAIL / FAIL CONFIRMED, and every requirement marked High risk:
- does the requirement's `source` name a SINGLE document containing the whole
  statement? A source string joining two documents with "and" is a finding —
  flag it and name the clause that may not be covered.
- did any stage report a verdict against a clause absent from the implementing
  sub-task's acceptance criteria?
- do any two requirements in the suite fail to be jointly satisfiable (E5)?

Flag 🔴 when a published FAIL rests on a clause found in only one of several
cited sources. That is a retraction waiting to happen, and it is cheaper to
find here than after the bug is filed.
```

---

## Cost, honestly

| Edit | Cost per run | Catches |
|---|---|---|
| E1–E4 | grooming writes one extra line per multi-source requirement | the error at creation — the real fix |
| E5 | one comparison pass already partly performed | jointly-unsatisfiable rule pairs |
| F1 | a handful of `getConfluencePage` / `getJiraIssue` calls, FAIL-bound + High-risk only | the EP-55706 defect, at stage 6 |
| F2 | zero — pure classification | stage 8's near-miss, the cheapest of the lot |
| F3 | one quote per drafted bug | wrongly-typed Jira bugs |
| F4 | one section in a comment | unverified code-read claims reading as environment problems |
| F5 | one analyzer pass over a bounded set | anything E and F both miss |

**F2 first if only one ships.** It costs nothing, and on this run it alone would have produced the
right verdict — the reasoning was already written, only the label was wrong.

## Suggested order of work

1. **F2** — zero cost, immediate.
2. **E3** — one field definition; the single change that made the error invisible.
3. **E1 + E2 + E4** — the grooming rule and its output format, together.
4. **F1 + F3** — the code-phase net and the filing gate.
5. **F4 + F5** — reporting and the analyzer dimension.
6. **E5** — the satisfiability check; the most conceptual, least urgent.

## What these edits do NOT fix

The code phase still cannot verify a requirement it was never given a source for. Five of this
story's requirements have no acceptance criterion at all (REQ-15, 19, 24, 25 and REQ-12's
breakpoints) — they exist only on a frontend sub-task. F1 will report "no source of record" for
those, which is more honest than today, but it does not create the missing criteria. That remains a
shift-left problem the pipeline can surface and cannot solve.

---

## G. Stop publishing to shared tickets before the human has checked

Raised by the plugin owner during the EP-55706 run, in response to what the run actually did.

### What the current design does

`qa-pipeline-code` step 6 publishes results to Jira. Step 9 builds the run sheet. Stage 10 ingests
the human's verdicts. So **publication always precedes verification** — by design, not by accident.

Step 8 already half-recognises the problem: a ✅ PASS is held back from the story because
"automated verdicts are provisional (the creator's own base rates: ~half of machine results wrong)".
But an ❌ FAIL is published immediately, at full volume, to shared tickets — and a wrong FAIL costs
more than a wrong PASS, because it sends a named person to work on something.

### What it cost on this run

Published before any human looked at the product:

- a story comment tagging two people and asking them to decide **four** questions — **three of which
  the acceptance criteria already answered** (one was not even a disagreement: the build matched the
  AC exactly);
- **EP-56188**, a Bug filed against the frontend for a clause the acceptance criteria never
  contained;
- count verdicts that were invalid within hours (EP-56197);
- `TC-REQ-19.2` reported as browser-confirmed on an event where the control never appears at all.

Two retractions and a rewritten bug followed, all within 24 hours, all found by a human asking
questions — none by the pipeline.

**The `PROVISIONAL` label did not prevent any of it.** Nobody reads a verdict table and a tagged
request for decisions as provisional. Marking output tentative does not make readers treat it
tentatively; withholding it does.

### G1 — `qa-pipeline-code/SKILL.md`, step 6

Split the publish by audience, and gate the human-facing half:

```markdown
   **Publish in two waves. Only the first happens now.**

   **Wave 1 — now, agents only.** Post the machine archive comment(s). They
   are unreadable prose to a human, no one is tagged, and a resumed run needs
   them. Then post ONE short status comment on the QA sub-task, no verdicts:
   `QA automated pass complete — N cases, M settled by machine, K for manual.
   Results published after the manual round.`

   **Wave 2 — after `qa-manual-results` (stage 10).** The human summary, the
   story comment, the stage-verdict table and any request for a product
   decision. By then every verdict has either been confirmed by a human or
   retracted, and the summary states what IS rather than what the machine
   currently believes.

   **The exception, and it is narrow.** A finding may be published in wave 1
   if ALL of: it was confirmed at RUNTIME (not from a code read); it has
   evidence attached; and it blocks the manual round from proceeding. An
   environment fault that stops the tester working (this run: EP-56197)
   qualifies. A code-read FAIL never does.
```

### G2 — `qa-pipeline-code/SKILL.md`, step 7 (bug filing)

```markdown
   - **File after the manual round, not before** — same rule as step 6.
     A bug drafted from an automated verdict waits for the human to walk that
     case. The exception is identical and equally narrow: runtime-confirmed,
     evidenced, and blocking. Everything else goes into the run sheet as a row
     for the tester, and becomes a bug in stage 10 if it survives contact.
```

### G3 — `qa-pipeline-code/SKILL.md`, step 8 (handoff)

```markdown
   - **Never ask a named person for a decision before the manual round**, and
     never before the source-fidelity check in F1 has confirmed the question
     is real. On this run, three of four "product decisions" put to two people
     were already answered by the acceptance-criteria page. Asking a colleague
     to decide something the spec already decides is worse than not asking:
     it implies the spec is ambiguous when it is not.
```

### G4 — `qa-manual-results/SKILL.md`, step 4

Stage 10 becomes the first point at which anything human-facing is published, so it must now own the
full summary rather than a delta:

```markdown
- This stage posts the FIRST human-facing summary of the run (see
  qa-pipeline-code G1). Write it as the complete picture — verdict, stage
  table, confirmed bugs, what needs a human, what was not tested — not as a
  diff against a provisional comment, because no provisional comment was
  posted. Where the machine's verdict and the human's disagree, state the
  human's and note the machine's in one clause.
```

### What this costs

Feedback reaches the team later — by the length of the manual round. That is the trade, and it is
worth taking: the alternative is what this run did, which is fast feedback that then had to be
retracted twice.

It also removes the argument for `PROVISIONAL` as a safety device. Either a verdict is confirmed and
publishable, or it is not published. There is no third state that a busy reader honours.
