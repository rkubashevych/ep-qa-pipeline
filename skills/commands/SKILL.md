---
name: commands
disable-model-invocation: true
description: >
  Lists every ep-qa-pipeline command: what it does and what to type.
  Prints a fixed table; runs nothing.
---

# ep-qa-pipeline commands

Print the section below as it is, then stop. Do not run any of the
commands, read a ticket or check the environment.

---

**Plain words work for everything in the first three groups.** The
single stages (fourth group) start only from their slash command; the
orchestrators run them for you.

**Start here**

| Command | What it does | Type |
|---|---|---|
| `/ep-qa-pipeline:qa-pipeline` | Reads the ticket's state and proposes the route: refinement, docs, code, bug-fix, retest, walk, results, RC smoke | "qa this ticket EP-1234", "test this" |

**Modes**

| Command | What it does | Type |
|---|---|---|
| `/ep-qa-pipeline:qa-refinement` | Before estimation: questions comment + QA sizing, no test cases | "prepare EP-1234 for estimation" |
| `/ep-qa-pipeline:qa-pipeline-docs` | Docs phase: context → grooming → test cases → QA Service suite + QA sub-task | "run the QA docs pipeline for EP-1234" |
| `/ep-qa-pipeline:qa-pipeline-code` | Code phase: PR → code review → API → browser → verdicts → walk plan. Also retest and bug-fix modes | "run the QA code pipeline", "retest EP-1234", "test the bugfix EP-1234" |
| `/ep-qa-pipeline:qa-rc-smoke` | Release candidate: each scope item on RC (code, build, core behaviour) | "smoke test the RC for EP-1234" |
| `/ep-qa-pipeline:qa-manual-runsheet` | Fixtures + walk plan (the code phase's last step) | "build the walk plan for EP-1234" |
| `/ep-qa-pipeline:qa-manual-walk` | The guided hand-test, one card at a time | "walk me through EP-1234" |
| `/ep-qa-pipeline:qa-manual-results` | Writes the walk or a filled run sheet back to QA Service and Jira | "ingest the manual results" |
| `/ep-qa-pipeline:qa-api-tests` | Turns the ticket's API cases into real tests in QA Service + frontend test sub-task | "automate the API cases for EP-1234" |

**Checks**

| Command | What it does | Type |
|---|---|---|
| `/ep-qa-pipeline:qa-run-analyzer` | Health check of a finished run | "analyze the run for EP-1234" |
| `/ep-qa-pipeline:qa-service-watch` | What changed in QA Service since last week | "check QA Service for updates" |

**Single stages — slash command only**

Each one reads the previous stage's file from `~/.ep-qa/runs/<KEY>/`,
so run it on a ticket whose earlier stages already ran.

| Command | Stage | What it does |
|---|---|---|
| `/ep-qa-pipeline:task-context EP-1234` | 1 | Ticket + AC pages → `<KEY>-context.md` |
| `/ep-qa-pipeline:requirements-grooming EP-1234` | 2 | Context → numbered requirements + open questions |
| `/ep-qa-pipeline:qa-test-cases EP-1234` | 4 | Requirements → test cases + structural checks |
| `/ep-qa-pipeline:pr-summary EP-1234` | 5 | Map of the PR / branch changes |
| `/ep-qa-pipeline:code-review EP-1234` | 6 | Each test case checked against the PR code |
| `/ep-qa-pipeline:api-testing EP-1234` | 7 | `[API]` cases run against the test env |
| `/ep-qa-pipeline:web-testing EP-1234` | 8 | `[UI]` cases run in the browser |

`/ep-qa-pipeline:commands` prints this list.
