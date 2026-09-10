# Example of test cases — the "Featured exhibitor" toggle (EP-0000)

**Contents** *(reader aid — not part of the format)*: the requirements ·
REQ-1 admin toggle · REQ-2 badge · REQ-3 sorting · REQ-4 API field ·
REQ-5 limit of 10 · REQ-6 badge in search · Structural checks ·
Statistics block

This example shows the expected level of detail, the format, the
application of techniques, the `[risk]` / channel / `[core]` markers,
and — since 0.40.0 — where structural checks go now that there is no
checklist file. It is the docs-phase output for the tracked fixture
`fixtures/EP-0000-context.md` (a synthetic ExpoPlatform story, not a
real ticket), so the smoke test in MAINTAINERS can be compared against
it. It uses the vertical block layout from `output-template.md` — no
wide tables.

Requirements for the example (as groomed — what stage 2 produced from
the fixture):

- REQ-1 `[risk: Medium]`: The exhibitor settings page in the admin
  panel shows a "Featured" toggle, default OFF, visible only to users
  with the `manage_exhibitors` permission.
- REQ-2 `[risk: High]`: When the toggle is ON, the public exhibitor
  list shows a "Featured" badge on that exhibitor's card. *(Badge text
  is an unresolved conflict: Confluence "Featured" vs Jira
  "★ Featured".)*
- REQ-3 `[risk: Medium]`: Featured exhibitors sort above non-featured
  exhibitors; within each group the existing alphabetical order is
  kept.
- REQ-4 `[risk: Medium]`: `GET /api/v2/exhibitors/{event_id}/list`
  returns a boolean field `featured` for every exhibitor.
- REQ-5 `[risk: High]`: A maximum of 10 exhibitors can be featured per
  event; switching the 11th toggle ON shows the validation message
  "Featured limit reached (10 per event)" and the toggle stays OFF.
- REQ-6 `[risk: Low]`: The badge also appears in the exhibitor search
  results, not only the main list.

---

# EP-0000 - Test cases

Requirements: runs/EP-0000/docs/EP-0000-requirements.md
Notes: ⚠️ REQ-2 badge text is an unresolved conflict (Confluence
  "Featured" / Jira "★ Featured") — cases written for both versions.
Generated: 2026-09-10

---

## REQ-1 — "Featured" toggle on the exhibitor settings page  [risk: Medium] [UI]

Applied techniques: Use Case, Decision Table (permission × visibility)

### TC-REQ-1.1 — Toggle switches ON and persists  [UI] [core]

Pre: logged in as an organiser with `manage_exhibitors`; event
  [data: the throwaway test event]; exhibitor "Northwind" [test data]
  has Featured = OFF
Steps:
1. Open Exhibitors → Northwind → Settings
2. Switch the "Featured" toggle ON
3. Save
4. Reload the settings page
Exp:
- After step 3 the page saves without a validation message
- After step 4 the "Featured" toggle reads ON
Post: Northwind is featured

### TC-REQ-1.2 — Toggle is absent without the permission  [UI]

Pre: logged in as an organiser WITHOUT `manage_exhibitors`
  [test data]; same event and exhibitor as TC-REQ-1.1
Steps:
1. Open Exhibitors → Northwind → Settings
2. Look for the "Featured" toggle
Exp:
- No "Featured" toggle is rendered on the page
- The rest of the settings page is unchanged

---

## REQ-2 — "Featured" badge on the public exhibitor card  [risk: High] [UI]

Applied techniques: Use Case, State Transition (OFF → ON → OFF);
  extended: both versions of the unresolved badge text are asserted

### TC-REQ-2.1 — Badge appears when the toggle is ON  [UI] [core]

Pre: Northwind has Featured = ON (TC-REQ-1.1); public exhibitor
  list of the event open in a visitor session
Steps:
1. Locate Northwind's card in the exhibitor list
2. Read the badge on the card
Exp:
- Northwind's card carries a badge
- version A (Confluence): the badge text is "Featured"
- version B (Jira): the badge text is "★ Featured"
- No other card carries the badge

### TC-REQ-2.2 — Badge disappears when the toggle goes OFF  [UI]

Pre: Northwind has Featured = ON and shows the badge (TC-REQ-2.1)
Steps:
1. As the organiser, switch Northwind's "Featured" toggle OFF
   and save
2. Reload the public exhibitor list as the visitor
3. Locate Northwind's card
Exp:
- Northwind's card carries no badge
Post: Northwind is not featured

---

## REQ-3 — Featured exhibitors sort above the rest  [risk: Medium] [UI]

Applied techniques: Use Case, EP (featured / non-featured partition)

