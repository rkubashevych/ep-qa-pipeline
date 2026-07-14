#!/usr/bin/env python3
"""Extract `File: <name>` fenced blocks from Jira archive comments.

qa-pipeline-code Step 0 helper. Save the archive comment body/bodies
to text files, then:

    python3 extract_archive.py comment1.txt [comment2.txt ...] [-o DIR]

Handles: several files per comment, split files labeled
`File: <name> (part i/N)` (re-joined in order), fences of 3+ backticks,
CRLF line endings. Writes each file to DIR (default: cwd) and prints a
manifest. Exits non-zero on missing parts or malformed fences.
"""
import os
import re
import sys

LABEL = re.compile(
    r"^File:\s*(?P<name>\S+?)"
    r"(?:\s*\(part\s*(?P<i>\d+)\s*/\s*(?P<n>\d+)\))?\s*$")


def parse(text):
    """Yield (name, part_i, part_n, content) for each labeled block."""
    lines = text.replace("\r\n", "\n").split("\n")
    k = 0
    while k < len(lines):
        m = LABEL.match(lines[k].strip())
        if not m:
            k += 1
            continue
        # find the opening fence (skip blank lines)
        j = k + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        fence = re.match(r"^(`{3,})", lines[j].strip()) if j < len(lines) else None
        if not fence:
            sys.exit(f"ERROR: no fenced block after label: {lines[k].strip()}")
        marker = fence.group(1)
        body, j = [], j + 1
        while j < len(lines):
            if lines[j].strip() == marker:
                break
            body.append(lines[j])
            j += 1
        else:
            sys.exit(f"ERROR: unclosed fence for {m.group('name')}")
        yield (m.group("name"),
               int(m.group("i")) if m.group("i") else None,
               int(m.group("n")) if m.group("n") else None,
               "\n".join(body))
        k = j + 1


def main():
    argv = sys.argv[1:]
    outdir = "."
    if "-o" in argv:
        p = argv.index("-o")
        outdir = argv[p + 1]
        argv = argv[:p] + argv[p + 2:]
    if not argv:
        sys.exit(__doc__)
    files = {}   # name -> {None: content} or {i: content, ..., 'n': N}
    for path in argv:
        with open(path, encoding="utf-8") as f:
            for name, i, n, content in parse(f.read()):
                d = files.setdefault(name, {})
                if i is None:
                    d[0] = content
                else:
                    d[i] = content
                    d["n"] = n
    os.makedirs(outdir, exist_ok=True)
    for name, d in files.items():
        n = d.pop("n", None)
        if n:
            missing = [str(i) for i in range(1, n + 1) if i not in d]
            if missing:
                sys.exit(f"ERROR: {name} missing part(s) {','.join(missing)}/{n}")
            content = "\n".join(d[i] for i in range(1, n + 1))
        else:
            content = d[0]
        dest = os.path.join(outdir, os.path.basename(name))
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content if content.endswith("\n") else content + "\n")
        parts = f" ({n} parts)" if n else ""
        print(f"wrote {dest}: {len(content.splitlines())} lines{parts}")


if __name__ == "__main__":
    main()
