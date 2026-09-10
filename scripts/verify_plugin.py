#!/usr/bin/env python3
"""verify_plugin.py — the pre-commit gate for the ep-qa-pipeline repo.

    python3 scripts/verify_plugin.py            # check the repo you are in
    python3 scripts/verify_plugin.py --root X   # check another checkout
    python3 scripts/verify_plugin.py --no-git   # skip the staged-paths check

Runs in a few seconds and exits non-zero on any FAIL. Parked since 0.18.2,
shipped in 0.36.0 after two days in which every class of defect it
catches actually happened: two skill descriptions over the 1024-char
discovery ceiling, a fix "written and never committed" for two rounds,
CRLF churn on five files, two files without a trailing newline.

Checks (MAINTAINERS recipe step 6.0):
  1. versions   plugin.json == marketplace.json == CHANGELOG top heading
  2. skills     every skills/*/SKILL.md: frontmatter `name` == folder,
                `description` <= 1024 chars (joined), <= 500 lines (WARN)
  3. text       every tracked text file: LF only, no NUL, trailing newline
  4. wiring     every skill folder is named in README.md and has a
                `## <name>` section in evals/triggering.md
  5. references every `references/<file>.md` a SKILL.md or reference
                names exists — same-skill, `<skill>/references/` and
                `../<skill>/references/` forms; write cross-skill
                references in one of the last two so this can check them
  6. vocabulary every status in status-vocabulary.md has its base token
                in reconcile_counts.py STATUSES
  7. selftest   reconcile_counts.py --selftest passes
  8. staged     `git diff --cached --name-only` has no run-artefact path
                (runs/, EP-*, GS-*, build_*, repro_*, *-testdata*,
                *-runsheet*, *-walk-*, .env*, _*) — the `git add -A` guard
"""
import os
import re
import subprocess
import sys

TEXT_GLOBS = ("README.md", "MAINTAINERS.md", "CHANGELOG.md", "CLAUDE.md",
              ".gitignore", ".claude-plugin/plugin.json",
              ".claude-plugin/marketplace.json", "evals/triggering.md")
ARTEFACT_PATTERNS = [
    re.compile(p) for p in (
        r"^runs/", r"(^|/)EP-\d", r"(^|/)GS-", r"(^|/)build_", r"(^|/)repro_",
        r"-testdata", r"-runsheet", r"-walk-", r"(^|/)\.env", r"(^|/)_[^_]",
    )
]
DESC_LIMIT = 1024
LINES_WARN = 500


class Report:
    def __init__(self):
        self.fails, self.warns, self.oks = [], [], []

    def ok(self, msg):
        self.oks.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def fail(self, msg):
        self.fails.append(msg)


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, None
    fm = m.group(1)
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc = re.search(r"^description:\s*>\n((?:[ \t]+.*\n?)+)", fm, re.M)
    if desc:
        d = " ".join(l.strip() for l in desc.group(1).splitlines() if l.strip())
    else:
        d1 = re.search(r"^description:\s*(.+)$", fm, re.M)
        d = d1.group(1).strip() if d1 else None
    return (name.group(1).strip() if name else None), d


def skill_dirs(root):
    base = os.path.join(root, "skills")
    return sorted(d for d in os.listdir(base)
                  if os.path.isfile(os.path.join(base, d, "SKILL.md")))


def check_versions(root, r):
    try:
        import json
        pv = json.loads(read(root, ".claude-plugin/plugin.json"))["version"]
        mv = json.loads(read(root, ".claude-plugin/marketplace.json"))["plugins"][0]["version"]
    except Exception as e:  # noqa: BLE001
        r.fail(f"versions: cannot read manifests ({e})")
        return
    m = re.search(r"^## (\d+\.\d+\.\d+)\b", read(root, "CHANGELOG.md"), re.M)
    cv = m.group(1) if m else None
    if pv == mv == cv:
        r.ok(f"versions: plugin.json = marketplace.json = CHANGELOG = {pv}")
    else:
        r.fail(f"versions: plugin.json {pv} / marketplace.json {mv} / CHANGELOG {cv}")


def check_skills(root, r):
    for d in skill_dirs(root):
        rel = f"skills/{d}/SKILL.md"
        text = read(root, rel)
        name, desc = frontmatter(text)
        if name != d:
            r.fail(f"{rel}: frontmatter name {name!r} != folder {d!r}")
        if desc is None:
            r.fail(f"{rel}: no description in frontmatter")
        elif len(desc) > DESC_LIMIT:
            r.fail(f"{rel}: description {len(desc)} chars > {DESC_LIMIT}")
        n = text.count("\n")
        if n > LINES_WARN:
            r.warn(f"{rel}: {n} lines > {LINES_WARN} (move detail to references/)")
    r.ok(f"skills: {len(skill_dirs(root))} SKILL.md frontmatters checked")


def text_files(root):
    for rel in TEXT_GLOBS:
        if os.path.exists(os.path.join(root, rel)):
            yield rel
    for dirpath, _, files in os.walk(os.path.join(root, "skills")):
        for f in files:
            if f.endswith((".md", ".py", ".json", ".sh")) and "__pycache__" not in dirpath:
                yield os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/")
    for dirpath, _, files in os.walk(os.path.join(root, "scripts")):
        for f in files:
            if f.endswith(".py"):
                yield os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, "/")


