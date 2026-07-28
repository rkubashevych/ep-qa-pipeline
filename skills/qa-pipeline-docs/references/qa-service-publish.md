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
| Web UI base URL | `https://qa-service.expoplatform.com` — suite detail page: `<base>/<productId>/test-suites/<suite path>` (verified, e.g. `/expoplatform/test-suites/exhibitor/exhibitor-favorites`). |

**Writing the suite link into Jira — bare URL only.** The Atlassian
connector's markdown→ADF conversion drops/mangles `[text](url)`
hyperlinks, so a markdown link arrives in Jira as unclickable text.
Always write the **full bare URL on its own**, which Jira auto-links:

```
QA Service suite: https://qa-service.expoplatform.com/expoplatform/test-suites/<suite path>
(<N> requirements / <M> cases, prefix <PREFIX>)
```

Never wrap it in `[...](...)`, never shorten it, never put the path in
the link text. Same rule for every place the suite is referenced —
sub-task description, human summary comment, story note.

## Mapping — pipeline files → QA Service

> Calibrated against an importer-built reference suite
> (`common/account-interactions`, prefix ACINT) — match its shape, not
> just the schema's required fields. **Controlled vocabularies below are
> mandatory:** free-text values outside them make the suite's own
> dashboards read zero (verified: invented `levelText` and
> `status: draft` collapsed every level/status bucket to 0 across 89
> cases while the total read 89).

### Requirements → `create_requirement`

| Pipeline | QA Service |
|---|---|
| `REQ-N: <text>` | `title` = a SHORT label naming the rule (≤ ~9 words, e.g. "Interaction query scoped to one event") — NOT the full sentence |
| `REQ-N: <text>` | `summary` = the requirement's full text, verbatim and self-contained (a reader must understand it without the ticket). **Never a bare `[risk: …]` tag** — the risk suffix goes at the END, after the text. Never omit `summary`. |
| kind (classify — do not default everything to `fr`) | `rule` = a MUST/MUST-NOT constraint · `invariant` = a property that must always hold · `risk` = a grooming risk · `nfr` = performance/security/limit/compat requirement · `fr` = functional behaviour · `oq` = still-open grooming question · `discrepancy` = "(unresolved conflict)" item. A suite with 0 rules / 0 invariants / 0 risks is a mis-classification, not a fact about the feature. |
| kind → stableId segment | `<PREFIX>-RULE-NN` · `-INV-NN` · `-R-NN` (risk) · `-NFR-NN` · `-FR-NN` · `-OQ-NN` · `-DISC-NN`, each numbered per kind from 01. The ID must match the kind — never file an invariant as `-FR-`. |
| `[risk: High/Medium/Low]` on a normal requirement | append to `summary` as ` [risk: High]` |
| a `risk`-kind requirement | `summary` ends with `Impact: high · Likelihood: medium` (lowercase vocab: `low`/`medium`/`high`) and names what it threatens by stableId, since `detail` cannot be written via MCP (see Known gaps) |
| REQ-N → stableId map | record it; the checklist/test-case files still use REQ-N |

### Test cases → `create_test_case` + `edit_test_case`

Creation takes only `suiteId`/`title`/`stableId`/`folderName`; all
content goes through the follow-up `edit_test_case`.

