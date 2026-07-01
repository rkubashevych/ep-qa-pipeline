# Task Context skill setup guide

This skill collects task data from the tracker and produces a
structured context file. It is already configured for ExpoPlatform's
stack — Jira (Atlassian Cloud) accessed through the connected Atlassian
MCP tools.

## Stack configuration

The skill is set up for the following stack. The reference below
records what is configured and where to adjust it if the project
changes.

### 1. Tracker

Jira (Atlassian Cloud) — `https://expoplatform.atlassian.net`.

### 2. How the AI accesses the tracker

Through the connected Atlassian MCP tools (the Atlassian connector) —
for example `getJiraIssue` and `searchJiraIssuesUsingJql`. Make sure
the Atlassian connector is connected and authenticated. If it is
unavailable, the skill stops and tells the user; it does not fall back
to a browser or an internet search.

### 3. Task types in the project

Jira's standard issue types: Story, Task, Bug, Epic, Sub-task.

### 4. Fields in each task type

These are mapped in references/field-maps.md to Jira's standard fields:
Summary, Description, Comments, Attachments, Linked issues, Labels,
Components, Status.

**Acceptance Criteria are not a Jira field.** At ExpoPlatform they live
on a Confluence page linked from the ticket, and the skill treats that
page as the primary source of truth. It reads the link via
`getJiraIssueRemoteIssueLinks` and fetches the page via
`getConfluencePage`, then merges the criteria with the Jira Description
and flags any conflicts. This requires the Atlassian connector to have
**Confluence access enabled**, not just Jira. No custom-field key setup
is needed, since the field maps use Jira's standard fields.

### 5. The mandatory field

The field that MUST be filled for there to be something to process is
the task Description. For bugs this is the Description (steps to
reproduce / bug description).

## Configuration order

The skill ships configured for the stack above. If you adapt it for a
different project, edit the files in this order:

### Step 1: references/field-maps.md

This is first and most important. Fill in the field map:
1. Create a section for each task type
2. For each type fill the table:
   - Value — the human-readable field name
   - Field key — the technical key in the tracker
   - Mandatory — yes/no (at least one "yes" per type)
3. Delete task types you do not use
4. Add types not in the template

### Step 2: SKILL.md — "Tracker access" section

Confirm the access instructions match your tracker and access method.
State:
- Which MCP tools or CLI commands to use
- How to parse the task URL
- What to do if the integration is unavailable
- The fallback scenario

### Step 3: SKILL.md — "Task types and fields" section

Confirm the list of task types matches your project.

### Step 4: SKILL.md — "Empty fields" section

Confirm the mandatory fields per task type match your field map.

### Step 5: SKILL.md — "Attachments" section

Confirm the description of how your tracker/MCP returns attachments. If
unsure — leave it as is; the default flow (ask the user to upload)
works with any tracker.

### Step 6: SKILL.md — "Inputs" section

Confirm the task key format for your tracker.

## Post-setup check

After setup, check:
- [ ] The "Tracker access" instructions are concrete and correct
- [ ] field-maps.md contains the real fields of your project with the
      correct technical keys
- [ ] There is at least one mandatory field per task type
- [ ] The tracker access method is stated (MCP, CLI, or manual copy)

## Test run

After setup, do a test run on one real task:
1. Give the AI a task key or URL (e.g. `EP-1234`)
2. Check that all fields from the map are collected
3. Check that the context file contains all the information from the
   ticket without loss
4. If something is missing — check the field map

## Skill files

```
task-context/
  SKILL.md                         — skill instructions
  references/
    field-maps.md                  — project field map
    output-template.md             — output file template
  setup-guide.md                   — this guide
```
