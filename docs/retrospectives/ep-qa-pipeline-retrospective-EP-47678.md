# ep-qa-pipeline — retrospective from the EP-47678 run

**Story:** EP-47678, Global Search — Top results
**Run:** stages 5–10, machine phase 2026-08-11, manual ingestion the same day
**Scale:** 41 suite cases, 2 PRs read, 19 fixture entities + 2 logins provisioned, 4 bug drafts produced, 1 Defect filed, 1 ticket corrected by comment, 2 suite cases edited, 1 suite case created
**Author:** the same session that ran stages 9–10 and the manual reconciliation. Written at the plugin owner's request.

Read alongside `ep-qa-pipeline-retrospective-EP-47675.md` (24 verdicts overturned),
`-EP-53767.md` (0 overturned) and `-EP-53768.md` (22 overturned). **This run overturned 3 of 41.**
On the headline number it is the second-best run recorded.

The headline number is also the least interesting thing about it. **Only 34 of the 41 verdicts were
produced by executing anything.** The other 7 were settled by reading source code, and they were
published in the same PASS column, with the same weight, as verdicts obtained from a browser. Two of
those seven were wrong. The count gate passed, because the count gate counts rows — it does not weigh
evidence.

All numbers below are computed from the stage reports, the suite, the returned run sheet and the live
re-walk — not from recollection.

---

## 1. Scoreboard

| Stage | Definite verdicts published | Overturned | Accuracy |
|---|---|---|---|
| 5 — pr-summary | n/a (map, not verdicts) | — | correct, and non-obvious: it attributed the locale string to PR 7123, not PR 7093, whose 51-file diffstat contains no locale file |
| 6 — code review | 8 (7 PASS · 1 FAIL) | **3** | **62%** |
| 7 — api-testing | 5 (2 PASS · 1 FAIL · 2 PARTIAL) | 0 | **100%** |
| 8 — web-testing | 32 (19 PASS · 5 FAIL · 1 FAIL CONFIRMED · 7 BLOCKED) | 0 | **100%** |
| 8 — BLOCKED calls | 7 | 0 avoidable | **100%** appropriate |
| 9 — fixtures | 2 of 7 blocked cases "unblocked, conditionally" | both still unexecuted | **0 cases actually recovered** |

**Stage-10 ingestion: 26 CONFIRMS · 5 FILLS · 3 RETRACTS · 0 non-standard · 0 unmatched · 7 not run.**

### The 3 changed verdicts

| Shape | Case | What it means |
|---|---|---|
| FAIL → PASS | TC-REQ-1.2 | The expected result was wrong, not the build |
| PASS → BLOCKED | TC-REQ-2.3 | Published PASS for a state the same run had proven unreachable |
| PASS → BLOCKED | TC-REQ-5.3 | Published PASS for a case that cannot execute on a deployed host |

All three originated in stage 6. **Stages 7 and 8 — everything that touched a running system — were
100% accurate across 37 verdicts.** That is the sharpest signal in this run and it points at exactly
one thing: the failure mode is not the testing, it is the *not*-testing.

### What earlier runs' fixes did and did not carry over

- **Positive controls (EP-47675 F1, EP-53768 F1): held, properly, for the first time.** Both absence checks carried a control recorded on the same surface in the same run — api-testing used the endpoint's legacy `{"query": …}` path to prove `zzqqxwv1234` genuinely matches nothing, and web-testing proved the hide path works by showing the empty query renders no `#top` and no chrome while sections stay intact. This is the finding that has dominated two prior retrospectives. It is fixed.
- **Verdict maps derived from explicit id lists, not regex over prose (EP-53768 F9): held.** No verdict map was scraped this run.
- **Count reconciliation: held, and handled well under pressure.** `reconcile_counts.py` reported higher raw id counts than the reports' Statistics. Rather than suppress or "fix" the number, the run verified by hand, identified the excluded sections producing the false positive, and changed nothing. Correct behaviour.
- **Screenshot path as an environment precondition (EP-53768 F7): did NOT hold.** Unchanged and unchecked — see F9.
- **"Published from a code read alone" (EP-53768 F2): did NOT hold.** It regressed with the polarity flipped — see F1.

---

## 2. Where the errors actually were

Three wrong verdicts, one cause. Stage 6 is allowed to settle a case as PASS from source code, and
nothing downstream distinguishes that from a PASS obtained by looking at the product.

The seven cases settled this way were TC-REQ-2.3, 3.2, 5.3, 7.1, 9.2, 10.1, 14.1. Five happened to be
right — confirmed by a live walk during stage 10, which is the only reason we know. Two were wrong, and
both were wrong in a way stage 6 had the information to catch:

