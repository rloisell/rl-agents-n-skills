# Rulesets, CI Diagnosis, and BC Gov Standards

## Contents

- [Branch protection model](#branch-protection-model) • [Ruleset management](#ruleset-management-gh-cli) • [Common CI failure patterns](#common-ci-failure-patterns) • [Dependabot PR review order](#dependabot-pr-review-order) • [Authoritative BC Government standards](#authoritative-bc-government-standards)

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

## Authoritative BC Government standards

These OCIO standards apply to BC Government project repositories on `github.com/bcgov`:

| Standard | Mandate |
|----------|---------|
| [Development Standards for Information Systems and Services v3.0 (May 2015), §2.1](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/development_standards_for_information_systems_and_services.pdf) | (1) Open Source projects MUST use `github.com`; (2) MUST reside within the **BCGov** organization; (3) MUST be approved by the appropriate Deputy Minister or designate; (4) MUST adhere to the Content Approval Checklist; (5) Project components MUST consist only of Open Repositories; (6) All activity MUST follow the BC Open Source Development Policy; (7) **Repository Administrators MUST use 2-factor authentication**; (8) All repository content MUST apply an approved license; (9) Content SHOULD apply one or more pre-approved default licenses (Apache 2.0, MIT, OGL-BC). |
| [Guidelines on the Use of Open Source Software (R1.0, Apr 2012)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/guidelines_on_the_use_of_open_source_software_2016.pdf) | Adoption of OSS dependencies follows business value, TCO, and risk assessment. |

When opening or reviewing a BCGov-organization PR, verify: license file
present, repository is public, 2FA enforced on org membership, and branch
protection rules align with the project's ruleset definition.
