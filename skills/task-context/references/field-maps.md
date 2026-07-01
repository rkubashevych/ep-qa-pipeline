# Field Maps

This is the field map for the project in the tracker — Jira (Atlassian
Cloud). For each task type it lists which fields to read.

These maps use Jira's standard fields and stay generic to Jira:
- "Value" — what the field means in plain language
- "Field key" — the field in the Jira API. Standard fields use their
  Jira name (summary, description, comment, attachment, issuelinks,
  labels, components, status).
- **Acceptance Criteria are NOT a Jira field — they live on a Confluence
  page linked from the ticket.** The skill reads the ticket's linked
  Confluence page (`getJiraIssueRemoteIssueLinks` → `getConfluencePage`)
  and treats it as the primary source of truth. See the "Acceptance
  Criteria (primary source — Confluence)" section of SKILL.md.
- "Mandatory" — if the field is empty, the skill stops and asks for it
  to be filled. The mandatory field is the task description.
- Acceptance Criteria is marked "important" rather than mandatory: the
  skill will not stop if the Confluence page is missing, but it warns
  the user and flags the gap in the context file, because the downstream
  QA skills depend on it heavily.

These field maps are fixed for the project. Do not reopen them every
time — use them as is.

## Story

| Value | Field key | Mandatory |
|---|---|---|
| Summary | summary | — |
| Description | description | yes |
| Acceptance Criteria | Confluence page (linked from ticket) | important |
| Comments | comment | no |
| Attachments | attachment | no |
| Linked issues | issuelinks | no |
| Labels | labels | no |
| Components | components | no |
| Status | status | no |

## Task

| Value | Field key | Mandatory |
|---|---|---|
| Summary | summary | — |
| Description | description | yes |
| Acceptance Criteria | Confluence page (linked from ticket) | important |
| Comments | comment | no |
| Attachments | attachment | no |
| Linked issues | issuelinks | no |
| Labels | labels | no |
| Components | components | no |
| Status | status | no |

## Bug

| Value | Field key | Mandatory |
|---|---|---|
| Summary | summary | — |
| Description (steps to reproduce / bug description) | description | yes |
| Acceptance Criteria | Confluence page (linked from ticket) | important |
| Comments | comment | no |
| Attachments | attachment | no |
| Linked issues | issuelinks | no |
| Labels | labels | no |
| Components | components | no |
| Status | status | no |

## Epic

| Value | Field key | Mandatory |
|---|---|---|
| Summary | summary | — |
| Description (epic summary / goal) | description | yes |
| Acceptance Criteria | Confluence page (linked from ticket) | no |
| Comments | comment | no |
| Attachments | attachment | no |
| Linked issues | issuelinks | no |
| Labels | labels | no |
| Components | components | no |
| Status | status | no |

## Sub-task

| Value | Field key | Mandatory |
|---|---|---|
| Summary | summary | — |
| Description | description | yes |
| Acceptance Criteria | Confluence page (linked from ticket) | important |
| Comments | comment | no |
| Attachments | attachment | no |
| Linked issues | issuelinks | no |
| Labels | labels | no |
| Components | components | no |
| Status | status | no |
