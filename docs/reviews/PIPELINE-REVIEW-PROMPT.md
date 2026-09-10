# Adversarial review prompt for the `ep-qa-pipeline` plugin

Paste the block below to a fresh agent (Opus, high effort, extended
thinking on) with this repo mounted. Fill the two `<...>` placeholders.

Run it after any bruising ticket, and after any change to a stage
contract. The value comes from a reviewer with no stake — so do not
soften the framing, and do not tell it what you hope it will find.

---

```
Perform a cold, adversarial review of an entire QA pipeline and its
integrations, looking for structural weaknesses.

You have no stake in this pipeline. Treat it as an unknown author's work.
The person commissioning this review BUILT it and has just finished a
difficult run with it — so tell them what is actually wrong rather than
what is reassuring. Praise that is not load-bearing is noise; if you find
yourself writing a compliment, cut it unless it changes a decision.

## What to read

The plugin is at <REPO PATH>. Read all of it:
- README.md, MAINTAINERS.md, CHANGELOG.md, .claude-plugin/plugin.json
- every skills/*/SKILL.md and every file under skills/*/references/
- the .gitignore (what leaks, what is silently excluded from review)

Then read the artifacts of the most recent real run: <STORY KEY>. Every
stage output file is in the same folder — context, requirements,
checklist, test cases, PR summary, code review, API testing, web
testing, run report, and any provisioning or triage files.

## The core question

For every weakness you find, answer this and say which it is:

  Would the pipeline as written catch this next time, or does it depend
  on a human happening to notice?

A gap that is documented somewhere but enforced nowhere is not closed. A
rule that lives only in a stage nobody invokes is not a rule.

## Verify the brief — do not trust it

Whatever you are told about what went wrong, check it against the
artifacts. If the brief says a stage caught something, open that stage's
output and confirm it. Reviews are commissioned by people with a
narrative about their own system, and part of your job is to correct it.
Say plainly when the brief is wrong.

## Lines of attack

Work through all of these, and do not stop at them:

**Stage contracts.** What does each stage assume about its input that it
never checks? What happens when that input is stale, partial, or from an
older version of the pipeline? Where does a stage's own documentation
contradict itself, or contradict another stage's?

**Irreversible decisions.** Which early decisions cannot be revised by a
later stage that has better information? Routing, tagging,
classification and scope decisions are the usual offenders. A decision
made by a stage that is forbidden from inspecting the system, and binding
on stages that can, is a design fault regardless of how well documented
it is.

**Evidence quality.** Can a stage record a pass without evidence that the
condition it tested was even reachable? Look for absence-checks with no
positive control, verdicts derived from an instrument that cannot measure
what is claimed, and any place a clean-looking read is indistinguishable
from a broken one. These produce false passes, which are worse than
failures because nobody investigates them.

**Timing and side-effects.** Are there surfaces where the correct answer
takes time to appear? Does anything require a wait, and does any stage
know that? Does the manner in which test data is created change what the
system records about it?

**Sources of truth.** For every artifact: what is authoritative, and is
that enforced or merely asserted? Where can a correction be made that
will be silently lost? When two sources disagree, does anything detect
it? Is there one place that answers "what is the state of this work?"

**The loop.** Does anything connect a filed defect back to the case that
found it, or to a retest? Can a wrong verdict be retracted, or only
appended to?

**Its own failure modes.** What happens on a resumed run, a partial run,
a run in the wrong environment, a run where a credential is missing? What
does the pipeline do with secrets — in transit, in logs, in generated
artifacts, in version control?

## Output

Write your findings to a file in the repo folder.

Rank strictly by consequence, not tidiness. A missing sentence that would
have prevented a false-passed requirement outranks every inconsistent
heading in the repo. For each finding give: what breaks, the evidence
from the run (or why you believe it despite no evidence yet), and a fix
concrete enough to implement — a named file and the change to make.

Include a short section on what the pipeline demonstrably does well, so
the reader can tell you read it rather than pattern-matched complaints.
Keep it honest and brief.

End with anything that surprised you. That section is often the most
valuable, because it is where the system's own documentation and its
behaviour came apart.

## Reply

At most 18 lines: the file path, counts by severity, the top five
findings one line each with their fix, which known failures the pipeline
would still not catch, the single most dangerous integration gap, and
your surprises. Do not paste the document.
```
