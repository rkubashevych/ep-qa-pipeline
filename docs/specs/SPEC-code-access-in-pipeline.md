# Where the source clone belongs in the pipeline

Status: **analysis + proposal — nothing implemented.**
Author: Claude session, 2026-08-19. Decision needed from: Roman.
Evidence base: all 57 skill files, CHANGELOG.md, 5 retrospectives,
PIPELINE-REVIEW-2026-07-30, and 222 per-ticket run artifacts across 25
tickets.

---

## 0. URGENT, unrelated to the question — a credential is committed

`portal-ui`, branch `master`, file `.gitmodules`: the
`expo-react-components` submodule URL has a **Bitbucket username and
token embedded in it in plaintext**. It is on master, it is in history,
and it reaches every developer who has ever cloned `portal-ui`.
(`admin-ui`'s `.gitmodules` declares the same submodule cleanly, with no
credential — so this is a mistake in one repo, not a convention.)

I have not used it and am not repeating it here. Actions: rotate that
credential, replace the URL in `portal-ui/.gitmodules` with the clean
form `admin-ui` already uses, and treat the history as compromised.
Your own `CLAUDE.md` rule applies exactly — *"A failed command that
echoed a secret = rotate the token."*

Second finding from the same check: **`expo-react-components` returns
404 for your token.** It is not among the 15 repos you can read. So the
recurring blind spot your run reports keep hitting —
`EP-47678-code-review.md:11`, *"`expo-react-components` is a git
submodule; `SwiperSlider`, `SessionHeader`… are **not readable from
this repo**, so any verdict that depends on their internals… is QA
rather than PASS"* — **is not fixed by cloning.** It needs a read grant
on that repo. That is a one-line ask to whoever owns Bitbucket access,
and it removes a cap that has downgraded verdicts on at least three
tickets (EP-47678, EP-53768, EP-55295).

---

## 1. The short answer to your question

**Do you need the repo at all?** Yes — but for less than you'd hope,
and not primarily in the docs phase.

**Where you guessed (docs phase, to settle open questions):** half
right. Reading the *pre-change baseline* to answer "how does this work
today?" is sound and your pipeline already has the channel for it.
Reading the *feature branch* during stages 1–4 would be actively
harmful — it would quietly delete your only detector for "the developer
built the wrong thing".

**Where it actually pays:** stage 6 code-review, and it is not close.
That is the one stage whose own text disclaims its verdicts —
`code-review/SKILL.md:299`, *"A FAIL from code reading alone is a CLAIM,
not a settled verdict"* — with a measured error rate beside it at
`:305-306`: *"half of code-read-only negative verdicts were wrong
across real runs (6 of 12 on one ticket)"*. Every one of its four
unreachable verdict classes is a whole-tree-search problem.

**And the honest caveat:** your pipeline's *worst* failures are not
code-visibility failures, and more code access pushes on its known
worst habit. §5 is the guardrail that has to ship with the clone. If
you only read one section, read that one.

---

## 2. The clone changes an outcome in exactly four places

Ranked by evidence, not by appeal.

### 2.1 Stage 6 — regression vs pre-existing (highest value)

Today: `code-review/SKILL.md:116-117` — *"Read files only from the head
branch of the PR. Do not read files from the base branch, master or
other branches."* That rule exists for a good reason (verdicts drifting
onto code the PR didn't ship), but it makes "is this FAIL a regression
or has it always been like that?" formally unanswerable. The stage gets
one narrow escape at `:243-247` — check the full file from the PR branch
before marking FAIL — which is head-branch only, never a before/after.

Change: permit reading **the merge-base of the head branch** —
explicitly not master's tip, not other branches, not the general
repository context. `EP-55279-pr-summary.md:4` shows merge-base diffing
already in use elsewhere in the pipeline, so this is consistent, not
novel. This is the single change with the clearest link to the measured
50% false-negative rate.

### 2.2 Stage 6 — absence claims become provable

Three instructions currently assert absence from a ~20-file diff:

- `:239-241` — *"whether what should have been removed was actually
  removed (e.g. an old field/key **no longer read or written
  anywhere**)"*. "Anywhere" across 37,900 files.
- `:290-292` — `SPEC-DEFECT` covers a case whose premise names something
  that *"does not exist in this codebase"*.
