# CLAUDE.md — rl-agents-n-skills

Canonical governance baseline for all `rl-agents-n-skills` consumer projects.

All projects that mount this repo as a submodule (at `.github/agents/` or `.agents/`)
inherit these rules. Project-level `CLAUDE.md` files may add to these rules but must not
contradict them.

---

## Confidentiality and Privacy Rules

> **These rules are non-negotiable and apply to every AI agent, skill, and workflow
> in this repository, as well as any repo that mounts this repo as a submodule.**

### Rule 1 — No client or engagement details in public repos

**Unless a repository is explicitly private and access-restricted:**

- Do NOT include client organisation names, ministry names, or program area names as
  analysis subjects in skill files, CLAUDE.md, README files, or any other committed file.
- Do NOT include real OCP namespace IDs (e.g. `d7abee-dev`, `04d1a3-tools`) in examples,
  YAML snippets, or knowledge entries.
- Do NOT include real application names, GitHub repo paths, or workload names discovered
  during a client engagement.
- Do NOT include specific findings (RoleBinding counts, image names, NetworkPolicy names,
  route hostnames) that could identify a client's systems or security posture.
- Do NOT reference private analysis repos (e.g. `rloisell/FOI-analysis`) in public skill
  files.

**Use generic placeholders instead:**

| Real value | Replace with |
|---|---|
| `d7abee-dev` (real namespace ID) | `<ns-prefix>-dev` |
| `foi-requests` (real app name) | `<app-a>` or `<program-area>-frontend` |
| `rloisell/FOI-analysis` (private analysis repo) | omit, or use `<org>/<analysis-repo>` |
| `allow-from-d106d6-dev` (real NP name) | `allow-from-<source-ns>` |
| `[FOI-analysis]` in KNOWLEDGE entries | `[multi-app-engagement]` or `[engagement]` |

### Rule 2 — Knowledge entries must be generic lessons, not case reports

When `agent-evolution` appends KNOWLEDGE entries, entries must capture the **generalisable
pattern**, not the specific engagement finding.

✅ Good: `Cross-namespace NPs with no port/pod filtering are wide-open — always scope with podSelector + ports`
❌ Bad:  `[FOI-analysis] allow-from-d106d6-dev in d7abee-dev has no podSelector — remediate`

### Rule 3 — Analysis repos must be created as private

Any repo created to hold OCP CLI captures, analysis reports, or client-facing deliverables
**must be created as a private repository**. Use `gh repo create --private` or equivalent.
The `rl-project-template` scaffold instruction already includes `--private` — do not remove it.

### Rule 4 — AI sessions inherit these rules

When an AI agent is working on an analysis engagement, these rules apply to:
- Any GitHub PR, issue, or commit comment created in a public repo
- Any file added to a public repo as part of skill or toolkit extraction
- Any `agent-evolution` update that appends to KNOWLEDGE sections

If you are unsure whether information is client-specific, **omit it** and use a generic
description instead.

---

## Mid-Session Knowledge Capture

When a new reusable pattern, pitfall, or platform fact is discovered during a session:

1. Identify the correct SKILL.md (`<skill>/SKILL.md` in this repo)
2. Append to the `<SKILL>_KNOWLEDGE` section using the format:
   `- YYYY-MM-DD: [engagement-type] <imperative statement>`
3. Ensure the entry is generic (see Rule 2 above)
4. Raise a PR to this repo if the session is operating from a fork or submodule copy

---

## Universal Coding Standards

- Bash scripts: `set -euo pipefail`; use `local` for variables in functions
- Python: type hints on public functions; no bare `except:`
- YAML: 2-space indent; quote strings with special characters
- Markdown: ATX headings (`#`, `##`); fenced code blocks with language tag
- Secrets: never hardcode; use Vault, External Secrets Operator, or OCP Secrets
- Images: always pin to SHA in non-dev environments; never use `:latest` in production

---

## Subagent Registry

See `README.md` for the full agent list. Key orchestrating agents:

| Agent | When to invoke |
|---|---|
| `session-workflow` | Start and end of every development session |
| `bc-gov-foi-multi-app-orchestrator` | Analysing 2+ interconnected OCP apps in a program area |
| `ocp-resilience-analyst` | Per-namespace R01–R15 resilience posture |
| `ocp-migration-analyst` | Silver/Gold → Emerald migration gap analysis |
| `container-network-analyst` | Cross-namespace and cross-cluster network flow mapping |
| `security-architect` | STRA, RBAC audit, image provenance, OWASP |
| `agent-evolution` | End-of-session skill and KNOWLEDGE updates |
