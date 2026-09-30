# QA Service code analysis vs ep-qa-pipeline — 2026-09-30

**Scope.** A read of the qa-service **source code**
(`C:\media-files\Coding\qa-service`, branch `feat/defect-caller-report`
@ `d773ff1`, 898 commits since 2026-06-23). The questions are how the
service works, what the pipeline could borrow from it, and which service
gaps are worth fixing. This builds on
`QA-SERVICE-INTEGRATION-REVIEW-2026-09-14.md`, which judged the MCP
surface from the outside. This review reads the code behind it.

**Method.** Five parallel read-only deep-dives covered:
1. requirements and case design;
2. runs, CI, defects and UAT;
3. implement, discover, link and code-sync;
4. the MCP surface, security and architecture;
5. how this plugin uses the service, mined from the CHANGELOG and docs.

No files were changed and no MCP calls were made. Every claim is backed
by a `file:line` in the qa-service tree. Claims marked **✔** were
re-checked by hand in the code for this report. The rest were checked by
the reviewing agent against the code but not re-read here.

Paths below are relative to the qa-service root unless they start with
`skills/` (this plugin).

---

## 1. Verdict in eight lines

1. **qa-service is a serious piece of engineering** (≈87 k LOC, about
   3,200 tests, 128 MCP tools). Its best ideas are *mechanical honesty
   devices*:
   - citations built by the code, not the model;
   - tri-state `resolved` links;
   - plan-hash consent tokens;
   - supersede-never-overwrite verdicts;
   - model-free source-change detection;
   - an independent evidence-auditor agent spec.

   Several map straight onto this pipeline's false-pass problem.
2. **Four verified bugs make the service's own "green" untrustworthy**:
   - UAT sign-off grades itself, because the auditor never runs (✔).
   - The CI "latest verdict" is decided by ingest time, so a backfill lets
     old reports win (✔).
   - Full-mode case generation silently drops cases past 25 requirements
     (✔).
   - A "verified" test link means the file exists; the test name is never
     checked, an unmerged PR counts, and a red test counts (✔).
3. **The service repeats the false pass our pipeline was built to
   prevent.** An agent claiming `implemented` with an empty ref flips the
   case to implemented (`lib/server/implementTests.ts:446-451`). Keep
   treating every service-side `implemented` / `resolved` / `verified` as
   a *claim*.
4. **Your `d773ff1` (not merged yet) retires most of our 0.43.6 bug
   workaround.** `record_case_result` now takes `defect.file:false`,
   `defect.jiraKey` and a caller-written report filed as the caller.
   There are three edge cases to know about before we rely on it (§4.2).
5. **The MCP client pain has concrete code causes.**
   - There are no tool annotations anywhere. That explains the
     `register_review_status` "write" refusal.
   - `principal` is taken from the caller as given; the verified identity
     is ignored.
   - `source` defaults to `manual`.
   - There is no batch record tool, although the bulk method exists and
     CI uses it.
   - `get_suite` has no size bound and is pretty-printed.
6. **Security is the weakest area.**
   - Agents run with `bypassPermissions` and the worker's full environment,
     including GitHub, SSH, Claude and AWS credentials (✔).
   - Extraction runs `claude -p` with no tool restriction over unfenced
     Jira text.
   - One anonymous `MCP_TOKEN` grants all 128 tools.
   - The tests never run in CI; every push to main deploys (✔).
7. **Where the pipeline is stronger:**
   - reading Jira comments, AC fields and attachments (the service reads
     summary and description only);
   - keeping both versions of a conflict;
   - the grounding rule for expected results (the generator sees only
     title + summary);
   - the rich verdict vocabulary;
   - positive-control absence checks;
   - the open-items ledger.

   These are worth proposing to the service.
8. **Recommended next moves** (§8):
   - adopt 4 service ideas into the plugin: an auditor stage, plan-hash
     confirmation, fencing, quote verification;
   - change 5 pipeline rules because of what the code revealed;
   - file ≈12 service fixes, most of them small.

---

## 2. What qa-service is, in one page

| Layer | What | Where |
|---|---|---|
| Web + API | Next.js 14, Postgres (45 tables, 58 migrations applied at first DB use), Google SSO | `app/`, `lib/server/db/schema.ts`, `middleware.ts` |
| Library | products (config constant, no table) → suites → folders → cases; requirement registers (rule / invariant / risk / fr / nfr / oq / discrepancy); trace edges | `lib/server/testSuiteStore.ts` (3,540 lines) |
| AI steps | `execFile('claude', ['-p', prompt, '--model', m, '--output-format','json'])` — no SDK, no schema mode. Opus for collect/generate, Sonnet for review/revise/import, Haiku for suggest | `lib/server/suiteImport.ts:691-729`, `app/config/aiModels.ts` |
| Provenance | the model names block + locator + verbatim quote; the code builds the URL and verifies the quote | `lib/server/requirementSources.ts` |
| Review gate | rubric skill pasted verbatim with its digest; approve mints a hash-locked version; re-approval raises impacts on covering cases | `registerReview.ts`, `registerVersionStore.ts` |
| Source watch | sha256 of the re-fetched text; re-locate each verified quote; `stale_quote` / `new_material` | `lib/server/sourceWatch.ts` |
| Runs | fixed roster, `not_run` stored, supersede-with-link, one current row per (run, case) | `lib/server/testRunStore.ts` |
| Defects | a `fail` files a Jira bug after the verdict commits; dedupe on `[stableId]` in the summary | `lib/server/testRunDefects.ts` |
| CI | JUnit / reports-server ingest, strict join ladder (declared id → exact ref), worst-leg-wins | `lib/server/ci/*` |
| Repo side | discover (code→cases), implement (cases→test PRs by agents), link, code-sync (tags only), scaffold | `discoverTests.ts`, `implementTests.ts`, `mcp/workOrder.ts` |
| Agents | 9 test implementers, tag-backfill, `uat`, `uat-evidence-auditor`; 10 `.claude/rules`; 21 authoring skills (the docs say 17) | `.claude/` |
| Worker | `worker-stub/server.mjs` **is** the production worker (the Fargate entrypoint runs it). One batch at a time; Fargate RunTask per implement chunk | `Dockerfile.worker`, `scripts/worker-entrypoint.sh` |
| MCP | 128 tools, a self-documenting manual (29 topics), consent tokens for implement only | `lib/server/mcp/*`, `.claude/mcp-manual.md` |
| Delivery | 2 main authors, 76 % of commits Claude-co-authored, push to main → build → deploy; **tests are not run in CI** | `.github/workflows/deploy.yml` |

---

## 3. Side by side

| Capability | qa-service | ep-qa-pipeline | Stronger |
|---|---|---|---|
| Requirement intake | Jira summary + description, 2 levels of children, capped at 60 and silently truncated; Confluence page; KB; uploads. **No comments, AC fields, attachments or links** (`app/lib/jira-client.ts:153-245`) | description, comments, AC fields, attachments, linked Confluence; AC ledger with ids and a count check | **pipeline** |
| Provenance | code-built links, quote verification, unverified quotes kept and flagged | verbatim `Clause:` lines, AC ids on every REQ/case, `sources[].quote` sent | **service** (mechanical); pipeline has the data but no checker |
| Conflicts | resolved by assertion (spike 0.43.3) | kept as `(unresolved conflict)`, both versions asserted | **pipeline** |
| Case design | 25 requirements per batch, sees only `[id] (kind) title — summary`; only the level section of the planning skill injected; no atomicity or format rules | technique by type, BVA/pairwise by risk, one focus per case, banned words, grounding rule, one `[core]` per REQ | **pipeline** |
| Level routing | detailed surface/level rules, "leave unrouted rather than guess" | channel tags `[UI]`/`[API]`/… as routing hints | service for automation levels; pipeline for execution |
| Review of the register | rubric codes (UNTESTABLE, AMBIGUOUS, COMPOUND, NO-ORACLE, WRONG-LEVEL…), versioned, digest-stamped | grooming's 4 questions, SPEC/BEHAVIOUR classes, recon answers BEHAVIOUR | complementary |
| Change tracking | hash + quote re-location, explicit baseline adopt | source register rebuilt per run, retest scope built from the suite | **service** (mechanism); both have blind spots |
| Execution | none by the service itself (UAT agent aside); CI ingest | code review, API via curl, UI via Playwright, guided manual walk, RC smoke | **pipeline** |
| Verdict model | 6 verdicts, supersede chain, URL-only evidence, optional even for pass | ≈17 statuses, evidence class, `Source:` + `Clause:` on every FAIL, positive controls | **pipeline** (the service flattens it) |
| Evidence audit | an excellent auditor *spec*, **never run** (§4.1-A) | run-analyzer's evidence-quality bucket; no independent re-open of screenshots | neither in practice |
| Defect filing | auto on `fail`, per-project field map, caller identity (after `d773ff1`) | EP bug form, filed by the operator, two-wave | converging |
| Cross-round memory | versions + impacts on the register | open-items ledger, carried-risk rows | complementary |
| Write safety | consent token for implement; everything else from echo-prefix to nothing | confirmation pauses, destructive tools forbidden, `git_guard.py` hook | pipeline in discipline, service in mechanism |

---

## 4. Service gaps worth fixing

The ranking favours "silently produces wrong data" over "is inconvenient".
Each item has a suggested fix.

### 4.1 Correctness: the service's own green can be false

**A. UAT sign-off grades itself (✔).**
- In real-agent mode `worker-stub/server.mjs:502-519` never starts
  `uat-evidence-auditor`. It relabels the UAT agent's own final JSON:
  confirmed→SUFFICIENT, defect→INSUFFICIENT, unverified→UNVERIFIABLE, and
  `auditOverall='ready'` iff every item is confirmed.
- `lib/server/signoff.ts:18` accepts it, because
  `hasAudit = Boolean(auditRef || verdict)`.
- This is exactly the self-graded pass that QAS-RISK-06 and SIGN-02 name.
  UNVERIFIABLE does not block `ready` either (`signoff.ts:35`).
- *Fix:* spawn the auditor as a second process over the evidence dir.
  Require `auditRef` (not just `verdict`) in `hasAudit`. Block on
  UNVERIFIABLE at the release-gate bar.

**B. CI "latest verdict" follows ingest time (✔).**
- `recordResults` stamps `recordedAt = new Date()`
  (`testRunStore.ts:748`).
- `app/lib/executed-tier.ts:81` picks the latest verdict by `recordedAt`.
- `ci/backfill.ts:115` syncs newest first, so the **oldest** report is
  written last and wins the case dots, `get_test_case.lastResult` and the
  unscoped executed tier.
- A re-sync of an old report can override a newer manual verdict. This is
  the ingestion-lag trap from our `provisioning-rules.md`, built into the
  service.
- *Fix:* store `executedAt` from the report or run, order by it, and never
  re-supersede an unchanged verdict on re-sync.

**C. Full-mode generation drops cases past 25 requirements (✔).**
- Each 25-requirement batch is told to mint `${prefix}-TC-01…`
  "sequentially" without the ids earlier batches used
  (`suiteImport.ts:567`, `:1391`).
- `remintTakenIds` runs only in gaps mode (`:1418-1421`).
- `dedupeByStableId` (`:265-269`) then keeps the first of every
  colliding id and silently drops the rest along with their trace
  edges. The dropped requirements read "uncovered" with no error.
- *Fix:* pass the minted ids forward between batches and re-mint in both
  modes.

**D. "Verified" test links prove little (✔ for the first three).**
- For `landing:none`, the default, `refVerify.ts:95-123` checks only that
  the **file** exists. `::testName` is never checked.
- `app/lib/impl-ref.ts:47-65` fuzzy-resolves a missing path by basename
  and *prefers non-test files*.
- `isVerifiedLink` (`app/lib/test-suite-types.ts:429`) ignores
  `at`/`prNumber`, so a link pinned to a declined PR stays green forever.
  Merge polling exists only for tag PRs.
- `testsGreen` and per-case `outcome:'fail'` are parsed and never read.
- An `implemented` claim with an empty ref, or with no verifier
  credentials, still flips the case to implemented
  (`implementTests.ts:446-463`).
- *Fix:* check the test name in the file; count PR-pinned links only
  after merge; refuse `implemented` without a verified ref; record
  `outcome` and let a red test read `partial`.

**E. Doc-pack re-import wipes the approval ledger.**
- `replaceSuiteContent` deletes and re-inserts every requirement
  (`testSuiteStore.ts:1530-1541`).
- Versions, reviews, impacts and sources cascade on `requirements.id`
  (`schema.ts:453,491,600,1538,1589`).
- `applyImportedMeta` can also rewrite the suite prefix, and there is no
  unique index on (product, prefix).
- The `start_import_docs` description mentions neither.
- *Fix:* upsert by stableId instead of delete+insert, and put a consent
  token on the tool. (Our ban on `start_import_docs` stands and now has a
  second reason.)

**F. Discovery marks tests "gone" on a partial scan.**
- `applyDiscovery` (`discoverTests.ts:103-137`) applies `plan.gone` even
  when `rateLimited`, `failedReads` or `truncated` (the 200-file cap) is
  set.
- Authored cases are never marked stale, and no job re-verifies
  `resolved`, so it never decays.

**G. Run history is append-only only while the run survives.**
- Verdicts can be re-recorded on `completed` and `closed` runs
  (`testRunStore.ts:870`).
- `DELETE /api/test-runs/{id}` hard-deletes all verdicts, even on
  release-attached runs (`:1566-1574`).
- `releaseId`/`env` are editable after close with no trail (`:1542`).
- The status write in `recordResult` can overwrite a concurrent close
  (`:945-954`).

**H. Roll-ups miscount.**
- `/api/releases/[id]/test-status` sums runs instead of taking the latest
  verdict per case. A corrected fail still reads failing, and
  `flaky`/`known_defect` are left out.
- `flaky` is counted in no executed-tier bucket
  (`executed-tier.ts:189-193`).
- Aborted runs count toward coverage.
- A `skipped` verdict closes the "never executed" gap.

**I. Requirements collection loses data quietly.**
- One enum slip, e.g. `priority:"P3"`, throws away a whole 40 k-char chunk
  (strict array parse, `suiteImport.ts:1114`), and the run still reports
  `ready`.
- A re-collect overwrites human-edited requirement text by stableId
  (`testSuiteStore.ts:1638-1665`).
- `toSuite` shows `failed` as `ready` once a suite has rows
  (`:139-173`).

**J. The review gate can fail open.**
- An unknown severity is downgraded to `minor` (✔,
  `registerReview.ts:434-438`; deliberate, but "Critical" or
  "Blocker " then pass).
- Findings are cut to 12 *before* normalisation (`:426`), so a blocker in
  position 13 vanishes.
- An AI `approve` mints the version with no human step.
- Approving a case clears impacts raised *after* its review.

### 4.2 Gaps that hit this pipeline directly (MCP-client view)

| # | Gap | Code | What it costs us | Fix |
|---|---|---|---|---|
| 1 | **Defect filing, after `d773ff1`** — most of our 0.43.6 ask is now built: caller-written report, EP bug-form fields as ADF, filed as the caller when they have connected Atlassian, `file:false`, `jiraKey`. Remaining issues: **(a)** `defect.jiraKey` is silently dropped when the product's `defects.autoFile` is off (the gate at `testRunStore.ts:966` wraps the whole defect path); **(b)** dedupe matches the whole token in key + summary only (`testRunDefects.ts:354-356`), so a hand-filed bug naming the id only in its body gets a duplicate; **(c)** verdict `evidence[]` is never passed into the bug (`testRunStore.ts:973-986`); **(d)** "on behalf of" prefers the self-declared principal (`testRunDefects.ts:543`); **(e)** the fallback body is still a case dump | as cited | we can retire "file first, then record `fail`", but (a) decides whether `jiraKey` works on EP at all | apply `jiraKey` / `file:false` regardless of `autoFile`; search the description too; pass evidence; take "on behalf of" from `verifiedPrincipal()` |
| 2 | **No tool annotations** — no `readOnlyHint` / `destructiveHint` anywhere under `lib/server/mcp` | `lib/server/mcp/tool.ts` | the auto-mode classifier blocked `register_review_status` (a read) in the 09-14 review; nothing separates reads from destructive tools | annotate all 128 |
| 3 | **Attribution** — the MCP `principal` is taken from the caller and stored even when a verified email exists (`runTools.ts:144`); `source` defaults to `manual` (✔ `testRunStore.ts:894`); `approve_register_entry` is always `'unattributed'` (✔ `reviewTools.ts:194` passes no principal) | as cited | we pass both, so we are safe, but a hand call without `source` records a machine verdict as a human one | default principal to the verified email and store both; one-line fix for override |
| 4 | **No batch verdict tool** — `recordResults` (500-row transactions, used by CI) is not exposed | `testRunStore.ts:727` | 60+ single calls per pass, then a re-read to verify (retro EP-47675 F8) | expose `record_case_results`, returning per-case `rejected` |
| 5 | **`create_test_run` takes UUIDs only**; add, remove and record take stable ids | `testRunStore.ts:315` | a `search` per case before every run (0.44.0 🟡, 0.46.0 docs) | resolve stable ids in `create` |
| 6 | **Unbounded reads** — `get_suite` returns the whole suite plus implement history with no field selection; `list_test_runs` and `list_uat_runs` are unpaged; everything is pretty-printed with indent 2 | `handler.ts:137`, `testRunStore.ts:616-637` | the 190 KB `list_suites`, `get_suite` without `detail` (0.38.0) | `include`/`fields`, a `ticket` filter on `get_suite`, pagination, compact JSON |
| 7 | **No neutral retraction** — no "retracted/unknown" verdict, no reason field on supersede; cross-run overturns are not reconciled | `app/lib/test-run-types.ts:14,35` | a human "machine PASS invalid, not re-tested" must be `blocked` or `skipped` | a `retracted` verdict plus `supersedeReason` |
| 8 | **Evidence** — URL-only, optional even for `pass`; adding a link means re-recording the verdict; no upload | `app/lib/evidence-url.ts:121-146` | the RC smoke re-records every verdict to add a link (0.46.0); laptop paths in notes (0.43.2) | an `append_evidence` tool; an optional per-product "pass needs evidence" rule; an upload tool (UAT already has one internally) |
| 9 | **`env` is free text, compared exactly and case-sensitively** | `executed-tier.ts:75`, `runTools.ts:91` | `rc` ≠ `RC` ≠ `alpha2`; scoped coverage splits silently | normalise, or a per-product env enum |
| 10 | **No idempotency keys** on `create_*` | `mcp/tools.ts` | a retried create without a stableId duplicates | `clientRequestId`; meanwhile we always pass explicit stableIds and prefixes (we do) |
| 11 | **Errors lose their status** — `TestRunError(…, 404/409)` reaches the client as text only | `handler.ts:140-153` | we tell not-found from conflict by parsing prose | `{code, message}` |
| 12 | **Tool results are not fenced** — `untrusted.ts` is used in 2 places only; `list_feedback_replies`, `list_source_impacts`, `find_repo_rules` and case text come back raw | `handler.ts:82,137` | our stages read other teams' Jira text through the connector unfenced | fence free-text fields in results |
| 13 | **Releases** — no `create_release`; `releaseId` is fixed at run creation (web `update()` can change it, MCP cannot) | `testRunStore.ts:1542` | 🟡 [Environment] on every run whose fixVersion has no release | `create_release` from a Jira fixVersion; an MCP `update_test_run` with an audit trail |
| 14 | **Jobs run inside the web process** (`void fn()`) — ≈10 deploys a day orphan them; reapers are triggered by page views and kill live runs (import 15 min vs up to 30 min of retries; Mode C implement 30 min vs a 60-min budget); no `cancel_job` or rate limit (both promised in the agent-tools spec §8.3) | `agentTools.ts:268…`, `testSuiteStore.ts:1043,1455` | a `start_*` we start can report failed while it is still writing | a real queue, or at least heartbeats inside the retry loop |

### 4.3 Security

Ranked by blast radius. Tell the service owners before anything else in
this report.

1. **High: agents with a full secret environment and no permission gate
   (✔).**
   - `worker-stub/server.mjs:415-420` and `:776` spawn
     `claude … --permission-mode bypassPermissions` with
     `env: process.env`.
   - That environment holds `GITHUB_TOKEN`, `GIT_SSH_KEY`, the Claude
     token, the worker token and the ECS task-role credentials.
   - Agents have Bash, WebFetch and WebSearch.
   - Case text (from Jira, doc import and AI generation) is pasted
     **unfenced** into `buildPrompt` (`implementTests.ts:122-139`).
   - A prompt-injected case can therefore exfiltrate credentials.
   - *Fix:* give the child a minimal environment, an egress allowlist,
     short-lived scoped tokens, fencing in `buildPrompt`, and drop
     WebFetch from implementers.
