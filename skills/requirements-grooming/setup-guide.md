# Requirements Grooming skill setup guide

This skill analyzes the requirements from a context file and produces a
numbered list of requirements for the next skills in the chain. The
grooming logic is universal — setup is minimal.

## What is configured

### 1. The context-collection skill name

This skill expects a context file from the previous skill in the chain.
It is configured for the context-collection skill named **task-context**.

If in your chain the context-collection skill has a different name —
replace "task-context" in two places:
- `description` in the frontmatter (the line "Takes the context file
  created by the task-context skill")
- the "Inputs" section in the body of SKILL.md

### 2. Communication language (optional)

The skill communicates in English. If you need a different language —
find the "Rules" section in SKILL.md and replace the line:
```
- All communication and all output-file content — in English.
```
with your language.

## What does NOT need configuring

The grooming method (4 questions), the REQ-N numbering rules, the chat
output format, the rules about what not to generate — this is universal
logic, do not touch it.

## Configuration order

1. In `SKILL.md` frontmatter: confirm "task-context" is the name of
   your context-collection skill.
2. In `SKILL.md` "Inputs" section: confirm the same name.
3. Optionally: change the communication language.

## Post-setup check

- [ ] The context-collection skill name is correct in both places
- [ ] No unresolved configuration placeholders remain in SKILL.md

## Skill files

```
requirements-grooming/
  SKILL.md                         — skill instructions
  references/
    output-template.md             — output file template
  setup-guide.md                   — this guide
```
