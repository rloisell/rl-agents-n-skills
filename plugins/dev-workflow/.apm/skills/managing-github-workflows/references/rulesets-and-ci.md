# Rulesets, CI Diagnosis, and BC Gov Standards

## Contents

- [Branch protection model](#branch-protection-model) • [Ruleset management](#ruleset-management-gh-cli) • [Common CI failure patterns](#common-ci-failure-patterns) • [Dependabot PR review order](#dependabot-pr-review-order) • [Runtime, framework, and dependency update discipline](#runtime-framework-and-dependency-update-discipline) • [Evidence-based PR review method](#evidence-based-pr-review-method) • [Authoritative BC Government standards](#authoritative-bc-government-standards)

## Branch protection model

All `main` branches use GitHub **Rulesets** (rather than classic branch
protection) with these standard rules:

- No deletion or force-push to `main`
- Pull requests required before merging
- All registered status checks must pass before merge
- Restrict bypass actors so admins cannot silently bypass PR requirements

### Status check context names

The `name:` field in each workflow job must **exactly match** the ruleset status
check context string. The YAML job ID key is ignored by rulesets.

| Workflow | Job ID | `name:` field = required context |
|----------|--------|----------------------------------|
| `build-and-test.yml` | `test-api` | `.NET Build & Test` |
| `build-and-test.yml` | `frontend-build` | `Frontend Build & Test` |

## Ruleset management (`gh` CLI)

```bash
# List rulesets
gh api repos/<owner>/<repo>/rulesets | jq '.[] | {id, name, enforcement}'

# Create ruleset
gh api repos/<owner>/<repo>/rulesets --method POST --input ruleset.json

# Update ruleset
gh api repos/<owner>/<repo>/rulesets/<id> --method PUT --input updated.json

# Check and update repo visibility (free-plan rulesets require public repos)
gh repo view <owner>/<repo> --json visibility
gh repo edit <owner>/<repo> --visibility public
```

## Common CI failure patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Status check required but never posted | Job `name:` differs from ruleset context | Match `name:` in workflow YAML to ruleset string exactly |
| PR blocked, no checks posted | Workflow `paths:` filter excludes changed files | Broaden `paths:` to include changed config/doc paths |
| `npm ci` fails | `package-lock.json` not committed | Run `npm install` locally and commit lock file |
| `dotnet test` fails | Missing test DB or unapplied migration | Use test DB container or configured test fixture |
| Ruleset not enforcing | Private repo on free GitHub plan | Make repo public or upgrade plan |

## Dependabot PR review order

1. GitHub Actions version bumps (lowest risk; merge first)
2. NuGet minor/patch updates (review changelog; merge after CI passes)
3. npm minor/patch updates (audit locally; merge after CI passes)
4. Major version bumps (require manual verification)

## Runtime, framework, and dependency update discipline

- **Runtime/framework vs library split**: classify updates by component role (language runtime, SDK, or primary application framework vs third-party library/plugin/dev tool), not by semver bump size—a patch or minor SDK update is still a framework update.
- **Coherent framework batching**: batch runtime, SDK, and primary framework updates together across manifests, `global.json`/toolchain pins, `Containerfile`/`Dockerfile` `FROM` base images, and CI workflow runner/SDK steps after verifying official vendor support lifecycles and EOL dates (never infer support from a package manager's `latest` column).
- **Deprecation and abandonment checks**: for third-party libraries, inspect registry/maintainer deprecation notices and the date of the most recent published release. Flag a library as deprecated when marked so, and as potentially abandoned when no release has been published for `>= 1 year` as of the check date (report `Unknown` if unverifiable; do not silently upgrade to another deprecated or abandoned release).
- **Pinned lockfile and wrapper regeneration**: regenerate lockfiles using the repository's pinned package manager or wrapper (`mvnw`/`gradlew`, `dotnet restore --locked-mode`, `npm ci`/committed `package-lock.json`, `composer.lock`). Avoid force flags or bulk `--audit fix` commands that cross component scope.
- **Safe component-scoped rollback**: in unattended/automated runs, capture exact pre-update file contents before editing; if build or test verification fails, restore only that component's changed files and verify the restore rather than running a broad `git reset` or discarding unrelated work.

## Evidence-based PR review method

- **GitHub PR pagination check**: fetch `repos/<owner>/<repo>/pulls/<number>/files?per_page=100` (paginated) and cross-check the total returned file count against `changedFiles` (the files API caps at 3,000 files). Treat missing patches or truncated diffs as explicit coverage gaps rather than claiming full coverage.
- **Head-SHA comparison on re-reviews**: inspect prior reviews and commits since the last approved head SHA; never treat a new commit as automatically dismissing an earlier finding, and re-verify the current head SHA before citing file lines.
- **Merge-base diff and steelman filtering**: compare against the merge base (`git diff <base>...<head>`), not a moving target branch tip. For each candidate finding, state the strongest plausible defense of the author's choice (steelman), verify the actual failing path in source, and discard pre-existing, stylistic, speculative, or CI-detectable issues.
- **Structured deliberate-debt marker**: track intentional, bounded shortcuts in source comments using:
  `# crow-debt: shortcut; <what>; ceiling: <limit>; revisit: <trigger>; owner: <team>`
  Flag entries as `no-trigger` when `revisit:` is absent, or `incomplete` when `ceiling:` or `owner:` is missing.

## Authoritative BC Government standards

These OCIO standards apply to BC Government project repositories on `github.com/bcgov`:

| Standard | Mandate |
|----------|---------|
| [Development Standards for Information Systems and Services v3.0 (May 2015), §2.1](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/development_standards_for_information_systems_and_services.pdf) | (1) Open Source projects MUST use `github.com`; (2) MUST reside within the **BCGov** organization; (3) MUST be approved by the appropriate Deputy Minister or designate; (4) MUST adhere to the Content Approval Checklist; (5) Project components MUST consist only of Open Repositories; (6) All activity MUST follow the BC Open Source Development Policy; (7) **Repository Administrators MUST use 2-factor authentication**; (8) All repository content MUST apply an approved license; (9) Content SHOULD apply one or more pre-approved default licenses (Apache 2.0, MIT, OGL-BC). |
| [Guidelines on the Use of Open Source Software (R1.0, Apr 2012)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/guidelines_on_the_use_of_open_source_software_2016.pdf) | Adoption of OSS dependencies follows business value, TCO, and risk assessment. |

When opening or reviewing a BCGov-organization PR, verify: license file
present, repository is public, 2FA enforced on org membership, and branch
protection rules align with the project's ruleset definition.
