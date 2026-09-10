# qa-pipeline-skill

ExpoPlatform's QA pipeline plugin (14 skills) AND a one-plugin
marketplace. The run workspace and the credentials are NOT here since
0.39.0 — they live in `~/.ep-qa` (`EP_QA_HOME`). Full map: `MAINTAINERS.md` — read it before
changing anything. This file is only the gotchas that must be loaded
from message one.

## Hard rules

- **Never `git add -A` or `git add .`** — the working tree may still
  hold legacy live-credential run artifacts. Explicit paths only,
  secret-scan first. Recipe: MAINTAINERS.md step 6.
- **Never write skill files via a shell through the Cowork mount**
  (sed/python/redirects) — writes get silently truncated. Host-side
  file tools or a local editor only.
- **Run outputs are git-ignored by broad rule** (`EP-*`, `build_*.py`,
  `repro_*.py`, `*-testdata*`, runsheets). A new artifact name that
  escapes the patterns means widen the pattern, not add a filename.
- Credentials live in `~/.ep-qa/.env.qa-agents` — outside this tree,
  never in chat, reports, code, or URLs
  (`skills/qa-pipeline/references/environment.md`). A failed command
  that echoed a secret = rotate the token. `ALLOWED_HOSTS` in that file
  is the only set of hosts a stage may call.

## Verify commands

- **Before every commit:** `python3 scripts/verify_plugin.py` — versions,
  descriptions ≤ 1024, LF/newline, wiring, references, vocabulary,
  self-test, no run artefact staged, and no `.env*` / `runs/` inside
  the checkout. FAIL = do not commit.
- Counting script: `python3 skills/qa-run-analyzer/scripts/reconcile_counts.py --selftest`
- Docs-stage smoke test: run `fixtures/EP-0000-context.md` through
  grooming → test-cases (expectations at the fixture's foot; expected
  output = `skills/qa-test-cases/references/test-cases-example.md`)
- Trigger regression: walk `evals/triggering.md` after ANY frontmatter
  description edit
- Secret scan before commit: `secret-leak-scan` skill or gitleaks

## Change discipline

- Every release: bump BOTH `.claude-plugin/plugin.json` and
  `marketplace.json`, add a CHANGELOG entry.
- Run-report 🔴 items and review findings are implemented or
  explicitly rejected in the CHANGELOG — never silently dropped.
- The pipeline's rules encode paid-for failures (false passes, wiped
  data, wrong blockers). Before deleting one, check the CHANGELOG for
  the incident that created it.
