# Student Activity Type Matrix

Date: 2026-07-11

Activity rendering remains in `frontend/src/app/shared/lesson-viewer.component.*`. Formal scoring remains in assessment routes and APIs.

| Type identifier | Renderer/component | API interaction | Submission model | Feedback model | States implemented | Accessibility risks | Responsive risks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `video` | Native `video` or YouTube `iframe` | None in viewer | None | Browser media controls | In progress, ready to continue | Captions depend on media source | Wide media at mobile widths |
| `image` | Native `img` | None | None | None | In progress, ready to continue | Alt uses activity title | Large images need viewport checks |
| `coloring` | `ColoringCanvasComponent` | None in viewer | Local canvas interaction | None | In progress, ready to continue | Canvas keyboard alternatives remain a future risk | Canvas controls need mobile QA |
| `interactive_map` | `AfricaMapExplorerComponent` | None in viewer | Local interaction | Component-specific | In progress, ready to continue | Must remain keyboard operable | Map density at 390px needs visual QA |
| `storybook` | `StorybookViewerComponent` | Static storybook assets | None | None | In progress, ready to continue | Image alt/captions depend on pages | Image fit needs visual QA |
| `audio` | Native `audio` | None | None | Browser media controls | In progress, ready to continue | Captions/transcripts depend on content | Native controls vary by browser |
| `story` | Text block | None | None | None | In progress, ready to continue | Long text readability | Good after wrapping |
| `reflection` | Textarea | None | Local draft only | None | In progress, ready to continue | Draft is not authoritative progress | Mobile keyboard overlap needs visual QA |
| `checkpoint` | Text block | None | None | None | In progress, ready to continue | None beyond reading level | Good after wrapping |
| `quiz` | Radio options or fallback text input | None in viewer | Local selection before lesson completion | No correctness shown | In progress, validation-needed, ready to continue | Must not imply scored submission | Long options wrap on mobile |
| fallback | Text block | None | None | None | In progress, ready to continue | Unknown content quality | Needs visual QA per content |

## Implemented Interaction States

- Not started: future lesson steps in the step list.
- In progress: current activity step before required local interaction is satisfied.
- Validation-needed: quiz activity when Next is pressed without a selected answer.
- Ready to continue: current step can move forward.
- Completed: prior steps in the step list.

## Not Implemented Here

Submitted, correct, incorrect, partially correct, retry available, retry unavailable, and awaiting feedback belong to formal assessment behavior because no lesson activity submission endpoint exists.
