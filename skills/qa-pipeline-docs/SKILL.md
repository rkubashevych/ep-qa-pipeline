---
name: qa-pipeline-docs
description: >
  Orchestrator for the documentation half of the QA pipeline (stages
  1, 2 and 4 — stage 3 folded into 4 in 0.40.0) plus publishing. Given
  a Jira ticket, runs task-context, then requirements-grooming, then
  qa-test-cases, runs the run-analyzer, then publishes: the QA Service suite with the
  requirements, test cases and structural checks — the record the code
  phase reads from — and a QA sub-task on the story as the human-facing
  tracker (no file dumps into Jira). Auto-advances with default
  decisions, pausing only to confirm the publish (say "interactive
  mode" to get the grooming pause back). Use it
  when the user says "run the QA docs pipeline", "build the test cases
  for a ticket", "groom and write test cases", "publish the test cases
  / add these cases to QA Service" (publish-only on existing files), or
  gives a ticket and wants the full test-case set without
  invoking each stage by hand. Only questions and a QA estimate before
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
then publishes to a QA sub-task on the story. Each stage is a real
skill in this repo — this orchestrator sequences them, it does not
reimplement them.

## Input

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

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

## After a refinement run — reuse, don't redo (0.45.0)

When `runs/<ISSUEKEY>/docs/` already holds `qa-refinement` output
(`-open-questions.md`, `-answers.md`, `-recon.md`, `-sizing.md`), say so
in the first line ("Refinement run found: N questions, M answered") and
carry each file forward:

- **Stages 1–2 still re-run.** The ticket changed, which is the point
  of asking. task-context re-reads the description and comments, where
  the answers were written. Grooming also reads `-answers.md` as the
  owner's answers (its Inputs) and re-applies every settled one as
  `resolved by the owner (<date>)`, including the inferred ones and
  the "AC still says otherwise" notes that no Jira field carries.
- **Recon is reused, not repeated.** Keep `-recon.md`. Run recon only
  for BEHAVIOUR items it does not cover, and append them as the next
  `B<n>` sections. Never overwrite the file (`recon.md` → "Reuse").
- **Questions: only what is new or still open.** Before step 2 drafts
  anything, read `-open-questions.md` and `-answers.md`:
  - a question the owner answered is settled and never asked again;
  - one still waiting (not clear, partial, or in a posted follow-up
    with no answer) is listed in the publish preview as "still open
    since <date>", not re-posted;
  - only items grooming raises for the first time go into a new
    comment, in the same shape.
- **Publish adopts the QA sub-task** named on `-sizing.md`'s
  `QA sub-task:` line (step 6).

## When to run (shift-left)

The docs phase needs only the ticket, not the code — run it as EARLY
as possible (refinement, or as soon as the ticket is written). Early,
grooming findings can still fix the spec and prevent bugs, and devs
can self-check against the published cases. At QA time it still works,
but findings arrive after the code is written. If the ticket's status
shows dev has not started or is in progress, say so and note the
findings are in time to act on; never block the run on status.

## How it runs

Post one short line per stage boundary (`Stage <n>/5 done — <stage
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
     **`../qa-pipeline/references/recon.md`** (the single home since
     0.45.0 — sources in order docs → refreshed local clone → the
     running system; read-only except one narrow, restored setting
     flip; the verbatim header; folding back into the requirements
     file as "Resolved by observation (recon)"). No env access / user
     declines → skip, and BEHAVIOUR items go to the ticket like
     everything else.
   - **Open items → ticket NOW, not at publish (shift-left is a
     clock, not a label).** Only SPEC items and BEHAVIOUR items recon
     could not settle go to the ticket. Draft the comment immediately
     in the **questions-only shape**
     (`../qa-pipeline-code/references/jira-writing-style.md` →
     "Grooming open-questions comment": one intro line, then numbered
     one-line questions — no section headers, no evidence), save it as
     `<ISSUEKEY>-open-questions.md`, show it, and ask ONE quick yes/no:
     "post these open questions to <KEY> now?". On yes, post before stage 4; the
     run continues either way. (An answer arriving while stages 3–4
     run can still fix the cases this run; a question first seen at
     the publish preview has already cost the whole phase — on a real
     ticket, five unanswered questions each became a blocked or
     contested case downstream.) Items already answered in chat are
     settled — do not post those. If the user declines, include the
     draft in the stage-6 publish preview instead.

3. *(retired in 0.40.0 — the checklist is now the first working step
   of qa-test-cases; no file, no pause. Stage numbers 4+ are unchanged
   so every cross-reference still holds.)*

4. **qa-test-cases** — do not pause: build on what is written, note
   ambiguity as "needs clarification"; the grounding rule handles the
   rest. Produces `<ISSUEKEY>-test-cases.md` — the test cases AND the
   Structural checks section (the former checklist's `[UI]` presence /
   label / type lines, id `REQ-N/struct-k`), each group with its
   `Covers: AC-n` line.

   **The AC ledger runs through all three stages (0.42.0):** stage 1
   writes one `AC-n` bullet per criterion and the page/captured count,
   stage 2 maps every REQ to its ids, stage 4 carries them on `Covers:`.
   Before the publish, run `reconcile_counts.py <ISSUEKEY>` and read its
   "AC ledger" lines: an uncovered `AC-n` or a page/captured mismatch is
   fixed before anything is published — a suite that misses a criterion
   is the one thing this phase exists to prevent.

5. **qa-run-analyzer** — run automatically; writes
   `<ISSUEKEY>-run-report.md`.

6. **Publish** — two destinations, ONE confirmation:
   (a) a new QA sub-task on the story (the human-facing tracker); (b)
   the QA Service suite with the requirements, cases **and the
   structural checks** — per **`references/qa-service-publish.md`**
   (field mapping, suite naming, re-run rules, the STRUCT cases). **(b)
   is the record the code phase reads from** — since 0.33.0 no fenced
   copy of any file is posted to Jira. (b) is on whenever the connector
   is present; when it is absent or the user declines, publish (a) only
   and say so plainly in the final response: the code phase for this
   ticket can then run only on this machine, from
   `runs/<ISSUEKEY>/docs/`. Never block (a) on (b).

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
     - **Exception — adopt a QA sub-task a human already created
       (0.45.0).** When the story has a QA sub-task WITHOUT the pipeline
       label — typically created at estimation, before the pipeline ran
       (EP-57799 on EP-56227) — creating a second one splits the
       tracker. Find candidates with `parent = <KEY>` and a summary
       starting "QA" (or the `QA sub-task` type where the project has
       one); `qa-refinement` records the one it saw on the
       `QA sub-task:` line of `<KEY>-sizing.md`. Offer in the SAME
       preview: "adopt <KEY-X> instead of creating a new sub-task".
       On yes:
       - add the label;
       - keep the summary, the assignee and the human's description;
       - append the pipeline description below it, under a `QA
         pipeline` heading. Never replace what a person wrote.
       On no, create a new one as usual and leave the human's sub-task
       untouched. The supersede rule does not apply to it, because it
       was never a pipeline sub-task.
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
   - **No checkbox tracker comment — retired in 0.34.0.** Until then a
     follow-up comment listed one `- [ ] TC-REQ-N.M …` line per case.
     Nobody ticked it (the connector cannot; the human's verdicts go to
     the run), and the two things it actually carried now live in the
     suite itself: the per-ticket **scope** (`detail.ticket` on every
     case, `sources: [{kind: jira, label: <KEY>}]` on every requirement)
     and the **REQ-N / TC-REQ-N.M ↔ stableId map** (`detail.pipelineId`
     on both) — `qa-service-publish.md` → "Mapping". The QA Service run
     is the tracker.
   - **Count gate — do not publish a number you did not derive.**
     Before the preview, mechanically recount the `### TC-REQ` headings
     and channel tags (shell available:
     `python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <KEY>`;
     otherwise count the headings directly). If the statistics block
     disagrees, FIX the test-cases file first — never publish the
     mismatched number or use it for suite levels. The recount includes
     the `[core]` markers: the core count must equal the number of
     behavioural requirements — fix before publishing.
   - **No machine-readable archive — retired in 0.33.0.** Nothing that
     is a file is pasted into Jira any more: not the requirements, not
     the test cases, not the "structural checks only" block. Why: the fenced dumps ran to 45,000 characters per
     ticket, were silently truncated by Jira's markdown→ADF conversion
     at least once, had to be split into parts and re-joined by a
     script, and duplicated a record the team already keeps in QA
     Service. The two things the archive used to carry now live where
     they belong:
     - **Cases and requirements** → the suite (already the rule since
       0.11.2).
     - **Structural checks** (the `[UI]` presence / label / field-type
       lines in the test-cases file's Structural checks section — no
       test case by design) → the suite too, as `STRUCT` cases per
       `qa-service-publish.md` → "Structural checks".
       They used to live only in a fenced block on the sub-task, which
       also meant web-testing's verdicts on them never reached the run.
       Now they are roster cases like any other.
     - **No suite** (connector absent / user declined) → nothing is
       posted in their place. `runs/<ISSUEKEY>/docs/` is the only copy;
       the code phase reads it on this machine and pauses on any other
       (`qa-pipeline-code` step 0). Say so in the final response.
     Pre-0.33 tickets still carry archive comments; the code phase can
     still read them (`scripts/extract_archive.py`, legacy).

## Final response

After publishing, report:
- The paths of the three stage files (context, requirements,
  test-cases; plus recon when it ran) + the run report
  (`runs/<ISSUEKEY>/docs/`).
- The QA sub-task key + URL and what was posted (the description only
  — no tracker comment, no archive).
- The QA Service suite path + requirement/case counts and the
  count-verification result (or "QA Service publish skipped —
  connector not enabled").
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items for the code phase.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat. Do NOT run `qa-manual-runsheet` here — the walk plan needs the
  automated verdicts to know what is left for the human.
