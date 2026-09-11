# EP-0000 - Fixture: exhibitor "Featured" badge toggle

Source: fixture — not a real ticket (smoke-test input for the docs pipeline)
Type: Story
Status: In Development
Generated: 2026-07-09

## Goal
Organizers can mark an exhibitor as "Featured" per event; featured
exhibitors show a "Featured" badge on the public exhibitor list and
sort above non-featured ones.

## Scope
- In scope: admin toggle, public list badge, list sorting, API field.
- Out of scope: mobile apps, exports, emails.

## Requirements
> Primary source: the linked Confluence acceptance-criteria page (one
> `AC-n` bullet per criterion, page order, verbatim), then the Jira
> Description's own items (`JD-n`). Never a merged paraphrase.
- AC-1 (Confluence §1): The exhibitor settings page in the admin panel
  shows a "Featured" toggle, default OFF, visible only to users with the
  `manage_exhibitors` permission.
- AC-2 (Confluence §1): When the toggle is ON, the public exhibitor list
  shows a "Featured" badge on that exhibitor's card.
- AC-3 (Confluence §2): Featured exhibitors sort above non-featured
  exhibitors; within each group the existing alphabetical order is kept.
- AC-4 (Confluence §3): `GET /api/v2/exhibitors/{event_id}/list` returns
  a boolean field `featured` for every exhibitor.
- AC-5 (Confluence §3): A maximum of 10 exhibitors can be featured per
  event; switching the 11th toggle ON shows the validation message
  "Featured limit reached (10 per event)" and the toggle stays OFF.

AC items on the page: 5 · captured: 5

## ⚠️ Conflicts to resolve
- AC-2 badge label: Confluence says the badge text is "Featured"; the
  Jira Description says "★ Featured".

## Additional requirements (from comments)
- CM-1 (comment 2026-07-01): the badge must also appear in the exhibitor
  search results, not only the main list.

## Sub-tasks

| Sub-task | Type | Status | PR branch (if stated) |
|---|---|---|---|
| EP-0001 | Backend sub-task | In Review | EP-0001 |
| EP-0002 | Frontend sub-task | In Review | EP-0002 |

---

**How to use this fixture (smoke-testing skill edits):**

1. Copy this file to `~/.ep-qa/runs/EP-0000/docs/EP-0000-context.md`
   (the run folder — `skills/qa-pipeline/references/data-locations.md`).
   It is already in the stage-1 output shape: the `AC-n` / `CM-n` ids
   and the page/captured count line are what task-context writes; the
   `§` section numbers are synthetic, like the ticket.
2. Run `requirements-grooming` → `qa-test-cases` on it (stage 3 is
   folded into 4 since 0.40.0).
3. Expect: ~6 REQs (5 + 1 from comments); the badge-label conflict
   raised as a Contradiction; the limit-of-10 producing BVA cases at
   9/10/11; channel tags splitting `[UI]` (badge, toggle, sorting) from
   `[API]` (the `featured` field); the toggle's presence and default
   OFF as Structural checks lines, not cases; REQ-ID traceability
   intact end to end; exactly ONE `[core]`-marked case per behavioural
   REQ, with a matching `Core cases:` line in the test-cases statistics
   block; every REQ carrying a `source:` id from the fixture's
   `AC-1…AC-5` / `CM-1` bullets, every group a `Covers:` line,
   `AC coverage: 5/5` — compare with
   `skills/qa-test-cases/references/test-cases-example.md`, which is
   this fixture's expected output, and run `reconcile_counts.py
   EP-0000` on the result.
   If any of that breaks after a skill edit, the edit regressed
   the pipeline.

Do NOT publish this fixture to Jira (skip the publish step of
`qa-pipeline-docs`) — EP-0000 does not exist.
