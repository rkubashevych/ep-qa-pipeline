# QA Service publish — suite creation from pipeline output

How `qa-pipeline-docs` step 6 publishes the groomed requirements and
test cases into **QA Service** (the team's test-suite system of record)
via its MCP connector, alongside the Jira QA sub-task. Edit this file —
not the orchestrator's SKILL.md — when adopting for another product or
QA Service instance.

## Preconditions

- The QA Service MCP connector must be enabled in the session. Detect it
  by the presence of its tools (`list_products`, `create_suite`,
  `create_requirement`, `create_test_case`, `edit_test_case`, …).
- **If the connector is absent, skip this publish silently-but-visibly:**
  do everything else as normal and add one line to the final response —
  "QA Service publish skipped (connector not enabled)". Never block the
  Jira publish on it.
- QA Service is **production data shared with the whole team**; there
  are no delete tools. Publish only after the user's explicit yes at the
  step-6 pause (one confirmation covers Jira + QA Service).

## Config

| Setting | Value |
|---|---|
| Product id | `expoplatform` |
| Suite path convention | `<role>/<feature-area>/<ticket-feature-slug>` — role is one of `admin`, `organizer`, `exhibitor`, `visitor`, `common` |
| Suite title | the story summary, cleaned (no ticket key, no "[QA-PIPELINE]") |
| Suite prefix | short UPPERCASE mnemonic of the feature (2–8 chars, e.g. `ZTB`, `PSRCH`). Propose one; the user can override at the pause. |
| Folder | reuse the `folderId` of an existing sibling suite with the same role/feature-area (find it via `list_suites`); omit if none fits |
| Web UI base URL | `https://qa-service.expoplatform.com` — suite detail page: `<base>/<productId>/test-suites/<suite path>` (verified, e.g. `/expoplatform/test-suites/exhibitor/exhibitor-favorites`). Every "QA Service suite" line in Jira (sub-task description, human summary, story note) links here; if a link cannot be built, fall back to the plain suite path. |

## Mapping — pipeline files → QA Service

**Requirements** (`<ISSUEKEY>-requirements.md`) → `create_requirement`:

| Pipeline | QA Service |
|---|---|
| `REQ-N: <text>` | `title` = requirement text (first sentence if long; rest → `summary`) |
| numbering `REQ-N` | `stableId` = `<PREFIX>-FR-NN` (zero-padded; REQ-3 → `<PREFIX>-FR-03`) |
| `[risk: High/Medium/Low]` | prepend to `summary` as `[risk: …]` |
| kind | `fr` for normal requirements; `oq` for grooming items still open at publish time (questions / contradictions / gaps — same list the Jira comment gets); `discrepancy` for "(unresolved conflict)" requirements |

**Test cases** (`<ISSUEKEY>-test-cases.md`) → `create_test_case` then
`edit_test_case` (creation only takes title/stableId; all content goes
through the edit call):

| Pipeline | QA Service |
|---|---|
| `TC-REQ-N.M — <name>` | `title` = scenario name; `stableId` = `<PREFIX>-NN` sequential over the whole file, in file order (record the TC-REQ-N.M → stableId map for the Jira comment) |
| parent `REQ-N` | `traceability` = `["<PREFIX>-FR-NN"]` |
| channel tag `[UI]` / `[API]` / `[mobile]` / `[export/email]` | `levelText` = `E2E (UI)` / `API` / `E2E (mobile)` / `E2E (export/email)` |
| `Applied techniques` (per REQ group) | `techniques` (uppercase, e.g. `["BVA", "STATE"]`) |
| requirement risk | `priority`: High → `P0`, Medium → `P1`, Low → `P2` |
| scenario polarity | `type`: `positive` or `negative` (negative = error/denial/limit paths) |
| — | `status`: `draft` |
| `Pre:` | `detail.preconditions` |
| `Steps:` (numbered, with `[data: …]` inline) | `detail.steps` (keep numbering, one string) — move long `[data: …]` values to `detail.testData` |
| `Exp:` | `detail.assertions` |
| `Post:` | append to `detail.notes` as `Post: …` |
| case goal | `detail.goal` = one sentence: what the case verifies (derive from name + Exp) |
| "needs clarification" markers | `detail.notes` |

## Suite selection — append by default

**Default: append to the existing feature suite.** One suite per
FEATURE, not per ticket — suites are the feature's living test design,
and splitting one feature across sibling suites is the main way this
integration loses its value. Create a new suite only when the ticket
introduces a feature that has no suite yet.

Always resolve the target BEFORE writing, and name it in the publish
preview so the user can redirect:

1. `list_suites`; find the suite whose role + feature area matches what
   the ticket touches (the context file's "Existing QA Service suite"
   section usually already names it). Ignore ticket-key naming — match
   on the FEATURE.
2. **Match found → append there**, whatever the issue type:
   - *Feature-extension story* (adds/changes behavior of an existing
     feature): append its requirements and cases; the feature's suite
     grows. Do not create a sibling suite for the story.
   - *Bug / bugfix*: append the regression cases that prove the fix
     (reference the bug key in `detail.notes`, e.g. `Regression for
     EP-NNNNN`), plus at most a `risk` or `discrepancy` requirement if
     the bug revealed a missing rule.
   - *Re-run of the same ticket*: append only what is new or changed.
   In every case use the suite's existing prefix and continue its
   stableId numbering (`get_suite` → highest used id). Apply the
   requirement-immutability and case-dedup rules below.
3. **No match → create a new suite**, named after the FEATURE (never
   after the ticket key), path/prefix per Config. This is the genuinely
   new-feature case only.
4. **Ambiguous** (the ticket spans two features, or the nearest suite is
   a partial match): do not guess silently — state both candidates in
   the publish preview with a recommendation and let the user pick. An
   existing suite whose imported requirements are empty (`0r · 0t`,
   a failed import) still counts as the feature's suite: append to it
   rather than creating a duplicate.

## Procedure (inside the step-6 confirmed publish)

1. `list_suites` for the product; pick the target suite per "Suite
   selection" above — append to the feature's existing suite by
   default; a new suite only when the feature has none.
2. **New suite needed** → `create_suite` (title, productId, prefix,
   folderId if a sibling folder was found). **Existing suite (the
   default: feature-extension story, bug, or re-run)** → do NOT create
   a duplicate; append
   only requirements/cases that are new or changed (compare stableIds
   via `get_suite`), and say so in the publish preview. There are no
   delete tools — never try to remove superseded items; mark them via
   `edit_test_case` `status: deprecated` instead.
   - **Requirements are immutable via MCP** (create only — no edit, no
     status): a requirement whose text materially changed since the
     last publish gets a NEW entry with a revision stableId
     (`<PREFIX>-FR-NNb`) and a summary starting `Supersedes
     <old stableId>:`. The old entry stays; never re-create an
     unchanged requirement.
   - **Case dedup on append:** before appending cases to an existing
     suite, compare each candidate against the suite's active cases
     (title + goal + assertions). A candidate that verifies the same
     behavior the same way is a duplicate — skip it and trace its
     requirement to the EXISTING case instead; list every skip in the
     publish preview. Append it only if it genuinely differs (new data
     path, new boundary, regression for a specific bug).
3. Create requirements in file order, then cases in file order
   (create + edit per case).
4. **Tag the cases for Coverage.** `list_tags` once; for each created
   case pick the applicable existing feature @tags (match the feature
   area, surface, and entity — do not force a tag that doesn't fit) and
   apply via `tag_case`. If an obviously-needed tag does not exist,
   `propose_tag` it and apply once accepted — proposed tags await
   approval (`approve_tag` is the reviewer's call, not the pipeline's),
   so note pending proposals in the final response. Untagged cases are
   invisible to `get_coverage` — that is the point of this step.
5. Verify: `get_suite` once at the end; check the requirement/case
   counts match the statistics block of the test-cases file. Report any
   mismatch in the final response.
6. Add to the Jira QA sub-task description (step 6 already writes it):
   `QA Service suite: <path> — <requirementCount> requirements /
   <testCaseCount> cases` plus the TC-REQ-N.M → stableId map (one line
   per case, in the machine-archive comment, not the description, if
   longer than ~15 lines). The map is REQUIRED in one of the two places
   — the code phase uses it for reconciliation and result write-back.

## Code phase — suite as the case source (qa-pipeline-code step 0)

When the code phase runs with the QA Service connector present, the
suite — not the Jira archive comment — is the source of truth for case
CONTENT (the team may have fixed cases in the web UI between phases):

1. Locate the suite: the `QA Service suite:` line in the QA sub-task
   description; fall back to a `list_suites` match on the story.
2. `get_suite`; using the TC-REQ-N.M → stableId map, reconcile the
   extracted `<STORY>-test-cases.md` against the suite cases:
   - a suite case's content differs (steps/assertions/priority edited
     in the UI) → the suite version wins; update the local file.
   - a suite case is `deprecated` → drop it from execution; note it.
   - a suite case exists with no counterpart in the Jira file (added
     by the team) → append it to the local file under its requirement,
     channel-tagged from its `levelText`, and execute it too.
   List every reconciliation change to the user before the stages run.
   If the stableId map is missing (a run published before it existed),
   match cases by title; cases that match nothing run from the Jira
   version unchanged — and skip the result write-back for them.
3. Connector absent or suite not found → the Jira archive comment alone
   is authoritative, exactly as before. Never block on QA Service.

## Result write-back (qa-pipeline-code step 6)

Within the same step-6 confirmation that posts the Jira result
comments, also write the run outcome to QA Service for every EXECUTED
case (skip not-executed ones):

- `get_test_case` first, then `edit_test_case` re-sending the full
  `detail` object with `notes` appended (never send a partial `detail`
  — treat it as replace-not-merge unless proven otherwise):
  `Run <YYYY-MM-DD> (<STORY> code phase): PASS | FAIL — <one-line
  reason if FAIL>; details: QA sub-task <KEY>`.
- A FAIL that produced a filed bug also gets `bug <BUGKEY>` appended to
  that line.
- Do NOT overwrite the lifecycle `status` (e.g. `implemented`) with a
  run result — run outcomes live in notes; the only status the
  pipeline ever sets is `deprecated` for superseded cases (docs phase).
- Include the write-back in the step-6 preview (how many cases get a
  result note) and report the PASS/FAIL counts written in the final
  response. Connector absent → skip silently-but-visibly, as always.

## Publish preview additions (same single pause)

The step-6 preview shown to the user must also state:
- QA Service: **appending** N requirements / M cases to existing suite
  `<path>` (K duplicates skipped) — or **creating** suite `<path>`
  (prefix `<PREFIX>`) because the feature has no suite yet — or
  "skipped (connector not enabled)".
- The reason for the choice in one clause ("matches the feature this
  ticket extends" / "no existing suite for this feature"), plus the
  runner-up candidate when the match was ambiguous — this line is what
  lets the user redirect before anything is written.