2. **High: an unrestricted extraction agent.**
   - Collect, generate, review and revise run `claude -p` with no
     `--allowedTools` / `--max-turns` / `cwd` over unfenced Jira and
     Confluence text (`suiteImport.ts:691-708`).
   - The `===== label =====` source delimiter can be spoofed from a Jira
     description, which shifts provenance.
   - *Fix:* use `--tools ""` or an SDK call with no tools, a temp cwd,
     fencing, and pass the prompt on stdin (argv also risks E2BIG; the
     code's own comment cites 80 KB prompts).
3. **High: authentication without authorisation.**
   - The shared anonymous `MCP_TOKEN` is checked first and wins even with
     OAuth on (`mcp/authorize.ts:31-63`).
   - There are no roles; every caller gets deletes, `register_repository`
     and implement.
   - The consent-token HMAC key falls back to `MCP_TOKEN`
     (`mcp/signing.ts:28`), which every client holds.
4. **Medium: fail-open configuration.**
   - A blank `AUTH_SECRET` falls back to a public constant (✔,
     `lib/auth/secret.ts:6,15`).
   - SSO is off unless all `AUTH_GOOGLE_*` are set.
   - An empty `AUTH_ALLOWED_DOMAINS` admits any Google account.
   - With SSO off, `x-qa-tester` selects whose stored Atlassian
     credential is read or overwritten (`lib/server/principal.ts:39`).
   - The worker accepts any bearer token when `AGENT_WORKER_TOKEN` is
     unset (✔, `server.mjs:873-876`).
5. **Medium: no gate before deploy (✔).**
   - `.github/workflows/deploy.yml` builds and deploys on push to main.
     The ≈3,200 tests, CRED-01 (`scripts/scan-token.mjs`) and any secret
     scan never run.
   - `docs/release-management/testing.md:82` claims CRED-01 runs in CI.
6. **Medium: no audit trail.** `mcp_tool_call` logs carry no user or
   request id, and there is no audit table. A `delete_test_cases` of 500
   ids (no confirmation, `structureTools.ts:307`) cannot be tied to a
   person.
7. **Low:**
   - agent-written `.html` evidence is served from the app origin with no
     CSP;
   - the Google token cache has no eviction;
   - the KB dev token is committed as a default (`app/config/env.ts:104`);
   - `CREDENTIAL_SECRET`, `EVIDENCE_ALLOWED_HOSTS` (empty = any host) and
     `IMPLEMENT_FARGATE_*` are missing from `.env.example`.

---

## 5. What the pipeline should borrow

Ranked by false-pass prevention per unit of effort. Each idea names where
it would land in this plugin.

| # | Idea | From | Lands in | Effort |
|---|---|---|---|---|
| 1 | **An independent evidence auditor**: a separate, read-only pass that trusts only artifacts on disk. It re-opens every cited screenshot (blank, cropped, wrong page), re-issues cited GET-only calls, and keeps a contradiction ledger (the final conclusion must be the evidenced one), an orphan-vs-missing artifact diff and full claim coverage. Each claim gets SUFFICIENT / INSUFFICIENT / UNVERIFIABLE against a named bar, with a remediation list naming the artifact that would close each gap. It must never backfill evidence itself. **Actually run it**, unlike the service. | `.claude/agents/uat-evidence-auditor.md` | new step between web-testing and the wave-1 publish, or a mode of `qa-run-analyzer`; spawned as a fresh subagent so it does not share the tester's context. A PASS whose claim is INSUFFICIENT becomes BLOCKED (unverified) | M |
| 2 | **Plan-hash confirmation** for every outward write: hash the exact preview (comment body, keys, field set, roster ids), store the hash in the run folder, and refuse the write if the payload changed between confirm and send | `lib/server/mcp/consent.ts`, `signing.ts` | the publish pause (`qa-pipeline-docs`), wave-1/2 Jira posts, `qa-manual-results` write-back. A small script, e.g. `scripts/plan_hash.py` | S |
| 3 | **Fence untrusted text**: `<<<UNTRUSTED <label> … UNTRUSTED>>>` with the terminator neutralised inside the content | `lib/server/mcp/untrusted.ts` (40 lines, tested) | `task-context` (Jira and Confluence bodies, comments), `pr-summary` (PR descriptions, commit messages), any `list_feedback_replies` read | S |
| 4 | **Mechanical quote verification**: whitespace- and case-insensitive substring search of each `Clause:` / `sources[].quote` in the fetched source text; a miss is kept but flagged `unverified`, never silently dropped; a minimum length (the service lacks one: 3-word quotes "verify") | `requirementSources.ts:90-124`, `quoteAnchor.ts` | extend `reconcile_counts.py` or add a sibling script run at the count gate; source-fidelity bucket in the analyzer | S |
| 5 | **Tri-state code citations in code-review**: a PASS (code) citing `file:line` is re-checked (the file exists at the PR head, the symbol or line is present) before publishing; otherwise it reads "unverified", a distinct state | `refVerify.ts`, `reconcile.ts` (tri-state `resolved`) | `code-review` output check, run by script over `<KEY>-code-review.md` | S–M |
| 6 | **Model-free source change detection**: digest the source text (never its `updated` timestamp, which the service's own comments move) and re-locate each REQ's stored quote. A missing quote means the REQ is stale; long new uncovered lines are new material; adopting the new baseline is an explicit act | `sourceWatch.ts:110-234` | retest mode + the source register: replaces "re-fetch and eyeball". Or call `check_source_updates` directly, knowing its blind spots (§4.1: baseline at first check, unverified quotes unwatched, deletions and short changes missed) | M |
| 7 | **Review finding codes**: requirements: UNTESTABLE, AMBIGUOUS, COMPOUND, INCOMPLETE, UNMEASURABLE, CONTRADICTS, IMPLEMENTATION, UNSOURCED. Cases: NOT-VERIFIED, NO-ORACLE, FLAKY, WRONG-LEVEL, COMPOUND, TYPE-MISMATCH, UNTRACED. Severity phrased as consequence: "a tester reading this would ___" | `.claude/skills/requirement-review`, `test-case-review` | grooming's open-items classes; a self-review pass in `qa-test-cases` | S |
| 8 | **Methodology digest per report**: stamp the sha256 of the SKILL.md (+ references) each stage ran with | `mcp/workOrder.ts:69`, `registerReview.ts` | each stage report's header; lets the analyzer tie a malfunction to a skill version | S |
| 9 | **Failure classes**: boot / exec / **quota** / env / other, each with its next step, so a Claude usage cap is not read as a product defect or a BLOCKED | `app/lib/worker-health.ts:45` | `status-vocabulary.md` for BLOCKED reasons; analyzer | S |
| 10 | **Tool ladder** from the UAT agent: Playwright → curl → DB/log/mail → ask the human last; use the product's own primitives (download the real import template, don't hand-craft one) | `.claude/agents/uat.md` | `web-testing` / `qa-manual-runsheet` provisioning rules (partly there already) | S |
| 11 | **Honest truncation**: every capped list returns `count` + `truncated`, and every batch reports per-item `rejected` / `notFound` / `blocked` | `structureTools.ts:35` | publish verification, analyzer outputs | S |
| 12 | **Feedback grouping**: one comment per *destination document* (the child issue that holds the sentence, not the epic); only blocker/major findings; body-hash dedup; edit in place | `feedbackCompose.ts:25-83`, `feedbackSend.ts` | the `qa-refinement` questions comment when questions span child stories | S |
| 13 | **Rule files with a "floor" flag and the incident as the *why*** (e.g. destructive-commands: "autonomous runs have a fixed ceiling: branch · commit · non-force push · PR — so they never stall"). A one-line preamble pasted into every stage, with the full text cited | `.claude/rules/*.md`, `mcp/rulesPreamble.ts` | our hard rules are scattered through SKILL.md files; a shared `references/floor-rules.md` quoted at each stage's top would cut drift | M |

**Deliberately not borrowed:**
- **Service-side generation**: §4.1-C, plus the 0.43.3 spike's 19/27.
- **Self-approving AI review**: §4.1-J.
- **Rubric fail-open on unknown severity.** For us an unknown severity
  should block.

---

## 6. What the service should borrow from the pipeline

Worth proposing to the service owners, because each one closes a §4 gap:

1. **Read comments, AC custom fields, attachments and linked pages** in
   `jira-client.ts` (see `skills/task-context/references/field-maps.md`).
   The watch misses them for the same reason.
2. **Keep conflicts in two versions** instead of resolving them, and
   exclude `oq`/`discrepancy` from full-mode generation (`suiteImport.ts:1355`).
3. **Give the generator the source**: quotes, `detail` fields, priority
   and risk, not the 280-character summary. Add the grounding rule: no
   expected result the requirement text does not give.
4. **A richer verdict vocabulary**: a `retracted` verdict; a case-is-wrong
   verdict (SPEC-DEFECT is `skipped` + note today); an evidence class
   (code-read vs runtime vs reproduced-with-control).
5. **Positive-control absence checks** for any "not shown / not sent"
   assertion (`skills/api-testing/references/absence-check-protocol.md`).
   The UAT agent and auditor would benefit most.
6. **The open-items ledger** as a run-level object: risk rows that are
   not cases yet (`RISK-CR-*`), carried to the next run on the same
   ticket.

---

## 7. Changes this plugin should make now

These are prompted by what the code revealed. Each is small.

1. **Defect workaround after `d773ff1` merges and deploys.** This is a
   decision for you, not a mechanical change.
   - `test-runs.md:89-93,128-133` says "nothing in `record_case_result`
     suppresses" filing. After the merge that is false.
   - The two-wave rule still has a second reason: "no verdict shown to a
     human before the human round". A `fail` recorded with `file:false`
     is still visible on the run page.
   - Options:
     - **(a)** keep machine FAIL rows `not_run` in wave 1 and record
       stage-10 fails with `defect: {jiraKey}` or a full caller report,
       retiring "file first via Atlassian, then record";
     - **(b)** also record wave-1 machine FAILs with `defect.file:false`.
   - Before either, confirm EP's `defects.autoFile` is on. Otherwise
     `jiraKey` is dropped silently (§4.2 #1a).
   - Per CLAUDE.md, this rule came from the EP-56912 incident (0.30.0). Record the
     change and its reason in the CHANGELOG.
2. **Strengthen the `start_import_docs` ban** (`qa-service-publish.md:247-254`)
   with the second reason: it cascade-deletes versions, reviews and
   impacts, and can rewrite the suite prefix (§4.1-E).
3. **Add a `discover_tests` guard** if it is ever adopted: apply only when
   `rateLimited`, `failedReads` and `truncated` are all clean (§4.1-F).
4. **A read-only note in code-review / analyzer.**
   - A service `implemented` status, a `resolved:true` link, or
     `product_coverage.verified` are claims.
   - They mean "a file exists"; they do not mean the test exists, was
     merged or is green (§4.1-D).
   - They are never evidence for a verdict.
5. **Normalise `env`** to lowercase at every `create_test_run`: `rc`,
   `alpha2`, `alpha-<n>` (§4.2 #9). The RC smoke already writes `rc`, so
   write the rule down so another stage cannot drift to `RC`.
6. **Keep passing `principal` and `source` on every `record_case_result`**
   (we do: `test-runs.md:62-65,108`). Add one line saying why: the service
   defaults `source` to `manual` and stores `principal` exactly as given.

---

## 8. Suggested order of work

**Service side** (you have commit access; `d773ff1` is yours):
1. Security: minimal agent environment and fencing in `buildPrompt`;
   no-tools `claude -p` for extraction; `npm test` + CRED-01 in the
   workflow before deploy. (§4.3 #1, #2, #5)
2. Run the real auditor, and require `auditRef` in `hasAudit`. (§4.1-A)
3. Order verdicts by `executedAt`. (§4.1-B)
4. Carry minted ids across generation batches. (§4.1-C, one-line class)
5. `jiraKey` / `file:false` independent of `autoFile`; the
   `approve_register_entry` principal; default `principal` to the
   verified email. (§4.2 #1, #3, all small)
6. Tool annotations. (§4.2 #2)
7. `record_case_results` batch; stable ids in `create_test_run`.
   (§4.2 #4, #5)
8. `get_suite` field selection and a ticket filter; compact JSON.
   (§4.2 #6)

**Plugin side:**
1. §7 items 2–6 (docs-only, one patch release).
2. Borrow #3 (fencing) and #4 (quote verification script). Both are small
   and testable.
3. Borrow #2 (plan-hash confirmation).
4. Spike borrow #1 (the auditor) on the next code-phase run: run it over
   the stage reports and count how many PASSes it downgrades. Decide on
   that number.
5. §7 item 1 once `d773ff1` is deployed.

---

## 9. What was verified by hand vs reported

Re-read in the code for this report (✔):
- the UAT relabelling and `hasAudit`;
- `recordedAt = now` and the executed-tier sort;
- the backfill order;
- the generation batch/remint split and the dedupe drop;
- `refVerify` file-only for `landing:none`;
- `isVerifiedLink` ignoring the PR pin;
- `testsGreen` never read;
- the severity downgrade;
- `bypassPermissions` + `env: process.env`;
- worker auth open when the token is unset;
- `AUTH_SECRET` fallback;
- deploy workflow without tests;
- the `approve_register_entry` principal;
- the `source` default;
- the `d773ff1` defect input and its `autoFile` gate.

Everything else was checked by the reviewing agent against the code at
the cited lines, not re-read here. These are the items to re-check
before filing, because they depend on runtime behaviour:
- §4.1-E: whether the cascade happens on real Postgres. FKs are declared
  `onDelete: cascade`.
- §4.2 #14: the reaper timings in practice.
- §4.3 #2: whether `claude -p` read-only tools need no permission in this
  CLI version.
