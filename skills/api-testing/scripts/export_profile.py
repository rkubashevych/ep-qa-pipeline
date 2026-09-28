#!/usr/bin/env python3
"""Profile an export file: header row, per-column fill, named-cell checks.

The pipeline's rule for exports (skills/qa-pipeline/references/export-checks.md):
every export assertion checks the header AND the values. This script is the
instrument for the value half. Stdlib only - reads XLSX (via zipfile + XML)
and CSV; no openpyxl needed.

    python3 export_profile.py FILE                       # header + fill profile
    python3 export_profile.py FILE --baseline OLD_FILE   # + columns that lost values
    python3 export_profile.py FILE --expect 'COLUMN|ROW-MATCH|VALUE' [--expect ...]
    python3 export_profile.py FILE --sheet 2             # XLSX sheet by 1-based index
    python3 export_profile.py --selftest

--expect: in every data row containing ROW-MATCH (substring, any cell), the
cell under COLUMN must equal VALUE (after trimming). VALUE '<empty>' asserts an
empty cell. Exit code 1 when any expectation fails or no row matches.

Exit codes: 0 ok, 1 an expectation failed, 2 usage / unreadable file.
Never prints anything but the file's own contents - but a cell CAN hold a
secret if a fixture was careless; check before pasting output anywhere.
"""
import csv
import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
EMPTY = "<empty>"


def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group()
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def _text(node):
    return "".join(t.text or "" for t in node.iter(NS + "t"))


def read_xlsx(data, sheet_no=1):
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    shared = []
    if "xl/sharedStrings.xml" in names:
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(NS + "si"):
            shared.append(_text(si))
    sheet_path = None
    if "xl/workbook.xml" in names and "xl/_rels/workbook.xml.rels" in names:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = wb.find(NS + "sheets")
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        if sheets is not None and len(sheets) >= sheet_no:
            rid = sheets[sheet_no - 1].get(RNS + "id")
            tgt = targets.get(rid, "")
            tgt = tgt.lstrip("/")
            sheet_path = tgt if tgt.startswith("xl/") else "xl/" + tgt
    if sheet_path not in names:
        cands = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        if len(cands) < sheet_no:
            raise ValueError("no worksheet %d in the file" % sheet_no)
        sheet_path = cands[sheet_no - 1]
    root = ET.fromstring(z.read(sheet_path))
    rows = []
    for r in root.iter(NS + "row"):
        cells = {}
        for c in r.findall(NS + "c"):
            t, v, inl = c.get("t"), c.find(NS + "v"), c.find(NS + "is")
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif inl is not None:
                val = _text(inl)
            elif v is not None:
                val = v.text or ""
            else:
                val = ""
            ref = c.get("r")
            idx = _col_index(ref) if ref else (max(cells) + 1 if cells else 1)
            cells[idx] = val
        width = max(cells) if cells else 0
        rows.append([cells.get(i, "") for i in range(1, width + 1)])
    return rows


def read_csv(data):
    text = data.decode("utf-8-sig", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return [list(r) for r in csv.reader(io.StringIO(text), dialect)]


def load(path, sheet_no=1):
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:2] == b"PK":
        rows = read_xlsx(data, sheet_no)
    else:
        rows = read_csv(data)
    rows = [r for r in rows if any((c or "").strip() for c in r)]
    if not rows:
        return [], []
    header = [(h or "").strip() for h in rows[0]]
    width = max(len(header), max(len(r) for r in rows))
    header += [""] * (width - len(header))
    data_rows = [r + [""] * (width - len(r)) for r in rows[1:]]
    return header, data_rows


def profile(header, rows):
    out = []
    for i, h in enumerate(header):
        vals = [(r[i] or "").strip() for r in rows]
        filled = [v for v in vals if v]
        samples = []
        for v in filled:
            if v not in samples:
                samples.append(v)
            if len(samples) == 2:
                break
        out.append({"col": i + 1, "header": h, "filled": len(filled), "samples": samples})
    return out


def fmt_profile(path, header, rows, prof):
    lines = ["file: %s" % path, "data rows: %d, columns: %d" % (len(rows), len(header))]
    for p in prof:
        smp = " | ".join(" ".join(s.split())[:40] for s in p["samples"])
        lines.append("%3d  %-48.48s filled %d/%d%s" % (
            p["col"], p["header"] or "(no header)", p["filled"], len(rows),
            ("   e.g. " + smp) if smp else ""))
    empty = [p for p in prof if p["filled"] == 0]
    if not rows:
        lines.append("WARN NO DATA ROWS - this file can only verify structure (export-checks.md)")
    elif empty:
        lines.append("WARN EMPTY ON EVERY ROW (a finding until explained): " +
                     ", ".join("%d %s" % (p["col"], p["header"] or "(no header)") for p in empty))
    return lines


def compare(prof, base_prof, n, base_n):
    lines = []
    base = {p["header"]: p for p in base_prof if p["header"]}
    for p in prof:
        b = base.get(p["header"])
        if not b or not base_n:
            continue
        old = b["filled"] / base_n
        new = p["filled"] / n if n else 0.0
        if b["filled"] and (p["filled"] == 0 or new < old / 2):
            lines.append("WARN FILL DROPPED: %s - baseline %d/%d (%.0f%%) -> now %d/%d (%.0f%%)" % (
                p["header"], b["filled"], base_n, old * 100, p["filled"], n, new * 100))
    now = {p["header"] for p in prof}
    for h in base:
        if h not in now:
            lines.append("WARN COLUMN GONE vs baseline: %s" % h)
    for p in prof:
        if p["header"] and p["header"] not in base:
            lines.append("- new column vs baseline: %s" % p["header"])
    return lines or ["baseline: no column lost values"]


