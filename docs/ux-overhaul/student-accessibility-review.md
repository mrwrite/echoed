# Student Accessibility Review

Date: 2026-07-11

## Completed

- `/learn` has one `h1`: "Continue your learning".
- Next learning appears first in DOM order after the page hero.
- Course progress bars include `role="progressbar"`, `aria-valuenow`, and text percentages.
- Student course states use text labels such as `Ready`, `In progress`, and `Complete`; status is not color-only.
- Loading, empty, and error states reuse shared `EchoLoadingStateComponent` and `EchoStatePanelComponent`.
- Lesson save state uses `role="status"` and save failure uses `role="alert"`.
- The lesson runtime return button has an accessible name: "Return to the course overview".
- Migrated controls use 44px-friendly button/link sizing and visible focus styles.
- `/learn/courses/:courseId` uses one `h1`, semantic ordered lists for unit and lesson hierarchy, text state labels, disabled lesson controls for locked/unavailable lessons, and accessible progress bars.
- Lesson runtime now exposes course, unit, and lesson-position context when the existing student-course data can resolve it.
- Quiz activity validation uses `role="alert"` and does not rely on color alone.
- Assessment submission uses the shared confirmation dialog with focus trap/Escape behavior supplied by `EchoConfirmationDialogComponent`.
- Certificate loading, empty, and error states use shared status/alert semantics.

## Risks

- Full keyboard walkthrough was not completed against a running seeded backend in this pass.
- Full automated contrast tooling was not run.
- Activity controls that delegate to canvas/map/storybook components still need device and assistive-technology QA in a later pass.

## Deferred Checks

- Keyboard-only seeded student journey through login, `/learn`, lesson, activity, completion, and return.
- Screen-reader verification for lesson activity controls and assessment result states.
- 200% zoom verification with real seeded lesson content.
