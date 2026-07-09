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
> Primary source: the linked Confluence acceptance-criteria page,
> merged with the Jira Description.
- The exhibitor settings page in the admin panel shows a "Featured"
  toggle, default OFF, visible only to users with the
  `manage_exhibitors` permission.
- When the toggle is ON, the public exhibitor list shows a "Featured"
  badge on that exhibitor's card.
- Featured exhibitors sort above non-featured exhibitors; within each
  group the existing alphabetical order is kept.
- `GET /api/v2/exhibitors/{event_id}/list` returns a boolean field
  `featured` for every exhibitor.
- A maximum of 10 exhibitors can be featured per event; switching the
  11th toggle ON shows the validation message "Featured limit reached
  (10 per event)" and the toggle stays OFF.

## ⚠️ Conflicts to resolve
- Badge label: Confluence says the badge text is "Featured"; the Jira
  Description says "★ Featured".

## Additional requirements (from comments)
- Comment (2026-07-01): the badge must also appear in the exhibitor
  search results, not only the main list.

## Sub-tasks

| Sub-task | Type | Status | PR branch (if stated) |
|---|---|---|---|
| EP-0001 | Backend sub-task | In Review | EP-0001 |
| EP-0002 | Frontend sub-task | In Review | EP-0002 |

---

**How to use this fixture (smoke-testing skill edits):**

1. Copy this file into a chat's working directory.
2. Run `requirements-grooming` → `qa-checklist` → `qa-test-cases` on it.
3. Expect: ~6 REQs (5 + 1 from comments); the badge-label conflict
   raised as a Contradiction; the limit-of-10 producing BVA cases at
   10/11; channel tags splitting `[UI]` (badge, toggle, sorting) from
   `[API]` (the `featured` field); REQ-ID traceability intact end to
   end. If any of that breaks after a skill edit, the edit regressed
   the pipeline.

Do NOT publish this fixture to Jira (skip the publish step of
`qa-pipeline-docs`) — EP-0000 does not exist.
