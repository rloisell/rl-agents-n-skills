# GitHub Spec-Kit Guide

Spec-Driven Development using `specify-cli` (`github/spec-kit`).

## Contents

- [Installation](#installation) • [Project initialization](#project-initialization) • [Slash commands](#slash-commands) • [Directory structure](#directory-structure) • [Extensions and presets](#extensions-and-presets) • [Pre-merge checklist](#pre-merge-checklist) • [Knowledge](#knowledge)

## Installation

```bash
# Install specify-cli pinned to a stable release
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.7.4

# Verify and check environment
specify version
specify check

# Upgrade
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

## Project initialization

```bash
# Default: creates slash-command prompt files at .github/prompts/speckit.*
specify init --here --ai copilot

# Alternative: installs SKILL.md files for VS Code auto-discovery
specify init --here --ai copilot --ai-skills

# Commit initialization artifacts
git add .specify/ .github/prompts/
git commit -m "chore: initialise github spec-kit"
```

Add to `.gitignore`:

```text
__pycache__/
*.pyc
*.pyo
```

## Slash commands

### Core SDD workflow

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Create or update project governing principles — run once per project |
| `/speckit.specify` | Define what to build: requirements, user stories, acceptance criteria |
| `/speckit.plan` | Generate a technical implementation plan (tech stack + architecture) |
| `/speckit.tasks` | Break the plan into an actionable task list |
| `/speckit.implement` | Execute all tasks and build the feature |

### Optional enhancement commands

| Command | When to use |
|---------|-------------|
| `/speckit.clarify` | After `/speckit.specify` — surface underspecified areas before planning |
| `/speckit.analyze` | After `/speckit.tasks`, before `/speckit.implement` — cross-artifact consistency check |
| `/speckit.checklist` | Generate quality checklists for requirements completeness and clarity |
| `/speckit.optimize.run` | Audit constitution for token bloat, stale rules, and ambiguity |

## Directory structure

```text
.specify/
  templates/
    overrides/                # project-local template overrides
  extensions/                 # installed extensions
  presets/                    # installed presets
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

## Extensions and presets

```bash
# Discover and install extensions
specify extension search
specify extension add spec-kit-verify       # post-implementation quality gate
specify extension add spec-kit-cleanup      # scout-rule fixes + issue triage
specify extension add spec-kit-bugfix       # structured bug-to-spec trace workflow
specify extension add spec-kit-ci-guard     # spec compliance gates for CI/CD
specify extension add spec-kit-brownfield   # bootstrap spec-kit into existing codebases
specify extension add spec-kit-pr-bridge    # auto-generate PR descriptions from spec artifacts

# Discover and install presets (compliance formats, Agile terminology, test-first ordering)
specify preset search
specify preset add <preset-name>
```

## Pre-merge checklist

1. All tasks in `/speckit.tasks` output marked complete.
2. `/speckit.analyze` run with 0 consistency issues.
3. All acceptance criteria checked off in the spec.
4. Implementation aligns with the plan phase structure.
5. Unit tests passing.
6. Run `/speckit.verify` (via `spec-kit-verify` extension).

## Knowledge

- 2026-04-22: [agent-skills] "GitHub Spec-Kit" and "Microsoft Spec-Kit" refer to the same `specify` CLI (`github/spec-kit`, MIT).
- 2026-04-22: [agent-skills] `--ai copilot` creates `.github/prompts/speckit.*` slash-command files; `--ai copilot --ai-skills` creates `SKILL.md` files for auto-discovery instead.
