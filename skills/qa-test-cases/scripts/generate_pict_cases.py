#!/usr/bin/env python3
"""Pairwise (2-wise) test-combination generator for the qa-test-cases skill.

Input: a PICT-style model file.
    Parameter: value1, value2, value3
    OtherParam: a, b
Lines starting with # are comments. Blank lines ignored.
Constraint lines (IF/THEN, [Param] syntax) are NOT supported by the
built-in generator — if the model contains them, install Microsoft
PICT and this script will delegate to the `pict` binary automatically.

Output (stdout): a markdown table of combinations, one row per
generated case, ready to be turned into TC-REQ-N.M blocks.

Usage:
    python3 generate_pict_cases.py model.txt
    python3 generate_pict_cases.py model.txt --order 3   # 3-wise
"""
import itertools
import shutil
import subprocess
import sys


def parse_model(path):
    params, constraints = [], []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.upper().startswith("IF ") or line.startswith("["):
                constraints.append(line)
                continue
            if ":" not in line:
                sys.exit(f"Bad model line (expected 'Name: v1, v2'): {line}")
            name, _, vals = line.partition(":")
            values = [v.strip() for v in vals.split(",") if v.strip()]
            if len(values) < 2:
                sys.exit(f"Parameter '{name.strip()}' needs >= 2 values")
            params.append((name.strip(), values))
    if len(params) < 2:
        sys.exit("Model needs >= 2 parameters")
    return params, constraints


def run_pict_binary(path, order):
    out = subprocess.run(["pict", path, f"/o:{order}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"pict failed: {out.stderr.strip()}")
    rows = [r.split("\t") for r in out.stdout.strip().splitlines()]
    return rows[0], rows[1:]


def greedy_pairwise(params, order):
    """Greedy IPO-style n-wise generation. Deterministic."""
    names = [p[0] for p in params]
    axes = [p[1] for p in params]
    idx = range(len(params))
    uncovered = set()
    for combo in itertools.combinations(idx, order):
        for vals in itertools.product(*(axes[i] for i in combo)):
            uncovered.add((combo, vals))

    def covered_by(case):
        hits = set()
        for combo in itertools.combinations(idx, order):
            key = (combo, tuple(case[i] for i in combo))
            if key in uncovered:
                hits.add(key)
        return hits

    cases = []
    while uncovered:
        best_case, best_hits = None, set()
        # seed each candidate from an uncovered tuple, fill greedily
        for (combo, vals) in itertools.islice(iter(sorted(uncovered)), 50):
            case = [None] * len(params)
            for c, v in zip(combo, vals):
                case[c] = v
            for i in idx:
                if case[i] is None:
                    scored = []
                    for v in axes[i]:
                        case[i] = v
                        scored.append((len(covered_by(
                            [x if x is not None else axes[j][0]
                             for j, x in enumerate(case)])), v))
                    case[i] = max(scored)[1]
            hits = covered_by(case)
            if len(hits) > len(best_hits):
                best_case, best_hits = case, hits
        cases.append(best_case)
        uncovered -= best_hits
    return names, cases


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    order = 2
    for i, a in enumerate(sys.argv):
        if a == "--order":
            order = int(sys.argv[i + 1])
    if not args:
        sys.exit(__doc__)
    params, constraints = parse_model(args[0])

    if constraints:
        if shutil.which("pict"):
            names, rows = run_pict_binary(args[0], order)
        else:
            sys.exit("Model has constraints — install Microsoft PICT "
                     "(github.com/microsoft/pict) or remove the "
                     "constraint lines and filter rows manually.")
    elif shutil.which("pict"):
        names, rows = run_pict_binary(args[0], order)
    else:
        names, rows = greedy_pairwise(params, order)

    total = 1
    for _, vals in params:
        total *= len(vals)
    print(f"# {order}-wise combinations: {len(rows)} cases "
          f"(exhaustive would be {total})")
    print()
    print("| # | " + " | ".join(names) + " |")
    print("|---|" + "|".join(["---"] * len(names)) + "|")
    for n, row in enumerate(rows, 1):
        print(f"| {n} | " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
