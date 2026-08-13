# Triggering tests — should / should-NOT fire

The free tier of skill testing: after ANY edit to a SKILL.md
`description`, walk this list and check each query would route to the
right skill (read the descriptions as a fresh session would — the
description is the only thing discovery sees). A miss here is a
discovery regression even if the skill body is perfect.

Convention: ✅ = this skill must fire · ❌ = must NOT fire (the arrow
names who should handle it instead).

## task-context (stage 1)
- ✅ "pull task context for EP-55123"
- ✅ "process the ticket EP-54990 for the pipeline"
- ✅ "prepare task context" (with a Jira key/URL)
- ❌ "what does ticket EP-55123 say?" → plain chat answer, no skill
- ❌ "summarise this Jira ticket for my standup" → plain chat

## requirements-grooming (stage 2)
- ✅ "groom the requirements"
- ✅ "review the ticket requirements through a QA lens"
- ✅ (auto) after task-context inside qa-pipeline-docs
- ❌ "write requirements for a new feature" → not this pipeline; chat
- ❌ "groom the backlog" → PM activity, no skill

## qa-checklist (stage 3)
- ✅ "build a checklist from the requirements"
- ✅ "make the QA checklist"
- ❌ "make me a checklist for the release day" → generic list, chat
- ❌ "make a packing checklist" → chat

## qa-test-cases (stage 4)
- ✅ "write test cases from the checklist"
- ✅ "generate test cases for the requirements"
- ❌ "write unit tests for this function" → coding task, no skill
- ❌ "add these cases to QA Service" → qa-pipeline-docs publish step

## pr-summary (stage 5)
- ✅ "read the PR and map the changes"
- ✅ "PR summary for EP-54610"
- ❌ "review this PR" (quality judgement) → code-review, and only
  with test cases; a bare quality ask is /review-pr (backend) or chat
- ❌ "summarise this GitHub PR" → outside Bitbucket workspace, chat

## code-review (stage 6)
- ✅ "code review against the test cases"
- ✅ "check the implementation covers the cases"
- ❌ "review my code style / architecture" → not this skill (needs
  the test-cases file; style is out of scope by rule)
- ❌ "review the alpha branch PR comments" → review-pr skill

## api-testing (stage 7)
- ✅ "run the API checks"
- ✅ "hit the endpoints for the QA cases"
- ❌ "test this public REST API for me" → generic task, chat/code
- ❌ "run the API tests in the e2e repo" → that repo's own tooling

## web-testing (stage 8)
- ✅ "web testing", "test in the browser", "run the QA checks"
- ✅ "browser testing for EP-55123"
- ❌ "manual testing" / "I'll test by hand, prepare it" →
  qa-manual-runsheet (9)
- ❌ "I finished testing, here are my results" → qa-manual-results (10)

## qa-manual-runsheet (stage 9)
- ✅ "prepare the manual tests", "make a run sheet"
- ✅ "set up the data so I can just check the cases"
- ❌ "run the manual tests yourself" → web-testing does browser runs
- ❌ "the sheet is filled, update the results" → qa-manual-results
- ❌ "retest EP-1234, the fix landed" → qa-pipeline-code retest mode
  (which then invokes this stage scoped; invoked bare on a story with
  prior artifacts, this stage must PAUSE and ask full-run vs retest)

## qa-manual-results (stage 10)
- ✅ "ingest the manual results"
- ✅ "the tester finished the run sheet" / pasted TC-Result-Notes table
- ✅ "write back my manual results"
- ❌ "build me the run sheet" → qa-manual-runsheet
- ❌ "what were the results of the run?" → read the report/Jira, chat

## qa-run-analyzer
- ✅ "analyze the run", "how did that run go"
- ✅ "run health check"
- ❌ "analyze this log file" → generic task, chat
- ❌ "why did this test fail?" → diagnosing-bugs or chat

## qa-pipeline-docs (orchestrator)
- ✅ "run the QA docs pipeline for EP-55123"
- ✅ "build the test cases for a ticket" (full flow implied)
- ❌ "publish this page to Confluence" → confluence-sync
- ❌ "just groom the requirements" → requirements-grooming alone

## qa-pipeline-code (orchestrator)
- ✅ "run the QA code pipeline"
- ✅ "review the PRs and test in the browser for EP-55123"
- ✅ "the fix landed, retest EP-55123" (retest mode)
- ✅ "test the bugfix EP-56133" (bug-fix mode — Bug ticket, no docs
  phase; derives mini cases from the ticket's repro steps)
- ❌ "review this PR" (alone) → pr-summary/code-review or review-pr
- ❌ "run all the tests" (in a repo context) → that repo's test runner
