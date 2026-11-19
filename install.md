# Repository Installation & Lifecycle

This document defines how to install, update, select, and remove the domain plugins and skills in `rl-agents-n-skills`.

Plugins are installed with [APM](https://github.com/microsoft/apm) (Agent Package Manager). APM copies each plugin's skills and agents into the target agent harness folders, maintains a manifest and lockfile, and handles updates and uninstalls.

Each domain plugin keeps its skills and agents in `plugins/<domain>/.apm/` alongside `plugins/<domain>/apm.yml`. Everything APM installs is committed to git, so there is no build or copy step: install directly from GitHub or clone the repository and run `apm install`. This works the same on Windows, macOS, and Linux.

## Available Domain Plugins

| Plugin | Path | Scope |
|---|---|---|
| `dev-workflow` | `plugins/dev-workflow` | Session management, GitHub workflows, spec-driven dev, diagrams/versioning, skill evolution |
| `app-engineering` | `plugins/app-engineering` | .NET 10 / EF Core / REST APIs, BC Gov Design System, DIAM/OIDC IAM, observability, local dev |
| `openshift-devops` | `plugins/openshift-devops` | Emerald OpenShift, Option 2 CI/CD, migration & resilience analysis, CI/CD governance |
| `security-and-networking` | `plugins/security-and-networking` | AppSec, Vault, DB security, data lineage/STRA/PIA, Zero Trust, enterprise & OCP networking |
| `systems-infrastructure` | `plugins/systems-infrastructure` | Unix/RHEL/Solaris administration, DNS diagnostics, Cisco IOS/NX-OS networking |

- **Dependencies:** None of the five plugins declare external APM dependencies; they can be installed together or independently.
- **One scope only:** If a plugin is installed globally (`~/.apm/apm.yml`), do not also list it in a project's `apm.yml`, or it will be installed twice. Check existing global installs first:

```bash
apm deps list --global
```

---

## Option 1: APM Package (Recommended)

### 1. Install APM

Use APM 0.35.0 or newer (`agy` / Antigravity target requires it).

On Windows (PowerShell):

```powershell
irm https://aka.ms/apm-windows | iex
```

On macOS / Linux:

```bash
curl -sSL https://aka.ms/apm-unix | sh -s -- @v0.35.0
```

Verify:

```bash
apm --version
```

### 2. Install directly from GitHub or get a pinned clone

Install all five plugins from the repository's root collection manifest:

```bash
apm install https://github.com/rloisell/rl-agents-n-skills --global --target claude,copilot,codex,agy
```

Run from a consuming project's root and omit `--global` for a project-local installation:

```bash
apm install https://github.com/rloisell/rl-agents-n-skills --target codex,copilot
```

Select a single domain plugin with APM's `owner/repo/subdirectory` shorthand:

```bash
apm install rloisell/rl-agents-n-skills/plugins/openshift-devops --global --target claude,copilot,codex,agy
```

For reproducible installs, append an existing tag or commit SHA:

```bash
apm install "https://github.com/rloisell/rl-agents-n-skills#<tag-or-commit>" --global --target claude,copilot,codex,agy
apm install "rloisell/rl-agents-n-skills/plugins/app-engineering#<tag-or-commit>" --global --target codex,copilot
```

Use a comma-separated `--target` list. Other supported targets include `gemini`, `cursor`, `opencode`, and `windsurf` (see `apm install --help`). On Windows, add `--parallel-downloads 0`.

#### Clone-based alternative

```bash
git clone https://github.com/rloisell/rl-agents-n-skills.git
cd rl-agents-n-skills
git checkout <tag-or-commit>
```

### 3. Install globally (available in every project)

Global installs require the **absolute path** to the repo or plugin folder.

**All five plugins, one command** (from the repo root):

Windows (PowerShell):

```powershell
apm install --global "$PWD" --target claude,copilot,codex,agy --parallel-downloads 0
```

macOS / Linux:

```bash
apm install --global "$PWD" --target claude,copilot,codex,agy
```

**One or a few plugins** (in isolation):

Windows (PowerShell):

```powershell
apm install "$PWD\plugins\<domain>" --global --target claude,copilot,agy,codex --parallel-downloads 0
```

macOS / Linux:

```bash
apm install "$PWD/plugins/<domain>" --global --target claude,copilot,agy,codex
```

`--parallel-downloads 0` avoids an "Access denied" error on Windows when APM renames its staging folder.

```text
APM state and cache          ~/.apm/                              (Windows: %USERPROFILE%\.apm\)
Claude Code skills           ~/.claude/skills/
Copilot and Codex skills     ~/.agents/skills/                    (shared)
Antigravity (agy) skills     ~/.gemini/antigravity-cli/skills/
```

If a skill folder already exists that APM did not create, APM skips it; add `--force` to overwrite.

### 4. Install into one project instead

From the consuming project root, point at the local clone:

```bash
apm install <path-to-clone>/plugins/<domain> --target claude,copilot,agy,codex
```

APM records the dependency in the project's `apm.yml`, writes `apm.lock.yaml`, deploys skills into `.claude/skills/` and `.agents/skills/`, and adds `apm_modules/` to `.gitignore`. In CI, reproduce the exact install with `apm install --frozen`.

### 5. Verify, Update, and Uninstall

Preview without writing files:

```bash
apm install <path-to-clone>/plugins/<domain> --target claude --dry-run
```

Update from a clone:

```bash
git fetch --tags && git checkout <new-tag-or-commit>
apm install --global
```

Uninstall:

```bash
apm uninstall <path-to-clone>/plugins/<domain> --global     # global install
apm uninstall <path-to-clone>/plugins/<domain>              # project install
```

### Troubleshooting on Windows

- **`[WinError 3] The system cannot find the path specified` under `%LOCALAPPDATA%\apm\cache\...`:** Install from a short local clone path (e.g. `C:\src\rl-agents-n-skills`) using the absolute-path command in section 3, or enable Windows Long Paths (`LongPathsEnabled = 1` and `git config --global core.longpaths true`).
- **`Access denied` on `.apm-resolution-staging`:** Add `--parallel-downloads 0`. If an earlier install was interrupted, delete `%USERPROFILE%\.apm\apm_modules\.apm-resolution-staging` and `%USERPROFILE%\.apm\.apm-lifecycle.lock` and retry.
- **`N files skipped -- local files exist, not managed by APM`:** Add `--force` to overwrite unmanaged skill folders.

---

## Option 2: Native Marketplace (Claude Code / Copilot CLI)

### Claude Code
```text
/plugin marketplace add rloisell/rl-agents-n-skills
/plugin
/plugin install <domain>
```

### Copilot CLI
```bash
copilot plugin marketplace add rloisell/rl-agents-n-skills
copilot plugin
copilot plugin install <domain>@rloisell-rl-agents-n-skills
```

---

## Local Development (Contributors & Testing)

Install plugins straight from the working tree to test changes before pushing:

```bash
apm install --global "$PWD" --target claude,copilot,agy,codex --parallel-downloads 0
```

Validate plugin structure, skills, and agents using `authoring-plugins`, `authoring-skills`, `authoring-subagents`, and `authoring-instructions` before opening a PR.
