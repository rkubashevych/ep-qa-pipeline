# ep-qa-pipeline — retrospective from the EP-55706 run

**Story:** EP-55706, Global Search — UI improvements based on feedback from IMEX
**Run:** one Cowork session, 2026-08-12, stages 5–9 complete; stage 10 not yet run
**Scale:** 52 suite cases + 6 structural checks, 2 frontend PRs (89 files), 5 Jira comments posted, 27 suite write-backs, 1 bug filed, 1 new suite case created
**Author:** the same session that ran it. Written at the plugin owner's request, after he asked one question the pipeline had no mechanism to ask itself.

Read alongside `ep-qa-pipeline-retrospective-EP-47675.md` (24 verdicts overturned),
`-EP-53767.md` (zero overturned) and `-EP-53768.md` (22 of 66 overturned). This run cannot yet
be scored against those — the human round has not happened. What it can contribute is a **failure
mode none of the three earlier retrospectives names**, because it is not a verdict error. It is a
premise error, and every verification the pipeline owns is structurally incapable of catching it.

---

## 1. The finding, in one paragraph

The run published **TC-REQ-20.2 as FAIL** and filed **EP-56188** against it, asserting that News
cards must be "no larger than other result cards on the page". That clause appears in **exactly one
of the three sources**, and it is the one that was superseded. The Confluence acceptance-criteria
page (P2 2018639874, item 4) requires only "equal in size, single horizontal scroll, no enlarged 1st
card". The implementing sub-task **EP-55973** requires the same three things and no more. Only the
design sub-task **EP-55708** carries the cross-section clause. **Against the spec of record, the
build passes.** The correct verdict is SPEC-DEFECT — the same bucket as 14.2, 16.1 and 17.2 — and
the bug should be a product question, not a defect.

The cost was one wrong published verdict, one wrongly-typed Jira bug, and one suite case carrying a
FAIL it did not earn. The fix cost **one `getConfluencePage` call**, made only because a human
asked "is there any requirement for this?".

---

## 2. How the error was created

`qa-service-publish.md` defines a requirement's `source` as *"(the AC page or ticket it came from)"*
— **singular**. Grooming duly wrote one string. Here is `GSRCH-RULE-18` as published:

> **statement:** Every card in the News section has the same width and height as every other News
> card, **and no News card is larger than the result cards of the other category sections on the
> same page.**
>
> **source:** Confluence P2 2018639874 item 4 **and its acceptance criteria**, and design sub-task
> EP-55708 item 2

The statement is the **union of two sources**. The `source` line names both **as if both supported
all of it**. Clause 1 comes from the AC page; clause 2 comes from EP-55708 alone. Nothing in the
artifact records that split, so nothing downstream can recover it.

This is not a transcription slip. It is the grooming method working as written. `## Grooming method`
question 4 tells the stage to find "contradictions between requirements in the context file" — and
these two sources do not *contradict*, they **differ in scope**: one says strictly more than the
other. There is no instruction covering that case, so the stage did the natural thing and merged.

The sharpest evidence that this was a systemic gap rather than inattention: the docs phase flagged
**9 requirements as needing clarification and 4 as outright contradictions**, including **REQ-21 —
the other News requirement**. It was looking hard at this exact area of the page and still collapsed
REQ-20, because REQ-20 did not match any pattern it was told to look for.

---

## 3. Why four later stages could not catch it

| Stage | Had the evidence? | Why it passed |
|---|---|---|
| 6 — code review | **Yes** | EP-55973's acceptance criteria were in its inputs. It never compares a case's asserted expectation against the implementing sub-task's own criteria — it compares the case against the *code*. Classified 20.2 "QA — visual sizing not readable from code" and routed it on. |
| 7 — api-testing | No | Out of scope, `[UI]` case. |
| 8 — web-testing | **Forbidden** | The skill explicitly bars reading the tracker or code. Correct by design — but see §4, because it reasoned its way to the answer anyway. |
| analyzer | No | Checks traceability (does REQ-20 have a case?) and counts. Both were perfect. Neither asks whether REQ-20 is *true*. |
| step 6 count gate | No | `reconcile_counts.py` is arithmetic. It agreed with itself, correctly. |
| step 9 post-publish verification | No | Verified 27/27 write-backs landed, both comments exist, bug traceable. All confirmed a **wrong** verdict was published **faithfully**. |

