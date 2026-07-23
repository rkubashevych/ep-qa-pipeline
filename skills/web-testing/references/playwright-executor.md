# Playwright executor (preferred backend)

Status: **active — preferred when the Playwright MCP tools are
available in the session.** The Claude in Chrome extension remains
the fallback executor (see SKILL.md "Execution backends"). First run
on a real ticket: compare a few results against expectations before
trusting a full unattended run.

## Why it is preferred

The extension drives the user's real Chrome — it needs the window
active and breaks when the user touches the browser. Playwright runs
its own browser (headless by default), independent of the user's
screen, with auto-waiting, deterministic locators, and built-in
evidence capture (screenshots, console, traces).

## Contract stays identical

Everything in SKILL.md except the executor is unchanged: same inputs
(code-review + test-cases + checklist), same scope rule (only `[UI]`
QA/FAIL), same classification (PASS / FAIL / FAIL CONFIRMED / FAIL
REJECTED / BLOCKED / OBSERVATION), same escalation rule, same output
template. Only the "how a step is executed" changes.

## Mode

- Default: **headless**. If a case behaves suspiciously differently
  from the expectation (rendering/anti-bot quirks), retry it headed
  before classifying — note the retry in the report.
- Viewport: 1440×900 or larger (MUI admin tables clip on small
  viewports).

## Tool mapping

| Extension tool | Playwright equivalent |
|---|---|
| `navigate` | `page.goto(url)` |
| `find` (natural language) | `get_by_role` / `get_by_label` / `get_by_text` — prefer role+name |
| `read_page` | aria snapshot |
| `computer` click/type/key | `locator.click()` / `locator.fill()` / `keyboard.press()` |
| `form_input` | `locator.fill()` / `select_option()` |
| `get_page_text` | `page.inner_text("body")` |
| screenshot (FAIL evidence) | screenshot tool + trace if available |

MUI notes from browser-rules.md still apply (selects are buttons +
listbox portals; date pickers need keyboard entry).

## Login — scripted, no pause

1. Read `references/login-config.md` for the URL/field shape and
   credentials from `.env.qa-agents` (search order per SKILL.md
   Step 4). Never print the values.
2. Perform the login with Playwright (fill username/password, submit,
   wait for the post-login page). This REPLACES the extension path's
   "PAUSE for browser login" — do not ask the user unless the login
   fails.
3. If login fails or hits SSO/2FA: pause once and ask the user to
   complete it (headed mode), then reuse the session.
4. Persist auth state per host when the MCP supports it, so one login
   covers the run.

## Evidence (FAIL only)

On every FAIL / FAIL CONFIRMED:

- Take a screenshot of the failing state; save as
  `<ISSUEKEY>-<TC-ID>-fail.png` in the working directory and
  reference it from the report row.
- Capture browser console errors for the failing page and quote the
  relevant line(s) in the finding.

Nothing is captured for PASS — evidence noise costs tokens and
review time.

## Known risks

- SSO / 2FA on some hosts may block scripted login — headed manual
  login fallback (above).
- `navigation_paths.json` memory is less critical (deep-linking
  works), but keep writing it — the extension fallback still uses it.
- Headless rendering can rarely differ from real Chrome — the headed
  retry rule above covers it.
