---
name: qa-pipeline-docs
description: >
  Orchestrator for the documentation half of the QA pipeline (stages
  1-4) plus publishing. Given a Jira ticket, runs task-context, then
  requirements-grooming, then qa-checklist, then qa-test-cases, runs the
  run-analyzer, then publishes: a QA sub-task on the story holding the
  checklist + test cases (so the code phase can pick them up without
  manual file attaching) and, when the QA Service MCP connector is
  enabled, a QA Service suite with the requirements and test cases as
  the team's permanent system of record. Auto-advances with default
  decisions, pausing only to confirm the publish (say "interactive
  mode" to get the grooming pause back). Use it
  when the user says "run the QA docs pipeline", "build the test cases
  for a ticket", "groom and write test cases", or gives a ticket and
  wants the full checklist/test-case set without invoking each stage by
  hand.
---

# QA Pipeline -- Docs (stages 1-4 + publish)

> **Tool names:** bare names like `createJiraIssue` /
> `addCommentToJiraIssue` (here and in this skill's references) are
> tools of the **Atlassian MCP connector**; `create_suite` /
> `create_test_case` / `edit_requirement` etc. belong to the
> **QA Service MCP connector**. The install-specific server prefix
> varies — match by tool name on the server that provides it.

> Recommended settings for the whole run: **Opus . Effort: High .
> Extended thinking: On**. Grooming (stage 2) benefits most; the lighter
> stages run fine on this too. This avoids switching models mid-run.

Runs the first four pipeline stages end to end, health-checks the run,
then publishes the result to a QA sub-task on the story. Each stage is a
real skill in this repo -- this orchestrator sequences them, it does not
reimplement them.

## Input

- A Jira ticket key or URL (e.g. `EP-44730`). If the key given is itself
  a sub-task, use its parent Story as the story for publishing.

## When to run (shift-left)

The docs phase needs only the ticket — not the code. Run it as EARLY
as possible: at refinement, or as soon as the ticket is written,
ideally before or while dev is coding. Early, the grooming findings
(stage 2) can still fix the spec and prevent bugs instead of catching
them, and devs can self-check against the published test cases before
handing off to QA. Run at QA time it still works, but grooming
findings arrive after the code is written — strictly worse. If the
ticket's status shows dev has not started or is in progress, say so
and note the findings are in time to act on; never block the run on
status.

## How it runs

**Session name first:** as soon as the ticket key is known, suggest the
user rename this session to `QA-pipeline <KEY> — docs` (Claude Code:
`/rename QA-pipeline <KEY> — docs`; Cowork: click the chat title).
Sessions can't be renamed programmatically — one short reminder, then
move on.

Execute each stage by reading that stage's `SKILL.md` and following it
**in full** -- do not summarise or shortcut it. Pass each output file to
the next stage automatically (they share the working directory).


1. **task-context** -- run the `task-context` skill on the ticket.
   - Pause only if it needs you: attachments to upload, or a Confluence
     access / missing-AC issue. Otherwise continue automatically.
   - Produces `<ISSUEKEY>-context.md`.

2. **requirements-grooming** -- run the `requirements-grooming` skill.
   - **Auto-default (no pause).** Present the grooming findings
     (questions, contradictions, potential bugs, uncovered
     requirements, risks, Confluence-vs-Jira conflicts) in chat for
     visibility, then continue WITHOUT waiting — treat every finding
     as "skip": requirements stay as written, unresolved conflicts
     keep both versions marked "(unresolved conflict)". The findings
     resurface at the publish confirmation, where the user can still
     answer them (then regenerate from stage 2) or post the open items
     to the ticket. If the user asks for **interactive mode**, pause
     here and wait for decisions as grooming's own SKILL.md describes.
   - **Open items → ticket NOW, not at publish (shift-left is a clock,
     not a label).** If genuinely open items remain — questions,
     contradictions needing the PM/analyst, spec gaps — draft the
     ticket comment immediately (one line per item, grouped Questions /
     Contradictions / Gaps, no pipeline jargon), show it, and ask ONE
     quick yes/no: "post these open questions to <KEY> now?". On yes,
     post it before stage 3 starts; the run continues either way
     without waiting for answers. Rationale: an answer that arrives
     while stages 3–4 run can still fix the cases this run; a question
     first seen at the publish preview has already cost the whole
     phase (on a real ticket, five unanswered questions each became a
     blocked or contested case downstream). Items the user answered in
     chat are settled — do not post those. If the user declines the
     stage-2 post, fall back to including the draft in the stage-6
     publish preview as before.
   - Produces `<ISSUEKEY>-requirements.md`.

3. **qa-checklist** -- run the `qa-checklist` skill.
   - Do not pause for clarifying questions: build on what is written,
     note the ambiguity in the file ("needs clarification"), continue.
   - Produces `<ISSUEKEY>-checklist.md` (with channel tags).

4. **qa-test-cases** -- run the `qa-test-cases` skill.
   - Do not pause for clarifying questions: the grounding rule already
     handles ambiguity (no test case is invented; the requirement is
     marked "needs clarification"). Continue.
   - Produces `<ISSUEKEY>-test-cases.md`.

5. **qa-run-analyzer** -- run the `qa-run-analyzer` skill automatically.
   It health-checks the docs run and writes `<ISSUEKEY>-run-report.md`.

6. **Publish** -- two destinations, ONE confirmation.
   (a) a new QA sub-task on the story, so the code phase can read the
   checklist/test-cases from Jira instead of via re-attached files;
   (b) a QA Service suite holding the same requirements + test cases as
   the team's permanent, traceable system of record — per
   **`references/qa-service-publish.md`** (field mapping, suite naming
   and re-run rules live there). This is on by default whenever the
   connector is present. Publish (a) only — and say so once in the final
   response — when the connector is absent or the user declines. Never
   block (a) on (b).
   - **REQUIRED PAUSE / CONFIRM.** Before writing anything to Jira or
     QA Service, show the user ONE preview: the parent story, the new
     sub-task summary, the assignee, what will be posted, and the QA
     Service line (new suite path + requirement/case counts, or
     "appending to existing suite", or "skipped — connector not
     enabled"). Proceed only after an explicit yes. (Writing to the
     tracker or to QA Service is a change and must be confirmed.)
   - Create with the Atlassian connector (`createJiraIssue`), using the
     project key, issue type, assignee, summary format, and label from
     **`references/publish-config.md`** (the per-team values live there —
     edit that file, not this one, when adopting the plugin), with
     `parent` = the Story key.
     - Always create a NEW sub-task (do not reuse an existing one).
     - **Supersede the old one:** if an earlier pipeline QA sub-task
       exists on this story (same label), add a comment to it after
       creating the new one — "Superseded by <NEW-KEY> (newer pipeline
       run)" — and offer to close/cancel it if the workflow allows.
       The code phase already prefers the newest, but humans need the
       pointer.
   - **Description content** (keep it a summary, NOT a second tracker):
     - A link to the spec/Confluence AC and the parent story.
     - The QA Service suite line: the full **bare** suite URL (never a
       markdown link — the connector drops hyperlinks) followed by
       `(N requirements / M cases, prefix <PREFIX>)`. Format:
       `references/qa-service-publish.md` → "Writing the suite link
       into Jira". Omit if the QA Service publish was skipped.
     - A "How to use this ticket" note: the checkbox tracker in the
       comment is the single source of truth for **manual** testing
       status — tick as you verify by hand; the full steps/expected
       results for each case live in the QA Service suite (linked
       above). Automated results arrive later as two code-phase comments
       (machine archive + human summary); the connector cannot tick
       checkboxes, so transfer automated PASS/FAIL to the tracker by
       hand if you want one combined view.
     - The `⚠ SPECIAL ATTENTION` list and a short run-report summary.
     - An "Open questions from grooming" list — the same open items
       drafted for the story comment (questions / contradictions /
       gaps, one line each), so a manual tester sees them without
       opening the story. Omit if there are none.
     - Do NOT paste the checklist here — it duplicates the test cases and
       is not the tracker. One tracker only.
   - **Test cases → a follow-up comment (`addCommentToJiraIssue`), as an
     interactive checkbox tracker** for the human to tick pass/fail.
     **One line per case — no Pre/Steps/Exp** (measured: inlining them
     duplicated the machine archive by 99.3% and cost ~15,000 characters
     per ticket; the steps live in the QA Service suite and the local
     file):
     - One Jira task checkbox per test case:
       `- [ ] TC-REQ-N.M — <name>  [<channel>] · <PREFIX>-<SEG>-NN`
       (id, short name, channel tag, and the QA Service case id so a
       reader can find the full case in one hop).
     - Group by `### REQ-N — <label>  [channels]` headings so the
       tracker mirrors the test-cases file, and end the comment with
       the statistics block from the test-cases file.
     - **Count gate — do not post a number you did not derive.** Before
       posting, mechanically recount the `### TC-REQ` headings and
       their channel tags (where a shell is available, run
       `python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <KEY>`;
       otherwise count the headings directly). If the statistics block
       disagrees with the mechanical count, FIX the test-cases file
       first — never post the mismatched number to Jira or use it for
       suite levels.
     - Nothing else goes in this comment. If a case genuinely needs its
       steps visible in Jira (a blocker a human must reproduce without
       QA Service access), add them to that ONE case, not to all.
   - **Machine-readable archive → only when QA Service did NOT publish.**
     The code phase reads the cases from the suite when there is one, so
     the fenced archive is a fallback, not a default:
     - **QA Service suite published** → skip the archive comment, with
       ONE exception: the checklist's **structural checks that have no
       test case** (the `[UI]` presence / label / field-type checks)
       exist nowhere else — not in the suite, not in the tracker — and
       `web-testing` executes them. Post those, and only those, as a
       short fenced block headed
       `File: <ISSUEKEY>-checklist.md (structural checks only)`,
       preserving their REQ grouping and channel tags. Everything the
       cases already cover stays out. State in the final response that
       the code phase will read the cases from the suite. (Saves ~45,000
       characters per ticket while keeping one authoritative copy of
       each artifact.)
     - **No suite (connector absent / user declined)** → post the full
       `<ISSUEKEY>-requirements.md`, `<ISSUEKEY>-checklist.md` and
       `<ISSUEKEY>-test-cases.md` contents
       exactly as before, each inside its own fenced code block preceded
       by a plain `File: <name>` line, so `qa-pipeline-code` Step 0 can
       still rebuild them (the requirements file is what lets the
       code-phase analyzer re-verify upstream traceability — without it
       that check dies silently in every fresh chat). Do not shorten or
       reformat file contents inside the blocks.
     - **Size limit:** a Jira comment body maxes out around ~32,000
       characters. Measure the assembled comment before posting; if it
       exceeds ~30,000, split it into several comments with the same
       shape, labelling split files `File: <name> (part i/N)` — split
       only at line boundaries. The code phase re-joins parts in order.

## Final response

After publishing, report:
- The paths of the four stage files + the run report.
- The QA sub-task key + URL and what was posted (tracker comment +
  archive comment).
- The QA Service suite path + requirement/case counts and the
  count-verification result (or "QA Service publish skipped —
  connector not enabled").
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items the code phase should know about.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat. `qa-pipeline-code` ends by building the manual run sheet
  (`qa-manual-runsheet`), so do NOT run that stage here — the run sheet
  needs the automated verdicts to know what is left for the human.