**The structural cause:** the code phase never reads the primary source. It reads the *derived*
cases — that is the whole design, and it is what lets the phases run in separate chats. A
mis-derivation upstream is therefore invisible downstream **by construction**. Every stage after
grooming inherits the error, and none of them holds the document that would expose it.

### The verification paradox

This run was heavily verified. Count gate, `reconcile_counts.py` self-test, traceability recount by
hand, a dedicated post-publish pass, 27/27 write-backs re-read from the live suite. Every one of
those asks **"do these numbers agree with each other?"** None asks **"is the premise true?"**

Internal consistency cannot detect a uniformly-propagated wrong premise. It is the one property
guaranteed to be preserved by it. A run can be perfectly self-consistent and confidently wrong, and
this one was — the machinery all reported green while carrying a false requirement end to end.

---

## 4. The near-miss, and why it is the most useful thing in this run

Stage 8 measured the cards, failed the case, and then wrote this into its own findings section
**unprompted**:

> the case would "pass" if the tester happened to pick one of those as the comparison section. The
> case text should name the comparison section, or the requirement should state a maximum.

Compare the skill's own SPEC-DEFECT definition:

> executing the case showed its premise or expected result is wrong (the UI element it assumes does
> not exist as described, the expected behaviour contradicts the ticket's own spec). Not a FAIL, not
> a PASS: the case or requirement needs correcting.

**Stage 8 wrote the SPEC-DEFECT rationale in prose and filed the row as FAIL.** It had the right
analysis and the right vocabulary available and did not connect them. That is a cheap fix — see
proposed edit **F2** — and it is cheap precisely because the reasoning already happens; only the
classification step is missing.

Then the orchestrator (me) read that caveat, found it convincing enough to **reproduce verbatim in
the bug draft** under the heading *"the wrinkle you'll get pushed back on"*, and filed the Bug
anyway. I wrote that a developer "can reasonably answer works-as-intended, and under a literal
reading of REQ-20 they'd have a point" — then did not spend the one call needed to find out whether
they'd have a point. **Predicting the rebuttal precisely enough to pre-argue against it is the
strongest available signal that the premise needs checking, not defending.**

---

## 5. Scoreboard, such as it is

| Stage | Verdicts published | Known wrong so far | Note |
|---|---|---|---|
| 5 — pr-summary | n/a (map) | — | 89 files, both PRs; correctly identified with no dev sub-task branches surviving |
| 6 — code review | 32 definite (28 PASS · 2 FAIL · 2 SPEC-DEFECT) | 0 confirmed | 2 FAILs never verified — see §6 |
| 7 — api-testing | 2 PARTIAL + 1 risk FAIL CONFIRMED | 0 | ground truth established, EP-56095 confirmed at runtime |
| 8 — web-testing | 27 rows (18 PASS · 1 FAIL · 5 BLOCKED · 3 SPEC-DEFECT) | **1** (the FAIL) | 6/6 structural checks executed |
| structural checks | 6 of 6 | 0 | |

**1 correction so far, and it came from a human question, not from any pipeline mechanism** — the
same pattern the EP-47675 and EP-53768 retrospectives both record. Stage 10 has not run, so the
true accuracy is unknown and this table will move.

### What the run got right, for balance

- The **highest-value case in the ticket** (TC-REQ-26.1, the deep-link prefill regression) was
  executed in a **genuine unauthenticated context**, not a signed-in approximation. That is the
  distinction the QA sub-task warned would make or break the verdict, and stage 8 honoured it.
- **Five BLOCKED calls were all genuine and all probed.** Stage 8 tried four zero-result queries,
  route interception, a forced 500 on the RSC payload and pathological input before concluding the
  empty and error states were unreachable; stage 9 then probed three admin levers and reverted every
  write. Set against EP-53768, where **10 of 12 BLOCKED calls were avoidable**, this is the single
  clearest improvement between runs — the `Probe:` requirement is working.
- The **count gate held**. Every report's Scope and Statistics agreed with the mechanical count
  before anything reached Jira.
- **Zero writes leaked.** Every probe that mutated admin state was reverted and re-verified.

The BLOCKED improvement matters and should not be lost in the noise of §1. It is what the earlier
retrospectives asked for, and it worked.

---

## 6. Two verdicts this run could not settle, and should have flagged louder

TC-REQ-19.1 and TC-REQ-25.1 arrived FAIL from code review and ended BLOCKED — the genuine
sections-less empty state is unreachable on event 3551. They were reported accurately, but the human
summary listed them under "needs a human" rather than saying plainly: **two code-read defect claims
are sitting unverified, and the pipeline's own base rate for unverified code-read claims is poor**
(EP-53768: 6 of 12 "NOT IMPLEMENTED" verdicts were wrong). A code-read FAIL that never got runtime
confirmation deserves a distinct, louder status than "blocked" — see proposed edit **F4**.

Worth noting the empty-state blocker also hid the more interesting question. TC-REQ-25.1's code
finding is that the panel title resolves to `No results for {query} found`, which matches **neither**
documented version (A says "No results found", B says "No results for {query}"). That is a third
string nobody specified — a likely SPEC-DEFECT hiding behind a BLOCKED.

---

## 7. A second, smaller instance of the same class

`GSRCH-FR-08` (inherited from EP-47675) states:

> The card for an entity on this page MUST show the same fields in the same layout as that entity's
> card on its own listing page.

If every block reuses its own listing page's card, card sizes are **inherited** and cannot be
equalised across sections. Measured on the live build: five distinct card sizes on one page (246×287
· 246×296 · 254×294 · 300×337 · 344×515 · 424×300). So REQ-20's clause 2 is not merely
under-specified — it is **unsatisfiable while FR-08 holds**.

Two requirements in the same suite contradict each other, one of them inherited from an earlier
story, and no stage compares a new requirement against the established suite for *satisfiability* —
only for contradiction of a stated rule. Grooming's suite-comparison step exists (`## Grooming
method`, question 4, last bullet) but is scoped to "a rule flipped, a limit changed, an invariant
broken". Mutual unsatisfiability is none of those.

---

## 8. Errors made by this session, for symmetry

1. **Filed EP-56188 as a Bug with the doubt already written down.** §4. The primary error.
2. **Published a FAIL that should have been SPEC-DEFECT**, requiring a retraction under the
   supersede convention — the exact ceremony the convention exists for, incurred avoidably.
3. **Shipped a broken measurement snippet to the user.** The DevTools one-liner labelled each
   carousel using `closest('section, .MuiPaper-root, div')` — `div` matches almost immediately, so
   it printed the first *card's* text rather than the section title. The user's output showed News
   as "August 5, 2026" and two session blocks as "News" and "Help". The numbers were right, the
   labels were nonsense, and a tester without the mapping would have drawn the wrong conclusion.
4. **Wrote "Screenshot in the archive comment" into the human summary** when the archive is text
   only and the MCP cannot attach images. Caught and corrected before posting, but it was drafted.
5. **Did not re-verify stage 7's guest-context numbers against stage 8's signed-in numbers** until
   the divergence (115 vs 96) forced it. Both were correct for their context; the run should have
   established which context was authoritative *before* two stages measured in different ones.

---

## 9. The one-line conclusion

Every verification this pipeline owns is a **consistency** check, and this run's error was a
**fidelity** error — so a run that was green on every gate it had shipped a requirement that its own
spec of record does not contain. The gap is not in any stage's diligence; it is that no stage is
ever pointed back at the primary source after grooming reads it once.

Proposed edits: `ep-qa-pipeline-proposed-edits-EP-55706.md`.
