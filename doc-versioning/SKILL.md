---
name: doc-versioning
description: Enforces safe versioning discipline for numbered report/document files — copy-first rule, header-filename consistency, un-numbered file classification, PDF parity, and pre-operation inventory. Use whenever creating a new version of a versioned document or working with a report that has both .md and .pdf artefacts.
tools: Read, Bash, Grep, Glob
metadata:
  author: Ryan Loiselle
  version: "1.0"
---

# Document Versioning Skill

Prevents version artefact corruption when producing new versions of numbered
documents (reports, analyses, handoff packages). Based on a failure mode
encountered during the JUSTINRCC Migration Analysis — where v5.md was edited
in-place to produce v6 content, silently overwriting the archival v5.

---

## Rule 1 — Copy First, Edit Second (BLOCKING)

**Never edit a numbered version file to produce a new version.**

Before making any edits, create the new version file:

```bash
cp REPORT-vN.md REPORT-v(N+1).md
```

All edits go into `v(N+1).md`. `vN.md` must remain byte-for-byte identical to
its original state as the archival source.

> This is the single most important rule. Violating it destroys the version
> history — once overwritten, the original content is unrecoverable unless
> a git commit or backup exists.

---

## Rule 2 — Header–Filename Consistency

The version number in the document header must match the filename.

| Filename | Required header field |
|----------|-----------------------|
| `REPORT-v4.md` | `**Date:** ... (v4 — ...)` or equivalent version line |
| `REPORT-v5.md` | `**Previous version:** v4 (...)` |

After any rename, open the file and update:
- The date/version line
- The `Previous version:` reference (if present)
- Any internal v-note or changelog block at the top

---

## Rule 3 — Classify Un-numbered Files Before Acting

Un-numbered files (e.g., `Report.md`, `REPORT-Analysis.md`) have ambiguous
status. Before treating them as a version, classify them:

| Question | If YES | If NO |
|----------|--------|-------|
| Does the header contain a version reference? | It is a versioned file in disguise — rename to match | It is a working draft — do not archive |
| Does it duplicate an existing numbered version? | Confirm content matches, then decide: alias or delete | It may fill a gap in the version sequence |
| Is it newer than the highest numbered version? | It belongs at the next version slot — rename accordingly | It is an older draft — identify which version it maps to |

> Un-numbered files must never remain in the directory alongside numbered
> versions without explicit classification. Ambiguity causes future confusion
> for both humans and AI agents.

---

## Rule 4 — PDF Parity

Every `.md` version must have a corresponding `.pdf` rendered from that exact
`.md` file. Render immediately when the `.md` is finalised.

```bash
# Render a single version (using render.sh in the report directory)
./render.sh REPORT-vN.md

# Verify parity after any rename/delete operation
ls *.md *.pdf | sed 's/\.md$//' | sed 's/\.pdf$//' | sort | uniq -c | awk '$1 != 2'
# If this outputs anything, parity is broken
```

PDF naming must exactly match the `.md` basename:
- `REPORT-v4.md` → `REPORT-v4.pdf`
- `REPORT-v5.md` → `REPORT-v5.pdf`

---

## Rule 5 — Version Chain Integrity

Each file's header must explicitly name its previous version. This creates a
human-readable chain and allows AI agents to reconstruct the history.

Minimum required header fields for any version ≥ v2:

```markdown
**Date:** YYYY-MM-DD (vN — description of changes)
**Previous version:** v(N-1) (YYYY-MM-DD — description of that version)
```

If the previous version line is missing, add it before producing a new version.

---

## Pre-Operation Inventory

Run this before starting any versioning task:

```bash
# List all .md and .pdf files sorted, showing which pairs exist
ls -1 *.md *.pdf 2>/dev/null | sort
```

Confirm:
1. Every `.md` has a matching `.pdf` (or note which are missing)
2. The version sequence is contiguous (no gaps, no un-numbered artefacts)
3. No duplicate content exists under different names

Document any gaps before proceeding — do not add a new version on top of a
broken chain.

---

## Safe Version Bump Checklist

Use this checklist whenever creating a new version:

- [ ] Run pre-operation inventory — confirm chain is intact
- [ ] `cp vN.md v(N+1).md` — create the new file first
- [ ] Make all edits in `v(N+1).md` only
- [ ] Update header: version line, previous version reference, date
- [ ] Update any internal v-note / changelog block
- [ ] Verify `vN.md` is unchanged (file size / diff if uncertain)
- [ ] `./render.sh v(N+1).md` — produce the PDF immediately
- [ ] Confirm `v(N+1).pdf` exists and is non-zero
- [ ] Confirm `vN.pdf` still exists and matches `vN.md`

---

## KNOWLEDGE

Causal discoveries appended by agent-evolution at session end.

- 2026-04-22: [JUSTINRCC] v5.md was edited in-place to produce v6 content before being copied to v6.md. This silently destroyed v5 as an archival source. The unnumbered `JUSTINRCC-Migration-Analysis.md` turned out to be the true v4 content (ag-devops alignment revision), not a "latest alias" — it was unmodified and saved the recovery. Without it, v4 would have been permanently lost. Copy-first is now Rule 1.
- 2026-04-22: [JUSTINRCC] v4.pdf was rendered from what was labelled v4.md — but that file contained v5 content (post in-place edit). After renaming, v4.pdf became v5.pdf (mismatched but content-correct). Both v4.pdf and v6.pdf were missing and required re-render after the rename sequence completed. Always render PDFs as the final step after all renames are confirmed.
