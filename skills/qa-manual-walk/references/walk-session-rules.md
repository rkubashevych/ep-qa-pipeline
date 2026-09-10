# Walk session rules — the conversation

**Contents:** What a turn looks like · Mapping words to verdicts ·
The positive-control question · Cards by kind · Questions the tester
asks · Deferring, skipping, stopping · The state file · Tone

The walk is the one place in the pipeline where the agent talks to a
person mid-test. These rules keep that conversation honest: the tester
supplies the observation, the agent supplies context on request, and
the verdict is always traceable to the tester's own words.

## What a turn looks like

One card, one question. The agent's message is the card as written in
the plan — header, account line when the account changes, **Do**,
**You should see** — optionally preceded by the card's `say-first:`
sentence, and followed by exactly one question: **What happened?**

Not in the message: the next card, the machine's verdict, the reason
the case exists, the coverage map, a progress line (unless due), any
reminder of the rules. The tester asked for a session, not a briefing.

Example of a complete turn:

> **Card 4 · TC-REQ-3.2 · favouriting a brand you may not see**
> *Still as Anna (qa-viewer-optout@example.test).*
> **Do:** Open Marketplace → Brands and click the star on the
> "Northwind" card.
> **You should see:** the star stays empty and nothing is added to
> your Favourites.
>
> What happened?

## Mapping words to verdicts

The tester answers in their own words. Map as follows and **always
store the words verbatim** as the note.

| The tester says (examples) | Verdict | What the agent does |
|---|---|---|
| "pass", "ok", "yes", "works", "as expected", "✓" | PASS | On a card with ONE visible pass condition: record and move on. On an absence-check or half-observable card: ask the positive-control question first (below). |
| any description of a mismatch — "the star lit up", "it shows 0", "I got a 500", "the button isn't there" | FAIL | Restate once, naming the expectation: "So the star lit — recording FAIL against 'star stays empty'. Right?" One confirmation, then ask for evidence once (screenshot / Jam link / the exact error text). Never nag for evidence. |
| "can't", "no access", "page won't load", "the account doesn't log in", "the email never came" | BLOCKED | Record the reason in the tester's words. Probe the blocker if it is something the agent can check from here (a login, a host, a fixture id) — a dissolved blocker turns the card back into a WALK card. |
| "skip", "not now", "not relevant" | SKIPPED | Ask for the reason in one clause if none was given; record it. A SKIPPED core card gets one sentence of pushback ("this is the REQ's only walked row") — once. |
| "later", "come back to this" | deferred | Card moves to the end of the walk. Not a verdict. |
| a question ("where is that menu?", "which account?", "why does this matter?") | — | Answer from backstage in one or two sentences, then re-ask "what happened?" |
| something partial — "the list is empty" on an absence check | — | Positive-control question, then map. |
| a report about the *case*, not the product — "this expectation is wrong, the button is called Save now", "this can't be done as a visitor" | case correction | Capture under `Case corrections` (case id, what is wrong, what the tester saw). Then ask: "test it against what the product actually does, or skip it?" and map that answer. |

Ambiguous words ("hmm", "sort of", "mostly") are not a verdict. Ask
what specifically differed. Never resolve ambiguity toward PASS.

A verdict once mapped can be changed by the tester at any time in the
walk ("actually, card 4 was a fail") — update the state file and say so.

## The positive-control question

Some cards cannot be judged from a bare "pass":

- **Absence checks** — "nothing appears", "the list is empty", "no
  email arrives", "the request is refused". These pass when the
  feature is broken and nothing was ever created. The card's **You
  should see** already pairs the absence with its positive control
  ("the list is empty **and** the counter reads 1"); the agent's job
  is to make sure the tester looked at both. Ask: *"and the counter?"*
  / *"and does the existing favourite still show?"* before recording.
- **Half-observable cards** — a click shows the star lit, not that the
  stored row is typed `exhibitor`. The card says which half the tester
  can see. The agent records the tester's PASS on the visible half and
  notes, in the results file, that the other half rests on the machine
  verdict named in backstage. Never let a half-observable card read as
  fully human-confirmed.
- **Lagging surfaces** — backstage says `wait: 45 min` or similar. The
  agent says it up front (`say-first:`), offers to defer the card to
  the end of the session, and on return asks when the action was
  performed before accepting a "nothing appeared".

## Cards by kind

- **WALK** — the tester acts, observes, answers. The default.
- **SPOT-CHECK** — a machine PASS the error model distrusts (High risk,
  or code-reading only). Same as WALK for the tester; the agent does
  not say "the machine passed this" before the answer — that is leading
  the witness. It may say so after.
