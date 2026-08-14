# Run sheet format

**Contents:** Sheet 1 — Case index (columns, row states incl. VERIFY
spot-check, colour spec + REJECTED muted palette, formatting) ·
Sheet 2 — Accounts · Sheet 3 — Entities · Sheet 4 — Reference ·
Sheet 5 — Environment · Credentials · What must not happen

The deliverable is a workbook whose first sheet is the only thing the
tester needs open. Everything else is reference material they consult
when something looks wrong.

## Sheet 1 — Case index

**Twelve columns. Resist adding more.** Every extra column is noise the
tester has to scroll past to reach the three that matter.

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC | Title | Ch. | Risk | Code review | API verdict | Ready? | **Log in as** | **Do** | **Expect** | Result | Notes |

H, I and J replace five old columns — `Account(s) to use - id · login /
password`, `Entity/entities to use`, `What to do (one line)`,
`Precondition already in place`, `Caveat / watch out`. Entity ids move
into the steps where they are needed; precondition and caveat merge into
the pass condition instead of sitting two columns away from it.

**Deliberately not columns:**

- **UI verdict** — one automated-verdict column is enough context. A
  stage-8 result goes in Notes when there is one.
- **How the case is run** — that belongs at the top of **Do**, not in its
  own column (see below).

### Can a human even run it? Put it in Do, not a column

The channel tag says **who runs the case in the automated pipeline**. It
does not say whether a person can run it by hand. Where they differ, open
the **Do** cell with a one-line marker:

- a click produces exactly that request → say so: *"This click IS the
  case — the card sends POST /profile/connect {type:visitor, id:…}"*
- the UI cannot produce the payload → *"⚠ Clicking twice will NOT work,
  the star toggles. Trigger it, then DevTools → Network → Copy as fetch →
  re-run."*
- no UI path exists → give the request, and point at the token recipe on
  the Environment sheet
- not manually observable → say why, and who could obtain it

Two mistakes this prevents:

- **Assuming a toggle can duplicate.** A favourite star toggles, so
  clicking twice *unfavourites* — it can never produce the duplicate a
  400-on-duplicate case needs.
- **Overstating what a click proves.** Clicking a star shows the star lit;
  it does not show the stored row is typed `exhibitor`. Where only part of
  an assertion is observable by hand, say so in **Expect** and name which
  half the automated stage owns. Half-verified is not verified.

Keep A–H dim (9pt grey is enough) — they are reference, not instruction.
I–K carry the work. L–M are the tester's.

**TC** — the case id, e.g. `TC-REQ-12.2`. Frozen column.

**Log in as** — exactly one account: display name, email and password
inline, with the numeric id in brackets. One line, copy-pasteable.

> `qa-viewer-optin@example.test` / `Pw!example1` (12345)

If the case needs a second session, either split it into two rows or
make the switch an explicit numbered step in **Do** — never leave two
accounts side by side for the tester to choose between.

**Do** — concrete, numbered if more than one action, naming the surface
and the entity by name *and* id:

> 1. Open Marketplace → Brands
> 2. Click the star on any brand card

**Expect** — the pass condition, judgeable without opening another file:

> Action blocked, no favourite recorded. Star stays empty.

Where the case is an absence check, the Expect must carry the positive
control in the same cell:

> Interactions list empty **and** PAGE LIKES reads 1

**Result** — left empty, with a dropdown: PASS / FAIL / BLOCKED /
SKIPPED, **and conditional formatting so the cell recolours itself when a
value is picked**. A dropdown that only changes the word is a missed
opportunity: the tester should be able to see the shape of the run by
scrolling, without reading.

**Notes** — left empty. The tester's own words.

### Colour — reuse the existing palette, do not invent one

**Use the hex values already in `build_data_pack.py`.** They were chosen
for this workbook, testers are used to them, and — crucially — they are
saturated enough to tell apart at a glance.

| Meaning | Values | Fill | Font |
|---|---|---|---|
| good | PASS · READY | `E2EFDA` green | `375623` |
| bad | FAIL · High | `FCE4D6` peach | `833C00` / `C00000` |
| attention | QA · PARTIAL · MUST TEST · Medium | `FFF2CC` amber | `7F6000` |
| not run | BLOCKED · NOT EXECUTED · N/A · Low · — | `F2F2F2` grey | `808080` |
| skipped | SKIPPED | `D9E1F2` blue | `1F4E78` |

Header: `1F4E78` navy, white bold.

**One body font throughout: Arial 10.** Do not set a monospace font on
the credential column. It was tried — the reasoning being that `l` vs `1`
and `O` vs `0` are easier to tell apart in a fixed-width face — and it
reads as a mistake in the grid, because one column in a different typeface
looks broken rather than deliberate. Consistency wins; if a password is
genuinely ambiguous, the tester copies and pastes it anyway.

Applied per value to `Risk`, `Code review`, `API verdict`, `Ready?`
(D–G) and `Result` (K). Use `EXACT()` rather than `SEARCH()` so a
compound value cannot match two rules, and set `stopIfTrue` on each.

**A muted pastel palette was tried and rejected.** Softer tints looked
calmer in isolation but were indistinguishable in a grid — the tester
could not tell amber from cream from grey, and stopped trusting the
colour at all. Distinguishable beats gentle. If a colour needs squinting
at, it is doing nothing.

