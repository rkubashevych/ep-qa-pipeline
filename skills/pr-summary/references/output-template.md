# <ISSUEKEY> - PR Summary

PRs: <one line per PR — issue key (role): URL / branch>
  - <EP-47975 (backend)>: <URL or branch>
  - <EP-54610 (frontend)>: <URL or branch>
Completeness: <complete | partial — N of M changed files not summarised: <reason>>

## Changed files
> When the summary covers several PRs, repeat the structure below once
> per PR, with a top-level heading naming the sub-task (e.g.
> "### EP-47975 (backend)") before its entity groups.

### <Entity or group name>

| File | Category | What changed |
|------|----------|--------------|
| <path> | <component/API/model/...> | <short description> |
| <path> | <category> | <short description> |

### <Next entity or group>

| File | Category | What changed |
|------|----------|--------------|
| <path> | <category> | <short description> |

## Behaviours touched
> Diff-derived inventory of user-observable behaviour changes — one
> line each. Code-review compares this list against the test cases;
> anything no case exercises lands in its "Unmapped changes".

- <endpoint / setting / state field / counter / UI element>: <what changed, one line>
- None *(if the PR touches nothing user-observable)*

## Shared / high blast-radius files

<"None", or one line per shared changed file:>
- <path> — used by <other consumers visible in the code>; regression
  risk: <one short line>
