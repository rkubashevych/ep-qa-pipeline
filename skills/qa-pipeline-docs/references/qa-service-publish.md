# QA Service publish — suite creation from pipeline output

**Contents:** Preconditions · Config · Mapping — pipeline files → QA
Service · Suite selection — append by default · Procedure (inside the
step-6 confirmed publish) · Code phase — suite as the case source ·
Result write-back (incl. Improvised coverage becomes permanent + the
Retraction convention) · Publish preview additions

How `qa-pipeline-docs` step 6 publishes the groomed requirements and
test cases into **QA Service** (the team's test-suite system of record)
via its MCP connector, alongside the Jira QA sub-task. Edit this file —
not the orchestrator's SKILL.md — when adopting for another product or
QA Service instance.

## Preconditions

QA Service publishing is **on by default** whenever the connector is
present — it is part of a normal publish, not an extra. The user can
still decline at the step-6 confirmation, or say "no QA Service" when
invoking the pipeline; honour that for the run without arguing.

- The QA Service MCP connector must be enabled in the session. Detect it
  by the presence of its tools (`list_products`, `create_suite`,
  `create_requirement`, `create_test_case`, `edit_requirement`,
  `edit_test_case`, `edit_suite`, `apply_auto_tags`, …).
- **If the connector is absent, skip this publish silently-but-visibly:**
  do everything else as normal and add one line to the final response —
  "QA Service publish skipped (connector not enabled)". Never block the
  Jira publish on it.
- QA Service is **production data shared with the whole team.** The
  connector DOES expose destructive tools — `delete_suite`,
  `delete_test_cases`, `delete_requirements`, `delete_suite_folder`,
  `delete_test_case_folder`, `merge_duplicate_case` — and **no pipeline
  stage ever calls one of them.** A wrong case is corrected
  (`edit_test_case`), retired (`status: na` + a `discrepancy:` note) or
  left for a human in the web UI; "skip duplicates" never becomes
  "delete duplicates". Publish only after the user's explicit yes at
  the step-6 pause (one confirmation covers Jira + QA Service).

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

### Requirements → `create_requirement` (one call each — it takes everything)

`create_requirement` accepts `kind`, `title`, `summary`, `stableId`,
`priority` AND `detail`. Send them all in the creating call; no
follow-up `edit_requirement` is needed on a fresh publish.

| Pipeline | QA Service |
|---|---|
| `REQ-N: <text>` | `title` = a SHORT label naming the rule (≤ ~9 words, e.g. "Interaction query scoped to one event") — NOT the full sentence |
| `REQ-N: <text>` | `summary` = the requirement's full text, verbatim and self-contained (a reader must understand it without the ticket). **Never a bare `[risk: …]` tag** — the risk suffix goes at the END, after the text. Never omit `summary`. |
| kind (classify — do not default everything to `fr`) | `rule` = a MUST/MUST-NOT constraint · `invariant` = a property that must always hold · `risk` = a grooming risk · `nfr` = performance/security/limit/compat requirement · `fr` = functional behaviour · `oq` = still-open grooming question · `discrepancy` = "(unresolved conflict)" item. A suite with 0 rules / 0 invariants / 0 risks is a mis-classification, not a fact about the feature. |
| kind → stableId segment | `<PREFIX>-RULE-NN` · `-INV-NN` · `-R-NN` (risk) · `-NFR-NN` · `-FR-NN` · `-OQ-NN` · `-DISC-NN`, each numbered per kind from 01. The ID must match the kind — never file an invariant as `-FR-`. |
| `[risk: High/Medium/Low]` | `priority`: High → `P0`, Medium → `P1`, Low → `P2`. Keep the ` [risk: High]` suffix on `summary` too — it is what the checklist/test-case files carry. |
| requirement `detail` (ALWAYS populate — this is what makes it more than a line of text) | `type` (short classifier: Constraint / Data integrity / Security / State machine / Referential…), `statement`, `rationale`, `scope`, `source` — the document containing the WHOLE statement; if more than one document is involved, attribute per clause and mark the spec of record, e.g. `spec of record: Confluence AC page item 4. Clause "no larger than other result cards": design sub-task EP-55708 item 2 ONLY — not in the AC page`. A bare list of documents joined by "and" is not acceptable: it asserts that all of them support all of the statement. Per kind: `actor` / `trigger` / `outcome` for `fr`; `metric` / `target` for `nfr`; `impact` / `likelihood` / `mitigation` for `risk` (vocab `low`/`medium`/`high`). |
| cross-references between requirements | `detail.related` / `enforces` / `threatens` / `implements` / `constrainedBy` — arrays of stableIds. All but `related` become trace-graph edges on write, so a rule that enforces an invariant, or a risk that threatens one, must say so here. |
| REQ-N → stableId map | `detail.pipelineId` = `REQ-N` on the requirement (since 0.34.0 — the map lives on the item, nowhere else); the checklist/test-case files still use REQ-N |
| the ticket the requirement came from | `sources` = `[{kind: "jira", label: "<ISSUEKEY>", url: "<ticket URL>"}]` plus one entry per governing document (`confluence` for the AC page, `anchorUrl` to the exact heading when there is one). This is the per-ticket **scope marker** inside a per-feature suite — the code phase selects this run's requirements by it |

### Test cases → `create_test_case` (one call each — it takes everything)

`create_test_case` writes the case **with its full content in one
call**: `title`, `stableId`, `folderName`, `levels`, `levelText`,
`status`, `priority`, `type`, `techniques`, `traceability` and the whole
`detail` object. Do NOT create a bare case and fill it with a follow-up
`edit_test_case` — that is twice the calls and leaves a window where the
case is empty. `edit_test_case` is for CORRECTING cases later.

| Pipeline | QA Service |
|---|---|
| `TC-REQ-N.M — <name>` | `title` = scenario name |
| — | `stableId` = `<PREFIX>-<SEG>-NN`, where `<SEG>` is a 2–5 char aspect code shared by the cases of one behaviour area (`AUTH`, `VAL`, `DATA`, `READ`, `REG`, `CTR`, `BVA`, `PRIV`…), numbered per segment from 01. Fall back to the channel code (`UI`/`API`/`MOB`/`EXP`) only when no aspect is meaningful. **Never a flat `<PREFIX>-01…89`** — IDs must carry meaning. |
| requirement group `REQ-N` | `folderName` = a functionality label derived from the REQ group's behaviour area (e.g. "Opted-out favourite is invisible to the other party"). **Target ~5–8 cases per folder:** split a large REQ group into sub-aspect folders ("<area> — validation", "<area> — permissions"), merge adjacent tiny groups under one functional label. **Never dump everything into "General"** — a publish where any case lands in General, or one folder holds >10 cases, is a mapping failure; fix the folder plan before writing. State the folder plan (folder → case count) in the publish preview. |
| parent `REQ-N` (+ any seam requirements the case also covers) | `traceability` = the requirement stableIds, kind-correct (`["<PREFIX>-RULE-02","<PREFIX>-INV-01"]`) — list every requirement the case verifies, not just the parent |
| channel tag → level | Pass **`levels`** (the code array — this is what the Coverage-by-level table counts and the implement workflow selects on) AND `levelText`: `[API]` → `levels: ["AE"]`, `API-E2E` · `[UI]` → `["E2E"]`, `E2E (UI)` · `[mobile]` → `["M"]`, `Manual` · `[export/email]` → `["M"]`, `Manual` · dual-tagged `[API][UI]` → `["AE", "E2E"]`, `API-E2E + E2E (UI)` (one case, two levels — never two cases). Other codes when they genuinely apply: `U` Unit, `I` Integration, `C` Contract, `CFE` Component-FE, `Perf` Performance, `worker` Worker-home. A case with no `levels` is counted nowhere and can never be picked up for automation. **Never invent labels** — `API`, `E2E (mobile)`, `E2E (export/email)` are not canonical. |
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
| ` [core]` heading marker | `detail.core` = `yes` on the REQ's core case (the human-tier representative that stage 9 always walks); omit on all other cases. Also propose a `core` tag in step 4 where the tag catalogue allows — pending approval is fine. |
| `TC-REQ-N.M` id | `detail.pipelineId` = `TC-REQ-N.M` (since 0.34.0). The code phase rebuilds the local file's ids from this; never from a Jira comment |
| the ticket | `detail.ticket` = `<ISSUEKEY>` (since 0.34.0). The per-ticket scope marker: step 0 executes the suite cases whose `detail.ticket` is this run's key (plus team-added cases tracing to this run's requirements). Feature tags are NOT used for this — the tag catalogue is the platform-feature vocabulary and needs approval |

