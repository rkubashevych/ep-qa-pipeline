# Setup guide for the PR Summary skill

This skill reads a PR and builds a summary of the changes for the
code-review skill. The file-description and verification logic is
universal. The only thing to configure is how the PR is accessed.

This skill is configured for ExpoPlatform's stack:
- **Version control / PR system:** Bitbucket Cloud
- **Codebase:** PHP/Phalcon backend monolith
- **Tracker:** Jira (Atlassian Cloud), ticket key format `PROJECT-123` (e.g. `EP-1234`)

## What you need to know before configuring

### 1. Which version control system?

Bitbucket Cloud.

### 2. How does the AI access the PR?

- **CLI** (recommended) — `git` for fetching branches.
  Make sure the CLI is installed and authenticated.
- **REST API** — direct calls to the Bitbucket Cloud REST API
  (`https://api.bitbucket.org/2.0/...`). Requires a Bitbucket Cloud
  **API token** with scopes (set `BB_EMAIL` to your Atlassian email and
  `BB_API_TOKEN` to the token). App passwords are deprecated and are
  being permanently disabled as of June 9, 2026 — do not use them.

### Token scopes & mode

- Branch mode (git CLI: `git fetch`/`diff`/`show`) needs only
  `read:repository:bitbucket` — and the branch name equals the issue key
  (e.g. `EP-54610`). This works with the existing `bitbucket-git-cli`
  token.
- PR-URL mode (REST `/pullrequests/...` endpoints) additionally needs
  `read:pullrequest:bitbucket`. If the token lacks it, those calls 403 —
  create a new "API token with scopes" that includes it, or just use
  branch mode.
- A token's scopes cannot be edited after creation; you must create a
  new one. The token value is shown only once at creation.

### 3. What is the PR URL format?

Bitbucket Cloud:
`https://bitbucket.org/{workspace}/{repo}/pull-requests/{id}`
(example `https://bitbucket.org/expoplatform/backend/pull-requests/123`).

## Configuration

The placeholders below are already resolved with ExpoPlatform values
in SKILL.md. If the stack ever changes, update the same sections:

### Step 1: SKILL.md — "Input" section

The PR URL format for Bitbucket Cloud is set in the "Input" section.

### Step 2: SKILL.md — "Code access" section

The specific tools and commands (git CLI + Bitbucket REST API)
are set in the "Code access" section, including what to do
if the CLI is unavailable.

### Step 3: SKILL.md — "Workflow" section

The actual commands for Bitbucket Cloud are set in the "Workflow"
section:
- PR mode (PR URL provided)
- Branch mode (branch name only)
- How to read the diff and the full content of a file

### Step 4: SKILL.md — "If the CLI is unavailable" section

The authentication setup (git credentials, `BB_EMAIL` /
`BB_API_TOKEN` API token) is described in that section.

## Verification after configuration

- [ ] All configuration blocks in SKILL.md are resolved with Bitbucket values
- [ ] Specific CLI commands or API requests are given
- [ ] The authentication setup is described
- [ ] It is documented what to do if the CLI is unavailable

## Skill files

```
pr-summary/
  SKILL.md                         — the skill instructions
  references/
    output-template.md             — output file template
  setup-guide.md                   — this guide
```
