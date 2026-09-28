# Export checks — headers AND values, on every run

**Contents:** Why this file exists · The rule · The three layers ·
Fixtures that can fail · Verdicts · The profiler · Where each stage
applies it

One home for how the pipeline tests an **export of any kind**: an XLSX
or CSV download, a PDF agenda or badge, a report file, an emailed
attachment, a sync/integration payload. The stages point here; this file
changes, they do not.

## Why this file exists

EP-48506 (the schedule-agenda export refactor, 2026-09) went through
the whole pipeline and an RC regression, and shipped two defects that
were visible in the files the pipeline itself had saved:

- **EP-57871** — the Download Schedule XLSX Email column blank for
  every counterpart whose per-event record carried no copy of their
  email (admin-panel-created accounts). Reported from a live event
  (Groceryshop) two days after release.
- **EP-57884** — Job Title and Tel. blank on **every** row, for
  everyone (the export looked the value up under a renamed key).

The case that should have caught both, "Custom form fields appear as
XLSX columns", said *"Read the header row"* and expected *"each flagged
field appears as its own column"*. It passed — correctly, on its own
terms, with a causal proof that ticking a field made its column appear.
Nobody read a cell. The export saved from that run
(`EP-48506-export-41603.xlsx`, 2,052 rows) has **Job title filled on 0
of 2,052 rows** while its neighbours fill ~750. The RC check read the
header row of an export whose exhibitor had an empty schedule — zero
data rows, so zero values to be wrong.

A header proves the column exists. Only a cell proves the export works.

## The rule

> **Every export assertion checks the header AND the values, on every
> run — first run, retest, bug-fix, regression, RC check.** A header-
> only (or count-only, or "the file downloads") check is structure, not
> a verdict on the export's content, and never exits as PASS.

It is not a refactor rule. A new column, a changed query, a changed
fixture path, a new client configuration — any of them empties a column
while the header stays perfect.

## The three layers

Every export case (and every walk card or agent step that reads an
export) covers all three. Write them into the case; execute all three.

1. **Structure — the header row.** The expected columns are present,
   with the labels the source of record states, in the stated order
   where an order is stated. Optional columns (shown only when a setting
   is on or a value exists) are asserted in both states when the
   requirement defines both.
2. **Values — named cells.** For each asserted column, at least one
   fixture row whose cell must hold a **known value**: "the row for
   `zz_<key>_x3`, column Email, reads `zz_<key>_x3@…`". The expected
   value comes from the entity itself (what the account / exhibitor /
   session record holds, read before the export), never from an earlier
   export. Where the source leaves a cell legitimately empty, say which
   row is expected empty — that is a value assertion too.
3. **Fill profile — every column, every row.** The filled count per
   column over all data rows (`export_profile.py` below). **A column that
   is empty on every row is a finding until explained**: either the
   fixture holds no source value for it (then the fixture is incomplete
   — fix it or say the column is unverified), or the export is broken.
   When a baseline exists — an export of the same data from the build
   before the change, another environment on the old build, or a file a
   previous run saved — compare profiles: a column that had values and
   now has none, or lost most of them, is a FAIL candidate even when no
   case names it.

A **row set** check (the right entries are in the file, once each) is a
fourth thing some cases need; it does not replace any of the three.

## Fixtures that can fail

A value check is only as good as the data behind it (EP-57871: the
column filled for self-registered accounts and was blank only for
admin-created ones).

- **A distinctive value in every asserted column** for every fixture
  counterpart — `zz_<key>_jobtitle_x3`, not "Manager" — so a cell that
  shows the wrong person's value, or a stale copy, is caught.
- **Vary how the entity was created** when the column's value may be
  stored differently by path: admin-panel create, self-registration,
  REST / import. At least two paths per asserted column when the code
  review names more than one write path; record each fixture's path in
  the testdata notes.
- **At least one data row per export.** An export of an empty schedule
  verifies nothing but the header — say so, and it is structure only.
- Turn on whatever setting makes the column appear (e.g. "Include in
  Download Schedule"), snapshot the original, revert at the end
  (api-testing reference §9 / provisioning rules).

## Verdicts

| Evidence recorded | Verdict ceiling |
|---|---|
| structure + values + fill profile, all as expected | `PASS` |
| structure only (headers, counts, "the file opens") | `PARTIAL — structure only; values not read` — never PASS |
| a named cell wrong, or an asserted column empty where the fixture holds a source value | `FAIL` / `FAIL CONFIRMED` (Source + Clause as usual) |
| a column empty and the fixture holds no source value for it | that column is **unverified** — `BLOCKED (unverified)` for it, or fix the fixture; never PASS |
| an un-asserted column empty on every row, or dropped vs the baseline | a finding: `RISK-CR-<n>` row or `OBSERVATION (no source checked)` — never silently ignored |

A manual PASS on an export card follows the same ceiling: the card's
"You should see" names a cell value, so "the columns are there" is not
an answer the walk can record as a full PASS. It is a **Half** row
(structure confirmed by the human, values resting on the machine's
profile of the same export) when a machine value check exists, and
BLOCKED (`values not read`) when none does
(`../../qa-manual-walk/references/walk-session-rules.md` → the
positive-control question).

## The profiler

`../../api-testing/scripts/export_profile.py` — stdlib only (no
`openpyxl` needed), XLSX and CSV:

```
python3 skills/api-testing/scripts/export_profile.py FILE
python3 skills/api-testing/scripts/export_profile.py FILE --baseline OLD_FILE
python3 skills/api-testing/scripts/export_profile.py FILE \
    --expect 'Email|zz_ep57871 Member X3|zz_ep57871_x3@expoplatform.test'
python3 skills/api-testing/scripts/export_profile.py --selftest
```

It prints the header, the data-row count, each column's filled count
with two sample values, flags every column empty on every row, and —
with `--baseline` — every column whose fill dropped. `--expect
'COLUMN|ROW-MATCH|VALUE'` asserts that in the row(s) containing
ROW-MATCH, COLUMN holds VALUE (`VALUE` may be `<empty>`); exit code 1
on any failed expectation. ROW-MATCH is a verbatim substring of any
cell in the row, so match on a distinctive fixture value (`zz_<key>_x3`),
not on a prefix another fixture shares. Paste its output (no secrets in it — but
check: a cell can hold a password if a fixture was careless) into the
stage report's evidence for the case. PDFs: extract the text
(`pdftotext` / `pypdf`) and assert the named values in it the same way;
the profiler does not read PDFs.

## Where each stage applies it

- **qa-test-cases (stage 4)** — an export case's Exp names all three
  layers; header presence of an export is **not** a Structural check on
  its own (that is how the values fell out of scope) — it lives in the
  same case as the values.
- **code-review (stage 6)** — trace each asserted column to its **value
  source** (the query / field / key that fills the cell), not only to
  the header builder; a value source that changed between the old and
  the new code is a `RISK-CR-<n>` row even when the header code is
  untouched. Export contents stay QA (never code-PASS).
- **api-testing (stage 7)** — an HTTP-fetchable export is downloaded,
  profiled and value-checked; the report carries the profiler output.
- **qa-manual-runsheet (stage 9)** — an export card's "You should see"
  names a cell ("the Email cell in X3's row reads …") and asks for a
  glance for empty columns; fixtures follow "Fixtures that can fail".
- **qa-manual-walk / qa-manual-results (stage 10)** — a tester's
  "columns are there" on an export card is structure only, recorded as
  such, not PASS.
- **qa-run-analyzer** — audits it (§5 Evidence quality).
