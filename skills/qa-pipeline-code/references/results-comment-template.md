# Results comments — two waves (step 6 = wave 1 · stage 10 = wave 2)

**Contents:** wave 1 (one status line) · the retired archive (0.33.0) ·
Comment — human summary (wave 2: the shape, the table, To do and
Questions, the footer, a worked example, Overall verdict, Partial runs,
Writing rules) · Story note — QA passed / QA failed (wave 2)

**Wave 1 (step 6, now):** the QA Service **test run** (created and
recorded per `../../qa-pipeline/references/test-runs.md`; FAIL / PARTIAL
rows stay `not_run` for the human) and **one short status comment**:

```
QA automated pass complete — N cases, M settled by machine, K for manual
— QA Service run <id> open. Results published after the manual round.
```

Posted on the QA sub-task when the ticket has one, otherwise on the
ticket under test. Agents-only wording; no verdicts visible to a human
skimmer, nobody tagged. **Nothing else is posted in wave 1.**

**Wave 2 (stage 10, after the manual round):** the human summary below,
plus story notes / bug filings / decision requests — all on
human-confirmed verdicts. Narrow wave-1 exception: runtime-confirmed +
evidenced (rated SUFFICIENT by the step-5 evidence audit) + blocking the
manual round.

## The retired archive (0.33.0) — and the rules that survive it

Until 0.33.0 wave 1 also posted a "machine archive": every stage report
pasted verbatim into fenced blocks on the QA sub-task, split into parts
above ~30,000 characters and re-joined by `scripts/extract_archive.py`.
It is gone. The per-case record is the QA Service run (0.30.0); the
reports' home is the run folder `runs/<STORY>/r<N>/` (0.32.0); the
docs-phase files are the suite. The archive duplicated all three,
ran to three to five unreadable comments per pass, and was silently
truncated by Jira's markdown→ADF conversion at least once.

What survives from the 0.26.0 archive-target rule, because it was never
really about archives:

| Ticket under test | Status line | Human summary | Anything else |
|---|---|---|---|
| Story with a QA sub-task | on the sub-task | on the sub-task | nothing |
| Story with no QA sub-task | on the story | on the story | nothing |
| Bug | on the bug | on the bug | nothing |
| Defect (is itself a sub-task) | on the defect | on the defect | nothing |

- **A fenced file dump on any ticket is a ❌** in the post-publish
  check — a Story face, a Bug, a Defect, and now the QA sub-task too.
- **Do not walk up to the parent story's QA sub-task** for a Bug or
  Defect. One ticket's run does not write into another ticket's thread.
  **One exception: a retraction** goes to the ticket where the
  retracted verdict was published, whatever ticket that is — ≤ 6 lines
  (run id, `<case> — <old> → <new>`, reason, where the new verdict was
  established), no dumps (`../../qa-pipeline/references/test-runs.md`
  → "Retraction target rule"; the case that needed it: EP-56109 carried
  three FAIL CONFIRMEDs that EP-56133 retest 3 passed, and no rule let
  the fix reach the thread).
- **The reports are local-only.** A resume on another machine, or by a
  colleague, restores verdicts from the run and nothing else — step 0's
  resume mode pauses and says so instead of re-running finished stages.
  A split Claude Code ↔ Cowork run needs both environments to see the
  same run folder (in this setup they do).
- **Pre-0.33 tickets** still carry archive comments; `extract_archive.py`
  reads them (legacy). Never post a new one.

## Comment — human summary (for people) — wave 2

**Why this shape (0.48.0).** The EP-58440 summary (2026-10-13) was
correct but hard to read, in the user's words: "different fonts styling
is used and table is hard to read, maybe there is some not relevant
info". There were three causes:
- **Six type styles in one comment:** an h1 title, bold pseudo-headings,
  a plain `Status:` line, "**Label:** text" lines, inline code, and
  URLs mid-sentence.
