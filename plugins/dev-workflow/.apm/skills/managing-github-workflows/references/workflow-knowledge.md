# Workflow Knowledge

Causal discoveries and operational findings for GitHub workflows and rulesets.

- 2026-02-27: [sample-app] [CONTEXT: ci-cd] Ruleset status check context strings must exactly match the `name:` field in the workflow job, not the YAML job ID key.
- 2026-02-27: [sample-app] [CONTEXT: ci-cd] `gh pr merge --squash --delete-branch` keeps `main` history linear and automatically removes merged feature branches.
- 2026-02-27: [sample-app] [CONTEXT: config] GitHub Rulesets on the free plan require the repository to be public — private repositories silently ignore rulesets.
- 2026-02-28: [sample-app] [CONTEXT: ci-cd] A workflow `paths:` filter that only includes `src/**` blocks PRs touching `.github/` or config files from ever satisfying required status checks. Broaden `paths:` when workflow/config changes must trigger CI.
- 2026-04-22: [template] [CONTEXT: config] Branch protection rule "Changes must be made through a pull request" is bypassed silently by admin pushes — CAUSE: "Restrict who can bypass required pull requests" is unchecked in repo settings — FIX: Enable that restriction in GitHub Settings -> Rules.
