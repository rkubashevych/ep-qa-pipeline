---
name: qa-pipeline-docs
description: >
  Orchestrator for the documentation half of the QA pipeline (stages
  1-4) plus publishing. Given a Jira ticket, runs task-context, then
  requirements-grooming, then qa-checklist, then qa-test-cases, runs the
  run-analyzer, then publishes: the QA Service suite with the
  requirements, test cases and structural checks — the record the code
  phase reads from — and a QA sub-task on the story as the human-facing
  tracker (no file dumps into Jira). Auto-advances with default
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

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first — a new chat is not a reason to ask for an
upload; then the suite; asking the user is the last resort, not the
first — Jira archive comments are legacy, read only on pre-0.33 tickets).

**Where this phase writes:** `runs/<ISSUEKEY>/docs/` — create it before
stage 1 and print it once (`Run folder: runs/EP-1234/docs`). Every
stage 1–4 file and this phase's run report go there; a re-run
overwrites in place. Nothing is written to the repo root.

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

**Run clock (progress + time left):** stamp the wall clock (`date
+%H:%M`) at run start and after every stage below completes, then post
exactly ONE progress line per boundary — nothing more:

`⏱ Stage <n>/6 done — <stage name> · elapsed <E> min · ~<R> min left`

Initial per-stage budgets (minutes): task-context 8 · grooming 12
(+10 when recon runs) · checklist 7 · test-cases 12 · analyzer 5 ·
publish 12. Compute `<R>` as the unfinished stages' budgets scaled by
the run's own pace (elapsed ÷ sum of finished budgets, clamped to
0.5–3); round to 5 minutes and keep the `~`. Stamp both ends of any
user-waiting pause (the publish confirmation) and subtract the waited
time from elapsed — waiting is not pace. No shell available → skip
the clock silently.

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
   - **Recon first — self-answer the answerable (default when env
     access exists).** Grooming marks each open item SPEC (an intent
     decision only the PM/owner can make) or BEHAVIOUR ("how does the
     app work today?" — an observable fact). BEHAVIOUR items do not go
     to a human until observation has been tried: dispatch a
     READ-ONLY look at the running system (admin panel, live pages, a
     generated export, existing Confluence "how it works" pages — and,
     when a local repo clone exists, the code itself: a constant, a
     threshold, a column list is a current-behaviour fact, cited
     file+line; clone location and rules:
     `../pr-summary/references/bitbucket-access.md` → "Local clone")
     and write `<ISSUEKEY>-recon.md`, opening with this header verbatim:
     "These are observations of CURRENT behaviour, not requirements.
     They settle what a tester needs to know; they do not change the
     acceptance criteria. Where observed behaviour and the AC could
     diverge, the item is raised as a question, not resolved."
     Rules: strictly no writes; every observation carries its evidence
     (URL/element/response, per the Probe convention); recon facts may
     ground an expected result ONLY where the requirement itself
     references current behaviour — they never become requirements.
     Fold the answers back into the requirements file as "resolved by
     observation (recon)". No env access / user declines → skip, and
     BEHAVIOUR items go to the ticket like everything else. Real-run
     evidence: a run with recon ended with 1 open question; comparable
     runs without it posted 4–5, most answerable by looking.
   - **Open items → ticket NOW, not at publish (shift-left is a
     clock, not a label).** Only SPEC items and BEHAVIOUR items recon
     could not settle go to the ticket. Draft the comment immediately
     — one line per item, grouped Questions / Contradictions / Gaps,
     no pipeline jargon; voice rules:
     `../qa-pipeline-code/references/jira-writing-style.md`
     — show it, and ask ONE quick yes/no: "post these
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
     only after an explicit yes.
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
     - `- [ ] TC-REQ-N.M — <name>  [<channel>][ core] · <PREFIX>-<SEG>-NN`
       (id, short name, channel tag, ` [core]` marker where the case
       is the REQ's core case, QA Service case id).
     - Group by `### REQ-N — <label>  [channels]` headings mirroring
       the test-cases file; end with the statistics block from that
       file.
     - **Count gate — do not post a number you did not derive.**
       Mechanically recount the `### TC-REQ` headings and channel tags
       first (shell available:
       `python3 <plugin>/skills/qa-run-analyzer/scripts/reconcile_counts.py <KEY>`;
       otherwise count the headings directly). If the statistics block
       disagrees, FIX the test-cases file first — never post the
       mismatched number or use it for suite levels. The recount
       includes the `[core]` markers: the core count must equal the
       number of behavioural requirements — fix before posting.
     - Nothing else goes in this comment. If one case genuinely needs
       its steps visible in Jira (a blocker reproduced without QA
       Service access), add them to that ONE case.
   - **No machine-readable archive — retired in 0.33.0.** Nothing that
     is a file is pasted into Jira any more: not the requirements, not
     the checklist, not the test cases, not the "structural checks
     only" block. Why: the fenced dumps ran to 45,000 characters per
     ticket, were silently truncated by Jira's markdown→ADF conversion
     at least once, had to be split into parts and re-joined by a
     script, and duplicated a record the team already keeps in QA
     Service. The two things the archive used to carry now live where
     they belong:
     - **Cases and requirements** → the suite (already the rule since
       0.11.2).
     - **Structural checks** (the checklist's `[UI]` presence / label /
       field-type checks that have no test case) → the suite too, as
       `STRUCT` cases per `qa-service-publish.md` → "Structural checks".
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
- The paths of the four stage files + the run report
  (`runs/<ISSUEKEY>/docs/`).
- The QA sub-task key + URL and what was posted (description + tracker
  comment — no archive).
- The QA Service suite path + requirement/case counts and the
  count-verification result (or "QA Service publish skipped —
  connector not enabled").
- The run-analyzer health verdict (🟢/🟡/🔴 per category) and any
  ⚠ SPECIAL ATTENTION items for the code phase.
- The next step: run `qa-pipeline-code` on the Story key in a fresh
  chat. Do NOT run `qa-manual-runsheet` here — the run sheet needs the
  automated verdicts to know what is left for the human.
