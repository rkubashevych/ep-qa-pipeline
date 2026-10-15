# Background scans — impact scan and the existing QA Service suite

Read by `task-context` (stage 1), flow steps 7–8. Both scans fill
background sections of the context file. Neither is a source of
requirements: the anti-invention prohibitions in the SKILL.md apply
unchanged, and neither ever blocks the run.

Contents: 1. Related functionality & bug history (impact scan) ·
2. Existing QA Service suite (established test design)

## 1. Related functionality & bug history (impact scan)

The ticket says what changes; this scan says what else might be
affected. It feeds grooming's dependency questions and risk ratings.

1. Derive 1–2 keyword queries from the feature/entity the ticket
   touches (e.g. "exhibitor logo", "session registration").
2. **Primary — knowledge-base skill installed:** run its Step 1
   "SCOUT — Search" primary endpoint with those keywords (read that
   skill's SKILL.md for the current URL/token contract — do not copy
   it here, it rotates). Take the top 3–5 documentation hits.
   **Check the host first:** a stage may call only the hosts in
   `ALLOWED_HOSTS` (`../../qa-pipeline/references/environment.md`). When
   the SCOUT host is not listed, skip straight to the fallback and write
   `Source: connector fallback (SCOUT host not in ALLOWED_HOSTS)`. Never
   call it anyway. (EP-56227, 2026-09-29: the endpoint had moved to a
   host the list did not carry.)
3. **Fallback — SCOUT fails, its host is not allowed, or knowledge-base
   is not installed:** use the Atlassian connector directly:
   `searchConfluenceUsingCql` on the ExpoDoc space
   (`text ~ "<keywords>"`), and `searchJiraIssuesUsingJql` for EP bugs,
   open and closed (`project = EP AND issuetype = Bug AND
   text ~ "<keywords>"`), top 5 each.
4. Write the results into the "Related functionality & bug history"
   section of the output file: which other surfaces/features the
   entity appears in (one line per doc hit, with link), and a bug
   history line (N open / M closed bugs in this area, notable
   recurring ones by key).

Rules: keep it ≤10 lines. If both paths fail, write "Impact scan
unavailable" and continue. Internal-only content stays internal.

## 2. Existing QA Service suite (established test design)

If the QA Service MCP connector is present in the session, pull the
feature's established requirements so grooming can check the ticket
against them instead of re-deriving from scratch:

0. **Look for the developer's suite first.** A developer
   using the `sdlc` plugin registers the ticket's requirements in QA
   Service before QA does (`sdlc-qa`, stage 2). Check two places:
   - **The ticket.** A `qa-service.expoplatform.com/…/test-suites/…`
     URL in the story, its sub-tasks, their comments or remote links.
     A pipeline QA sub-task's description doesn't count, because the
     pipeline wrote it.
   - **The repo.** A spec file `docs/specs/<KEY>-*.md` (sdlc names it
     `<TICKET>-YYYY-MM-DD-<slug>.md`) with a `## Register — QA Service`
     section. That section names the product, the suite, its prefix and
     the requirement IDs the ticket owns. Look on the branches named
     after the story and its dev sub-tasks in each repo, then on each
     repo's default branch. Use the local clone if there is one, else
     the Bitbucket `src` endpoint
     (`../../pr-summary/references/bitbucket-access.md`). If there's no
     branch yet or no access, skip this source and say so.
   Found → `get_suite` with `productId` to confirm it exists, write the
   section as in step 2 with the `Developer's suite: yes …` line on
   top, and skip step 1. Not found → write `Developer's suite: none
   found (<sources checked>)` and continue with step 1 as usual.
1. `search {query: "<feature words>", kinds: ["suite"], productId:
   "expoplatform"}` with the same keywords as the impact scan (two or
   three calls with different word sets are fine — each answer is ~1 KB;
   `search` matches suite titles and prefixes, not summaries). Match the
   suite whose role/feature path corresponds to what the ticket touches.
   Nothing found → `list_suites` once, as the fallback only (it returns
   the whole product, ~190 KB). Still no match → write "No existing QA
   Service suite found" in the section and continue.
2. On a match, `get_suite` and write the "Existing QA Service suite"
   section of the output file:
   - suite path, title, requirement/case counts, one-line summary;
   - the requirements as one line each: `stableId — title (kind)`.
     If the suite has more than ~40, list ALL of kind `risk`, `oq`,
     `discrepancy`, `invariant` plus the `fr`/`rule` items matching
     the ticket's keywords, and close with "+N more not listed";
   - any cases whose notes reference open bug keys (known-bug areas),
     one line each.
3. Connector absent → omit the section entirely.

Grooming (next stage) uses this section to detect contradictions
between the ticket and the established requirements.
