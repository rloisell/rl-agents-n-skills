# CLAUDE.md — ocp-resilience-toolkit

This toolkit analyzes and grades OpenShift namespace resilience (R01–R15).

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

- **Domain**: OpenShift resilience posture and prioritised remediation
- **Stack**: Multi-repo orchestrator (Bash/Python/yq)
- **Primary Subagent**: `ocp-resilience-analyst`

## Toolkit rules

- Resilience Scoring: Always include R-code (e.g., R07) in remediation advice.
- PDB Analysis: Check for 0-budget PDBs as high-priority failures.
- HPA/VPA: Verify that replicas > 1 for all production-labeled workloads.
