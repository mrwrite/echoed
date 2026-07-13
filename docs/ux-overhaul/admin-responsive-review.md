# Admin Responsive Review

Date: 2026-07-13

Target widths: 1440, 1280, 768, and 390 CSS pixels.

- Page width is constrained to the shared 72rem content maximum with responsive page padding.
- Overview metrics and shortcuts use auto-fit grids; alert/attention content remains first in DOM order.
- User and course desktop tables switch below 768px to equivalent stacked records. Desktop tables are removed from layout rather than left focusable off-screen.
- Organization and badge collections use auto-fit grids with a 13rem minimum bounded by container width.
- Filter fields and commands become full-width at mobile sizes; controls retain 44px touch height.
- Detail definition grids switch from two columns to one; identifiers use `overflow-wrap`.
- Dialog responsiveness and focus behavior are supplied by the shared confirmation component.
- No component uses viewport-scaled font sizes, negative letter spacing, fixed page widths, or pointer-only actions.

Automated build/unit validation passes. Seeded Playwright executes through a disposable SQLite fallback, and the Admin flow completes its 390px horizontal-overflow assertion. The browser smoke suite passes all three scenarios.
