# Organization Administration Accessibility Review

Date: 2026-07-14

The canonical Organization pages use one page heading, semantic section headings, labeled search/filter/form controls, text status labels, shared loading/error/empty states, and descriptive links whose accessible names include the affected class or destination. Result counts and save outcomes use live status regions.

Invitation privilege changes use the shared confirmation dialog with explicit object and consequence wording, focus trapping, Escape/cancel behavior, and focus restoration. The UI does not rely on hover-only controls or color alone. Inputs and actions retain visible focus and minimum touch-target sizing.

Member, invitation, class, and offering collections use responsive semantic records rather than horizontally scrolling desktop tables. Long names, usernames, and invitation addresses wrap. The mobile navigation and reduced-motion behavior remain provided by the shared shell.

Automated component and Playwright coverage verifies labels, keyboard entry through primary navigation and filters, confirmation cancellation, permission handling, and the 390px layout. A full assistive-technology audit remains part of the cross-product accessibility hardening task.
