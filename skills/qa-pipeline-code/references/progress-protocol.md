# Progress protocol

Shared by every long-running stage (6 code-review, 7 api-testing, 8 web-testing,
9 qa-manual-runsheet, 10 qa-manual-results). The point is that a human who walks
away can tell, at a glance, how far along the run is and roughly when it ends.

## The rule

A stage that will process more than 15 items MUST emit progress. A stage that
will not, must not — a heartbeat on a 6-item run is noise.

Emit at three moments:

1. **On entry**, once — the denominator.
2. **Every 10 items**, or every 5 minutes, whichever comes first.
3. **On exit**, once — the final tally.

## Format

One block, exactly this shape, so it is greppable and skimmable:

```
[stage 8 · web-testing]  34/103  ▓▓▓▓▓░░░░░░░░░  33%
   PASS 21 · FAIL 4 · BLOCKED 9 | 42m elapsed · ~78m left (1.2 min/case)
   now: TC-REQ-24.3 News counter capped at 9
```

Rules for the block:

- The bar is 14 characters, `▓` filled and `░` empty. Do not use colour.
- Counters are running totals for **this stage only**, never cumulative
  across stages.
- The estimate is `median seconds per completed item × items remaining`.
  Use the median, not the mean — one login pause otherwise poisons it.
- Label it `~` and never state it as a promise. If fewer than 5 items have
  completed, print `estimating…` instead of a number.
- `now:` names the item in flight. This is what tells a returning human
  whether the run is alive or wedged.

## The progress file

Alongside the chat output, maintain `<STORY>-progress.md`, rewritten (not
appended) at every heartbeat:

```markdown
# EP-47675 — run progress
Updated: 2026-08-05 16:12 · stage 8 of 10

| Stage | Items | Done | Verdicts | Status |
|---|---|---|---|---|
| 5 pr-summary | 3 PRs | 3 | — | ✅ 4m |
| 6 code-review | 103 | 103 | 17 judged, 86 routed | ✅ 31m |
| 7 api-testing | 10 | 10 | 7 PASS · 3 blocked | ✅ 12m |
| 8 web-testing | 103 | 34 | 21 PASS · 4 FAIL · 9 BLOCKED | ⏳ ~78m left |
| 9 runsheet | — | — | — | queued |
| 10 results | — | — | — | queued |

**In flight:** TC-REQ-24.3 · News counter capped at 9
**Blocked on you:** nothing
```

The `Blocked on you` line is the one that matters most. Any stage that pauses
for a login, an authorisation or a decision writes what it needs there before
it stops, so a human returning to the session knows in one line why it is idle.

## Task-list mode (Cowork)

When `TaskCreate` / `TaskUpdate` are available, ALSO drive them, because they
render as a live widget the user can watch without reading chat:

- One task per pipeline stage, created up front by the orchestrator.
- The active stage's task is updated at each heartbeat with the same
  `34/103 · 33%` text.
- A stage that pauses sets its task text to `⏸ waiting: <what you need>`.

Do not narrate task updates in prose. The widget is the narration.

## Timestamps

Every stage writes its start and end time into its own report file's header:

```
Started: 2026-08-05 14:31 · Finished: 15:02 · Duration: 31m · 103 items
```

Without this, no retrospective can measure where the run's time actually
went — which is exactly what happened on EP-47675.
