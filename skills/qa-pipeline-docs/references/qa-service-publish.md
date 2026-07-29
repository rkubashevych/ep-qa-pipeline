# QA Service publish — suite creation from pipeline output

How `qa-pipeline-docs` step 6 publishes the groomed requirements and
test cases into **QA Service** (the team's test-suite system of record)
via its MCP connector, alongside the Jira QA sub-task. Edit this file —
not the orchestrator's SKILL.md — when adopting for another product or
QA Service instance.

## The switch — QA Service publishing is OPTIONAL

| Setting | Value |
|---|---|
| QA Service publishing | `ask` |

Options: `ask` (default — put the question to the user at the start of
the run) · `always` (publish whenever the connector is present, no
question) · `never` (Jira-only; never publish, never ask). Change the
row to `never` while the QA Service write-API gaps (EP-55653) are open
and you want Jira-only runs without being asked every time.

**How `ask` behaves.** ONE question, asked at the START of the run
(step 0, before stage 1) — never at the end, so a "no" costs nothing:

> QA Service: publish this ticket's requirements + test cases to a
> suite as well as the Jira QA sub-task? (yes / no — Jira-only)

Rules:

- If the user already stated a preference when invoking the pipeline
  ("run the docs pipeline, no QA Service" / "…and publish to QA
  Service"), honour it and do NOT ask.
- If the connector is not present, do not ask at all — Jira-only, note
  it once in the final response.
- Carry the answer through the whole run and restate it in the step-6
  publish preview ("QA Service: skipped — you chose Jira-only at the
  start"). The user can still flip it at that confirmation.
- **A "no" disables WRITES only.** Reading an existing suite in stage 1
  (grooming comparison material) has no side effects and stays on — it
  is one of the more useful parts. If the user says "skip QA Service
  entirely" / "don't touch it", skip the read too.
- A "no" is not a failure and must not be reported as a gap by the run
  analyzer: it records `— publishing declined by the user`.

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
| `[risk: High/Medium/Low]` | `priority`: High → `P0`, Medium → `P1`, Low → `P2`. Keep the ` [risk: High]` suffix on `summary` too — it is what the checklist/test-case files carry. |
| requirement `detail` (ALWAYS populate — this is what makes it more than a line of text) | `type` (short classifier: Constraint / Data integrity / Security / State machine / Referential…), `statement`, `rationale`, `scope`, `source` (the AC page or ticket it came from). Per kind: `actor` / `trigger` / `outcome` for `fr`; `metric` / `target` for `nfr`; `impact` / `likelihood` / `mitigation` for `risk` (vocab `low`/`medium`/`high`). |
| cross-references between requirements | `detail.related` / `enforces` / `threatens` / `implements` / `constrainedBy` — arrays of stableIds. All but `related` become trace-graph edges on write, so a rule that enforces an invariant, or a risk that threatens one, must say so here. |
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
| channel tag → level | Pass **`levels`** (the code array — this is what the Coverage-by-level table counts and the implement workflow selects on) AND `levelText`: `[API]` → `levels: ["AE"]`, `API-E2E` · `[UI]` → `["E2E"]`, `E2E (UI)` · `[mobile]` → `["M"]`, `Manual` · `[export/email]` → `["M"]`, `Manual`. Other codes when they genuinely apply: `U` Unit, `I` Integration, `C` Contract, `CFE` Component-FE, `Perf` Performance, `worker` Worker-home. A case with no `levels` is counted nowhere and can never be picked up for automation. **Never invent labels** — `API`, `E2E (mobile)`, `E2E (export/email)` are not canonical. |
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

### Suite header — always set it (`edit_suite`)

`create_suite` still takes only title/productId/prefix/folderId, so
immediately after creating a suite call `edit_suite` to fill the header
a browser needs: `summary` (a paragraph saying what the feature is and
what the suite covers — model it on an importer-built suite),
`status` (`Draft`), `owner` (the pipeline operator + team),
`lastReviewed` (today, YYYY-MM-DD). A suite that lands with a bare
title is an incomplete publish.

### Correcting an existing suite (all of it is editable now)

Nothing published is frozen — `edit_requirement`, `edit_test_case` and
`edit_suite` all merge (omitted fields are preserved) and every write
rebuilds the suite's trace-graph edges. So on a re-run, or when a
mistake surfaces:

- wrong requirement `kind` or a stableId that misrepresents it →
  `edit_requirement` with the corrected `kind` + `stableId`. Renaming a
  stableId rewrites every reference to it in the suite (test-case
  traceability and other requirements' cross-link lists) — no orphans.
- thin requirement (no `detail`, no `priority`) → fill it in place
  rather than creating a superseding entry.
- a requirement that no longer applies → `status: "retired"` (there is
  still no delete).
- case missing `levels`, or with a stale status/traceability → edit it.

Prefer correcting in place over creating revision entries; the
"supersede with `-FR-NNb`" workaround is obsolete.

**Still not settable via MCP:** the `implementations[].ref` (setting
`levels` auto-creates a placeholder entry `{ref: "", level: <code>}` —
harmless, but it means a non-empty `implementations` array does NOT
mean a real test is linked).

### NEVER call `summarize_requirement` on pipeline-written requirements

`summarize_requirement` (and the UI's per-requirement **Regenerate** /
**Generate missing summaries** buttons) rewrites BOTH `title` and
`summary` from the requirement's current content. It is now repairable
with `edit_requirement` — but only if you still have the original text,
which the tool does not return before overwriting it.

Tested on one requirement (PRIVFAV-FR-02):

- before — `title`: "An opted-out favourite is added to the user's own
  favourites list exactly like a regular favourite" · `summary`:
  "[risk: Medium]"
- after — `title`: "Opted-out favouriting parity" · `summary`:
  "Opted-out users retain full access to favouriting, storing and
  managing saved items identically to regular users…"

Three losses, all in one call: the requirement's testable text was
replaced by a 3-word label (the scoping word "own" — the whole point —
is gone from both fields); the generated summary **contradicts the
suite's own invariant** (an opted-out favourite is explicitly NOT
identical: no notification, no connection row, no lead); and the
`[risk: …]` signal was dropped.

Rule: the pipeline never calls it, and never advises the user to click
those buttons on a suite it published. Pipeline-authored requirement
text is authoritative — a generated label is not an improvement over it.

**Post-publish enrichment that IS safe:** "Auto-tag untagged" /
`apply_auto_tags` (additive, touches only tag links). Treat "Collect
requirements" / "Import docs" (`start_collect_requirements`,
`start_import_docs`) as UNVERIFIED on an already-populated suite: they
merge a fresh extraction into the register by stableId, and since the
extractor mints its own ids they may duplicate rather than enrich —
and there is no delete. Test on a throwaway suite before ever pointing
them at a real one.

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
5. Verify: `get_suite` once at the end and check:
   - counts match the statistics block of the test-cases file;
   - **status buckets account for every case** — all-zero means `status`
     was outside `planned/implemented/partial/deferred/na`. This IS
     fixable: re-`edit_test_case` with `status: "planned"` before
     finishing.
   - **`stats.byLevel` sums to the case total** — a zero row against a
     non-zero total means `levels` was not sent. Fixable: re-
     `edit_test_case` with the right code array.
   - **`traceLinks` is non-empty** — it should hold one `satisfies` link
     per case (plus requirement↔requirement edges from `detail`
     cross-links). Empty means `traceability` never landed.
   - no requirement kind is suspiciously absent (0 rules AND 0
     invariants AND 0 risks = mis-classification). Fixable in place with
     `edit_requirement` (`kind` + corrected `stableId`) — do it rather
     than reporting it.
   - the suite header is filled (`summary`, `status`, `owner`,
     `lastReviewed`) — otherwise call `edit_suite`.
   Fix what is fixable before finishing; report the rest.

> **Verified — all three edit tools MERGE.** Omitted fields are
> preserved: an edit sending only `status` + `levelText` left `detail`
> (all keys), `techniques`, `priority`, `type`, `traceability` and the
> attached tags byte-identical across 88 cases. Partial edits are safe —
> no read-modify-write needed. Inside `detail`, send a key complete:
> assume the key you send replaces that key's value.
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

- `get_test_case` first (to read the current `notes`), then
  `edit_test_case` with `detail: { notes: "<existing notes>" + "\nRun
  <YYYY-MM-DD> (<STORY> code phase): PASS | FAIL — <one-line reason if
  FAIL>; details: QA sub-task <KEY>" }`. Top-level fields you omit are
  preserved (verified: `edit_test_case` merges), but inside `detail`
  send `notes` complete — assume a key you send replaces that key.
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
