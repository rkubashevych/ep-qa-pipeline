# QA Service integration review — 2026-09-14

**Scope:** how `ep-qa-pipeline` 0.43.1 uses the QA Service MCP connector, and
which connector features it does not use — judged on fit, not on novelty.

**Method.** Read every plugin file that names a connector tool
(`qa-service-publish.md`, `test-runs.md`, the three orchestrators, analyzer,
task-context, runsheet, results). Read the connector's own manual
(`list_help_topics` → all 27 pages), the tag rule, the `test-case-review`
skill, `list_agent_actions`, and the tool schemas. Then checked the live
data: 128 suites, 205 test runs, 205 CI runs, 6 releases, 0 UAT runs, the
three runs the pipeline itself created (EP-53978 retest 3, EP-55950 r1,
EP-56739 r1), `coverage_report` / `executed_coverage` / `list_sources` on the
GSSQ, GSTOP and GSRCH suites, and the run folders `~/.ep-qa/runs/EP-55950`,
`EP-56739`. One read was refused by the Claude Code auto-mode classifier
(`register_review_status`, wrongly classed as a write), so the version-gate
state of the suites is unverified — see §5.

**Counts.** The connector exposes 118 tools. The plugin names 39. Of the
79 unnamed, 8 are worth adopting now, 6 are worth a spike, the rest are
either forbidden by an incident-born rule, out of the pipeline's job, or
not exposed over MCP yet.

---

## 1. Verdict in five lines

1. **The core integration is sound and now exercised.** Since the
   2026-09-10 coherence review said "no QA Service run was ever created by
   a pipeline run", two real passes have run end to end (EP-55950: 61-case
   roster, 35 machine + 26 manual verdicts, all 61 superseding correctly;
   EP-56739: 8-case bug-fix roster, `known_defect` and SPEC-DEFECT →
   `skipped` mapped as the rule says). Provenance (`sources` with
   `kind: jira / confluence / context`) is landing and is readable via
   `list_sources`. The five write-API gaps the plugin reported to the QA
   Service team on 2026-07-28 are all closed on the service side.
2. **Four rules no longer match the service** and cost something on every
   run (§3): `close_test_run` on a fully-recorded run is refused because
   the service auto-completes; `list_suites` is a 190 KB read called from
   four skills where `search` returns 1 KB; `create_suite` is documented
   without `teams`, so a new suite lands flagged "No team"; `evidence[]` is
   never populated, so every verdict's proof is a path nobody but this
   machine can open.
3. **Two cheap, high-value adoptions**: `coverage_report` (the analyzer
   currently derives requirement gaps by hand; EP-55950's run report spent
   a paragraph on what one call returns) and `sources[].quote` (the
   pipeline already quotes the clause verbatim in its `Clause:` lines; the
   service can store and re-verify it).
4. **One structural fact to decide on, not a bug:** `product_coverage`
   reads `verified: 0` for every pipeline suite and always will — "verified"
   means an implemented test whose ref resolves in a repo. The pipeline's
   contribution is visible only in the executed tier. Either accept that,
   or hand the AE/E2E cases to the implement workflow (§4.2).
5. **Reject, with reasons, the tempting ones**: service-side generation
   (`start_generate_test_cases` etc.), UAT (`commission_uat` is not exposed
   over MCP and overlaps stages 8–10), CI (`ci_run_status` results join to
   nothing today: `unjoinedCount 3906` on every observed run), code-sync
   and link (the pipeline writes no test code).

---

## 2. What is integrated well — evidence

| Area | Plugin rule | Live evidence |
|---|---|---|
| Requirements with structure | `create_requirement` with kind / priority / detail / cross-links / `sources`, one call each | GSRCH: 59 requirements, kinds spread (rule / invariant / risk / fr / nfr / oq / discrepancy), `traceLinks` built; `list_sources` shows 7 provenance rows incl. `kind: context` for a pr-summary section |
| Cases with levels | `levels` code array + `levelText`, aspect-segmented stableIds, folders of 5–8 | EP-55950 roster: 31 `AE`, 27 `E2E`, 3 `C`; 9 aspect segments; `stats.byLevel` non-zero |
| Runs as the verdict store | one run per pass, `principal` per row, `source: machine | manual`, re-record = retraction | EP-55950: 61/61 rows carry `supersedesId`; three principals (stage-6 agent, walk-witnessed agent, tester e-mail); `executed_coverage` moved 63 → 4 `neverExecuted` |
| Verdict mapping | SPEC-DEFECT → `skipped` + `discrepancy:` note; keyed FAIL CONFIRMED → `known_defect`; machine FAIL stays `not_run` | EP-56739 REG-04 `skipped` with the SPEC-DEFECT note; REG-03 `known_defect` naming EP-56739; `defects: []` (no machine `fail` filed a bug) |
| Two-question pause (F13 from the coherence review) | "Record the run?" separate from "Post the status line?" | implemented in `qa-pipeline-code` step 6; EP-56739 ledger row 15 shows the tester declining (b) while (a) was recorded |
| Suite as source of truth | step 0 reconciles local ↔ suite, suite wins | EP-55950 run report: "0 diffs across 378 comparisons" |