- `:358` — N/A requires *"concrete evidence from the code"*.

There is a positive control on record for how this looks done properly,
from the one run that *did* have whole-tree search:
`EP-53978-retest-code-review.md:236` — *"At `alpha` head
`Account::createConnection()` has no production call site… Verified by
workspace code search plus the direct grep of all 12 non-vendor files
above the index threshold, so the search covers the whole repo."* That
is the standard the other 24 tickets couldn't meet.

### 2.3 Stage 5 — blast radius becomes producible at all

`pr-summary/SKILL.md:147-163` already *requires* it: flag every shared
changed file *"with one line naming what else consumes it — based only
on what the code shows (imports, usages, table names)"*. Identifying
consumers **is** whole-tree search. The instruction contradicts its own
access model, and the analyzer absorbs the failure as cosmetic —
`qa-run-analyzer/SKILL.md:120-124`, *"a visibility flag for regression
risk, not a failure of the run."* A clone makes a mandated section real
rather than aspirational, and it feeds stage 6's unmapped-changes check
(`code-review/SKILL.md:318-329`).

### 2.4 Stage 7 — route and payload discovery

This is the cheapest, most boring, best-evidenced win. Stage 7 currently
*probes* for endpoint names — `api-testing/SKILL.md:133-134`, *"confirm
the real `/api/v1|v2/...` path by probing and reading the error
message"*, implemented as a literal loop over guessed spellings
(`api-testing-reference.md:160-167`). What that has cost:

| Ticket | The guess | What it cost |
|---|---|---|
| EP-55194 | probed `sessions/save` → 404; real endpoint is `POST /api/v1/exhibitor/saveSession` | **5 cases published as false BLOCKED**, corrected only because you supplied a Jam recording (`EP-55194-api-testing.md:18`) |
| EP-53768 | 12 web cases blocked needing "an event with 1–2 sponsored products"; the answer was one global setting, `product_search_limit` | **6 wrong BLOCKED verdicts published** to Jira and the suite. Retro F3: *"10 of 12 blocks were avoidable, and 6 of them were unblocked by information that the same run discovered one stage later"* (`ep-qa-pipeline-retrospective-EP-53768.md:143-150`) |
| EP-55104 | `GET /api/v1/visitors/attending` | real endpoint `POST /api/v1/exhibitors/speakAt`; wrong mapping propagated into checklist, test-cases **and** a Jira note on EP-55200 (`EP-55104-run-report.md:37`) |
| (reference) | ticket maps "logo upload" to `photoSave` | *"`photoSave` never writes the logo"* — one controller read (`api-testing-reference.md:277-282`) |

Each of those is a controller or routes file away. Note the doc already
warns you: *"ticket endpoint names can be **wrong**, not just
shorthand"* (`:235`).

### 2.5 Also worth having, lower value

**Stage 9 field semantics.** `provisioning-rules.md:53-66`:
`data.acc.favourite` *"reads like 'has favourited' and is actually 'may
favourite'… Several precondition verifications were built on it and were
**worthless**."* And `:80-84`, a fixture *"created without a consent
value silently defaulted to opted out"* — that default is in a
migration. Both settled by reading source.

**Gains nothing:** `qa-run-analyzer` (reads only pipeline output files;
its checks are consistency arithmetic). **Gains almost nothing on
verdicts:** `web-testing` — the running browser is ground truth, and its
real blockers are auth, hosts, MUI portals and analytics lag, none of
which source resolves. Don't spend effort there.

---

## 3. The docs phase — the safe pattern, and the line not to cross

Your instinct was right that stages 1–4 ask questions code could
answer. The grooming skill already sorts them for you —
`requirements-grooming/SKILL.md:199-209`: *"**Classify every open item:
SPEC or BEHAVIOUR.** … BEHAVIOUR = an observable fact about the app
today"*. BEHAVIOUR items are exactly the code-answerable class:
validator limits, which roles gate a widget, the real default sort,
whether a field is serialised to the mobile API or an export at all,
what the empty state renders.

And you already have the channel: `qa-pipeline-docs/SKILL.md:91-111`,
the stage-2 recon step, with its guard at `:99-107` — *"These are
observations of CURRENT behaviour, not requirements"*, and recon facts
*"may ground an expected result ONLY where the requirement itself
references current behaviour — they never become requirements."* The
measured benefit is recorded at `:109-111`: *"a run with recon ended
with 1 open question; comparable runs without it posted 4–5, most
answerable by looking."*

