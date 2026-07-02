## Context

The public landing, login, and registration pages now establish a premium EchoEd visual direction: dark bordered canvases, purple/gold accents, frosted surfaces, confident typography, compact premium actions, and clear product-led messaging. The authenticated V2 workspace/admin area still reads closer to a generic admin dashboard in several places, with uneven spacing, raw list/form layouts, and less polished navigation.

This change is UI/UX polish only. Existing Angular routes, service calls, authorization, organization bootstrap, data contracts, and education runtime behavior remain unchanged.

## Goals / Non-Goals

**Goals:**
- Extend the approved premium visual direction into workspace/admin pages.
- Establish reusable frontend utility classes for shell, page, hero, cards, metrics, status badges, action rows, empty states, forms, lists, timelines, and buttons.
- Polish the sidebar and top header without changing the navigation items users are allowed to see.
- Improve page-level hierarchy for the workspace dashboard, project/product/content/admin pages, and settings.
- Preserve existing user actions, service calls, routes, and guards.
- Honor keyboard focus states, responsive layout, and reduced-motion preferences.

**Non-Goals:**
- No backend changes.
- No authorization, route semantic, or organization bootstrap changes.
- No new product, billing, AI generation, review, access, learner, or analytics features.
- No changes to lesson runtime governance or education delivery behavior.
- No dependency additions.

## Decisions

1. **Use shared SCSS utility classes instead of a new component library.**
   - Rationale: The affected pages already mix standalone Angular components and local templates. Shared classes in existing global/component styles provide broad consistency with lower risk than introducing a new component hierarchy.
   - Alternative considered: Create new Angular primitives for every UI element. Rejected for this polish phase because it would create more behavioral and template churn.

2. **Keep page data bindings and actions intact while upgrading visual structure.**
   - Rationale: Acceptance criteria require existing functionality unchanged. Templates can be reorganized into premium cards/forms/lists, but should keep the same event handlers, router links, and service-backed collections.
   - Alternative considered: Add computed view models or new service aggregation. Rejected because it risks changing data behavior.

3. **Polish shell navigation through presentation-only metadata and CSS.**
   - Rationale: Sidebar icons, active states, grouping, and collapsed layout can improve without altering permission decisions or route availability.
   - Alternative considered: Replace routing/navigation semantics. Rejected by scope.

4. **Use a light content surface inside a premium gradient shell where appropriate.**
   - Rationale: The admin workspace needs readability for dense operational content while still inheriting the public-page premium feel.
   - Alternative considered: Fully dark dashboards everywhere. Rejected because table/form-heavy workspace pages need high readability and clear contrast.

## Risks / Trade-offs

- **Large page surface area** -> Mitigation: prioritize shared classes and targeted templates/styles for the listed workspace routes.
- **Visual polish could accidentally alter behavior** -> Mitigation: preserve existing bindings, service calls, router links, and action handlers; run existing frontend tests and build.
- **Component style budgets may be stressed** -> Mitigation: centralize reusable styles and keep local CSS focused.
- **Dense pages can become overly decorative** -> Mitigation: keep admin pages product-led and professional, with content surfaces optimized for scanning.
- **Screens may vary by available seeded data** -> Mitigation: improve empty states and card/list layouts without assuming new backend fields.
