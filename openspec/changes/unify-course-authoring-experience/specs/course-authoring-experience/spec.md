## ADDED Requirements

### Requirement: Permitted creators enter one canonical course studio
The platform SHALL provide one canonical course-authoring experience for every user with an organization-scoped or platform-scoped authoring capability and SHALL NOT require users to choose between disconnected shell-creation and nested-editing workflows.

#### Scenario: Content administrator starts a course
- **WHEN** a content administrator with active organization authoring permission selects Create course
- **THEN** the platform creates or opens a durable draft in the canonical course studio
- **AND** the same studio supports setup, structure, content, quality, preview, and review submission

#### Scenario: User lacks authoring permission
- **WHEN** a user without course-authoring capability navigates directly to a course-studio route
- **THEN** the platform denies the authoring action consistently with the backend authorization decision
- **AND** it does not expose mutation controls through alternate routes

### Requirement: Course creation supports guided starting points
The course studio SHALL support blank creation, internal templates, and permitted course duplication through a common draft-creation contract.

#### Scenario: Creator starts from a blank course
- **WHEN** a permitted creator chooses Blank course and supplies the minimum required identity
- **THEN** the system creates a durable organization-scoped draft and opens it in the studio

#### Scenario: Creator duplicates a permitted course
- **WHEN** a permitted creator chooses a course they are authorized to duplicate
- **THEN** the system creates a distinct draft with copied authorable content, regenerated identifiers, preserved source attribution, and no inherited learner enrollments or publication state

### Requirement: Course setup captures instructional identity and alignment metadata
The course studio SHALL let creators define title, description, subject, audience or age or grade range, locale, course-level learning objectives, skills, and standards metadata supported by the canonical course model.

#### Scenario: Creator completes course setup
- **WHEN** a creator enters supported instructional identity and alignment metadata
- **THEN** the system persists it to the durable draft and presents it in subsequent quality and preview views

#### Scenario: Required setup data is missing
- **WHEN** a creator attempts a transition that requires missing or invalid setup data
- **THEN** the studio identifies each affected field in text, explains how to correct it, and moves focus to or links directly to the first issue

### Requirement: Creators build the canonical course hierarchy in context
The course studio SHALL present a persistent editable outline for canonical units, lessons, activities, source references, and assessment references without introducing a parallel hierarchy.

#### Scenario: Creator adds nested content
- **WHEN** a creator adds a unit, lesson, or supported activity from the outline
- **THEN** the new item appears in its intended parent with a deterministic order and can be edited without leaving the course context

#### Scenario: Creator duplicates an outline item
- **WHEN** a creator duplicates a permitted unit, lesson, or activity
- **THEN** the system creates distinct identifiers, preserves authorable content and attribution, and places the duplicate adjacent to the source item with deterministic ordering

### Requirement: Reordering is efficient and accessible
The course studio SHALL support deterministic reordering through keyboard-operable, single-pointer non-drag controls in addition to any drag-and-drop interaction.

#### Scenario: Creator reorders without dragging
- **WHEN** a creator activates Move up, Move down, or an equivalent non-drag position control
- **THEN** the item moves to the requested valid position, ordering is renumbered deterministically, and the result is announced as a status message

#### Scenario: Creator uses drag and drop
- **WHEN** a creator completes a drag-and-drop reorder
- **THEN** the same canonical ordering operation and validation apply as for non-drag reordering

### Requirement: Draft work is durable and recoverable
The course studio SHALL autosave durable drafts, display current save state, prevent duplicate creation during retries, detect conflicting revisions, and allow failed changes to be retried without discarding the creator's input.

#### Scenario: Autosave succeeds
- **WHEN** a creator changes a draft and the autosave interval elapses
- **THEN** the system persists the change against the current revision and displays the saved state and time

#### Scenario: Autosave fails
- **WHEN** a draft save fails because of network or server error
- **THEN** the studio retains the unsaved input, displays a specific failed-save state, and offers retry without creating another course

#### Scenario: Draft has a conflicting revision
- **WHEN** a save is based on a revision older than the server's current revision
- **THEN** the system rejects silent overwrite and presents a bounded conflict outcome with reload or recovery options

#### Scenario: Creator exits and resumes
- **WHEN** a creator leaves the studio after a successful save and later reopens the draft
- **THEN** the studio restores the saved course graph, selected draft identity, and current lifecycle state

### Requirement: Quality guidance is actionable and progressively disclosed
The course studio SHALL distinguish blocking issues from recommendations and SHALL evaluate completeness, objective alignment, assessment coverage, deterministic ordering, accessibility prompts, source attribution, media validity, and canonical governance readiness where data is available.

#### Scenario: Course has quality issues
- **WHEN** a creator opens the quality view for an incomplete or inconsistent draft
- **THEN** the studio groups issues by severity and course location
- **AND** each issue explains the expected correction and links to the affected item

#### Scenario: Course has no known blocking issue
- **WHEN** all required automated checks pass
- **THEN** the studio reports that automated checks are satisfied without representing that result as human review approval or certification

### Requirement: Authorized staff can preview the learner-safe experience
The course studio SHALL provide authorized staff a responsive learner preview of a selected durable draft or version without making it learner-visible.

#### Scenario: Creator previews a draft
- **WHEN** authorized staff selects learner preview
- **THEN** the system renders the learner-safe serialization and ordered delivery view for that draft or version
- **AND** it suppresses educator-only fields while clearly labeling the experience as a preview

#### Scenario: Learner requests the previewed draft
- **WHEN** a learner attempts to access content that has only been previewed and not published
- **THEN** canonical learner availability rules continue to return the governed unavailable outcome

### Requirement: The authoring experience is responsive and WCAG 2.2 AA-oriented
The course studio SHALL provide programmatic labels, logical headings and focus order, keyboard operation, visible focus, text-based error identification, announced save and reorder status, adequately sized controls, and usable layouts across desktop, tablet, and mobile breakpoints.

#### Scenario: Keyboard user builds course structure
- **WHEN** a creator uses only a keyboard to add, edit, reorder, validate, preview, and submit a course
- **THEN** all required authoring functions remain operable with visible focus and predictable focus movement

#### Scenario: Assistive technology receives status feedback
- **WHEN** save, validation, upload, reorder, or submission state changes asynchronously
- **THEN** the relevant status is exposed programmatically without forcing an unexpected context change

### Requirement: Import and export adapters protect canonical data
The platform SHALL define a bounded import/export boundary that maps supported external or internal packages to the canonical authoring aggregate and reports unsupported or invalid content before mutation.

#### Scenario: Creator imports a supported package
- **WHEN** a permitted creator uploads a supported course package
- **THEN** the system validates it, presents a mapping and issue report, and creates a draft only after explicit confirmation

#### Scenario: Package contains unsupported content
- **WHEN** an import includes unsupported activity, assessment, metadata, or media constructs
- **THEN** the system reports each unsupported construct and does not silently discard it

