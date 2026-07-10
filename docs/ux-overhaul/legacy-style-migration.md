# Legacy Style Migration

## Phase 1 Approach

Production now imports `frontend/src/styles/tokens/design-tokens.css`. Global compatibility aliases in `frontend/src/styles.scss` map older `--echo-*`, `--echo-v2-*`, and draft `--ee-*` names to approved semantic token values where practical.

This phase intentionally avoids rewriting every legacy page stylesheet. The new shell and shared primitives consume semantic `--ee-color-*`, `--ee-space-*`, `--ee-radius-*`, `--ee-shadow-*`, `--ee-motion-*`, and focus-ring tokens directly.

## Temporary Aliases

- `--echo-*`: retained for older dashboard and public page styles.
- `--echo-v2-*`: retained for existing workspace/V2 pages.
- `--ee-midnight`, `--ee-purple`, `--ee-azure`, and related draft aliases: retained for legacy V2 page styles, now backed by approved token values.
- `--ee-duration-*` and `--ee-easing-*`: retained for older pages, backed by approved motion tokens.

## Remaining Legacy Patterns

- Raw color values remain in older page-local SCSS and inline component styles outside the Phase 1 shell.
- Several older pages still use large rounded cards, gradients, and glass-like panels.
- Sass deprecation warnings remain in `frontend/src/styles/_typography.scss` for mixed declarations.
- Some V2 route labels remain in page internals; visible shell navigation has been renamed where safe.

## Migration Rules

1. Migrate page styles only when their screen enters the approved implementation phase.
2. Keep backend route names and model terminology unchanged.
3. Replace visible commercial/investor-facing labels only when the route can safely keep its technical path.
4. Prefer shared primitives before adding new page-local controls.
5. Remove compatibility aliases only after `rg` confirms no production consumers remain.
