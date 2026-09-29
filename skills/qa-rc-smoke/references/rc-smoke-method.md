# RC smoke — the method

**Contents:** The RC estate · Step 2: code on the RC branch · Step 3:
served build · Step 4: runtime probes · Setting changes · Instruments
that lie · Step 5: the QA Service run · The report template · The Jira
comment

Everything here was measured on the EP-57782 smoke (Prod 2026-09-30,
2026-09-29) unless another ticket is named. Values drift, so every step
re-discovers what it can instead of trusting this file.

## The RC estate

| What | Value (2026-09-29) | Re-discover with |
|---|---|---|
| Admin panel + backend API | `api-rc.expoplatform.net` (`/admin/…`, `/api/v1/…`) | — |
| Admin UI (React, admin-ui repo) | `https://api-rc.expoplatform.net/adminv2/…`, loaded in the `#newAdminIframe` iframe of the legacy admin page | the iframe's `script[src]` list |
| Default event | **32785 "CANYON 2026"**, portal `canyon2026-rc.expoplatform.net` | admin → Events list |
| Other RC portals | `rctest-rc`, `axent-rc`, `test43-rc`, `mp-rc`, `tos23rc-rc`, `canyon2026-clone-*-rc`, `mp-clone-*-rc` (all `.expoplatform.net`) | EP-57431 `-rc-presence-check.md`; EP-RC-gdpr-event-scan.md (42 events) |
| RC branches | `expoplatform-main-ira`: **`RC`** · `portal-ui`: **`rc-next14`** (not `rc`, which is stale since 2026-05) · `admin-ui`: **`rc`** | Bitbucket refs query (below) |

**Read the RC values from `.env.qa-agents`, not from this table.** The
file's RC block holds `RC_ADMIN_BASE_URL`, `RC_EVENT_ID` and
`RC_FRONTEND_HOST` (`../../qa-pipeline/references/environment.md`).
When `RC_EVENT_ID` differs from the table, the file wins, and the
report says which event was used.

Credentials on RC:
- **Admin:** the same account as alpha2 (confirmed 2026-09-29). Use
  `RC_ADMIN_USERNAME` / `RC_ADMIN_PASSWORD` when set, otherwise
  `ADMIN_USERNAME` / `ADMIN_PASSWORD`, against `RC_ADMIN_BASE_URL`. The
  admin-panel session login (`/admin/index/login` → cookie →
  `/admin/exhibitions/select/<RC_EVENT_ID>`) follows the api-testing
  reference §3. Read values with `load-env.sh` and never print them.
  If the permission layer refuses a scripted login, fall back to the
  user signing in by hand in the Playwright browser, which is how
  EP-57782 ran.
- **Organizer key:** the alpha `ORGANIZER_API_KEY` is rejected on RC
  portals (EP-57431). Whether RC admin REST (`/api/v1/login`, which
  sends it as `Authorization: Basic`) accepts it is **untested**. Use
  `RC_ORGANIZER_API_KEY` when set. Otherwise the alpha key may be tried
  once for the admin REST login, and the report records the answer.
  Never use it for portal calls.
- **Portal:** the admin credentials do not work portal-side (a separate
  account space). Guest endpoints need nothing.

Guest endpoints need nothing. `ALLOWED_HOSTS` must list the RC hosts;
`*.expoplatform.net` covers them all (a `*.rc.expoplatform.net` entry
does not match `canyon2026-rc`).

## Step 2 — code on the RC branch

Bitbucket REST with `BB_EMAIL` / `BB_API_TOKEN`, read from the file and
never echoed (`../../pr-summary/references/bitbucket-access.md`).

- **Find the branch:** `GET repositories/expoplatform/<repo>/refs/branches?q=name~"rc" OR name~"RC"&fields=values.name,values.target.hash,values.target.date`.
  Pick the release branch by name and recency, not by the first hit.
  Feature branches named `EP-…-RC` are not it.
- **Markers, from the item's pr-summary:**
  - new files present (`src/<commit>/<path>?format=meta` → `commit_file`);
  - deleted files absent (404);
  - a distinctive line present (grep the raw file, record `file:line`).
