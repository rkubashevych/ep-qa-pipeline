# Setup guide for the Web Testing skill

This skill executes the QA and FAIL test cases in a real browser.
The testing logic, the classification, and the navigation memory are
universal. The only thing to configure is the login configuration.

This skill is configured for ExpoPlatform's stack:
- **Browser tool:** the Claude in Chrome extension
- **Target product:** an ExpoPlatform event / admin site
- **Tracker:** Jira (Atlassian Cloud), ticket key format `PROJECT-123` (e.g. `EP-1234`)

## What you need to know before configuring

### 1. Which browser tool do you use?

The skill is built for the **Claude in Chrome extension**.
All tool names (`navigate`, `find`, `computer`, `form_input`,
etc.) are the names of that extension's tools.

If you use the Playwright MCP or another tool —
you need to adapt all the tool names in SKILL.md
and references/browser-rules.md to your system.

### 2. What does login look like in your product?

For the ExpoPlatform event / admin site:
- The login URL
- How to find the email/username and password fields (label, placeholder)
- The submit button text
- Which credentials to use and where to get them
- What appears after a successful login

The shipped login-config.md is already filled in for the ExpoPlatform
e2e alpha and reads credentials from env vars / the e2e `.env`. When
adapting to ANOTHER product, use clearly-labelled placeholders
(`<LOGIN_URL>`, `<TEST_USER>`, `<TEST_PASSWORD>`) until the real
values are supplied. Never commit real credentials.

### 3. Is registration of new users needed?

If the test cases require creating new accounts —
prepare an email template and the default data for registration.

## Configuration

### Step 1: references/login-config.md — login (REQUIRED)

For ExpoPlatform the file is already configured — nothing to do.
When adapting to another product/environment, replace its values:

- The login URL
- The descriptions of the login form fields
- The credentials for each role
- The success indicator after login
- The post-login actions (if any)

If registration is not needed — delete the Registration section
and the Default data section.

### Step 2: navigation_paths.json — the navigation memory

The file is git-ignored (it accumulates environment-specific paths),
so a fresh clone does not have it. Nothing to configure — the skill
creates it on first run and fills it in as it learns paths. In Cowork,
keep it in a mounted persistent folder (see the persistence note in
SKILL.md Step 3) so the memory survives across sessions.

### Step 3 (optional): SKILL.md — the previous skill's name

If your skill chain is named differently than
`code-review` and `qa-test-cases` — update the references
to those skills in the "Input" section of SKILL.md.

## Verification after configuration

- [ ] references/login-config.md contains no `<placeholders>`
- [ ] The login URL is set
- [ ] The credentials for all roles are set
- [ ] The success indicator is set
- [ ] The source of the credentials is set (hardcoded / .env / other)

## Skill files

```
web-testing/
  SKILL.md                         — the skill instructions
  navigation_paths.json            — the memory of navigation paths
  references/
    login-config.md                — login configuration (configure this!)
    browser-rules.md               — browser interaction rules
    output-template.md             — output file template
  setup-guide.md                   — this guide
```
