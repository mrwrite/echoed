# Studio Activity Authoring Matrix

Date: 2026-07-13

The legacy draft model names these activity identifiers. Current CRUD is restricted to admin/teacher, so canonical Studio exposes none as editable controls.

| Type | Stored authoring fields | Learner rendering evidence | Validation/scoring | Preview | Accessibility concern |
| --- | --- | --- | --- | --- | --- |
| `text`, `story` | title, content, order | Text presentation | Non-empty content is not centrally validated | Student renderer exists | Heading/list semantics and readable line length |
| `video`, `audio` | title, content URL/reference, order | Media presentation varies | No verified rights/caption/transcript validation | Partial | Captions, transcript, controls, autoplay |
| `storybook` | title, content, ordered image pages | Storybook pages | Page/image validation is limited | Partial | Image alternative text is not modeled |
| `coloring` | title, uploaded/reference content | Image activity | Upload accepts file without documented type/size validation | Partial | Alt text and non-pointer alternative absent |
| `quiz` | title, serialized content, order | Lesson viewer validates answers before advance | Separate assessment system also exists; no stable Studio authoring schema verified | Learner renderer only | Labels, errors, answer exposure |
| `reflection`, `discussion` | title, content, order | Instruction/prompt presentation | No persistence contract verified | Presentation only | Clear instructions; do not imply saved responses |
| `checkpoint` | title, content, order | Runtime-dependent | No verified authoring/scoring contract | Unsupported in Studio | State announcement |

## Assessment model

Assessments expose title, description, scope relationships, assessment/availability/delivery states, passing score, maximum attempts, policy/lifecycle metadata, and ordered questions. Questions expose prompt, type, choices, explanation, points, and order. Creation is admin/teacher-only; no edit/delete authoring endpoints are present.

## Decision

Studio does not invent rubrics, manual grading, partial credit, retries, answer configuration, or activity editors. Content drafts may use artifact types `assessment_seed` or `lesson_draft`, but those records are not described as executable assessments or activities.