- **TC-REQ-5.3** was published PASS while the *same code review* wrote RISK-CR-6 about that very case — the shipped mock fixture carries 16 items, not the 12 the case names, and the case is only executable on a dev build with `NEXT_PUBLIC_SEARCH_MOCK=true`. The stage knew the case could not run on a deployed host and marked it PASS anyway.
- **TC-REQ-2.3** was published PASS for a state the run itself proved unreachable: it requires `top` empty while entity sections are non-empty, and the padding defect means `top` is never empty for a non-empty query. Worse, a PASS here directly contradicts TC-REQ-2.1 on the same sheet, which records a full strip rendering for a no-match query. **Two rows of the same report asserted opposite things about the same page state, and nothing noticed.**

The third, TC-REQ-1.2, is a different animal and is discussed as F4.

---

## 3. Findings, worst first

### F1 — a PASS from a code read is indistinguishable from a PASS from execution (severity: critical)

This is EP-53768's F2 with the sign reversed. That run published `NOT IMPLEMENTED` from repository
evidence; this run published `PASS`. Same root: a stage that cannot see the product is permitted to
issue a terminal verdict, and the report format has no column that records how a verdict was obtained.

`PASS` from a code read is more dangerous than `NOT IMPLEMENTED` from a code read, because it is even
less likely to be questioned. Nobody re-tests a pass.

Seventeen percent of this run's verdicts (7/41) were of this kind. Twenty-nine percent of those (2/7)
were wrong. Both wrong ones were wrong because the case *could not run in the target environment at all*
— a fact about the environment, which is precisely the thing a code read cannot see.

**Fix.** Every verdict row carries a required `evidence:` value — `executed` / `code-read` / `inferred`.
A `code-read` verdict may not be recorded as PASS; it renders as `QA — suspected pass, not executed` and
is excluded from the pass tally in every roll-up. The run report's "Final: PASS 27" line would then have
read `PASS 20 · SUSPECTED 7`, which is the truth and would have routed all seven to the human instead of
five of them accidentally.

### F2 — the run sheet is delivered pre-filled with the machine's own verdicts (severity: critical)

Stage 9 builds the manual run sheet with the Result column already populated with the machine verdict.
The tester is then asked to confirm or overturn — but every unchanged row is indistinguishable from a row
nobody opened.

Of 41 returned rows, **exactly one** is provably human-edited (TC-REQ-1.2, pre-filled FAIL → PASS). The
other 40 carry the value they shipped with. The sheet cannot tell you whether that is 40 confirmations
or 40 untouched cells, and stage 10's entire purpose is to ingest a signal the artifact is not capable
of carrying.

This also silently inverts the pipeline's own risk model. The rows most in need of a human — the seven
never-executed ones — were pre-filled PASS, which is the value least likely to prompt anyone to look.

**Fix.** The Result column ships **blank**. The machine verdict moves to a separate, visually distinct,
read-only column (`Machine said`). A blank Result stays blank and is reported as not run. The cost is
that a tester must tick 41 boxes; the benefit is that a tick means something. If ticking 41 boxes is too
expensive, that is an argument for a shorter sheet, not for pre-filling it.

### F3 — "can this case run here at all?" is never asked (severity: high)

Both bad verdicts came from cases that were *unexecutable in the target environment*, and in both cases
the run held the evidence of unexecutability in its own artifacts. There is no executability
precondition anywhere in the pipeline: a case is assumed runnable until a stage happens to trip over the
reason it is not.

**Fix.** Before any stage settles a case, it must answer whether the case's preconditions are satisfiable
on the run's environment. Where they are not — a mock-only build flag, a module that is off, a state
another defect makes unreachable — the verdict is `BLOCKED — not executable here`, with the blocker
named. This is cheap: the information sat in RISK-CR-6 and in the padding finding, in the same
documents, hours earlier.

### F4 — a single-source spec conflict was published as a defect while multi-source conflicts were handled correctly (severity: high)

This run handled *nine* requirements carrying two contradictory versions with real sophistication:
version A and version B cases reported on separate rows, an explicit refusal to give a single verdict,
and a "which version was built" table settled by finding the discriminating case. That is the best
requirement-conflict handling in any run so far.

REQ-1's heading copy is mechanically the same problem — the spec says `Top results`, the build ships
`Top Results` — and it was published as `FAIL CONFIRMED`, escalated into a bug draft, and written into
the suite as a product defect. The difference is only that the conflict had one documented side rather
than two, so the machinery built for conflicts never engaged.

It was wrong. The shipped copy is correct and the specification was stale. Cost: one FAIL published to
Jira, one bug draft written, one suite case needing correction.

**Fix.** Extend the discrepancy concept to spec-vs-shipped for copy, labels and enumerations. A
mismatch where the *only* deviation is capitalisation, wording or ordering of a user-facing string is a
`discrepancy — product-copy decision`, never a `FAIL`, unless a second source corroborates the spec.
The run report actually said this in its own triage note — *"this is a product-copy decision, not a
code-logic defect"* — and then published FAIL anyway. The insight existed; the status vocabulary had
nowhere to put it.

