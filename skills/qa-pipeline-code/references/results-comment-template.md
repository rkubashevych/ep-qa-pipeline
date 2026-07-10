# Results comments — qa-pipeline-code step 6

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

Run health: 🟢 coverage · 🟢 input · 🟡 process — detail in the run
report (archive comment above).
```

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
