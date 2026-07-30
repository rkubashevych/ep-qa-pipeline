# Results comments — qa-pipeline-code step 6

**Contents:** Comment 1 — machine archive · Comment 2 — human summary
(incl. PROVISIONAL status line, Requirements to correct, Overall
verdict, Partial runs, Writing rules) · Story note — QA passed (posted
by qa-manual-results) · Story note — QA failed (step 8)

Step 6 posts **two comments** to the QA sub-task, in this order:

1. **Machine archive** — the raw report files, for agents. Long is fine.
2. **Human summary** — short and formatted, for people. Posted second so
   it is the newest comment on the ticket.

Both are always posted, regardless of verdict. Never merge them into one
comment.

## Comment 1 — machine archive (for agents)

Verbatim report files in labeled fenced code blocks — the same
convention as the docs-phase archive comment (`qa-pipeline-docs`
step 6), so any future agent can rebuild the full reports from Jira
with the same parser. **Do not shorten, reformat, or paraphrase the
file contents.**

Shape (one `File:` line + one fenced block per file):

````
Machine-readable results archive (for agents). Humans: see the summary comment.

File: <STORY>-code-review.md

```
<full file contents>
```

File: <STORY>-api-testing.md

```
<full file contents>
```

File: <STORY>-web-testing.md

```
<full file contents>
```

File: <STORY>-run-report.md

```
<full file contents>
```
````

Include every report file that exists. If a stage produced no file
(e.g. no `[API]` cases → no api-testing report), add a plain line
instead: `File <STORY>-api-testing.md not produced — <reason>`.

**Size limit:** a Jira comment body maxes out around ~32,000
characters. If the assembled archive exceeds ~30,000, split it into
several archive comments (posted in order, all before the human
summary), each with the same shape, labelling split files
`File: <name> (part i/N)`. Split only at line boundaries; parts
re-join by simple concatenation.

## Comment 2 — human summary (for people)

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

**Needs a human**

- BLOCKED: TC-REQ-N.M — <why; what would unblock it>
- Endpoint-mapping correction: ticket says <X>, real endpoint is <Y>
- ⚠ <special-attention / blast-radius note from the run report>

**Not tested in this run**

- N [mobile] cases → manual/device testing; N [export/email] cases
  → export/MailDev
- N of M cases verified by code reading only (code-review PASS — never
  executed against a running system)

**Requirements to correct** *(omit if none)*

- TC-REQ-N.M (SPEC-DEFECT): the case/requirement says <X>; the spec /
  observed deliberate behaviour is <Y> — fix the case, not the code

Status: PROVISIONAL — automated verdicts; manual verification pending
(<N> rows on the run sheet, incl. <N> spot-checks). Final status
arrives with the manual-results comment, which supersedes this line.

Run health: 🟢 coverage · 🟢 input · 🟡 process — detail in the run
report (archive comment above).

**Test docs:** <N> requirements / <M> cases, run results written back —
https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path>
```

QA Service line rules: include it whenever the docs phase published a
suite (even if this run's write-back was skipped — then say
"write-back skipped: <reason>"). Omit the line entirely only when no
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
web-testing pending in Cowork), post the same two comments with:

- Verdict: `⏳ PARTIAL — <pending stages> pending`.
- Archive: only the report files that exist, plus a plain line per
  missing file: `File <STORY>-web-testing.md not produced — pending
  (runs in Cowork)`.
- Summary: a **Pending** line naming what remains and where it runs.

The resumed session posts a fresh final pair (archive + summary).
Never edit or delete earlier comments — newest pair wins.

### Writing rules

- Write for a PM/dev skimming Jira: plain words, no pipeline jargon
  ("checked against the code", not "stage 6").
- One line per confirmed bug — the evidence lives in the archive
  comment; never restate full findings.
- FAIL REJECTED items are not bugs — count them as passes in the
  prose; mention a rejection only when it corrects the ticket's
  stated expectations.
- Numbers in the stage table must match the report files' Statistics
  blocks exactly.

## Story note — QA passed (posted by qa-manual-results step 4, NOT step 8)

Posted to the **PARENT story** (not the QA sub-task) when the overall
verdict is ✅ PASS **after the manual results are ingested** — managers
and devs read the story, not the sub-task. ≤10 lines, plain words, no
pipeline jargon. Step 8 must not post this on automated verdicts
alone; if the user insists on a story note at step 8, use the title
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
**Details:** full reports on QA sub-task <KEY>
**Status:** ready for <merge / release / next step>
```

Rules:

- Numbers must match the human summary's stage table.
- "Non-blocking notes" are FAIL REJECTED corrections or cosmetic
  remarks — never confirmed bugs (a confirmed bug means the verdict
  is not PASS).
- Omit any line that would be empty (notes, Not covered).
- Only for ✅ PASS. For FAIL / PASS WITH GAPS use the variant below.

## Story note — QA failed (step 8)

Also posted to the **PARENT story**, for the same reason: managers and
devs read the story, not the sub-task — and that matters *more* when a
run produced defects, not less. Post it **in addition to** the
reassignment path, not instead of it.

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
**Details:** full reports and per-case verdicts on QA sub-task <KEY>
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
