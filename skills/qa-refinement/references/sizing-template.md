# `<STORY>-sizing.md` — the QA sizing note

The file is written by `qa-refinement` step 5. It is for QA's own
estimate and is never posted to Jira unless the user asks. Keep it
short enough to read before a refinement meeting.

```
# <STORY> — QA sizing (<YYYY-MM-DD>)

QA sub-task: <KEY — summary> (human-created, adopt at publish) | none
Inputs: <N> requirements (<n> High risk) · <q> open questions posted (comment <id>)
Existing estimate on the ticket: <"QA 2d" (comment <date>)> | none

## Scope matrix
| Surface / area | Variants that multiply the work | In QA scope? |
|---|---|---|
| <page or area> | <views, drawer, roles, languages, settings on/off> | yes / ask (Q<n>) / no |

## Case count (rough)
<arithmetic, one line per area — e.g. "Sessions: 5 location types × 3 views ≈ 15 + search 5 + chips/reset 5">
Total ≈ <low>–<high> test cases (+ <s> structural checks)

## Effort
| Activity | Days (low–high) | Moves if |
|---|---|---|
| Test design + test data | | |
| Web execution | | |
| API execution | | Q<n>: is the API QA's? |
| Admin / settings | | |
| Retest + regression | | |
| **Total** | **<low>–<high>** | |

## Blocks execution
- <backend not started / not deployed — branch state from recon>
- <test environment + fixture data needed>
- <Q<n> gates REQ-<a>, REQ-<b>>
```

## How to derive the numbers — show the arithmetic

- **Case count.**
  - Start from the requirements file: one behavioural REQ is 1–3
    cases, a structural REQ is 0 cases and 1 structural line, and a
    `Risk:` REQ has 0 cases.
  - Then multiply only by the variants the requirements actually name:
    views, surfaces, roles, languages, a setting on and off.
  - Never multiply by a variant the ticket does not mention.
- **Effort.**
  - Anchor on the case count, not on a feeling. A typical web case takes
    10–20 minutes to execute, including data setup. An API case takes
    5–10.
  - Add test-data preparation separately when the fixture is non-trivial
    (several halls, settings in both states, two languages).
  - Add at least one retest round.
- **Ranges.** The low end assumes every open question gets the
  narrower answer and the environment is ready. The high end assumes
  the wider answer plus one retest round.
- **An existing estimate on the ticket** gets one line: when it was
  given and what was added since. Never overwrite it.

The first real use was EP-56227 (2026-09-29):
- 44 REQ → about 55–70 cases;
- about 5–6 days, against the 2d estimate on the ticket from 8 Sep. That
  estimate predated search, tri-state headers, chips and the
  custom-location rules.
