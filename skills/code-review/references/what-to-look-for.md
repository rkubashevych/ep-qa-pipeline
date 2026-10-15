# What to look for in the code — per PR kind

Read by `code-review` (stage 6) while assessing a case against the PR.
ExpoPlatform splits a story into separate frontend and backend
sub-tasks, each with its own Bitbucket PR. First determine which kind
of PR you are reviewing — from the sub-task type, the repo, or the
files in the PR summary (PHP/Phalcon vs frontend sources) — then apply
the matching list. A PR may occasionally touch both.

## Backend (PHP/Phalcon monolith)

- Presence of elements: controllers and actions, service methods,
  model fields, Volt view variables/labels, response payload fields,
  messages.
- Conditional logic: if/else, switch, guard clauses, ACL/permission
  checks, feature flags.
- States: default, active, disabled, error, empty — as represented in
  model attributes, status fields, or response flags.
- Validations: Phalcon validators, rules, messages, triggers, boundary
  values.
- Data: model fields, column types, formats, mappings, API/response
  contracts, DB migrations.
- Binding: whether the logic is wired to the correct route, controller
  action, DI service, model, or Volt template.

## Frontend (`portal-ui` — Next.js + React, TypeScript, Material UI)

- Presence of elements: React components (incl. MUI components like
  Button, TextField, Dialog), fields, labels, texts, messages,
  tooltips, icons.
- Conditional logic: conditional rendering (`&&`, ternaries), hooks
  (`useState`, `useEffect`, `useMemo`), guards, permission/role checks,
  feature flags.
- States: default, active, disabled, error, loading, empty — as held
  in component state, context, or props; check `disabled`/`readOnly`
  props where behaviour depends on them.
- Validations: react-hook-form rules and resolvers, validation
  messages, triggers, boundary values.
- Data: request/response field names and formats, API contracts,
  mapping/transform logic (e.g. reading the correct key like
  `settings.logo` vs `do_not_allow_logo`, inverting a boolean),
  prepareData/transform helpers, TypeScript types.
- Binding: whether the element is wired to the correct Next.js
  route/page, component, and API endpoint.
