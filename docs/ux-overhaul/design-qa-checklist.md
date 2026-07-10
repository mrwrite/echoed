# Design QA Checklist

## Before Implementation

- [ ] Audit artifacts reviewed.
- [ ] Route inventory accepted.
- [ ] Role-capability matrix accepted.
- [ ] Backend change assessment accepted.
- [ ] Figma-ready package reviewed or imported.
- [ ] Design-lab prototype reviewed at 1440, 1280, 768, and 390 widths.

## Per Screen

- [ ] Role and user goal are clear.
- [ ] One primary action is obvious.
- [ ] Page title and description match route context.
- [ ] Loading, empty, error, permission, and success states exist.
- [ ] Forms have labels, hints, validation, and submit-pending state.
- [ ] Destructive actions require confirmation.
- [ ] Keyboard-only operation works.
- [ ] Screen-reader order is logical.
- [ ] Mobile layout has no overlap or clipped text.
- [ ] Status is not color-only.
- [ ] API dependencies are documented.
- [ ] Backend changes are explicitly classified as required, optional, or avoided.

## Per Component

- [ ] Uses semantic tokens.
- [ ] Has documented variants and states.
- [ ] Has accessible name/role/value.
- [ ] Has focus/hover/active/disabled/loading states.
- [ ] Has responsive behavior.
- [ ] Has component tests or Storybook coverage.

## Release Readiness

- [ ] `npm test -- --watch=false --browsers=ChromeHeadless` passes.
- [ ] `npm run build` passes.
- [ ] Playwright role-flow smoke tests pass for seeded demo.
- [ ] Visual regression screenshots reviewed.
- [ ] Contrast checks pass.
- [ ] No investor/commercial copy remains in visible UI.
- [ ] Deprecated routes/styles have a rollback plan.
