# Playwright executor (the default backend)

Status: **the default since 0.35.0 — used whenever the Playwright MCP
tools are in the session.** The Claude in Chrome extension is the one
fallback (SKILL.md "Execution backends"). First run on a real ticket:
compare a few results against expectations before trusting a full
unattended run.

## Why it is the default

The extension drives the user's real Chrome — it needs the window
active and breaks when the user touches the browser. Playwright runs
its own browser (headless by default), independent of the user's
screen, with auto-waiting, deterministic locators, and built-in
evidence capture (screenshots, console, traces).

## Contract stays identical

Everything in SKILL.md except the executor is unchanged: same inputs
(code-review + test-cases with its Structural checks section), same scope rule (SKILL.md →
Scope: the routing invariant — routed-in, dual-tag and RE-ROUTE cases
included), same classification (PASS / FAIL / FAIL CONFIRMED / FAIL
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
   credentials from `$EP_QA_HOME/.env.qa-agents`
   (`../../qa-pipeline/references/environment.md`). Never print the
   values. The host was already checked against `ALLOWED_HOSTS` in
   the Scope step; do not navigate anywhere else.
2. Perform the login with Playwright (fill username/password, submit,
   wait for the post-login page). This REPLACES the extension path's
   "PAUSE for browser login" — do not ask the user unless the login
   fails.
3. If login fails or hits SSO/2FA: pause once and ask the user to
   complete it (headed mode), then reuse the session.
4. Persist auth state per host when the MCP supports it, so one login
   covers the run.

## Evidence (FAIL only) — what the backend can actually write

On every FAIL / FAIL CONFIRMED record, in this order of preference:

1. **The screenshot, straight into `$EP_QA_HOME/evidence/`.** The
   Playwright MCP server writes only inside its output directory, so the
   server is started with `--output-dir` pointing at
   `$EP_QA_HOME/evidence/` (README → "Before you run"; `environment.md`
   layout). Take the screenshot with `filename:
   <ISSUEKEY>-r<N>-<TC-ID>-fail.png` — the round is in the name because
   the store is flat — and the report row cites
   `evidence/<ISSUEKEY>-r<N>-<TC-ID>-fail.png`. No copying step.
   (EP-56197 open-items #12: the earlier "screenshot into the sandbox,
   then copy with host tools" rule left every Playwright FAIL without
   its screenshot for two rounds.) Output directory not configured —
   the tool reports a path outside `$EP_QA_HOME` — say so once in the
   report and fall to 2.
2. **The documented equivalent — always written:**
   `<ISSUEKEY>-web-evidence.md` in the run folder, one numbered section
   per FAIL: the URL, the exact DOM / text reading that contradicts the
   expectation (aria snapshot or `inner_text` excerpt, quoted), the
   console lines captured **before** navigating away, the timestamp.
   The report row cites `web-evidence.md §n` — that reference is what
   the run's roster note carries (`test-runs.md` → evidence), because
   an on-disk screenshot cannot be uploaded there anyway.

A FAIL with a `§n` reading and no screenshot is compliant; a FAIL with
neither is not a FAIL, it is a claim. Nothing is captured for PASS —
evidence noise costs tokens and review time.

## Known risks

- SSO / 2FA on some hosts may block scripted login — headed manual
  login fallback (above).
- `navigation_paths.json` memory is less critical (deep-linking
  works), but keep writing it — the extension fallback still uses it.
- A server started without `--output-dir` writes to a per-session temp
  folder that is gone with the session. The report row shows it (a
  path outside `$EP_QA_HOME`): fall to the `§n` reading, and tell the
  user the one-line reconfiguration.
- Headless rendering can rarely differ from real Chrome — the headed
  retry rule above covers it.
