---
name: qa-pipeline-docs
description: >
  Orchestrator for the documentation half of the QA pipeline (stages
  1-4) plus publishing. Given a Jira ticket, runs task-context ->
  requirements-grooming -> qa-checklist -> qa-test-cases, runs the
  run-analyzer, then creates a QA sub-task on the story holding the
  checklist + test cases so the code phase can pick them up without
  manual file attaching. Auto-advances, pausing only where human input
  is needed (grooming decisions, and confirming the Jira write). Use it
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

## How it runs

Execute each stage by reading that stage's `SKILL.md` and following it
**in full** -- do not summarise or shortcut it. Pass each output file to
the next stage automatically (they share the working directory).

1. **task-context** -- run the `task-context` skill on the ticket.
   - Pause only if it needs you: attachments to upload, or a Confluence
     access / missing-AC issue. Otherwise continue automatically.
   - Produces `<ISSUEKEY>-context.md`.

2. **requirements-grooming** -- run the `requirements-grooming` skill.
   - **REQUIRED PAUSE.** Present the grooming findings (questions,
     contradictions, potential bugs, uncovered requirements, risks, and
     any Confluence-vs-Jira conflicts) and **wait for the user's
     decisions.** Do not proceed until they answer or say to skip. This
     checkpoint must never be auto-resolved.
   - Produces `<ISSUEKEY>-requirements.md`.

3. **qa-checklist** -- run the `qa-checklist` skill.
   - Pause only for a genuine clarifying question. Otherwise continue.
   - Produces `<ISSUEKEY>-checklist.md` (with channel tags).

4. **qa-test-cases** -- run the `qa-test-cases` skill.
   - Pause only for a genuine clarifying question. Otherwise continue.
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
   - Create with the Atlassian connector (`createJiraIssue`):
     - project `EP`, issue type **"QA sub-task"** (id `10107`),
       `parent` = the Story key.
     - assignee = **Roman Kubashevych** (accountId
       `712020:2647832a-3298-435d-afd6-18a9441a1909`; if it changes,
       resolve `r.kubashevych@expoplatform.com` via
       `lookupJiraAccountId`).
     - summary = `[QA-PIPELINE] <story summary> — test cases`.
     - label `qa-pipeline` (so the code phase can find it).
     - Always create a NEW sub-task (do not reuse an existing one).
   - **Description content** (keep it a summary, NOT a second tracker):
     - A link to the spec/Confluence AC and the parent story.
     - A "How to use this ticket" note: track pass/fail on the test-case
       checkboxes in the comment (the single source of truth for status);
       the full checklist + requirements live in the pipeline files; the
       code phase reads the test cases from the comment.
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

## Final response

After publishing, report:
- The paths of the four stage files + the run report.
- The QA sub-task key + URL and what was posted (tracker comment +
  archive comment).
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items the code phase should know about.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat.