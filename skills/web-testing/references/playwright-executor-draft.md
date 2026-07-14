# Playwright executor — DRAFT (not active)

Status: **draft, unpiloted.** The active executor is the Claude in
Chrome extension, and SKILL.md's "do not use the Playwright MCP" rule
stands until a pilot on a real ticket proves this alternative. Use
only when the user explicitly asks to pilot Playwright.

## Why consider it

The extension is interactive but non-reproducible: no traces, no
scripted re-runs, screenshots by hand. Playwright gives scripted
runs, `trace.zip` artifacts, auto-waiting, and deterministic
re-execution of the same test case on the next regression pass.

## Contract stays identical

Everything in SKILL.md except the executor is unchanged: same inputs
(code-review + test-cases + checklist), same scope rule (only `[UI]`
QA/FAIL), same classification (PASS / FAIL / FAIL CONFIRMED / FAIL
REJECTED / BLOCKED / OBSERVATION), same escalation rule, same output
template. Only the "how a step is executed" changes.

## Tool mapping

| Extension tool | Playwright equivalent |
|---|---|
| `navigate` | `page.goto(url)` |
| `find` (natural language) | `page.get_by_role/get_by_label/get_by_text` — prefer role+name |
| `read_page` | `page.aria_snapshot()` |
| `computer` click/type/key | `locator.click()` / `locator.fill()` / `page.keyboard.press()` |
| `form_input` | `locator.fill()` / `select_option()` |
| `get_page_text` | `page.inner_text("body")` |
| screenshot (FAIL evidence) | `page.screenshot(path=...)` + keep `trace.zip` |

MUI notes from browser-rules.md still apply (selects are buttons +
listbox portals; date pickers need keyboard entry).

## Login

Reuse login-config.md values; credentials via env / e2e `.env`, never
inline. Persist auth state (`context.storage_state`) per host so one
manual login (or scripted modal login) covers the run.

## Pilot checklist (do this once before adopting)

1. Pick one closed ticket with a finished web-testing report as the
   baseline (e.g. a recent EP story from this repo's run files).
2. Run the same QA/FAIL scope via Playwright headed mode on alpha2.
3. Compare: same statuses? login/2FA friction? MUI widget failures?
   time per case vs the extension?
4. Decide: replace the executor, keep both (Playwright for regression
   re-runs, extension for exploratory), or drop.

## Known risks

- Login modal / SSO / 2FA on alpha hosts may block scripted login —
  fall back to manual login + saved storage state.
- `navigation_paths.json` memory is less valuable (Playwright can
  deep-link), but keep writing it for the extension path.
- Cowork sandbox may lack a display; headed debugging belongs in
  Claude Code on the host machine.
