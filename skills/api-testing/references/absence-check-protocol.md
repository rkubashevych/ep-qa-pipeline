# Absence-check & evidence-provenance protocol — shared reference

The single source of truth for when a PASS is allowed on checks that
assert something does NOT appear, or that read counters / analytics /
leads / statistics / notifications / dashboards. Binding on
**api-testing (stage 7)**, **web-testing (stage 8)**, and audited by
**qa-run-analyzer** (Evidence quality bucket). `qa-manual-runsheet`
already enforces the same rules for human runs via its
`references/provisioning-rules.md`; this file makes them binding on the
automated verdict-producing stages too.

Why this exists: on a real run, the story's central privacy claim
("zero records attributable anywhere") was recorded PASS by stage 7 and
endorsed by the run report — and reversed a day later. The favourite
had been created with `curl`, which never enters client-side tracking,
so the surfaces checked were guaranteed to be empty whether the feature
worked or not. A clean read from an instrument that cannot show a
failure is not evidence.

## Definitions

- **Instrumented surface** — anything whose value is produced by the
  tracking/analytics pipeline rather than read directly from the
  primary store: counters, leads, statistics endpoints, interaction
  dashboards, notification feeds, "recently active" style widgets.
- **Provenance** — how the precondition data came to exist: `UI`
  (performed in a browser by a person or browser agent) or `API`
  (curl/HTTP/script).
- **Absence check** — a case whose expected result is that something
  does NOT appear (no row, no name, zero count, empty list).

## The four rules

### 1. Provenance — API-created data cannot prove anything on an instrumented surface

A case whose assertion reads an instrumented surface may **not** be
classified PASS or PARTIAL if its precondition was created over the
API. Actions performed over the API frequently skip client-side
tracking entirely, so the surface stays clean regardless of whether the
feature is correct.

- In **api-testing**: classify it
  `NOT-TESTABLE (instrumentation)` and list it in the report's
  **"Route to web-testing"** section. Do not spend calls "confirming"
  emptiness first — the result is uninterpretable either way.
- In **web-testing**: create the precondition through the UI as part of
  the case, when the case's steps call for it. Where the no-unrequested-
  writes rule forbids creating it, PAUSE and ask the user to perform
  the precondition by hand, then continue — do not silently skip.

### 2. Positive control — an absence check with no proof the instrument works is VACUOUS

Before recording PASS on any absence check, the run must have observed
the SAME surface showing a value for data that is supposed to appear
(e.g. a deliberate public favourite that the counter does count). No
positive control in this run → the verdict is not PASS; record
`NOT-TESTABLE (instrumentation)` with "no positive control available"
as the reason, or arrange the control first.

A surface may not be cited as conclusive evidence in one case and
dismissed as unmeasurable in another case of the same run. If the
positive control never appeared, every absence-PASS read from that
surface in that run is void.

### 3. Ingestion lag — measure it, wait it, read twice

Instrumented surfaces ingest with a delay (30–60 minutes has been
measured on alpha2; do not assume, measure once per run using the
positive control's timestamp). An absence verdict requires a second
read **after** the measured lag has elapsed since the action. A single
immediate read is not evidence — rows appear later with their original
timestamps. Record both read times in the evidence.

### 4. "Anywhere" claims — enumerate or downgrade

A requirement of the form "appears nowhere / not attributable
anywhere" is only as strong as the list of surfaces actually read.
The evidence must enumerate each surface checked **per role** (admin,
organizer, exhibitor/target, third-party visitor). Organizer- and
target-side dashboards count; if any role's surfaces were out of reach,
the verdict is at most PARTIAL with the unchecked roles named — never a
bare PASS.

## Interaction with waiting rules

`browser-rules.md` says "never wait a fixed number of seconds — wait
for a specific element". That rule is written for presence checks and
is exactly backwards for absence checks: you cannot wait for an element
that must never appear. For absence checks the correct pattern is: wait
until the positive control is visible on the same surface (proves
ingestion has caught up), then read the absence.

## What the analyzer flags (Evidence quality bucket)

- 🔴 any absence-check PASS with no positive control recorded this run
- 🔴 any PASS/PARTIAL on an instrumented-surface assertion whose
  precondition provenance is API (or is unstated)
- 🔴 the same surface treated as conclusive in one case and
  unmeasurable in another within one run
- 🟡 any absence verdict recorded from a single immediate read (no
  second read after the measured lag)