**The proposal, therefore, is narrow:** add source to the recon source
list at `:95-97`, **pinned to the merge-base / pre-change baseline —
never the ticket's own feature branch.** Every observation carries
`file:line` as evidence. Code ranks **below** the Confluence AC and
below a sub-task in the spec-of-record ordering at `:143-150` — code is
never spec of record. `qa-checklist/SKILL.md:45` and
`qa-test-cases/SKILL.md:73` (*"do not inspect code"*) stay **exactly as
they are**; code facts reach them only through the requirements file,
marked "resolved by observation".

### The line: never read the feature branch in stages 1–4

`code-review/SKILL.md:289-295` defines `SPEC-DEFECT` — *"the code is
consistent and deliberate, but the test case's expected result
contradicts what the ticket/spec itself requires."* That status is your
**only** detector for "built the wrong thing", and it works only
because the test case's oracle is spec-derived and the code is seen for
the first time at stage 5–6. Derive the cases from that same code and
the status becomes unreachable by construction — every `Exp:` turns
into a tautology.

**Absence finding you should know about:** there is no positive
statement of oracle independence anywhere in the docs phase. No rule
says "expected results must be independent of the implementation".
Independence is enforced *purely* by the access ban at
`qa-checklist/SKILL.md:45` and `qa-test-cases/SKILL.md:73`. Relax the
ban and nothing downstream re-imposes it. Worse: the recon guard is
stated **once, in the orchestrator only** — a directly-invoked
`requirements-grooming` run (a supported entry point) is not bound by it
at all. If you touch the docs phase, that rule has to be written down
explicitly first.

---

## 4. The bigger coverage win, which is not the clone

You asked about coverage. The largest gap I found isn't code access —
it's that **the pipeline is blind to the tests that already exist.**

Zero occurrences of `teststone`, `playwright-tests`, `ds-api-tests`,
`qa-tests`, `Codeception`, `PHPUnit`, `Cypress`, `Locust`, `Pact` or
`Vitest` anywhere under `skills/`. The only mention of an existing suite
is instrumental — `login-config.md:3-4` borrows login steps from the
`e2e-testing` Playwright repo. Stage 6 is affirmatively told to ignore
tests (`code-review/SKILL.md:85-86`, *"Do not assess … tests, CI"*).

Meanwhile the machinery is sitting there unused. The QA Service
connector exposes `discover_tests`, `detect_test_source`,
`link_implemented_tests`, `executed_coverage`, `coverage_report`,
`sync_ci_report` — **no skill mentions any of them** — and two
repositories are already registered with report paths mapped: the
monolith (`universal/Tests`, Codeception + PHPUnit) and
`ExpoPlatform-Ltd/e2e-testing` (Playwright).

Consequence: every case with no code-text verdict becomes QA, then a
runtime execution, then a run-sheet row a human walks. A case already
covered by a green Codeception or Playwright test is **paid for twice.**
Given rows are the human's actual time — `CHANGELOG.md:209`, *"32→14
rows on EP-53768, 33→8 on EP-53767"*; `:721`, *"the difference between
handing a tester 89 rows and 11"* — this is where the leverage is.

