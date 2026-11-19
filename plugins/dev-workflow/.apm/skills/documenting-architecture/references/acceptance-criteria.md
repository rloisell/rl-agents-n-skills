# Acceptance Criteria — documenting-architecture

Observable pass/fail criteria for verifying architecture diagramming and document versioning workflows.

## Diagram Suite & Exports

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Base suite preservation | All 10 base suite diagrams remain present; feature diagrams are added alongside them | Any base diagram is deleted or overwritten without replacement |
| Source & folder layout | Sources live in `diagrams/drawio/`, `diagrams/plantuml/`, or `diagrams/data-model/` | Diagram sources placed in ad-hoc or root directories |
| Export format parity | Every `.drawio` and `.puml` source has a matching exported `.svg` (and `.png` if required) | Source files exist without corresponding exported renders |
| Template & syntax validity | PlantUML diagrams use valid syntax and appropriate C4/sequence/class/state templates | `plantuml -tsvg` or `drawio --export` fails with syntax or rendering errors |

## Document Versioning & PDF Parity

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Pre-operation inventory | `ls -1 *.md *.pdf \| sort` is checked and un-numbered `.md` files are classified first | Version bump proceeds with unclassified or broken version chains |
| Copy-first discipline | `REPORT-vN.md` is copied to `REPORT-v(N+1).md` before any edits are made | `REPORT-vN.md` is edited in-place or renamed without preserving `vN` |
| Header & link consistency | `v(N+1).md` updates title version, date, and `Previous version:` link to `vN` | `v(N+1).md` retains stale `vN` headers or broken `Previous version:` links |
| Markdown/PDF parity | Every versioned `.md` has a matching `.pdf` (`uniq -c \| awk '$1 != 2'` returns empty) | Any `.md` lacks a `.pdf` or an orphaned `.pdf` exists without `.md` |

## Scope Boundaries

- **Trigger**: Architecture diagram creation/export, diagram folder setup, or numbered `.md`/`.pdf` report version bumps.
- **Do not trigger**: Feature specification authoring (`driving-spec-development`) or Git/PR operations (`managing-github-workflows`).
