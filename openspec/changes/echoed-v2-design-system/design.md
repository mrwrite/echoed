# Design Notes

## Visual Language

The EchoEd V2 design system uses a deep indigo/midnight base with luminous accent colors. It favors frosted panels, subtle borders, large editorial headings, comfortable spacing, and restrained transitions.

Influences:

- Linear and Vercel for focused product workspace density.
- Stripe Dashboard for clear metrics and operational hierarchy.
- Notion and Arc for polished surfaces and calm navigation.
- Raycast and Apple for contrast, motion restraint, and premium restraint.

## Component Approach

Reusable standalone Angular components expose a small projection-based API. They intentionally do not fetch data, navigate, or mutate state. The global `.ee-*` utility classes remain available for existing pages and are upgraded to the same visual language.

## Behavior Preservation

All changes are presentational:

- Existing services remain untouched.
- Existing route definitions remain untouched.
- Existing forms submit through the same handlers.
- Existing lesson runtime and governance remain untouched.
