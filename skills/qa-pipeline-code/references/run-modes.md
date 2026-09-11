# Run modes — bug-fix, resume, retest (qa-pipeline-code step 0)

**Contents:** Which mode · Bug-fix mode · Resume mode · Retest mode

Step 0 of `qa-pipeline-code` decides the mode before anything else runs.
This file holds the full rules for the three non-default modes; the
SKILL.md keeps only the entry conditions and the one-line summary of
each. Everything here was in the SKILL.md until 0.41.0 and moved
verbatim — the rules did not change, only their address.

## Which mode

- **First run** — no earlier `r*` folder for the key, none of the
  retest / resume signals:
  `r1`, the default path in SKILL.md.
- **Retest** — the user says so ("retest <KEY>", "the fix landed"), or
  the retest signals fire and the user confirms. Always a new
  `r<max+1>/` folder.
- **Bug-fix** — the user says so, or the ticket is a Bug with no QA
  sub-task and no suite and the user confirms. Also a new folder.
- **Resume** — the newest folder's run report is `partial`, or its QA
  Service run is `running` with `not_run` rows and no
  `-manual-results.md`, and the user did NOT ask for a retest or
  bug-fix (an explicit request always wins over the resume signals).

## Bug-fix mode (no docs phase)

For testing a fix to a standalone
Bug ticket. Two ways in: the user says so ("test the bugfix
EP-XXXX", "quick check of the fix"), or step 0 finds issuetype Bug
with no QA sub-task and no suite — then ASK "full pipeline or
bug-fix mode?". How it differs from a normal run — and nothing
else differs:
- **Cases come from the bug ticket itself.** Derive 2–4 mini cases
  into a normal `<KEY>-test-cases.md`: TC-1 = the reproduction
  steps with the FIXED behaviour as the expected result (quote the
  ticket's own words — the source-of-record rule applies: no
  expected result that the ticket does not state); TC-2 = the
  negative sibling (the old broken input/path must not regress the
  surrounding behaviour); plus one regression case per behaviour
  the fix PR touches beyond the bug (from pr-summary's "Behaviours
  touched" — add these AFTER stage 5 runs). Channel-tag each case;
  the routing invariant applies as usual.
- **No docs phase, no QA sub-task — but a suite.** Structural checks
  are skipped (say so). **Publish the mini cases to the FEATURE's
  suite before stage 5** (append, or create the feature's suite),
  with one requirement carrying the ticket's own expected result,
  per `../../qa-pipeline-docs/references/qa-service-publish.md` →
  "Bug-fix mode — the regression mini suite" — **behind its own
  REQUIRED PAUSE** (preview the suite, the requirement and each case;
  write nothing before the yes). That is what lets step 6 open a run with a
  roster and stage 10 record the human verdicts; until 0.33.0 a
  bug-fix run left no durable record at all (EP-56998 open-items
  #13). Connector absent → PAUSE, say what is lost, continue only
  on an explicit yes. The Jira write-back targets are the BUG
  ticket's comments — same two-wave rule: the status comment now,
  the human-facing verdict after your manual check. A Bug or Defect
  gets exactly two comments across the whole run, and the second is
  the verdict a person actually wants to read. The reports stay in
  the run folder, so a resume needs the same machine.
- **Stages 5–8 run unchanged** on the derived branch (the bug key
  is the branch, or use the main-issue PR fallback). All evidence
  rules, gates and pauses apply — a small scope is not a licence to
  skip the absence-check protocol or the probe rule.
- **The manual round shrinks to fit:** stage 9 emits a handful of
  cards (or, if you say you'll verify directly, skip the plan and
  just report your result — "the fix works, ingest it" runs stage
  10 against your one-line verdict, which stage 10 treats as a
  one-row TC / Result / Notes table per mini case, principal = you).
  Verdict flip / bug reopen offers happen at stage 10, as always.

## Resume mode

Look in this order:
1. **The run folder** — `<STORY>-code-review.md`,
   `-api-testing.md`, `-web-testing.md`, `-run-report.md`,
   `<STORY>-open-items.md` (the ledger — per ticket, no round
   suffix) and, when present, `<STORY>-manual-results.md` and
   `<STORY>-remaining-cases-triage.md`. The last two carry verdict
   corrections that SUPERSEDE the stage reports; a resumed run must
   honour them over older PASS/FAIL lines. When a QA Service run
   already exists for this pass (`list_test_runs` on the suite, title
   `<STORY> …`), its roster verdicts are the machine record — resume
   into that run, never create a second one for the same pass.
2. **The QA Service run** — for the *verdicts* of a pass whose
   reports are not here: `get_test_run` gives every roster row's
   verdict, principal and note. The prose of a stage report
   (findings, blast radius, unmapped changes) exists only in the run
   folder; pre-0.33 tickets may still carry it in legacy archive
   comments on the QA sub-task (`../scripts/extract_archive.py`).
3. **No run folder for this pass → PAUSE.** The reports live only on
   the machine that ran the stages (no archive is posted since
   0.33.0). Say that plainly,
   ask whether this is the machine the earlier run used, and offer
   either to re-run the missing stages or to have the files
   attached. Never assume "no file" means "stage never ran" — on a
   different machine it means "cannot see it from here", and quietly
   re-running a 45-minute browser stage because a folder was not
   mounted is exactly the waste this guard exists to prevent. **A stage is done only if
its report is COMPLETE — file existence is not completion.** Read
each restored report's `Completeness:` header (older reports lack
one — then derive it: do Scope and Statistics agree, and is every
in-scope case present in Results or Not-executed-here?). A report
that is `partial`, internally inconsistent, or
header-less-and-uncheckable gets its stage RE-DISPATCHED for the
missing cases — a resumed run must not inherit "NOT EXECUTED 15" as
"done" (a real run did exactly that). Skip only complete stages;
continue from the first missing or partial one (typically
web-testing in Cowork after 5–7 ran in Claude Code) unless the user
asks to re-run. Tell the user which stages were restored complete
vs partial vs pending before continuing.

## Retest mode (the fix came back)

Two ways in, both valid: the
user says so ("retest <KEY>", "the fix landed"), OR step 0 notices
the signals — newest human summary / manual-results comment is
❌ FAIL, or a previous QA Service run for this key holds `fail` /
`known_defect` rows (or, pre-0.30, the suite carries RETEST /
supersede lines) — and ASKS "full run or retest?" instead of
assuming. Never require a magic phrase.
**Scope (three tiers, confirmed by the user before stage 5):**
1. every FAIL / FAIL CONFIRMED case (including retracted-to-FAIL) —
   the defects' own cases;
2. the blast radius — REQ siblings, cases sharing the fixed code
   path (from the fix PR's Behaviours touched), and confirmed
   `RISK-CR-*` rows;
3. every case that never got a real verdict: NOT EXECUTED,
   unresolved BLOCKED, rows the human never walked.
**Read the ledger first.** `<STORY>-open-items.md`
(`../../qa-pipeline/references/open-items-ledger.md`) holds what earlier
rounds left undecided — carried risk rows, in/out rulings never made,
findings with no case and no key, `[core]` nominations. Show the open
rows in the same scope confirmation ("N open items from earlier
rounds — decide or carry each") and write any decision the user gives
into the `Decision` column before stage 5. Prior verdicts come from
the previous pass's QA Service run (`get_test_run`, or
`case_execution_history` per case) — that is the record, not the
markdown; where the retracted-verdict tier applies, note **where each
old verdict was published** (ticket + comment id) in
`<STORY>-retest-scope.md`, because stage 10's retraction goes there.
Every FAIL / PARTIAL row a pass leaves `not_run` is scope tier 1 or 3
of the next pass by construction.
**Build the scope from the SUITE, not from the local test-cases
file.** When the sub-task names a QA Service suite and the connector
is present, `get_suite` FIRST and diff it against
`<STORY>-test-cases.md`: any requirement or case the suite has and
the file does not is IN SCOPE by default, and every such case must
be listed by id in `<STORY>-retest-scope.md` with an explicit
in/out decision. The suite is the system of record and moves
between runs — a PM ruling, a QA-added case or a corrected
expectation lands there, not in the file the docs phase wrote.
(Real run: the suite had gained a P0 requirement and two P0 manual
cases from a PM comment four days after the baseline. The retest
scope was derived from the 89-case file, so neither case was in any
stage report; one of them was then failed by accident and recorded
as an unstatused observation, and the other was never executed at
all.) No suite or no connector → say once in the run report that
the scope could not be reconciled against the system of record.
**The scope binds ALL stages including stage 9:** pr-summary runs
on the fix branch/PR; 6–8 execute only the scoped cases;
`qa-manual-runsheet` builds cards for the scoped cases ONLY — never
a full-plan rebuild. Fixtures are FRESH by default: prior fixtures
are presumed contaminated for any counter/analytics assertion (one
run left a phantom like and a counter stuck at 15). Reuse a prior
account only for stateless checks, after re-verifying its login and
baseline.
Wave 1 posts the one status line, prefixed `RETEST:`; the human
summary follows at stage 10. The retest is a NEW run on the same suite (one
run per pass); a FAIL that now passes is simply recorded `pass` in
it, and the retraction comment goes to wherever the old FAIL was
published (`test-runs.md` → "Retraction target rule"); verified
bugs get a closing comment offered on their tickets. Everything else
keeps its verdicts — say so in the summary. Stage 10 ingests the
retest walk results (or an exported sheet) like a first run.
