# API Testing Reference (ExpoPlatform) — for the QA agent

A reusable playbook for exercising ExpoPlatform REST endpoints directly (curl / HTTP),
so API `[API]` test cases from the QA pipeline can be executed without the browser.

The file has two kinds of content — treat them differently:

- **Stable method** (§0–§7, §9, §10, and the §11.2/§12 techniques): the
  auth model, route discovery, envelope, and safety rules. These apply
  to any feature and rarely change.
- **Worked-example data** (§8, the §11.1/§11.3 discoveries, the ids in
  §12): recorded from the **logo restriction** feature (EP-54971) on
  **alpha2 / event 3551, June 2026**. Hosts, entity ids, and category
  ids WILL go stale — re-resolve them on the target event (§7) instead
  of trusting them; keep the lessons, not the numbers.

> **No secrets in this file.** All credentials are read at runtime from the project `.env`
> (the same variables `env.ts` validates). Never hardcode username / password / API keys
> into a skill or test file — `.env` is git-ignored for this reason.

---

## 0. Config & credentials (read from `.env`)

The agent must load these from an env file — search order:
`.env.qa-agents` in the mounted qa-pipeline-skill repo, then the e2e
project's `.env` (see its `.env.example` for the full list), then
plain environment variables:

| Variable | Meaning |
|---|---|
| `ADMIN_BASE_URL` | API host, e.g. `https://api-alpha2.expoplatform.net`. **No trailing `/admin`** — helpers append paths themselves. |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin / superadmin login. |
| `ORGANIZER_API_KEY` | Sent as HTTP Basic auth on every REST call (`Authorization: Basic <key>`). Org/event-scoped. |
| `EVENT_ID` | The event to select (sent as `x-sel-exhibition` on admin REST calls). |
| `BASE_URL` / `BASE_PATH` | Visitor / exhibitor frontend host + path (for exhibitor-token calls). |

**Shell-safety (passwords with `;` `?` `!` `$`…):** credentials may contain
shell metacharacters — `ADMIN_PASSWORD` does. Mishandled, a `;` silently
truncates the value (the rest runs as a command) and login fails with
"incorrect password". Rules:

- **Never retype a secret inline** into a command or an `export FOO=...`
  line. Load it from the file programmatically.
- Values in the env file may be single-quoted — strip the quotes when
  parsing manually.
- Safe load pattern (handles quotes and metacharacters):
  ```bash
  getenvvar() {  # getenvvar NAME FILE
    grep -m1 "^$1=" "$2" | cut -d= -f2- | sed "s/^'//; s/'\$//; s/^\"//; s/\"\$//"
  }
  ADMIN_PASSWORD=$(getenvvar ADMIN_PASSWORD .env)
  ```
  This function ships as **`scripts/load-env.sh`** in the skill folder —
  source it (or run `load-env.sh NAME FILE`) instead of retyping it.
- Always expand as `"$ADMIN_PASSWORD"` (double-quoted). For JSON login
  bodies prefer building the payload with `python3`/`jq --arg` so quotes
  and backslashes in values cannot break the JSON.
- The same applies to any exhibitor/visitor password taken from test
  data.

**Per-environment caveat:** `.env` must hold the values for the environment under test.
The committed `.env` may point at a different alpha (e.g. `ep51796alphaalpha`, event 459),
while alpha2 (`api-alpha2.expoplatform.net`) is in `.env.example`. Before running, confirm
`ADMIN_BASE_URL`, `ORGANIZER_API_KEY` and `EVENT_ID` match the target env. Example target:
alpha2, event `3551`.

---

## 1. Three auth contexts (pick the right one or you get 404 / 400 / wrong data)

| Endpoint family | Host | Auth | Notes |
|---|---|---|---|
| `/api/v1/...`, `/api/v2/...` REST | `ADMIN_BASE_URL` | **admin token** via `x-auth-token` | Most admin-facing reads/writes. This is what most `[API]` cases use. |
| `/admin/...` legacy admin panel | `ADMIN_BASE_URL` | **PHP session cookie** (not token) | Event comes from the session (`/admin/exhibitions/select/{id}`), not a header. |
| exhibitor-facing (`/api/v1/manuals/...`, `/profile/...`) | `BASE_URL` | **the exhibitor's** token | Looks up entity by `exhibitor_id` from the token — admin's token returns nothing. |

---

