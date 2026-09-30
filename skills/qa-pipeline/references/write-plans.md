# Write plans — what the user approved is what gets written

Every outward write in this pipeline sits behind a REQUIRED PAUSE: the
publish, the wave-1 run and status line, the bug offer, the stage-10
write-back, the refinement questions, the RC smoke comment. Until
0.47.0 the only record of what was approved was the user's "yes" in
chat. The 40–90 calls that followed were composed afresh from the
model's working memory.

What landed could therefore differ from what was shown, and nothing
would notice. The ways it happens are ordinary:
- two late cases added "while we're at it";
- a comment reworded after approval;
- a context compaction halfway through a 90-case publish, after which
  the payload is rebuilt from a summary.

This protocol makes the comparison mechanical. It is borrowed from
qa-service's implement consent token (`lib/server/mcp/consent.ts`),
which hashes the exact plan the user saw and refuses to apply a plan
whose hash differs.

## The plan file

`runs/<KEY>/<folder>/<KEY>-<step>-plan.json`, next to the reports of
the step that writes:
- `docs/` for the docs publish and the refinement comment;
- `r<N>/` for the code-phase steps and stage 10;
- the RC ticket's folder for the RC smoke.

```json
{"step": "qa-pipeline-code step 6 (a) record the run",
 "ticket": "EP-1234",
 "writes": [
   {"tool": "create_test_run", "args": {"suiteId": "…", "title": "EP-1234 first run 2026-09-30 — alpha2", "env": "alpha2", "caseIds": ["…"]}},
   {"tool": "record_case_result", "args": {"runId": "$run", "caseId": "EP-FAV-UI-01", "verdict": "pass", "source": "machine", "principal": "ep-qa-pipeline agent (EP-1234 first run, stage 8)", "note": "…", "evidence": []}},
   {"tool": "addCommentToJiraIssue", "args": {"issueKey": "EP-1235", "commentBody": "QA automated pass complete — …"}}
 ]}
```

**Rules for the file**
- **Exactly the arguments that will be sent.** Every comment body and
  every note is written in full. There are no placeholders except
  `$<name>` for an id a previous write in the same plan returns
  (`$run`, `$subtask`, `$suite`). Those are filled at execution time
  and are the only difference allowed.
- **One plan per confirmation.** Where a pause asks two questions
  (step 6's "Record the run?" and "Post the status line?"), there are
  two plans. A yes to one approves only that one.
- **The plan is a run artefact:** it sits under `$EP_QA_HOME`, never in
  the checkout. It holds no secret by construction, because the write
  tools take none.

## The sequence

1. **Build the plan file**, then run
   `python3 <plugin>/skills/qa-pipeline/scripts/plan_hash.py make <plan>`.
   It freezes an approved copy and prints the write count per tool and
   `sha256 <12 chars>`.
2. **Show the preview from the file.** Use `plan_hash.py show <plan>`
   for the list, plus whatever the step's own preview rules require
   (counts, the `fail`s by case, the bug drafts). End the preview with
   the line `Plan: <file name> · <N> writes · sha256 <12 chars>`.
3. **On an explicit yes**, run `plan_hash.py check <plan>`.
   - `OK` → proceed to step 4.
   - `CHANGED` → write nothing. Show the lines `check` printed (which
     write was added, removed or changed, and which arguments) and ask
     again. A new yes needs a new `make`.
4. **Execute the writes in file order, reading each call's arguments
   from the file.** Never recompose a call from memory. After a
   compaction, re-read the plan file rather than the summary of it.
5. **A write fails or must change mid-way** (a tool rejects an
   argument, a value turns out wrong):
   - stop;
   - correct the plan file;
   - `make` again;
   - show what changed, including the writes already done;
   - ask again.

   Writes already made are not repeated. The re-issued plan lists only
   what is left, and its preview says so. Any `$<name>` placeholder a
   done write already answered is **replaced by the real id** (the run
   id, the issue key) in the new plan, since nothing in it can return
   that value any more.
6. **Record the outcome** in the step's report: the plan file name, its
   hash, and the ids the writes returned (run id, comment id, issue
   keys).

**No shell** (a Cowork session without one): write the plan file
anyway, show it, and execute from it. Say `Plan: <file> · not hashed —
no shell` in the preview. The file still pins what was approved, but
nothing checks it mechanically.

## What this does not do

- **It is a discipline, not an enforcement.** Nothing outside the model
  stops a call that is not in the plan: MCP writes are not intercepted
  the way `scripts/git_guard.py` intercepts `git add -A`. What it
  changes:
  - the comparison between "approved" and "about to send" is a script's
    output, not a recollection;
  - the preview and the writes come from the same file.
- **It does not judge content.** The publication gate
  (`sources-of-record.md` §7), the quote check (§8) and each step's own
  preview rules still apply to what goes into the plan.

## Where it applies

| Pause | Plan file |
|---|---|
| `qa-pipeline-docs` step 6: the sub-task + the suite publish | `docs/<KEY>-publish-plan.json` |
| `qa-refinement`: the questions comment (and a re-run's in-place edit) | `docs/<KEY>-questions-plan.json` |
| `qa-pipeline-code` step 6 (a): the run + its verdicts | `r<N>/<KEY>-run-plan.json` |
| `qa-pipeline-code` step 6 (b): the wave-1 status line | `r<N>/<KEY>-status-plan.json` |
| `qa-pipeline-code` step 7 (the per-bug yes chooses which drafts enter the plan; the plan is then confirmed once, as a whole), and the bug-fix mini-suite publish | `r<N>/<KEY>-bugs-plan.json` / `r<N>/<KEY>-minisuite-plan.json` |
| `qa-manual-results` step 4: bugs, verdicts, retractions, the human summary | `r<N>/<KEY>-writeback-plan.json` |
| `qa-manual-results` step 4b: the handback (story note, transition, reassignment) | `r<N>/<KEY>-handback-plan.json` |
| `qa-rc-smoke` step 6: the results comment (the run is covered by the step-1 yes) | `<RC-KEY>-rc-comment-plan.json` |

A pause not in this table still follows the protocol whenever it
confirms more than one write.