- **Ancestry, when the fix commit is known:**
  `commits/<rc-branch>?exclude=<fix>^` lists what the branch has beyond
  the fix's parent. The fix commit and its merge commit must both be
  in that list.
- **Commits pushed after the merge.** A feature branch can carry
  commits added after its merge (EP-57107: three Swagger/test commits).
  Check whether one of them is on RC. If not, say which state RC
  carries.
- A PR merged to `master` (admin-ui's usual target) reaches `rc` by a
  later cut. Check the file on `rc`, not the PR's state.

## Step 3 — served build

Plain HTTPS GETs of public static assets. No credentials needed.

- **Portal:** GET the page the item lives on, collect every
  `_next/static/…js` it references (92 on `/marketplace/exhibitors`),
  fetch each and grep for the fix's literal. Minification keeps string
  literals: `{"/v1/search/exhibitors":[401],"/v1/search/filters":[401]}`
  was found verbatim in `29249-46a4f8efc797fe7b.js`.
- **Admin UI:** the unauthenticated `/admin/` page is the legacy login
  shell (jQuery only), so the bundle is not reachable from there. Once
  the user is signed in, read the iframe's `script[src]`
  (`/adminv2/assets/index-<hash>.js`, ~2.6 MB) and grep it. Check for
  the new string and also that the old one is gone (count 0).
- **Backend-only items** have no bundle. The runtime probe is the
  build evidence. Name the RC branch commit next to it.

## Step 4 — runtime probes

Pick each item's cases in this order:
1. its `[core]` cases;
2. the case the bug report reproduces;
3. one boundary or negative case per rule the change introduced.

Smoke depth is "the item works and its main rule holds", not the
suite. EP-57782 used 8 probes for a 154-case API suite, 1 for each bug.

- **Guest API probes:** POST/GET with `x-application: 3`, no
  `Authorization`, against the RC portal host. Read the HTTP status and
  also the body `code` and `errors[].field/message`, because the
  platform answers errors inside a 200 envelope as well.
- **Browser, guest:** a fresh browser context (not the signed-in one).
  Install observers with `addInitScript` before navigating. Read the
  DOM for the observable, and screenshot to
  `$EP_QA_HOME/evidence/<RC-KEY>-rc-<ITEM>-<what>.png`.
- **Browser, admin:** the user signs in by hand in the Playwright
  browser. Select the event with `/admin/exhibitions/select/<id>`. The
  admin UI lives in `#newAdminIframe`, so use
  `page.frameLocator('#newAdminIframe')`. A tab can open on the last
  tab used (`tabName=`), so click the tab you need explicitly. For
  dialogs, fill, trigger, read, **Cancel**, then navigate away.
  Nothing is saved.
- **Reads that look like writes.** A "check" call behind a dialog
  (`POST /api/v1/exhibitor/<id>/checkMemberEmail` → `{busy, busyExhibitorId}`)
  writes nothing when it refuses. It is safe only when the expected
  answer is a refusal. If it could accept, stop before the step that
  saves.
- **Fallbacks.** If the Playwright MCP drops ("Connection closed"),
  try Claude in Chrome. If that cannot run JS or screenshot either (a
  foreign extension's frame: "Cannot access a chrome-extension:// URL
  of different extension"), give the user a three-step check to do by
  hand and record it as `source: manual` with them as principal
  (EP-57782 GSRCH-AUTH-03).

## Setting changes

Some items can only be observed under a configuration the RC events do
not have. For example, EP-57398 needs an exhibitor catalogue that is
members-only (`rst`), and none of the 11 RC portals had one. In that
case:

1. **Ask separately.** Name the event, the setting, the expected
   duration, and that the event is shared.
2. **Who flips it.** The agent may do it only if the permission layer
   allows it. EP-57782's attempt to replay the Exhibitor settings form
   was refused ("Modify Shared Resources"). Do not retry through
   another route. Hand the user the exact control instead.
   - Members-only exhibitors: Admin → General → Modules → Exhibitors →
     the **OPEN ACCESS** pill (not the ON/OFF switch next to it, which
     turns the module off).
   - The Registration → Exhibitor settings form no longer renders
     `rst` (EP-57398 r1).
3. **Verify the precondition** with a guest probe and a UTC timestamp.
   Example: `search/exhibitors` → 401 "Unauthorized: Not authorized" at
   15:18:42.
4. **Run the check.**
5. **Restore.** Ask the user to restore, then verify with the same
   probe (200 at 15:23:42). The restore is the first line of the final
   response until it is verified. Write the change and the restore
   instruction into the report **before** the check runs, so a dead
   session leaves a recipe behind.

## Instruments that lie

- **Mocks on server-rendered pages.** `page.route` intercepts only the
  client's own fetches. The marketplace listing renders server-side, so
  the mocked `search/exhibitors` never reached the toast path. The 401
  scenario, the 500 control and a `/brands` control all showed no
  toast. **Result: inconclusive.** Always run a control that must
  produce the observable. If the control is silent too, the probe
  proves nothing.
- **A sibling page used as a control can have different gating on
  RC.** `/marketplace/brands` 401s for guests on alpha2 under rst = 1,
  but answered 200 on RC. Probe the control's precondition too.
- **Guest probes and SSR.** A guest API 200 does not mean the page
  renders. A guest API 401 is the precondition, not the verdict.

## Step 5 — the QA Service run

`../../qa-pipeline/references/test-runs.md` applies, with these values:

- **Title:** `<RC-KEY> RC smoke — <release> — rc (event <id>)`.
- **`env`:** `rc`.
- **`releaseId`:** the release whose `jiraFixVersion` equals the
  ticket's release (`list_releases`). If there is none, omit it, and say
  `release: none — no QA Service release for <release>; create it in
  the web UI` (there is no `create_release` over MCP, and `releaseId`
  cannot be added to a run after it is created).
- **One run across all the suites** of the scope items. A run may span
  suites. `caseIds` must be **catalogue ids** (UUIDs from `search`):
  `create_test_run` answers "none of the given case ids exist" for
  stable ids (EP-57871, EP-57782). `record_case_result` accepts stable
  ids.
- **`principal`:** `ep-qa-pipeline agent (<RC-KEY> RC smoke), operator
  <e-mail>`. A leg the user ran by hand is recorded as `source: manual`
  with the user's e-mail as principal.
- **Verdicts:**
  - `pass` needs the runtime observation in the note: host, event,
    request, response, and the RC branch commit.
  - Code-and-build-only evidence is **not** a `pass`. Leave the case
    off the roster, and write it in the report as "present".
  - An inconclusive runtime is `blocked`, with the instrument failure
    in the note.
- A fully recorded run completes itself; `close_test_run` is only for
  rows deliberately left unrun.

## The report template — `<RC-KEY>-rc-smoke.md`

```
# <RC-KEY> — RC smoke (<release>)

**Question asked:** …
**Target:** admin `api-rc…`, event <id> "<name>", portal `<host>`. Hosts checked against ALLOWED_HOSTS.
**Date / depth:** <date>, smoke, read-only (+ any authorised setting change, with its window).

## RC branches read
| Repo | Branch @ commit | Date |

## Results
| Item | Code on RC | Served build | Runtime on RC | Verdict |

### <ITEM> — <verdict>
Code markers (file:line) · served-build hit (asset name, the literal) · runtime probes (request → response) · still open from earlier rounds, unchanged.

## Blockers
## Follow-up (dated entries: setting changes + restore times, QA Service run id, Jira comment id, tooling failures)
```

## The Jira comment

Markdown (`contentFormat: markdown`; wiki markup renders as literal
text). Keep it to one screen:
- `## RC smoke: <release>, <no blockers found | n blockers>`;
- one environment line;
- the results table (item · code · served build · runtime · result);
- one short paragraph per item;
- the caveats;
- the QA Service run link;
- the closing line `This is not a sign-off. It is evidence for the
  sign-off decision.`

An edit after a later check (a runtime leg that came back from the
user) updates the same comment (`commentId`) instead of adding a
second one.
