## ADDED Requirements

### Requirement: Role-aware application spaces
EchoEd SHALL present authenticated users with role-aware application spaces that reflect implemented capabilities instead of one generic workspace for all roles.

#### Scenario: Student receives learner navigation
- **WHEN** an authenticated user has only the `student` role
- **THEN** the primary navigation SHALL prioritize Learn, Assignments, Courses, Progress, Achievements, Discussions, and Profile
- **AND** workspace, studio, admin, and content operations SHALL NOT be shown

#### Scenario: Teacher receives teaching navigation
- **WHEN** an authenticated user has `teacher` or `instructor` access
- **THEN** the primary navigation SHALL prioritize Today, Classes, Assignments, Curriculum, Learner Support, Reports, Discussions, and Settings

#### Scenario: Admin receives administration navigation
- **WHEN** an authenticated user has `admin` or supported `super_admin` access
- **THEN** the primary navigation SHALL prioritize Admin Home, Users, Organizations, Curriculum, Badges, Reports, Moderation, Assets, and Platform Settings

### Requirement: Existing backend contracts are preserved
The overhaul SHALL reuse existing backend authentication, organization, role, permission, curriculum, lesson, progress, assignment, section, review, upload, analytics, and discussion APIs unless a separate backend change is explicitly proposed and approved.

#### Scenario: Login continues through current auth API
- **WHEN** a user signs in through the redesigned login screen
- **THEN** the frontend SHALL call the existing `/api/auth/token` flow
- **AND** session routing SHALL wait for the existing permission bootstrap

#### Scenario: Learning progress uses current governed segment APIs
- **WHEN** a student starts, restores, or completes a lesson
- **THEN** the frontend SHALL use the existing start-course, progress segment, lesson, and segment-complete APIs
- **AND** no parallel progress system SHALL be introduced

### Requirement: Community project language
EchoEd SHALL remove investor, commercial, sales, revenue, marketplace, and conversion language from user-facing screens unless the text is historical source content.

#### Scenario: Community workspace is shown
- **WHEN** users navigate to community or access-related areas
- **THEN** visible labels SHALL use community, stewardship, access, contribution, and learning language
- **AND** commercial labels SHALL NOT be shown to users

### Requirement: Accessible shared states
EchoEd SHALL provide consistent loading, empty, error, success, and permission-denied states across redesigned screens.

#### Scenario: Data fails to load
- **WHEN** a page-level API request fails
- **THEN** the screen SHALL explain what failed, whether data changed, and how to retry
- **AND** the error state SHALL be announced appropriately for assistive technology

#### Scenario: User lacks permission
- **WHEN** a user opens a route they cannot access
- **THEN** the screen SHALL show the current role or organization context where available
- **AND** it SHALL provide a safe next action such as back, profile, org switch, or sign in

### Requirement: Responsive role workflows
Redesigned screens SHALL remain usable at 390px mobile, 768px tablet, 1280px small desktop, and 1440px desktop target widths.

#### Scenario: Learner uses mobile navigation
- **WHEN** a student uses the app on a mobile viewport
- **THEN** the learner navigation SHALL expose the primary learner tasks without relying on a desktop sidebar

#### Scenario: Staff data tables reach mobile widths
- **WHEN** teacher or admin data tables do not fit the viewport
- **THEN** the UI SHALL provide an equivalent responsive data-list layout with the same key information and actions

### Requirement: Accessible controls and confirmation flows
Shared controls, menus, dialogs, tabs, drawers, lesson controls, quiz controls, and confirmation flows SHALL meet WCAG 2.2 AA expectations.

#### Scenario: Destructive action is initiated
- **WHEN** a user starts a destructive action such as deleting a user, deleting a course, or revoking access
- **THEN** EchoEd SHALL show a confirmation dialog that names the affected object and explains the impact
- **AND** the action SHALL NOT execute until the user confirms

#### Scenario: Keyboard user operates navigation and dialogs
- **WHEN** a keyboard-only user navigates redesigned screens
- **THEN** all interactive controls SHALL be reachable, visibly focused, and operable without a pointer

### Requirement: Visual design system foundations
EchoEd SHALL provide a warm, scholarly, culturally grounded, accessible visual system with documented tokens, typography, spacing, color roles, motion, icon, imagery, and data-visualization guidance.

#### Scenario: New component is implemented
- **WHEN** a redesigned component is added or migrated
- **THEN** it SHALL use the approved design token roles and component specifications
- **AND** it SHALL avoid undocumented page-local visual patterns unless justified

### Requirement: Coded design reference and visual validation
EchoEd SHALL maintain an isolated coded design reference and visual acceptance criteria before replacing broad production pages.

#### Scenario: Design reference is reviewed
- **WHEN** reviewers open the design-lab prototype
- **THEN** they SHALL be able to inspect representative public, login, student, teacher, admin, navigation, and shared state screens
- **AND** the reference SHALL NOT affect production Angular routing or backend behavior

#### Scenario: Production implementation begins
- **WHEN** production pages are redesigned
- **THEN** implementation SHALL include responsive, accessibility, and visual-regression acceptance checks for affected screens