The July gaps ticket (`docs/specs/qa-service-api-gaps-ticket.md`) is fully
resolved: `levels` writable, `edit_requirement` exists, trace links build on
write, `create_suite` takes the header, and `status` / `priority` / `type` /
`kind` are schema enums (an out-of-vocabulary value is now rejected, not
silently zeroed). Mark that spec closed.

---

## 3. Rules that no longer match the service

### 3.1 `close_test_run` — the run cannot be "closed" once every row has a verdict

`test-runs.md` says stage 10 ends with `close_test_run mode: closed` and
"never leave a fully-ingested run `running`"; the analyzer and the
dispatcher look for `closed`. On EP-55950 the call was **refused**: the
service auto-completes a run the moment its last `not_run` row receives a
verdict, and `completed` is terminal. Both pipeline runs of 09-11 read
`completed`, not `closed`, and that is correct.

What `close_test_run` is actually for (its own description): ending a run
that still has `not_run` rows — `closed` keeps them unrun, `aborted` marks
the pass unfinished. So:

- `test-runs.md` "Stage 10 — the human pass": *completed (every row
  recorded) or closed (rows deliberately left unrun, e.g. a card the
  tester declared out of scope) are both terminal; call `close_test_run`
  only when rows remain `not_run` at the end of ingestion; `aborted` when
  the pass was abandoned.*
- Analyzer §4 and dispatcher state table: read `completed | closed` as
  "done", `running` + `stale: true` as "manual results never ingested".
- `qa-manual-results` step 4 and README stage-10b line: same wording.

### 3.2 `list_suites` where `search` belongs

`list_suites` for `expoplatform` returned 190,590 characters (3,860 lines)
this session — and the plugin calls it in `task-context` (suite lookup),
`qa-pipeline` (dispatcher step 1), `qa-service-publish.md` (suite
selection and procedure step 1), and the analyzer §4. Every one of those
reads is a "find the feature's suite" question. `search {query, kinds:
["suite"]}` answered "global search" with 7 hits in ~1 KB, ordered
exact-prefix first, and reports `total` so a truncated group is visible.

Adopt: `search` on the feature keywords (and on the prefix when the QA
sub-task names one) first; `list_suites` only when `search` returns
nothing, and then only to confirm "no suite". Note the limit in the rule:
`search` matches titles and IDs, not summaries — a suite whose title does
not name the feature needs the fallback. Files: `task-context/SKILL.md`
"Existing QA Service suite" step 1, `qa-pipeline/SKILL.md` step 1,
`qa-service-publish.md` Suite selection step 1 + Procedure step 1,
`qa-run-analyzer/SKILL.md` §4.

`search` also resolves a stableId to the row id that `get_test_case` /
`edit_test_case` take — the results stage's case-correction path
currently has no stated way to get that id.

### 3.3 `create_suite` without `teams`

The tool requires `teams` semantically ("a suite created without them is
flagged *No team* in the web UI until someone assigns them"; vocabulary:
Organizer | Exhibitor | Visitor | Mobile | Data Science | Integration |
Designers | Staff | Hyve). `qa-service-publish.md` Config and "Suite header"
list `summary / status / owner / lastReviewed` and never `teams`. Live:
`common/meeting-export` (MEXP, pipeline-created) has `teams: []`; the
Global Search suites carry `["Exhibitor"]`, presumably set by hand.

Adopt: map the suite path's role to a team (`exhibitor` → Exhibitor,
`visitor` → Visitor, `organizer` / `admin` → Organizer, `common` → the team
the story's dev sub-tasks belong to, ask at the pause if unclear) and pass
it in `create_suite`; add `teams` to the verify step 5 header check and to
the analyzer's "bare suite header" finding; `assign_suite_teams` repairs an
existing suite.

