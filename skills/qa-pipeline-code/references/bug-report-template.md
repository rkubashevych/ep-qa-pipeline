# Bug report template — default filing path

Used by qa-pipeline-code step 7 when the `/knowledge-base` skill is
not installed. One Jira bug per confirmed finding. Draft first, show
the user, create via `createJiraIssue` only after an explicit yes.

## Duplicate check (before drafting)

Search first: `searchJiraIssuesUsingJql` with the summary's key
phrases and the affected area, e.g.
`project = EP AND issuetype = Bug AND text ~ "<key phrase>" ORDER BY created DESC`.
If a plausible match exists, show it to the user instead of drafting —
link the existing ticket in the QA sub-task comment.

## Fields

| Field | Value |
|---|---|
| Project | `EP` |
| Issue type | `Bug` |
| Summary | `[<area>] <symptom in one line — what breaks, where>` |
| Priority | propose from impact (blocker flow → High); user confirms |
| Labels | `qa-pipeline` |
| Links | "relates to" the Story; mention the QA sub-task key |

## Description skeleton

```
h3. Environment
<host / alpha env from the run> · event <EVENT_ID if relevant>
Found by: qa-pipeline run on <STORY> (QA sub-task <KEY>)

h3. Steps to reproduce
<numbered steps copied from the failing TC-REQ-N.M — concrete data
from its [data: ...] annotations, not generalised>

h3. Expected result
<the Exp: block of the test case — verbatim>

h3. Actual result
<what the run observed: api-testing endpoint + observed field, or
web-testing step + what the agent saw; attach the FAIL screenshot
if one was taken>

h3. Source
TC-REQ-N.M (<STORY>-test-cases.md) · REQ-N
Stage: api-testing | web-testing · Status: FAIL / FAIL CONFIRMED
Code-review finding (if any): <file, line, one-line finding>
```

## Rules

- Steps, data, and expected results come from the test case and the
  run reports — do not re-derive or embellish.
- One bug per root symptom: several TCs failing for the same cause →
  one bug listing all affected TC-IDs.
- Redact every token/credential; screenshots must not show secrets.
- After creation, add the new bug key(s) to the QA sub-task as a short
  comment so the handoff step (step 8) can link them.
