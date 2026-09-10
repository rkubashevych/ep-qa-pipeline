# The open-items ledger — memory across rounds

**Contents:** Why · The file · What goes in · Who writes, who reads,
who closes · Staleness rule · Where it lives

## Why this file exists

EP-56197 round 3's run report says "carried a third round, still open"
four times: `RISK-CR-1` (a PR that can delete the fix's own tests),
`RISK-CR-2` (never executed), `RISK-CR-3` (the fix rests on two lines in
an unchanged file), six behaviours with no covering case. EP-53978 pass 5
spent its whole scope file reconstructing what passes 1–4 had left
undecided. Nothing in the pipeline remembered: the only record of an
open item was that round's run report — git-ignored, per round, rebuilt
from scratch by the next analyzer run.

MAINTAINERS step 1 says a run-report 🔴 tagged [Pipeline] is an open
defect until implemented or rejected in the CHANGELOG. That rule had no
machine-readable input. This file is it.

## The file

`runs/<KEY>/<KEY>-open-items.md` — **one per ticket**, one level above
the per-pass `r<N>/` folders it joins (`data-locations.md` → "The run
folder"). The pass folders are the rounds; the ledger is what carries a
question from one to the next.

```markdown
# Open items — <KEY>

| # | Item | Class | First seen | Last seen | Owner | Decision | Closed |
|---|------|-------|------------|-----------|-------|----------|--------|
| 1 | RISK-CR-1 — PR 4830 can delete the fix's own tests, CI green | [Pipeline] risk row | r1 2026-08-20 | r3 2026-09-07 | PR author | — | — |
| 2 | GSTOP-WDTH-05 in suite, absent from the 41-case file — in or out? | [Pipeline] scope | p3 2026-08-12 | p5 2026-09-07 | QA (Roman) | — | — |
| 3 | TC-REQ-6.2 has no `[core]` marker; stage 9 nominated TC-REQ-6.2 | nomination | r2 | r2 | — | accepted r2 | r2 2026-09-03 |
| 4 | `Dark` products 18 vs 21 — owned by EP-56739 | [Product] other-ticket | r3 | r3 | EP-56739 | tracked there | — |
```

Columns: `Item` — one line, the id first when there is one (`RISK-CR-n`,
a stable id, a TC id). `Class` — `[Pipeline]`, `[Product]`, `[Input]`,
`risk row`, `scope` (in/out decision), `nomination` (`[core]` chosen by
stage 9 for an older file), `other-ticket` (a defect owned elsewhere —
name the key in Owner). `First seen` / `Last seen` — round or pass label
+ date. `Decision` — the recorded ruling in ≤ 1 line, or `—`. `Closed` —
round + date, or `—`.

## What goes in

Every 🔴 and 🟡 from a run report that is **not settled by the run
itself**: unmapped changes awaiting a scope/requirement decision, risk
rows carried without execution or decision, findings with no case, no
requirement and no bug key, suite/file divergences awaiting an in/out
ruling, unanswered open questions the code phase depends on, `[core]`
nominations stage 9 made for a file without markers, and defects owned
by another ticket that this ticket's close depends on.

Not in: anything with a bug key of its own (Jira tracks it), anything
already fixed in the CHANGELOG (that is the pipeline's ledger), product
verdicts (the QA Service run holds those — `test-runs.md`).

## Who writes, who reads, who closes

- **`qa-run-analyzer` writes.** After the findings section, for each
  🔴/🟡 that meets "what goes in": update `Last seen` on a matching row
  (match on the id or on the item text), or append a new row with
  `First seen` = this round. It never closes a row.
- **`qa-pipeline-code` step 0 reads** in retest and bug-fix mode
  (resume mode too): show the open rows (`Closed = —`) as part of the
  scope confirmation — *"3 open items from earlier rounds; decide or
  carry each"* — and record any decision the user gives in the
  `Decision` column before stage 5 runs. A run that starts without
  reading the ledger repeats the previous round's questions.
- **`qa-manual-runsheet` (stage 9) writes** its `[core]` nominations
  for a file without markers (class `nomination`), so the next round's
  stage 9 starts from the same choice instead of choosing again.
- **`qa-manual-results` (stage 10) is the only stage that closes a
  row**: when a decision lands (a PM ruling, a case promoted to the
  suite, an item filed as a bug — write the key, a risk row executed to
  a verdict), fill `Decision` and `Closed`. It also lists the still-open
  rows at the end of the human summary under **Carried forward** — one
  line each, so the reader of the summary sees what the round did *not*
  settle.
- The user closes a row by saying so ("drop RISK-CR-2") — record the
  reason as the Decision; never delete the row.

## Staleness rule

The analyzer flags 🔴 `[Pipeline] carried item` any open row whose
`First seen` is **two or more rounds** before the current one and whose
`Decision` is `—`. Two rounds is the threshold because one carry is a
normal "not this round"; two means nobody owns it. The 🔴 names the row
and the owner and is itself what MAINTAINERS step 1 requires a CHANGELOG
answer to, when the class is `[Pipeline]`.

## Where it lives

`runs/<KEY>/` — beside the pass folders, not inside one
(`data-locations.md` resolution order). Durable copy: where the ticket has a QA sub-task, the
ledger is archived with the reports in wave 1 (`File:
<KEY>-open-items.md` in the machine archive comment) and restored by
step 0 like any other file. Where there is no QA sub-task — a Bug, a
Defect — the run folder is the only copy, exactly as for the
reports; a resume on another machine pauses for it rather than starting
a fresh, memory-less ledger. It matches the `EP-*` ignore rule and is
never committed.
