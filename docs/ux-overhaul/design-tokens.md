# Design Tokens

Machine-readable token files:

- `frontend/src/styles/tokens/design-tokens.json`
- `frontend/src/styles/tokens/_design-tokens.scss`
- `frontend/src/styles/tokens/design-tokens.css`

## Token Categories

| Category | Examples | Purpose |
| --- | --- | --- |
| Primitive color | `color.primitive.palm.700` | Raw palette values. |
| Semantic color | `color.action.primary.background` | Component/system meaning. |
| Typography | `font.family.body`, `font.size.body.md` | Stable text hierarchy. |
| Spacing | `space.4`, `space.layout.page` | Layout rhythm. |
| Radius | `radius.control.default`, `radius.card.default` | Shape consistency. |
| Border | `border.width.default`, `color.border.subtle` | Surface distinction. |
| Elevation | `shadow.raised`, `shadow.overlay` | Depth without excess. |
| Motion | `motion.duration.fast`, `motion.easing.standard` | Predictable interaction. |
| Focus | `focus.ring.color`, `focus.ring.width` | Accessible focus. |

## Color Roles

| Role | Token | Usage |
| --- | --- | --- |
| Page background | `color.surface.page` | Main app background. |
| Surface | `color.surface.default` | Panels, cards, dialogs. |
| Raised surface | `color.surface.raised` | Headers, drawers, overlays. |
| Primary text | `color.text.default` | Body and headings. |
| Muted text | `color.text.muted` | Secondary metadata. |
| Primary action | `color.action.primary.*` | Main CTA and active nav. |
| Secondary action | `color.action.secondary.*` | Secondary buttons. |
| Success | `color.status.success.*` | Completed, published, active. |
| Warning | `color.status.warning.*` | Needs review, pending, caution. |
| Danger | `color.status.danger.*` | Errors/destructive. |
| Info | `color.status.info.*` | Neutral guidance, links. |

## Accessibility Notes

- Do not use token pairs unless documented as AA-compliant.
- Status badges must include text labels.
- Focus ring must be visible on dark and light surfaces.
- Minimum touch control height: 44px.