- **AGENT-RUNS** — the case is a request the tester would otherwise
  paste into a terminal. The agent runs it under `api-testing`'s rules
  (read-only default; a write snapshots-and-reverts or uses the
  throwaway fixture stage 9 provisioned; credentials from `.env`, never
  echoed). The tester supplies only the human-only input the card
  names ("paste me the token from the MORE link"). The agent shows the
  call and result in ≤ 5 lines, states the verdict against the card,
  and asks the tester to confirm. Recorded as `source: machine`,
  principal `ep-qa-pipeline agent (<KEY> walk, witnessed by <tester>)`.
  A failed AGENT-RUNS call that looks like an environment problem (401
  on every call, host 503) is BLOCKED, not FAIL — and the agent says
  which.
- **BLOCKED** — stage 9 could not provision or probe it into being
  runnable. Re-probe before presenting. Still blocked → one-line
  reason, one-line unblock, "can you supply that now?". Not → BLOCKED,
  reason recorded, no further time spent.
- **DEVICE** — needs a phone or another instrument only the tester
  holds. Same as WALK; the agent asks for the platform in the answer
  ("iOS or Android, or both?") when the card covers both, and records
  the verdict per platform in the note.

`Covers:` lists — a card that carries several cases settles all of them
with one verdict. When recording, name them: "that settles TC-3.1 and
TC-3.2 as well". A tester who says "3.2 was different" splits the
verdict for that case only.

## Questions the tester asks

Answer from the card's backstage block, in plain words, in the
tester's language. Typical:

- *"Where is that?"* — the navigation path, or offer to say what the
  screen looks like. If the agent does not know, say so; do not guess a
  menu name.
- *"Which account again?"* — the session's account line, with the
  password (the plan holds it; chat is where it may be said, the
  results file is not).
- *"Why does this matter?"* — the source clause and the risk, one or
  two sentences. "The ticket's own acceptance criterion; a fail here
  is the bug it reports."
- *"What did the machine say?"* — the machine verdict and its source,
  after the tester has answered, never before.
- *"Is this the PR's fault?"* — backstage `scope:` line. Some cards
  carry a `say-first:` version of this because the tester must know it
  before judging; most do not, and it is said only when asked or when
  a FAIL lands.
- *"How do I get the token / code / email?"* — the `how-to:` line;
  for AGENT-RUNS cards the tester only needs to find and paste it.

## Deferring, skipping, stopping

- **Deferred** cards run at the end of the walk in the order deferred.
  A card deferred twice is asked about once more, then recorded as
  SKIPPED with "deferred twice, not run".
- **Stopping early** ("let's stop here", no answer for a long time,
  the tester says they'll continue tomorrow): write the results file
  with the cards answered so far and a `Not run` list, say plainly that
  nothing has been recorded anywhere, and how to resume. Do **not**
  hand to stage 10 — a partial write-back is a partial record, and the
  two-wave rule wants one human summary per round.
- **Stopping for good** (the tester says the rest will not be run):
  hand to stage 10 with the results file as it stands; the not-run
  cards are reported as not run, never as skipped or passed.

## The state file

`<ISSUEKEY>-walk-state.json`, written after every card:

```json
{
  "key": "EP-56998",
  "run": {"id": "…", "title": "EP-56998 bug-fix 2026-09-08 — alpha2"},
  "round": "r1",
  "tester": "qa-tester@example.test",
  "env": "alpha2", "event": 3551,
  "started": "2026-09-10T09:12:00Z", "updated": "2026-09-10T09:40:12Z",
  "position": 7,
  "cards": {
    "4": {"tc": ["TC-REQ-3.2"], "kind": "WALK", "verdict": "FAIL",
          "words": "the star lit up and Northwind is in my favourites",
          "evidence": ["https://jam.dev/c/…"], "source": "manual",
          "at": "2026-09-10T09:31:02Z"}
  },
  "deferred": [9],
  "corrections": [{"tc": "TC-REQ-5.1", "note": "button is now called Save"}]
}
```

No credentials in it, ever. It is the audit trail of the session —
stage 10 keeps it beside the results file and never deletes it.

## Tone

Short, warm, unhurried. The tester is doing the work; the agent is
holding the map. No emoji beyond the verdict marks in the summary, no
praise for passing cards, no apology for failing ones. When the tester
finds a real bug, say what it is in one sentence and move on to
evidence — the celebration is the record.
