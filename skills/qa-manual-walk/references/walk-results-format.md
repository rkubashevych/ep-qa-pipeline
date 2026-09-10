# Walk results format — `<ISSUEKEY>-walk-results.md`

The hand-over from the walk to `qa-manual-results`. Stage 10 joins it
to the run **by TC id**, exactly as it joins a filled run sheet — so
the columns below are the sheet's TC / Result / Notes with the fields a
live session adds. One row per card; a `Covers` card lists every case
it settles.

No credentials anywhere in this file. Passwords live in the plan and
`-testdata.json` only.

```
# <ISSUEKEY> — Walk results

Run: <QA Service run id> · <run title>            (or "no run — <why>")
Round: r<N> · Env: <label> · Event: <id>
Plan: <ISSUEKEY>-walk-plan.md (built <YYYY-MM-DD>) · State: <ISSUEKEY>-walk-state.json
Tester: <e-mail>                 (principal for every source: manual row)
Session: <start> → <end> UTC · Completeness: complete | complete (<N> cards declared not run) | stopped early (<N> cards not run — resume later)

## Summary

| Verdict | Human (source: manual) | Agent-run, witnessed (source: machine) |
|---|---|---|
| PASS | <N> | <N> |
| FAIL | <N> | <N> |
| BLOCKED | <N> | <N> |
| SKIPPED | <N> | — |
| not run | <N> | <N> |

## Verdicts

> FAILs first, then BLOCKED, then the rest in card order.
> `Notes` is the tester's words verbatim; the agent adds nothing to it.
> `Half` marks a half-observable card: the human verdict covers the
> visible half only; the machine verdict named in `Rests on` covers the
> rest.

| Card | TC (Covers) | Kind | Result | Source | Notes (verbatim) | Evidence | Half / Rests on |
|---|---|---|---|---|---|---|---|
| 4 | TC-REQ-3.2 | WALK | FAIL | manual | "the star lit up and Northwind is in my favourites" | https://jam.dev/c/… | — |
| 7 | TC-1 | AGENT-RUNS | PASS | machine (witnessed) | "yes that's the 200" | — | — |
| 2 | TC-REQ-1.1, TC-REQ-1.3 | WALK | PASS | manual | "ok, and the counter says 1" | — | — |
| 5 | TC-REQ-2.4 | WALK | PASS | manual | "star lit" | — | Half — stored type rests on API PASS (stage 7) |

## Not run

<card ids with their TC ids, and the reason: "stopped early", "deferred twice">, or "none"

## Case corrections

> Findings about the CASE, not the product. Stage 10 applies them to the
> suite (`suggest_test_case` / `edit_test_case`) under the same confirm
> as the verdicts. Never applied by the walk itself.

| TC | What is wrong | What the tester saw |
|---|---|---|
| TC-REQ-5.1 | expected result names a "Submit" button | the button is "Save" since the redesign |

## Blocked reasons

| Card | TC | Reason (re-probed at <time>) | Would unblock |
|---|---|---|---|
| 9 | TC-3 | activation code reaches the platform only by email; no deliverable mailbox in this run | one registration on a Gmail address |

## Observations

> Things the tester noticed that no card asked about. Labelled
> `OBSERVATION (no source checked)` per `sources-of-record.md` § 7 —
> stage 10 reports them as questions, never as defects.

- <one line each, or "none">
```

## Rules

- **Join key is the TC id.** Card numbers are for the conversation;
  stage 10 ignores them for the join.
- **`Source` is honest.** A card the agent executed is `machine
  (witnessed)` even when the tester confirmed the result. Only a card
  the tester performed is `manual`. The two-wave summary counts them
  separately.
- **Notes are verbatim.** Trailing "ok" and all. The agent's
  interpretation is the `Result` column; the tester's evidence is the
  `Notes` column; they must never be merged.
- **Nothing in this file has been recorded anywhere** when it is
  written. The header's `Run:` line names where it *will* be recorded.
  Stage 10's preview is the moment the tester sees the final list.
- **Stopped early → no hand-over.** The file is still written (with
  `Completeness: stopped early`) so the session is not lost, but stage
  10 is invoked only when the walk is finished or the tester says the
  remaining cards will not be run — the latter is `complete (N cards
  declared not run)`, and stage 10 writes it back without asking.
- **No credentials.** Tokens, codes and passwords the tester pasted
  appear as `<token supplied>` in Notes (redacted in the state file
  already).
