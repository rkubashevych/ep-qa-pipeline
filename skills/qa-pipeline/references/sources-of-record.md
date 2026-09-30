# Sources of record — the register and the gate

Why this file exists: on 2026-09-07 the code phase (EP-56133, retest 3)
produced three "findings" that were not defects. One of them —
*"a matching Group renders nowhere on the Global Search results page"* —
was minutes from being filed as a Bug. The as-built front-end
documentation names `groups` as its own example of a type the front end
**deliberately does not render**. The finding was correct as an
observation and wrong as a defect, and nothing in the pipeline caught it,
because **no stage of the code phase reads a source of record at all**.

The gap was structural, not a lapse:

- `task-context` (stage 1) fetches the acceptance-criteria page — but
  stage 1 does not run in retest or bug-fix mode, which is most code-phase
  runs.
- `code-review`'s source-fidelity check fires only for FAIL-bound and
  High-risk **test cases**. Observations and risk rows never touch a spec.
- The bug-drafting gate fires last, after a finding has already been
  written into a report, a chat summary and a run sheet as though settled.
- Only the *product brief* was ever in scope. Briefs say what should
  exist. **As-built documents say what deliberately does not** — and that
  is the document class that defeats a false defect.

## 1. What counts as a source of record

Four kinds, in precedence order. Higher beats lower on a contradiction,
and a contradiction is a `discrepancy` finding, not a defect.

| # | Kind | Where it lives | What it settles |
|---|------|----------------|-----------------|
| 1 | **Product brief / acceptance criteria** | Confluence, linked from the ticket (ExpoPlatform: space `P2`) | What the build must do. The Given/When/Then clauses. |
| 2 | **As-built documentation** | Confluence, written from merged code (ExpoPlatform: space `FRON` for front end, `DS` for the search service) | What the build actually does, and what it deliberately does **not** do. Names the entities, states and paths that exist. |
| 3 | **Implementing sub-task's own acceptance criteria** | Jira, on the Backend/Frontend sub-task | What was actually commissioned. A clause in the brief but not here is a mis-derived requirement. |
| 4 | **The ticket under test** | Jira description + comments | For a Bug: the reproduction steps and the stated expected result. Nothing else. |

A test case is **not** a source of record. Neither is a suite
requirement, an earlier run's report, a Slack message, a developer's
comment about intent, or this pipeline's own prior verdict. All of those
are derived, and a derived artifact cannot license a defect claim about
the product.

## 2. The register

Every code-phase run keeps `<KEY>-sources.md` in the run folder:
one row per source, with its id, what it governs, and the fetch date.

```markdown
| # | Source | Id / key | Governs | Fetched |
|---|--------|----------|---------|---------|
| 1 | Acceptance criteria — "Global Search. Top results" (the AC ledger: AC-1…AC-9) | Confluence P2 1846673419 | the Top strip's presence, ordering, cap | 2026-09-07 |
| 2 | As-built FE — "Global Search" | Confluence FRON 1885732888 | which entities render, states, contract | 2026-09-07 |
| 3 | AI Search API V2 documentation | Confluence DS 2061074452 | the search service's own contract | 2026-09-07 |
| 4 | Ticket under test | EP-56133 | the reproduction and its expected result | 2026-09-07 |
```

**Finding the acceptance-criteria page:** `getJiraIssueRemoteIssueLinks`
on the story, then `getConfluencePage` on the Confluence link (in bug-fix
and retest mode, the page governing the *feature*, reached via the
parent story or the suite).

**Finding the as-built document** — it is rarely linked from the ticket,
which is why it kept being missed. In order:

1. The QA Service suite's `summary` often names it outright (EP-56133's
   suite cited "the as-built front-end documentation (Confluence FRON
   1885732888)" — the pipeline had the reference and never opened it).
2. The product brief's own page usually links it, or is linked *from* it.
3. `searchConfluenceUsingCql` on the feature name, restricted to the
   as-built spaces: `space in (FRON, DS) AND title ~ "<feature>"`.
4. The epic's ticket ledger — as-built pages list the tickets that built
   the feature, so the reverse lookup works.