def check_expect(header, rows, spec):
    parts = spec.split("|")
    if len(parts) != 3:
        return False, "BAD --expect %r (want 'COLUMN|ROW-MATCH|VALUE')" % spec
    col, match, want = parts[0].strip(), parts[1], parts[2].strip()  # ROW-MATCH kept verbatim
    if col not in header:
        return False, "FAIL %s - no column %r in the header" % (spec, col)
    i = header.index(col)
    hits = [r for r in rows if any(match in (c or "") for c in r)]
    if not hits:
        return False, "FAIL %s - no data row contains %r" % (spec, match)
    want_v = "" if want == EMPTY else want
    bad = [(r[i] or "").strip() for r in hits if (r[i] or "").strip() != want_v]
    if bad:
        return False, "FAIL %s - %d of %d matching row(s) read %r" % (
            spec, len(bad), len(hits), bad[0] if bad[0] else EMPTY)
    return True, "PASS %s - %d matching row(s)" % (spec, len(hits))


def _xlsx_bytes(rows):
    """Minimal XLSX (inline strings) for the self-test."""
    def cell(ci, ri, v):
        col = ""
        n = ci
        while n:
            n, rem = divmod(n - 1, 26)
            col = chr(65 + rem) + col
        esc = v.replace("&", "&amp;").replace("<", "&lt;")
        return '<c r="%s%d" t="inlineStr"><is><t>%s</t></is></c>' % (col, ri, esc)
    body = "".join(
        '<row r="%d">%s</row>' % (ri, "".join(cell(ci, ri, v) for ci, v in enumerate(r, 1) if v != ""))
        for ri, r in enumerate(rows, 1))
    sheet = ('<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/'
             'spreadsheetml/2006/main"><sheetData>%s</sheetData></worksheet>' % body)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()


def selftest():
    import os
    import tempfile
    rows = [["Name", "Company", "Email", "Job Title"],
            ["zz Member X", "Acme", "x@t.test", ""],
            ["zz Member X3", "Acme", "", ""],
            ["zz Owner2", "Beta", "o2@t.test", ""]]
    base = [["Name", "Company", "Email", "Job Title"],
            ["zz Member X", "Acme", "x@t.test", "Buyer"],
            ["zz Member X3", "Acme", "x3@t.test", "Seller"]]
    ok = True
    with tempfile.TemporaryDirectory() as d:
        fx, fb, fc = (os.path.join(d, n) for n in ("a.xlsx", "b.xlsx", "c.csv"))
        open(fx, "wb").write(_xlsx_bytes(rows))
        open(fb, "wb").write(_xlsx_bytes(base))
        open(fc, "w", encoding="utf-8", newline="").write(
            "\n".join(",".join(r) for r in rows) + "\n")
        for path in (fx, fc):
            h, r = load(path)
            prof = profile(h, r)
            got = {p["header"]: p["filled"] for p in prof}
            ok &= h == rows[0] and len(r) == 3
            ok &= got == {"Name": 3, "Company": 3, "Email": 2, "Job Title": 0}
            text = "\n".join(fmt_profile(path, h, r, prof))
            ok &= "EMPTY ON EVERY ROW" in text and "Job Title" in text.split("EMPTY ON EVERY ROW")[1]
        h, r = load(fx)
        bh, br = load(fb)
        cmp_lines = compare(profile(h, r), profile(bh, br), len(r), len(br))
        ok &= any("FILL DROPPED: Job Title" in l for l in cmp_lines)
        ok &= not any("FILL DROPPED: Email" in l for l in cmp_lines)  # 2/3 vs 2/2: not halved
        ok &= check_expect(h, r, "Email|Member X3|<empty>")[0]
        ok &= not check_expect(h, r, "Email|Member X3|x3@t.test")[0]
        ok &= check_expect(h, r, "Email|zz Owner2|o2@t.test")[0]
        ok &= not check_expect(h, r, "Phone|Member X|1")[0]
        ok &= not check_expect(h, r, "Email|nobody|x")[0]
        fe = os.path.join(d, "empty.csv")
        open(fe, "w").close()
        eh, er = load(fe)
        ok &= eh == [] and er == []
        oh, orows = load(fb)  # header only, no data rows
        oh_text = "\n".join(fmt_profile(fb, oh, [], profile(oh, [])))
        ok &= "NO DATA ROWS" in oh_text
    print("SELFTEST PASS - xlsx + csv parse, fill profile, empty-column flag, baseline drop, --expect"
          if ok else "SELFTEST FAIL")
    return 0 if ok else 1


def main(argv):
    try:  # a cell may hold any character; never crash on a narrow console codepage
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    if "--selftest" in argv:
        return selftest()
    args, expects, baseline, sheet = [], [], None, 1
    it = iter(argv)
    for a in it:
        if a == "--expect":
            expects.append(next(it, ""))
        elif a == "--baseline":
            baseline = next(it, None)
        elif a == "--sheet":
            sheet = int(next(it, "1"))
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            args.append(a)
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        header, rows = load(args[0], sheet)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as e:
        print("cannot read %s: %s" % (args[0], e))
        return 2
    prof = profile(header, rows)
    print("\n".join(fmt_profile(args[0], header, rows, prof)))
    if baseline:
        try:
            bh, br = load(baseline, sheet)
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as e:
            print("cannot read baseline %s: %s" % (baseline, e))
            return 2
        print("baseline: %s (%d rows)" % (baseline, len(br)))
        print("\n".join(compare(prof, profile(bh, br), len(rows), len(br))))
    failed = False
    for spec in expects:
        good, line = check_expect(header, rows, spec)
        failed |= not good
        print(line)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
