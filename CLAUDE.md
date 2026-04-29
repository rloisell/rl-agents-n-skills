# CLAUDE.md — ocp-migration-toolkit

This toolkit manages OpenShift migration analysis and reporting.

## Governance hierarchy

| File | AI tool | Authority |
|------|---------|-----------|
| `rl-agents-n-skills/CLAUDE.md` | Claude Code | **Canonical baseline** — all projects inherit these rules |
| `.github/copilot-instructions.md` | GitHub Copilot | Per-project Copilot rules and additions |
| `CLAUDE.md` (this file) | Claude Code | Toolkit-specific additions only |

## Canonical governance

Refer to [rl-agents-n-skills/CLAUDE.md](../../rl-agents-n-skills/CLAUDE.md) for 
universal coding standards, mid-session knowledge capture rules, and the 
complete subagent registry.

## Project context

- **Domain**: OpenShift 4 namespace discovery and gap analysis
- **Stack**: Multi-repo orchestrator (Bash/Python/yq)
- **Primary Subagent**: `ocp-migration-analyst`

## Toolkit rules

- Path context: Scripts often run against multiple local repo clones.
- Data integrity: JSON/YAML outputs must follow schema in `specs/`.
- Report generation: Use `jinja2` templates for markdown outputs.
