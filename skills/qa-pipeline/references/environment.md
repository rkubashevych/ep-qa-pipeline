# The environment — where secrets and runs live, which hosts may be touched

**Contents:** Why · `EP_QA_HOME` · Resolution order · The credentials
file · `ALLOWED_HOSTS` · Secrets in chat · What must not happen

This is the single home for three rules every stage used to restate in
its own words: where the credentials file is, where the run folder is,
and which hosts a stage may send a request to. Other files point here;
they do not repeat the values.

## Why this file exists

Until 0.39.0 the plugin checkout doubled as the run workspace and the
credential store: `.env.qa-agents` and `runs/` sat in the same folder
that Cowork mounts, that every other installed skill can read, and that
the marketplace serves from. `.gitignore` protected git and nothing
else — a prompt-injected ticket could have read the file through any
file tool, and a `git add -A` was one keystroke from publishing ~700
credential-bearing run files (MAINTAINERS → Gotchas). "Never target
production" was a sentence in three SKILLs with nothing that compared a
host against anything.

## `EP_QA_HOME`

One directory outside the plugin tree holds everything that is not the
plugin:

```
$EP_QA_HOME/                    default: ~/.ep-qa/   (Windows: %USERPROFILE%\.ep-qa\)
  .env.qa-agents                the credentials file (below)
  runs/<KEY>/…                  the run folder — layout in data-locations.md
  cache/navigation_paths.json   web-testing's navigation memory
```

Every `runs/<KEY>/…` path written anywhere in this plugin is relative
to `$EP_QA_HOME` — `runs/EP-1234/r2/` means `$EP_QA_HOME/runs/EP-1234/r2/`.
The plugin checkout (or the marketplace cache) holds skills and nothing
that a run writes.

## Resolution order — the same for every stage

1. **`EP_QA_HOME`** when the variable is set (Claude Code: from the
   shell; a `.env` is not read for this — the variable tells where the
   `.env` is).
2. **`~/.ep-qa`** when it exists. In Cowork, "exists" means the folder
   is mounted in the session — mount `~/.ep-qa`, not the plugin
   checkout, when a run needs to write.
3. **Legacy** — `runs/` and `.env.qa-agents` beside the plugin's
   `skills/` folder (the pre-0.39 layout). **Read-only**: an old ticket's
   reports and ledger are read from there; nothing new is written there.
4. Nothing reachable → **PAUSE** before the first write: "No
   `~/.ep-qa` reachable — mount it (Cowork) or create it (`mkdir
   ~/.ep-qa`) and put `.env.qa-agents` in it." The stage may go on only
   after the user says where to write; it never silently falls back to
   the checkout.

Print the resolved home once per run, in the same line as the run
folder: `Run folder: ~/.ep-qa/runs/EP-1234/r2`. Do not print it again.

`skills/qa-run-analyzer/scripts/reconcile_counts.py` and
`skills/api-testing/scripts/load-env.sh` implement the same order
(`ep_qa_home()` / `ep_qa_env_file()`); a skill that needs the path in a
shell uses them rather than restating the rule.

## The credentials file — `$EP_QA_HOME/.env.qa-agents`

The only place a credential lives. Variables (the api-testing reference
§0 explains each):

| Variable | Used by |
|---|---|
| `ADMIN_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ORGANIZER_API_KEY`, `EVENT_ID`, `BASE_URL`, `BASE_PATH` | api-testing, stage 9 provisioning, the walk's AGENT-RUNS cards |
| `BB_API_TOKEN` (and the other Bitbucket variables in `pr-summary/references/bitbucket-access.md`) | pr-summary, code-review |
| `ALLOWED_HOSTS` | every stage that sends a request to a product host (below) |
| `QA_OPERATOR_EMAIL` | qa-pipeline-docs publish (the QA sub-task assignee), qa-manual-results (the default tester principal) |

The e2e project's `.env` is **not** read any more: two files with the
same variables gave two answers on which alpha was under test. Copy the
values you need into `.env.qa-agents` once.

Never: in a skill file, an example, a report, a Jira comment, a suite
note, a URL, or chat. A stage that needs a value reads it from the file
at run time and never prints it (`load-env.sh` — it handles quoting and
shell metacharacters).

## `ALLOWED_HOSTS` — the only hosts a stage may touch

```
ALLOWED_HOSTS=api-alpha2.expoplatform.net,ennies-alpha2.expoplatform.net,canyon2026-rc.expoplatform.net,*.alphanext14prod.expoplatform.net
```

Comma-separated hostnames; a leading `*.` matches one or more whole
labels — `*.rc.expoplatform.net` does NOT match
`canyon2026-rc.expoplatform.net`, so list such hosts by name. No
scheme, no path, no port.

**The rule.** Before the first request of a run — the api-testing
login, web-testing's first navigation, stage 9's first provisioning
call, the walk's first AGENT-RUNS card, a bug-fix mode repro — the
stage takes every host it is about to use (`ADMIN_BASE_URL`,
`BASE_URL`, the per-event frontend host, the host on the ticket or in
`login-config.md`) and checks each against the list:

- **Listed** → proceed. Say which hosts, once, in the run's first line.
- **Not listed** → **PAUSE** naming the host and the list. The user
  adds it to `.env.qa-agents` and says "go", or names another host. The
  stage never edits the list itself and never proceeds "just for reads".
- **`ALLOWED_HOSTS` missing or empty** → PAUSE once: "no allow-list
  configured — add `ALLOWED_HOSTS=` to `.env.qa-agents`". A run without
  a list does not start.
- **A production host is refused even when listed.** Hosts ending in
  `expoplatform.com` are production (the QA Service and Jira are
  connectors, not test targets, and are not subject to this rule). A
  ticket that names one gets `BLOCKED — production host` on every case
  it would have run, and the user checks it by hand.

The check is on the host string, before any network call. It is not a
substitute for the test-event authorisation (qa-pipeline-code step
"stage 9" REQUIRED PAUSE) — that one asks *which event*; this one asks
*which machine*.

## Secrets in chat

Cowork and Claude Code transcripts are retained and can be shared. So:

- **A `.env` value is never spoken, printed, echoed or quoted** — not
  the admin password, not an API key, not a token, not even a
  "first four characters". "Log in with the admin account from your
  `.env.qa-agents`" is the whole sentence.
- **A stage-9 throwaway account's password may be said** — those
  accounts exist for one run on a throwaway event, are recorded in
  `-testdata.json`, and are retired at stage 10 (`qa-manual-results`
  step 4c). The walk plan's session line carries them for this reason.
  Anything else the tester needs to type is "in the plan file,
  Session N".
- A password, token or code the **tester** pastes into chat is stored
  as `<token supplied>` (`walk-session-rules.md`), never verbatim.

## What must not happen

- A run writes into the plugin checkout because `~/.ep-qa` was not
  mounted and nobody asked.
- A stage reads the e2e `.env` "because it was there".
- A request goes to a host that was never compared with `ALLOWED_HOSTS`
  — including a "quick GET to see if it is up".
- A skill file, example or CHANGELOG entry carries a real hostname
  paired with a real credential, or an internal infrastructure host.
