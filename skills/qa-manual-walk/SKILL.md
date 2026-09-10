---
name: qa-manual-walk
description: >
  The live half of stage 10 — a guided, one-card-at-a-time manual test
  session in chat. Takes the walk plan built by qa-manual-runsheet
  (stage 9), presents each case as a plain-language card ("as <who>,
  do <this>, you should see <that>"), asks what happened, answers
  questions from the card's backstage notes, runs the API / harness
  cards itself while the tester supplies only what a human can (an
  email token, a phone), keeps a resumable state file, and hands the
  verdicts to qa-manual-results for the confirmed write-back. Use when
  the user says "walk me through EP-1234", "let's test EP-1234
  together", "start the manual walk", "continue the walk", "next
  case", or wants to hand-test a ticket with the agent instead of a
  spreadsheet. Do NOT use to build the plan (qa-manual-runsheet), to
  run cases unattended (web-testing), to ingest a filled sheet
  (qa-manual-results), or to explain a PR or code ("walk me through
  the PR" → pr-summary; "…the code" → code-review).
---

# QA Manual Walk

A test session, not a document. The tester and the agent walk the
walk plan together: one card at a time, in the order a person actually
moves through the product, with every question answerable on the spot.

This stage exists because the run sheet failed the person it was built
for. A sheet has to carry everything in every cell — the account, the
action, the pass condition, the machine's evidence, the caveats, the
harness command — because nobody is there to answer a question. In a
session the agent is there. So the card carries only what the tester
needs to act, and the rest stays backstage until it is asked for.

Nothing here weakens a rule the pipeline paid for. Fresh fixtures,
probed blockers, positive controls, half-observable honesty, the fail-
by-fail confirm before any verdict is recorded — all still apply. They
are enforced by the agent in conversation instead of printed into a
cell.

## Source of truth

- **Cases** — the QA Service suite, as for every stage. The walk plan
  is a *view* built from it by stage 9. If a card and the suite
  disagree, the suite wins and the disagreement is a finding.
- **Verdicts** — the pass's QA Service test run
  (`../qa-pipeline/references/test-runs.md`). **This stage records
  nothing on the run, the suite, or Jira.** It writes only its own two
  working files. The write-back happens in `qa-manual-results`, after
  the tester has seen every verdict about to be recorded — a recorded
  `fail` files a Jira defect, so that confirm is not optional.
- **The plan file** — `<ISSUEKEY>-walk-plan.md`, format in
  `../qa-manual-runsheet/references/walk-plan-format.md`. Read it in
  full before the first card, including every backstage block.

## Input

1. `<ISSUEKEY>-walk-plan.md` — required. Missing → say that stage 9
   (`qa-manual-runsheet`) has to build it first; do not improvise a
   plan from the test-cases file, because a plan without provisioned,
   verified fixtures is exactly the false-pass machine stage 9 exists
   to prevent.
2. `<ISSUEKEY>-testdata.json` — the fixture record the plan refers to.
3. `<ISSUEKEY>-walk-state.json` — present means a walk is in progress:
   resume it (see "Resume"), never start over silently.
4. The pass's QA Service test run (connector present) — for the roster
   and the machine verdicts the cards were built against; used
   read-only here.
5. `<ISSUEKEY>-open-items.md` — the ledger; retest history for cards.
6. `.env.qa-agents` (or the e2e `.env`) — only for AGENT-RUNS cards.
7. **The tester's identity** — their e-mail, which becomes the
   `principal` on every human verdict at write-back. Ask once at the
   start if it is not obvious from the session.

**Where to find inputs:** `../qa-pipeline/references/data-locations.md`
(run folder first; asking the user is the last resort).

## Output

- `<ISSUEKEY>-walk-state.json` — written after **every** card; the
  resume point. Deleted by nobody: stage 10 reads it as the audit trail
  of the session.
- `<ISSUEKEY>-walk-results.md` — written at the end (and on an early
  stop): one row per card with TC id(s), verdict, the tester's words
  verbatim, evidence links, card kind, and `source` — the input
  `qa-manual-results` ingests. Format:
  `references/walk-results-format.md`.

Both files sit beside the plan, carry no credentials, and are
git-ignored by the `EP-*` / `*-walk-*` rules. The plan itself carries
live passwords — it stays out of version control and Jira like the
run sheet before it.

## The session — how it runs

The full conversational rules are in
`references/walk-session-rules.md`. Read them before the first card.
The shape:

### Step 0 — Pre-flight (one short message)

Confirm you are on the environment and event the plan was built for
(the plan header names them); confirm the tester's e-mail; state the
size — "N cards in M sessions, roughly T minutes; the machine settled K
cases without a card" — and where a previous walk stopped, if
resuming. Then start. Do not re-explain the pipeline.

### Step 1 — Present one card

Exactly the card as the plan states it: the header line (id, kind,
risk), the account if it changes, **Do**, **You should see**. Nothing
from backstage unless the card has a `say-first:` line (a required
wait, a scope warning the tester must hear *before* judging). Then one
question: **"What happened?"** — and wait.

### Step 2 — Listen, map, confirm when needed

The tester answers in their own words. Map to a verdict per the rules
file: a plain "pass" / "ok" is a PASS on a card with a single visible
pass condition; any description of a mismatch is a FAIL, restated once
for confirmation ("So the star stayed lit — I'll record FAIL against
'star empty'. Right?"); "can't", "no access", "the page 500s" is
BLOCKED with the reason; "skip" is SKIPPED with the reason. A question
is answered from backstage, then the card is re-asked. **Absence
checks and half-observable cards always get the positive-control
question before any verdict** ("and what does the counter read?").

Save the tester's words verbatim — they become the note on the record.

### Step 3 — Cards the agent runs

An **AGENT-RUNS** card (API / harness / anything with an HTTP verb in
it) is executed by the agent under `api-testing`'s write-safety rules,
with the tester watching. The tester supplies only the human-only
input the card names (a token from a mailbox, a code from a phone).
Show the call and its result in five lines or fewer, state the verdict
against the card, ask the tester to confirm. **Record it as
`source: machine`, principal `ep-qa-pipeline agent (<KEY> walk,
witnessed by <tester>)`** — the agent executed it, so it is a machine
verdict a human watched, and it is counted that way in the summary.
Never dress it as human-confirmed.

### Step 4 — Blocked cards are re-probed live

Before presenting a **BLOCKED** card, re-probe its reason (stage 9
rule 5 — probe every blocker). Dissolved → present it as a WALK or
AGENT-RUNS card and say why. Still standing → present the one-line
reason and the unblock, and ask whether the tester can supply it now
("do you have an activation code to hand?"). Otherwise BLOCKED, reason
recorded.

### Step 5 — Keep state, show progress

Write the state file after every card. Every five cards, or when
asked, one progress line: `7/11 · 5 pass · 1 fail · 1 blocked · next:
session 2 as <account>`. Deferred cards ("later") go to the end of the
walk, not into the void.

### Step 6 — Finish and hand over

When the last card is answered (or the tester stops): write
`<ISSUEKEY>-walk-results.md`, show the summary table (verdict per card,
FAILs first with the tester's words), then invoke **`qa-manual-results`
with that file as its input** — it reconciles against the run, shows
every `fail` about to be recorded case by case, and on the tester's
explicit yes records, closes the run, posts the first human-facing
summary, closes ledger rows, and offers the bug filings. Nothing is
written to any record before that yes.

## Rules

- **Never lead the witness.** The card shows the expectation because
  the tester must know what to check — but the first question is
  always "what happened?", never "did it pass?". On cards where the
  rules file requires it, the positive-control question comes before
  the verdict.
- **The tester's words are the note.** Verbatim, even when the word is
  "ok". A mapped verdict without the words behind it is the agent's
  opinion, not the tester's evidence.
- **One card, one question per turn.** No previews of the next card,
  no summaries of the last three, no re-explaining the plan.
- **Backstage on request only** — but *offer* it when it matters: a
  card whose FAIL would not be the PR's fault, a surface known to lag,
  a half-observable expectation. Say the one relevant sentence, not the
  block.
- **Cards say who, do, see; the agent says why.** If a tester asks
  "why are we checking this?", answer from backstage — the source
  clause, the machine verdict, the risk — in plain words.
- **Corrections go back to the suite, via stage 10.** A tester who
  discovers a wrong expected result, a missing condition, or a case
  that does not match the product is reporting a finding: capture it
  under `Case corrections` in the results file. Stage 10 applies it to
  the suite with the same confirm as the verdicts. Never edit the plan
  to make a case pass.
- **The product is touched only by AGENT-RUNS cards**, and only within
  `api-testing`'s write-safety rules (read-only by default; a write
  snapshots-and-reverts or uses a throwaway fixture). The walk never
  provisions — that is stage 9's job, and a fixture created mid-walk
  has no verified baseline.
- **Mirror the tester's language in chat; files stay in English.**
- **Do not rush, do not pad.** The one-line-per-stage brevity rule of
  the orchestrators does not apply inside the walk — but every turn is
  still short: the card, or the answer, and one question.
- **Never touch production.** The plan names the event; if the tester
  is somewhere else, stop and say so.

## Resume

"Continue the walk for EP-1234" → read `<ISSUEKEY>-walk-state.json`,
show one progress line, re-confirm the environment in one clause, and
present the next card. If the state file's run id no longer matches an
open run (`get_test_run` → `closed`), say so and stop: the round was
already written back, and a second walk on the same run needs
`reopen_test_run` by stage 10, not a silent continuation.

## Final response

One short block: the results file path; counts (pass / fail / blocked /
skipped / deferred, and how many were agent-run); the FAILs with the
tester's words; the case corrections collected; and the sentence that
`qa-manual-results` is now running the confirmed write-back (or, if the
tester stopped early, that nothing has been recorded and the walk can
be resumed).
