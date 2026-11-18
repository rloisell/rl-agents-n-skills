# AI Session Files Schema

Every project maintains four audit-trail files under `AI/` alongside `AI/nextSteps.md`.

## Contents

- [File overview](#file-overview) • [WORKLOG.md](#worklogmd) • [CHANGES.csv](#changescsv) • [COMMANDS.sh](#commandssh) • [COMMIT_INFO.txt](#commit_infotxt)

## File overview

| File | Updated | Purpose |
|------|---------|---------|
| `AI/WORKLOG.md` | End of session | Narrative log of all actions taken |
| `AI/CHANGES.csv` | Every file create/modify/delete | Machine-readable change record |
| `AI/COMMANDS.sh` | Every significant shell command | Reproducible command history |
| `AI/COMMIT_INFO.txt` | After every commit or push | Branch, hash, and push outcome record |

## WORKLOG.md

Prepend a new dated section at the top of Session History (newest first):

```markdown
## YYYY-MM-DD — Session N: <one-line objective>

### Actions
- <what was done, bullet list>

### Files Changed
- `path/to/file.ext` — <what changed and why>

### Commands Run
- `<significant command>` — <why it was run>

### Decisions Made
- <architectural or process decisions and their rationale>

### Outstanding / Carry-over
- <anything left for next session>
```

Keep the document under ~600 lines. Condense early history into summaries rather
than deleting entries so the full narrative remains traceable.

## CHANGES.csv

Append one row per file action (`created`, `modified`, `deleted`). No header row
is required once the file exists.

```csv
YYYY-MM-DD,created,src/Project.Api/Entities/NetworkTest.cs,Added NetworkTest entity for scheduled checks
YYYY-MM-DD,modified,.github/workflows/build-and-test.yml,Expanded path filter to include .github/**
YYYY-MM-DD,deleted,src/Project.Api/Migrations/00001_OldMigration.cs,Replaced by corrected migration
```

Fields: `date,action,relative/path/to/file,reason`.

## COMMANDS.sh

Append a dated comment header followed by significant commands run in that session:

```bash
# YYYY-MM-DD — Session N — <objective>
dotnet ef migrations add InitialCreate --project src/Project.Api
dotnet ef database update --project src/Project.Api
git add -A && git commit -m "feat: add NetworkTest entity and migration"
git push origin feat/network-test-entity
gh pr create --title "feat: add NetworkTest entity and migration" --base main
gh pr merge 5 --squash --delete-branch
```

Include migrations, git operations, `gh` CLI commands, container/cluster commands,
builds, and test runs. Omit trivial reads, `ls`, and `pwd`.

## COMMIT_INFO.txt

Append one line per significant commit or push:

```text
YYYY-MM-DD  <hash>  <branch>  <short message>  [pushed: yes/no]
```

Example:

```text
2026-02-27  a3f9c2d  feat/network-test  feat: add NetworkTest entity  pushed: yes
2026-02-27  1eb68b3  main               chore: squash merge PR #16    pushed: yes
```
