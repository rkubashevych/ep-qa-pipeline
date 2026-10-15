---
name: qa-pipeline-docs
description: >
  Orchestrator for the docs half of the QA pipeline (stages 1-4 plus
  publish). Given a Jira ticket: task-context, requirements-grooming,
  QA Service case generation and test discovery, qa-test-cases and the
  run-analyzer, then publishes the QA Service suite and a QA sub-task,
  pausing to confirm the writes. Use when the user says "run the QA
  docs pipeline", "build the test cases for a ticket", "groom and
  write test cases", or "publish the test cases / add these cases to
  QA Service" (publish-only). Only questions and a QA estimate before
  estimation, no test cases → qa-refinement.
---

# QA Pipeline -- Docs (stages 1-4 + publish)

> **Tool names:** bare names like `createJiraIssue` /
> `addCommentToJiraIssue` (here and in this skill's references) are
> tools of the **Atlassian MCP connector**; `create_suite` /
> `create_test_case` / `edit_requirement` etc. belong to the
> **QA Service MCP connector**. The install-specific server prefix
> varies — match by tool name on the server that provides it.

Runs the first four pipeline stages end to end, health-checks the run,
then publishes to the QA Service suite and a QA sub-task on the story.

## Input

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
— run folder, then the suite; a new chat is no reason to ask.

**Where this phase writes:** `runs/<ISSUEKEY>/docs/` under
`$EP_QA_HOME` (`../qa-pipeline/references/environment.md`; nothing
reachable → PAUSE, never the plugin checkout) — create it before
stage 1 and print it once (`Run folder: ~/.ep-qa/runs/EP-1234/docs`). Every
stage 1–4 file and this phase's run report go there; a re-run
overwrites in place. Nothing is written to the repo root.

**Publish-only mode.** When the user asks only to publish ("add these
cases to QA Service", "publish the test cases for EP-1234") and
`runs/<ISSUEKEY>/docs/<ISSUEKEY>-test-cases.md` already exists, skip
stages 1–4: run step 5 (the analyzer and its count gate) and step 6
(publish) on the files that are there. A missing stage file → name it
and offer the full run; never publish a file the analyzer has not
counted.

- A Jira ticket key or URL (e.g. `EP-44730`). If the key is itself a
  sub-task, use its parent Story as the story for publishing.

**After a refinement run.** When `runs/<ISSUEKEY>/docs/` already holds
`qa-refinement` output (`-open-questions.md`, `-answers.md`,
`-recon.md`, `-sizing.md`), read `references/special-cases.md` §1
before stage 1: stages 1–2 re-run, recon is reused, only new questions
are asked, and the publish adopts the QA sub-task it names.

**Shift-left.** The docs phase needs only the ticket, not the code. If
the ticket's status shows dev has not started or is in progress, say
the findings are in time to act on; never block the run on status.

## How it runs

**First task of the week → QA Service watch.** Before stage 1,
`qs_watch.py due` (`../qa-service-watch/SKILL.md` → "When it runs");
due → run that skill (read-only, ~1 min, ≤5 lines), then continue.

Post one short line per stage boundary (`Stage <n>/6 done — <stage
name>`) and nothing more between stages.

Execute each stage by reading its `SKILL.md` and following it **in
full** — do not summarise or shortcut it. Stages share the run folder
(`runs/<KEY>/docs/`); pass each output file to the next automatically.

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
   - **Recon first — self-answer the answerable (default when env
     access exists).** Grooming marks each open item SPEC (an intent
     decision only the PM/owner can make) or BEHAVIOUR ("how does the
     app work today?" — an observable fact). BEHAVIOUR items do not go
     to a human until observation has been tried: run recon per
     **`../qa-pipeline/references/recon.md`** — read-only except the
     one narrow, restored setting flip that file allows; folded back
     into the requirements file as "Resolved by observation (recon)".
     No env access / user declines → skip, and BEHAVIOUR items go to
     the ticket like everything else.
   - **Open items → ticket NOW, not at publish (shift-left is a
     clock, not a label).** Only SPEC items and BEHAVIOUR items recon
     could not settle go to the ticket. Draft the comment immediately
     in the shape of `../qa-pipeline-code/references/jira-writing-style.md`
     → "Grooming open-questions comment" (read it in full: questions
     only, every name checked in its `## Names` table), save it as
     `<ISSUEKEY>-open-questions.md`, show it, and ask ONE quick yes/no:
     "post these open questions to <KEY> now?". On yes, post before
     stage 4 — an answer arriving while stages 3–4 run can still fix
     the cases; the run continues either way. Items already answered in
     chat are settled — do not post those. If the user declines,
     include the draft in the stage-6 publish preview instead.

3. **QA Service first** — per
   **`references/qa-service-first.md`**. With the connector present,
   QA Service authors before we do: the suite and its header (`teams`,
   `jiraKeys` + the rest), this ticket's requirements, then
   `start_generate_test_cases` (`full` on an empty suite, `gaps`
   otherwise) and `discover_tests` over the feature's existing tests.
   **REQUIRED PAUSE / CONFIRM** — its own preview and plan
   (`docs/<ISSUEKEY>-qs-plan.json`), because it writes to shared data
   before stage 4. Produces `<ISSUEKEY>-qs-cases.md`, the export stage 4
   reads. No connector, or the user says no → skip in one line; stage 4
   writes every case.

4. **qa-test-cases** — do not pause: build on what is written, note
   ambiguity as "needs clarification"; the grounding rule handles the
   rest. With `<ISSUEKEY>-qs-cases.md` present it adopts the QA Service
   cases that fit (`Adopted:` line), writes only what is missing, and
   lists the rest under "QA Service cases not adopted" with a reason.
   Every case may carry a `Level:` line (the lowest automation level
   that can prove it, `U` first for a pure rule). Produces
   `<ISSUEKEY>-test-cases.md` — the test cases AND the
   Structural checks section (the former checklist's `[UI]` presence /
   label / type lines, id `REQ-N/struct-k`), each group with its
   `Covers: AC-n` line.

   The AC ledger runs through all three stages: stage 1 writes one
   `AC-n` bullet per criterion and the page/captured count, stage 2
   maps every REQ to its ids, stage 4 carries them on `Covers:`. Step
   6's count gate checks it.

5. **qa-run-analyzer** — run automatically; writes
   `<ISSUEKEY>-run-report.md`.

6. **Publish** — two destinations, ONE confirmation:
   (a) a new QA sub-task on the story (the human-facing tracker); (b)
   the QA Service suite with the requirements, cases **and the
   structural checks** — per **`references/qa-service-publish.md`**
   (field mapping, suite naming, re-run rules, the STRUCT cases). **(b)
   is the record the code phase reads from.** When stage 3 ran, the suite, its
   header and the requirements already exist: (b) edits the
   requirements the user's answers changed, creates only the cases
   written here, stamps the adopted ones and marks the not-adopted ones
   (`qa-service-publish.md` → "Adopted cases" and "Cases stage 4 did
   not adopt"). It also files this ticket's requirements into topic
   folders and, as the last write, starts QA Service's review pass over
   the ticket's requirements and cases, which runs in the background
   (Procedure steps 4b and 7). (b) is on whenever the connector
   is present; when it is absent or the user declines, publish (a) only
   and say so plainly in the final response: the code phase for this
   ticket can then run only on this machine, from
   `runs/<ISSUEKEY>/docs/`. Never block (a) on (b).

   - **Count gate — do not publish a number you did not derive.**
     Before the preview, run `python3
     <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <KEY>`
     (no shell → count the `### TC-REQ` headings, tags, `[core]`
     markers and the `source:` / `Covers:` ids directly):
     - its "AC ledger" lines: an uncovered `AC-n` or a page/captured
       mismatch is fixed before anything is published — a suite that
       misses a criterion is the one thing this phase exists to prevent;
     - headings, channel tags and `[core]` markers: a statistics block
       that disagrees is fixed in the test-cases file first, and the
       core count must equal the number of behavioural requirements.
       Never publish a mismatched number or use it for suite levels.
   - **REQUIRED PAUSE / CONFIRM.** Before writing anything, show ONE
     preview: the parent story, the sub-task summary, the assignee,
     what will be posted, and the QA Service line (new suite path +
     requirement / case / structural-check counts, or "appending to
     existing suite", or "skipped — connector not enabled: code phase
     will read runs/<ISSUEKEY>/docs/ on this machine only"). Proceed
     only after an explicit yes. The writes are one plan,
     `docs/<ISSUEKEY>-publish-plan.json`
     (`../qa-pipeline/references/write-plans.md`): `make` before the
     preview, which ends with its `Plan: … sha256 …` line; `check` after
     the yes; every `createJiraIssue` / `create_*` / `edit_*` call
     executed from the file — never recomposed, and after a compaction
     re-read from it.
   - Create via `createJiraIssue` with the project key, issue type,
     assignee, summary format, and label from
     **`references/publish-config.md`** (edit that file, not this one,
     when adopting the plugin), `parent` = the Story key.
     - Always create a NEW sub-task. **Supersede the old one:** if an
       earlier pipeline QA sub-task exists (same label), comment on it
       "Superseded by <NEW-KEY> (newer pipeline run)" and offer to
       close it. The code phase already prefers the newest; humans
       need the pointer.
     - **Exception — a QA sub-task a human already created.** Before
       the preview, look for one per `references/special-cases.md` §2
       (no pipeline label; `parent = <KEY>` with a summary starting
       "QA", or the `QA sub-task:` line of `<KEY>-sizing.md`). Found →
       offer in the SAME preview to adopt it instead. Never replace
       what a person wrote.
   - **Description content** (a summary, NOT a second tracker):
     - Links to the spec/Confluence AC and the parent story.
     - The QA Service suite line: the full **bare** suite URL (never a
       markdown link — the connector drops hyperlinks) followed by
       `(N requirements / M cases, prefix <PREFIX>)`. Format:
       `qa-service-publish.md` → "Writing the suite link into Jira".
       Omit if the QA Service publish was skipped.
     - A "How to use this ticket" note: the cases and their status
       live in the QA Service suite (link above) and its test runs —
       there is nothing to tick here; this ticket receives one status
       line when the automated pass finishes and one human-readable
       summary when the manual round is written back.
     - The `⚠ SPECIAL ATTENTION` list and a short run-report summary.
     - An "Open questions from grooming" list — the same open items as
       the story comment, so a manual tester sees them without opening
       the story. Omit if none.
     - Do NOT paste the cases or the structural checks here.
   - **Jira gets the description only** — no tracker comment, no file
     pasted (requirements, cases, structural checks). The suite holds
     all three, the per-ticket scope (`detail.ticket` on every case,
     `sources: [{kind: jira, label: <KEY>}]` on every requirement) and
     the REQ-N / TC-REQ-N.M ↔ stableId map (`detail.pipelineId`) —
     `qa-service-publish.md` → "Mapping"; the QA Service run is the
     tracker. **No suite** (connector absent / user declined) → nothing
     is posted in their place: `runs/<ISSUEKEY>/docs/` is the only copy,
     the code phase reads it on this machine and pauses on any other
     (`qa-pipeline-code` step 0). Say so in the final response.

## Final response

After publishing, report:
- The paths of the three stage files (context, requirements,
  test-cases; plus recon when it ran) + the run report
  (`runs/<ISSUEKEY>/docs/`).
- The QA sub-task key + URL and what was posted (the description only
  — no tracker comment, no archive).
- The QA Service suite path + requirement/case counts and the
  count-verification result (or "QA Service publish skipped —
  connector not enabled"); the split "adopted from QA Service A ·
  written here W · code-level K"; the tests discovery imported, or the
  To do when discovery could not run; the review pass: its verdicts if
  it finished, else "running — job <id>".
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items for the code phase.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat. Do NOT run `qa-manual-runsheet` here — the walk plan needs the
  automated verdicts to know what is left for the human.