### TC-REQ-3.1 — Featured group first, alphabetical inside each group  [UI] [core]

Pre: exhibitors "Aster", "Northwind", "Zephyr" [test data] on the
  event; Northwind and Zephyr featured, Aster not; public list open
Steps:
1. Read the order of the exhibitor cards from the top
Exp:
- The order is: Northwind, Zephyr, Aster
- Featured cards (Northwind, Zephyr) are alphabetical among
  themselves; the non-featured card follows

---

## REQ-4 — `featured` field in the exhibitor list API  [risk: Medium] [API]

Applied techniques: Use Case, EP (featured true / false)

### TC-REQ-4.1 — Every exhibitor carries a boolean `featured`  [API] [core]

Pre: same three exhibitors as TC-REQ-3.1; an admin token for the
  event
Steps:
1. GET /api/v2/exhibitors/{event_id}/list
   [data: event_id = the throwaway test event]
2. Read the `featured` field of every item in `data`
Exp:
- Every item has a `featured` field
- Its type is boolean (`true` / `false`, never `1`, `"yes"`, null)
- Northwind and Zephyr → `true`; Aster → `false`

---

## REQ-5 — Limit of 10 featured exhibitors per event  [risk: High] [UI]

Applied techniques: 3-value BVA on the count (9 / 10 / 11),
  Use Case (the validation message)

### TC-REQ-5.1 — The 10th toggle ON is accepted  [UI]

Pre: exactly 9 exhibitors featured on the event [test data];
  a 10th exhibitor with Featured = OFF
Steps:
1. Switch the 10th exhibitor's "Featured" toggle ON and save
Exp:
- The page saves without a validation message
- The toggle reads ON after reload
Post: 10 exhibitors featured

### TC-REQ-5.2 — The 11th toggle ON is refused with the message  [UI] [core]

Pre: exactly 10 exhibitors featured (TC-REQ-5.1); an 11th with
  Featured = OFF
Steps:
1. Switch the 11th exhibitor's "Featured" toggle ON
2. Save
Exp:
- The message "Featured limit reached (10 per event)" is shown
- The toggle reads OFF after the attempt and after reload
- The count of featured exhibitors on the event stays 10

### TC-REQ-5.3 — Turning one OFF frees a slot  [UI]

Pre: exactly 10 exhibitors featured; the 11th refused (TC-REQ-5.2)
Steps:
1. Switch one of the 10 featured exhibitors' toggle OFF and save
2. Switch the 11th exhibitor's toggle ON and save
Exp:
- Step 2 saves without a validation message; the toggle reads ON
- The count of featured exhibitors is 10 again

---

## REQ-6 — Badge in exhibitor search results  [risk: Low] [UI]

Applied techniques: Use Case

### TC-REQ-6.1 — Search result card carries the badge  [UI] [core]

Pre: Northwind featured (TC-REQ-1.1); public exhibitor search open
Steps:
1. Search for "Northwind"
2. Read the badge on the result card
Exp:
- The result card carries the "Featured" badge (same text as the
  list — see the REQ-2 versions)

---

## Structural checks  [UI]

> Presence / label / type / default-state checks — no scenario needed,
> no test case by design. Each line becomes one `EP0000-STRUCT-NN` case
> at publish; `REQ-N/struct-k` is its `detail.pipelineId`. Not counted
> in the test-case total.

- [ ] REQ-1/struct-1 [UI] The exhibitor settings page has a toggle labelled "Featured"
- [ ] REQ-1/struct-2 [UI] The "Featured" toggle is OFF by default on an exhibitor that was never featured
- [ ] REQ-2/struct-1 [UI] The badge is rendered on the exhibitor card itself, not in a tooltip or on hover

---

## Statistics

- Requirements covered: 6 (REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6)
- Requirements needing clarification: 1 (REQ-2 — badge text, two versions)
- Channel breakdown: [UI] 9 · [API] 1 · [API][UI] 0 · [mobile] 0 ·
  [export/email] 0
- Core cases: 6 (= behavioural requirements)
- Structural checks: 3 (not in the total)
- Total number of test cases: 10

---

*What this example is meant to show:* the toggle's presence and its
default (REQ-1) are structural lines, its behaviour is two cases; the
limit (REQ-5, High) gets the extended 3-value BVA the risk demands; the
API requirement (REQ-4) is one `[API]` case, not a structural line —
"the field is present in the response" needs a call; the unresolved
badge text is asserted in both versions rather than guessed; every
behavioural REQ has exactly one `[core]`; and every number in the
statistics block can be re-derived with `reconcile_counts.py EP-0000`.
