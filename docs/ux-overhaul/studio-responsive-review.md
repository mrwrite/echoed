# Studio Responsive Review

Date: 2026-07-13

Target widths: 1440, 1280, 768, and 390 CSS pixels.

- Canonical pages use the shared constrained content width and responsive page padding.
- Overview counts, attention records, shortcuts, and libraries use bounded auto-fit grids.
- Search and filters wrap and become full-width on mobile.
- Detail definition grids change from two columns to one below 768px.
- Project creation/source/draft forms stack rather than compress into a narrow two-column editor.
- Long titles, citations, references, and draft bodies use wrapping and preserve document flow.
- Review actions wrap on desktop and become full-width touch targets on mobile.
- Shared confirmation dialogs remain bounded by viewport width.
- No viewport-scaled font size, negative letter spacing, fixed authoring canvas, horizontal table, or drag-only control was introduced.

The seeded Playwright Studio flow passed its 390px horizontal-overflow assertion in Chromium. Deep authoring at 200% zoom, mobile virtual-keyboard behavior, and representative long-citation review remain manual follow-up items.
