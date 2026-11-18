# Git Conventions

Branch naming, commit message formatting, and conventional commit types across
all project repositories.

## Branch Naming

Format: `<type>/<short-slug>` (lowercase, hyphen-separated, <= 40 characters).

| Type | Use for | Example |
|------|---------|---------|
| `feat` | New user-facing feature | `feat/network-test-crud` |
| `fix` | Bug fix | `fix/build-target` |
| `chore` | Maintenance, tooling, config, dependency updates | `chore/diagram-folder-structure` |
| `docs` | Documentation only | `docs/deployment-analysis` |
| `refactor` | Restructuring without behavior change | `refactor/service-layer-split` |
| `test` | Test additions or corrections | `test/network-test-integration` |

## Commit Message Format

```text
<type>: <short imperative description (<= 72 chars)>

- detail line 1 (what changed and why)
- detail line 2
```

### Subject line rules

- Use imperative mood: `add`, `fix`, `remove` (not `added`, `fixes`, `removing`).
- Omit trailing period.
- Keep under 72 characters.

### Body rules

Include a body whenever the change is non-obvious:

- Separate subject and body with a blank line.
- Start each bullet with `- `.
- Explain *why*, not only *what*.

### Examples

```text
feat: add NetworkTest CRUD endpoints

- Created NetworkTest entity with MariaDB mapping
- Added CreateNetworkTestRequest / UpdateNetworkTestRequest DTOs
- Registered INetworkTestService in DI
```

```text
chore: update agent skill structure

- Consolidated workflow skills under dev-workflow plugin
- Extracted reference guides into references/ subdirectories
```
