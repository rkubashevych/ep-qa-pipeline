# Browser interaction rules

The skill uses the Claude in Chrome extension for all
browser actions. These rules are mandatory for every
interaction with the page.

## General principle

Behave like a real user. Do not rush.
Wait for loading before an action. Wait for the result
after an action.

## Tools

The names of the Claude in Chrome extension tools:

| Tool | Purpose |
|------|---------|
| `navigate` | Go to a URL |
| `find` | Find an element by a natural-language description |
| `read_page` | Page structure (accessibility tree) |
| `computer` action: `screenshot` | Screenshot (only for FAIL evidence) |
| `computer` action: `left_click` | Click by coordinates or ref |
| `computer` action: `type` | Enter text |
| `computer` action: `key` | Press a key |
| `computer` action: `scroll` | Scroll |
| `computer` action: `scroll_to` | Scroll to an element by ref |
| `form_input` | Set a form field value by ref |
| `get_page_text` | Get the page text |
| `tabs_context_mcp` | List of tabs |
| `tabs_create_mcp` | Create a new tab |

## Interaction pattern

For each action (click, input, selection), follow
this sequence:

1. **See** — `read_page` or `find` to see
   the current state of the page and locate the element.
2. **Locate** — make sure the target element is visible.
   If it is not visible — `computer scroll` and repeat the search.
3. **Act** — `computer left_click`, `computer type`,
   `form_input`, etc.
4. **Verify** — `find` or `read_page` or
   `get_page_text` to see the result of the action.

Never skip steps 1 and 4.

## Waiting

- After `navigate` to a new page — `find` the key
  element that confirms the page has loaded.
  Do not start actions before confirmation.
- After a click that opens a modal, dropdown, menu —
  `find` the element that appears before the next action.
- After submitting a form — `find` a success message,
  a validation error, or check that `navigate` reached a new URL.
- Do not use `computer wait` with a fixed number of
  seconds. Always wait for a specific element or text.

## Finding elements

Priority:
1. `find` with a natural-language description — the most reliable.
   Examples: `find "Save button"`, `find "Email input field"`,
   `find "dropdown with label Region"`.
2. `read_page` with `filter: "interactive"` — to review
   all interactive elements.
3. `read_page` with `ref_id` — to focus
   on a specific part of the page.

If an element is not found on the first attempt:
- `computer scroll` down and try `find` again.
- `read_page` to check whether the page has loaded.
- After 2 failed attempts — BLOCKED for that test case.

## Entering data

- For text fields: `find` the field → `form_input` with the ref
  and value. Or `computer triple_click` to select
  → `computer type` with the new text.
- Before entering into a filled field — clear it:
  `computer triple_click` → `computer type` with the new
  value.
- For dropdowns: `find` the dropdown → `computer left_click`
  → `find` the option → `computer left_click`.
  Use `form_input` only for a native HTML `<select>`.
- For checkboxes: `find` the checkbox → check
  the current state → `computer left_click` only if
  it needs to change.

## ExpoPlatform UI notes (portal-ui: React + Material UI)

The product under test is `portal-ui`, a Next.js + React app built with
Material UI (MUI). Account for MUI's behaviour:

- **MUI `Select` is not a native `<select>`.** `form_input` will not
  work on it. Click the select to open the listbox, then `find` the
  option in the popup and click it.
- **Dialogs, menus, dropdown popups render in a React portal** at the
  end of the `<body>`, not next to their trigger. After opening one,
  `find` the option/element globally — do not assume it is nested under
  the trigger.
- **Buttons may be MUI components** with the label in a child element;
  `find` by the visible text rather than by tag.
- **Autocomplete fields** filter as you type — type a few characters,
  then `find` and click the matching option from the popup.
- **Toasts/snackbars** confirming success are transient — `find` the
  message promptly after the action.

## Interpreting test-case steps

How to translate a written test-case step into browser actions:

