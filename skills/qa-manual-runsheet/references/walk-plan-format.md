# Walk plan format — `<ISSUEKEY>-walk-plan.md`

**Contents:** Why a plan and not a sheet · The header · Sessions ·
The card · The backstage block · Card kinds · Voice rules (the part
that matters) · The coverage map · Credentials · What must not happen

The walk plan is what stage 9 hands to the human round since 0.31.0.
`qa-manual-walk` reads it and presents one card at a time in chat; the
optional run sheet (`runsheet-format.md`) is generated *from* it for a
tester who prefers a file. The plan is a **view** of the QA Service
suite — never an input to any automated stage, never a place to fix a
case.

## Why a plan and not a sheet

The run sheet had to carry everything in every cell: the account, the
action, the pass condition, the machine's evidence, the caveat, the
harness command, the scope disclaimer — because nobody is there to
answer a question. On a real ticket (EP-56998) that produced Do and
Expect cells of 500–1500 characters each, seven reference columns the
tester had to read past, and five sheets. Technically complete, and the
tester could not concentrate on it.

A plan separates the two audiences. The **card** carries only what the
tester needs to act — who, do, see — in plain language. The
**backstage** block carries everything the agent needs to answer
questions, judge an answer honestly, and run a case itself. Same facts,
same rigour, two registers.

## The header

```
# EP-56998 — walk plan

Run: <QA Service run id> · <title>              (or "no run — <why>")
Round: r1 · Env: alpha2 · Event: 3551 · Portal: https://<host>
Plan built: 2026-09-08 by qa-manual-runsheet 0.31.0
Cases in scope: 14 → cards: 11 in 3 sessions · settled without a card: 3
REQs walked: 5/5 (map at the end)
Fixtures: EP-56998-testdata.json (verified 2026-09-08 12:0x UTC, 3 logins proven)

## Before you start
- <one line per thing that is true for the whole walk: where to log in,
  a global wait, a host that is down. Three lines is a lot.>
```

## Sessions

Cards are grouped into **sessions**, one per login account, ordered the
way a tester moves: log in once, do everything that account does,
surfaces in the order the product presents them. Sessions run in
product-role order — admin → organiser → exhibitor → visitor — so the
set-up a higher role performs is in place before the role that sees its
effect logs in; a plan that needs another order says why in the
header. Within a session, destructive cards come last. A session opens
with its account line:

```
## Session 1 — as Anna, an opted-out viewer
Log in as: qa-viewer-optout@example.test / Pw!example1  (id 12345)
Why this account: she has consent = off, so every visibility case reads from her.
```

**One account per session, one account per card.** Stage 9's rule 1
("one explicit Log in as") stands — it is just stated once per session
instead of once per row, and a card that genuinely needs a second
account is a card in that account's session, or a numbered switch
inside **Do**. Never two accounts side by side for the tester to pick
from.

## The card

```
### Card 4 · TC-REQ-3.2 · favouriting a brand you may not see   WALK · High · [core]
Do: Open Marketplace → Brands and click the star on the "Northwind" card.
You should see: the star stays empty and nothing is added to your Favourites.
Backstage:
  kind: WALK
  machine: CR PASS · API — · WEB NOT EXECUTED
  why-walked: [core] of REQ-3; High risk; code-reading-only PASS
  source: AC-4 · REQ-3 clause "a viewer without consent cannot favourite" (Confluence AC §2.1)
  positive-control: Anna's existing favourite "Contoso" must still show in Favourites
  half-observable: no
  covers: TC-REQ-3.3 (same surface, same fixture — a second star)
  entity: brand "Northwind" id 88112 (owner 186933) — zero baseline read twice 12:01/12:03 UTC
  wait: —
  scope: —
  say-first: —
  retest: —
  how-to: Favourites is the heart icon in the top bar
```

The header line: card number (conversation handle), the case id (the
join key), a **title that is a sentence a tester would say**, then the
kind, the risk, and `[core]` when the case is the REQ's representative.

**Do** — one to three lines, second person, imperative. Names the screen
as the UI labels it, then the control, then the entity by its visible
name. Numbered only when order matters.