### F5 — an unverified consequence travelled into a bug draft alongside verified facts (severity: high)

RISK-CR-5 recorded a verified fact — `global_search.top_results` exists only in the `en` bundle — and an
unverified consequence: non-English locales *"may render the raw key"*. The verified and the unverified
halves were written in the same voice and carried together into Draft 1 as "arguably the more important
half".

The consequence was false. The locales fall back to the English string; the heading reads `Top Results`
everywhere. Verifying it took one question and one check.

This is EP-53768's F5 recurring one level down: that run applied evidence classes to *defects*; risk
rows and their consequences got none.

**Fix.** Apply the evidence class to every claim that reaches a draft, not just to defect headlines. A
consequence that has not been observed is written as an open question with the check that would settle
it — never as a co-equal finding.

### F6 — the duplicate search finds duplicates but not precedents (severity: medium)

Draft 3's duplicate check was genuinely good: two searches, 39 hits reviewed, correct identification of
EP-55860 and EP-56095 as related-not-duplicate, and correct reasoning about why the translation tickets
were a different subsystem.

It did not surface **EP-55937** — a Defect raised by this same pipeline on the sibling story, on the
neighbouring "capped at 10" behaviour, **Closed by reject** the day before because the argument was read
as an acceptance-criteria dispute and the ACs had since changed. That is the single most decision-
relevant piece of history for how EP-56133 should be argued, and the drafting stage never saw it,
because it searched for tickets describing the same *symptom* rather than tickets whose *argument* had
already failed.

EP-56133 was reframed by hand as query-insensitivity, with the number 10 demoted to a symptom,
specifically to avoid that fate.

**Fix.** The pre-file search includes closed and rejected tickets in the same component and epic, and
the draft must quote any rejection reason found in the neighbourhood. "This argument was rejected here
before, and this is why this one differs" belongs in the ticket body.

### F7 — stage 9 provisioned before proving the fixture could reach the surface under test (severity: medium)

Nineteen entities, two logins and seventeen side-effect owner accounts were created on a live event to
unblock four cases. The fixture was verified — carefully — on the endpoint's **local-filter** path.
The cases run against the **DS-ranked** path. The DS path had not indexed any of it, and four re-reads
across eleven minutes confirmed 0 of 12 fixture exhibitors in the strip.

Net cases recovered: **zero**. TC-REQ-6.1 and 6.2 were marked READY and came back blank; 17.1 and 17.2
were correctly left blocked on the upstream defect.

The disclosure was exemplary — the honest caveat is the clearest paragraph in the testdata notes, and
the decision to leave the rows READY with a positive-control stop condition rather than grey them out
was defensible. But the ordering was backwards: reachability on the path the case actually uses is a
precondition for provisioning, not a result of it.

One further cost: a `product/set` call returned **HTTP 500 with an empty body and created the row
anyway**, and there is no product delete endpoint on the admin REST API, so the run left an
unrevertible artifact on a live event that a human had to remove by hand.

**Fix, two parts.** (1) Prove reachability on the exact path the case exercises, with one throwaway
object, before bulk-provisioning. (2) Do not create an entity type whose delete path has not been
confirmed to exist; if none exists, say so and get an explicit decision first.

### F8 — a defect draft need not name the requirement it breaches (severity: medium)

Draft 2 (light-card widths diverging below `sm`) came from genuinely good work: a code-review risk
chased to a runtime measurement, 240px next to 270px in one row at 560px, a defect no case in the suite
could have caught. Finding it was the pipeline at its best.

Drafting it as a Medium bug was not. **No requirement specifies light-card width below the `sm`
breakpoint.** REQ-12's two versions state a width without qualifying a viewport, and the design source
never covers mobile. A dev could reasonably bounce it as "mobile was never specified", and the ticket
would have burned credibility that EP-56133 needed.

The draft asserted "this holds under BOTH readings of REQ-12" without noticing that neither reading
mentions a breakpoint.

**Fix.** Every defect draft carries a `breaches:` line naming the requirement and the clause. If no
clause covers the observed condition, the item is routed as a discrepancy or an open question against
the requirement — not filed as a bug. The evidence still lands somewhere permanent; `GSTOP-WDTH-05`
already does exactly this and is the model.

### F9 — environment preconditions are still not checked before the run (severity: medium, recurrence)

EP-53768's F7 said: treat a collectable screenshot path as an environment precondition checked at step 0.
Unchanged. This run's Playwright screenshot root is still `C:\Users\…\Temp\.playwright-mcp`, outside the
Cowork-connected folder, so the evidence image for the live re-walk could not be written next to the
report.

