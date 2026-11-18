---
name: documenting-architecture
description: >-
  Creates, exports, and versions architecture documentation, including the
  10-diagram standard suite (draw.io, PlantUML, and Mermaid) and safe
  versioning discipline for numbered markdown and PDF reports. Use when
  generating or exporting architecture diagrams, setting up diagram folders,
  or producing a new version of a numbered document or report.
---

# Documenting Architecture

Maintains the 10-diagram architecture suite and enforces copy-first versioning
discipline for numbered markdown and PDF deliverables.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Maintain all 10 base diagrams**: never delete base suite diagrams; add feature-specific diagrams alongside them per [ten-diagram-suite.md](references/ten-diagram-suite.md).
2. **SVG preferred**: export `.drawio` and `.puml` sources to SVG (plus PNG where Markdown viewers lack SVG support) and commit both source and exported renders.
3. **Copy first, edit second (BLOCKING)**: never edit `REPORT-vN.md` in-place to create `v(N+1)`; copy `vN.md` to `v(N+1).md` first per [doc-versioning.md](references/doc-versioning.md).
4. **PDF parity**: every versioned `.md` file must have a matching `.pdf` rendered after all renames and edits are finalized.

## Quick start

Select the diagramming tool for your artifact, then follow [Workflow](#workflow) for diagram exports or versioned reports:

| Use draw.io when... | Use PlantUML when... | Use Mermaid when... |
|---------------------|----------------------|---------------------|
| Deployment & network topology | C4 Context / Container / Component | Quick inline docs |
| Free-form infra & whiteboarding | Sequence, class, state, ERD | GitHub README & folder trees |

## Workflow

1. **Architecture diagrams**:
   - Place sources under `diagrams/drawio/`, `diagrams/plantuml/`, and `diagrams/data-model/`.
   - Author PlantUML diagrams from [plantuml-templates.md](references/plantuml-templates.md).
   - Export SVG/PNG renders using `drawio --export` and `plantuml -tsvg` / `-tpng`.
2. **Versioned reports**:
   - Run pre-operation inventory (`ls -1 *.md *.pdf | sort`) to verify chain integrity.
   - Classify any un-numbered `.md` files before bumping.
   - Copy `REPORT-vN.md` -> `REPORT-v(N+1).md`, update headers and `Previous version:`, then render PDF.

## Verification

Confirm exported diagram renders exist for all sources and `.md`/`.pdf` parity
holds with zero mismatches:

```bash
ls *.md *.pdf 2>/dev/null | sed 's/\.md$//' | sed 's/\.pdf$//' | sort | uniq -c | awk '$1 != 2'
```

## References

- [Ten-Diagram Suite](references/ten-diagram-suite.md) — unified 10-diagram suite, folder layout, VS Code extensions, and CLI export commands
- [PlantUML Templates](references/plantuml-templates.md) — index of diagram template skeletons
- [Diagram Templates](assets/templates/sequence.puml) — `.puml` (`sequence`, `class`, `state`, `c4-context`), `.mmd` (`architecture.mmd`), and `.drawio` (`architecture.drawio`) templates
- [Document Versioning](references/doc-versioning.md) — copy-first rule, header consistency, un-numbered file classification, and PDF parity
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for diagram exports and report versioning
