## Why

The V2 workspace/admin area does not yet match the premium visual direction established by the redesigned landing, login, and registration pages. This polish phase makes the authenticated content/admin workspace feel investor-ready, product-led, and cohesive without changing backend behavior, authorization, routing semantics, or education runtime behavior.

## What Changes

- Apply a shared premium admin design language to the V2 workspace shell and workspace pages.
- Refine the sidebar into a polished workspace rail with icon-led navigation, clearer active states, better grouping, non-clipped labels, improved collapsed behavior, and a refined profile footer.
- Refine the top command header with stronger breadcrumb/title hierarchy, cleaner organization selector styling, premium tour CTA treatment, and improved avatar presentation.
- Replace gray/washed workspace backgrounds with a premium shell using subtle gradients, frosted panels, clean content surfaces, and consistent max-width containers.
- Add consistent hero panels, cards, status badges, action rows, empty states, forms, lists, metrics, and timelines for workspace/admin pages.
- Polish `/workspace`, `/workspace/projects`, `/workspace/product-studio`, `/workspace/products`, `/workspace/knowledge-sources`, `/workspace/artifacts`, `/workspace/review-center`, `/workspace/access`, `/workspace/analytics`, `/workspace/commercial`, `/workspace/learners`, and `/workspace/settings`.
- Preserve all existing data flows, service calls, permissions, route behavior, and runtime lesson governance.

## Capabilities

### New Capabilities

### Modified Capabilities
- `design-system-governance`: Extend the reusable design-system contract to cover premium authenticated workspace/admin primitives and motion/accessibility behavior.
- `shell-bootstrap-and-navigation-readiness`: Extend shell/navigation visual requirements for a premium workspace rail and command-center header while preserving deterministic role-aware navigation.

## Impact

- Affected code is limited to frontend Angular workspace/admin components, shared EchoEd design-system styles, and OpenSpec artifacts.
- No backend API changes.
- No authorization changes.
- No route semantic changes.
- No education runtime behavior changes.
- Existing frontend tests and production build remain the verification boundary.
