#!/usr/bin/env python3
"""skill_stamp.py — the `Skill:` line every stage report carries in its header.

    python3 skill_stamp.py <skill-name>     # → Skill: code-review 0.47.0 · sha 3f9a1c2
    python3 skill_stamp.py --selftest

The version is the plugin's (`.claude-plugin/plugin.json`); the sha is over
what the skill actually runs with: its SKILL.md, its references/*.md, its
scripts/*.py, and the shared skills/qa-pipeline/references/*.md and
scripts/*.py every stage reads (status vocabulary lives with the analyzer
and is included for every skill too). A local edit anywhere in that set
that was never released shows as a different sha under the same version.

Why (0.47.0): a report carried a `Date:` and nothing else, so "was that run
0.45 or 0.46, or a local edit?" had no answer — and the analyzer could not
tie a stage misbehaving to the rules it ran with. Borrowed from qa-service,
which stamps the sha256 of the methodology text on every work order and
review (lib/server/mcp/workOrder.ts, registerReview.ts). Stdlib only.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def stamp(skill, root=ROOT):
    sdir = os.path.join(root, "skills", skill)
    main = os.path.join(sdir, "SKILL.md")
    if not os.path.exists(main):
        raise FileNotFoundError(f"no skill {skill!r} under {os.path.join(root, 'skills')}")
    files = [main]
    dirs = [(os.path.join(sdir, "references"), ".md"), (os.path.join(sdir, "scripts"), ".py"),
            (os.path.join(root, "skills", "qa-pipeline", "references"), ".md"),
            (os.path.join(root, "skills", "qa-pipeline", "scripts"), ".py")]
    for d, ext in dirs:
        if os.path.isdir(d):
            files += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(ext)]
    vocab = os.path.join(root, "skills", "qa-run-analyzer", "references", "status-vocabulary.md")
    if os.path.exists(vocab):
        files.append(vocab)
    h = hashlib.sha256()
    for f in dict.fromkeys(files):   # de-duplicated, order kept (qa-pipeline itself)
        h.update(os.path.relpath(f, root).replace(os.sep, "/").encode())
        with open(f, "rb") as fh:
            h.update(fh.read().replace(b"\r\n", b"\n"))
    try:
        with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8-sig") as fh:
            version = json.load(fh)["version"]
    except (OSError, ValueError, KeyError):
        version = "unknown"
    return f"Skill: {skill} {version} · sha {h.hexdigest()[:7]}"


def selftest():
    errs = []
    try:
        s = stamp("qa-pipeline")
        if not s.startswith("Skill: qa-pipeline ") or " · sha " not in s:
            errs.append(f"unexpected stamp shape: {s}")
        if stamp("qa-pipeline") != s:
            errs.append("stamp is not deterministic")
    except Exception as e:  # noqa: BLE001
        errs.append(f"stamp failed: {e}")
    try:
        stamp("no-such-skill")
        errs.append("an unknown skill did not raise")
    except FileNotFoundError:
        pass
    if errs:
        print("SELFTEST FAIL")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("SELFTEST PASS — stamp shape, determinism, unknown skill refused")


def main(argv):
    try:  # Windows consoles default to cp1252; the stamp carries a middle dot
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if argv[:1] == ["--selftest"]:
        selftest()
        return 0
    if len(argv) != 1:
        print(__doc__)
        return 2
    try:
        print(stamp(argv[0]))
    except FileNotFoundError as e:
        print(e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