If no as-built document exists, record that as a row with
`Id: NONE FOUND` and say so once in the run report. Absence is a real
finding about the feature's documentation; silence is not.

**One fetch per distinct source per run**, not per case or per finding —
in practice three to five fetches. Cache them in the register, **and
save each fetched body verbatim** to `r<N>/sources/<label>.md`, fenced
(§8). The register row says what the source is; the saved file is what
every `Clause:` of this pass is checked against.

## 3. The gate

> **No finding is stated as a defect without a quoted clause from a
> register entry.**

"Stated as a defect" covers every surface: a FAIL or FAIL CONFIRMED in a
stage report, a bug draft, a run-sheet row phrased as a fault, a line in
the human summary, and **anything said to the user in chat**. The chat is
not a lower standard than the report; on the run that produced this file,
chat was where the unsourced claims did their damage.

For each candidate defect, record two lines:

```
Source: <register row #> — <document>, <section> · AC-<n>
Clause: "<the sentence, quoted verbatim>"
```

**Verbatim means copied from the saved source file, not retyped from
memory.** Since 0.47.0 the quote is checked mechanically (§8). A
paraphrase inside quotation marks is a misquotation, whichever words it
changes.

The trailing `· AC-<n>` is the ledger id of the acceptance criterion the
clause belongs to (task-context SKILL.md → "The AC ledger"); it is what
lets a reader of a bug, a walk card or the human summary say *which*
criterion is failing without re-reading the page. Omit it only when the
clause comes from a document that is not the AC page (the as-built doc,
a design sub-task) — then the row number alone identifies the source.
The id is on the REQ (`source:` line) and the test-case group
(`Covers:`) the finding belongs to; copy it from there.

Then one of three outcomes:

- **Clause found, build contradicts it** → the defect stands. Normal
  FAIL / FAIL CONFIRMED handling.
- **Clause found in one source, contradicted by a higher-precedence one**
  → `SPEC-DEFECT`. Name both documents and say which the code
  implements. Never a FAIL, and never a Bug against a developer.
- **No clause in any source** → `OBSERVATION (no source checked)`.

## 4. `OBSERVATION (no source checked)`

A real thing seen, with no document saying it is wrong. It is honest
output and worth recording — three of the four findings in the run that
prompted this file were of exactly this kind, and two of them are
plausibly worth fixing.

Rules, all of them load-bearing:

- It **may not** appear in a list of defects, bugs, or failures.
- It **may not** be handed to `/knowledge-base` or `createJiraIssue`.
- It is phrased as a question, not a verdict: *"should X be Y? no source
  of record says either way"* — never *"X is broken"*.
- When reported to the user it carries its label. Presenting an
  unsourced observation next to verified failures in one numbered list
  gives it authority it has not earned, which is precisely the failure
  this section exists to prevent.
- It converts to a defect only by finding the clause, or to a product
  question by being raised with the docs-phase owner.

## 5. Precedent is not a source

