# Skill Structure Standard

All skills in `rl-agents-n-skills` follow the [Agent Skills Open Standard](https://agentskills.io/specification.md) and the `authoring-skills` contract inside the APM-native plugin layout (`plugins/<domain>/.apm/skills/<skill-name>/`).

## Directory Layout

```text
plugins/<domain>/.apm/skills/<gerund-skill-name>/
├── SKILL.md           # Required: <= 100 lines; YAML frontmatter + lean router
├── references/        # Optional: deep guides, schemas, and KNOWLEDGE logs
├── assets/
│   └── templates/     # Optional: standalone templates (.j2, .yaml, .puml, .mmd, .drawio, Containerfile)
├── scripts/           # Optional: executable helper/validation scripts
└── evals/             # Recommended: evals/evals.json routing & quality checks
```

- **Self-contained**: All `references/`, `assets/`, and `scripts/` live inside the skill that uses them; never embed standalone file templates inside `references/` or share files across skills via relative `../` links.
- **Naming**: Use gerund names (`managing-*`, `building-*`, `deploying-*`, `securing-*`, `auditing-*`). Directory name must equal frontmatter `name` (`^[a-z0-9-]+$`).

## `SKILL.md` Contract

1. **Frontmatter**: `name` and third-person `description` stating what the skill does and when to use it.
2. **Line budget**: `<= 100` lines; move deep material to `references/` and templates to `assets/templates/`.
3. **Canonical sections** (per `authoring-skills`):
   - `## Contents` — local navigation links
   - `## Constraints` — non-negotiable rules (`MUST` / `NEVER`)
   - `## Quick start` (or `## Modes`) — primary commands or mode table
   - `## Workflow` — ordered execution steps
   - `## Verification` — deterministic checks / validation commands
   - `## References` — links to `references/*.md` and `assets/templates/*`
4. **Long references**: Any `references/*.md` over ~100 lines should open with a `## Contents` list.

## Validation

Validate every skill against the `authoring-skills` contract before merging:

```bash
python <path-to-authoring-skills>/scripts/audit_skill.py plugins/<domain>/.apm/skills/<skill-name> --mode source
```
