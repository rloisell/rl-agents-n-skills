---
name: spec-kit
description: Drives spec-first feature development using GitHub Spec-Kit (specify-cli) — enforces constitution → specify → plan → tasks → implement workflow, manages extensions and presets, and applies the Spec-Driven Development lifecycle. Use when starting a new feature, writing spec or plan files, breaking work into tasks, or installing extensions/presets.
tools: Bash, Read, Write, Grep, Glob
user-invocable: false
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Requires specify-cli from github/spec-kit. Supports --ai copilot (prompt files) or --ai copilot --ai-skills (SKILL.md). See https://github.com/github/spec-kit
---

# GitHub Spec-Kit Agent

Enforces Spec-Driven Development: constitution → specify → plan → tasks → implement.
No implementation code before spec, plan, and tasks exist.

**This is the generic template version.** Project-specific feature tables and spec IDs
live in the project's own `spec-kit.agent.md` or `.specify/` configuration.

---

## Core Rule

**Follow the SDD workflow in order. No skipping phases.**

```
constitution  →  specify  →  (clarify)  →  plan  →  (analyze)  →  tasks  →  implement
```

---

## Installation

```bash
# Install specify-cli (pin to a stable release — check https://github.com/github/spec-kit/releases)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.7.4

# Verify
specify version
specify check

# Upgrade
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

---

## Project Initialisation

```bash
# Default: creates slash-command prompt files at .github/prompts/speckit.*
specify init --here --ai copilot

# Alternative: installs SKILL.md files for VS Code auto-discovery
specify init --here --ai copilot --ai-skills

# Commit initialisation artifacts
git add .specify/ .github/prompts/
git commit -m "chore: initialise github spec-kit"
```

Add to `.gitignore`:
```
__pycache__/
*.pyc
*.pyo
```

---

## Core Slash Commands (SDD Workflow)

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Create or update project governing principles and dev guidelines — **run once per project** |
| `/speckit.specify` | Define what to build: requirements, user stories, acceptance criteria |
| `/speckit.plan` | Generate a technical implementation plan (provide tech stack and architecture choices) |
| `/speckit.tasks` | Break the plan into an actionable task list |
| `/speckit.implement` | Execute all tasks and build the feature |

---

## Optional Enhancement Commands

| Command | When to use |
|---------|-------------|
| `/speckit.clarify` | After `/speckit.specify` — surfaces underspecified areas before planning |
| `/speckit.analyze` | After `/speckit.tasks`, before `/speckit.implement` — cross-artifact consistency check |
| `/speckit.checklist` | Generate custom quality checklists for requirements completeness and clarity |

---

## Typical Feature Workflow

```
1.  /speckit.constitution   ← once per project
2.  /speckit.specify        ← describe the feature (what + why, not the tech)
3.  /speckit.clarify        ← (recommended) surface gaps
4.  /speckit.plan           ← provide tech stack and architectural constraints
5.  /speckit.analyze        ← verify consistency before task generation
6.  /speckit.tasks          ← generate task list
7.  /speckit.implement      ← build it
```

---

## Directory Structure (post-init)

```
.specify/                     ← specify-cli config and templates
  templates/
    overrides/                ← project-local template overrides
  extensions/                 ← installed extensions
  presets/                    ← installed presets
.github/
  prompts/
    speckit.constitution.prompt.md
    speckit.specify.prompt.md
    speckit.plan.prompt.md
    speckit.tasks.prompt.md
    speckit.implement.prompt.md
    speckit.clarify.prompt.md
    speckit.analyze.prompt.md
    speckit.checklist.prompt.md
```

---

## Extensions

Extensions add new commands or workflow phases:

```bash
# Discover
specify extension search

# Install
specify extension add <extension-name>

# Examples of useful extensions
specify extension add spec-kit-verify       # post-implementation quality gate
specify extension add spec-kit-cleanup      # scout-rule fixes + issue triage
specify extension add spec-kit-bugfix       # structured bug-to-spec trace workflow
specify extension add spec-kit-ci-guard     # spec compliance gates for CI/CD
specify extension add spec-kit-brownfield   # bootstrap spec-kit into existing codebases
specify extension add spec-kit-pr-bridge-   # auto-generate PR descriptions from spec artifacts
```

See the full catalog at: https://github.com/github/spec-kit/blob/main/extensions/catalog.community.json

---

## Presets

Presets customise how spec-kit behaves without adding new commands:

```bash
# Discover
specify preset search

# Install
specify preset add <preset-name>
```

Use presets to enforce BC Gov compliance formats, apply Agile terminology, or
mandate test-first task ordering.

---

## Pre-Merge Checklist

1. All tasks in `/speckit.tasks` output marked complete
2. `/speckit.analyze` run — 0 consistency issues
3. All acceptance criteria checked off in spec
4. Implementation aligns with the plan phase structure
5. Unit tests passing
6. Run `specify extension add spec-kit-verify` if not already installed, then `/speckit.verify`

---

## Files to Commit

```bash
git add .specify/ .github/prompts/
# .gitignore must include: __pycache__/ *.pyc *.pyo
```

---

## Spec-Kitty vs Spec-Kit Quick Reference

Both tools implement Spec-Driven Development. Choose based on team/project preference:

| Aspect | Spec-Kitty (`spec-kitty` CLI) | GitHub Spec-Kit (`specify` CLI) |
|--------|-------------------------------|----------------------------------|
| Install | `pip install spec-kitty` | `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` |
| Config dir | `.kittify/` | `.specify/` |
| Feature dir | `kitty-specs/{NNN}-{slug}/` | Flexible — specify creates files in project root or designated folder |
| Task format | `WP{NN}-title.md` with YAML frontmatter | tasks.md list (AI-generated from `/speckit.tasks`) |
| Lane tracking | `planned → in-progress → review → done` | Phase-based (no formal lanes) |
| Validation | `spec-kitty validate-tasks --all` | `/speckit.analyze` + `spec-kit-verify` extension |
| Extensions | Not supported | 40+ community extensions |
| Presets | Not supported | Multiple community presets |
| Agent support | CLI prompt files | 30+ AI agent integrations |
| Stars | Custom/private | 90k+ (github/spec-kit) |

---

## SPEC_KIT_KNOWLEDGE

> Append new spec-kit discoveries here.
> Format: `YYYY-MM-DD: [project] <discovery>`

- 2026-04-22: [rl-agents-n-skills] GitHub Spec-Kit (`github/spec-kit`) is sometimes referred to as "Microsoft Spec-Kit" in community docs and MCP bridge projects — it is a GitHub-owned open-source project, MIT licensed.
- 2026-04-22: [rl-agents-n-skills] `--ai copilot` creates `.github/prompts/speckit.*` files (slash commands for Copilot Chat). `--ai copilot --ai-skills` creates SKILL.md files for VS Code auto-discovery instead.
