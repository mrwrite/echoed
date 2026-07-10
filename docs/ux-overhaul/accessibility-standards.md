# Accessibility Standards

Target: WCAG 2.2 AA.

## Keyboard

- All interactive controls reachable by Tab.
- Visible focus on every focusable element.
- Menus, tabs, comboboxes, dialogs, drawers, lesson controls, and quiz controls must support expected keyboard behavior.
- Escape closes menus/popovers/dialogs unless a critical confirmation requires explicit choice.

## Screen Readers

- One `h1` per page.
- Landmarks: banner, navigation, main, complementary where applicable.
- Loading: `role="status"` with concise text.
- Errors: `role="alert"` only for immediate feedback.
- Route changes should focus the page heading or main container.

## Color and Contrast

- Body text: 4.5:1 minimum.
- Large text: 3:1 minimum.
- Icons, borders, focus, charts: 3:1 minimum.
- Never use color alone for status.

## Forms

- Every control has a programmatic label.
- Hints and errors use `aria-describedby`.
- Required fields are indicated visually and programmatically.
- Submit buttons show pending state without losing focus.

## Motion

- Respect `prefers-reduced-motion`.
- No parallax, background orbs, or decorative motion on app screens.
- Loading skeletons should pause under reduced motion.

## Responsive and Touch

- Primary touch targets should be 44px minimum.
- Text must not overlap or clip at 390px width.
- Tables must have responsive data-list alternatives when columns exceed viewport.

## Data Visualization

- Include text summaries.
- Use patterns/labels in addition to color.
- Tooltip information must be accessible through keyboard or details panels.

## Lesson and Assessment Safety

- Progress-saving state must be visible.
- Leaving a lesson with unsaved work requires confirmation.
- Assessment submit must announce pending, success, and failure states.