**You should see** — one to two lines, what is visible. For an absence
check the positive control is in the same sentence ("the list is empty
**and** the counter reads 1"). For a half-observable case, what the
tester can see, and that the rest is checked another way.

## The backstage block

Fixed keys, in this order, `—` when empty. The agent reads all of them;
the tester sees none unless they ask or a rule says to volunteer one.

| Key | Holds |
|---|---|
| `kind` | WALK · SPOT-CHECK · AGENT-RUNS · BLOCKED · DEVICE (below) |
| `machine` | the stage 6 / 7 / 8 verdicts, one per stage, verbatim status names from `status-vocabulary.md` — e.g. `CR PASS · API — · WEB NOT EXECUTED`; `—` for a stage that did not hold the case |
| `why-walked` | the selection reason from step 2a: must-walk / `[core]` / VERIFY (High-risk or code-reading-only PASS) / risk extra / SPECIAL ATTENTION |
| `source` | the ledger id, register row and verbatim clause the expectation rests on (`AC-<n> · REQ-N clause "…" (<document §>)`; `sources-of-record.md`) — or `OBSERVATION (no source checked)`. A tester who asks "which AC is this?" gets the id. |
| `positive-control` | for absence checks: the visible fact that proves the state existed |
| `half-observable` | `no`, or which half the tester sees and which machine verdict owns the rest |
| `covers` | other case ids this card settles, with the one-clause reason |
| `entity` | ids, owners, verified baselines — everything that used to sit in the Entities sheet |
| `wait` | a required delay for lagging surfaces, with the surface named |
| `scope` | when a FAIL here would not be the PR's fault — what the PR does and does not touch |
| `say-first` | the ONE sentence the agent must say before the tester judges (a wait, a scope warning). Empty on most cards. |
| `retest` | prior verdict, defect key, date — on retest rounds |
| `how-to` | where a thing is, how to obtain an input (a token from the MORE link, a code from an email) |
| `run` | AGENT-RUNS only: the exact call or harness line the agent executes, the human-only input it needs, the write-safety class (read-only / snapshot-revert / throwaway) |
| `blocked` | BLOCKED only: the probed reason, the probe (what was checked, when), the unblock and who can supply it |

## Card kinds

- **WALK** — the tester acts and observes. Default.
- **SPOT-CHECK** — a machine PASS the error model distrusts (`[risk:
  High]`, or any PASS whose only evidence is code reading). Trimmed to
  the fastest action that would expose a wrong PASS. Same presentation
  as WALK; `why-walked` says so. Never dropped: about half of
  unverified machine PASSes have historically been wrong.
- **AGENT-RUNS** — the case is a request. Nothing with an HTTP verb, an
  endpoint, a status code, a curl line or a file path is a human card.
  **Do** says what the tester supplies ("paste me the token from the
  MORE link in the meeting email"); **You should see** says what the
  agent will report ("I'll show the call; it should return 200 with a
  token in the body"). The `run` key holds the actual call.
- **BLOCKED** — stage 9 could not make it runnable and **probed the
  reason** (rule 5). **Do** is the unblock, in one line; **You should
  see** is what would pass once unblocked. `blocked` holds the probe.
- **DEVICE** — needs a phone or another instrument only the tester
  holds. WALK with the platform named.

Cases the machine settled with runtime-grade evidence at Low/Medium
risk get **no card** — they are listed in the coverage map as
`settled (<status>, <source>)`. A tester who wants to see one asks the
agent.

## Voice rules — the part that matters

The card is read by a person who may never have opened the ticket, mid-
test, on a second screen. Every rule below was broken by a real sheet.

1. **Who, do, see. Nothing else.** No WHY, no MUST NOT HAPPEN block, no
   SCOPE warning, no HALF-OBSERVABLE label, no machine verdict, no
   quoted PR text. Every one of those has a backstage key. A card that
   needs a caveat *before* judging gets one `say-first:` sentence.
2. **Say the screen, not the intent.** "Open Marketplace → Brands and
   click the star on the Northwind card", not "attempt to favourite a
   brand". Use the labels the UI shows.
3. **Say what you will see, not what the system does.** "The star
   stays empty and nothing appears in Favourites", not "the action is
   blocked and no favourite row is written". The row is the agent's
   business.
4. **No ids in the sentence unless the tester must type them.**
   Entities by visible name; ids in `entity`. An id the tester needs
   (an event number in a URL) goes in parentheses at the end.
5. **No HTTP verbs, endpoints, status codes, curl, DevTools recipes, or
   file paths in a human card.** If the case is that, it is
   AGENT-RUNS. The tester supplies the token; the agent supplies the
   request.
6. **Absence checks carry their positive control in the same
   sentence.** "The interactions list is empty and PAGE LIKES reads 1."
   A card that says only "nothing appears" is not finished.
7. **Half-observable cards say so in one clause** — "the star lights;
   I'll check how it was stored" — and the `half-observable` key names
   the machine verdict that owns the rest.
8. **Length: Do ≤ 3 lines, You should see ≤ 2 lines.** A card that
   needs more is two cards or an AGENT-RUNS card.
9. **The title is a sentence the tester would say** — "favouriting a
   brand you may not see", not "REQ-3 negative partition — consent
   denial path". The technique is the agent's business.
10. **The test:** could a colleague who has never read the ticket do
    this card and tell you pass or fail from what they saw? If not,
    rewrite it.

## The coverage map

At the end of the plan, one line per REQ of the ticket:

```
## Coverage
- REQ-1 — Card 1 (TC-REQ-1.1 [core]) · Card 2 (TC-REQ-1.3) · settled: TC-REQ-1.2 (PASS, api-testing)
- REQ-2 — Card 3 (TC-REQ-2.1 [core], covers TC-REQ-2.2)
- REQ-3 — Card 4 (TC-REQ-3.2 [core], covers TC-REQ-3.3) · Card 5 (TC-REQ-3.1 SPOT-CHECK)
```

No behavioural REQ may read machine-only — that is step 2a's floor.
`[core]` nominations made for an older suite are recorded in
`<ISSUEKEY>-open-items.md` as before.

## Credentials

The plan carries **throwaway** account passwords in the session lines —
accounts stage 9 created for this run, random password each, retired
at stage 10 — and that is what makes it usable. It lives under
`$EP_QA_HOME/runs/`, never attached to Jira, never pasted into a suite
note. A `.env.qa-agents` account (admin, organiser) is **never**
written into a plan: its session line reads `Log in as: the admin
account from your .env.qa-agents` (`../../qa-pipeline/references/environment.md`
→ Secrets in chat). Examples in this file use `example.test` addresses
and obviously synthetic passwords. Everything in `runsheet-format.md`
→ Credentials applies unchanged.

## What must not happen

- A card with an HTTP verb, a curl line, or a status code in **Do** or
  **You should see** that is not AGENT-RUNS.
- A card with more than one account.
- A card whose **You should see** is an absence with no positive control.
- A BLOCKED card whose `blocked` key has no probe.
- A behavioural REQ with no card in the coverage map.
- A caveat, scope warning, or machine verdict in the card body.
- A plan that reads like the old sheet with the columns turned into
  lines. If the tester still cannot concentrate on it, the voice rules
  were not applied.
