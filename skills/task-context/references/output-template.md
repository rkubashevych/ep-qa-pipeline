# <ISSUEKEY> - <Task title>

Source: <task URL in the tracker>
Type: <task type>
Status: <status, or omit the line if empty>
Components: <comma-separated, or omit the line if empty>
Labels: <comma-separated, or omit the line if empty>
Generated: <YYYY-MM-DD>

## Goal
<short expected outcome of the task>

## Scope
- In scope: <what is included>
- Out of scope: <what is not included, or "Not specified">

## Requirements
> Primary source: the linked Confluence acceptance-criteria page,
> merged with the Jira Description.
- <requirement>
- <requirement>
- <requirement>

## ⚠️ Conflicts to resolve
> Only when the Confluence acceptance criteria and the Jira Description
> disagree. List each conflict with both versions so a human decides.
- <topic>: Confluence says "<X>"; Jira Description says "<Y>".

## Additional requirements (from comments)
- <requirement found in comments that is not in the main requirements>

## Sub-tasks
> Only when the input is a parent Story with sub-tasks. Lists the
> sub-tasks so later stages know which PRs and surfaces exist.

| Sub-task | Type | Status | PR branch (if stated) |
|---|---|---|---|
| <ISSUEKEY> | Backend / Frontend / QA sub-task | <status> | <branch or —> |

## Related context
> This section is for context only.
> It is not a requirement of the current task and is not processed by
> the next skills.

- <ISSUEKEY>: <what it adds to understanding the current task>

## Related functionality & bug history
> Impact scan — background for grooming (dependencies + risk
> likelihood). Not requirements.

- Appears in: <other surface/feature where the entity shows up —
  one line per documentation hit, with link>
- Bug history: <N> open / <M> closed bugs in this area
  <; notable: KEY-123 — one-line summary>
- Source: <knowledge-base /search | connector fallback | unavailable>

## Attachments
- `attachments/<file>`: <type and what it contains>

---

Section rules:
- Goal, Scope, Requirements — always present. If there is no data — "Not specified in the tracker".
- ⚠️ Conflicts to resolve — only when the Confluence acceptance criteria and the Jira Description actually disagree. Omit the section entirely if there are no conflicts.
- Sub-tasks — only when the input is a parent Story that has sub-tasks. Omit otherwise.
- Additional requirements (from comments) — only when there are relevant comments with new requirements.
- Related context — only when there are real linked issues in the tracker. Comments from the current task are not related context.
- Related functionality & bug history — always attempt the impact scan; if it found nothing or was unavailable, keep the section with a single "Impact scan unavailable" or "No related hits" line.
- Attachments — only when there is data.

Formatting rules:
- Metadata (Source, Type, Status, Components, Labels, Generated) — each
  on its own line. Omit a metadata line entirely if its field is empty.
- Status, Components, and Labels are informational only — they are not
  requirements and the next skills do not act on them.
- Each requirement — a separate bullet.
- Do not merge text into one line.
