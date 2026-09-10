# api-testing — setup guide

Team-specific choices to confirm before running this skill.

## 0. Run this in Claude Code, not Cowork

This stage authenticates against the REST API with the credentials in
`~/.ep-qa/.env.qa-agents` (`EP_QA_HOME`; the plugin's
`skills/qa-pipeline/references/environment.md`) and needs a shell for
curl, so run it — and the `qa-pipeline-code` orchestrator — from
**Claude Code** with that folder in place. Cowork is for the docs half
and browser `[UI]` testing. Never paste credentials into chat — they're
read from the file at runtime. (See the plugin's `MAINTAINERS.md` →
"Where to run each stage" and "Where things live".)

## 1. Credentials — from `.env.qa-agents` (never commit real values)

The skill reads these at runtime from `$EP_QA_HOME/.env.qa-agents`.
Confirm they point at the environment under test:

| Variable | Meaning |
|---|---|
| `ADMIN_BASE_URL` | API host, e.g. `https://api-alpha2.expoplatform.net` (no trailing `/admin`). |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin / superadmin login. |
| `ORGANIZER_API_KEY` | HTTP Basic auth on every REST call. |
| `EVENT_ID` | Event to select (`x-sel-exhibition`). |
| `BASE_URL` / `BASE_PATH` | Visitor / exhibitor frontend host + path. |
| `ALLOWED_HOSTS` | Comma-separated hosts the stage may call (`*.suffix` allowed). Every host above must match; production is refused even when listed. |

The skill **pauses and asks** if the file, a required variable or the
allow-list is missing, or a host is not on it — it never proceeds
unauthenticated, never calls an unlisted host, and never hardcodes
secrets.

## 2. Per-event frontend host (for exhibitor-token cases)

The exhibitor/visitor frontend domain is **per-event and not
discoverable** via the API/admin/DB — it must be supplied per event
(e.g. event 3551 → `https://ennies-alpha2.expoplatform.net`), together
with an exhibitor login (username, not email). See
`references/api-testing-reference.md` §11.

## 3. Write-safety on shared environments

Default is read-only. Any mutating case must snapshot-and-revert or use
a throwaway entity (reference §9, §12). Category `saveSettings` affects
every exhibitor in the category — use a disposable category id, never a
shared one.

## 4. Trigger phrases

Adjust the `description` frontmatter in `SKILL.md` to match how your team
phrases requests ("api testing", "test the endpoints", "run the API
checks", etc.).

## 5. Endpoint-mapping caveat

Ticket endpoint names can be **wrong**, not just shorthand. Confirm what
an endpoint actually does before trusting a test case's mapping
(reference §11.3 — the `photoSave` vs `profileSave` lesson).
