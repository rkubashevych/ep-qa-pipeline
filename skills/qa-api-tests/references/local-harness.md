# The local harness for the monolith's API tests

The source of truth is the team's harness repo,
`https://github.com/ExpoPlatform-Ltd/php-monolyth-local-env` — its
`README.md` (setup) and `API-TESTS.md` (how to write, run and register
an API test). Read both from the local clone before the first run on a
machine, and `git pull` it first: this file only records what
`qa-api-tests` depends on, as of commit `942f8a5` (2026-10-12). When
the harness repo and this file disagree, the harness repo wins.

## What the skill checks in Step 0

| Check | How | Missing → |
|---|---|---|
| Harness clone | the `php-monolyth-local-env` folder; its `.env` `PROJECT_PATH` names the backend clone (default: `expo/` next to it) | name it; skip Step 3 |
| Backend clone | `git -C <PROJECT_PATH> fetch origin` succeeds; the branch is created from fresh `origin/alpha` | same |
| Containers up | `docker ps` shows `expo-qa-server` (PHP) and `expo-qa-postgres`; else `docker compose up -d` in the harness folder, or `./setup.sh` after a `git pull` in the backend clone (it re-runs composer, migrations and swagger) | same — never improvise another runner |
| Hosts | `api-w.expo.loc` / `w.expo.loc` resolve to 127.0.0.1 (README step 2) | same |
| Smoke | `docker exec -w /var/www/html/universal expo-qa-server php vendor/bin/codecept run api-admin ExhibitorCategories` is green | same |

On Windows the README keeps both repos inside WSL2: on `C:\` the suite
runs 5–10× slower. Say so if the clone is on `C:\`; don't move it.

**Git Bash (0.59.0).** MSYS rewrites `docker exec -w /var/www/html/...`
into a Windows path ("Cwd must be an absolute path"). Prefix every
`docker exec` and `./setup.sh` with `MSYS_NO_PATHCONV=1`. With that set,
`setup.sh`'s last step, `curl -o /dev/null` (the superadmin login
check), exits 23. Composer, migrations and swagger have already run, so
run that login check by hand (`-o NUL`) instead of reading the exit 23
as a failed setup.

**API v2 runs only with `s3.enabled = false` (0.59.1; 0.59.0 said it
could not run).** v2 public requests log to DynamoDB
(`LoggerPublicApi::logInsert`, the `api_public_log` table). The
harness has no AWS keys, so with the template's
`[amazon] s3.enabled = true` that write throws and the request answers
500. The backend clone's `config.ini` (git-ignored, line `s3.enabled`)
set to `false` makes v2 run: on MEXP, the v2 export, contract and
v2/v3 parity Cests went from 500 to green (`API-TESTS.md` §14 lists the
same fix). Back the file up before the edit, say in the report that it
was changed, and leave it as the user wants it. In CI v2 stays blocked
(EP-50538 / EP-50539), so a v2 test is green locally only.
**v1 writes that record statistics** (`/api/v1/schedule/save` edit,
`confirm`) need a reachable DynamoDB whatever the flag says. With
`false` they fail with "Typed property …Statistics\Providers\Dynamo::
$marshaler must not be accessed before initialization"; with `true`
they fail on missing AWS keys. Such a case needs LocalStack; set it
aside, don't report it as a product defect. **v3 runs normally**
(Bearer key; e.g. `Products/*V3Cest`, `Meetings/*V3Cest`).

## Running one test (what the batch loop executes)

```bash
docker exec -w /var/www/html/universal expo-qa-server php vendor/bin/codecept run <suite> <Dir>/<Name>Cest.php:<method> --debug
```

`<suite>` is `api-admin`, `api-front`, `api-public` or `api-mob`; the
path is relative to the suite folder; the part after `:` is a regex.
Output (the failing response first: `<Test>.fail.json`) lands in
`universal/Tests/Codeception/_output/`, owned by root — clean it
through `docker exec`, not from the host.

The checklist (`API-TESTS.md` §14) requires the Cest green on its own,
with its folder, with the whole suite, **and on a second run** (the
second run catches rows left in the database).

## Red before you touched it

`API-TESTS.md` §11 lists tests that fail on a clean `alpha` in this
harness (verified 2026-10-12: `api-front Auth/AuthCest` invalid-method
cases; four `api-mob` Sync / deep-link Cests). A red test is first
checked against that list, then re-run on clean `alpha` without the new
test. Only then is it a product defect (`onFailure: flag-only` reports
it). A defect is never "fixed" by loosening an assertion.

## Conventions the QA Service plan does not set by itself

- **Branch:** the one the plan names, `qa/<level>-<suite-path>` (e.g.
  `qa/ae-meeting-export`), off fresh `origin/alpha`. Never pass
  `targetBranch` to `plan_implement_tests`: QA Service takes it as the PR
  base (0.59.0). The ticket key goes in the commit and the PR title.
- **Commits:** `<KEY>: …` or `test(<scope>): …`.
- **Case id:** `@testCaseId <ID>` in the METHOD docblock, one per test;
  method names `testCamelCase` (never `test_<ID>_…` in a new test).
- **Tags:** `@group <tag>` (without `@`), 1–3, approved catalogue only.
- **Skip:** `@skip <reason> — EP-xxxxx` in the method docblock; never a
  class-level skip, never a skip without a ticket. A skipped test is
  not linked (`qa-api-tests` Step 2).
- **Level by path:** `api-*/…/*Cest.php` → AE; `…/contract/…Cest.php` →
  C (register with `level: 'C'` — discovery would file it as AE).

## What CI does with these tests

On a PR into `alpha` only the unit suites gate. API tests run:
`api-public` after every push to `alpha`; `api-admin`, `api-front`,
`api-mob` only in the manual `alpha-full-tests` pipeline. So:
- before the merge, the local run IS the only execution — a case linked
  with `landing: pr` is "implemented" on the strength of that run alone;
- after the merge, results reach QA Service through
  `ci/report-junit.sh`, joined by `@testCaseId` / ref; unregistered
  tests report as `no_case`.

The report and the To do say which suite the new tests are in and
whether CI will run them on its own.
