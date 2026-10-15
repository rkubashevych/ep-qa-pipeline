# Playwright executor (the default backend)

Status: **the default since 0.35.0 — used whenever the Playwright MCP
tools are in the session.** The Claude in Chrome extension is the one
fallback (SKILL.md "Execution backends"). First run on a real ticket:
compare a few results against expectations before trusting a full
unattended run.

## Why it is the default

The extension drives the user's real Chrome — it needs the window
active and breaks when the user touches the browser. Playwright runs
its own browser, independent of the user's
screen after the one sign-in, with auto-waiting, deterministic
locators, and built-in evidence capture (screenshots, console,
traces).

## Contract stays identical

Everything in SKILL.md except the executor is unchanged: same inputs
(code-review + test-cases with its Structural checks section), same scope rule (SKILL.md →
Scope: the routing invariant — routed-in, dual-tag and RE-ROUTE cases
included), same classification (the full WEB set in SKILL.md →
"Classification" — not restated here, so it cannot drift), same
escalation rule, same output template. Only the "how a step is executed" changes.

## Mode

- **Headed** — the user signs in in this window (Login, below), and
  the Playwright MCP opens a visible browser unless started with
  `--headless`. A server started headless cannot take the sign-in:
  say so and give the user the one-line restart without the flag.
  The run stays independent of the user's own Chrome either way.
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
| screenshot (FAIL / `[core]` PASS evidence) | screenshot tool + trace if available |

MUI notes from browser-rules.md still apply (selects are buttons +
listbox portals; date pickers need keyboard entry).

## Login — the user signs in by hand (0.72.0)

The procedure is SKILL.md → Step 4. What is Playwright-specific:

1. The browser must be **visible** (headed — see Mode) so the user
   can sign in in it. The
   host was already checked against `ALLOWED_HOSTS` in the Input
   section (SKILL.md → Input, the test-host paragraph); do not navigate
   anywhere else.
2. Never `fill` a password, and never read `.env.qa-agents` from
   inside the browser process (`browser_run_code_unsafe` / evaluate) —
   the first puts the secret in a tool argument, the second is refused
   as a containment escape. Do not retry that route.
3. Impersonation for a non-admin role runs in the page (an in-page
   `fetch` of the admin's impersonate action, then navigate to the
   link it returns) so no token or link is printed.
4. Persist auth state per host when the MCP supports it, so one login
   covers the run.

(Until 0.72.0 this section said "scripted, no pause": fill the
username and password from `.env.qa-agents`. Through an MCP tool that
places the password in the transcript; the runs that worked had the
user sign in by hand.)

## Evidence — what the backend can actually write

Since 0.47.0 **every PASS gets a `§n` reading too**, and every `[core]`
PASS a screenshot (`<ISSUEKEY>-r<N>-<TC-ID>-pass.png`): the step-5
evidence audit re-reads them (`../../qa-pipeline-code/references/evidence-audit.md`).
A PASS reading is short — URL, signed-in role, the quoted text or
aria excerpt that satisfies the case's expected result, timestamp; no
console lines unless something was logged. **The file's shape** (both
backends, every round — the audit's "Evidence cited" column assumes
it): `# <ISSUEKEY> - Web evidence` as the first line, then one section
per reading, numbered in the order written and never renumbered on
resume:

```
## §<n> — <TC id> · <verdict>

URL: <page URL> · as <signed-in role / account label — never the password>
Seen: <the quoted text or aria excerpt that decides the verdict, verbatim>
Expected: <the case's expected result, one line>
Screenshot: <evidence/<ISSUEKEY>-r<N>-<TC-ID>-pass|fail.png, or "none">
At: <timestamp>
```

On every FAIL / FAIL CONFIRMED record, in this order of preference:

1. **The screenshot, straight into `$EP_QA_HOME/evidence/`.** The
   Playwright MCP server writes only inside its output directory, so the
   server is started with `--output-dir` pointing at
   `$EP_QA_HOME/evidence/` (README → "Before you run"; `environment.md`
   layout). Take the screenshot with an **absolute** `filename:
   <$EP_QA_HOME resolved>/evidence/<ISSUEKEY>-r<N>-<TC-ID>-fail.png`
   (`-pass.png` for a `[core]` PASS) — never a bare name: the server
   can resolve a relative name against the workspace, i.e. this plugin
   checkout, which must hold no run artefact. The round is in the name
   because the store is flat. The report row cites
   `evidence/<ISSUEKEY>-r<N>-<TC-ID>-fail.png`. No copying step.
   (EP-56197 open-items #12: the earlier "screenshot into the sandbox,
   then copy with host tools" rule left every Playwright FAIL without
   its screenshot for two rounds.) The tool reports a path outside
   `$EP_QA_HOME/evidence/` anyway (output directory not configured, or
   the write refused) — say so once in the report, move nothing into
   the checkout, and fall to 2.
2. **The documented equivalent — always written:**
   `<ISSUEKEY>-web-evidence.md` in the run folder, one numbered section
   per FAIL (and, short form, per PASS / FAIL REJECTED — above): the URL, the exact DOM / text reading that contradicts the
   expectation (aria snapshot or `inner_text` excerpt, quoted), the
   console lines captured **before** navigating away, the timestamp.
   The report row cites `web-evidence.md §n` — that reference is what
   the run's roster note carries (`test-runs.md` → evidence), because
   an on-disk screenshot cannot be uploaded there anyway.

A FAIL with a `§n` reading and no screenshot is compliant; a FAIL with
neither is not a FAIL, it is a claim — and since 0.47.0 the same holds
for a PASS. (Until then: "nothing is captured for PASS — evidence noise
costs tokens and review time". The cost is a few lines per case; the
saving was that a wrong PASS had nothing anyone could re-read, and it
reached the walk plan as "settled".)

## Known risks

- SSO / 2FA on some hosts — the user completes it in the same hand
  sign-in (SKILL.md → Step 4).
- `navigation_paths.json` memory is less critical (deep-linking
  works), but keep writing it — the extension fallback still uses it.
- A server started without `--output-dir` writes to a per-session temp
  folder that is gone with the session. The report row shows it (a
  path outside `$EP_QA_HOME`): fall to the `§n` reading, and tell the
  user the one-line reconfiguration.
- Playwright's Chromium can rarely render differently from the user's
  Chrome — note it in the report when a case looks suspiciously off.
