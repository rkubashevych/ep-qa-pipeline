# Setup guide for the QA Checklist skill

This skill is almost fully universal — it works with any tracker and
product without changes. The checklist-building method, the numbering
rules, the types of checks, and the anti-patterns are based on ISTQB
and do not depend on the environment.

This adaptation is configured for ExpoPlatform: the tracker is Jira
(Atlassian Cloud) and ticket keys use the `PROJECT-123` format
(for example `EP-1234`).

## What needs configuring

### 1. Communication language (optional)

By default the skill communicates in English. If a different language
is needed, in the "Rules" section of SKILL.md replace the line:
```
- All communication and all output file content is in English.
```
with your language.

### 2. Reference to the previous skill (optional)

If in your chain the requirements grooming skill has a name other
than "requirements-grooming", replace that reference in the "Input"
section of SKILL.md.

## What does NOT need configuring

- `references/checklist-design-rules.md` — ISTQB rules, fully
  universal, do not touch
- `references/checklist-example.md` — example of the level of
  detail, do not touch
- `references/output-template.md` — the output file structure
  template, do not touch
- The REQ-N.M numbering method, the verification, and the filtering
  rules — do not touch

## Post-configuration check

- [ ] If the language was changed, verify it is changed everywhere
- [ ] If the previous skill's name was changed, verify it is changed
      in the "Input" section

## Skill files

```
qa-checklist/
  SKILL.md                              — skill instructions
  references/
    checklist-design-rules.md          — building rules (ISTQB)
    checklist-example.md               — example of detail
    output-template.md                 — output file template
  setup-guide.md                       — this guide
```
