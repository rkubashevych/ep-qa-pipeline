---
name: qa-checklist
description: >
  The third stage of task processing. Takes the requirements file
  created by the requirements-grooming skill, decomposes each
  requirement into atomic checks, and builds a reference QA
  checklist — the input for test cases and for manual testing.
  Use it when the user says "build a checklist", "make a checklist",
  "checklist of checks", or after requirements grooming is complete.
---

# QA Checklist

Decomposes numbered requirements into atomic checks and builds
a reference QA checklist — the input for test cases and for
manual testing.

## Input

The input is the `<ISSUEKEY>-requirements.md` file created by the
requirements-grooming skill. In the same chat the file is available
in the working directory automatically. If the chat is new, the user
uploads the file to the chat.

`<ISSUEKEY>` is a Jira (Atlassian Cloud) ticket key in the
`PROJECT-123` format, for example `EP-1234`.

Data sources for this skill:
- The requirements file — the only source of requirements.
- The user's answers to questions asked before the checklist is generated.

First, read the requirements file in full, including any "Notes" block
under the Goal (for example a "⚠️ No Confluence acceptance-criteria
page linked" warning or unresolved-conflict flags carried from
grooming). If a Notes block is present, copy it into the checklist
file's Notes line so a manual tester knows the input was weaker than
ideal. If anything in the requirements is unclear or ambiguous for
building checks, ask the user before you start generating. Do not start
generating while there are unresolved questions.

Do not go to the tracker, do not use external tools, do not search
the internet, do not inspect code.

The requirements file is read-only.
Do not change, rewrite, or clean up its content.

If the requirements file is missing, empty, or corrupted, stop and
tell the user that the requirements-grooming skill must be run first.

## Rules

- All communication and all output file content is in English.
- Chat messages are short.
- The checklist is built only from what is in the requirements file.
  Do not assume, do not add to it, do not interpret requirements on
  your own. Do not invent routes, selectors, roles, states, data, or
  expected behaviour that is not in the requirements.
- Do not change the meaning or wording of requirements. The skill
  decomposes requirements into checks, but it does not rewrite or
  improve the requirements themselves.
- If a requirement was left unchanged after grooming (the user
  skipped the question in skill 2), build the checklist on what is
  there. Do not skip such a requirement and do not mark it as
  incomplete. The requirements file is final.
- If a requirement is marked "(unresolved conflict)" and holds two
  contradictory versions, you cannot write a single unambiguous check
  for it. Do not silently pick one side. Instead, write the checks for
  each version separately, each labelled with which version it belongs
  to (e.g. "REQ-7.1 (version A — Confluence): ...", "REQ-7.2 (version B
  — Jira): ..."), and note in the final response that this requirement
  needs resolution before the checks can be trusted.
- Do not add general QA advice that is not tied to a specific
  requirement of the task.
- After the file is saved, stop. Do not continue into code review,
  test cases, or planning.

## Numbering

Checklist items inherit the requirement IDs from the requirements file.

The order of requirements in the checklist must match the order of
requirements in the requirements file. Do not change, reorder, or
group requirements any differently than they appear in the file.

A single requirement can produce several checks. Each check gets a
sub-number after a dot: REQ-3.1, REQ-3.2, REQ-3.3.

The main REQ-* number does not change — it is the same as in the
requirements file and onward in code review.

Sub-item numbering is sequential, without gaps, in the order the
checks appear in the checklist.

If a requirement already has sub-items (REQ-5a, REQ-5b), each
sub-item is numbered separately: REQ-5a.1, REQ-5a.2, REQ-5b.1,
REQ-5b.2.

## Channel tags

ExpoPlatform features often span more than the web UI. Tag each check
with the channel it must be verified on, so later stages can route it
(only `UI` checks are executable by the browser-based web-testing
skill). Use one of:

- `[UI]` — admin panel or frontend web UI (browser-testable).
- `[API]` — an API response/contract check (e.g. an endpoint returns
  `logo=null`); verified with API tools, not the browser.
- `[mobile]` — mobile app (Android/iOS) behaviour.
- `[export/email]` — non-HTTP outputs: XLS/CSV exports, emails,
  integration push-back (e.g. ASP, Aditus).

Put the tag at the start of the check text, after the REQ-ID. A
requirement that spans channels produces separate checks per channel
(e.g. a public-profile rule → one `[UI]`, one `[API]`, one `[mobile]`).
If the requirements describe only a web UI, everything is `[UI]`.

## Checklist-building method

The rules for quality, decomposition, wording, types of checks,
filtering out the unnecessary, base sets for typical elements, and
anti-patterns are in references/checklist-design-rules.md.

Read that file before you start generating the checklist.

## Verification before saving

After generating the checklist and before saving the file:

1. Run the checklist through the filter for unnecessary checks.
2. Go through the checklist and verify:

- Every requirement from the requirements file has at least one
  check in the checklist. If a requirement has no checks, add one
  or explain why it is impossible.
- There are no checklist items without a REQ-ID.
- The order of requirements in the checklist matches the order in
  the requirements file.
- There is no duplication: the same check does not appear twice.
- Elements of the same type have the same base set of checks.
- Each item is atomic: one check, one pass/fail.
- Each item is self-contained: understandable without opening the
  requirements file.
- There are no checks for behaviour that is not in the requirements.

If a problem is found, fix it before saving.

## Output file

Create the `<ISSUEKEY>-checklist.md` file in the working directory
and give it to the user to download.

The file stays in the working directory — the next skill in the same
chat picks it up automatically.

If the file already exists, delete it completely and create a new
one. The output is always a single file with the result of the last
run. Do not merge with the previous version, do not append, do not
keep data from the previous write.

Before finishing, verify:
- One top-level heading
- One coherent checklist with no duplicated sections

The file structure template is in references/output-template.md.
An example of the level of detail is in references/checklist-example.md.

## Final response

After the file is saved, report:
- The path to the saved file
- The number of checklist items
