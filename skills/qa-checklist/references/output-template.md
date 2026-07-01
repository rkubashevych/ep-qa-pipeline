# <ISSUEKEY> - QA checklist

Requirements: <path to the requirements file>
Notes: <carry forward any warning/unresolved-conflict note from the requirements file; omit the line if none>
Generated: <YYYY-MM-DD>

## Checklist

### REQ-1: <requirement text from the requirements file>
- [ ] REQ-1.1: [UI] <check>
- [ ] REQ-1.2: [API] <check>

### REQ-2: <requirement text from the requirements file>
- [ ] REQ-2.1: <check>
- [ ] REQ-2.2: <check>
- [ ] REQ-2.3: <check>

### REQ-3a: <requirement sub-item text from the requirements file>
- [ ] REQ-3a.1: <check>
- [ ] REQ-3a.2: <check>

### REQ-3b: <requirement sub-item text from the requirements file>
- [ ] REQ-3b.1: <check>

---

Section rules:
- Metadata (Requirements, Notes, Generated) — each on its own line. Omit Notes if there is nothing to carry forward.
- Each requirement — a separate ### subheading with the REQ-ID and
  the requirement text.
- Each check — a checkbox with REQ-ID.sub-number, then a channel tag ([UI] / [API] / [mobile] / [export/email]), then the check text.
- If a requirement has sub-items (REQ-3a, REQ-3b), each sub-item is
  a separate subheading with its own checks.
- The order of requirements matches the order in the requirements file.
