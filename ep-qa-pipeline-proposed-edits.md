# ep-qa-pipeline — proposed edits, ready to drop in

Companion to `ep-qa-pipeline-retrospective-EP-47675.md`. Each block below is
anchored to a **section heading** rather than a line number, because headings
survive edits and line numbers do not.

Three changes here: **A. walk sheet first** (parallel human testing, and better
evidence), **B. progress reporting**, **D. candidate defects and co-reproduction
before filing**. Then the cosmetic list (**C**) with effort tags.

---

## A. Walk sheet first

### Why this is more than a time saving

Today `qa-manual-runsheet` runs at stage 9 and builds the sheet **from** the
machine's verdicts. The human therefore sees `FAIL CONFIRMED` before touching
the page. That is not an independent observation, it is a confirmation request.

On EP-47675 the machine's UI stage scored **54%**. Its verdicts were worth less
as a filter than an unprimed human walk is worth as evidence. Splitting the
sheet in two buys parallel time *and* removes the priming.

It also removes the conditions that produced the 30-row cascade: a human who has
not been shown a chain of machine FAILs is much less likely to write one.

### A1 — new file: `qa-manual-runsheet/references/walk-sheet-format.md`

Define a second output mode. Same skill, different emission point and a strictly
smaller column set.

```markdown
# Walk sheet (stage 5.5) — format

The walk sheet is the run sheet's EARLY sibling. It exists so a human can test
in parallel with the machine, and so their observations are independent of it.

## Hard rule

The walk sheet contains NO machine verdict, in any column, in any wording,
including "code review predicts", "expected to fail" and "known issue".
A tester must be able to reach a verdict from the case alone. The only
exception is a version-sibling flag (see below), because a tester who does not
know a case is a deliberate sibling will file a false bug.

## Columns, in this order

| Column | Notes |
|---|---|
| `TC` | join key, never reordered away |
| `Set` | `CORE` or `EXTENDED` — which side of the cut line (see below) |
| `Why` | the test-design technique that put this row in CORE, blank for EXTENDED |
| `Priority` | P0 / P1 / P2 |
| `Journey` | groups rows so a tester stays on one page |
| `Title` | |
| `Log in as` | exact credential, or `guest` |
| `Test data` | exact query token / record id |
| `Do` | numbered, imperative, one action per line |
| `Expect` | the assertion, and ONLY the assertion |
| `Console check` | optional paste-ready one-liner (see below) |
| `Result` | BLANK. dropdown: PASS / FAIL / BLOCKED / SKIPPED |
| `Notes` | BLANK |
| `Evidence` | BLANK — Jam or screenshot URL |

## The cut line

Every row is in the sheet. Nothing is hidden or dropped. But the sheet is
divided in two by a visible cut line, so a tester who has ninety minutes and a
tester who has a day both know what to do.

**Above the line — CORE.** The smallest set that still covers the behaviour
space, chosen by test-design technique, never by priority alone. Target size is
25 to 35 rows regardless of how large the suite is. If CORE exceeds 35, the
selection is not aggressive enough; go back and merge equivalence classes.

**Below the line — EXTENDED.** Everything else: near-duplicates, additional
members of a class already covered, and rows the machine can settle unaided.
Not junk, just lower marginal value per minute. The machine sweeps these in
parallel whether the human reaches them or not.

### How the divider renders

The cut line is a real row in the sheet, not a footnote. It spans the full
width, is filled a solid colour, has its text frozen visible, and reads:

> **⎯⎯ CUT LINE ⎯⎯  Everything ABOVE covers the whole behaviour space (31 rows,
> about 90 min). Stop here and the run is still meaningful. Everything BELOW is
> extra depth — near-duplicates of cases already above, which the machine is
> testing in parallel. Work down only if you have time.**

Repeat the same explanation in the `Today` tab header and in the run sheet's
`Legend` tab. A tester should never have to ask what the coloured row means,
and should never feel that stopping at it is quitting.

### How CORE is selected

By technique, and the technique is NAMED in the `Why` column so the choice is
auditable rather than a matter of taste:

| Technique | Applies to | Effect |
|---|---|---|
| Equivalence partitioning | query tokens, input values | one matching, one non-matching, one empty — not twelve variants of "a word that matches" |
| Boundary values | counters, caps, thresholds, pagination | the value at the cap and the value either side of it, nothing in between |
| Decision table | entitlement and permission matrices | one row per distinct outcome, not one per role × flag combination |
| Pairwise | combinatorial config (selector × auth state × query state) | all pairs covered without the full cross-product |
| State transition | open/close, expand/collapse, back-navigation families | each transition once, not each path through them |
| **Version siblings** | contested A/B requirements | **BOTH siblings always go in CORE. Never reduce a pair.** |

That last row is not negotiable. On EP-47675, EP-55937 was found only because
both mutually exclusive siblings failed, which means the build matched neither
documented reading. Reducing a pair to one member makes that class of defect
invisible by construction.

Two further rules for CORE membership, regardless of technique:

- Any case on a `[risk: High]` requirement goes in CORE.
- Any case whose only existing evidence is code reading goes in CORE, because a
  PASS that was never executed is not a PASS.

## Ordering

Within CORE, and again within EXTENDED, sort by journey so the tester stays on
one page at a time rather than being bounced between them. Priority breaks ties
inside a journey. Do not sort by priority across the whole sheet — it scatters a
tester across six pages to run six P0s.

## The `Console check` column

Where a case's assertion can be settled by a single browser-console
expression, supply it, ready to paste. EP-47675 demonstrated repeatedly that
a one-liner settles in seconds what clicking settles in minutes.

Rules: read-only, no `await` chains longer than one statement, and it must
print a value that maps directly onto the `Expect` column.

## Version siblings

Where a case is one of an A/B pair under a contested requirement, mark it
`SIBLING A of REQ-n` in `Do`. Do not say which one is expected to fail —
that is a machine prediction. Say only that a pair exists, so the tester
reports the observation rather than filing a bug.

## The `Today` tab

Sheet 1 is a single-screen view: only rows the human still has to run, in
order, with a tick column. Everything else lives on later tabs. A tester
should never scroll 118 rows to find their next job.

Its header carries the cut-line explanation and the live count:

> **CORE: 12 of 31 done · about 55 min left.** CORE is the smallest set that
> still covers the whole behaviour space. Finish CORE and the run is
> meaningful. EXTENDED (87 rows) is extra depth on cases CORE already covers —
> the machine is testing those in parallel, so only work down if you have time.

## Stage 9 must report the split

When the walk sheet comes back, the reconciliation sheet and the stage-10
report state CORE completion and EXTENDED completion separately. "31 of 31
CORE, 4 of 87 EXTENDED" is a well-executed run. A single blended "35 of 118"
reads as a third-finished run and is actively misleading about coverage.
```

