# Acceptance Criteria — driving-spec-development

Observable pass/fail criteria for verifying Spec-Driven Development (SDD) workflows with Spec-Kit and Spec-Kitty.

## Phase Gate & Artifact Completeness

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Spec-before-code gate | Specification, technical plan, and task breakdown exist before implementation begins | Implementation code is written prior to spec, plan, and tasks |
| Requirement traceability | Feature spec defines unique `REQ-{NN}` IDs and testable acceptance criteria | Requirements lack `REQ-{NN}` identifiers or verifiable criteria |
| Scaffolding & gitignore | `.specify/` or `.kittify/` and `.github/prompts/` are committed; `__pycache__/`, `*.pyc`, `*.pyo` are in `.gitignore` | SDD config is untracked or Python cache files are committed |
| BC Gov §1 alignment | Public-sector features map requirements, assumptions, uncertainties, approvals, and owners | Public-sector spec omits OCIO §1 mapping table |

## Toolchain-Specific Validation

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Spec-Kit (`specify`) | `constitution -> specify -> plan -> tasks` sequence followed; `/speckit.analyze` reports 0 issues and all tasks checked | Phases skipped or `/speckit.analyze` reports unresolved inconsistencies |
| Spec-Kitty (`spec-kitty`) | `spec.md`, `plan.md`, and `tasks/WP{NN}-*.md` exist with valid YAML frontmatter; `spec-kitty validate-tasks --all` reports 0 mismatches | Missing WP frontmatter fields or `validate-tasks --all` fails |
| Lane progression | Completed work packages transition cleanly `planned -> in-progress -> review -> done` | Work packages marked `done` without passing review or validation |

## Scope Boundaries

- **Trigger**: Starting a new feature with Spec-Kit or Spec-Kitty, validating WP boards, or mapping BC Gov §1 requirements.
- **Do not trigger**: Architecture diagram exports (`documenting-architecture`) or session shutdown logging (`managing-dev-sessions`).