### 3.4 `evidence[]` is always empty

All 69 roster rows across the two runs have `evidence: []`. The notes say
`evidence: EP-56739-walk-results.md` — a path on one laptop. The service
accepts `{kind: screenshot | link | log, url, caption}` with an http(s) URL
on its host allowlist; `test-runs.md` already says a Jira URL or a jam.dev
link qualifies, but no writer does it.

Adopt (small): when a verdict has a Jira URL (the bug, the comment where
it was published, the ticket's AC page anchor) attach it as `link`
evidence; keep the disk path in the note. The screenshot itself still
cannot land — there is no upload tool — and that is worth a one-line ask
to the QA Service owners, because `$EP_QA_HOME/evidence/*.png` (0.43.1) is
now a flat store that would map cleanly onto an upload.

### 3.5 `releaseId` — the rule is right, the gap is upstream

EP-55950 carries `fixVersion: Prod 2026-09-23`; `list_releases` has no
release for it (newest: "RC 2026-08-26" ↔ `Prod 2026-08-26`), so the run
was created without `releaseId` exactly as the rule says. Consequence: the
verdicts cannot be scoped by release, and the release checklist (§4.3)
cannot see them. There is no `create_release` over MCP, and a run's
`releaseId` cannot be set after creation.

Adopt (one line, no tool change): the step-6 preview says `release: none —
fixVersion <X> has no QA Service release; ask <release owner> to create it
before the retest so the next run attaches`. The analyzer records the
same as a 🟡 [Environment] row, not a pipeline defect.

---

## 4. Unused features — triage

### 4.1 ADOPT NOW (cheap, closes a real gap, no new risk)

| Tool | What it replaces / closes | Where |
|---|---|---|
| `search` | four `list_suites` reads per pipeline (§3.2); stableId → row id | task-context, dispatcher, publish, analyzer, results |
| `coverage_report {suiteId}` | the analyzer's hand-derived "requirements with no case" list. Returns `gaps` worst-first (`uncovered` → `planned` → stale), `orphans`, `merges`, and the executed tier in one call. On GSSQ the EP-55950 report wrote a paragraph explaining 11 uncovered requirements; the call returns them by stableId and kind. Also belongs in publish verify step 5 (replaces the "traceLinks non-empty" heuristic with the actual gap list) | analyzer §4 (+ §1 coverage), `qa-service-publish.md` step 5 |
| `sources[].quote` (+ `locator`) on `create_requirement` / `edit_requirement` | the register's `Clause: "<verbatim>"` is already produced at grooming; storing it makes `list_sources` `verifiedCount` meaningful (today 0 on every pipeline requirement) and lets a reader check the claim without opening the page. `anchorUrl` is documented but `quote` is not | `qa-service-publish.md` Requirements mapping row "sources" |
| `teams` on `create_suite`; `assign_suite_teams` | §3.3 | publish Config + Suite header + verify step 5; analyzer bare-header check |
| `evidence[]` links on `record_case_result` | §3.4 | `test-runs.md` mapping table note column; step 6; results step 4 |
| `get_suite_tree` | the Config rule "reuse the `folderId` of an existing sibling suite found via `list_suites`" — the tree is where `folderId` comes from and shows the real hierarchy (`common` → feature folders; `organizer/payments/…`). Current pipeline suites are filed correctly, but the rule points at the wrong tool | publish Config "Folder" row |
| `get_test_run {historyFor}` | one call instead of `get_test_run` + `case_execution_history` when the results stage needs one case's chain | results step 2 (optional) |
| `close_test_run` semantics | §3.1 (a rule correction, not a new tool) | `test-runs.md`, analyzer §4, dispatcher, results |

### 4.2 SPIKE FIRST (real potential, real cost — do one deliberately, then decide)

**Versions / the AI review gate** — `review_requirement`,
`review_test_case`, `register_review_status`, `list_register_impacts`,
`revise_test_case`, `register_versions`, `register_version_diff`.

What it is: an approved, immutable snapshot of a requirement or case,
minted only when a fixed-rubric AI review passes (rubrics are the
`requirement-review` and `test-case-review` skills, digest-stamped on the
verdict). Approving a requirement at v2+ raises a **pending impact** on
every case tracing to it; a case cannot pass its own review while an
impact is unaddressed.

Why it fits: the pipeline's weakest cross-round mechanism is exactly this.
`qa-service-publish.md` says "changed requirements are edited in place";
nothing then tells the next round which cases the change invalidated —
EP-55950 ledger rows 1 and 3 (cases still `planned` against a retired
discrepancy version; titles stating a superseded behaviour) are the
symptom. The `test-case-review` rubric (NOT-VERIFIED, NO-ORACLE, FLAKY,
WRONG-LEVEL, COMPOUND, INCOMPLETE, TYPE-MISMATCH, UNTRACED,
STALE-VS-REQUIREMENT) is also a stricter, independent second opinion on
the docs phase than the analyzer's count-based checks.

Why not blind: each review is a minutes-long Opus call on the service, per
entry; a 60-case suite is an hour of server time. v1 raises no impacts, so
the loop only pays off from the second edit onward. And `list_register_impacts`
on GSRCH returned 0 — nobody on the team appears to use the gate yet, so
there is no precedent for how approvals are read.

Spike: after the next docs publish, run `review_requirement` on the P0
requirements and `review_test_case` on the `[core]` cases only (≈ 10
calls); read the findings; record in the CHANGELOG whether they caught
anything grooming missed. Adopt as an opt-in publish step ("review core
entries?") only if they did. `register_review_status` is the one-call
read to check where a suite stands; it was blocked by the auto-mode
classifier in this session, so run it from a normal session first.

**Implement workflow** — `plan_implement_tests` (dry run, changes nothing)
→ `start_implement_tests`.

Why it matters: `product_coverage` shows `verifiedPct: 0` on all 13
pipeline suites and will forever — verified = implemented + resolved ref.
The pipeline's 31 `AE` and 27 `E2E` cases on GSSQ are exactly what the
implement action selects on (monolith Codeception for `AE`, the
`e2e-testing` Playwright repo for `E2E`). Today they read as
"planned, never automated" on the team dashboard.

Why not blind: implementing pushes commits and opens PRs in shared repos
(effect class `outward`); it is a different job from verifying a ticket.

Spike: at the end of stage 10, when the human pass confirmed a case, offer
`plan_implement_tests {suiteId, level: "AE", stableIds: [the confirmed
AE cases]}` as a read-only plan in the final response — what would be
built, where, by which agent + skill, with the confirmation token. The
user decides whether to start it. Never `start_*` from the pipeline.

**`get_coverage {tags}` for retest scoping.** The retest tiers in
`run-modes.md` are judgement-based; the review's "there is no per-case
'files this case exercises' map" still holds. But the tag join gives a
cheap second signal: the cases in *other* suites that carry this feature's
tags are regression candidates a retest should at least list. Spike on
the next retest: one `get_coverage` call on the suite's tags, printed as
"related cases elsewhere", no execution.

**`discover_tests` preview** in code-review's closing step, as the
coherence review proposed — with two caveats the review missed and the
manual states: discovery reads the repo's **configured branch** (`alpha`)
from a cached snapshot, so a PR's own new tests on a feature branch are
invisible until merge; and only **one repo per product** is discoverable
(the monolith) — `portal-ui` / `admin-ui` tests cannot be found at all.
So the preview can answer "which existing monolith tests already cover the
paths this PR touches" (regression footprint), never "did this PR add
tests". Worth one try on a backend-only ticket; drop it if the footprint
adds nothing the `Behaviours touched` list did not.

**`ensure_release_checklist` / `get_release`.** The checklist is a
Sonnet-generated list of "Verify …" items per Jira key in the fixVersion
(RC 2026-08-26: 30 items over 12 tickets, `aiReviewed: false`,
`humanReviewed: false` on all). The pipeline produces far richer per-ticket
evidence than those items, and a run attached to the release would be the
natural proof — but only once the release exists (§3.5) and the checklist
items have no MCP write for "reviewed". Spike = read `get_release` for the
ticket's fixVersion at stage 10 and, if the ticket has checklist items,
quote them in the human summary as "release checklist items this pass
answers". No writes.

**`regroup_test_cases`.** Not in the manual; schema not inspected. The
publish reference's "cases piled into General → `create_test_case_folder`
+ `move_test_case`" repair might be one call. Check its description before
the next append to a legacy suite.

### 4.3 KEEP FORBIDDEN or REJECT (with the reason recorded)

| Tool(s) | Decision | Reason |
|---|---|---|
| `start_generate_test_cases`, `start_collect_requirements`, `start_import_docs`, `derive_suite_structure`, `scaffold_tests` | REJECT for pipeline suites | Service-side authoring competes with stages 2–4 and mints its own ids; `import_docs` is the one action that *replaces* content; 0.10.4 recorded `summarize_requirement` destroying pipeline text. The plugin's cases carry AC provenance, `[core]`, channel tags and the grounding rule — none of which the generator knows. Keep the UNVERIFIED warning in `qa-service-publish.md`. |
| `summarize_requirement` | KEEP FORBIDDEN | incident-born (PRIVFAV-FR-02) |
| `delete_*`, `merge_duplicate_case`, `remove_run_cases`, `untag_case`, `move_suite`, `rename_suite*` | KEEP FORBIDDEN | 0.37 rule: the pipeline never deletes or restructures shared data |
| `commission_uat`, `list_uat_runs`, `get_uat_run` | REJECT for now | `commission_uat` is `mcp.status: planned` (no tool); `list_uat_runs` is empty; the `uat` agent drives Playwright MCP and does what stages 8–10 already do, with less grounding. Revisit when exposed, as a possible *alternative* runner for stage 8, not an addition. |
| `ci_run_status`, `sync_ci_report`, `backfill_ci_reports`, `sweep_ci_dispatches` | REJECT for now | 205 observed CI runs, every one `junit:unit` on `alpha` with `unjoinedCount 3906` — the unit results join to no case. A pr-summary header line would report a green/red that says nothing about the ticket. Re-check when `unjoinedCount` drops. |
| `link_implemented_tests`, `plan_link_tests`, `*_link_batch`, `*_link_proposals`, `unlink_implemented_tests` | REJECT | the pipeline writes no tests and owns no test code; linking belongs to whoever authors the tests (the `registering` routine is for developers) |
| `*_code_sync*`, `start_auto_tag_propose`, `list_case_tag_approvals`, `accept_tag_suggestion`, `propose_tag`, `approve_tag`, `reject_tag_suggestion` | REJECT / human-only | code-sync writes `@tags` into repos; tag approval is "a human decision" per the tag rule; `apply_auto_tags` with `perCase` (already used) is the right write |
| `register_repository`, `set_test_source`, `detect_test_source`, `list_repositories`, `list_sources` (product form) | REJECT | plumbing for implement/link |
| `get_authoring_skill`, `get_skill`, `get_agent`, `list_skills`, `list_agents`, `list_agent_actions`, `get_rule`, `list_jobs`, `get_job` | N/A | the workspace behind actions the pipeline does not dispatch; `get_rule tags` is worth one read when the tag step is next edited |
| `get_help_topic` at run time | REJECT the review's "diff the vocab every run" | the schema enums now enforce the vocabulary; a drift fails the write loudly. Read the manual when editing the publish reference, not on every run |
| `suggest_test_case` | KEEP as is | already named "when available"; it needs a `folderId`, which the results stage can get from `get_suite` |
| `reopen_test_run`, `add_run_cases`, `run_defects`, `case_execution_history`, `executed_coverage`, `get_coverage` (named) | KEEP | already used correctly |

---

## 5. What this review could not verify

- **Version-gate state** of any suite: `register_review_status` was
  refused by the Claude Code auto-mode permission classifier ("External
  System Writes" — it is a read). Run it once from a normal session
  before deciding on §4.2.
- **`regroup_test_cases` semantics** — not inspected.
- **Whether `list_sources` `verifiedCount` checks the quote against the
  requirement's stored text or against the source document** — the
  description is ambiguous; the spike is to pass one `quote` and read the
  count.
- **EP-53978 retest 3** (2026-09-02, the off-book run) was not re-read;
  `test-runs.md` already documents its two mistakes.

---

## 6. Suggested order of work

1. **0.43.2 — rule corrections, no new mechanism:** §3.1 close semantics,
   §3.2 `search` first, §3.3 `teams`, §3.4 evidence links, §3.5 release
   preview line, `get_suite_tree` for `folderId`. Mark the July gaps spec
   closed. CHANGELOG dispositions for every row of §4.3 so the rejections
   are on record (MAINTAINERS rule 1).
2. **0.44 — the two reads:** `coverage_report` in the analyzer and publish
   verify; `sources[].quote`. Both are additive and testable on the next
   docs publish.
3. **Spikes, one per run, each with a CHANGELOG line:** versions gate on
   core entries → `plan_implement_tests` read-only offer →
   `get_coverage` on retest → `discover_tests` preview on a backend ticket
   → `get_release` quote at stage 10.