## 2. Get an admin token (REST — the common path)

```bash
API="$ADMIN_BASE_URL"; ORG="$ORGANIZER_API_KEY"; EV="$EVENT_ID"
TOKEN=$(curl -s -X POST "$API/api/v1/login" \
  -H "Authorization: Basic $ORG" -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['token'])")
```

Then send on **every** admin REST call:

```
Authorization: Basic <ORGANIZER_API_KEY>
x-auth-token:  <TOKEN>
x-access-token:<TOKEN>
x-sel-exhibition: <EVENT_ID>     # selects the event for admin REST
x-application: 1
```

The login response also confirms the account (`data.user.isSuperAdmin`, `displayName`).

## 3. Get an admin-panel session (only for `/admin/...` endpoints)

```bash
curl -s -c cj.txt -X POST "$API/admin/index/login" \
  -H "X-Requested-With: XMLHttpRequest" \
  --data-urlencode "username=$ADMIN_USERNAME" --data-urlencode "password=$ADMIN_PASSWORD"
curl -s -b cj.txt -c cj.txt "$API/admin/exhibitions/select/$EV"   # puts exhibition_id in the session
# then call /admin/... with -b cj.txt
```

If login returns `{"mfa":true}` the account can't be automated. `{"error":...}` = rejected.

## 4. Get an exhibitor / visitor token (frontend cases)

```bash
curl -s -X POST "$BASE_URL/api/v1/login" \
  -H "Authorization: Basic $ORG" -H "Content-Type: application/json" \
  -d "{\"username\":\"<exhibitor.username>\",\"password\":\"<pw>\"}"
```

`username` is the exhibitor's **`username`** field (what they were created with), **not** their email.

---

## 5. Response envelope

All REST responses wrap in:

```json
{ "code": 200, "errors": null, "data": { ... } }
```

- Success: `code: 200`, `errors: null`.
- Client/validation error: `code: 400`, `errors: [{ "message": "...", "type": "...", "code": 400 }]`.
- Auth/permission failure: `{ "errors": { "resource": "Access denied" } }`.
- The Playwright `ApiClient` unwraps to `response.data.data`; with raw curl, read `.data` yourself.

---

## 6. Finding the real route (ticket endpoint names are usually shorthand)

QA tickets write endpoints loosely (e.g. `GET /exhibitorCategories/get`). The real path
almost always carries an `/api/v1/` or `/api/v2/` prefix. **Probe and read the error message:**

| Response | Meaning |
|---|---|
| `404 "Invalid endpoint"` | Wrong path — try another prefix/name. |
| `400 "Missing required parameter: X"` | **Right endpoint**, you just need to supply `X`. |
| `400 "Invalid Filter. Valid filters: ..."` | Right endpoint, wrong query param — use a listed filter. |
| `200` | Correct. |

```bash
auth=(-H "Authorization: Basic $ORG" -H "x-auth-token: $TOKEN" \
      -H "x-access-token: $TOKEN" -H "x-sel-exhibition: $EV" -H "x-application: 1")
for p in "/api/v1/<name>/get" "/api/v2/<name>/get" "/api/v1/<name>/list"; do
  code=$(curl -s -o /tmp/b -w "%{http_code}" "${auth[@]}" "$API$p")
  echo "[$code] $p :: $(head -c 160 /tmp/b)"
done
```

## 7. Finding test data (event / category / exhibitor)

- **Exhibitors on an event:** `GET /api/v2/exhibitors/{EVENT_ID}/list?limit=5` → `data.list[].id`, `.name`, `.logo`.
- **Category id** for an exhibitor: read it from the exhibitor-settings response
  (`data.category.category.id` / `.title`). Don't rely on a ticket's hardcoded ids —
  they're often from a different environment.

---

## 8. Worked example — logo restriction (EP-54971), on alpha2 / event 3551

> **Dated example (2026-06).** The method below is the model to copy;
> the concrete ids/hosts are snapshots — re-resolve per §7 before use.

Resolved test data on that env: exhibitor `9145077` (Critical Kit), category `13776`
(Exhibitor Unlimited), default state (logo ON, no override).

### Read (GET) — safe