| Pipeline | QA Service |
|---|---|
| `TC-REQ-N.M — <name>` | `title` = scenario name |
| — | `stableId` = `<PREFIX>-<SEG>-NN`, where `<SEG>` is a 2–5 char aspect code shared by the cases of one behaviour area (`AUTH`, `VAL`, `DATA`, `READ`, `REG`, `CTR`, `BVA`, `PRIV`…), numbered per segment from 01. Fall back to the channel code (`UI`/`API`/`MOB`/`EXP`) only when no aspect is meaningful. **Never a flat `<PREFIX>-01…89`** — IDs must carry meaning. |
| requirement group `REQ-N` | `folderName` = the REQ group's behaviour-area label (e.g. "Opted-out favourite is invisible to the other party"). Group the file's cases into 4–8 such folders. **Never dump everything into "General".** |
| parent `REQ-N` (+ any seam requirements the case also covers) | `traceability` = the requirement stableIds, kind-correct (`["<PREFIX>-RULE-02","<PREFIX>-INV-01"]`) — list every requirement the case verifies, not just the parent |
| channel tag → level | `levelText` = EXACT canonical label only: `[API]` → `API-E2E` · `[UI]` → `E2E (UI)` · `[mobile]` → `Manual` · `[export/email]` → `Manual`. Other canonical labels when they genuinely apply: `Unit`, `Integration`, `Contract`, `Component-FE`, `Performance`, `Worker-home`. **Never invent labels** (`API`, `E2E (mobile)`, `E2E (export/email)` are invalid and produce an empty level on the case). |
| — | `status` = `planned` (vocabulary: `planned` / `implemented` / `partial` / `deferred` / `na`). **`draft` is NOT in the vocabulary** — it renders as 0 in every readiness bucket. Use `deferred` for a case knowingly not executable yet, `na` for one routed out. |
| `Applied techniques` (per REQ group) | `techniques`, uppercase tokens (`BVA`, `EP`, `STATE`, `DT`, `UC`, `CONTRACT`, `INVARIANT`, `UI-CONF`) |
| requirement risk | `priority`: High → `P0`, Medium → `P1`, Low → `P2` |
| scenario polarity | `type`: `positive` or `negative` (negative = error/denial/limit paths) |
| case goal | `detail.goal` = one sentence: what the case verifies |
| `Pre:` | `detail.preconditions` |
| `Steps:` (numbered) | `detail.steps` (keep numbering, one string) |
| `[data: …]` values | `detail.testData` — ALWAYS populate it (extract the data out of the steps/preconditions); leaving it empty loses the case's data setup. Write "None — uses default event fixtures" when there really is none. |
| `Exp:` | `detail.assertions` |
| `Post:` | append to `detail.notes` as `Post: …` |
| "needs clarification" markers | `detail.notes` |
| tags applied in step 4 | `detail.tagPlan` = one line naming the tags attached and why (mirrors the reference suites) |

### Known MCP gaps — state them, don't fake them

These cannot be set through the connector today (verified against the
tool schemas). Do not invent workarounds that corrupt other fields;
report them once in the final response instead:

- **Requirement `detail` and `priority`** — `create_requirement` accepts
  only kind/title/summary/stableId, and there is no `edit_requirement`.
  So the relationship model (`type`, `related`, `implements`,
  `constrainedBy`, `enforces`) and the risk model (`impact`,
  `likelihood`, `threatens`) stay empty. Encode what matters in
  `summary` prose (as above) and say so.
- **Case `levels` array and `implementations`** — not parameters of
  `edit_test_case`. Setting an exact canonical `levelText` is the best
  available signal; **verify once** whether the server derives `levels`
  from it, and report the answer.
- **Suite `summary` / `status` / `owner` / `lastReviewed`** —
  `create_suite` takes only title/productId/prefix/folderId, so a
  pipeline-created suite has a bare header.
- **`traceLinks` graph** — materialized by the importer, not by
  `create_test_case`; per-case `traceability` is still stored and shown.

**Post-publish enrichment (tell the user once, in the final response):**
the web UI can fill several of these server-side — "Generate missing
summaries" (requirements), "Auto-tag untagged" (cases), "Collect
requirements" / "Import docs" (suite header + relationship detail).
That is a human click, never a pipeline action.

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
5. Verify: `get_suite` once at the end and check BOTH:
   - counts match the statistics block of the test-cases file;
   - **the dashboards are not zeroed** — `stats.byLevel` must sum to the
     case total (a zero row against a non-zero total means `levelText`
     was outside the canonical vocabulary) and the status buckets must
     account for every case (all-zero means `status` was outside
     `planned/implemented/partial/deferred/na`). Also confirm no
     requirement kind is suspiciously absent (0 rules AND 0 invariants
     AND 0 risks = mis-classification).
   Report any mismatch in the final response and fix it with
   `edit_test_case` before finishing — do not leave a suite whose own
   charts read zero.
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
