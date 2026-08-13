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
> Extended thinking: On**. Grooming (stage 2) benefits most.

Runs the first four pipeline stages end to end, health-checks the run,
then publishes to a QA sub-task on the story. Each stage is a real
skill in this repo — this orchestrator sequences them, it does not
reimplement them.

## Input

- A Jira ticket key or URL (e.g. `EP-44730`). If the key is itself a
  sub-task, use its parent Story as the story for publishing.

## When to run (shift-left)

The docs phase needs only the ticket, not the code — run it as EARLY
as possible (refinement, or as soon as the ticket is written). Early,
grooming findings can still fix the spec and prevent bugs, and devs
can self-check against the published cases. At QA time it still works,
but findings arrive after the code is written. If the ticket's status
shows dev has not started or is in progress, say so and note the
findings are in time to act on; never block the run on status.

## How it runs

**Session name first:** as soon as the ticket key is known, suggest
renaming the session to `QA-pipeline <KEY> — docs` (Claude Code:
`/rename …`; Cowork: click the chat title). One short reminder, then
move on.

Execute each stage by reading its `SKILL.md` and following it **in
full** — do not summarise or shortcut it. Stages share the working
directory; pass each output file to the next automatically.

1. **task-context** — pause only if it needs you (attachments to
   upload, a Confluence access / missing-AC issue). Produces
   `<ISSUEKEY>-context.md`.

2. **requirements-grooming** — produces `<ISSUEKEY>-requirements.md`.
   - **Auto-default (no pause).** Present the grooming findings in
     chat for visibility, then continue WITHOUT waiting — treat every
     finding as "skip": requirements stay as written, unresolved
     conflicts keep both versions marked "(unresolved conflict)". The
     findings resurface at the publish confirmation, where the user
     can still answer them (then regenerate from stage 2). If the user
     asks for **interactive mode**, pause here as grooming's own
     SKILL.md describes.
   - **Open items → ticket NOW, not at publish (shift-left is a
     clock, not a label).** If genuinely open items remain (questions,
     contradictions, spec gaps), draft the ticket comment immediately
     — one line per item, grouped Questions / Contradictions / Gaps,
     no pipeline jargon; voice rules:
     `../qa-pipeline-code/references/results-comment-template.md` →
     "Writing rules" — show it, and ask ONE quick yes/no: "post these
     open questions to <KEY> now?". On yes, post before stage 3; the
     run continues either way. (An answer arriving while stages 3–4
     run can still fix the cases this run; a question first seen at
     the publish preview has already cost the whole phase — on a real
     ticket, five unanswered questions each became a blocked or
     contested case downstream.) Items already answered in chat are
     settled — do not post those. If the user declines, include the
     draft in the stage-6 publish preview instead.

3. **qa-checklist** — do not pause for clarifying questions: build on
   what is written, note ambiguity in the file ("needs
   clarification"). Produces `<ISSUEKEY>-checklist.md` (with channel
   tags).

4. **qa-test-cases** — do not pause: the grounding rule already
   handles ambiguity. Produces `<ISSUEKEY>-test-cases.md`.

5. **qa-run-analyzer** — run automatically; writes
   `<ISSUEKEY>-run-report.md`.

