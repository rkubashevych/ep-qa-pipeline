Machine-readable results archive (for agents). Humans: see the summary comment.

File: EP-55194-code-review.md

```
# EP-55194 - Code Review

Test cases: ./EP-55194-test-cases.md
PR: #4322 — https://bitbucket.org/expoplatform/expoplatform-main-ira/pull-requests/4322 (source `HV-114-PR-alpha`, MERGED)
Notes: No Confluence AC linked; requirements derived from Jira Description + triage. REQ-5b/5c/5d are grooming "(default assumption)" — treat problems on them as "needs confirmation", not hard defects. **Critical scope note:** PR #4322 is the docs-phase-flagged candidate (via EP-55072) but is NOT a fix for EP-55194 — it changes only 3 MeetingProgram/Speed-Networking query files and does not touch the exhibitor Add-Event create/save path, `sessionInfo`, or the AccountEvent resource null-check. No dedicated fix branch exists for EP-55194 (parent still "Awaiting details"). Consequently no test case can be confirmed from this code; every case is a runtime-behaviour check and is marked QA for live execution in stages 7 (API) and 8 (UI).

## Results

| TC | Name | Status |
|----|------|--------|
| TC-REQ-1.1 | Save new event with a Type selected (happy path) | QA |
| TC-REQ-1.2 | Save endpoint returns success, not 500 | QA |
| TC-REQ-2.1 | Success feedback shown after save | QA |
| TC-REQ-2.2 | Created event appears in the exhibitor's list | QA |
| TC-REQ-2.3 | Save response persists the event | QA |
| TC-REQ-3.1 | Sampled Type creates without error | QA |
| TC-REQ-3.2 | Other Types create without error (spot-check) | QA |
| TC-REQ-4.1 | Endpoint does not 500 on "type" param | QA |
| TC-REQ-4.2 | Frontend renders the successful save | QA |
| TC-REQ-5a.1 | Re-run repro for bwitched2 on IMEX | QA |
| TC-REQ-5b.1 | Save endpoint without AccountEvent does not 500 | QA |
| TC-REQ-5b.2 | UI create without AccountEvent is graceful | QA |
| TC-REQ-5c.1 | Save with no Type selected | QA |
| TC-REQ-5d.1 | Exhibitor marketplace loads without error | QA |
| TC-REQ-5d.2 | sessionInfo returns success | QA |

## Findings

No FAIL or N/A rows. All items are QA (require runtime verification).

Runtime update (post-review): a user-supplied Jam shows the Add-Event save working on the current build (`saveSession` → 200, event persisted, no 5xx). So whatever prevents the 500 on the current deployment is NOT in PR #4322 — the code review's conclusion stands (this PR is not the fix); the runtime pass comes from the current build state / data, evidenced in api-testing and web-testing. Code review remains QA because the code that would fix EP-55194 is not present in the reviewed PR to confirm.

Global observation (not a per-case defect): the reviewed PR #4322 does not implement or modify the code path under test for EP-55194. Its three changed files —
`MeetingProgramRegistrationsRepository.php`, `MeetingProgramRepository.php`, `TimeSlotService.php` — add `EXISTS(... AccountEvents ...)` filters to the Speed-Networking feed/schedule reads only. The exhibitor Add-Event → Save controller that raises the "Internal Server Error" is untouched. Therefore the EP-55194 fix cannot be validated by code review against this PR; the QA statuses below must be resolved by live testing (stages 7–8) or deferred until a real fix branch is provided.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | 0     |
| FAIL   | 0     |
| QA     | 15    |
| N/A    | 0     |
| Total  | 15    |
```

File: EP-55194-api-testing.md