On the same run, `EP-55923` ("Round tables results are found and
permitted but never render", COMPLETE) was cited as precedent for filing
the Groups finding. The reasoning failed: Round Tables **is** one of the
12 entities the as-built document lists, so that was a genuine defect;
Groups is not, so the precedent does not transfer.

A closed ticket shows how a similar-looking case was once ruled. It does
not tell you whether the clause covers yours. Check the register, then
cite the precedent as supporting context if it still applies.

## 6. What this does not change

- The pipeline still does not re-groom requirements in the code phase.
  Confirming that a sentence exists is not re-deriving it.
- Stages still do not go to the tracker for anything else. The register
  is a bounded, read-only exception, same as code-review's existing
  source-fidelity check.
- A missing source never blocks a run. It downgrades a claim.

## 7. The publication gate — the comment, not only the report

§3 binds every surface. This section exists because one surface keeps
failing it: **the step where a stage report is compressed into an
outgoing Jira comment.** The report can be perfectly labelled and the
comment still wrong, because compression drops labels.

> **Before an outgoing comment is shown for confirmation, every line
> presented as a defect carries its register row and its verbatim
> clause. A line with no clause is labelled
> `OBSERVATION (no source checked)` and phrased as a question, or cut.**

Applies to `qa-pipeline-code` step 6 (wave 1) and `qa-manual-results`
step 4 (the human summary), and to any other comment a stage posts.

Checks, in order, on the drafted comment:

1. **Line by line.** Take each line that a reader would understand as
   "this is broken". Name its register row and quote its clause. No
   clause → relabel or delete.
2. **An observation the report labelled correctly must not reappear as a
   defect.** Not as a bullet under a "not fixed" heading, not as a row in
   a table of failures, and **not as a column that implies one** — a
   column header such as "true matches" or "expected" asserts a
   requirement, so it needs a clause exactly as a sentence would.
3. **Name the owning ticket on the line** when the defect belongs
   elsewhere, so the reader knows what will fix it: *"`Dark` products 18
   vs 21 — EP-56739"*, not *"the counter is wrong"*.
4. **Sourced defects and unsourced observations are not neighbours.**
   Separate headings, and the observation's heading says it is a
   question.
5. **Read the comment as the assignee would.** If a line would send a
   developer looking for a bug that no document requires them to fix,
   it fails this gate.

**The real case (2026-09-07, EP-56197).** The DS contract states, in the
current text: *"Note `items` is the ranked set and can be longer than
`total` — `total` counts matches, while `items` also carries the semantic
tail marked with `item_weak`."* The web-testing report recorded the
readings under `OBSERVATION (no source checked)` and said in terms
*"not a new defect"*. The drafted Jira comment then rendered the same
readings as a table with a **"True matches"** column under the heading
**"Still broken — the number is wrong in both directions"** — an
unsourced defect claim, contradicted by the contract, one confirmation
away from a developer's ticket. The tester caught it by asking which
document required the rendered count to equal the match count. Nothing
did. One sourced row survived the check; four did not.

## 8. Saved source text and the quote check (0.47.0)

§3 required a verbatim clause. Until 0.47.0 nothing checked that the
words inside the quotation marks were on the page:
- the analyzer raised 🔴 on a FAIL with **no** `Clause:` line;
- a FAIL whose clause was a paraphrase passed every check.

A bug quoting "Exhibitors can add up to 10 favourites" against a page
that says "*Visitors* can add up to 10 favourite exhibitors" loses its
credibility at the first reply. The idea is borrowed from qa-service
(`lib/server/requirementSources.ts`): the service looks for each
recorded quote in the text it actually fetched and marks the quote
unverified when it is not there.

**Saved sources.** Every source fetched as a source of record is saved
**verbatim, as returned** (no tidying, no summarising) to one file per
source, fenced (`untrusted-content.md`):

| Folder | Written by | Files |
|---|---|---|
| `runs/<KEY>/docs/sources/` | `task-context` | `confluence-<pageId>.md` (the AC page), `jira-<KEY>-description.md`, `jira-<KEY>-comments.md`, `jira-<SUBKEY>-description.md` per sub-task it read |
| `runs/<KEY>/r<N>/sources/` | `qa-pipeline-code` step 0 | one file per register row, same naming (`confluence-<pageId>.md` for the brief and the as-built doc, `jira-<SUBKEY>-description.md` for the implementing sub-task) — **plus, always, the story's `jira-<STORY>-description.md` and `jira-<STORY>-comments.md`** (one `getJiraIssue` call), so the `JD-n` / `CM-n` ledger items are re-checked too, not only the AC page |

Write the body with the Write tool, then fence it:

```
python3 <plugin>/skills/qa-pipeline/scripts/source_tools.py fence \
  --label 'confluence:<id> "<title>" · fetched <date>' <raw> --out <file>
```

With no shell, write the fence lines by hand. The same file name
across folders is what lets §9 compare them.

**The check.**

```
python3 <plugin>/skills/qa-pipeline/scripts/source_tools.py quotes <KEY> [--round r<N>] [--file <draft>]
```

- It reads every `Clause: "…"` in the round's reports, or in the drafts
  named with `--file`.
- It looks for each clause in the saved sources, ignoring case,
  whitespace, curly quotes, dashes and markup.
- An ellipsis (`…`) splits a quote into parts; each part must be found,
  in order.

It prints one of three results:

| Result | Meaning | What to do |
|---|---|---|
| `OK` | the words are in a saved source | — |
| `UNVERIFIED` | not found | Re-copy the clause from the saved file. If the page genuinely does not say it, the finding has no clause: `OBSERVATION (no source checked)` (§4). Never publish it as a quote. |
| `TOO SHORT` | a quote (or an ellipsis part) of fewer than 4 words — "the organiser" verifies against almost any page | Quote the whole sentence |

**Where it runs:**
- the step-6 count gate of `qa-pipeline-code` (the round's reports);
- the bug drafts before the step-7 offer (`--file`);
- the stage-10 human summary and bug drafts before the write-back
  preview (`--file`);
- the analyzer's §7.

A published line with an `UNVERIFIED` clause is a 🔴.

**No shell** (a Cowork session without one): do the same comparison by
reading. Open the saved source, find each clause, and write `quote check
by hand — N clauses` in the report. The rule holds; only the instrument
changes.

**Pre-0.47 rounds** have no `sources/` folder. The check falls back to
the context file's verbatim AC ledger and says how many files it read.
Nothing to read at all means exit 2, and the check is reported as not
run, not passed.

## 9. Drift — the source changed since the docs phase (0.47.0)

The retest already diffs the **suite** against the docs-phase file
(`../../qa-pipeline-code/references/run-modes.md`). That catches a case a PM
added in QA Service. It cannot catch a change to the **page**:
- a PM edits the AC page from "up to 10" to "up to 20";
- nobody touches the suite;
- suite and file still agree, and the pass tests the old rule.

The idea is borrowed from qa-service (`lib/server/sourceWatch.ts`): a
fingerprint of the fetched text, never of its `updated` timestamp.
Jira's timestamp moves on every comment, including our own.

```
python3 <plugin>/skills/qa-pipeline/scripts/source_tools.py drift <KEY> [--round r<N>]
```

It compares each `r<N>/sources/` file with the docs-phase file of the
same name, then re-finds each `AC-n` / `SB-n` / `JD-n` / `CM-n` ledger
item's verbatim text in the re-fetched sources. Its results:
- `unchanged` / `CHANGED` / `NEW SOURCE` / `NOT RE-FETCHED` per source
  file;
- **`STALE AC-n`**: the criterion's wording is gone from the re-fetched
  page. Every REQ whose `source:` names it, and every case covering it,
  may now test a rule the page no longer states;
- `NEW MATERIAL`: up to 8 long lines (60 or more characters) the
  re-fetched page has and the old one did not. This is often a new
  criterion that no REQ carries yet;
- `not re-checked`: a ledger item whose source file was not re-fetched
  this pass. It is said, not failed.
- exit 2, `NOT CHECKED`: no docs-phase file was re-fetched under the
  same name. Check the file names; this is never a clean result. With
  no shell, compare the saved pages by reading and say so, as for
  quotes.
- `not anchored`: a ledger item whose text was never found verbatim in
  the docs-phase sources (stage 1 paraphrased it). Drift cannot watch
  it. Say so once.

**What happens next** (`qa-pipeline-code` step 0):
- A `STALE` or `NEW MATERIAL` line goes into `<KEY>-sources.md` under
  `## Changed since the docs phase`, and into the chat line that shows
  the register.
- **Retest:** each stale criterion's cases are listed in
  `<KEY>-retest-scope.md` with an explicit in/out decision, in the same
  confirmation as the rest of the scope. New material is a
  `[Input]` ledger row (`open-items-ledger.md`) until someone decides
  whether it is a requirement.
- **First code-phase run:** the same lines are shown before stage 5.
  Stages 6–8 treat the **re-fetched** text as governing. A case whose
  expected result the new text contradicts is `SPEC-DEFECT`, never a
  FAIL against the build.

**Limits, said once.** The check sees only what was saved: the AC page,
the description, the comments and the sub-task descriptions. It does not
see an attachment or a page nobody linked. A reworded criterion reads
`STALE` even when its meaning did not change, so a human decides; the
script only makes sure someone looks.
