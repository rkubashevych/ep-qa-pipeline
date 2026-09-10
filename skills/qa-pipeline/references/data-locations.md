# Where the pipeline's data lives

One home for a fact every skill in this pipeline needs and each used to
state differently. When a stage's `## Input` section and this file
disagree, this file wins.

## The three stores

| Store | Holds | Authoritative for |
|---|---|---|
| **Working directory** | every `<ISSUEKEY>-*.md` stage file, the open-items ledger `<ISSUEKEY>-open-items.md` (per ticket, no round suffix), the manual round's files — `-walk-plan.md`, `-walk-state.json`, `-walk-results.md`, `-testdata.json`, the optional runsheet `.xlsx` — evidence screenshots | the stage reports — and, where no archive was posted, the ONLY copy |
| **QA Service suite + test runs** | requirements, test cases; per-case verdicts as **test runs** (`list_test_runs` / `get_test_run` / `case_execution_history` — one run per pass, `test-runs.md`); `notes` hold only `discrepancy:` lines and pre-0.30 history | test cases and requirements whenever a suite exists; per-case verdicts always |
| **Jira** | the docs-phase archive (QA sub-task, only when no suite), the results archive (**QA sub-task only** — 0.26.0), the wave-1 status line, the wave-2 human summary, the checkbox tracker | nothing the pipeline generates; it is a publication surface, not a source |

## Resolution order for an input file

Look in this order and stop at the first hit:

1. **The working directory.** Files persist between chats on the same
   machine — in this setup the qa-pipeline-skill folder is mounted, and
   every previous run's files are still in it. **A new chat is not a
   reason to ask for an upload.** Look first.
2. **The QA Service suite** — for `<ISSUEKEY>-test-cases.md` and
   `-requirements.md`, rebuild from `get_suite`. The suite is the system
   of record and moves between runs: a PM ruling, a QA-added case or a
   corrected expectation lands there, not in the file the docs phase
   wrote. On divergence the suite wins. **For prior verdicts** (a retest
   scope, a resume, stage 10's reconciliation) the previous pass's test
   run is the record — `get_test_run`, not the markdown reports and not
   the case notes.
3. **The archive comment on the QA sub-task** — docs-phase artefacts
   (requirements / checklist / test cases) and, since 0.26.0, results
   reports. Parse with
   `<plugin>/skills/qa-pipeline-code/scripts/extract_archive.py`.
   **Only tickets with a QA sub-task have one.** A Bug, a Defect (which
   is itself a sub-task and can never own one) and a small Story carry
   no archive by design.
4. **Ask the user to attach it.** Last resort, not first.

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

The archive target rule lives in `qa-pipeline-code/SKILL.md` step 6 and
its `references/results-comment-template.md`. In short: archives go to
QA sub-tasks only; a Story face, Bug or Defect gets the status line and
the human summary, and nothing else. The one exception is a
**retraction** (≤ 6 lines, no dumps), which goes to the ticket where the
retracted verdict was published, whatever ticket that is
(`test-runs.md` → "Retraction target rule").

## Credentials

Never in the working directory's committed files, never in Jira, never
in a suite note. `.env.qa-agents` in the mounted qa-pipeline-skill repo,
then the e2e `.env`, then env vars. The walk plan, the runsheet `.xlsx`
and `-testdata.json` carry live credentials and are git-ignored — they
are never attached to Jira. `-walk-state.json` and `-walk-results.md`
carry none by rule.
