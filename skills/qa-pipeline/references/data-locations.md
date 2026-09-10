# Where the pipeline's data lives

One home for a fact every skill in this pipeline needs and each used to
state differently. When a stage's `## Input` or `## Output` section and
this file disagree, this file wins.

## The three stores

| Store | Holds | Authoritative for |
|---|---|---|
| **The run folder** (`runs/<ISSUEKEY>/…`, below) | every `<ISSUEKEY>-*.md` stage file, the open-items ledger, the manual round's files — `-walk-plan.md`, `-walk-state.json`, `-walk-results.md`, `-testdata.json`, the optional runsheet `.xlsx` — evidence screenshots | the stage reports — and, where no archive was posted, the ONLY copy |
| **QA Service suite + test runs** | requirements, test cases; per-case verdicts as **test runs** (`list_test_runs` / `get_test_run` / `case_execution_history` — one run per pass, `test-runs.md`); `notes` hold only `discrepancy:` lines and pre-0.30 history | test cases and requirements whenever a suite exists; per-case verdicts always |
| **Jira** | the QA sub-task (description only), the wave-1 status line, the wave-2 human summary, retractions. **No archives since 0.33.0** — pre-0.33 tickets still carry legacy fenced dumps | nothing the pipeline generates; it is a publication surface, not a source |

## The run folder — `runs/<ISSUEKEY>/`

Since 0.32.0 every artefact a stage writes goes under `runs/`, never
into the repo root. The root held 688 `EP-*` files and 17 generator
scripts with live credentials when this rule was written; every
MAINTAINERS gotcha about `git add -A` exists because of that. `runs/`
is git-ignored as a whole.

```
runs/<ISSUEKEY>/
  <ISSUEKEY>-open-items.md      the ledger — one per ticket, no round
  docs/                         stages 1–4 (re-run = overwrite in place):
    <ISSUEKEY>-context.md · -requirements.md · -recon.md ·
    -checklist.md · -test-cases.md · -run-report.md
  r1/  r2/  r3/ …               one folder per code-phase PASS:
    <ISSUEKEY>-pr-summary.md · -sources.md · -code-review.md ·
    -api-testing.md · -web-testing.md · -web-evidence.md ·
    -run-report.md · -retest-scope.md · -human-summary.md ·
    -walk-plan.md · -walk-state.json · -walk-results.md ·
    -manual-results.md · -testdata.json · -testdata-notes.md ·
    -runsheet.xlsx · build_runsheet_<ISSUEKEY>.py · evidence/*.png
```

**File names do not change** — they keep the `<ISSUEKEY>-<stage>.md`
shape so every script, regex and archive label keeps working. Only the
directory changes.

**Rounds.** `r<N>` counts code-phase passes from 1: the first run is
`r1`, the first retest `r2`, and so on. The QA Service run titled
`<KEY> retest <k>` lives in `r<k+1>`. The `-retestN-` file-name suffix
is retired — the folder is the round, which is what lets
`reconcile_counts.py` find a retest's case file without being told
twice.

**Who decides the folder.** `qa-pipeline-docs` writes to `docs/`.
`qa-pipeline-code` step 0 establishes the pass folder before anything
else runs and prints it: a **resume** continues in the newest `r*`
folder (its run report is `partial`, or its QA Service run is still
`running` with `not_run` rows); a **new pass** — first run, retest mode,
bug-fix mode, "the fix landed" — creates `r<max+1>`. A stage invoked on
its own (not via an orchestrator) uses the newest `r*` folder, or asks
when none exists. Every stage creates the folder if it is missing;
none ever writes beside `runs/`.

**Round-suffixed names inside a folder are a mistake.** A file called
`<KEY>-retest3-code-review.md` inside `r4/` says the same thing twice
and breaks the scripts; the stale-artefact trap (EP-56197 r4 open-items
#24 — a round-3 results file read as round 4's) is exactly what the
folder prevents.

**Legacy.** Artefacts written before 0.32.0 sit in the repo root as
`<ISSUEKEY>-*`. They stay readable (resolution step 2 below) and are
never written to again. Optional tidy-up, by hand: move a ticket's root
files into `runs/<ISSUEKEY>/legacy/`.

## Resolution order for an input file

Look in this order and stop at the first hit:

1. **The run folder.** The current pass's `r<N>/` for stage reports,
   `docs/` for docs-phase files, `runs/<ISSUEKEY>/` for the ledger.
   For a *prior* round's file (a retest scope, a resume across rounds)
   look in the earlier `r*` folder by number — never in the current
   one. Files persist between chats on the same machine — in this
   setup the qa-pipeline-skill folder is mounted, and every previous
   run's files are still in it. **A new chat is not a reason to ask
   for an upload.** Look first.
2. **The repo root** — legacy artefacts of tickets run before 0.32.0
   (`<ISSUEKEY>-*` beside `runs/`). Read-only.
3. **The QA Service suite** — for `<ISSUEKEY>-test-cases.md` and
   `-requirements.md`, rebuild from `get_suite`. The suite is the system
   of record and moves between runs: a PM ruling, a QA-added case or a
   corrected expectation lands there, not in the file the docs phase
   wrote. On divergence the suite wins. **For prior verdicts** (a retest
   scope, a resume, stage 10's reconciliation) the previous pass's test
   run is the record — `get_test_run`, not the markdown reports and not
   the case notes.
4. **Legacy only — the archive comment on the QA sub-task** of a
   ticket run before 0.33.0 (fenced docs-phase files and results
   reports). Parse with
   `<plugin>/skills/qa-pipeline-code/scripts/extract_archive.py -o
   runs/<ISSUEKEY>/<folder>`. Never post a new one.
5. **Ask the user to attach it.** Last resort, not first.

## Two mistakes this file exists to prevent

**Never read a missing file as "that stage never ran."** On another
machine it means "cannot see it from here". Re-running a 45-minute
browser stage because a folder was not mounted is the specific waste
this ordering prevents. When a file is missing and the run looks like a
resume, PAUSE and ask whether this is the machine the earlier run used.

**Never treat file existence as stage completion.** Read the report's
`Completeness:` header. A `partial` report, or one whose Scope and
Statistics disagree, gets its stage re-dispatched for the missing cases.

## Which ticket receives what

The rule lives in `qa-pipeline-code/SKILL.md` step 6 and
`../qa-pipeline-code/references/results-comment-template.md`. In short:
every ticket — QA
sub-task, Story face, Bug or Defect — gets the wave-1 status line and
the wave-2 human summary, and nothing else; **no fenced file dumps
anywhere** since 0.33.0. The one cross-ticket comment is a
**retraction** (≤ 6 lines, no dumps), which goes to the ticket where the
retracted verdict was published, whatever ticket that is
(`test-runs.md` → "Retraction target rule").

## Credentials

Never in a committed file, never in Jira, never in a suite note.
`.env.qa-agents` in the mounted qa-pipeline-skill repo, then the e2e
`.env`, then env vars. The walk plan, the runsheet `.xlsx`,
`-testdata.json` and `build_runsheet_*.py` carry live credentials — they
live under `runs/` (git-ignored) and are never attached to Jira.
`-walk-state.json` and `-walk-results.md` carry none by rule.
