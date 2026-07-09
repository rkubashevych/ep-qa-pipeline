# Publish config — QA sub-task creation

The team/instance-specific values `qa-pipeline-docs` uses when creating
the QA sub-task (step 6). **Edit this file when adopting the plugin for
another person, project, or Jira instance** — the orchestrator's
SKILL.md stays generic and reads the values from here.

| Setting | Value |
|---|---|
| Jira project key | `EP` |
| Issue type | `QA sub-task` (id `10107`) |
| Assignee | the pipeline operator — resolve their Atlassian email via `lookupJiraAccountId` at run time |
| Assignee email (default operator) | `r.kubashevych@expoplatform.com` |
| Known accountId (cache; re-resolve if creation fails) | `712020:2647832a-3298-435d-afd6-18a9441a1909` |
| Summary format | `[QA-PIPELINE] <story summary> — test cases` |
| Label | `qa-pipeline` (the code phase finds the sub-task by this) |

Rules:

- Resolve the assignee from the email via `lookupJiraAccountId` when
  possible; the cached accountId is a fallback, not the source of truth.
- If you are not the default operator above, replace the email with your
  own before running (or tell the orchestrator whom to assign).
- The issue-type id is instance-specific. If `createJiraIssue` rejects
  id `10107`, list the project's issue types via
  `getJiraProjectIssueTypesMetadata` and update this table.
- The label must stay in sync with `qa-pipeline-code` Step 0, which
  searches `parent = <STORY> AND issuetype = "QA sub-task"` and prefers
  the newest sub-task with this label.
