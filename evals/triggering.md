# Triggering tests — should / should-NOT fire

The free tier of skill testing: after ANY edit to a SKILL.md
`description`, walk this list and check each query would route to the
right skill (read the descriptions as a fresh session would — the
description is the only thing discovery sees). A miss here is a
discovery regression even if the skill body is perfect.

Convention: ✅ = this skill must fire · ❌ = must NOT fire (the arrow
names who should handle it instead).

**Slash-only skills (0.61.0).** The seven single stages carry
`disable-model-invocation: true`: no phrase starts them, and their
descriptions do not load into a session — so no visible description
may redirect to them by bare name (0.70.0): a redirect names the
orchestrator that owns the stage, or the full slash command. Their ✅
is the slash command; the orchestrators still run them by reading the
SKILL.md. A phrase that used to start one stage now goes to the
dispatcher or the orchestrator that owns the stage (both propose
before they run), or Claude names the stage's slash command — the
"→" on each ❌ below. `commands` is model-invocable (0.70.0) so
"what commands are there?" can be answered.

## task-context (stage 1) — slash only
- ✅ `/ep-qa-pipeline:task-context EP-55123`
- ✅ (auto) step 1 of qa-pipeline-docs and qa-refinement
- ❌ "pull task context for EP-55123" → qa-pipeline (dispatcher)
- ❌ "process the ticket EP-54990" → qa-pipeline (dispatcher) — it reads
  the ticket's state and picks the route
- ❌ "what does ticket EP-55123 say?" → plain chat answer, no skill
- ❌ "summarise this Jira ticket for my standup" → plain chat

## requirements-grooming (stage 2) — slash only
- ✅ `/ep-qa-pipeline:requirements-grooming EP-55123`
- ✅ (auto) after task-context inside qa-pipeline-docs and qa-refinement
- ❌ "groom the requirements for EP-55123" → Claude names this slash
  command (it is written into qa-refinement's description and the
  `commands` table); qa-refinement if the questions should be posted
- ❌ "write requirements for a new feature" → not this pipeline; chat
- ❌ "groom the backlog" → PM activity, no skill
- ❌ "check the ticket for open questions before we estimate" →
  qa-refinement (grooming runs inside it, plus recon and the comment)

## qa-test-cases (stage 4) — slash only
- ✅ `/ep-qa-pipeline:qa-test-cases EP-55123`
- ✅ (auto) stage 4 of qa-pipeline-docs
- ❌ "write test cases for EP-55123" / "make the QA checklist" →
  qa-pipeline-docs (the full docs phase)
- ❌ "make me a checklist for the release day" → generic list, chat
- ❌ "write unit tests for this function" → coding task, no skill
- ❌ "add these cases to QA Service" → qa-pipeline-docs, publish-only
  mode (steps 5–6 on the files already in `runs/<KEY>/docs/`)

## pr-summary (stage 5) — slash only
- ✅ `/ep-qa-pipeline:pr-summary EP-54610`
- ✅ (auto) stage 5 of qa-pipeline-code
- ❌ "PR summary for EP-54610" → qa-pipeline-code or chat
- ❌ "review this PR" (quality judgement) → /review-pr (backend) or chat
- ❌ "summarise this GitHub PR" → outside Bitbucket workspace, chat

## code-review (stage 6) — slash only
- ✅ `/ep-qa-pipeline:code-review EP-54610`
- ✅ (auto) stage 6 of qa-pipeline-code
- ❌ "check the implementation covers the cases" → qa-pipeline-code
- ❌ "review my code style / architecture" → not this skill (needs
  the test-cases file; style is out of scope by rule)
- ❌ "review the alpha branch PR comments" → review-pr skill

## api-testing (stage 7) — slash only
- ✅ `/ep-qa-pipeline:api-testing EP-55123`
- ✅ (auto) stage 7 of qa-pipeline-code
- ❌ "run the API checks for EP-55123" → qa-pipeline-code
- ❌ "test this public REST API for me" → generic task, chat/code
- ❌ "run the API tests in the e2e repo" → that repo's own tooling