| Purpose | Call | Key fields |
|---|---|---|
| Category setting | `GET /api/v1/exhibitorCategories/get?id={categoryId}` | `data.settings.logo.enabled` |
| Exhibitor effective + category | `GET /api/v1/exhibitorSettings/get/{exhibitorId}` | `data.current.logo {enabled, isCustom}`, `data.category.logo {enabled}`, `data.category.category {id, title}` |
| Public list surface | `GET /api/v2/exhibitors/{EVENT_ID}/list?limit=N` | `list[].logo` (real URL when ON) |
| Public single | `GET /api/v2/exhibitor/get?event_id={EVENT_ID}&id={exhibitorId}` | `data.logo` (requires **both** `event_id` and the `id` filter) |

Interpretation for the logo feature:
- `isCustom:false` → exhibitor is **synced** to the category; `current.logo.enabled` equals the category's.
- `isCustom:true` → a per-exhibitor **override** is set; category changes no longer affect it.
- New positive key is `logo.enabled` (`true` = allowed). The legacy `do_not_allow_logo`
  flag should be **absent** everywhere — its presence is the REQ-24 regression to catch.

### Write (POST) — mutating, needs care (see §9)

- Category: `POST /api/v1/exhibitorCategories/saveSettings` with `logo: { enabled: <bool> }`.
- Exhibitor override: `POST /api/v1/exhibitorSettings/set` with `logo: { enabled: <bool>, isCustom: true }`.
- Frontend upload block: `POST {BASE_URL}/profile/photoSave` (expect `success: 0` when OFF),
  `GET {BASE_URL}/profile/profileEdit` (expect `isLogoEditable: false`) — needs an **exhibitor token**.

---

## 9. Read-only vs write safety (shared environments)

Alpha envs are shared. Default to **read-only** unless the case requires a write.

For mutating cases (`saveSettings`, `set`, `photoSave`, create/delete):
1. **Snapshot** the current value first (GET), or create a throwaway entity for the test.
2. Perform the write and assert.
3. **Revert** to the snapshot (or delete the throwaway) in teardown — never leave orphaned
   state. This matches the repo rule: create via API in setup, delete via API in teardown.

Report each case as PASS / FAIL / PARTIAL / BLOCKED, with the endpoint + observed field as evidence.

---

## 10. Gotchas checklist

- [ ] `ADMIN_BASE_URL` has **no** trailing `/admin`.
- [ ] Admin REST needs `x-sel-exhibition`; legacy `/admin/...` needs the session cookie instead.
- [ ] `ORGANIZER_API_KEY` goes in `Authorization: Basic` on **every** REST call, in addition to the token.
- [ ] Ticket endpoint names are shorthand — confirm the real `/api/v1|v2/...` path by probing (§6).
- [ ] `/api/v2/exhibitor/get` needs **both** `event_id` and an `id` (or `external_id`) filter.
- [ ] Category / exhibitor ids in a ticket are often from another env — resolve real ids on the target event (§7).
- [ ] Frontend `/profile/...` cases need the **exhibitor's own** token, not the admin token.
- [ ] Never hardcode secrets — read from `.env`.
- [ ] The **frontend host is per-event and not discoverable via the API/admin/DB** — it must be supplied (see §11).
- [ ] Ticket endpoint names can be **wrong**, not just shorthand — verify what an endpoint actually writes before trusting a test case (see §11, `photoSave`).

---

## 11. Frontend / exhibitor-token cases (worked example)

The `[API]` cases that hit `/profile/...` (upload logo, `isLogoEditable`, etc.) run against the
**event's frontend host** with the **exhibitor's own** token — the admin token is rejected there.

### 11.1 Finding the frontend host (must be supplied)

The frontend domain is **per-event** and is **not** exposed by the API, the admin panel, or the
events list (`GET /api/v1/exhibitions/list` returns events but **no domain field**). The alpha DB
(`alpha-db-rw.epdev.it:5432`) is firewalled from CI/sandboxes. So the agent must be **given** the
portal URL per event. Example: event `3551` → `https://ennies-alpha2.expoplatform.net`.

> Wrong host symptom: exhibitor login returns `400 "Incorrect login and/or password"` even with
> correct credentials — the account isn't on the event that host serves.

### 11.2 Get an exhibitor token (frontend)

```bash
FE="https://ennies-alpha2.expoplatform.net"          # event 3551's portal
ET=$(curl -s -X POST "$FE/api/v1/login" \
  -H "Authorization: Basic $ORG" -H "Content-Type: application/json" \
  -d '{"username":"<exhibitor.username>","password":"<pw>"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['token'])")
```

