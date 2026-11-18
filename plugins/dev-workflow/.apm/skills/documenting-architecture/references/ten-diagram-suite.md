# Ten-Diagram Standard Suite

Unified 10-diagram architecture suite reconciling C4-first PlantUML and
draw.io/UML conventions into a single canonical layout.

## Contents

- [Standard folder structure](#standard-folder-structure) • [Canonical 10-diagram suite](#canonical-10-diagram-suite) • [VS Code extensions and config](#vs-code-extensions-and-config) • [CLI export commands](#cli-export-commands) • [Knowledge](#knowledge)

## Standard folder structure

```text
diagrams/
  drawio/
    <name>.drawio              # source
    svg/<name>.svg             # exported SVG (committed)
  plantuml/
    <name>.puml                # source
    svg/<name>.svg             # exported SVG (committed)
    png/<name>.png             # exported PNG (committed when needed)
  data-model/
    <name>.drawio              # ERD / physical schema source
    svg/<name>.svg
    png/<name>.png

docs/
  architecture.md              # inline Mermaid diagrams (e.g., folder structure)
```

## Canonical 10-diagram suite

Every production-ready project maintains these 10 views. Where a project prefers
C4-PlantUML over draw.io for architectural context, use the PlantUML C4 column;
both map 1:1 to the same architectural viewpoints.

| # | Viewpoint | Primary Tool & Path | C4 / Text-Diffable Alternative |
|---|-----------|---------------------|--------------------------------|
| 1 | System Context / Architecture | `drawio/system-architecture.drawio` | `plantuml/c4-context.puml` |
| 2 | Container / Package Structure | `plantuml/package-structure.puml` | `plantuml/c4-container.puml` |
| 3 | Component / Domain Class Model | `plantuml/class-model.puml` | `plantuml/c4-component.puml` |
| 4 | Use Case / Capability Overview | `plantuml/use-cases.puml` | `docs/architecture.md` (Mermaid) |
| 5 | Sequence — Auth & Key Flows | `plantuml/seq-auth.puml` | `plantuml/<feature>-sequence.puml` |
| 6 | Sequence / Activity — Main Flow | `plantuml/seq-main-flow.puml` | `plantuml/<feature>-workflow.puml` |
| 7 | Entity Lifecycle / State Machine | `plantuml/<entity>-state.puml` | `plantuml/state-machine.puml` |
| 8 | Entity-Relationship Diagram | `data-model/erd.drawio` | `plantuml/er-model.puml` |
| 9 | Physical Database Schema | `data-model/physical-schema.drawio` | `data-model/<db>-schema.drawio` |
| 10 | Deployment & Network Topology | `drawio/deployment-topology.drawio` | `drawio/network-topology.drawio` + Mermaid |

Never remove the 10 base viewpoints. Add feature-specific diagrams alongside them.

## VS Code extensions and config

```bash
code --install-extension hediet.vscode-drawio       # draw.io native editing
code --install-extension jebbs.plantuml             # PlantUML preview
code --install-extension bierner.markdown-mermaid   # Mermaid preview
```

`.vscode/settings.json`:

```json
{
  "plantuml.render": "PlantUMLServer",
  "plantuml.server": "https://www.plantuml.com/plantuml",
  "plantuml.exportFormat": "svg",
  "plantuml.exportOutDir": "diagrams/plantuml/svg"
}
```

## CLI export commands

### draw.io CLI

```bash
# Single file
drawio --export --format svg --embed-diagram --border 10 \
  --output diagrams/drawio/svg/<name>.svg diagrams/drawio/<name>.drawio

# Batch export
find diagrams/drawio -name "*.drawio" -not -path "*/svg/*" | while read f; do
  name=$(basename "$f" .drawio)
  drawio --export --format svg --embed-diagram --border 10 \
    --output "diagrams/drawio/svg/${name}.svg" "$f"
done
```

### PlantUML CLI

```bash
# Single file (SVG preferred; use -tpng if PNG is required)
plantuml -tsvg -o diagrams/plantuml/svg diagrams/plantuml/<name>.puml

# Batch export
plantuml -tsvg diagrams/plantuml/*.puml -o ../svg/
plantuml -tpng diagrams/plantuml/*.puml -o ../png/
```

## Knowledge

- 2026-02-27: [template] [CONTEXT: toolchain] draw.io `.drawio` files are XML and diff cleanly in git. Prefer SVG exports for docs; add PNG only where SVG is unsupported.
- 2026-02-27: [template] [CONTEXT: toolchain] PlantUML server rendering works without local Java for day-to-day preview; use local PlantUML CLI for batch export at commit time.