### Structural checks → `create_test_case` (STRUCT cases) — since 0.33.0

The checklist's `[UI]` presence / label / field-type checks have no
test case in `<ISSUEKEY>-test-cases.md` by design (stage 4's rule), but
web-testing executes them, so they need a home in the record. Until
0.33.0 they lived only in a fenced "structural checks only" comment on
the QA sub-task — which also meant their verdicts never reached the run.
Publish each structural check as a case:

| Checklist | QA Service |
|---|---|
| a `[UI]` check under a structural REQ (or a structural check under a behavioural REQ) | one case; `title` = the check rephrased as a scenario ("State label is shown above the State select") |
| — | `stableId` = `<PREFIX>-STRUCT-NN`, numbered from 01 |
| REQ | `folderName` = `<REQ area> — structure`; `traceability` = the REQ's stableId |
| — | `levels: ["E2E"]`, `levelText: "E2E (UI)"`, `techniques: ["UI-CONF"]`, `type: positive`, `status: planned`, `priority` from the REQ's risk |
| the check text | `detail.goal` = the check verbatim; `detail.steps` = "1. Open <surface>. 2. Locate <element>."; `detail.assertions` = the check; `detail.testData` = "None — uses default event fixtures" |
| — | `detail.notes` = `Structural check from <ISSUEKEY>-checklist.md — no TC in the test-cases file by design (stage 4 rule).`; `detail.ticket` = `<ISSUEKEY>`; `detail.pipelineId` = `REQ-N/struct-k` (k = the check's position under its REQ) |

STRUCT cases are **not** counted in the test-cases statistics block and
never get a `[core]` marker; the publish preview reports them on their
own line ("N cases + S structural checks"). The analyzer's suite-sync
check expects exactly S extra `-STRUCT-` ids beyond the test-cases
file.

**The join key is the stableId, end to end.** On the code phase STRUCT
cases are roster cases like any other, and every surface that names a
structural check carries the same id so step 6 can join the verdict to
the roster row:

- step 0 rebuilds the checklist's structural section as
  `- [ ] REQ-N/struct-k · <PREFIX>-STRUCT-NN [UI] <check text>`;
- web-testing's "Structural checks" table has a `Case` column = that
  stableId, and its Status uses the vocabulary: `PASS` / `FAIL` /
  `NOT EXECUTED — page not visited` (never a bare "not visited");
- step 6 records them per the `test-runs.md` mapping (`NOT EXECUTED` →
  `skipped` with the reason);
- the scope count is reported as `M + S` (behavioural + structural),
  and roster count = M + S in the post-publish check.

### Suite header — set it IN `create_suite`

`create_suite` accepts the header fields directly: `summary` (a
paragraph saying what the feature is and what this suite covers — model
it on an importer-built suite), `status` (`Draft`), `owner` (the
pipeline operator + team), `lastReviewed` (today, YYYY-MM-DD), on top
of `title` / `productId` / `prefix` / `folderId`. Pass them at
creation — a suite that lands with a bare title is an incomplete
publish, and it is a missed parameter, not a limitation.

Use `edit_suite` only to fix or refresh the header of a suite that
already exists (e.g. bump `lastReviewed` when appending to it).

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
- **cases piled into "General" (or one oversized folder)** — a legacy
  publish from before the folder rule: reorganize in place with
  `create_test_case_folder` (one per functionality label, ~5–8 cases
  each) + `move_test_case`. When appending to such a suite, offer this
  reorganization in the publish preview — new cases must never join the
  General pile.

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
   delete tools — never try to remove superseded items; retire them
   instead (requirement → `edit_requirement` `status: "retired"`; case →
   `edit_test_case` `status: "na"` plus a `detail.notes` line saying
   what superseded it). **`deprecated` is not a valid case status** —
   the vocabulary is `planned` / `partial` / `implemented` / `deferred`
   / `na`.
   - **Changed requirements are edited in place** — `edit_requirement`
     takes kind / title / summary / priority / status / detail /
     stableId and merges. Update the existing entry rather than adding a
     revision; never re-create an unchanged requirement.
   - **Case dedup on append:** before appending cases to an existing
     suite, compare each candidate against the suite's active cases
     (title + goal + assertions). A candidate that verifies the same
     behavior the same way is a duplicate — skip it and trace its
     requirement to the EXISTING case instead; list every skip in the
     publish preview. Append it only if it genuinely differs (new data
     path, new boundary, regression for a specific bug).
3. Create requirements in file order (one `create_requirement` each,
   full content), then cases in file order (one `create_test_case`
   each, full content). Requirements first — cases reference their
   stableIds in `traceability`. Every case carries its `folderName`
   from the folder plan; when appending, reuse the suite's existing
   functionality folders where the label matches and create new ones
   only for genuinely new areas.
4. **Tag the cases for Coverage.** `list_tags` once to see the
   catalogue, then ONE `apply_auto_tags` call carrying the whole
   `perCase` array (`{stableId, tags}`, up to 400 cases) — not a
   `tag_case` call per case. Pick tags that genuinely match the feature
   area, surface and entity; do not force a tag that doesn't fit. A tag
   name that is not yet in the catalogue is created as PENDING for a
   human to approve (`approve_tag` is the reviewer's call, never the
   pipeline's) — list any pending names in the final response. Untagged
   cases are invisible to `get_coverage`, which is the point of this
   step.
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
   - **folder distribution matches the plan** — no case in "General",
     no folder over ~10 cases. Fixable in place:
     `create_test_case_folder` + `move_test_case`.
   Fix what is fixable before finishing; report the rest.

> **Verified — all three edit tools MERGE.** Omitted fields are
> preserved: an edit sending only `status` + `levelText` left `detail`
> (all keys), `techniques`, `priority`, `type`, `traceability` and the
> attached tags byte-identical across 88 cases. Partial edits are safe —
> no read-modify-write needed. Inside `detail`, send a key complete:
> assume the key you send replaces that key's value.
6. Add to the Jira QA sub-task description (step 6 already writes it)
   the bare suite URL + `(N requirements / M cases, prefix <PREFIX>)`.
   **Do not publish a separate TC-REQ-N.M → stableId map anywhere**:
   the mapping is `detail.pipelineId` on each case and requirement
   (0.34.0), so it lives on the item it belongs to and cannot go stale
   on its own. (Until 0.34 it rode on the checkbox-tracker lines.)
   A standalone map block was measured at ~2,000 characters and went
   stale the first time stableIds were corrected.

## Code phase — suite as the case source (qa-pipeline-code step 0)

When the code phase runs with the QA Service connector present, the
suite — not any local file — is the source of truth for case
CONTENT (the team may have fixed cases in the web UI between phases):

1. Locate the suite: the `QA Service suite:` line in the QA sub-task
   description; fall back to a `list_suites` match on the story.
2. `get_suite`; **scope = the cases whose `detail.ticket` is this run's
   key**, plus any case tracing to one of this run's requirements
   (`sources` with `kind: jira, label: <KEY>`) that lacks the marker
   (team-added — flag it). Join local ↔ suite by `detail.pipelineId`
   (pre-0.34 suites: the case id on the sub-task's tracker lines — shape
   in "Legacy formats" below; older still: match by title). Then reconcile
   the extracted `<STORY>-test-cases.md` against the suite cases:
   - a suite case's content differs (steps/assertions/priority edited
     in the UI) → the suite version wins; update the local file.
   - a suite case is `na` or `deferred` → drop it from execution; note it.
   - a suite case exists with no counterpart in the Jira file (added
     by the team) → append it to the local file under its requirement,
     channel-tagged from its `levelText`, and execute it too.
   List every reconciliation change to the user before the stages run.
   If neither an id nor a title match is possible, run that case from
   the local version unchanged and skip the result write-back for it.
   `-STRUCT-` cases rebuild the structural section of
   `<STORY>-checklist.md` (one `[UI]` check per case, under its REQ).
3. Connector absent or suite not found → `runs/<STORY>/docs/` on this
   machine is the only source (pre-0.33 tickets: the legacy archive
   comment via `extract_archive.py`). Neither reachable → PAUSE; never
   run the code phase on cases you cannot read.

## Bug-fix mode — the regression mini suite (qa-pipeline-code step 0) — since 0.33.0

A standalone Bug or Defect has no docs phase, so until 0.33.0 its 2–4
mini cases existed only in a local file and its verdicts only in
markdown: no suite, no run, no durable record (EP-56998 open-items
#13). Bug-fix mode now publishes the mini cases before stage 5 —
**behind its own REQUIRED PAUSE**, because normal step 0 has no confirm
and this is a write to shared production data — so that step 6 can
open a run with a roster and the human round has somewhere to write.
Order of operations: derive the mini cases → **preview + yes** →
publish → stages 5–8 → step 6 creates the run (roster = the published
cases) → stage 9 → walk → stage 10.

**The preview** (one message, one yes): the target suite (existing
path, or "new: <path>, prefix <PREFIX>"), the requirement (kind, title,
the ticket sentence it quotes), each case (stableId, title, channel),
and the `Regression for <KEY>` note. Nothing is written before the yes.

1. **Target suite = the FEATURE's suite**, per "Suite selection" above:
   `list_suites`, match on the feature the bug touches (the parent
   story's suite when the Bug is linked to one). Found → append.
   Not found → create the feature's suite (path / prefix per Config,
   named after the feature, never after the bug key). Ambiguous →
   state both candidates and ask.
2. **One requirement** unless the suite already states the rule:
   `kind: fr` (or `rule` when the ticket words it as a MUST), `title`
   = the expected behaviour in ≤ 9 words, `summary` = the ticket's own
   expected-result sentence verbatim, `priority` from the bug's
   priority, `detail.source` = `Bug <KEY>: <field>` — the
   source-of-record rule applies: no expected result the ticket does
   not state.
3. **The mini cases** as normal cases: `traceability` → that
   requirement, `detail.notes` opens with `Regression for <KEY>`,
   stableIds continue the suite's numbering under an aspect segment
   (`REG` when nothing better fits). TC-1 (the reproduction) carries
   `detail.core: yes`.
4. Regression cases added AFTER stage 5 (from pr-summary's
   "Behaviours touched") are appended the same way, through the same
   kind of preview + yes. Before step 6 they simply join the roster the
   run is created with; only a case learned after the run exists needs
   `add_run_cases`. The scope file says which cases were added when.
5. Connector absent → PAUSE and say what is lost (no run, no record,
   local-only verdicts); continue only on the user's explicit yes, and
   say so again in the final response.

## Result write-back (qa-pipeline-code step 6) — a QA Service test run

**Since 0.30.0 verdicts are recorded as a test run, not as notes text.**
The full rule — one run per pass, roster = scope, the status → verdict
mapping, what stays `not_run` until the human round, stage 10's manual
pass, retractions as re-records — is
**`../../qa-pipeline/references/test-runs.md`**, the single home. In
short, inside the same step-6 confirmation:

- `create_test_run` (title `<KEY> <mode> <date> — <env>`, `env`,
  `releaseId` when one exists, `principal`
  `ep-qa-pipeline agent (<KEY> <mode>, stage <n>)`, `caseIds` = the
  in-scope suite case ids) — then `record_case_result` per case using
  the mapping table, `source: machine`. **A `fail` files a Jira defect
  at record time**, so FAIL / PARTIAL rows stay `not_run` until stage 10
  (narrow exception: runtime-confirmed + evidenced + blocking).
- The run is left `running` when any row is `not_run`; stage 10 records
  the human pass into the same run and closes it.
- Do NOT overwrite the lifecycle `status` (e.g. `implemented`) with a
  run result; the only status the pipeline ever changes after creation
  is `na` for a superseded case (docs phase).
- Do NOT write run lines into `detail.notes` any more. Notes keep the
  `discrepancy:` line for SPEC-DEFECTs (a property of the case) and
  pre-0.30 history; the run is the verdict store. Pre-0.30 practice
  (append `Run <date> …` lines, the `⚠ CURRENT VERDICT:` first line) is
  retired — it re-implemented what the service does natively and was
  invisible to `executed_coverage`, which is how a suite read
  `verified: 0` after five passes (EP-53978).

### Improvised coverage becomes permanent (same step-6 write-back)

- **Confirmed risk rows** (`RISK-CR-<n>` executed by stage 7/8 with
  FAIL CONFIRMED, or worth keeping regardless): propose each as a real
  suite test case (`suggest_test_case` when available, else
  `create_test_case` after the same confirmation) so next run has a
  case where this run had only an improvisation. Say how many in the
  preview. Once the case exists, `add_run_cases` puts it on this pass's
  roster so its verdict is recorded like any other; a risk row not
  promoted has no roster slot and stays in the stage report and the
  open-items ledger (`../../qa-pipeline/references/open-items-ledger.md`).
- **SPEC-DEFECT verdicts:** append a `discrepancy:` line to the suite
  case's notes stating what the case says vs what the spec/behaviour
  is, and list the case under "Requirements to correct" in the human
  summary. Do not silently fix the case text — the correction goes
  through the docs-phase owner. On the run the case is `skipped` with a
  `SPEC-DEFECT —` note — never `known_defect`, which asserts a product
  defect (`test-runs.md`, mapping table).

### Retraction convention — how a wrong verdict gets corrected

Binding on EVERY writer of verdicts (code-phase step 6,
`qa-manual-results`, any future stage). A correction never edits or
hides the old verdict, and it must be impossible to read the old
verdict as current:

- **A retraction is a re-record on the run** (`record_case_result` on
  the same case; the service supersedes and keeps both, with each
  verdict's principal and timestamp — `case_execution_history` shows
  the chain). The pre-0.30 notes forms (`SUPERSEDES …` lines,
  `⚠ CURRENT VERDICT:` first line) are no longer written; where they
  exist they are history, and the run is the current truth.
- The stage that records a retraction also says so in its Jira human
  summary — retractions listed first, `old → new` with the reason and
  the run id. A correction that only lives in the suite has not been
  communicated.
- **Retraction target rule:** the retraction comment goes to the ticket
  and thread where the retracted verdict was **published**, even when
  that is not the ticket under test — the one sanctioned cross-ticket
  comment, bounded to ≤ 6 lines and no dumps
  (`../../qa-pipeline/references/test-runs.md` → "Retraction target
  rule"). Stage 10's reconciliation therefore records, per RETRACTS row,
  the ticket key + comment id where the old verdict lives.
- Include the write-back in the step-6 preview (run title, roster count,
  how many rows will be recorded per verdict, how many stay `not_run`
  for the human round, and — narrow exception only — each `fail` by
  case, since recording it files the bug) and report the recorded
  counts and the run id in the final response. Connector absent → skip
  silently-but-visibly, as always.

## Legacy formats (read-only — for tickets published before 0.34)

Nothing below is written any more. It is here so step 0 can read an
old ticket without guessing.

- **Checkbox tracker (0.26 – 0.33), one comment on the QA sub-task,
  one line per case:** `- [ ] TC-REQ-N.M — <name> [channel] · <stableId>`.
  The `<stableId>` is the suite case id — the join key that
  `detail.pipelineId` replaced. Checkboxes were manual-only and are not
  verdicts; the run is.
- **Structural checks (0.26 – 0.34):** a fenced block on the sub-task
  labelled `(structural checks only)` — the checklist's `[UI]`
  structural section verbatim (`- [ ] REQ-N.M [UI] <check>` lines), no
  case ids, because they had no suite case until STRUCT cases (0.35).
  Execute them from that block; promote them to `<PREFIX>-STRUCT-NN`
  cases only if the ticket is re-published.
- **Machine archive (pre-0.33):** comments made of `File: <name>` labels
  each followed by a fenced block (split files labelled `(part i/N)`).
  `skills/qa-pipeline-code/scripts/extract_archive.py` re-joins them.

## Publish preview additions (same single pause)

The step-6 preview shown to the user must also state:
- QA Service: **appending** N requirements / M cases to existing suite
  `<path>` (K duplicates skipped) — or **creating** suite `<path>`
  (prefix `<PREFIX>`) because the feature has no suite yet — or
  "skipped (connector not enabled)".
- The **folder plan**: each functionality folder with its case count
  (target ~5–8 per folder), plus — when the target suite's existing
  cases sit in "General" — the offer to reorganize them into the same
  folders.
- The reason for the choice in one clause ("matches the feature this
  ticket extends" / "no existing suite for this feature"), plus the
  runner-up candidate when the match was ambiguous — this line is what
  lets the user redirect before anything is written.
