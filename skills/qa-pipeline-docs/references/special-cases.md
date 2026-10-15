# Docs phase — two special cases

Read by `qa-pipeline-docs` when one applies. Neither happens on every
run.

## 1. After a refinement run — reuse, don't redo

When `runs/<ISSUEKEY>/docs/` already holds `qa-refinement` output
(`-open-questions.md`, `-answers.md`, `-recon.md`, `-sizing.md`), say so
in the first line ("Refinement run found: N questions, M answered") and
carry each file forward:

- **Stages 1–2 still re-run.** The ticket changed, which is the point
  of asking. task-context re-reads the description and comments, where
  the answers were written. Grooming also reads `-answers.md` as the
  owner's answers (its Inputs) and re-applies every settled one as
  `resolved by the owner (<date>)`, including the inferred ones and
  the "AC still says otherwise" notes that no Jira field carries.
- **Recon is reused, not repeated.** Keep `-recon.md`. Run recon only
  for BEHAVIOUR items it does not cover, and append them as the next
  `B<n>` sections. Never overwrite the file
  (`../../qa-pipeline/references/recon.md` → "Reuse").
- **Questions: only what is new or still open.** Before step 2 drafts
  anything, read `-open-questions.md` and `-answers.md`:
  - a question the owner answered is settled and never asked again;
  - one still waiting (not clear, partial, or in a posted follow-up
    with no answer) is listed in the publish preview as "still open
    since <date>", not re-posted;
  - only items grooming raises for the first time go into a new
    comment, in the same shape;
  - the file itself is never overwritten: new questions go under a
    dated `## Added <date>` section and the `Comment:` line stays — the
    answers pass finds the original comment by it.
- **Publish adopts the QA sub-task** named on `-sizing.md`'s
  `QA sub-task:` line (§2).

## 2. Adopt a QA sub-task a human already created

When the story has a QA sub-task WITHOUT the pipeline label —
typically created at estimation, before the pipeline ran (EP-57799 on
EP-56227) — creating a second one splits the tracker. Find candidates
with `parent = <KEY>` and a summary starting "QA"; `qa-refinement`
records the one it saw
on the `QA sub-task:` line of `<KEY>-sizing.md`. Offer in the SAME
publish preview: "adopt <KEY-X> instead of creating a new sub-task".

On yes:
- add the label;
- keep the summary, the assignee and the human's description;
- append the pipeline description below it, under a `QA pipeline`
  heading. Never replace what a person wrote.

On no, create a new one as usual and leave the human's sub-task
untouched. The supersede rule does not apply to it, because it was
never a pipeline sub-task.
