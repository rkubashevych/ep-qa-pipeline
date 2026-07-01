# Setup guide for the QA Test Cases skill

This skill is almost fully universal — it works with any tracker and
product without changes. The test-design techniques, the coverage
rules, and the anti-patterns are based on ISTQB and do not depend on
the environment.

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

If in your chain the checklist skill has a name other than
"qa-checklist", replace that reference in the "Input" section of
SKILL.md.

## What does NOT need configuring

- `references/test-case-design-rules.md` — ISTQB rules, fully
  universal, do not touch
- `references/test-cases-example.md` — example of the level of
  detail, do not touch
- `references/output-template.md` — the output file structure
  template, do not touch
- The TC-REQ-N.M numbering method, the verification, the filtering
  rules, and the test-case scope — do not touch

## Post-configuration check

- [ ] If the language was changed, verify it is changed everywhere
- [ ] If the previous skill's name was changed, verify it is changed
      in the "Input" section

## Skill files

```
qa-test-cases/
  SKILL.md                              — skill instructions
  references/
    test-case-design-rules.md          — building rules (ISTQB)
    test-cases-example.md              — example of detail
    output-template.md                 — output file template
  setup-guide.md                       — this guide
```