Placement: discovery in **stage 5** (a "changed file X is covered by
`universal/Tests/Codeception/…`" column is diff-adjacent and factual),
consumed by **stage 9**, which already owns the reduce-the-human-set
decision (`qa-manual-runsheet/SKILL.md:213-243`) and already has an
ALREADY SETTLED class requiring *"runtime-grade evidence"* (`:249-253`)
— a passing CI run is exactly that. Audited by `qa-run-analyzer`.

---

## 5. The guardrail that must ship with the clone

This is the part I'd argue hardest for, because the record is blunt
about it.

1. `CHANGELOG.md:494-496` — *"a code-review PASS removed a case from all
   runtime execution (65% of EP-53978's cases never touched a running
   system)."*
2. `ep-qa-pipeline-retrospective-EP-53768.md:126-137`, severity
   **critical** — *"Twelve cases were classified from repository
   evidence. Six were wrong. The classification is attractive precisely
   because it feels safe… while carrying more consequence: it tells the
   business to stop testing."*
3. `ep-qa-pipeline-retrospective-EP-55706.md:156` — *"the pipeline's own
   base rate for unverified code-read claims is poor."*
4. `EP-47675-run-report.md:341-345` — a full 103-case review by three
   parallel agents finished *before* anyone discovered `/global-search`
   doesn't exist on the authorised host: *"Two requests, under two
   seconds, versus a full code-review pass and a wrong root cause."*
5. `EP-47675-run-report.md:245` — *"A code-reading verdict that lands on
   the right status by the wrong mechanism will send a developer to the
   wrong line."* On that ticket a bug was **filed against working code**
   as the run's #1 finding, and *"was caught by the user, not by the
   stage"* (`:272-282`).

So the rule that ships alongside: **a clone may make a code verdict
better-evidenced; it may never make a code verdict sufficient.** More
searchable code must not increase the share of cases skipping runtime
execution. Concretely — `qa-run-analyzer` should flag 🔴 any case whose
only evidence is a repository search, and stage 9's ALREADY SETTLED
class must keep requiring runtime-grade evidence, with a whole-tree
grep explicitly *not* qualifying.

There's a second, quieter risk. EP-53768 already produced *"10 unmapped
behaviours in the PR that no case exercises"* including a
`ProductVerticalView` `sx` override; EP-55295's RISK-CR-1/2/3 are all
*"no covering case"*. A whole tree multiplies findings on unchanged
code, and `code-review/SKILL.md:88` (*"Do not analyze pre-existing code
that was not changed in the PR"*) becomes load-bearing in a way it
wasn't before. Keep it, and mean it.

---

## 6. Honest accounting

Across 25 tickets of history:

| Bucket | Incident families |
|---|---|
| A clone would have **prevented** it outright | **4** (EP-55194 route, EP-53768 setting, EP-55104 endpoint, the `expo-react-components` cap — and that last one needs a repo grant, not a clone) |
| A clone would have **reduced** the cost | **6** (EP-47675 ×4 incl. retest, EP-55751 route existence, the docs-phase behaviour questions) |
| **Unrelated** — a clone changes nothing | **~11**, including the single worst failure on record |
| Documented cases of code access **causing** harm | **7**, one critical-severity |

The worst failure on record is worth naming because it argues against
you: on EP-53978 the triage *"overturned at least eight verdicts"* and
*"the system of record kept asserting PASS on a violated privacy
requirement"* (`PIPELINE-REVIEW-2026-07-30.md:87`;
`CHANGELOG.md:564-567`). Root causes were instrumentation, provenance
and ingestion lag. A clone touches none of it.

Where this analysis is weakest, stated plainly: **no run report
anywhere says "a repo search would have caught this."** Every
would-have-prevented entry above is reconstruction from "the real
endpoint is X" and "stage 9 found the setting". Only one run
(EP-53978's retest) demonstrably used whole-repo search — n=1. And the
wrong-base-branch hazard is real in principle but no run report records
it firing.

**Verdict:** worth doing, on cost not on correctness. Expect roughly
15–20 recovered blocked-or-falsely-blocked rows across a 25-ticket
horizon, plus three or four fewer human questions per docs run. Setup
cost is 1.4 GB and under a minute. It is not the fix for the pipeline's
biggest problem, and it must not be sold internally as one.

---

## 7. Suggested order

1. **Today, independent of everything else:** rotate the credential in
   `portal-ui/.gitmodules`; request read access to
   `expo-react-components`.
2. **Fix the three doc bugs** in `pr-summary/references/bitbucket-access.md`
   (git username `x-token-auth`; `read:pullrequest` now granted; the
   monolith's base branch is `alpha`). These are wrong *today* and cost
   a failed run each — worth doing whether or not you clone.
3. **Stage 6 merge-base read** + absence-claim change (§2.1, §2.2), with
   the §5 guardrail in the same release. Highest value, smallest
   surface.
4. **Stage 7 route/payload from source** (§2.4). Cheap, well-evidenced.
5. **Stage 5 blast radius** (§2.3).
6. **Write the oracle-independence rule down** (§3), *then* extend recon
   to baseline source. Not before.
7. **Existing-test discovery** (§4) — biggest coverage win, biggest
   design effort, deserves its own spec next to
   `SPEC-two-tier-coverage.md`.
