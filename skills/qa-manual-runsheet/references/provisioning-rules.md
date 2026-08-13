# Provisioning rules and known traps

**Contents:** The tracking trap · Analytics lag · Fields that lie
about what they are · Fixtures · Verify every blocked reason ·
ExpoPlatform environment specifics · Disclosure

Hard-won on ExpoPlatform alpha2. The general principles apply anywhere;
the endpoint specifics are ExpoPlatform-only and should be re-verified
rather than trusted, since they have already changed once.

## The tracking trap — the most expensive one

**Actions performed over the API often do not enter client-side
interaction tracking.** On ExpoPlatform, favourite tracking fires from
the browser. A favourite created with `curl` writes the durable row but
never reaches the analytics pipeline.

Consequences, all of which have actually happened:

- An automated stage created its favourites over the API, saw nothing in
  the statistics endpoint, and recorded a PARTIAL — while the same case
  performed by hand in a browser exposed a genuine privacy leak.
- Two defects were filed attributing a counter's under-count to a broken
  function, when the real cause was that the favourite had been script-
  created and was therefore invisible to the analytics-backed half of
  the sum.
- A provisioned fixture "held" a favourite that could never appear on
  any analytics-backed surface, making its case unpassable and its
  absence-check meaningless.

**Rule:** any case whose assertion touches counters, leads, analytics,
statistics or an interactions dashboard must have its precondition
created **through the UI**, or the row must tell the tester to perform
the setup action themselves. Never provision such a precondition over
the API and present it as ready.

## Analytics lag

Analytics-backed surfaces on alpha2 ingest with a delay of roughly
**30 to 60 minutes**. A read taken immediately after an action returns a
clean result.

This produced a false PASS on a privacy requirement: the surface was
checked ~30 minutes after the action, showed nothing, and was recorded as
correct. The row appeared later with its original timestamp, and the
requirement was in fact violated.

**Rule:** for any absence check on an analytics-backed surface, put the
required wait in the row, and never record a verdict from an immediate
read. Establish the current lag once per run rather than assuming.

## Fields that lie about what they are

`POST /api/v1/profile/getInteractions` returns
`data.acc.favourite`. It reads like "has favourited" and is actually
"may favourite" — a capability flag. It returns `true` for an account
with no favourites at all, and `true` for a third party who has never
touched the target.

Several precondition verifications were built on it and were worthless.
The reliable signal was the UI: the star's `data-checked` attribute.

**Rule:** confirm what a field means before asserting on it. Where the
UI and an endpoint can disagree, prefer the UI for state. Note in the
sheet which signal the tester should trust.

## Fixtures

- **Fresh account per destructive case.** Any case that mutates state a
  later case depends on gets its own account. Cases then run in any
  order and can be re-run individually without a reset.
- **Dedicated target per counter case, with a verified zero baseline read
  twice.** Shared targets accumulate interactions from other cases and
  make every counter assertion unreadable. One shared fixture reached 12
  page likes across a run; no counter case using it could be judged.
- **Set every dependent attribute explicitly.** Consent flags, names,
  categories, roles. A fixture created without a consent value silently
  defaulted to *opted out* — wrong for something whose only job was to be
  a passive target — and it had null name fields, so the tester could not
  identify it in a list.
- **Record a known password for every account** and prove it
  authenticates. Do not rely on impersonation as the primary route;
  record it as a fallback.
- **Confirm a clean login.** Some accounts hit a blocking
  profile-completion dialog that cannot be dismissed. On ExpoPlatform it
  is cleared only by `POST /api/v1/profile/matchmakingSave` — writing the
  underlying profile columns does **not** clear it. Verify by actually
  logging in, not by reading fields back.

## Destructive-write safety — snapshot first, always

- **No write to a collection-shaped admin endpoint without a persisted
  snapshot and a VERIFIED restore path.** A save-style endpoint that
  takes a list frequently REPLACES the collection rather than appending
  — one run destroyed 930 permission pairs with a single call that
  looked like "add one". Before any such write: fetch the full current
  state to a file, confirm you can restore it (restore a copy or verify
  the endpoint semantics), then write.
- **After the run, verify the revert against the snapshot** — a
  machine check (fetch again, diff against the snapshot file), not a
  memory of having reverted. Mid-run disconnects have left shared
  events corrupt precisely because the revert lived only in intent.
