# Bitbucket access — shared reference

The single source of truth for how the code-phase skills (`pr-summary`
and `code-review`) authenticate against Bitbucket Cloud. Both SKILL.md
files point here — edit HERE, not in the skills, so the two never
drift apart.

## Repos

Bitbucket Cloud, workspace `expoplatform`:
- backend monolith (PHP/Phalcon) = `expoplatform-main-ira`
- frontend = `portal-ui` (Next.js + React, TypeScript, Material UI)
- admin = `admin-ui`

PR URL format: `https://bitbucket.org/{workspace}/{repo}/pull-requests/{id}`.
`{workspace}` and `{repo}` may be human-readable slugs OR UUIDs in
braces (e.g. `https://bitbucket.org/%7B9274fcef-...%7D/%7B880a8c6f-...%7D/pull-requests/6966`);
parse and use whichever form the URL contains.

## Branch mode vs PR mode — default to branch mode

The configured API token has `read:repository` scope but NOT
`read:pullrequest`, so the REST `/pullrequests/...` endpoints return
403, while git-CLI branch mode (clone/fetch/diff/show + the repository
`src` endpoint) works fully.

**Prefer branch mode.** The branch name is the issue key (e.g.
`EP-54610`); the base branch is `master` unless stated otherwise. Only
use PR-URL / REST mode if the token has been given the
`read:pullrequest:bitbucket` scope.

## Authentication setup

- Configure git credentials (or an SSH key) for the workspace.
- Set the `BB_EMAIL` and `BB_API_TOKEN` environment variables for REST
  API access. `BB_EMAIL` is your Atlassian account email;
  `BB_API_TOKEN` is a Bitbucket Cloud API token with scopes.
- Use Basic auth: `-u "$BB_EMAIL:$BB_API_TOKEN"`.

> **App passwords are dead.** Bitbucket Cloud app passwords are
> deprecated — new ones could not be created after September 2025, and
> all remaining app passwords are permanently disabled as of June 9,
> 2026 (full removal July 28, 2026). Use an API token, not an app
> password. Create one under Atlassian account settings → "Create and
> manage API tokens" → "Create API token with scopes", select Bitbucket
> as the app, and grant at least repository read (and pull-request read
> if you want PR-URL mode).

## If the CLI is unavailable

Stop. Do not use git clone workarounds, curl-as-substitute, or the
browser instead. Tell the user to install and authenticate the CLI.