- "Open [page/form/modal]" → `navigate` to a URL or `find` +
  `computer left_click` on the element that opens it.
- "Enter [value] into [field]" → `find` the field by description →
  `form_input` or `computer type`.
- "Click [button]" → `find` the button by text →
  `computer left_click`.
- "Select [option] in [dropdown]" → `find` the dropdown →
  `computer left_click` → `find` the option → `computer left_click`.
  Or `form_input` with the value (native `<select>` only).
- "Check that [element/text] is displayed" → `find` the element or
  `get_page_text` and look for the text.
- "Scroll to [element]" → `computer scroll` or `find` +
  `computer scroll_to`.

For each step:
a. `read_page` or `find` — see the current state.
b. Find the target element.
c. Perform the action.
d. Verify the expected result — the per-step expected result if the
   step has one, otherwise the case's `Exp:` block after the final
   step: look for the text, element or state on the page via `find`,
   `read_page` or `get_page_text`.
e. Record the result of the step: it matches or it does not match.

## Error handling

- The page did not load (timeout, 500, blank) — try reloading once
  via `navigate`. If it did not help — BLOCKED for all test cases of
  that page.
- Session expired during execution — repeat the login (per
  login-config.md), continue from the current test case.
- Element not found after 2 attempts (including scrolling) — BLOCKED
  for that test case with a description of what was looked for and
  where.
- An alert or dialog appears — read the text, record it, close it and
  continue. If the dialog blocks execution — BLOCKED.
- The Chrome extension does not respond — stop, notify the user.

## Verifying expected results

Methods for checking the expected result:

1. **Text on the page** — `find` with the text
   or `get_page_text` and look for the substring.
   Example: expecting "Record saved" → `find "Record saved"`.

2. **Presence of an element** — `find` the element by description.
   Example: expecting a new field → `find "new field label"`.

3. **Element state** — `read_page` and check
   the attributes (disabled, checked, selected).

4. **Absence of an element** — `find` returns
   an empty result. Or `get_page_text` and check
   that the text is NOT present.

5. **URL changed** — after navigation, check
   the current URL via `read_page` or `get_page_text`.

If the expected result cannot be verified
by any method — mark BLOCKED with a description of what exactly
cannot be verified.

## Screenshots

- Take a screenshot only for FAIL and FAIL CONFIRMED —
  as evidence of the discrepancy.
- Do not take screenshots for PASS, BLOCKED, FAIL REJECTED,
  OBSERVATION.
- Do not show screenshots to the user in the chat — they are
  only for the agent's internal analysis.

## Login

The login sequence:
1. `navigate` to the login URL from login-config.md.
2. `find` the username/email field — wait for it.
3. `form_input` or `computer type` — enter the username.
4. `find` the password field.
5. `form_input` or `computer type` — enter the password.
6. `find` the login button.
7. `computer left_click` on the button.
8. `find` the element that confirms a successful login
   (dashboard, welcome message, user avatar).

Credentials are taken from the source specified
in login-config.md (environment variables, a .env file, etc.).

## Registration

If a test case needs a new user:
1. Read the registration instructions from login-config.md.
2. Perform the registration steps.
3. Save the new user's credentials in context
   for later test cases.

## New tabs

If a click opens a new tab:
1. `tabs_context_mcp` — check the list of tabs.
2. Switch to the new tab.
3. `find` the key element — wait for it to load.
4. Continue working in the new tab.

## Navigation memory

The file `navigation_paths.json` stores the paths
to the product's pages.

Format:
```json
{
  "navigation_paths": {
    "Page Name": {
      "url": "https://...",
      "login_required": true,
      "navigation_steps": [
        "Step 1: describe the action",
        "Step 2: describe the action"
      ],
      "last_used": "2026-06-18T12:00:00Z"
    }
  }
}
```

Rules:
- Paths are saved after the first successful run.
- Existing paths are not overwritten without asking the user.
- If a path from memory does not work (element not found,
  page changed) — ask the user for a new path
  and update the entry.
