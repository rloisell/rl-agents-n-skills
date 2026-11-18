# APM Domain Refactor & Consolidation Plan (`rl-agents-n-skills`)

## Objective

Reorganize `rl-agents-n-skills` (currently 41 root skill directories + 24 root `agents/*.md` files) into a clean, APM-native multi-plugin repository under `plugins/<domain>/.apm/`, consolidating overlapping skills into fewer, logical gerund-named skills with rich `references/` directories, and producing root `AGENTS.md`, `CLAUDE.md` (<=5-line bridge), `architecture.md`, `install.md`, and `apm.yml`.

## Execution Strategy: Graph (DAG)

```mermaid
flowchart TD
    G0["approval_gate (Human Plan Approval)"]
    R1["analyze_cluster_workflow_dev (9 skills)"]
    R2["analyze_cluster_dotnet_app (7 skills)"]
    R3["analyze_cluster_devops_ocp (10 skills)"]
    R4["analyze_cluster_security_net (10 skills)"]
    R5["analyze_cluster_infra_sysadmin (5 skills)"]
    B1["barrier_domain_consolidation (Domain & Skill Map)"]
    M1["setup_worktree_and_scaffolds (Worktree + plugin skeletons)"]
    M2["build_domain_plugins (Subagents build consolidated skills & agents)"]
    M3["cutover_legacy_and_root_docs (Remove legacy dirs + AGENTS.md, architecture.md, install.md)"]
    V1["verify_apm_and_skills (Plugin, Skill, AGENTS.md, APM audits)"]

    G0 --> R1 & R2 & R3 & R4 & R5
    R1 & R2 & R3 & R4 & R5 --> B1
    B1 --> M1 --> M2 --> M3 --> V1
```

## Phase Breakdown

### Phase 1: Parallel Read-Only Domain & Skill Analysis (5 Research Subagents)
Each subagent reads its assigned `SKILL.md` files, sub-files, and corresponding `agents/*.md` files to catalog:
- Core capabilities, commands, scripts, and `<SKILL>_KNOWLEDGE` entries (preserving confidentiality rules).
- Overlap/duplication candidates where multiple small/related skills should merge into one cohesive skill with `references/`.
- Whether any `agents/*.md` truly requires subagent isolation (context isolation, tool sandboxing, or adversarial review) vs. being absorbed into a skill.

### Phase 2: Sync Barrier — Domain Taxonomy & Consolidation Design
Synthesize all 5 reports into:
1. **Organizational Domains** (`plugins/<domain>/`), e.g.:
   - `dev-workflow` (session/git/github/docs/diagrams/spec-driven dev/agent evolution)
   - `app-engineering` (.NET/EF Core/local-dev/REST API/BC Gov Design System/IAM/observability/data-flow)
   - `openshift-devops` (CI/CD, Emerald OCP, Containerfiles, resilience, migration, multi-app)
   - `security-and-networking` (AppSec/STRA, Vault, DB security, Zero Trust, network architecture, SDN/NetworkPolicy)
   - `systems-infrastructure` (Sysadmin, RHEL, Solaris, DNS, Cisco IOS)
   *(Exact domain boundaries will be finalized from Phase 1 evidence.)*
2. **Consolidated Skill Map**: Fewer, gerund-named skills (`<= 100` lines in `SKILL.md`, detailed guides/knowledge moved to `references/`).

### Phase 3: Isolated Worktree Build & Cutover
1. Create an isolated git worktree/branch (`.worktrees/apm-domain-refactor`).
2. Scaffold each domain plugin with `authoring-plugins` (`apm.yml`, `.claude-plugin/plugin.json`, `.apm/skills/`, `.apm/agents/`, `README.md`).
3. Dispatch domain-builder subagents to author the consolidated skills and retained subagents, preserving all generic knowledge and confidentiality rules.
4. Remove legacy root skill directories and root `agents/`, write root `apm.yml` collection manifest, `AGENTS.md`, `CLAUDE.md` (<=5-line bridge), `architecture.md`, `install.md` (modeled on `agent-plugins-skills/install.md`), and update `README.md`.

### Phase 4: Verification Gate
- `authoring-plugins`: `audit_plugin_structure.py` and `audit.py` on every `plugins/<domain>/`
- `authoring-skills`: `audit_skill.py --mode source` on every consolidated skill
- `authoring-instructions`: `audit_agents_md.py AGENTS.md --strict` and `CLAUDE.md` bridge check
- `packaging-with-apm`: `validate_apm_package.py` on every plugin and root `apm.yml`
