# Document Versioning Discipline

Prevents version artifact corruption when producing new versions of numbered
documents (reports, analyses, handoff packages).

## Contents

- [Rule 1 — Copy first, edit second](#rule-1--copy-first-edit-second-blocking) • [Rule 2 — Header-filename consistency](#rule-2--header-filename-consistency) • [Rule 3 — Classify un-numbered files](#rule-3--classify-un-numbered-files) • [Rule 4 — PDF parity](#rule-4--pdf-parity) • [Rule 5 — Version chain integrity](#rule-5--version-chain-integrity) • [Safe version bump checklist](#safe-version-bump-checklist) • [Knowledge](#knowledge)

## Rule 1 — Copy first, edit second (BLOCKING)

**Never edit a numbered version file in-place to produce a new version.**

Create the new version file before making any edits:

```bash
cp REPORT-vN.md REPORT-v(N+1).md
```

All edits go into `v(N+1).md`. `vN.md` must remain byte-for-byte identical to
its original archival state.

## Rule 2 — Header-filename consistency

The version number in the document header must match the filename:

| Filename | Required header field |
|----------|-----------------------|
| `REPORT-v4.md` | `**Date:** ... (v4 — ...)` or equivalent version line |
| `REPORT-v5.md` | `**Previous version:** v4 (...)` |

After any rename, update the date/version line, the `Previous version:`
reference, and any top changelog block.

## Rule 3 — Classify un-numbered files

Un-numbered files (e.g., `Report.md`, `REPORT-Analysis.md`) must be classified
before acting:

| Question | If YES | If NO |
|----------|--------|-------|
| Does the header contain a version reference? | Versioned file in disguise — rename to match | Working draft — do not archive alongside versions |
| Does it duplicate an existing numbered version? | Confirm content matches, then alias or delete | May fill a gap in the version sequence |
| Is it newer than the highest numbered version? | Belongs at next version slot — rename accordingly | Older draft — identify which version it maps to |

Un-numbered files must never remain alongside numbered versions without
explicit classification.

## Rule 4 — PDF parity

Every `.md` version must have a matching `.pdf` rendered from that exact file
after all renames and edits are finalized:

```bash
./render.sh REPORT-vN.md

# Verify parity (empty output = healthy)
ls *.md *.pdf | sed 's/\.md$//' | sed 's/\.pdf$//' | sort | uniq -c | awk '$1 != 2'
```

## Rule 5 — Version chain integrity

Minimum required header fields for any version >= v2:

```markdown
**Date:** YYYY-MM-DD (vN — description of changes)
**Previous version:** v(N-1) (YYYY-MM-DD — description of that version)
```

## Safe version bump checklist

- [ ] Run pre-operation inventory (`ls -1 *.md *.pdf 2>/dev/null | sort`) — confirm chain is intact
- [ ] `cp REPORT-vN.md REPORT-v(N+1).md` — create the new file first
- [ ] Make all edits in `v(N+1).md` only
- [ ] Update header: version line, previous version reference, date, and changelog
- [ ] Verify `vN.md` is unchanged
- [ ] Render `v(N+1).pdf` and confirm it is non-zero and matches `v(N+1).md`
- [ ] Confirm `vN.pdf` still exists and matches `vN.md`

## Knowledge

- 2026-04-22: [[engagement]] [CONTEXT: toolchain] Editing `v5.md` in-place before copying to `v6.md` silently destroyed `v5` as an archival source; an un-numbered draft proved to be the true `v4` alignment revision — CAUSE: in-place editing before copy — FIX: always copy `vN.md` to `v(N+1).md` first and classify un-numbered files before editing.
- 2026-04-22: [[engagement]] [CONTEXT: toolchain] Rendering PDFs before finalizing filename renames caused `v4.pdf` to hold `v5` content while `v4.pdf` and `v6.pdf` were missing — FIX: render PDFs only as the final step after all renames are confirmed.