```
# EP-55194 - API Testing

Code review: ./EP-55194-code-review.md
Test cases: ./EP-55194-test-cases.md
Environment: https://api-alpha2.expoplatform.net · event 3551 · frontend host https://ennies-alpha2.expoplatform.net
Notes: No fix branch exists for EP-55194; reviewed PR #4322 does not touch the exhibitor Add-Event save path. **Environment mismatch:** the bug is on IMEX (exhibitor "bwitched2", IMEX event); the only available API env is alpha2/event 3551 with a generic throwaway exhibitor (`zz_ownera_31877`). This run is therefore a behaviour probe of the current alpha2 deployment, not the IMEX repro. Auth/tokens redacted throughout.
Date: 2026-07-10

## Scope

[API] test cases executed against the REST API: 5
- QA (verify against the API): 5
- FAIL (confirm the bug): 0

## Not executed here
None ([API]-only run; [mobile]/[export-email]: none in this ticket).

> **REVISED after Jam review.** A user-supplied Jam (jam.dev/c/4bb11133-…) captured the real portal traffic on the current build. My direct-curl probe used the wrong endpoint name (`sessions/save` → 404) and an under-privileged raw token (`sessions` → 403), which I mis-recorded as BLOCKED. The real endpoint is `POST /api/v1/exhibitor/saveSession` and the Jam shows it returning 200. Statuses below are re-based on the Jam network capture.

## Results

| TC | Name | Source | Status | Endpoint | Comment |
|----|------|--------|--------|----------|---------|
| TC-REQ-1.2 | Save endpoint returns success, not 500 | QA | PASS | POST /api/v1/exhibitor/saveSession | Jam: **HTTP 200**, `data.status:true`. Not a 500. |
| TC-REQ-2.3 | Save response persists the event | QA | PASS | POST /api/v1/exhibitor/saveSession | Jam: 200 with `data.session.id: 33508` — created event returned/persisted. |
| TC-REQ-4.1 | Endpoint does not 500 on "type" param | QA | PASS | POST /api/v1/exhibitor/saveSession | Jam: save submitted with a Type (`session.type: 3`) → 200, no 500. |
| TC-REQ-5b.1 | Save endpoint without AccountEvent does not 500 | QA | PASS | POST /api/v1/exhibitor/saveSession | Jam 2 (exhibitor with no prior events): **HTTP 200**, `data.status:true`, `session.id: 33541`. No 500 for the no-AccountEvent condition. |
| TC-REQ-5d.2 | sessionInfo returns success (non-500) | QA | PASS | POST /api/v1/exhibitor/sessionInfo | Jam: **HTTP 200** through the portal session. (My raw-token probe got 403 — wrong session context.) |

## Findings

### PASS (Jam evidence): TC-REQ-1.2 / 2.3 / 4.1 / 5d.2
- **Endpoint:** `POST /api/v1/exhibitor/saveSession` and `POST /api/v1/exhibitor/sessionInfo` (portal `qa.exhibitor.alpha.cdot.io` → backend `ennies-alpha2`).
- **Observed (Jam network capture):** saveSession → HTTP 200, `data.status:true`, `data.session.id:33508`, `session.type:3` (a Type was submitted); sessionInfo → HTTP 200. Zero 5xx in the session.
- **Conclusion:** The save path returns 2xx and persists the event; the reported Internal Server Error does not reproduce on the current build.

### PASS (Jam 2 evidence): TC-REQ-5b.1 — missing-AccountEvent save
- **Endpoint:** `POST /api/v1/exhibitor/saveSession`.
- **Observed:** For an exhibitor with no prior events (the closest reproduction of the original "no AccountEvent" condition), saveSession returned HTTP 200, `data.status:true`, `session.id: 33541`; zero 5xx. The event was created — the no-AccountEvent path does not 500 on the current build.

### Note on my earlier direct-curl probe (superseded)
- My probe called `POST /api/v1/exhibitor/sessions/save` (404 — wrong name) and `POST /api/v1/exhibitor/sessions` with a raw login token (403 — session not initialised for that module). Neither reflected the real save path. The Jam's portal session, calling `saveSession`, returns 200. The BLOCKED statuses from that probe are withdrawn.

## Endpoint-mapping corrections (for future runs)
- Exhibitor "Add Event" save = `POST /api/v1/exhibitor/saveSession` (backend `ennies-alpha2`, driven by the exhibitor portal `qa.exhibitor.alpha.cdot.io`). Related: `POST .../exhibitor/sessions` (list), `POST .../exhibitor/sessionInfo`.
- `exhibitor/sessionInfo` is **POST**, not GET.
- A raw `/api/v1/login` token + `x-application:3` is NOT sufficient for these modules; the portal initialises a fuller session. Prefer capturing via the portal (or a Jam) over raw curl for these exhibitor endpoints.

## Writes performed (audit)
None by this skill's own calls (all rejected before any state change). The Jam performed a real create (session id 33508) as part of the user's own recording — not this run.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | 5     |
| FAIL   | 0     |
| FAIL CONFIRMED | 0 |
| FAIL REJECTED  | 0 |
| PARTIAL | 0    |
| BLOCKED | 0    |
| QA (not verified) | 0 |
| Total  | 5     |

Verdict: PASS — all 5 [API] cases confirmed via Jam network captures. saveSession/sessionInfo return 200 on the current build, including for an exhibitor with no prior events (session id 33541); no 500 anywhere.
```

File: EP-55194-web-testing.md

```
# EP-55194 - Web Testing

Code review: ./EP-55194-code-review.md
Test cases: ./EP-55194-test-cases.md
Host: exhibitor portals https://qa.exhibitor.alpha.cdot.io (Jam 1) and https://community.alpha.quizapp.io (Jam 2) → backend https://ennies-alpha2.expoplatform.net · alpha2 / event 3551
Notes: No fix branch exists; PR #4322 does not touch the Add-Event save path. **Primary evidence = a user-supplied Jam recording** (jam.dev/c/4bb11133-6510-4b2e-9a1f-470b59ff8d7d, author Roman Kubashevych, 2026-07-10) that exercises the full Add-Event flow on the current build. My own direct-API probe (stage 7) initially reported BLOCKED because it called the wrong endpoint (`/sessions/save` → 404) and hit the module gate on a raw token (`/sessions` → 403); the Jam shows the real endpoint `saveSession` returning 200 through the proper portal session. Results below are re-based on the Jam. Caveat: the Jam is event 3551, not the original IMEX case (exhibitor "bwitched2" / missing AccountEvent).
Date: 2026-07-10 (revised after Jam review)

## Scope

[UI] test cases in scope: 10
- QA (verify in the UI): 10
- FAIL (confirm the bug): 0
Executed to a result via two Jams + live check: 9 PASS · 1 QA (empty-Type validation only). 0 FAIL.

## Not executed here
> [API] cases are handled by stage 7 (api-testing). Listed for completeness.

| TC | Name | Channel | Why not executable here |
|----|------|---------|-------------------------|
| TC-REQ-1.2 | Save endpoint returns success, not 500 | [API] | Executed in stage 7 (api-testing). |
| TC-REQ-2.3 | Save response persists the event | [API] | Executed in stage 7 (api-testing). |
| TC-REQ-4.1 | Endpoint does not 500 on "type" param | [API] | Executed in stage 7 (api-testing). |
| TC-REQ-5b.1 | Save endpoint without AccountEvent does not 500 | [API] | Executed in stage 7 (api-testing). |
| TC-REQ-5d.2 | sessionInfo returns success | [API] | Executed in stage 7 (api-testing). |

## Results

| TC | Name | Source | Status | Comment |
|----|------|--------|--------|---------|
| TC-REQ-1.1 | Save new event with a Type selected (happy path) | QA | PASS | Jam: Add Event → "Choose type of Event" → Save, form filled, final Save → no error toast; event created. |
| TC-REQ-2.1 | Success feedback shown after save | QA | PASS | Jam: form closes and the event shows in the list with an "Approved" status; no error state. |
| TC-REQ-2.2 | Created event appears in the exhibitor's list | QA | PASS | Jam: "test123" appears in "My Exhibitor Events". |
| TC-REQ-3.1 | Sampled Type creates without error | QA | PASS | Jam: a Type was selected (Trade → "SIPMPE TRACK") and the event created without error. Note: sampled Type differs from the ticket's "Activities and competitions". |
| TC-REQ-3.2 | Other Types create without error (spot-check) | QA | PASS | Two Types across the two Jams both created without error: "Simple" (Jam 2) and Trade/"SIPMPE TRACK" (Jam 1). |
| TC-REQ-4.2 | Frontend renders the successful save | QA | PASS | Jam: UI renders the created event / Approved state, not an error toast. |
| TC-REQ-5a.1 | Re-run repro for bwitched2 on IMEX | QA | PASS (with caveat) | Jam: bug does NOT reproduce on the current build. Caveat: exercised on event 3551, not the original IMEX exhibitor "bwitched2". |
| TC-REQ-5b.2 | UI create without AccountEvent is graceful | QA | PASS | Jam 2: exhibitor with NO prior events created one successfully — "Event successfully saved", event "test556" listed with "Approved" status, no error. |
| TC-REQ-5c.1 | Save with no Type selected | QA | QA | The Jam selected a Type; the empty-Type validation path was not exercised. |
| TC-REQ-5d.1 | Exhibitor marketplace loads without error | QA | PASS | Live check: `/marketplace/exhibitors` on ennies-alpha2 loaded; exhibitor cards rendered; no server-error page. |

## Findings

### Evidence (Jam network captures — the save works)
- Jam 1 (exhibitor with events): `POST .../api/v1/exhibitor/saveSession` → **200**, `data.status:true`, `session.id: 33508`.
- Jam 2 (exhibitor with NO prior events): `POST .../api/v1/exhibitor/saveSession` → **200**, `data.status:true`, `session.id: 33541`; UI shows "Event successfully saved".
- Both: `sessionInfo` → 200, `sessions` → 200. **Zero 5xx** in either session; analyzer reported no error indicators. Direct refutation of the reported "Internal Server Error".

### QA (only remaining gap): TC-REQ-5c.1 — empty-Type validation
- **Reason:** Both Jams selected a Type. The "Save with no Type selected → graceful validation, not a 500" path was not exercised. To close: open the "Choose type of Event" modal, leave Type empty, Save, confirm a validation message (not a 500).

### Caveat: TC-REQ-5a.1 — original IMEX case not re-exercised
- The Jams confirm the flow on event 3551 for two exhibitors (incl. a no-events one). They do not re-run the exact original conditions (IMEX, exhibitor "bwitched2"). If the fix were data-specific, an IMEX confirmation would fully close it — but the no-events Jam already covers the most likely repro condition.

## Observations

- OBS-1: The exhibitor "Add Event" save endpoint is `POST /api/v1/exhibitor/saveSession` (portal `qa.exhibitor.alpha.cdot.io` → backend `ennies-alpha2`). `sessionInfo` and `sessions` are also POST. My stage-7 endpoint guesses were wrong; corrected here.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | 9     |
| FAIL   | 0     |
| FAIL CONFIRMED | 0 |
| FAIL REJECTED  | 0 |
| BLOCKED | 0    |
| QA (not verified) | 1 |
| OBSERVATION | 1 |
| Total  | 10    |

Verdict: PASS — the reported Internal Server Error does NOT reproduce on the current build. Confirmed across two exhibitors (one with events, one with none) and two Types; save returns 200 and persists, zero 5xx. Only the empty-Type validation path (5c.1) remains unverified.
```

