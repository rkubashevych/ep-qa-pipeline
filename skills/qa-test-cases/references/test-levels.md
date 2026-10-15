# Test levels — the `Level:` line (0.50.0)

Mirrors QA Service's `test-planning-and-design` skill, section "Level
Assignment Rules", at digest **`19d88114a5dd`** (read 2026-10-14 with
`get_skill test-planning-and-design`). When the export file's `QA
Service skills:` line shows another digest, re-read that section and
update this file with a CHANGELOG entry
(`../../qa-pipeline-docs/references/qa-service-first.md` → "Keeping up
with QA Service").

## Two different questions

- The **channel tag** (`[UI]` / `[API]` / `[API][UI]` / `[mobile]` /
  `[export/email]`) says how THIS pipeline verifies the case at runtime,
  on a test environment. It routes the case to api-testing, web-testing
  or the manual round. Unchanged.
- The **`Level:` line** says at which automation level the behaviour
  should be PROVEN in the product's test suites — QA Service's level
  codes. It feeds `levels` at publish, the Coverage-by-level table and
  the implement workflow. It does not change who runs the case here.

A case without a `Level:` line gets the level its channel implies
(`qa-service-publish.md` → "Test cases → `create_test_case`", the `channel tag → level` row), exactly as before
0.50.0.

## The rule

Pick **the lowest level that can verify the behaviour without faking
the thing being tested**: Unit < Integration < API-E2E < E2E (UI).

| Code | Level | Choose when |
|---|---|---|
| `U` | Unit | a pure rule: a parser, validator, formatter, sanitiser, calculator, mapping — testable without booting the app |
| `I` | Integration | real persistence or real wiring, no HTTP: a repository writes what the entity holds, an event reaches its subscriber, an export task builds rows from the DB |
| `AE` | API-E2E | the HTTP surface: status, envelope, auth, validation errors, cross-endpoint state |
| `C` | Contract | field names, types, required / optional, null-when — the shape a consumer relies on |
| `E2E` | E2E (UI) | a real browser is the only way to see it: a page journey, rendering, client-side tracking |
| `CFE` | Component-FE | one FE component, hook or mapper in isolation |
| `PAE` | Prod API-E2E | a live integration against real data — never on a test env, so never from this pipeline |
| `Perf` | Performance | a latency, throughput or memory budget stated in the requirement |
| `M` | Manual | past the limit of automation: visual judgement, a real device, a real mailbox, a downloaded file read by eye |

## Two invariants

- **Business logic is never covered only through the UI.** A rule whose
  only case is `E2E` or `M` gets a lower level as well.
- **One case, several levels, when the facets differ** — a pure-logic
  facet plus a wiring smoke: `Level: U + AE`. Never split one scenario
  into two ids just to carry two levels.

## Worked example — EP-55889 (export cell sanitising)

`ExportHelper::prepareCellString` keeps `Budget <5k, prefer >10 units`
unchanged. The pipeline verifies it by exporting a fixture meeting and
reading the Message cell (`[export/email]`, a human reads the file). The
rule itself is a pure function:

```
### TC-REQ-6.3 — Description containing < and > is exported unchanged  [export/email]
Level: U + M
```

`U` is the regex on its own (the developer's `PrepareCellStringTest`
proves exactly this); `M` is the cell in a real file. Before 0.50.0 the
case could only be `M`, and the suite read "0 Unit" while a unit test for
it already existed.

## Don't

- Don't write `Level:` to balance a pyramid. The shape is risk-driven.
- Don't pick `PAE` — the pipeline never tests against real customer
  data.
- Don't invent codes. The list above is QA Service's vocabulary; any
  other value collapses the level table to zero.