- `username` = the exhibitor's **`username`** (from the create response), **not** the email.
- **Prime the session** before profile calls: `POST {FE}/api/v1/auth` with the token headers
  (fresh logins aren't fully initialised until `/api/v1/auth` is called once).
- Frontend headers: `Authorization: Basic $ORG`, `x-auth-token`, `x-access-token`,
  `x-application: 3` (visitor/portal app), `x-lang: en`, plus `Origin`/`Referer` = `$FE`.

### 11.3 Profile endpoints (discovered on alpha2)

| Endpoint | Method | Notes |
|---|---|---|
| `/api/v1/profile/profileEdit` | GET | Returns `data.settings.isLogoEditable` (the FE gate — `false` when effective logo OFF), `data.userData.custom_fields.companylogo {id,url}`, and `data.sections` (form template). |
| `/api/v1/profile/photoSave` | POST (multipart `photo`) | **Generic/personal photo upload — NOT the company logo.** Returns `{status:true, success:1}` and does **not** change `companylogo` even when logo editing is ON. |
| `/api/v1/profile/profileSave` | POST | The real "Company Details" section save that persists the `companylogo` custom field. (Exists — a malformed body returns 502, whereas non-existent routes return a clean 404.) |

**Key gotcha (EP-54971 TC-22.1/31.1):** the ticket maps "logo upload" to `photoSave`, but `photoSave`
never writes the logo — so it can't validate a logo-upload block. The logo persists via `profileSave`,
and `companylogo` is a **custom field** (alongside `VAT_Country`, `VAT_Number`, `exhibitor_info_*`).
When a case's expected value doesn't reproduce, check whether the endpoint actually does what the
ticket claims before logging a bug.

### 11.4 Setting effective logo OFF for a frontend test

Frontend gating is driven by the exhibitor's effective logo value. Toggle it from the **admin** side
(per-exhibitor override, safe + revertible), then re-check the portal:

```bash
# admin: force this exhibitor OFF
curl -s "${authj[@]}" -X POST "$API/api/v1/exhibitorSettings/set/$EX" \
  -d "{\"id\":$EX,\"logo\":{\"enabled\":false,\"isCustom\":true}}"
# portal: GET /api/v1/profile/profileEdit → data.settings.isLogoEditable == false
# revert: set {"logo":{"enabled":true,"isCustom":false}}
```

---

## 12. Creating & cleaning up throwaway test entities

Prefer a disposable exhibitor over mutating real data.

```bash
# CREATE (organizer key + admin token). Does NOT accept category fields —
# 'exhibitor_category_id' / 'category' / 'category_id' are rejected.
EX=$(curl -s "${auth[@]}" -X POST "$API/api/v2/exhibitor/set" \
  -F "event_id=$EV" -F "name=ZZ Test $RANDOM" -F "email=zz+$RANDOM@expoplatform.test" \
  -F "username=zz_$RANDOM" -F "password=Test12345!" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['id'])")

# DELETE (teardown) — from_event=true removes it from the event
curl -s "${auth[@]}" -X DELETE "$API/api/v2/exhibitor/delete?id=$EX&event_id=$EV&from_event=true"
```

### 12.1 Category-level writes need the full settings payload

`POST /api/v1/exhibitorCategories/saveSettings` validates the **whole** settings object (it errors
`"Allow Header Image is required"` etc. on a partial body). Read the current settings, echo them back
with only the target field flipped, then restore:

```bash
# GET /api/v1/exhibitorCategories/get?id=$CAT  → data.settings  (save this)
# POST saveSettings  body = { id:$CAT, ...all settings..., logo:{enabled:false} }
# success looks like: {"data":{"error":false,"done":true}}
# then POST again with logo:{enabled:true} to restore
```

Category `saveSettings` affects **every exhibitor in that category**, so use a dedicated/disposable
category id — never a shared one. There is **no category-create API**; get a spare category id from
the event owner (e.g. 3551 used cat `14888` "Exhibitor Junior").

### 12.2 Precedence checks

- **Non-overridden** exhibitor (`current.logo.isCustom=false`) → follows the category value.
- **Overridden** exhibitor (`isCustom=true`) → keeps its own value when the category flips.
- Snapshot each entity's `current.logo` before writing and restore it in teardown; verify final state
  (`enabled:true, isCustom:false` = clean default).
