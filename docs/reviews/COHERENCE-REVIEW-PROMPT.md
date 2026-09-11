# Coherence & currency review prompt for the `ep-qa-pipeline` plugin

Paste the block below to a fresh agent (Opus or Fable, high effort,
extended thinking on, web search available) with this repo mounted.
Fill the `<...>` placeholders.

This is the third review prompt in the repo and it asks a different
question from the other two. `PIPELINE-REVIEW-PROMPT.md` asks *where
would the pipeline let a wrong verdict through*. `ORCHESTRATOR-DESIGN-
REVIEW-PROMPT.md` asks *is the orchestrator shaped right*. This one
asks: **after a burst of releases, does the plugin still describe one
system, what in it should be deleted, and is that system built the
way this kind of thing is built today — including what the best
public QA skills do that this one does not?** Run it after any day
with three or more releases, after any concept is retired, and roughly
once a month regardless.

---

```
Review the `ep-qa-pipeline` Claude Code plugin at <REPO PATH> for
internal coherence, streamlining, and currency. Review only — do not
edit any file under skills/, scripts/, hooks/, evals/ or the manifests.
Your one write is the report described at the end.

You have no stake in this plugin. Treat it as an unknown author's
work. The author has just shipped <N> releases in <PERIOD> (read the
CHANGELOG headings to confirm this — do not take my count on trust)
and is worried about exactly one thing: that the pieces no longer
agree with each other, and that the fast pace has left the design
behind what the surrounding tooling and the QA discipline now offer.
Tell them what is actually inconsistent or dated, not what is
reassuring. A compliment that does not change a decision is noise.

## Ground rules

- Verify every claim against a file and quote the line. "Probably
  stale" without a path and a line is not a finding.
- `python3 scripts/verify_plugin.py` exists and already checks:
  manifest versions, description length, LF/newline/NUL, skill↔README↔
  evals wiring, reference-file existence, status-vocabulary↔script
  parity, the count-gate self-test, and staged run artefacts. Run it
  once, record the result, and then DO NOT spend your review
  re-deriving those checks by hand. Your job is everything the script
  cannot see: meaning, not mechanics.
- `PIPELINE-REVIEW-2026-09-07.md` and `SKILL-BEST-PRACTICES-AUDIT-
  2026-07-30.md` are prior reviews. For every proposal in them, report
  its status today (implemented / rejected in CHANGELOG / silently
  dropped) in one table — but do not re-argue them. A proposal that is
  neither implemented nor rejected in the CHANGELOG is a finding under
  the plugin's own MAINTAINERS rule.
- Read in this order, all of it: CLAUDE.md → MAINTAINERS.md →
  README.md → CHANGELOG.md (every entry from the earliest release of
  the burst to HEAD, then skim the rest for the origin of each
  retired concept) → .claude-plugin/*.json → hooks/hooks.json →
  evals/triggering.md → every skills/*/SKILL.md → every file under
  skills/*/references/ and skills/*/scripts/ → every
  skills/*/setup-guide.md → scripts/. Then the newest complete run
  under runs/<STORY KEY>/ (docs/ plus the newest r<N>/, including its
  run report and open-items ledger) so you can compare what the
  skills say happens with what a run actually produced.

## Part 1 — One system or several? (coherence after the burst)

**1a. Build the retired-concept census first.** From the CHANGELOG
entries of the burst, list every concept, file name, path, term,
status token, backend, comment type or mechanism that was retired,
renamed or demoted to "legacy". Then grep the ENTIRE tracked tree
(skills, references, scripts, README, MAINTAINERS, CLAUDE.md, evals,
setup guides, script docstrings, hooks) for each one. Every surviving
mention is one of: (i) correctly marked legacy/read-only, (ii) stale
and misleading, (iii) contradicting a current rule. Report (ii) and
(iii) as a table: term · file:line · what it should say now. This
table is the spine of the review; do it exhaustively, not by sample.

**1b. Cross-reference integrity beyond file existence.** The script
proves referenced files exist. You check that the *reference is
right*: does the named section still exist under that heading, does
the step number still match the step, does the rule quoted from
another skill still read that way there, does the count of anything
("13 skills", "eight checks", "eleven skills share this boilerplate",
"stage 10a/10b") match what is actually in the tree? Check the shared
boilerplate blocks that appear in many skills (input resolution, data
locations, status vocabulary references) for divergence between
copies — the single source they point to may have moved on while
some copies did not.

**1c. Contract seams.** For every producer → consumer pair
(task-context→grooming→checklist→test-cases→publish→step 0→
pr-summary→code-review→api-testing→web-testing→analyzer→runsheet→
walk→results, plus the dispatcher and the ledger) take the output
template of the producer and the input section of the consumer and
check field by field: same file name, same path convention, same
header fields, same id shapes, same status tokens, same folder round
semantics. A field one side writes and the other side never reads —
or reads and the other never writes — is a finding. Do the same for
each skill's description versus its body: the description is what
discovery sees, so a description that promises or excludes something
the body does not is a routing defect.

**1d. Orphans and zombies.** Mechanisms kept alive by instruction
rather than use: a reminder about a comment nobody posts any more, a
script only a retired flow called, a reference file no SKILL.md names,
a setup-guide describing a setup the skill no longer performs, an
eval line testing a trigger phrase that was removed from the
description, a `.gitignore` pattern for a file shape that can no
longer be produced. Also the reverse: a new mechanism (e.g. a new
folder layout, a new card kind, a new status, a new run-API call)
that one stage produces and a downstream stage, the analyzer, the
dispatcher, the README or the evals never learned about.

**1e. Rule collisions.** Two rules that a single run cannot obey at
once. Prefer pairs where one is old and one is from the burst.
Quote both.

## Part 2 — What to delete, what is dead, what makes things worse

**2a. The deletion ledger.** Give a verdict for EVERY tracked file
outside runs/ and .git/, and for every named mechanism inside a
SKILL.md (a step, a pause, a gate, a check, a template section, a
status token, a hook, a script, an eval section): KEEP · MERGE INTO
<file> · DEMOTE TO LEGACY · DELETE. A KEEP needs one line of proof
that something reads it (a skill names it, a script imports it, a
run artefact shows it fired). No proof, no KEEP. For every DELETE or
MERGE, state what is lost and whether an incident-born rule (find it
in the CHANGELOG) depends on it; if one does, the verdict is KEEP and
the fix is to make the rule enforced somewhere cheaper. Candidates to
look at hardest: `setup-guide.md` files (the agent never loads them —
are they maintained, and for whom?), `.bak` and `.prev` files,
scripts kept as "legacy readers", template sections nobody fills,
`.gitignore` patterns for shapes that can no longer be produced, eval
lines whose trigger phrase no longer exists in any description,
reference files named by no SKILL.md, and any second copy of a rule.

**2b. Mechanisms that make things worse.** Use the run artefacts as
evidence, not the skills' own claims. For each gate, pause, check,
analyzer flag and required field, look at the last several runs and
answer: did it ever change an outcome? A pause that was answered
"yes" in every run is a cost with no decision behind it. An analyzer
flag that appears in every run report and is acted on in none is
noise that trains the reader to skip the report. A required field
that is always filled with the same placeholder is theatre. A rule
that produced only false alarms (check the ledgers and CHANGELOG for
"false positive", "retracted", "over-flagged") is worse than absent.
A verbosity requirement that pushed a real finding below the fold is
harm. Report each with the runs it was checked against and one of:
REMOVE · DEMOTE TO WARN · KEEP BUT NARROW (say how) · KEEP (it fired
and mattered — cite the run). Be as willing to say "this rule earned
its place" as "this rule is dead weight"; both need the evidence.

**2c. Streamlining.** Where does the plugin pay a context-window or
maintenance cost for no behavioural gain? Look for: rationale ("Real
case: …", "On one run …") in always-loaded SKILL.md bodies rather than
in references or the CHANGELOG; the same paragraph maintained in N
places; a SKILL.md body over ~450 lines; a reference file that could
be a table; a step that exists only to compensate for a defect fixed
elsewhere in the burst; two files that now describe the same artefact
from two angles (e.g. a rendering spec and a plan spec) without saying
which is authoritative. For each, propose the consolidation and state
plainly whether it changes behaviour (the bar: zero behaviour change,
or the change is named). Estimate the tokens saved per run for the
top five — the orchestrator's body is loaded on every code-phase run,
so a 100-line cut there is worth more than a 300-line cut in a
reference read once.

## Part 3 — Currency (is this how it is built today?)

Use web search and the tooling in your session. Today's date is in
your environment — reason from it, not from your training data.
Separate what you find into: ADOPT NOW (concrete gain, low risk) ·
CONSIDER (worth a spike, say what the spike is) · REJECT (looks
modern, would weaken an incident-born rule — name the rule and the
CHANGELOG entry). Cover at least:

- **Claude Code plugin & skill conventions.** Check docs.claude.com
  for the current skill frontmatter fields, hooks schema and event
  names, plugin manifest fields, eval tooling (`claude plugin eval`
  or its successor), sub-agent / forked-context options, and MCP
  tool naming. Is this plugin using what exists now, or hand-rolling
  something the platform provides (e.g. hand-walked triggering evals
  where a runnable eval suite exists; a Stop hook where a more
  specific event fits; prose gates where a hook could enforce)?
- **The QA Service connector.** Compare the tools the MCP server
  exposes in your session against the ones the skills actually call.
  Name every relevant tool the pipeline does not use and what
  hand-rolled mechanism it duplicates or what gap it would close.
- **Browser and API execution.** Current Playwright MCP capabilities
  (evidence capture, tracing, network interception, auth state,
  sandbox paths) versus what `web-testing` and `playwright-executor.md`
  assume; the same for the API stage's harness.
- **QA methodology.** Against current mainstream practice for
  risk-based testing, test design techniques, regression scoping by
  blast radius, flaky-result handling, evidence standards, defect
  triage, and — specifically — known failure modes of LLM-generated
  test artefacts (invented expected results, over-confident absence
  checks, requirement paraphrase drift, verdict inflation). For each
  practice: does the pipeline already encode it (cite where), encode
  it partially, or lack it? Do not pad this with textbook names; a
  practice earns a line only if you can say what would change in a
  named file.

## Part 4 — Gaps the fast pace left

Answer these directly: What did a release in the burst change that
no later release, no eval, no analyzer check and no run report has
yet exercised — i.e. what is shipped but unproven? Which open-items
ledger rows or run-report 🔴/🟡 [Pipeline] items from the newest runs
have no CHANGELOG disposition? What does `verify_plugin.py` still not
check that this review had to do by hand and could be mechanised in
under 40 lines (name the check and the file it would read)?

## Part 5 — Field survey: what the best public QA skills do

Search the web and GitHub for the most-used public Claude Code skills,
plugins and agent workflows for QA and testing. Cover at least:
Anthropic's own skills repository and any official plugin
marketplace; the curated "awesome" lists for Claude Code skills and
plugins; the top-starred repositories for "claude skill" / "SKILL.md"
plus testing, QA, test cases, test plan, exploratory testing, bug
report, regression, Playwright, browser testing, API testing,
requirements; and QA-agent projects built on Playwright MCP or
similar. Aim for 10–15 candidates. For each, record: URL · stars or
adoption signal · licence · one line on what it is. Then READ the
SKILL.md and references of the ten most relevant — the README is
marketing, the SKILL.md is the mechanism.

For each candidate, extract **mechanisms**, not prose: a test-design
technique with a procedure, a verdict or evidence rule, a
report/bug-report structure, a triage or flaky-handling protocol, a
traceability scheme, a self-check the skill runs on its own output,
a way of scoping regression, a fixture or test-data pattern, a
progressive-disclosure or context-budget trick, a hook or eval
pattern, a way of asking the human for the one thing only a human
knows. Then judge each mechanism against THIS plugin:

- ALREADY HERE — cite where the plugin does it (and whether the
  public version does it better; if so, how).
- ADOPT — say exactly which skill and section it lands in, what it
  replaces or adds, and why it does not weaken an incident-born rule.
- ADAPT — the idea fits but the mechanics do not (different tool,
  different record, different tester); say what the adapted form is.
- REJECT — say what it would break, naming the rule and its CHANGELOG
  entry.

Rules for this part: quote the source and its licence before
proposing to lift anything verbatim; a mechanism that only makes
sense for a solo developer's unit tests is not a fit for a
requirements-driven, human-in-the-loop, system-of-record pipeline —
say so rather than forcing it; popularity is a reason to read, not a
reason to adopt. Also record the inverse: the two or three things
this plugin does that none of the surveyed skills do, because that
is what the author should protect during any adoption. If a surveyed
skill is a direct competitor in shape (ticket → cases → execution →
record), compare the whole pipeline side by side in a short table.

## Output

Write `<REPO PATH>/COHERENCE-REVIEW-<YYYY-MM-DD>.md` with these
sections in this order: Scope actually read (be exact — a docs-phase
skill you skimmed is "skimmed") · Verdict in five lines · Retired-
concept census (the 1a table) · Findings ranked by consequence, each
with file:line evidence and a fix concrete enough to implement
(named file, the change) · Deletion ledger (the 2a table, every file
and mechanism with its verdict) · Mechanisms that make things worse
(2b, with the runs checked) · Streamlining proposals with the
behaviour-change bar stated and tokens-per-run estimated · Currency
table (ADOPT / CONSIDER / REJECT) · Field survey — candidate table,
then mechanisms as ALREADY HERE / ADOPT / ADAPT / REJECT, then what
this plugin does that none of them do · Prior-review disposition
table · What is shipped but unproven · Proposed `verify_plugin.py`
checks · What the plugin demonstrably gets right that most plugins do
not (short, load-bearing only) · Surprises — where the documentation
and the tree came apart in a way you did not expect.

Rank by consequence, not tidiness: a stale sentence that would route
a tester to a retired flow outranks twenty inconsistent headings.
Never paraphrase a rule you are calling stale — quote it.

## Reply

At most 25 lines: the report path, the verify_plugin.py result, the
census count (mentions found / stale / contradicting), counts by
severity, the top five findings one line each with their fix, the
DELETE and REMOVE verdicts as a bare list of names, the top three
ADOPT items from the currency pass and the top three from the field
survey (each with its source), the prior-review proposals still
undispositioned, and your surprises. Do not paste the document.
```
