# Login & Registration Config

Login configuration for the ExpoPlatform **alpha2 e2e-testing** site
under test, derived from the `e2e-testing` Playwright repo. This is a
staging environment — never production.

Do not hardcode real credentials in this file. Keep them in environment
variables (or the `e2e-testing` repo's `.env`) and reference them by
name, as below.

## Login

The portal login is a **modal dialog**, not a separate page.

- **URL:** `${BASE_URL}${BASE_PATH}` — currently
  `https://e2e-testing-alpha2.expoplatform.net/newfront` (the portal
  home page). Open it, then open the login dialog.
- **Open the dialog:** click the **"Sign in"** button in the page
  header.
- **Dialog:** a dialog titled **"Log in"** appears.
- **Email field:** input with placeholder **"Your email or user name"**.
- **Password field:** input with placeholder **"Your password"**.
- **Login button:** the **"Log in"** button inside the dialog.
- **Credentials (from env vars — do not inline):**
  - Manual visitor (default for web testing): `VISITOR_EMAIL` /
    `VISITOR_PASSWORD`. This is a shared persistent account created
    specifically for manual / browser-based investigation; automation
    never touches it, so it is safe to use here.
  - Admin panel (only if a test case needs the admin side):
    `ADMIN_USERNAME` / `ADMIN_PASSWORD` at the Admin URL below.
  - Default: log in as the manual visitor. Use the admin account only
    when a test case explicitly requires the admin panel.
- **Success indicator:** the page `header` is visible and the "Sign in"
  button is replaced by the logged-in state.

### OTP alternative

Some events have OTP authentication enabled instead of password. In
that case the dialog hides the password field and shows a **"Generate a
one-time password"** button:

1. Enter the email.
2. Click **"Generate a one-time password"**.
3. Wait for the **"Your one-time password"** input to appear.
4. The OTP is produced via the admin panel (see
   `src/api/requests/otp.requests.ts` in the `e2e-testing` repo) — no
   real email inbox is needed. Ask the user for the OTP value if you
   cannot generate it.
5. Enter the OTP and click **"Log in"**.

If you are unsure which mode the event uses: open the dialog and check
whether a password field or a "Generate a one-time password" button is
shown.

## Admin panel

- **URL:** `${ADMIN_BASE_URL}/admin` — currently
  `https://api-alpha2.expoplatform.net/admin`.
- **Credentials:** `ADMIN_USERNAME` / `ADMIN_PASSWORD`.

## Registration

Registration is normally **not needed** for manual web testing — use
the shared manual visitor account above. The automated suite creates
fresh visitors per run via the API/admin, but the web-testing skill
should not create accounts unless a test case explicitly requires a
brand-new user. If it does, ask the user how to provision one.

## Default data for registration

Not applicable for the default manual-visitor flow. If a test case needs
a new user, ask the user for the email/values to use.

## Notes

- Environment: **alpha2 staging** (`*.expoplatform.net`) — not
  production. Do not run destructive steps against it beyond what a test
  case explicitly requires.
- The frontend under test is `portal-ui` (Next.js + React + Material
  UI) — see the MUI interaction notes in `browser-rules.md`.
- OAuth / SSO login flows are out of scope for the agent; use the
  email+password (or OTP) flow above.
- Credential values live in the `e2e-testing` repo's `.env`
  (git-ignored). This config only references the variable names.