## web-testing (stage 8) — slash only
- ✅ `/ep-qa-pipeline:web-testing EP-55123`
- ✅ (auto) stage 8 of qa-pipeline-code
- ❌ "test in the browser for EP-55123" → qa-pipeline-code
- ❌ "run the QA checks" → qa-pipeline-code (the whole code phase)
- ❌ "manual testing" / "I'll test by hand, prepare it" →
  qa-manual-runsheet (9)
- ❌ "walk me through EP-55123" / "let's test it together" →
  qa-manual-walk (10a) — a guided session, not an unattended run
- ❌ "I finished testing, here are my results" → qa-manual-results (10b)

## commands
- ✅ `/ep-qa-pipeline:commands`
- ✅ "what commands does the pipeline have?", "how do I run just the
  grooming stage?", "what's the slash command for web testing?"
- ❌ "run the QA checks for EP-1234" → qa-pipeline-code (a run, not
  the list)

## qa-manual-runsheet (stage 9)
- ✅ "prepare the manual tests", "make a run sheet", "build the walk plan"
- ✅ "set up the data so I can just check the cases"
- ❌ "run the manual tests yourself" → qa-pipeline-code (stage 8 does
  the browser runs)
- ❌ "walk me through EP-1234" → qa-manual-walk (the plan must already
  exist; if it does not, the walk says to run this stage first)
- ❌ "the sheet is filled, update the results" → qa-manual-results
- ❌ "retest EP-1234, the fix landed" → qa-pipeline-code retest mode
  (which then invokes this stage scoped; invoked bare on a story with
  prior artifacts, this stage must PAUSE and ask full-run vs retest)

## qa-manual-walk (stage 10a)
- ✅ "walk me through EP-55123", "let's test EP-55123 together"
- ✅ "start the manual walk", "continue the walk", "next case"
- ✅ "I want to hand-test this with you instead of the spreadsheet"
- ❌ "prepare the manual tests" / "build the walk plan" →
  qa-manual-runsheet (9) — the walk presents a plan, it does not build one
- ❌ "test in the browser" → qa-pipeline-code (stage 8), unattended
  machine run
- ❌ "here's my filled sheet" / "ingest the results" → qa-manual-results
- ❌ "walk me through the PR" / "walk me through the code" → not a test
  session; chat, or `/ep-qa-pipeline:pr-summary`

## qa-manual-results (stage 10b)
- ✅ "ingest the manual results"
- ✅ "the tester finished the run sheet" / pasted TC-Result-Notes table
- ✅ "write back my manual results"
- ✅ (auto) at the end of a qa-manual-walk session, with
  `<KEY>-walk-results.md`
- ❌ "build me the run sheet" → qa-manual-runsheet
- ❌ "walk me through EP-55123" → qa-manual-walk (results come after)
- ❌ "what were the results of the run?" → read the report/Jira, chat
- ❌ "check the answers to our questions on EP-56227" → qa-refinement
  (answers pass on the grooming questions, not test results)

## qa-run-analyzer
- ✅ "analyze the run", "how did that run go"
- ✅ "run health check"
- ❌ "analyze this log file" → generic task, chat
- ❌ "why did this test fail?" → diagnosing-bugs or chat

## qa-pipeline (dispatcher)
- ✅ "qa this ticket EP-55123"
- ✅ "process EP-55123 for testing" / pasted ticket + "test this"
- ✅ "qa this ticket EP-57799" (a human-created QA sub-task, dev not
  started) → proposes refinement on the parent Story
- ❌ "run the QA docs pipeline for EP-55123" → qa-pipeline-docs
- ❌ "prepare EP-56227 for estimation" → qa-refinement (mode named)
- ❌ "retest EP-55123" / "test the bugfix EP-55123" → qa-pipeline-code
- ❌ "walk me through EP-55123" → qa-manual-walk
- ❌ "ingest the manual results" → qa-manual-results
- ✅ "qa pipeline — I need to smoke test if these items are on rc env
  EP-57782" (an RC regression ticket, mode not named in skill terms) →
  proposes the RC smoke
- ❌ "run the RC smoke for EP-57782" → qa-rc-smoke (mode named)

## qa-service-watch (weekly QA Service change check)
- ✅ "check QA Service for updates"
- ✅ "what's new in QA Service?" / "did QA Service change anything we should use?"
- ✅ (auto) first pipeline task of the week, via qa-pipeline / qa-pipeline-docs / qa-pipeline-code
- ❌ "how does request_dev_tests work?" → QA Service `get_help_topic`, no skill
- ❌ "update the plugin for the QA Service changes" → a maintainer release
  (MAINTAINERS recipe), not this read-only check
