# Linking existing tests to suite cases

Shared by `qa-manual-results` step 4d (the tests a developer's PR adds)
and `qa-api-tests` Step 2 (API tests already in the backend repo). Each
skill decides WHICH tests to link; this file is HOW. QA Service reads a
repository only when asked — nothing registers itself
(`get_help_topic registering`).

## The call

```
link_implemented_tests {suiteId, links: [{stableId,
  ref: "<path>::<method or exact test title>", level,
  repo: <the home's repoId, e.g. "main">, landing, prBranch?, prNumber?}],
  verify: true}
```

- **`ref` names the method or the test**, never the file alone.
- **`landing`:** `"merged"` when the test is on the repo's configured
  branch; `"pr"` with `prBranch` (and `prNumber` when known) before the
  merge. A `pr` link is re-linked with `landing: "merged"` after the
  merge — a To do and a ledger row until then.
- **`verify: true`, always.** The service records a case `implemented`
  only when the ref resolves; never set a status by hand.
- **Never link a `@skip`ped test** — a skipped test proves nothing; note
  it on the case instead (`detail.devTests`, with the skip reason).
  One exception, the **CI-only skip** (0.73.0): the skip names a ticket
  for something CI lacks and the product does not (EP-50538: no
  DynamoDB in CI, so every `/api/v2/` call answers 500), and this run
  saw the test green with the marker taken out. That test is linked,
  with `detail.ciSkip` on the case
  (`../../qa-api-tests/references/local-harness.md` → "CI-only skips").

## A link resolves only when the case id is IN the test file

QA Service verifies a link by finding the stableId in the file at that
ref; the test's own title and an older id do not count. The id goes at
the start of the test title in TS (`it('FAV-TC-03: …')`) and in the
method's docblock in PHP (`@testCaseId FAV-TC-03`), never in the method
name. All 40 MEXP links landed `partial`, "stableId … not found in the
file" (2026-10-14). A test found without its case id is either linked
after a PR stamps the id into it (another repo's code — the user's yes
first), or left unlinked with a To do.

## Reading the response

- **`partial` / unverified counts toward nothing.** Report it as not
  covered, never as linked coverage.
- **Unresolved for a file the checkout has** is Bitbucket rate-limiting
  QA Service (`429`, reported as "file not found"): keep the link, say
  so, re-link later (`../../qa-pipeline-docs/references/qa-service-first.md`
  → step 4).

## Discovery — tests with no declared id

`discover_tests {suiteId, pathPrefixes: [the files]}` previews and
writes nothing. It reads only the repo's **configured branch**, so it
works only after the merge. Check `rateLimited`, `failedReads` and
`truncated` before trusting the preview, then call it again with
`apply: true` and `refs` for the tests the user picks. QA Service
discovers one repo per product; a test in another repo cannot be
discovered.

All calls of one step go in one plan file and one confirmation
(`write-plans.md`).
