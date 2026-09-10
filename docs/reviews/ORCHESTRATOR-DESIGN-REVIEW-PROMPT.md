# Reusable prompt — cold design review of the QA pipeline orchestrators

Give this file to a FRESH agent (no prior context on this repo or its
author's sessions). Replace `<REPO PATH>` and `<DATE>` before running.
Re-run it after any significant change to the orchestrators or the
stage set; compare against the previous `ORCHESTRATOR-DESIGN-REVIEW-*`
file to see whether the design is converging on the intent.

---

You are doing a cold DESIGN review of two orchestrator skills in a QA
pipeline plugin, judging them against the creator's stated intent and
against best practice. You have no stake in this design; treat it as an
unknown author's work. Do not flatter. Praise only where it is
load-bearing (i.e. it changes a decision about what to keep).

## Where

Repo: `<REPO PATH>`. Do not trawl `.git/` or `.playwright-mcp/`.

## The creator's intent — the yardstick for this review

The creator (a QA engineer) describes the pipeline's purpose in their
own words, lightly edited:

"A QA Engineering process from start to finish based on shift-left
testing. Learn the task; gather all relevant documentation; analyse
gaps; cover all the acceptance criteria with test cases, both
machine-readable and human-readable. Analyse the code repo — find gaps
between code and requirements. Run API tests and browser tests via
Playwright or the Claude browser extension. Set up data for each test
scenario for my manual checks — because I never trust AI results 100%:
I always verify manually what I can, and typically around half of
AI-reported results turn out not to be true, and about half of the
real bugs are missed."

That last sentence is the design-critical constraint: the human is the
final arbiter; AI verdicts must be treated as provisional by the
architecture itself, not just by the user's habit. Judge everything
against this intent: does the pipeline as WRITTEN implement this
process, and is the human-verification loop first-class or bolted on?

## What to read

1. The two orchestrators IN FULL: `skills/qa-pipeline-docs/SKILL.md`
   and `skills/qa-pipeline-code/SKILL.md`, plus their references/
   folders.
2. Every stage skill they invoke, IN FULL: task-context,
   requirements-grooming, qa-checklist, qa-test-cases, pr-summary,
   code-review, api-testing, web-testing, qa-run-analyzer,
   qa-manual-runsheet, qa-manual-results (SKILL.md at minimum; dip
   into references/ where the SKILL delegates something important
   there).
3. README.md, MAINTAINERS.md, and skim CHANGELOG.md for what the
   design claims about itself.
4. Only as a reality check where useful: the per-ticket run artifacts
   in the repo root (or `runs/`), from the most recent real run.
5. **Read any existing `PIPELINE-REVIEW-*` / `ORCHESTRATOR-DESIGN-
   REVIEW-*` file LAST — only after you have written your own
   findings.** Check the CHANGELOG for which of their findings are
   already fixed. After reading, add a final reconciliation section:
   what your independent view confirms, what you found that they did
   not, and where you disagree. Do not let them set your agenda.

## What to evaluate

**A. Structure and step ordering.** Map the actual step sequence of
each orchestrator. Is this a coherent shift-left flow? Is anything in
the wrong order relative to the intent (what runs before/after what it
depends on)? Where does the "shift-left" claim hold and where is it
testing-after-the-fact with a shift-left label?

**B. Coverage of the intended process.** Walk the creator's intent
point by point and locate where each is implemented: task learning,
documentation gathering, gap analysis, AC coverage (machine- AND
human-readable), code-vs-requirements gap detection, API testing,
browser testing, per-scenario test data for manual checks, human
verification as final arbiter. For each: implemented well /
implemented weakly / missing. Pay special attention to whether "cover
ALL the AC" is enforced anywhere or just intended, and whether
code-vs-requirements gap analysis exists as a real step or only as a
side effect of code review.

**C. Integration seams.** The pipeline hands data across:
working-directory files, Jira sub-tasks + comments (archive/tracker),
QA Service suite (optional connector), .env credentials, Cowork vs
Claude Code environment split, subagent dispatch. For each seam: is
the contract explicit, is it validated, what happens when the seam is
degraded (no connector, no creds, fresh chat, split run)? Is there one
place that tells a newcomer how a ticket flows end to end, and does it
match what the skills actually say?

**D. Best practices — two lenses.**
- QA engineering: requirements traceability, risk-based
  prioritisation, entry/exit criteria per stage, test data management,
  defect lifecycle (found → filed → retested), regression strategy,
  the test pyramid / what is automated vs manual and why, independence
  of verification.
- Agent/skill design: context economy (what each stage loads),
  determinism (templates/scripts vs free generation),
  pause/confirmation points vs autonomy, idempotency and re-runs,
  subagent isolation, failure modes when a stage crashes mid-run,
  self-verification steps.

**E. The trust model.** Given "half of AI results wrong, half of bugs
missed": does the architecture actually treat automated PASS/FAIL as
provisional? Trace what happens to an automated verdict from creation
to final record, and what forces (or fails to force) human
confirmation before it becomes truth. Is the human's disagreement loop
(runsheet → manual results → retraction) load-bearing or optional?
What share of cases can still become "settled truth" with no human
ever looking?

**F. What is over-engineered.** The inverse question, equally
important: where has this pipeline accumulated complexity that does
not serve the intent — stages, rules, or artifacts a lean version
would drop? The creator maintains this alone; every rule is a
maintenance cost. Name concrete candidates for simplification and what
would be lost.

## Output

Write `<REPO PATH>/ORCHESTRATOR-DESIGN-REVIEW-<DATE>.md`:
- A one-page executive view first: does the pipeline implement the
  creator's process — where it is strong, where it diverges, the 3
  changes with the highest value.
- Then the detailed sections A–F.
- Each weakness: what it costs in practice, evidence (file + quote or
  step number), and a concrete fix (named file, change to make). Rank
  by consequence to the creator's intent, not by tidiness.
- A short honest "what to keep exactly as is" list.
- The reconciliation section vs the prior reviews last.

## Reply to the requester

At most 20 lines: file path; verdict in one sentence (does it
implement the intended process?); the intent points that are
missing/weak (one line each); top 3 improvements; top over-engineering
candidate; anything that surprised you; one line on how your view
differs from the prior reviews.
