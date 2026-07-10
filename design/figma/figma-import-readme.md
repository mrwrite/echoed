# Figma Import Readme

This package is Figma-ready, not a native `.fig` file.

## Import Order

1. Create pages from `figma-file-structure.md`.
2. Add variables from `figma-variables.json`.
3. Build components from `figma-component-map.json`.
4. Create frames from `figma-screen-manifest.json`.
5. Wire prototype links from `figma-prototype-connections.json`.

## Naming Rules

- Use semantic variable names exactly as provided.
- Use frame names from `screen.name`.
- Prefix component sets by domain, for example `Navigation/Sidebar`, `Card/Course`, `StatePanel`.

## Implementation Notes

- Use 8px card radius unless a component spec says otherwise.
- Do not use generic purple SaaS gradients.
- Do not put cards inside cards.
- Keep learner screens less dense than teacher/admin screens.
- Use real EchoEd content from seed data, especially `Introduction to Africa`, not placeholder lorem ipsum.

## Native Figma Status

No native Figma file was created because no functioning Figma connector was available in this session.
