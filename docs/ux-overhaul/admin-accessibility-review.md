# Admin Accessibility Review

Date: 2026-07-13

## Implemented Checks

- One named page `h1`, logical section headings, semantic `main`, tables, captions, headers, definition lists, forms, labels, and buttons.
- Desktop semantic tables have equivalent mobile records with the same identity, status, and primary action.
- Search/filter result counts and asynchronous states use live status semantics through shared components.
- Status always includes text; no meaning relies on color.
- Controls have 44px minimum height, visible tokenized focus rings, and no hover-only actions.
- Shared confirmation dialog traps focus, supports Escape, restores focus, names the object and consequence, and exposes action errors.
- Badge images use meaningful alt text; missing images have a named alternative.
- Form validation associates visible labels and `aria-invalid`; badge form errors are announced.
- Long names, usernames, and email addresses wrap in detail definitions.
- Existing shell skip link, mobile drawer focus behavior, and reduced-motion foundation remain unchanged.

## Validation

Karma coverage exercises state semantics, privacy omission, confirmation gating, navigation, deep-link roles, and image naming. Seeded Playwright covers primary Admin navigation, filtering, dialog cancel, unauthorized deep link, and 390px overflow when services are available.

Manual screen-reader and browser zoom execution remains open with seeded browser infrastructure. Sorting and pagination are not present because current APIs return unpaged lists and this phase does not invent server behavior.