New, same family: the **Claude in Chrome extension was unusable for the entire session** —
`tabs_context_mcp` reported tabs correctly and navigation worked, while every content read and
screenshot failed with `Cannot access a chrome-extension:// URL of different extension`, across two
tabs and three tool types. Six failures before falling back to Playwright, which worked immediately.
That is six wasted round-trips discovering an environment fact that a two-call preflight would surface.

**Fix.** A step-0 preflight that (a) writes and deletes a probe file at the screenshot root and reports
whether it is collectable, and (b) executes one trivial read on each available browser backend and
records which are alive. Both results go in the report header, and stage 8 picks its backend from that
rather than from a default.

### F10 — stage 8 recorded a shared-browser hazard as a caveat, not a consequence (severity: low, recurrence)

EP-53768's F4 again, in its mild form. Stage 8 detected that the browser profile was shared, that
another consumer logged a session in and forced a tab back to `/global-search` several times, and it
handled this *well* — re-taking affected measurements in an isolated tab verified stable over a 25s
poll, and explicitly declining to report the URL resets as a product defect.

That is the right response, and it happened because the stage chose to, not because anything required
it. The mechanism from EP-53768's F4 — detection must void affected assertions, not annotate them — is
still not implemented. It worked here on judgement.

---

## 4. What the design got right

Listing these because three of them are fixes from earlier retrospectives finally landing, and one of
them prevented two bad tickets in this run alone.

- **Positive controls, at last.** See §1. Two prior retrospectives named this as the critical finding; this run honoured it without being asked, on both absence checks, on the same surface, in the same run.
- **Bug drafts are drafted, not filed.** Four drafts produced; final disposition was **1 filed, 1 dropped entirely, 1 parked as a discrepancy, 1 folded into another ticket as a correction**. Three of four would have been wrong or premature as tickets. This single gate is the highest-value control in the pipeline and it paid for itself twice in one session.
- **Upstream attribution held under pressure.** The padding defect fails four of this story's cases and blocks four more — every incentive pointed at filing it against EP-47678. The run refused, proved the front end renders faithfully (`prepareTopItems.ts` filters and maps only; the strip gates on `topItems.length > 0`), and attributed it to the story that owns the endpoint.
- **The suite is treated as the system of record, explicitly.** Stage 9's reasoning is worth quoting as doctrine: writing a correction into the run sheet loses it, because the next run regenerates from the suite and repeats the mistake. Nine corrections went into case notes, append-only, `status` untouched, each read back to confirm.
- **A defect with no covering case got a case.** `GSTOP-WDTH-05` was created to hold the below-`sm` width divergence, traced, prioritised, and deliberately kept off the run sheet because it postdates the 41 and is expected to fail. "Written to hold the defect, not to describe it away" is the right instinct.
- **A prior report's claim was re-measured and honestly not reproduced.** The 2.3–6s endpoint latency warning inherited from earlier work was measured across 55 calls — cold 4.50s, warm median 1.08s, max 1.88s, zero calls near the 8s front-end timeout — and reported as not reproducing, rather than repeated because it was in the file.
- **Determinism was checked rather than assumed.** Three consecutive repeats plus a 25-minute-apart repeat, byte-identical id sequences, before any query-insensitivity claim was made.
- **The input-quality call was correct and unflinching.** 🔴 on input quality, with six unresolved product conflicts and two unanswered open questions named as the reason eight requirements cannot be given a verdict at all. That is the finding the business most needs and the one easiest to soften.

---

## 5. If only three things change

1. **F1 + F2 together.** They are one problem seen from two ends: the pipeline cannot distinguish a verdict that was tested from one that was asserted, and neither can the sheet it hands the human. An `evidence:` field on every verdict and a blank Result column would have caught both bad verdicts in this run automatically, and would have routed all seven never-executed cases to a person.
2. **F3.** Ask whether the case can run here before settling it. Both errors in this run were environment facts sitting in the run's own artifacts.
3. **F4.** Give single-source spec conflicts the same treatment the pipeline already gives two-sided ones. The vocabulary exists and is used well; it just does not reach the case where only the spec speaks.

Everything else on this list is a refinement. Those three are the difference between 62% and something
closer to what stages 7 and 8 already achieve.

---

## 6. Numbers for the record

| Metric | EP-47675 | EP-53767 | EP-53768 | **EP-47678** |
|---|---|---|---|---|
| Cases | ~? | ~? | 66 | **41** |
| Verdicts overturned at stage 10 | 24 | 0 | 22 | **3** |
| Defects reported → confirmed | — | — | 7 → 1 | **4 drafted → 1 filed** |
| Positive controls honoured | no | partial | no | **yes** |
| Verdicts from execution | — | — | — | **34 / 41 (83%)** |

Final verdict published for the story: **❌ FAIL — 26 PASS · 6 FAIL · 2 BLOCKED · 7 not run**, with
EP-56133 named as the blocker for nine cases.
