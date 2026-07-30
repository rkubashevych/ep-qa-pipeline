# Run sheet format

The deliverable is a workbook whose first sheet is the only thing the
tester needs open. Everything else is reference material they consult
when something looks wrong.

## Sheet 1 — Run sheet

Six columns, in this order. Nothing else belongs here.

| TC | Log in as | Do | Expect | Result | Notes |
|---|---|---|---|---|---|

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
SKIPPED.

**Notes** — left empty. The tester's own words.

### Row states

Rows that are not runnable still appear, so the case is visibly
accounted for rather than silently missing:

- **NEEDS FIXTURE** — put the blocker in **Expect** prefixed `BLOCKED —`,
  naming what would unblock it and who can provide it. Grey the row.
- **ALREADY SETTLED** — pre-fill **Result** with the existing verdict and
  put its source in **Notes** (`from code review`, `from API testing`).
  The tester skips it unless they want to confirm.

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

## Sheet 4 — Reference

Per-case detail the run sheet deliberately omits: the full precondition
that was established, prior automated verdicts with their source stage,
and any caveat the tester needs only if a row misbehaves (known
environment faults, timing requirements, surfaces that disagree).

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
