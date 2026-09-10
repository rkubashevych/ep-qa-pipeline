# Results comments — two waves (step 6 = wave 1 · stage 10 = wave 2)

**Contents:** wave 1 (one status line) · the retired archive (0.33.0) ·
Comment — human summary (wave 2, incl. Unverified defect claims,
Requirements to correct, Overall verdict, Partial runs, Writing rules)
· Story note — QA passed / QA failed (wave 2)

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
evidenced + blocking the manual round.

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

Target **≤ 30 lines**. No fenced file dumps, no per-TC tables of
passes. Most important information first. **Omit any section that
would be empty** — a clean run is a verdict line, the stage table, and
the health line, nothing more.

Template:

```markdown
# QA result: <verdict emoji + word> — <STORY>

<1–2 plain sentences: what was tested and the bottom line, e.g.
"18 of 20 test cases pass. 2 confirmed bugs in exhibitor logo
settings, reproduced in both UI and API.">

**Stage verdicts**

| Stage | Verdict | Passed | Failed | Other |
|---|---|---|---|---|
| Code review | ✅ / ❌ | N | N | N QA · N N/A |
| API testing | ✅ / ❌ / ⛔ | N | N | N PARTIAL · N BLOCKED |
| Web testing (UI) | ✅ / ❌ / ⛔ | N | N | N BLOCKED |

**Confirmed bugs**

1. **TC-REQ-N.M — <short name>** — expected <X>, got <Y>
   (<where: page / endpoint>). <Filed as EP-XXXXX | not filed yet>
   (evidence: reproduced-with-control | observed-once | code-read)

**Needs a human**

- BLOCKED: TC-REQ-N.M — <why; what would unblock it>
- Endpoint-mapping correction: ticket says <X>, real endpoint is <Y>
- ⚠ <special-attention / blast-radius note from the run report>

**Not tested in this run**

- N [mobile] cases → manual/device testing; N [export/email] cases
  → export/MailDev
- N of M cases verified by code reading only (code-review PASS — never
  executed against a running system)

**Unverified defect claims** *(omit only when there are none)*

- List every case that arrived FAIL from code review and ended BLOCKED
  or otherwise never reached runtime confirmation, one line each. These
  are NOT blocked cases in the ordinary sense: a defect has been
  asserted from a code read and never confirmed against the product.
  Say so plainly, and say what would confirm it. (Base rate from real
  runs: half of code-read-only negative verdicts were wrong.)

**Requirements to correct** *(omit if none)*

- TC-REQ-N.M (SPEC-DEFECT): the case/requirement says <X>; the spec /
  observed deliberate behaviour is <Y> — fix the case, not the code

Status: VERIFIED — manual round ingested <date>; <N> machine verdicts
confirmed, <N> retracted. (If rows were not walked:
`PARTIALLY VERIFIED — <N> rows not walked; those verdicts remain
machine-only.`) The file qa-pipeline-code step 6 writes carries
`Status: DRAFT — awaiting stage 10` instead; qa-manual-results replaces
the line when it ingests the human round and posts the comment.

**Carried forward** *(omit if the ledger has no open rows)*

- <id> — <one line> (since <round/date>; owner <who>)

Run health: 🟢 coverage · 🟢 input · 🟡 process — detail in the run
report (`runs/<STORY>/r<N>/<STORY>-run-report.md`).

**Test docs:** <N> requirements / <M> cases; QA Service run <id>
(<closed / running>: <N> pass · <N> fail · <N> blocked · <N> skipped) —
https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path>
```

QA Service line rules: include it whenever the docs phase published a
suite (even if this pass recorded no run — then say "no run: <reason>").
Omit the line entirely only when no
suite exists for this ticket. **Write the full bare URL** — never
`[text](url)`: the connector's markdown→ADF conversion drops
hyperlinks, so a markdown link lands in Jira as unclickable text
(see qa-service-publish.md → "Writing the suite link into Jira").

### Overall verdict

- ✅ **PASS** — no FAIL / FAIL CONFIRMED in any stage, nothing BLOCKED.
- ⚠ **PASS WITH GAPS** — no failures, but BLOCKED / PARTIAL / routed-out
  cases remain unverified.
- ❌ **FAIL** — at least one FAIL or FAIL CONFIRMED in any stage.
- ⛔ **BLOCKED** — a stage could not run at all.

### Partial runs (split environments)

When some stages have not run yet (e.g. 5–7 done in Claude Code,
web-testing pending in Cowork):

- Verdict: `⏳ PARTIAL — <pending stages> pending`.
- Status line: append `— PARTIAL: <pending stages> pending (runs in
  <environment>)`. The finished reports stay in the run folder and the
  resuming environment reads the same folder.
- Summary (wave 2, later): a **Pending** line naming what remains and
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
  prose; mention a rejection only when it corrects the ticket's
  stated expectations.
- Numbers in the stage table must match the report files' Statistics
  blocks exactly.

## Story note — QA passed (posted by qa-manual-results step 4b, NOT by qa-pipeline-code step 8)

Posted to the **PARENT story** (not the QA sub-task) when the overall
verdict is ✅ PASS **after the manual results are ingested** — managers
and devs read the story, not the sub-task. ≤10 lines, plain words, no
pipeline jargon. qa-pipeline-code step 8 must not post this on automated
verdicts alone; if the user insists on a story note at step 8, use the title
"✅ Automated QA passed — manual verification pending", include the
`Status: PROVISIONAL` line, and apply no workflow transition.

```markdown
✅ QA passed — <STORY>: <feature in plain words>

**What was tested:** <1 sentence — the user-facing behaviour>
**Environment:** <host / alpha env from the run> · event <EVENT_ID if relevant>
**Coverage:** <N> test cases (<N> UI, <N> API) + code review of <branches/PRs>
**Result:** all passed<, N non-blocking notes: <one line each>>.
**Not covered here:** <N [mobile]/[export] cases → manual check> *(omit if none)*
**Test docs:** https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path> *(bare URL, never a markdown link; omit if no suite)*
**Details:** per-case verdicts on QA Service run <run id>; full reports held by QA (run folder, <KEY> r<N>)
**Status:** ready for <merge / release / next step>
```

Rules:

- Numbers must match the human summary's stage table.
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
narrow wave-1 exception (a runtime-confirmed, evidenced, blocking fault).

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
**Details:** per-case verdicts on QA Service run <run id>; full reports held by QA (run folder, <KEY> r<N>)
```

Rules:

- Same numbers as the human summary's stage table.
- **Lead each defect line with the consequence, not the mechanism.**
  "Opted-out users are named to exhibitors" beats "consent evaluated at
  the wrong point in the read filter".
- Separate defects this story *caused* from ones it merely *surfaced*.
  Environment faults and pre-existing bugs must not inflate the story's
  apparent damage.
- Always include **What holds**. A failure note that lists only breakage
  misleads on scope; if the core of the feature is sound, say so.
- Never imply a status transition the user has not approved.
