# Recon — answer BEHAVIOUR questions by looking, before a human is asked

One home for the recon step. Two skills run it on the same terms:
`qa-pipeline-docs` (step 2) and `qa-refinement` (step 3).

Grooming marks every open item as one of two classes:
- **SPEC** — an intent decision only the PM/owner can make.
- **BEHAVIOUR** — "how does the app work today?", which is an observable
  fact.

A BEHAVIOUR item does not go to a human until observation has been
tried.

Real-run evidence:
- A docs run with recon ended with 1 open question; comparable runs
  without it posted 4–5, most of which could have been answered by
  looking.
- On EP-56227 (refinement, 2026-09-29), code recon settled 8 behaviour
  questions and the browser pass confirmed 3 of them. Two of those
  turned into sharper questions: the card still shows a custom location
  the filter would hide, and no filter survives a reload.

## The file

Write `<ISSUEKEY>-recon.md` in `runs/<ISSUEKEY>/docs/`. Open it with this
header, verbatim:

> These are observations of CURRENT behaviour, not requirements. They
> settle what a tester needs to know; they do not change the acceptance
> criteria. Where observed behaviour and the AC could diverge, the item
> is raised as a question, not resolved.

Then comes one section per BEHAVIOUR item (`B1`, `B2`, …). Each names
the REQ it serves, gives the answer in 1–3 lines, the evidence, and a
confidence (high / medium / low).

Fold the answers back into the requirements file under
"Resolved by observation (recon)" (one line per REQ). A recon fact:
- may ground an expected result ONLY where the requirement itself
  references current behaviour;
- never becomes a requirement;
- leaves the item open as a sharper question whenever it diverges from
  a requirement.

## Reuse — the file outlives the run that wrote it

`qa-refinement` and `qa-pipeline-docs` share `runs/<KEY>/docs/`, so a
docs run usually finds a recon file from refinement.
- **Never overwrite it.** Add new BEHAVIOUR items as the next `B<n>`
  sections, under a dated `## Added <date>` line.
- Re-check an existing section only when the REQ it serves changed
  since, or its clone tip is older than the integration branch's by a
  release. Record the re-check under the old section; don't replace
  it.
- Every earlier observation keeps its evidence, and grooming reads
  them before raising any BEHAVIOUR question.

## Order of sources — cheapest and safest first

1. **Existing docs.** Confluence "how it works" pages, and the Existing
   QA Service suite section in the context file.
2. **The code, when a local clone exists.** A constant, a threshold, a
   column list, a setting key or an empty-state string is a
   current-behaviour fact.
   - Clone location and rules:
     `../../pr-summary/references/bitbucket-access.md` → "Local clone".
   - **Refresh the clone first**, once per run: fetch plus
     fast-forward, then check that the index is not empty. A stale
     clone answers confidently from old code.
   - Record each clone's branch, tip commit and date at the top of the
     recon file.
   - Read the integration branch (`alpha`, `alpha-next14`), not a
     feature branch. A feature branch is planned behaviour and answers
     no BEHAVIOUR question. Its existence and last commit date are
     still worth recording, because they tell the estimate what exists
     yet.
   - Fan out with a read-only search agent when there are more than
     two or three items. Every answer carries repo + path + line and a
     short quote.
3. **The running system**, for three things:
   - what code alone leaves at medium confidence or below;
   - what a tester must see: rendered text, a reload, a setting's
     effect on a card;
   - every name the questions comment will use that no screen or label
     file has confirmed yet. That is the labels pass below, and it runs
     even when every behaviour item is settled.
   - Hosts: only hosts in `ALLOWED_HOSTS` (`environment.md`). Never
     production.
   - Login: the user signs in to admin by hand in the Playwright
     browser. There is no scripted login and no password in a tool
     call. A session left over from an earlier run is fine: check the
     page title and event, then carry on.
   - Screenshots go to `$EP_QA_HOME/evidence/` (the Playwright MCP's
     `--output-dir`). The run folder is outside its allowed roots, so
     name the file there in the recon section instead.

## Labels pass — the names the comment will use (0.47.1)

The questions comment names pages, toggles, tabs and messages. Each
name needs a row in the `## Names` table of `<KEY>-open-questions.md`
(`../../qa-pipeline-code/references/jira-writing-style.md` → "Every
name in the comment is a checked name").

The labels pass confirms the rows that are still `spec only`.
- **Label file first, when a clone exists.** Grep the view or
  translation file that renders the text on the integration branch:
  legacy admin `backend/admin/views/**.volt` + `backend/admin/langs/en.php`,
  admin-ui `src`, portal-ui `plugins/i18n/locales/en/translation.json`.
  - A hit gives a `label` source with file:line.
  - A label file is not proof the label is live, because the same
    setting can have two views. EP-55996's "Matchmaking sorting on
    Marketplace" is the label in `search/settings.volt`. The toggle
    admins actually use for that setting is labelled differently, on
    Networking & Matchmaking → Matchmaking. When a setting has more
    than one view, or a menu path is in doubt, confirm it on screen.
- **Then the screen, for every name still unconfirmed and every menu
  path.**
  - Open each page read-only and record:
    - the sidebar section and item;
    - the tab-strip label;
    - the page title;
    - the exact control text.
  - On the visitor side, run the flow the question describes. Example:
    search a word and read the tab number.
  - A typed search counts as a read. Saving a form does not.
- **Write the result back** to the Names table, with a `screen` source
  and the corrected name, and add a `B<n>` section to `-recon.md`.
- **A label pass can settle a question.** On EP-55996 the Exhibitors
  page already said "When searching by word or phrase, sorting is
  based solely on the relevance of the search results". That dropped
  a SPEC-looking question about matchmaking order.

The browser rules are the same as above. The user signs in by hand.
When the Playwright browser is held by another session ("Browser is
already in use"), use the Claude in Chrome extension instead of
waiting.

## Writes — none, with one narrow exception

Recon is read-only. The one exception is a **reversible setting flip
on a test event**, needed to observe a setting's effect (e.g. "does the
card hide X when setting Y is off?"). It is allowed only when every
condition below holds:
- the host is a test environment (alpha / alphanext), never
  production;
- the user said yes to this specific flip; a "go ahead with the check"
  that named it counts;
- the original value is read and recorded first;
- the value is restored straight after the observation, re-read, and
  the restore is recorded in the recon file (`verified back on`).

Never create, edit or delete entities during recon. That is
provisioning (`../../qa-manual-runsheet/references/provisioning-rules.md`).
Never open a page that persists on load. For example, admin Display
Filters saves the merged config when opened: read that config from
code instead.

## What recon never does

- It never answers a SPEC question. "The code does X" says nothing about
  whether X is intended. Where the build and the spec disagree, recon
  makes the question concrete ("today the card shows it; the contract
  says the filter hides it"). It does not close it.
- It never reviews a feature branch.
- It never blocks the run. With no env access, or when the user declines,
  skip recon and send the BEHAVIOUR items to the ticket like everything
  else.
