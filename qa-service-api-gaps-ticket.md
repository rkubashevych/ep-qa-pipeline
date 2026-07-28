# QA Service MCP — write-API gaps that leave programmatically published suites half-empty

**Type:** Task · **Component:** QA Service (MCP connector / write API)
**Reporter:** Roman Kubashevych · **Raised:** 2026-07-28

## Context

`ep-qa-pipeline` (Claude plugin) now publishes its groomed requirements
and generated test cases into QA Service over the MCP connector, so a
ticket's test design lands in the team's system of record instead of a
Jira comment. First real publish:
`common/enhancing-privacy-for-opted-out-users-favouriting-features-a`
(prefix PRIVFAV, 41 requirements / 89 cases).

Comparing it field-by-field against an importer-built suite
(`common/account-interactions`, ACINT — 43 requirements / 17 cases)
shows the MCP write path cannot reach several fields the importer
populates. The pipeline data itself is fine — the cases have
goal/steps/assertions/preconditions and techniques on 100% of records
(ACINT has empty `steps` on 14 of 17) — but the suite renders as a
second-class citizen in the UI.

Suites for reference:
https://qa-service.expoplatform.com/expoplatform/test-suites/common/enhancing-privacy-for-opted-out-users-favouriting-features-a
https://qa-service.expoplatform.com/expoplatform/test-suites/common/account-interactions

## Gap 1 — `levels` cannot be written or derived (highest impact)

Neither `create_test_case` nor `edit_test_case` exposes the `levels`
array, and the server does not derive it from `levelText`.

Tested directly on PRIVFAV-03: `edit_test_case` with the exact canonical
`levelText: "API-E2E"` → `levels` stayed `[]` (confirmed by a fresh
`get_test_case`). Across the suite, `levels: []` on 89/89 cases.

Consequences:

- `stats.byLevel` reads 0 across all nine level rows while
  `totals.total` reads 89 — the per-level dashboard is dead on arrival
  for any MCP-published suite.
- `implementableLevels` for this product is `["U","I","AE","C"]`, matched
  against `levels`. With `levels` empty, **no pipeline-published case is
  eligible for the implement workflow** (`plan_implement_tests` /
  `next_implement_batch`), so automation can never pick them up.

**Ask:** accept `levels` on `create_test_case` / `edit_test_case`, or
derive it server-side from a canonical `levelText` (the label→code map
already exists in `stats.byLevel`).

## Gap 2 — no `edit_requirement`; requirement `detail` and `priority` unreachable

`create_requirement` accepts only `suiteId`, `kind`, `title`, `summary`,
`stableId`. There is no edit tool at all, so a requirement is immutable
once written and its structured content can never be set.

Evidence: PRIVFAV has `detail: {}` and no `priority` on 41/41
requirements. ACINT populates 8 `detail` keys — `type`, `related`,
`implements`, `constrainedBy`, `enforces` (relationships) and `impact`,
`likelihood`, `threatens` (risk model) — plus `priority` on 38/43, and
derives 58 requirement→requirement trace links from them.

`summarize_requirement` does not help — it makes things worse, and
because there is no `edit_requirement`, its damage is permanent.
Tested on PRIVFAV-FR-02: it overwrote `title` ("An opted-out favourite
is added to the user's **own** favourites list exactly like a regular
favourite") with the label "Opted-out favouriting parity", and wrote a
summary that contradicts the suite's own invariant ("…managing saved
items identically to regular users", when the feature's whole point is
that an opted-out favourite is NOT identical: no notification, no
connection row, no lead). The `[risk: …]` marker was dropped too. There
is no way to restore the original text.

`kind`, `priority` and every relationship also stay unreachable, and a
mis-classified `kind` or wrong `stableId` is permanent (e.g.
PRIVFAV-FR-37 is stored as an `invariant` behind an `-FR-` id).

**Additional ask:** make the destructive regenerate safe — either have
it write only `summary` when `title` is already populated, or require an
explicit `overwriteTitle: true`, or (best) ship `edit_requirement` so a
bad regeneration can be corrected.

**Ask:** an `edit_requirement` tool covering `kind`, `title`, `summary`,
`priority`, `detail` — or, at minimum, accept `detail` + `priority` on
`create_requirement`.

## Gap 3 — `traceLinks` not materialized for MCP-created cases

PRIVFAV: all 89 cases carry a populated `traceability` array pointing at
real requirement stableIds, yet the suite's `traceLinks` is `[]`. ACINT
has 112 links (54 × `satisfies` from test cases, the rest between
requirements). So requirement coverage and impact analysis read
"unlinked" even though the per-case data is there.

**Ask:** materialize `test_case → requirement` (`satisfies`) links from
`traceability` on write, or expose a rebuild action.

## Gap 4 — `create_suite` cannot set the suite header

`create_suite` takes only `title`, `productId`, `prefix`, `folderId`, so
a pipeline-created suite has no `summary`, `status`, `owner` or
`lastReviewed` — it lands in the list as a bare title while every
importer-built suite carries a description, owner and review date.

**Ask:** accept those fields on `create_suite`, or add `edit_suite`.

## Gap 5 (small) — undocumented / unenforced vocabularies

The pipeline wrote `status: "draft"` on 89 cases. `draft` is outside the
stats vocabulary (`planned` / `implemented` / `partial` / `deferred` /
`na`), so every readiness bucket read 0 against a total of 89 — with no
error and nothing in the tool description to indicate the allowed set.
Same class of silent failure for `levelText` labels and `techniques`
tokens.

**Ask:** document the enums in the MCP tool descriptions and/or reject
out-of-vocabulary values, so a bad write fails loudly instead of
producing a suite whose own dashboards contradict its contents.

## Suggested priority

1. Gap 1 (`levels`) — blocks dashboards **and** the implement workflow.
2. Gap 2 (`edit_requirement`) — the difference between a thin
   requirement list and the real requirement model.
3. Gap 5 (vocabularies) — cheap, prevents silent corruption.
4. Gaps 3 and 4 — cosmetic/analytical, lower urgency.

## Already worked around on the pipeline side

Canonical `levelText`, `status: planned`, kind-classified requirements
with kind-matching stableIds, aspect-segmented case ids,
behaviour-area folders, `detail.testData`/`tagPlan`, real `@tag` rows
attached via `tag_case`/`apply_auto_tags`. These are in
`ep-qa-pipeline` ≥ 0.10.3 —
https://github.com/rkubashevych/ep-qa-pipeline