- **A stage table in pipeline terms.** "Code review ✅ 0 passed 0
  failed, 5 checked at runtime" tells a PM nothing. The reader wants to
  know what was checked and whether it works, not which stage did it.
- **The same item in up to three sections.** EP-58568 was in the intro,
  in Needs a human and in Carried forward. The questions were in Needs a
  human and again in Carried forward.

The shape below has **one heading level, one table, and every item
once**. The hand-edited EP-57698 summary (2026-10-06) already read this
way: a "What / How / Result" table with one row per check in screen
words.

Target **≤ 30 rendered lines**. **Omit any section that would be
empty.** A clean run is the title, the intro, the table and the footer.

Template:

```markdown
## <verdict emoji> <VERDICT WORD> — <STORY>

<≤ 2 sentences in screen words: what now works (or breaks) for the
person using the product, and where it was tested. If something outside
this ticket stops clients getting it, say so here, once.>

| What we checked | How | Result |
|---|---|---|
| <behaviour, in the words on the screen, with the before → after value if that was the point> | By hand | ✅ Pass |
| … | Browser | ❌ Fail |

### Bugs

1. <KEY or "not filed yet"> <what breaks for the user>. Breaks AC-<n>: "<clause, verbatim>"

### Retracted

- <what we checked>: was <old>, now <new>. <reason in one clause>

### To do

1. <one action, one line> (<owner>)

### Questions

1. <one decision, its two outcomes as the user would see them>? (<who answers>)

### Not tested

- <what>, because <why>

---
Checked by hand: <N> of <M>. The other <M−N> results are automated only.
Test run: https://qa-service.expoplatform.com/expoplatform/test-runs/<run id>
Test cases: https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path>
```

### Styles: only these

- **The title is `##`, never `#`.** h1 is Jira's largest font and it
  dwarfs everything around it in a comment thread. The verdict word comes
  from "Overall verdict" below.
- **Section headings are `###`, and there is no other heading or
  pseudo-heading.** No bold line standing in for a heading. No
  "**Label:** text" line (`jira-writing-style.md` already bans that
  pattern).
- **No inline code, italics or bold in the body.** Jira renders inline
  code in a monospace font on a grey background, which was one of the
  "different fonts". Ticket keys, case ids and file names stay plain
  text, and Jira links ticket keys by itself. On-screen text goes in
  straight double quotes.
- **No ids in prose:** no run UUID, commit hash or run-folder path. The
  run id is inside the Test run URL. The run folder is named in chat,
  not in Jira.