- ❌ "check the MEXP suite for gaps" → QA Service `coverage_report` / qa-run-analyzer

## qa-api-tests (API cases → implemented in QA Service)
- ✅ "automate the API cases for EP-57310"
- ✅ "write the API tests for this ticket and register them in QA Service"
- ✅ "make the API cases implemented in QA Service for EP-55889"
- ✅ "create the frontend test sub-task for EP-57253"
- ❌ "test the API for EP-1234" / "hit the endpoints" →
  qa-pipeline-code (stage 7 executes cases on a test env, writes no
  test code)
- ❌ "register the tests from PR #5544" (already written and merged)
  → qa-manual-results step 4d, or the QA Service link tools
- ❌ "write test cases for EP-1234" → qa-pipeline-docs
- ❌ "implement the unit tests for visitor/meeting-request" (a suite,
  no ticket, not API) → QA Service's own qa-implement-tests flow

## qa-rc-smoke (release-candidate mode)
- ✅ "smoke test the RC for EP-57782"
- ✅ "check these items are on RC: EP-57107, EP-57398, EP-57509"
- ✅ "RC regression for Prod 2026-09-30" / pasted "[Regression] RC
  release …" ticket + "check it"
- ✅ "are the release items deployed to rc?"
- ❌ "retest EP-57398 on alpha2" → qa-pipeline-code (retest mode)
- ❌ "test the bugfix EP-57509" → qa-pipeline-code (bug-fix mode)
- ❌ "run the full regression suite" → CI, no skill
- ❌ "check EP-57398 on production" → refused: production is never a
  test target (chat answer)
- ❌ "what's in the Prod 2026-09-30 release?" → plain chat / JQL, no
  skill

## qa-pipeline-docs (orchestrator)
- ✅ "run the QA docs pipeline for EP-55123"
- ✅ "build the test cases for a ticket" (full flow implied)
- ✅ "add these cases to QA Service" / "publish the test cases for
  EP-55123" (publish-only mode — stages 1–4 skipped when their files exist)
- ❌ "publish this page to Confluence" → confluence-sync
- ❌ "via QA Service, discover the tests under <path> for suite X and
  import them" → the QA Service tools directly (or sdlc-qa "link the
  tests I just wrote"); the docs phase discovers only inside its own
  stage 3 (0.50.0)
- ❌ "generate test cases for the Exhibitor Favorites suite in QA
  Service" (no ticket) → QA Service `start_generate_test_cases`
  directly, not a pipeline run
- ❌ "just groom the requirements" → Claude names
  `/ep-qa-pipeline:requirements-grooming` (slash only)
- ❌ "prepare EP-57799 for estimation — what questions do we have?" →
  qa-refinement (no test cases before the answers)

## qa-refinement (pre-estimation mode)
- ✅ "I need to prepare EP-57799 for estimation and decomposition —
  check if there are questions from our side"
- ✅ "refinement for EP-56227"
- ✅ "what questions do we have for this ticket before we estimate?"
- ✅ "QA estimate prep for EP-56227" / "decomposition prep"
- ✅ "check the answers to our questions on EP-56227" (answers pass)
- ❌ "the tester finished, here are the results" → qa-manual-results
  (test verdicts, not answers to grooming questions)
- ❌ "build the test cases for EP-56227" → qa-pipeline-docs
- ❌ "groom the requirements" (a file, no posting) → Claude names
  `/ep-qa-pipeline:requirements-grooming` (slash only)
- ❌ "estimate this story in story points" (no QA context) → chat
- ❌ "what does EP-56227 say?" → plain chat answer, no skill

## qa-pipeline-code (orchestrator)
- ✅ "run the QA code pipeline", "run the QA checks"
- ✅ "review the PRs and test in the browser for EP-55123"
- ✅ "the fix landed, retest EP-55123" (retest mode)
- ✅ "test the bugfix EP-56133" (bug-fix mode — Bug ticket, no docs
  phase; derives mini cases from the ticket's repro steps)
- ❌ "review this PR" (alone) → review-pr or chat
- ❌ "run all the tests" (in a repo context) → that repo's test runner
