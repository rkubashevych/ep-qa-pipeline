---
name: qa-pipeline-docs
description: >
  Orchestrator for the documentation half of the QA pipeline (stages
  1-4) plus publishing. Given a Jira ticket, runs task-context ->
  requirements-grooming -> qa-checklist -> qa-test-cases, runs the
  run-analyzer, then creates a QA sub-task on the story holding the
  checklist + test cases so the code phase can pick them up without
  manual file attaching. Auto-advances with default decisions, pausing
  only to confirm the Jira write (say "interactive mode" to get the
  grooming pause back). Use it
  when the user says "run the QA docs pipeline", "build the test cases
  for a ticket", "groom and write test cases", or gives a ticket and
  wants the full checklist/test-case set without invoking each stage by
  hand.
---

# QA Pipeline -- Docs (stages 1-4 + publish)

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
   - **Open items → ticket (shift-left), bundled with publish.** If
     genuinely open items remain — questions, contradictions needing
     the PM/analyst, spec gaps — do not ask about them separately:
     include a drafted ticket comment (one line per item, grouped
     Questions / Contradictions / Gaps, no pipeline jargon) in the
     stage-6 publish preview, as an opt-out part of that single
     confirmation. Items the user answered in chat are settled — do
     not post those.
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

6. **Publish to a new QA sub-task** -- create a QA sub-task on the story
   so the code phase can read the checklist/test-cases from Jira instead
   of via re-attached files.
   - **REQUIRED PAUSE / CONFIRM.** Before writing anything to Jira, show
     the user a preview: the parent story, the new sub-task summary, the
     assignee, and what will be posted. Create only after an explicit
     yes. (Writing to the tracker is a change and must be confirmed.)
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
     - A "How to use this ticket" note: the checkbox tracker in the
       comment is the single source of truth for **manual** testing
       status — tick as you verify by hand. Automated results arrive
       later as two code-phase comments (machine archive + human
       summary); the connector cannot tick checkboxes, so transfer
       automated PASS/FAIL to the tracker by hand if you want one
       combined view. The code phase reads the test cases from the
       comment.
     - The `⚠ SPECIAL ATTENTION` list and a short run-report summary.
     - Do NOT paste the checklist here — it duplicates the test cases and
       is not the tracker. One tracker only.
   - **Test cases → a follow-up comment (`addCommentToJiraIssue`), as an
     interactive checkbox tracker** so the human can tick pass/fail and
     the code phase can still read it:
     - One Jira task checkbox per test case: a single line
       `- [ ] TC-REQ-N.M — <name>` (id + short name only).
     - Put `Pre:` / `Steps:` / `Exp:` / `Post:` as **sibling lines right
       after** the checkbox (blank line between), NOT nested under it —
       nesting content inside a `- [ ]` item makes Jira drop the checkbox
       (it becomes a plain bullet). Steps go in a numbered list so each is
       on its own line. Verified: siblings keep the box interactive AND
       the steps readable.
     - Group by `### REQ-N — <label>  [channels]` headings so the
       tracker mirrors the test-cases file, and end the comment with
       the statistics block from the test-cases file.
   - **Machine-readable archive → one more comment**: post the full
     `<ISSUEKEY>-checklist.md` and `<ISSUEKEY>-test-cases.md` contents,
     each inside its own fenced code block, each preceded by a plain
     line naming the file (e.g. `File: EP-1234-test-cases.md`). This is
     what `qa-pipeline-code` reads back in a fresh chat (its Step 0
     extracts these fenced blocks) — the checkbox tracker is for humans,
     the fenced blocks are for the code phase. Do not shorten or
     reformat the file contents inside the blocks.
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
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items the code phase should know about.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat.