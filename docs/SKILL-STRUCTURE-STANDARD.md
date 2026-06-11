# Skill Structure Standard

This repository adopts a seven-section skill structure to improve consistency, reviewability, and upstream alignment.

## Required sections

All new skills should include these sections in this order:

1. Use When
2. Don't Use When
3. Workflow
4. Rules
5. Examples
6. Edge Cases
7. References

## Phase adoption policy

### Phase 1 (now)

1. Define and publish this standard.
2. Require new skills to follow the seven-section structure.
3. Keep existing legacy skills unchanged unless they are being actively edited.

### Phase 2 (now)

1. Apply the seven-section structure to newly created skills.
2. Start with `bc-gov-deployment-cicd-analyst` as the reference implementation.

### Phase 3 (next)

1. Add a lightweight validation script/check for required sections.
2. Add CI enforcement once false-positive risk is low.

## Notes on compatibility

1. Existing frontmatter fields remain supported.
2. Existing folder layout remains valid during transition.
3. This standard is designed to align with the emerging BC Gov agent-skills direction.
