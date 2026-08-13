# Task: implement the agreed changes to the ep-qa-pipeline plugin

You are editing a Claude Code plugin that runs ExpoPlatform's QA pipeline. The
changes below were agreed by the plugin owner (Roman) after a retrospective on
the EP-47675 run. Your job is to apply them faithfully, not to redesign them.

## Repo

```
C:\media-files\Coding\qa-pipeline-skill\
```

The plugin's skills live under `skills/<skill-name>/SKILL.md` with supporting
files under `skills/<skill-name>/references/`.

**Do not edit anything under `~/.claude/plugins/synced/`.** That is a read-only
synced cache. The repo above is the source of truth. After your edits the plugin
must be re-synced or reinstalled before a session picks them up — mention that in
your final report, do not attempt it yourself.

## Read these first, in this order

1. `ep-qa-pipeline-proposed-edits.md` (repo root) — the specification. Contains
   the exact blocks to insert, anchored to section headings.
2. `ep-qa-pipeline-retrospective-EP-47675.md` (repo root) — the evidence behind
   them. Read it so you understand *why* each change exists; you will need that
   judgement where the spec is ambiguous.
3. `MAINTAINERS.md` (repo root) — house conventions. Follow them over your own
   taste.

The proposed-edits file is the contract. Where it gives literal text, use that
text. Where it describes intent, match the surrounding file's existing voice —
these skills are written in a particular terse, imperative register and an edit
that reads differently is a bad edit.

## Scope: tier 1 only, unless told otherwise

Apply **D1, D3, D4, F1 and C5**. Leave A (walk sheet), B (progress wiring), F3,
F4 and the remaining C items alone — they are a separate piece of work.

### Task 1 — D1: rename the verdict vocabulary

`FAIL CONFIRMED` → `CANDIDATE DEFECT`, and introduce `DEFECT` as the only
filable status. `FAIL REJECTED` → `NOT A DEFECT`. Full definitions in the
proposed-edits file, section D1.

**This is the dangerous one. Read this whole subsection before you start.**

`FAIL CONFIRMED` occurs **55 times across 17 files**. Enumerate them yourself
before changing anything:

```
grep -rn "FAIL CONFIRMED\|FAIL REJECTED" . --include=*.md --include=*.py --include=*.json
```

Known consumers that are NOT prose and will break if you treat this as a
find-and-replace:

- **`skills/qa-run-analyzer/scripts/reconcile_counts.py`** — has the string in
  (a) a `STATUSES` tuple whose ordering matters (the comment says *"Longest
  alternatives first so FAIL CONFIRMED never half-matches as FAIL"* — the same
  hazard applies to `CANDIDATE DEFECT` vs `DEFECT`, so `CANDIDATE DEFECT` must
  come first), (b) a self-test markdown fixture, and (c) a `SELFTEST_EXPECT`
  counts dict. All three must change together. **Run the script's self-test
  after editing and paste the result into your report.**
- `skills/*/references/output-template.md` — report templates. Changing these
  changes the shape of published artifacts.
- `skills/qa-pipeline-docs/references/qa-service-publish.md` — write-back
  convention for the QA Service suite.

**Do not rewrite history.** `CHANGELOG.md`, `ORCHESTRATOR-DESIGN-REVIEW-*.md`
and `PIPELINE-REVIEW-*.md` are historical records that describe past runs. Leave
their occurrences alone. Only forward-looking instruction files change.

Backward compatibility: existing artifacts in the repo (`EP-*-web-testing.md`
etc.) contain the old strings. `reconcile_counts.py` should therefore accept
BOTH vocabularies on read and emit only the new one. Add the old strings as
deprecated aliases rather than deleting them, with a comment saying why.

### Task 2 — D3: replace `qa-pipeline-code/SKILL.md` step 7

Replace the whole of numbered step 7 (`**Offer to file the confirmed bugs**`)
with the block given in the proposed-edits file, section D3. The essential
behaviour change: candidates are walked **one at a time** with the human, never
presented as a batch, and nothing reaches `createJiraIssue` without a human
having reproduced it.

Check whether step 8 and the `## Final response` section reference step 7's
wording, and update them for consistency if so.

### Task 3 — D2: new reference file

Create `skills/qa-manual-runsheet/references/candidate-defect-format.md` from
the template in the proposed-edits file, section D2. Three fields are mandatory
on every candidate and the file must say so: **Confidence**, **What would kill
this**, and **Reproduce it with me**.

### Task 4 — D4: one-line additions

Add the "this stage emits CANDIDATE DEFECT, never DEFECT" paragraph to
`skills/web-testing/SKILL.md` and `skills/api-testing/SKILL.md`, under their
classification sections. Exact text in the proposed-edits file, section D4.

### Task 5 — F1: second observation before any failure verdict

Add the rule to `skills/web-testing/SKILL.md` under its hard rules. Text in the
retrospective, finding F1. Note the interaction with Task 1: the rule now reads
"before recording CANDIDATE DEFECT", not "before recording FAIL CONFIRMED".

### Task 6 — C5: confidence field

Add a `Confidence` field to the verdict vocabulary in
`skills/qa-run-analyzer/references/status-vocabulary.md`, values
`observed once` / `reproduced 2+ sessions` / `code-read only`, and require every
stage that emits a failure verdict to set it. Then make it load-bearing:
**a verdict at `observed once` cannot be published as `DEFECT`.** That sentence
is the point of the whole change — without it the field is decoration.

## Constraints

- Do not invent new requirements. If the spec is silent on something, do the
  smallest thing consistent with the surrounding file and flag it in your report.
- Do not reformat or restructure files you are not otherwise changing.
- Do not change any skill's YAML frontmatter (`name`, `description`) unless a
  task above explicitly requires it — descriptions drive skill selection and a
  careless edit changes when the skill fires.
- Keep each file's existing heading structure. The spec anchors to headings.
- One logical change per commit if the repo uses granular commits; check
  `git log --oneline -20` for the house style first.

## Verify before you report

1. `grep -rn "FAIL CONFIRMED\|FAIL REJECTED" skills/` returns only deliberate
   backward-compatibility aliases. Anything else is a miss.
2. `reconcile_counts.py` self-test passes. Paste the output.
3. Every file you edited still parses as valid markdown, and any JSON/Python you
   touched still loads.
4. Re-read each edited section cold and ask: would someone who has not read the
   spec understand this rule and be able to follow it? A rule that needs the
   spec to interpret it has failed.
5. Add a `CHANGELOG.md` entry describing what changed and why, in the file's
   existing format. One paragraph, referencing EP-47675 as the motivating run.

## Report back

- Files changed, one line each, with what changed.
- The `reconcile_counts.py` self-test output.
- Anything in the spec you found ambiguous, and what you chose.
- Anything you think is wrong with the spec. You are not obliged to agree with
  it — say so if you disagree, but implement what is written and flag the
  disagreement separately rather than quietly deviating.
- The reminder that the plugin needs re-syncing before the changes take effect.

## Background, in one paragraph

On the EP-47675 run the pipeline's web-testing stage published 37 verdicts and
17 were wrong, 16 of them false alarms — failures that were actually the product
working correctly. They were caught only because a human re-checked. The
changes above exist to make that failure structurally harder: a single automated
observation can no longer be labelled "confirmed", cannot be filed as a bug, and
must be reproduced with a human present before it reaches Jira. If an edit you
are making seems to weaken that gate, you have misread the spec.