def check_text(root, r):
    n = 0
    for rel in text_files(root):
        n += 1
        b = open(os.path.join(root, rel), "rb").read()
        if b"\r" in b:
            r.fail(f"{rel}: CRLF line endings (repo is LF-only)")
        if b"\x00" in b:
            r.fail(f"{rel}: NUL bytes (truncated write through the mount?)")
        if b and not b.endswith(b"\n"):
            r.fail(f"{rel}: no trailing newline")
    r.ok(f"text: {n} files LF / no NUL / trailing newline")


def check_wiring(root, r):
    readme = read(root, "README.md")
    evals = read(root, "evals/triggering.md") if os.path.exists(os.path.join(root, "evals/triggering.md")) else ""
    for d in skill_dirs(root):
        if f"`{d}`" not in readme and d not in readme:
            r.fail(f"wiring: skill {d} is not named in README.md")
        if not re.search(rf"^## {re.escape(d)}\b", evals, re.M):
            r.fail(f"wiring: evals/triggering.md has no `## {d}` section")
    r.ok("wiring: every skill named in README and evals")


REF_RE = re.compile(r"(?:(?:\.\./)*([\w-]+)/)?references/([\w\-.]+\.md)")


def check_references(root, r):
    missing = set()
    for d in skill_dirs(root):
        sdir = os.path.join(root, "skills", d)
        for dirpath, _, files in os.walk(sdir):
            for f in files:
                if not f.endswith(".md"):
                    continue
                text = open(os.path.join(dirpath, f), encoding="utf-8").read()
                for skill, ref in REF_RE.findall(text):
                    target = os.path.join(root, "skills", skill or d, "references", ref)
                    if not os.path.exists(target):
                        missing.add(f"skills/{d}/{f} → skills/{skill or d}/references/{ref}")
    for m in sorted(missing):
        r.fail(f"references: {m} does not exist")
    if not missing:
        r.ok("references: every referenced references/*.md exists")


def check_vocabulary(root, r):
    vocab = read(root, "skills/qa-run-analyzer/references/status-vocabulary.md")
    script = read(root, "skills/qa-run-analyzer/scripts/reconcile_counts.py")
    m = re.search(r"STATUSES = \((.*?)\)", script, re.S)
    statuses = set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()
    bad = []
    for row in re.findall(r"^\| `([^`]+)` \|", vocab, re.M):
        base = re.sub(r"\s*\(.*\)$", "", re.sub(r"\s*\[.*\]$", "", row)).strip()
        if base not in statuses:
            bad.append(row)
    for b in bad:
        r.fail(f"vocabulary: `{b}` has no base token in reconcile_counts.STATUSES")
    if not bad:
        r.ok(f"vocabulary: every status in status-vocabulary.md is in STATUSES ({len(statuses)} tokens)")


def check_selftest(root, r):
    p = subprocess.run([sys.executable, "skills/qa-run-analyzer/scripts/reconcile_counts.py", "--selftest"],
                       cwd=root, capture_output=True, text=True)
    if p.returncode == 0 and "SELFTEST PASS" in p.stdout:
        r.ok("selftest: reconcile_counts.py --selftest PASS")
    else:
        r.fail("selftest: reconcile_counts.py --selftest FAILED\n" + (p.stdout + p.stderr).strip())


def check_staged(root, r):
    try:
        p = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=root,
                           capture_output=True, text=True, timeout=20)
    except Exception:  # noqa: BLE001
        r.warn("staged: git not available — staged-paths check skipped")
        return
    if p.returncode != 0:
        r.warn("staged: not a git repo (or git failed) — staged-paths check skipped")
        return
    bad = [f for f in p.stdout.split() if any(pat.search(f) for pat in ARTEFACT_PATTERNS)
           and not f.startswith("fixtures/")]
    for f in bad:
        r.fail(f"staged: run artefact staged for commit — {f} (never `git add -A`)")
    if not bad:
        r.ok(f"staged: {len(p.stdout.split())} staged path(s), none a run artefact")


def main():
    args = sys.argv[1:]
    root = os.getcwd()
    if "--root" in args:
        root = args[args.index("--root") + 1]
    no_git = "--no-git" in args
    r = Report()
    for check in (check_versions, check_skills, check_text, check_wiring,
                  check_references, check_vocabulary, check_selftest):
        try:
            check(root, r)
        except Exception as e:  # noqa: BLE001
            r.fail(f"{check.__name__}: crashed — {e}")
    if not no_git:
        check_staged(root, r)
    for m in r.oks:
        print(f"  ok    {m}")
    for m in r.warns:
        print(f"  WARN  {m}")
    for m in r.fails:
        print(f"  FAIL  {m}")
    print(f"verify_plugin: {len(r.oks)} ok · {len(r.warns)} warn · {len(r.fails)} fail")
    sys.exit(1 if r.fails else 0)


if __name__ == "__main__":
    main()