- **Bare URLs, and only in the footer.** The connector's markdown→ADF
  conversion drops `[text](url)` hyperlinks, so a markdown link lands as
  unclickable text (qa-service-publish.md → "Writing the suite link
  into Jira").

### The table — replaces the stage-verdict table

- **One row per test case** when the run has ≤ 8 cases. With more,
  write one row per requirement or screen area, with the count in
  Result ("✅ 18 of 18"). Never more than 10 rows.
- **What we checked** is the behaviour as the person using it would
  describe it, in screen words. Give the before → after value when the
  fix was about a number ("Confirmed 10 → 11"). Add the case id in
  brackets only when a later section refers to that case.
- **How** is the strongest way the result was established, one of:
  `By hand` (a tester, stage 10), `Browser` (the agent drove the UI),
  `API`, `Code only` (read, never run). Combine them with "+", e.g.
  "Browser + by hand". A walk card the agent ran while the tester
  watched (`machine (witnessed)`) is `Browser` or `API`, never "by
  hand".
- **Result** is one of: ✅ Pass · ❌ Fail · ⛔ Blocked · ⏭ Not run ·
  ✏️ Case wrong (SPEC-DEFECT: the case is wrong, not the code). A FAIL
  REJECTED is ✅ Pass. A `Code only` row may show ✅ only with the word
  "Code only" in How, because a code read is never presented as a
  runtime pass.
- **The numbers are the run's numbers.** The count gate (step 6) and
  stage 10 reconcile against the QA Service run. The per-stage counters
  stay in the stage reports and the run report, not in Jira.

### Bugs, Retracted

- **Bugs:** one line per confirmed bug, consequence first. The
  publication gate (`../../qa-pipeline/references/sources-of-record.md`
  § 7) still applies line by line: an AC id and a verbatim clause, or the
  line is not a bug. An `OBSERVATION (no source checked)` goes to
  Questions, never here.
- **Retracted** lists every machine verdict the manual round overturned.
  It comes straight after Bugs because a reader who saw the machine
  verdict elsewhere needs the correction before anything else.

### To do and Questions — every item once

These two sections replace the old Needs a human, Requirements to
correct, Unverified defect claims and Carried forward.

- **To do** is something a named person must do. End each line with
  the owner in brackets: (QA), (PO), (PR author), (environment owner),
  or a ticket key. Order: what blocks release, then test gaps, then case
  corrections, then cleanup such as retiring N test accounts on <env>
  (`qa-manual-results` step 4c). Cap 5 items; past that, group them.
- **Questions** are product decisions nobody has made, including every
  `OBSERVATION (no source checked)`. Write them by the four rules in
  `jira-writing-style.md` → "Grooming open-questions comment": one
  decision each, setting names with their path, a concrete example, and
  no code words. Cap 5.
- **Every open ledger row appears exactly once, in To do or in
  Questions** (`../../qa-pipeline/references/open-items-ledger.md`). A
  question row goes to Questions, an action row to To do. The section
  the summary used to end with ("Carried forward") is folded into these
  two, so the ledger is still published in full.
- **An item with its own ticket is named once, by its key, where it
  fits best.** A release blocker that already has a ticket (EP-58568
  for EP-58440) belongs in the intro. It is not also a To do: its own
  ticket tracks it.
- **A case correction** (SPEC-DEFECT) is a To do for QA: "Fix <case
  id>: it assumes <X>; the product does <Y>." When the correction waits
  on a product answer, the question goes in Questions and the To do
  says "once question <n> is answered".
- **An unconfirmed defect claim** is a case that arrived FAIL from code
  review and never got runtime confirmation. It is a To do for QA,
  phrased as "Confirm or drop: <claim> (code read only, never seen in
  the product)". The words "code read only" are mandatory, because half
  of the code-read-only negative verdicts in real runs were wrong.
- **Not tested** names what this round did not reach: [mobile] or
  [export] cases, a blocked case and what would unblock it. Cap 3 lines.
  A blocked case that someone must unblock is a To do instead.

### The footer

- A `---` rule, then plain lines and nothing else.
- **`Checked by hand: N of M.`** is always present. It replaces the old
  `Status: VERIFIED / PARTIALLY VERIFIED` line and says the same thing
  in words a reader can't misread: N of the M results were confirmed by
  a person and the rest are machine-only. When N = M write
  `Checked by hand: all M.` The file step 6 writes,
  `<STORY>-human-summary.md`, carries `Status: DRAFT — awaiting stage
  10` in place of this line. qa-manual-results replaces it when it
  ingests the round.
- **`Test run:`** goes in whenever a run exists. When the docs phase
  published a suite but this pass recorded no run, write
  `Test run: none, <reason>`. **`Test cases:`** goes in whenever a suite
  exists. The run page is where a reader checks the verdicts; who
  recorded each one shows on each case's page under Execution history.
- **No run-health line in Jira.** The 🟢/🟡 health line is about the
  pipeline, not the product. It stays in the run report and in chat.

### Worked example — EP-58440, rewritten

The same facts as the comment the user rejected on 2026-10-13, in the
new shape:

```markdown
## ✅ PASS — EP-58440

A participant added to an existing confirmed meeting now counts under Confirmed on their Dashboard "Meeting requests" widget, within about 2 minutes. Tested on the EP-58440 env (copy of Northstar, event 437); clients get it once EP-58568 ships the new meetings query to production.

| What we checked | How | Result |
|---|---|---|
| Joining a confirmed meeting by its Invite Link adds it to Confirmed (10 → 11) | Browser + by hand | ✅ Pass |
| An exhibitor reassigning a meeting to another team member updates Confirmed (13 → 14) | Browser | ✅ Pass |
| Meredith Hodges' widget matches her schedule (13 confirmed, 6 incoming) | Browser | ✅ Pass |
| The meetings export still lists the added participant | API | ✅ Pass |
| A cancelled attendee can rejoin by the Invite Link (PDASH-REG-04) | Browser | ✏️ Case wrong |

### To do

1. Update ScheduleExportCest: it checks Last Modified after a participant is added and will fail with the new trigger; add a test for the trigger itself (PR #5539 author)
2. Add cases for the PR's side effects with no test yet: push and mobile updates, supplier analytics, export and lead timestamps (QA)
3. Fix PDASH-REG-04 once question 1 is answered: the cancel itself works, Confirmed drops by one (QA)
4. Write acceptance criteria for the widget; none exist today (PO)

### Questions

1. Should an attendee who cancelled be able to rejoin by the Invite Link? Today they see "You are already part of this meeting". (PO)
2. Should adding a participant change the meetings export's Last Modified date, or restart a pending request's auto-expire timer? (PO)
3. The join message reads "s-was-successfully-added-to-your-schedule-on-s". Is a fix tracked anywhere? (PO)

---
Checked by hand: 1 of 5. The other 4 results are automated only.
Test run: https://qa-service.expoplatform.com/expoplatform/test-runs/75c93335-07d6-4f10-98e2-9b6d212325c8
Test cases: https://qa-service.expoplatform.com/expoplatform/test-suites/visitor/participant-dashboard
```

Compared with the original: the stage table, the Status line, the
"Checked:" paragraph (it is the table now), Requirements to correct (now
To do 3), the Carried forward list (every row is now in To do or
Questions) and the run id printed twice are gone. EP-58568 appears once.

### Overall verdict

- ✅ **PASS**: no FAIL / FAIL CONFIRMED in any stage, nothing BLOCKED.
- ⚠ **PASS WITH GAPS**: no failures, but BLOCKED / PARTIAL / routed-out
  cases remain unverified.
- ❌ **FAIL**: at least one FAIL or FAIL CONFIRMED in any stage.
- ⛔ **BLOCKED**: a stage could not run at all.

### Partial runs (split environments)

When some stages have not run yet (e.g. 5–7 done in Claude Code,
web-testing pending in Cowork):

- Verdict: `⏳ PARTIAL — <pending stages> pending`.
- Status line: append `— PARTIAL: <pending stages> pending (runs in
  <environment>)`. The finished reports stay in the run folder and the
  resuming environment reads the same folder.
- Summary (wave 2, later): a Not tested line naming what remains and
  where it runs, if anything is still pending by then.

The resumed session posts a fresh status line. Never edit or delete
earlier comments — newest wins.

### Writing rules

- **Voice, caps and section discipline live in `jira-writing-style.md`**
  (same folder) — the single home for every human-facing text this
  pipeline writes into Jira: this summary, the status line, story
  notes, bug drafts, the grooming open-questions comment, and the
  stage-10 write-backs. Read it before composing; when it and a
  template disagree on tone or length, it wins.
- Comment-specific rules on top of it:
- One line per confirmed bug — the evidence lives in the stage report
  in the run folder and in
  the QA Service run's roster note for that case; never restate full
  findings.
- FAIL REJECTED items are not bugs — count them as passes in the
  table; mention a rejection only when it corrects the ticket's
  stated expectations.
- The table's counts must match the QA Service run exactly.
- **Self-check before showing the draft:** one `##`, only `###` below
  it, no bold or inline code in the body, no URL outside the footer, no
  item in two sections, and the Checked-by-hand line present.

## Story note — QA passed (posted by qa-manual-results step 4b, NOT by qa-pipeline-code step 8)

