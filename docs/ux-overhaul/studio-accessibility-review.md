# Studio Accessibility Review

Date: 2026-07-13

## Implemented

- One page `h1` with logical section headings on canonical Studio screens.
- Labeled search, select, text, textarea, and file-independent forms with native required semantics.
- Minimum 44px controls and visible tokenized focus rings.
- Result counts, creation success, review success, and errors use live status/alert semantics.
- Shared loading, empty, error, and confirmation components provide consistent announcements.
- Publish and review dialogs trap focus, start on Cancel, support Escape, lock while saving, and restore focus.
- Status meaning is written in text and not conveyed by color alone.
- Responsive records preserve the same information and actions without a pointer-only table.
- Preview is a normal document flow with pre-wrapped text and no inaccessible authoring canvas.
- No drag-only reorder interaction is present.
- Reduced-motion behavior comes from the shared shell and production component foundations.

## Review results

Unit coverage verifies confirmation-before-mutation, failure preservation, visible empty/error states, labeled filters, and role-guarded routes. The seeded smoke includes keyboard focus and a 390px overflow assertion when executable.

## Remaining manual work

Screen-reader announcement timing, browser zoom at 200%, contrast under user overrides, long real citations, and mobile virtual-keyboard behavior require browser/manual validation. Upload progress, image alt-text forms, and accessible reordering are deferred because no supported Studio APIs exist for those controls.