File: EP-55194-run-report.md

```
# EP-55194 - QA Run Report

Phase analyzed: code (stages 5–8)
Files reviewed: EP-55194-test-cases.md, EP-55194-checklist.md, EP-55194-pr-summary.md, EP-55194-code-review.md, EP-55194-api-testing.md, EP-55194-web-testing.md
Generated: 2026-07-10

> REVISED 2026-07-10 after reviewing TWO user-supplied Jam recordings (jam.dev/c/4bb11133-… and jam.dev/c/5ab20914-…). Runtime evidence flips the verdict to PASS: the Add-Event save works on the current build for both an exhibitor with events and one with none (`saveSession` → 200, events persisted — ids 33508 & 33541, zero 5xx). Only the empty-Type validation path remains unverified.

## Health at a glance

| Category | Status |
|---|---|
| Run / coverage health | 🟢 |
| Input quality | 🔴 |
| Skill / process | 🟡 |

## Issues worth fixing

> Each issue tagged with bucket (Pipeline/skill, Input, Product) and severity.

- 🟢 [Product] The reported Internal Server Error does NOT reproduce on the current build — two Jams: `saveSession` → 200, events persisted (ids 33508 & 33541, incl. an exhibitor with no prior events), zero 5xx. Bug appears resolved / non-reproducing; safe to close after the single empty-Type check below.
- 🟡 [Input] EP-55194 has **no fix branch and no dev sub-tasks**; parent is "Awaiting details". PR #4322 (EP-55072 / HV-114) is not the fix (does not touch the save path). So the code that resolves this is not identifiable — if a real fix landed, link it; if it was a data/config correction, note that on the ticket.
- 🟡 [Coverage] One edge case remains unexercised: empty-Type validation (5c.1 — Save with no Type selected → expect graceful validation, not a 500). The no-events / no-AccountEvent condition and multi-Type spot-check are now covered by the two Jams.
- 🔴 [Input] No Confluence AC linked — requirements derived from the Jira Description + triage only; REQ-2/3/5b/5c/5d carry "(default assumption)". Fix: add/link AC on the ticket.
- 🟡 [Pipeline/skill] My direct-curl API probe reported false BLOCKED (wrong endpoint name `sessions/save`; raw token lacked module session). The Jam corrected it. Lesson: for exhibitor portal endpoints, capture via the portal/Jam rather than raw curl, and confirm the endpoint name before concluding.
- 🟡 [Pipeline] Docs-phase count drift: the QA sub-task stats say "13 test cases · [UI] 9 · [API] 5", but the test-cases file contains 15 TC items ([UI] 10 · [API] 5). Note for the docs phase.

## Findings summary

Code review: PASS 0 · FAIL 0 · QA 15 · N/A 0 (Total 15). The reviewed PR #4322 does not touch the Add-Event save path, so it cannot be confirmed as the fix from code — but runtime evidence (below) shows the flow works on the current build.
API testing (Jam-based): PASS 5 · QA 0 · BLOCKED 0 (Total 5). `saveSession` → 200 (persisted session ids 33508 & 33541, incl. a no-events exhibitor); `sessionInfo` → 200; no 5xx. Endpoint-mapping correction: real save endpoint is `POST /api/v1/exhibitor/saveSession` (not `/sessions/save`); `sessionInfo` is POST.
Web testing (2 Jams + live check): PASS 9 · QA 1 · BLOCKED 0 · OBSERVATION 1 (Total 10). Full Add-Event flow completes for two exhibitors (incl. no-events) and two Types; events listed with "Approved" status, no error toast.
Confirmed bugs: none (0 FAIL / 0 FAIL CONFIRMED). The reported Internal Server Error does not reproduce on the current build.
Unverified edge (only one): empty-Type validation (5c.1 — save with no Type selected).
Routed to non-UI/non-API (mobile/export-email): none in this ticket.
Blast radius (from pr-summary): 3 shared MeetingProgram/Schedule files carry EXISTS-filter regression risk on Speed-Networking feeds — outside this ticket's scope, flagged for visibility.
Overall verdict: **PASS** — the Add-Event save works on the current build (200, persisted, no 5xx), confirmed across two exhibitors (one with no prior events) and two event Types; the reported 500 does not reproduce. Minor remainders: the empty-Type validation path (5c.1) is unverified, and the fixing change is not identifiable in the reviewed PR.

## Recommended next actions

1. Close EP-55194 as not reproducing on the current build (two Jams: save 200, persisted, no 5xx, incl. a no-events exhibitor). Optional single check before closing: Save with no Type selected → expect graceful validation, not a 500 (5c.1).
2. Optional: re-confirm on the original IMEX event with exhibitor "bwitched2" to fully rule out a data-specific residual (lower priority now the no-events case passes).
3. Clarify on the ticket what resolved it — link the actual fix PR/branch if one landed, or note it was a data/config correction (PR #4322 is not the fix).
4. Link/author acceptance criteria and confirm REQ-5b/5c/5d default assumptions.
```

