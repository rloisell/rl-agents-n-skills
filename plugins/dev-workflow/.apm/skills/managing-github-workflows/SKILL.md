---
name: managing-github-workflows
description: >-
  Manages the branch-first, PR-required GitHub workflow, including branch
  naming, conventional commit formatting, gh CLI PR lifecycle, GitHub Rulesets,
  CI failure diagnosis, Dependabot triage, and BC Gov OCIO repository standards.
  Use when creating branches, writing commits, opening or merging PRs,
  configuring rulesets, or troubleshooting CI checks.
---

# Managing GitHub Workflows

Enforces a branch-first, pull-request-required GitHub workflow with conventional
commits, ruleset-enforced status checks, and clean squash merges.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **No direct commits to `main`**: all changes go through feature branches and PRs.
2. **Conventional branch and commit format**: use `<type>/<short-slug>` (<= 40 chars) and `<type>: <imperative description>` (<= 72 chars) per [git-conventions.md](references/git-conventions.md).
3. **Exact job `name:` matching**: GitHub Rulesets match the workflow job's `name:` field, not the YAML job ID key.
4. **Squash merge and delete branch**: use `gh pr merge <number> --squash --delete-branch` once required checks pass.
5. **BC Gov compliance**: repositories under public-sector Open Source organizations must satisfy OCIO §2.1 and OSS guidelines in [rulesets-and-ci.md](references/rulesets-and-ci.md).

## Quick start

Create a feature branch, commit with a conventional message, open a PR with `gh pr create`, and squash-merge once required checks pass.

## Workflow

### Standard PR lifecycle

```bash
# 1. Create feature branch from updated main
git checkout -b feat/my-feature

# 2. Commit with conventional format
git add -A
git commit -m "feat: add my feature" -m "- added X" -m "- updated Y"

# 3. Push and open PR
git push -u origin feat/my-feature
gh pr create --title "feat: add my feature" --body "## Summary\n- Added X" --base main

# 4. Watch CI checks and squash-merge
gh pr checks <number> --watch
gh pr merge <number> --squash --delete-branch
git checkout main && git pull origin main
```

### CI failure diagnosis

```bash
# Fetch latest failed run and inspect failed step logs
RUN_ID=$(gh run list --workflow build-and-test.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view "$RUN_ID" --log-failed 2>&1 | tail -50
```

See [rulesets-and-ci.md](references/rulesets-and-ci.md) for CI failure patterns, ruleset API commands, and Dependabot ordering.

## Verification

Confirm the PR has all required status checks green, no merge conflicts, and
that `main` is fast-forwarded after squash merge:

```bash
gh pr checks <number>
git status --short
```

## References

- [Git Conventions](references/git-conventions.md) — branch naming, commit types, and message examples
- [Rulesets, CI, and BC Gov Standards](references/rulesets-and-ci.md) — ruleset CLI management, failure diagnosis, Dependabot order, and OCIO §2.1 & OSS compliance
- [SAST & Release CI](references/sast-and-release-ci.md) — Gitleaks + SonarQube SAST, Release Please semantic releases, and DinD + Buildx + Trivy container scanning
- [Workflow Knowledge](references/workflow-knowledge.md) — accumulated GitHub Actions and ruleset findings
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for PR lifecycle, rulesets, and CI diagnosis
