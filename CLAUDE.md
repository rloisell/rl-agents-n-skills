# CLAUDE.md — rl-agents-n-skills

This file provides base instructions for Claude Code when working in a project
that uses the **rl-agents-n-skills** plugin.

## Project context

You are working on a BC Government .NET/React/OpenShift project owned by
**Ryan Loiselle** (Developer / Architect). GitHub Copilot / Claude Code acts as
AI pair programmer.

## Always

- Add file header to every new file (see CODING_STANDARDS.md)
- Add per-method purpose comment above every method
- Add ALL-CAPS section labels between logical groups in classes
- Add `} // end ClassName` at end of every class
- Follow the service-layer pattern — no business logic in controllers
- Update `AI/WORKLOG.md`, `AI/CHANGES.csv`, `AI/COMMANDS.sh` at session end

## Mid-session knowledge capture

When any of these events occur **during a session**, record the finding immediately
— do not defer to session end:

- A non-obvious bug fix required diagnosis (root cause identified)
- A platform quirk or undocumented behaviour was discovered
- A workaround for a toolchain limitation was found
- A previously failing approach is confirmed to not work

Mark the candidate inline with `<!-- evolution-candidate -->` immediately after
the relevant code change or command, then include it verbatim in the end-of-session
agent-evolution invocation. Do not rely on end-of-session memory to reconstruct it.

## Never

- Add academic metadata (student IDs, course names)
- Make architectural decisions without direction from Ryan Loiselle
- Remove or rewrite existing comments unless asked
- Leave debug `console.log` / `Console.WriteLine` in committed code
- Use `EnsureCreated()` in startup — always `db.Database.Migrate()`
- Commit secrets or build output
- Bake `VITE_API_URL` at build time — serve `/config.json` from Nginx instead

## Code style

- C#: `var` for locals; expression-body (`=>`) for single-return members; primary constructors
- JS/JSX: `const`/arrow functions; named exports
- Match indentation and naming conventions already present in the file

## Available subagents

The following subagents are available from the rl-agents-n-skills plugin.
Delegate to them when the task matches their domain:

| Subagent | When to use |
|----------|-------------|
| `security-architect` | Security reviews, OWASP, Vault, STRA/PIA |
| `bc-gov-devops` | Helm, OpenShift, Artifactory, ArgoCD |
| `bc-gov-iam` | OIDC PKCE, Keycloak, oidc-client-ts |
| `session-workflow` | Session start/end, AI file updates |
| `github-workflow` | Branches, PRs, CI diagnosis |
| `diagram-generation` | draw.io, PlantUML, Mermaid |
| `ci-cd-pipeline` | GitHub Actions, Trivy, yq GitOps |
| `spec-kitty` | Spec-first WP workflow |
| `ef-core` | EF Core, MariaDB/Pomelo, migrations |
| `observability` | Serilog, health checks, Prometheus |
| `local-dev` | podman-compose, local troubleshooting |
| `agent-evolution` | **Always invoke at session end** after COMMIT_INFO is written — updates KNOWLEDGE sections, promotes shared skills, logs discoveries |
| `zero-trust-architect` | ZTA design, SASE architecture, ZTNA/CASB/SWG evaluation |
| `network-architect` | Routing/switching design, WAN, BGP/OSPF, topology review |
| `cisco-ios` | Cisco IOS/IOS-XE/NX-OS config, home lab, troubleshooting, password recovery |
| `sysadmin` | *nix admin tasks, Solaris 9/10/11 SPARC (LDoms), RHEL, storage, boot issues |
| `bc-gov-network-architect` | BC Gov workload connectivity, NetworkPolicy authoring, SDN zone classification, cross-zone failure diagnosis |
| `ocp-migration-analyst` | Full OCP migration analysis pipeline — namespace discovery, gap analysis, network mapping, report generation |
| `ocp-resilience-analyst` | OpenShift namespace resilience posture — R01–R15 grading, PDB/HPA/replica analysis, prioritised remediation |

## Deployment platform

BC Government Emerald OpenShift 4.x. See `docs/deployment/` for platform details.
Key rules: port 8080, non-root, DataClass Medium label, AVI `dataclass-medium`
annotation, double NetworkPolicy (egress sender + ingress receiver).

## Branch & PR workflow

```
main is always protected. Every change goes through a PR.

git checkout -b feat/my-feature
git commit -m "feat: description\n\n- detail"
git push origin feat/my-feature
gh pr create --title "feat: description" --base main
gh pr merge <number> --squash --delete-branch
```
