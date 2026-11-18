# dev-workflow Plugin

## Purpose
Software engineering lifecycle, GitHub workflows, spec-driven development, architecture documentation, and skill evolution.

## Plugin Components

### Skills

| Skill | Description |
|-------|-------------|
| `managing-dev-sessions` | Startup/shutdown discipline, orientation files, git checks, Dependabot triage, and `AI/` audit trail schemas |
| `managing-github-workflows` | Branch-first PR workflow, conventional commits, GitHub Rulesets, CI failure diagnosis, and OCIO §2.1 & OSS compliance |
| `driving-spec-development` | Spec-Driven Development with GitHub Spec-Kit (`specify`) and Spec-Kitty (`spec-kitty`), plus OCIO §1 Requirements Management alignment |
| `documenting-architecture` | Unified 10-diagram architecture suite (draw.io, PlantUML, Mermaid) and copy-first document versioning with PDF parity |
| `evolving-agent-skills` | Pre-session knowledge recall, causal `CAUSE`/`FIX` knowledge capture, shared-skill promotion, and evolution log maintenance |

### Sub-Agents

| Sub-Agent | Purpose | Preloaded Skills |
|-----------|---------|------------------|
| `agent-evolution` | Isolated session-end scanner for `AI/` logs and `SKILL.md` knowledge updates | `evolving-agent-skills` |

### Hooks
None.

## Directory Structure

```text
dev-workflow/
├── .apm/
│   ├── agents/
│   │   └── agent-evolution.md
│   └── skills/
│       ├── documenting-architecture/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── driving-spec-development/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── evolving-agent-skills/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── managing-dev-sessions/
│       │   ├── SKILL.md
│       │   └── references/
│       └── managing-github-workflows/
│           ├── SKILL.md
│           └── references/
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
└── README.md
```