Colour is still only ever a second signal: a blocked row also says
`BLOCKED` in `Ready?` and opens **Expect** with `BLOCKED —`, so the
meaning survives printing and colour-blindness.

**openpyxl trap:** differential-format fills are read by Excel from
`bgColor`, not `fgColor`. `PatternFill(fgColor=...)` inside a
`CellIsRule` writes `00000000` and produces no colour at all, silently.
Use `PatternFill(bgColor="E9F3EC")`. Verify by re-loading the saved
workbook and asserting each rule's `dxf.fill.bgColor.rgb` is not
`00000000` — the file opens perfectly fine while being wrong.

### Tinting rule (live)

- Tint columns A–K for row state and leave **Result** untinted, so the
  conditional-format colour reads cleanly instead of fighting the row.

### REJECTED — muted palette. Do not implement.

Recorded only so it is not reinvented (it was, once — the
`*-runsheet-calm-example.xlsx` iteration). Muted slate header `3E5C76`,
grey gridlines `D9D9D9`, pale tints (must-test `FDF6E3`, known-fail
`FBEDEC`, blocked/settled `F5F5F3`): calmer in isolation,
**indistinguishable in a grid** — the tester could not tell amber from
cream from grey and stopped trusting the colour at all. Distinguishable
beats gentle. The saturated palette in "Colour — reuse the existing
palette" above is the one and only spec; if two sections of this file
ever disagree again, the one the generator script implements wins and
the other must be moved under a REJECTED heading like this one.

### Row states

Rows that are not runnable still appear, so the case is visibly
accounted for rather than silently missing:

- **NEEDS FIXTURE** — put the blocker in **Expect** prefixed `BLOCKED —`,
  naming what would unblock it and who can provide it. Grey the row.
- **ALREADY SETTLED** — pre-fill **Result** with the existing verdict and
  put its source in **Notes** (`from code review`, `from API testing`).
  The tester skips it unless they want to confirm. Reserved for
  runtime-verified Low/Medium-risk verdicts only.
- **VERIFY (spot-check)** — Result left EMPTY (dropdown live), Notes
  carries `spot-check: machine PASS (<source>) — <why walked:
  High-risk / code-reading only / core — REQ representative>`. The
  Do/Expect are trimmed to the
  single fastest action that would expose a wrong PASS. Tint like
  READY, not like settled — these rows are work, not history. On a
  typical run this adds roughly the High-risk-PASS count in rows, not
  the full settled set.

### Formatting

- Freeze the header row and the TC column.
- Autofilter the header.
- Wrap text; row height auto. The tester reads whole cells, not
  truncated ones.
- Colour is a hint, never the only signal — a greyed row must still say
  `BLOCKED —` in text.

## Sheet 2 — Accounts

Every account provisioned: id, display name, email, password, consent or
role state, which cases it serves, whether it is single-use, and how to
reach it if a direct login is not possible. Flag retired accounts loudly
so nobody uses one.

## Sheet 3 — Entities

Every non-account fixture: id, name, type, owner, and — for anything used
in a counter case — its **verified zero baseline**, with a note that the
baseline was read twice.

**Covers column (K+1, after Result/Notes when present):** when one row
carries several cases, list them — `Covers: TC-REQ-3.1, TC-REQ-3.2`.
The tester's Result applies to all of them; a Note naming one case
overrides for that case only. Rows with no Covers entry carry just
their own TC.

## Sheet 4 — Reference

Per-case detail the run sheet deliberately omits: the full precondition
that was established, prior automated verdicts with their source stage,
and any caveat the tester needs only if a row misbehaves (known
environment faults, timing requirements, surfaces that disagree).

The Reference tab also carries the **coverage map**: one line per REQ —
which walked row(s) cover it (the REQ's `[core]` row at minimum), plus
`delegated to machine verdict (<status>)` for its unselected cases. No
REQ line may be blank, and no behavioural REQ line may read
machine-only; that's the selection's floor.

## Sheet 5 — Environment

Hosts, event id, how to log in, how to reach an account when direct
login is unavailable, known-broken endpoints, rate limits, required
waits. One table, no prose.

## Credentials

The run sheet necessarily carries throwaway test-account passwords —
that is what makes it usable. Two rules follow, and neither is optional:

- **The sheet and the provisioning record never enter version control.**
  They contain live credentials for accounts on a real environment.
  Write them to a path outside the repo, or ensure the repo ignores
  `*-runsheet.xlsx`, `*-testdata.json`, `*-testdata-notes.md` and
  `*-manual-test-data-pack.xlsx` before generating anything. Check, do
  not assume: on a real run these filenames matched no existing ignore
  rule and 84 account passwords were one `git add -A` from being
  committed.
- **Never put a real credential in this skill, its references, or any
  example.** Examples use `example.test` addresses and obviously
  synthetic passwords. A password pasted into documentation outlives
  every environment it was valid for.

Report in the notes file which accounts were created, so they can be
deactivated when the story closes.

## What must not happen

- A Result column with no Expect column beside it.
- A row naming more than one login.
- A blocked row whose reason was assumed rather than probed.
- An absence-check row with no positive control.
- Fifteen columns. If the tester has to scroll horizontally to see the
  pass condition, the sheet has failed.