Posted to the **PARENT story** (not the QA sub-task) when the overall
verdict is ✅ PASS **after the manual results are ingested** — managers
and devs read the story, not the sub-task. ≤10 lines, plain words, no
pipeline jargon. qa-pipeline-code step 8 must not post this on automated
verdicts alone; if the user insists on a story note at step 8, use the title
"✅ Automated QA passed — manual verification pending", include the
`Status: DRAFT — awaiting stage 10` line, and apply no workflow transition.

```markdown
✅ QA passed — <STORY>: <feature in plain words>

**What was tested:** <1 sentence — the user-facing behaviour>
**Environment:** <host / alpha env from the run> · event <EVENT_ID if relevant>
**Coverage:** <N> test cases (<N> UI, <N> API) + code review of <branches/PRs>
**Result:** all passed<, N non-blocking notes: <one line each>>.
**Not covered here:** <N [mobile]/[export] cases → manual check> *(omit if none)*
**Test docs:** https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path> *(bare URL, never a markdown link; omit if no suite)*
**Run:** https://qa-service.expoplatform.com/expoplatform/test-runs/<run id> *(bare URL; per-case verdicts)*
**Details:** full reports held by QA (run folder, <KEY> r<N>)
**Status:** ready for <merge / release / next step>
```

Rules:

- Numbers must match the human summary's table and the run.
- "Non-blocking notes" are FAIL REJECTED corrections or cosmetic
  remarks — never confirmed bugs (a confirmed bug means the verdict
  is not PASS).
- Omit any line that would be empty (notes, Not covered).
- Only for ✅ PASS. For FAIL / PASS WITH GAPS use the variant below.

## Story note — QA failed (posted by qa-manual-results step 4b)

Also posted to the **PARENT story**, for the same reason: managers and
devs read the story, not the sub-task — and that matters *more* when a
run produced defects, not less. Post it **in addition to** the
reassignment path, not instead of it. Wave 2, like the PASS note: the
human verdicts are in; qa-pipeline-code step 8 posts it only under its
narrow wave-1 exception (a runtime-confirmed, evidenced, blocking fault
the evidence audit rated SUFFICIENT).

Group the defects by what a reader has to decide about them, not by the
order they were filed. A flat list of thirteen keys tells a manager
nothing; "three of these are privacy exposures and two are not this
story's fault" tells them everything.

```markdown
❌ QA failed — <STORY>: <feature in plain words>

**What was tested:** <1 sentence — the user-facing behaviour>
**Environment:** <host / alpha env> · event <EVENT_ID if relevant>
**Coverage:** <N> cases (<N> UI, <N> API, <N> mobile, <N> export) + code review of <PR>
**Result:** <N> failed · <N> passed · <N> blocked · <N> not run. <N> defects raised.

**What holds:** <1–2 sentences on what genuinely works — a reader needs to
know how much of the feature is sound, not only that it failed>

**Blocks release / needs a decision**
- <KEY> — <one line, consequence first>

**Feature incomplete**
- <KEY> — <one line>

**Data integrity**
- <KEY> — <one line>

**Not caused by this story** *(omit if none)*
- <KEY> — <one line, and why it is out of scope>

**Not covered:** <N> blocked by environment/access, <N> awaiting a manual run
**Test docs:** https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path> *(bare URL)*
**Run:** https://qa-service.expoplatform.com/expoplatform/test-runs/<run id> *(bare URL; per-case verdicts)*
**Details:** full reports held by QA (run folder, <KEY> r<N>)
```

Rules:

- Same numbers as the human summary's table and the run.
- **Lead each defect line with the consequence, not the mechanism.**
  "Opted-out users are named to exhibitors" beats "consent evaluated at
  the wrong point in the read filter".
- Separate defects this story *caused* from ones it merely *surfaced*.
  Environment faults and pre-existing bugs must not inflate the story's
  apparent damage.
- Always include **What holds**. A failure note that lists only breakage
  misleads on scope; if the core of the feature is sound, say so.
- Never imply a status transition the user has not approved.