- **Write the restore recipe to the notes file BEFORE the first
  mutation**, so a crashed session leaves instructions, not a mystery.
- **Prove reachability on the exact path a case uses with ONE throwaway
  object before bulk-provisioning** — one run provisioned 19 entities
  and recovered 0 cases because the surface never showed them. And
  never create an entity type whose delete path you have not confirmed:
  one unrevertible row came from an HTTP 500 that still wrote.
- **Verify positive fixture claims as rigorously as blocked reasons.**
  Rule 5 probes blockers; the same rigour applies to "the fixture is
  ready": prove the account logs in, the entity appears on the exact
  surface, the count reads the expected baseline — including the
  host's own health. One sheet claimed 15 exhibitors where the event
  had 359, and 10 toggles where there were 15.

## Verify every blocked reason

A wrong "blocked" silently removes a case from testing. In one run four
cases were blocked on premises that dissolved on a single probe:

- "no setting exists to make favourites contribute leads" — it existed,
  under a differently named admin page, already enabled
- "no lead count is displayed anywhere" — it was on the exhibitor
  analytics tab
- "no brand exists on this event" — ten did; the error message was
  misleading
- "the endpoint is not exposed on either host" — it was, on the admin
  host

**Rule:** probe every blocker against the live system before writing it.
If a probe is not possible, write the reason as *unverified* and say what
would confirm it.

## ExpoPlatform environment specifics

Re-verify these; they have changed before.

- **Portal login:** `POST {FRONTEND_HOST}/api/v1/login` with
  `{"username": <email>, "password": ...}`, headers `x-application: 3`
  and `Authorization: Basic base64(ORGANIZER_API_KEY + ":")`. Throttles
  at roughly **6 attempts per 5 minutes per IP**. Returns
  `data.token` — a 32-char hex string, **not** a JWT.
- **Calling a user-scoped endpoint needs BOTH headers.** The login
  token goes in its own header alongside the API key, never instead of
  it:

  ```
  Authorization: Basic base64(ORGANIZER_API_KEY + ":")
  x-auth-token: <data.token from login>
  x-application: 3
  ```

  Verified on `POST /api/v1/profile/interactions` and
  `GET /api/v1/profile/interactionsCount`. The token does **not**
  authenticate as `Authorization: Bearer <token>`, as
  `Basic base64(token + ":")`, as a `token` field in the JSON body, or
  as a `?token=` query param — all four return
  `401 Unauthorized: Not authorized`, which reads like an expired
  session and is actually the wrong header. Four attempts were spent
  rediscovering this on a retest; do not rediscover it a third time.
- **There is no `/login` page** — it renders a soft 404. The login modal
  opens from the header Sign In button or `?openLoginPopup=true`. Log out
  via the avatar menu; the logout endpoints do not end the session.
- **v2 statistics endpoints need `Authorization: Bearer <key>`**, not
  Basic. Basic returns `403 Invalid API key`, which looks like a
  permissions problem and is not. Rate limit ≈ **one request per 45
  seconds**, returning 429 with the wait.
- **`POST /api/v2/account/set`** reports write failures inside
  `data.errors` while returning HTTP 200 with `errors: null`. Check the
  body, not the status. Its `networking` field wants `true`/`false`.
- **Account creation:** `POST /admin/index/doRegistration` (admin session
  + CSRF) is the working path. `/admin/visitors/saveVisitor?id=` fatals
  on create.
- **~~Known broken on alpha2~~ — FIXED 2026-08-03 (EP-55694).**
  Favourites-list reads (`profile/interactions`, `interactionsCount`)
  used to 500 on `hosted_buyer_buyers.id` for every user. Re-probed on
  2026-08-04: all list types and the count endpoint return 200. Kept
  here as the worked example of why an environment blocker must be
  re-probed rather than inherited — four cases sat BLOCKED on it, and a
  stale note would have kept them there.

## Disclosure

Anything mutated outside the provisioning plan goes in the notes file:
what changed, whether it was reverted, and what a human must clean up.
An unrevertible change — a password reset, an undeletable notification,
a stale analytics aggregate — must be named explicitly rather than
softened.
