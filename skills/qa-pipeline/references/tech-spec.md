# The tech spec — finding it, ledgering it, grooming it

Shared by `task-context` (stage 1, §1–§3) and `requirements-grooming`
(stage 2, §4). Applies only when the ticket has a tech spec; with none,
both stages run as if this file did not exist.

Developers attach a tech spec to the story — a Markdown file
(EP-55889: `EP-58436-tech-spec.md`, written on the spec sub-task
EP-58436): data mapping, limits, scope, what is out of scope, the dev
tests they plan, and their own AC trace. It is the one document that
says what the build will do beyond the acceptance criteria, and on
EP-55889 three of its rules reached no case (the translation-map
fallback, the empty map, "the Custom meetings report does not change").
Its status is **as-designed documentation**: it says what the developer
intends to build, not what product asked for (`sources-of-record.md` §1).

## 1. Find it (task-context)

`getJiraIssue {fields: ["attachment"]}` on the story and on each
sub-task whose summary names a spec ("Spec", "Tech spec", "Technical
design"). A tech spec is an `.md` / `.markdown` attachment whose name
contains `tech-spec` / `tech_spec` / `techspec` / `spec`, or whose first
heading starts with "Tech Spec". Several → take each; say which is
newest. None → write `Tech spec: none attached` and change nothing else.

## 2. Fetch it (task-context)

No upload needed. The Atlassian connector's `downloadJiraIssueAttachment`
(run with `executeRead`) returns a short-lived, single-file download
command. Run it once, saving to `runs/<KEY>/docs/sources/<file>`. **The
link carries a token: never print it, never put it in a file; report
the saved path only.** Fallback when the operation is unavailable: ask
for the upload, as for any attachment.

## 3. Write it into the context (task-context)

Under `## Tech spec (as-designed — <file>, <date>)` in the context file:
the `TS-n` items, then the spec's Tests table and AC-trace table
verbatim, as they are.

A `TS-n` item is each statement a test could check from outside — a
data mapping, a limit, a default, an empty / null rule, an in-scope or
out-of-scope surface, an effect on a consumer:
`TS-1 (Tech spec §2, <file>): <the statement, verbatim>`.

- Not a TS item: implementation internals no test can see (a helper's
  name, a file, "no migration"), and the spec's own Tests table and
  AC-trace table (copied verbatim, not itemised).
- A statement the AC already makes gets no TS bullet; one that adds to
  it, narrows it or contradicts it does.
- TS items are mapped like SB items and are not counted on the
  page/captured line.

## 4. Groom the TS items (requirements-grooming)

Every `TS-n` appears on at least one `source:` line, and the coverage
line gains ` · TS <n>/<N>`. For each one:

- **It restates an AC / SB rule more precisely** (a limit, a default,
  the field a column reads) → add the `TS-n` to that REQ's `source:` and
  fold the precise value into the REQ text, marked `(tech spec)`.
- **It adds observable behaviour no AC states** (the 32,767-character
  cut, a translation-map fallback, an empty-map rule) → a new REQ, kind
  `rule` / `fr`, with ` [as-designed]` after the risk marker, so a
  reader knows product never asked for it — it is what the developer
  built.
- **It puts a surface out of scope** ("the Custom meetings report is
  unchanged") → a REQ that the named surface does NOT change, so a
  regression case guards it.
- **It contradicts an AC / SB rule** → the REQ keeps the spec-of-record
  version, and grooming raises a Contradiction finding, SPEC class,
  quoting both: the spec of record wins until the owner says otherwise
  (`sources-of-record.md` §1).
- **An AC item the spec's own AC-trace table does not mention** → a
  finding "AC-n not addressed by the tech spec", BEHAVIOUR class: recon
  or the developer can say whether it was simply left out of the table.
- The spec's **Tests table** (planned developer tests) is not a source of
  requirements; carry it to the Notes so stage 4 can name those tests on
  the `Code-level:` line and registration can find them later.