6. **Publish** — two destinations, ONE confirmation:
   (a) a new QA sub-task on the story (the code phase reads the
   checklist/test-cases from Jira); (b) a QA Service suite with the
   same requirements + cases — per
   **`references/qa-service-publish.md`** (field mapping, suite
   naming, re-run rules). (b) is on by default when the connector is
   present; publish (a) only — saying so once in the final response —
   when the connector is absent or the user declines. Never block (a)
   on (b).

   - **REQUIRED PAUSE / CONFIRM.** Before writing anything, show ONE
     preview: the parent story, the sub-task summary, the assignee,
     what will be posted, and the QA Service line (new suite path +
     requirement/case counts, or "appending to existing suite", or
     "skipped — connector not enabled"). Proceed only after an
     explicit yes.
   - Create via `createJiraIssue` with the project key, issue type,
     assignee, summary format, and label from
     **`references/publish-config.md`** (edit that file, not this one,
     when adopting the plugin), `parent` = the Story key.
     - Always create a NEW sub-task. **Supersede the old one:** if an
       earlier pipeline QA sub-task exists (same label), comment on it
       "Superseded by <NEW-KEY> (newer pipeline run)" and offer to
       close it. The code phase already prefers the newest; humans
       need the pointer.
   - **Description content** (a summary, NOT a second tracker):
     - Links to the spec/Confluence AC and the parent story.
     - The QA Service suite line: the full **bare** suite URL (never a
       markdown link — the connector drops hyperlinks) followed by
       `(N requirements / M cases, prefix <PREFIX>)`. Format:
       `qa-service-publish.md` → "Writing the suite link into Jira".
       Omit if the QA Service publish was skipped.
     - A "How to use this ticket" note: the checkbox tracker comment
       is the single source of truth for **manual** testing status —
       tick as you verify by hand; full steps live in the QA Service
       suite; automated results arrive later as two code-phase
       comments; the connector cannot tick checkboxes, so transfer
       automated PASS/FAIL by hand if you want one combined view.
     - The `⚠ SPECIAL ATTENTION` list and a short run-report summary.
     - An "Open questions from grooming" list — the same open items as
       the story comment, so a manual tester sees them without opening
       the story. Omit if none.
     - Do NOT paste the checklist here. One tracker only.
   - **Test cases → a follow-up comment (`addCommentToJiraIssue`), as
     an interactive checkbox tracker.** **One line per case — no
     Pre/Steps/Exp** (inlining them duplicated the machine archive
     99.3% and cost ~15,000 chars/ticket; the steps live in the suite
     and the local file):
     - `- [ ] TC-REQ-N.M — <name>  [<channel>] · <PREFIX>-<SEG>-NN`
       (id, short name, channel tag, QA Service case id).
     - Group by `### REQ-N — <label>  [channels]` headings mirroring
       the test-cases file; end with the statistics block from that
       file.
     - **Count gate — do not post a number you did not derive.**
       Mechanically recount the `### TC-REQ` headings and channel tags
       first (shell available:
       `python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <KEY>`;
       otherwise count the headings directly). If the statistics block
       disagrees, FIX the test-cases file first — never post the
       mismatched number or use it for suite levels.
     - Nothing else goes in this comment. If one case genuinely needs
       its steps visible in Jira (a blocker reproduced without QA
       Service access), add them to that ONE case.
   - **Machine-readable archive → only when QA Service did NOT
     publish.** The code phase reads cases from the suite when there
     is one:
     - **Suite published** → skip the archive comment, with ONE
       exception: the checklist's **structural checks that have no
       test case** (the `[UI]` presence / label / field-type checks)
       exist nowhere else — not in the suite, not in the tracker — and
       web-testing executes them. Post those, and only those, as a
       short fenced block headed
       `File: <ISSUEKEY>-checklist.md (structural checks only)`,
       preserving REQ grouping and channel tags. State in the final
       response that the code phase will read the cases from the
       suite. (Saves ~45,000 chars/ticket; one authoritative copy.)
     - **No suite (connector absent / user declined)** → post the full
       `<ISSUEKEY>-requirements.md`, `-checklist.md` and
       `-test-cases.md` contents, each inside its own fenced code
       block preceded by a plain `File: <name>` line, so
       `qa-pipeline-code` step 0 can rebuild them (the requirements
       file is what lets the code-phase analyzer re-verify upstream
       traceability). Do not shorten or reformat file contents. Choose
       fence lengths longer than any fence inside the file, and after
       posting, READ THE COMMENT BACK and verify each file's length
       against disk — Jira's markdown→ADF conversion has silently
       truncated an archive containing nested code fences.
     - **Size limit:** a Jira comment maxes out around ~32,000
       characters. Measure before posting; above ~30,000, split into
       several comments of the same shape, labelling split files
       `File: <name> (part i/N)` — split only at line boundaries. The
       code phase re-joins parts in order.

## Final response

After publishing, report:
- The paths of the four stage files + the run report.
- The QA sub-task key + URL and what was posted (tracker comment +
  archive comment).
- The QA Service suite path + requirement/case counts and the
  count-verification result (or "QA Service publish skipped —
  connector not enabled").
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items for the code phase.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat. Do NOT run `qa-manual-runsheet` here — the run sheet needs the
  automated verdicts to know what is left for the human.