### A2 — `qa-pipeline-code/SKILL.md`, section `## How it runs`

Insert a new numbered item **before** item 1 (pr-summary), and renumber:

```markdown
0. **environment probe + walk sheet (stage 5.5)** — runs BEFORE code review so
   the human can test in parallel with the machine.

   a. **Environment probe.** Ask the user for every candidate host. For each,
      record: hostname, event id, `data-version`, the module flags this story
      depends on, and one smoke query. Publish the matrix as
      `<STORY>-environments.md` and repeat it in the header of every later
      artifact. Then apply the standing rule for the rest of the run:
      **before recording BLOCKED, NOT TESTABLE or UNVERIFIABLE, check the case
      on every host in the matrix.**

   b. **Provision fixtures** — the accounts and data the cases need
      (qa-manual-runsheet steps 3 and 4, unchanged, just earlier).

   c. **Emit the walk sheet** — `<STORY>-walk-sheet.xlsx` per
      `../qa-manual-runsheet/references/walk-sheet-format.md`. No machine
      verdicts. Sorted by priority. Hand it to the user and say plainly:
      *"Start whenever you like, I'll work the machine stages in parallel and
      merge your results at stage 9."*

   d. **Do not block on it.** The human's walk and the machine's stages run
      concurrently. Stage 9 merges whatever the human has completed by then;
      unfinished rows stay open and are not treated as skipped.
```

### A3 — `qa-manual-runsheet/SKILL.md`, section `## Output`

Add:

```markdown
This skill has TWO emission modes.

- **Walk-sheet mode (stage 5.5)** — `<STORY>-walk-sheet.xlsx`, built from the
  test cases alone, before any machine verdict exists. Format:
  `references/walk-sheet-format.md`. Steps 1, 3, 4 and 5 of the workflow apply;
  step 2 (classify against machine verdicts) does not, because there are none.
- **Reconciliation mode (stage 9)** — `<STORY>-runsheet.xlsx`, the existing
  behaviour, plus: import the human's `Result` / `Notes` / `Evidence` columns
  from the walk sheet by TC id, and place the machine verdict BESIDE the
  human's rather than in place of it.

When both exist, stage 10 reads the human column as an INDEPENDENT observation
made without sight of the machine's, and says so in its report. That is
stronger evidence than a post-hoc agreement and should be described as such.
```

### A4 — `qa-manual-runsheet/SKILL.md`, section `## The six rules that make a run sheet usable`

Add a seventh:

```markdown
7. **Never show a tester a verdict they are about to produce.** In walk-sheet
   mode this is absolute. In reconciliation mode, the machine's column sits to
   the RIGHT of the human's and the sheet opens with the human's column in
   view. A tester who reads "FAIL CONFIRMED" before running the case is no
   longer an independent observer, and the run loses the only check it has on
   the machine's 54% UI accuracy.
```

### The trade-off, stated honestly

The human will walk some rows the machine would have settled in seconds. That is
the price of independence. The cut line is the mitigation: CORE is sized so that
stopping at it is a complete act rather than an abandoned one, and EXTENDED is
swept by the machine regardless of whether the human reaches it.

What this deliberately does NOT do is hide the EXTENDED rows. A filtered ~30-row
sheet would feel better to open and would quietly remove the only human check on
the 87 rows the machine judges alone — which, at the accuracy measured in the
retrospective, is exactly the wrong place to remove oversight.

---

## B. Progress reporting

### B1 — new file: `qa-pipeline-code/references/progress-protocol.md`

Supplied as a separate file alongside this one. Drop it in as-is.

### B2 — `qa-pipeline-code/SKILL.md`, section `## Between stages`

Add:

```markdown
Every stage that will process more than 15 items follows
`references/progress-protocol.md`: a heartbeat every 10 items or 5 minutes, a
`<STORY>-progress.md` file rewritten at each heartbeat, and — where
`TaskCreate` / `TaskUpdate` exist — one task per stage driven live.

The orchestrator creates the task list up front, one task per stage, so the
user can see the whole run's shape before it starts.
```

### B3 — one line in each of `code-review`, `api-testing`, `web-testing`, `qa-manual-results`, under `## Workflow`

```markdown
Follow `../qa-pipeline-code/references/progress-protocol.md` while working
through the case list. Stamp start time, end time and duration into this
stage's report header.
```

---

## D. Candidate defects, and co-reproduction before filing

### The problem

The skill already refuses to file silently — `qa-pipeline-code` step 7 requires
an explicit yes per bug. Two things are still wrong with it.

**It offers in bulk.** The current wording is *"make ONE offer listing all the
bugs"*. Presented with seven drafts at once, a human either rubber-stamps the
batch or stops the whole thing to ask for a repro. On EP-47675 the human did the
second, which was correct, and the skill had no step for it.

**It calls them confirmed before anyone has looked.** The status is literally
`FAIL CONFIRMED`. Measured accuracy of that status on this run was 54%: twelve
of the seventeen wrong calls were the product working correctly. A word that
means "settled" must not be attached to a verdict that is wrong half the time.

### D1 — vocabulary: `status-vocabulary.md`

Rename the machine's runtime failure verdict:

| Old | New | Meaning |
|---|---|---|
| `FAIL CONFIRMED` | `CANDIDATE DEFECT` | the machine observed a failure at runtime. Not yet reproduced by a human. NOT filable |
| — | `DEFECT` | reproduced with a human present, or reproduced twice in independent sessions. Filable |
| `FAIL REJECTED` | `NOT A DEFECT` | co-reproduction showed the product behaving correctly |

Nothing may reach `createJiraIssue` from `CANDIDATE DEFECT`. The only route to
Jira is through `DEFECT`, and the only route to `DEFECT` is D3.

This single rename is most of the fix. It makes the gate structural instead of
a request for good behaviour.

### D2 — new artifact: `<STORY>-candidate-defects.md`

Emitted at stage 9 alongside the run sheet. One entry per candidate, in this
shape:

```markdown
## CD-03 · Round tables results are found but never render
**From:** TC-REQ-29.10 (web-testing, 2026-08-05) · **Status:** CANDIDATE — not reproduced with a human
**Where:** ennies-alpha2.expoplatform.net · event 3551 · data-version 1.20.0
**Confidence:** observed once, one session

### Reproduce it with me
1. Open `https://ennies-alpha2.expoplatform.net/global-search`
2. F12 → Console, paste:
   ```js
   console.log([...document.querySelectorAll('h2[id$="-title"]')].map(h => h.textContent.trim()));
   ```
3. Tell me what it prints.

**I expect:** 8 blocks, no "Round tables", despite the API returning 2.
**What would kill this:** a "Round tables" block present, or the API returning 0.

### Outcome
- [ ] DEFECT — file it
- [ ] NOT A DEFECT — machine was wrong, record why
- [ ] NEEDS MORE — another environment, another account, another day
```

Three fields carry the weight:

- **Confidence** — `observed once` / `reproduced 2+ sessions` / `code-read only`.
  Ties to C5. A candidate at `observed once` is a question, not a finding.
- **What would kill this** — a stated falsifier, mandatory. A candidate with no
  falsifier is not a testable claim and must not be written. On EP-47675 the
  falsifier line is what stopped two drafts from becoming false bug reports.
- **Reproduce it with me** — numbered, executable by the human alone, and short
  enough to fit on one screen. Prefer a console one-liner over a click path.

### D3 — replace `qa-pipeline-code/SKILL.md` step 7 entirely

```markdown
7. **Co-reproduce candidates, then file only what survives.**

   The run produces CANDIDATE DEFECTS, never confirmed bugs. Filing is a
   separate, human-paced activity that happens after the run.

   a. Emit `<STORY>-candidate-defects.md` (see
      `../qa-manual-runsheet/references/candidate-defect-format.md`). Give the
      user the count and nothing else: *"7 candidates. Want to walk them?"*

   b. **ONE AT A TIME. Never present a batch.** Take the strongest candidate
      first — highest severity, cheapest to reproduce. Give the user its repro
      steps and stop. Wait. Do not queue the next one, do not summarise the
      others, do not explain what you will do after.

   c. When the user reports what they saw, classify it with them:
      - reproduced → `DEFECT`. Search Jira for duplicates, draft per
        `references/bug-report-template.md`, show the draft, file on an
        explicit yes.
      - did not reproduce → `NOT A DEFECT`. Record the machine's error in the
        run sheet with the reason. This is a finding about the pipeline and is
        worth as much as a bug.
      - inconclusive → `NEEDS MORE`. Say exactly what would settle it.

   d. Then, and only then, move to the next candidate.

   e. If the user says "file them all", still show each draft, but you may
      batch the drafts into one message. Never skip the drafts themselves.

   **Never** call `createJiraIssue` for anything still marked
   `CANDIDATE DEFECT`. **Never** describe a candidate as confirmed, verified,
   reproduced or a bug until step (c) has happened for it.
```

### D4 — one line in `web-testing/SKILL.md` and `api-testing/SKILL.md`

Under the classification section:

```markdown
This stage emits `CANDIDATE DEFECT`, never `DEFECT`. It has no authority to
confirm a failure — a single automated observation is a hypothesis. Confirmation
happens in stage 10 with a human present.
```

### Why this is worth the ceremony

It costs a few minutes per candidate. On EP-47675 that ceremony, applied
informally because the human insisted on it, prevented at least two false bug
reports: the "signed-in users get a worse page" claim (the account simply had an
empty exhibitor listing everywhere) and the Show-all counter claim (the
instruction was unfalsifiable because the counter caps at 10).

Two false bugs not filed is worth more than seven bugs filed fast.

---

## C. Cosmetic and quality-of-life, with effort tags

| # | Change | Where | Effort |
|---|---|---|---|
| C1 | Freeze panes (header row + TC column) and colour-by-verdict conditional formatting | `runsheet-format.md` | 10 min |
| C2 | `Today` tab — only the rows still needing a human, in order, with a tick column | `walk-sheet-format.md` | 30 min |
| C3 | `Console check` column with paste-ready one-liners | `walk-sheet-format.md` | per-story |
| C4 | Run header block (host, event id, `data-version`, module flags, date) stamped into EVERY artifact | all stage skills | 20 min |
| C5 | **Confidence field on machine verdicts** — `observed once` / `reproduced 2+` / `code-read only` | `status-vocabulary.md` | 30 min |
| C6 | Auto-drafted bug file per FAIL at stage 9, pre-filled, so filing is approve-and-go | `qa-manual-runsheet` | 1 h |
| C7 | Suite write-back must be VERIFIED by re-reading the suite, not trusted from tool responses | `qa-manual-results` | 15 min |
| C8 | Per-story output subfolder instead of a flat directory | `qa-pipeline-code` step 0 | 15 min |

**C5 is the one to do first of these.** At 54% UI accuracy, "observed once" and
"reproduced 3 times across 2 sessions" must not render identically. It is the
cheapest possible defence against the failure that cost this run three sessions,
and it makes F1 self-enforcing: a stage that can only write `observed once`
cannot publish a FAIL.

**C7 is not cosmetic despite its size.** During this run a write-back subagent
reported a count that did not match its manifest. Re-reading the suite caught
it. Trusting the tool's success response would not have.

---

## Suggested order of work

1. **F1** (second observation before any FAIL) + **C5** (confidence field) +
   **D1** (rename `FAIL CONFIRMED` to `CANDIDATE DEFECT`) — the same fix from
   three directions, and together they address the run's biggest failure. D1 is
   the highest leverage single line in this document: it makes the gate
   structural rather than a request for good behaviour.
2. **A** (walk sheet first) — biggest change to how your day feels, and it
   improves evidence quality rather than trading it away.
3. **D3** (one candidate at a time, co-reproduce before filing) — small edit,
   large change to how the end of a run feels.
4. **B** (progress) — no correctness impact, high comfort.
5. **F5** (environment probe) — already folded into A2 step a.
6. **F3, F4, C1, C2, C7** — small, independent, do them whenever.
