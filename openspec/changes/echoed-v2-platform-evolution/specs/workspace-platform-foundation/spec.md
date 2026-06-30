# workspace-platform-foundation Specification

## ADDED Requirements

### Requirement: Workspace SHALL become the top-level V2 operating context
EchoEd SHALL introduce Workspace as the user-facing V2 container above existing organizations, projects, products, sources, artifacts, learners, analytics, and settings.

#### Scenario: Existing organization appears in V2 workspace navigation
- **WHEN** a user belongs to an existing organization
- **THEN** the V2 workspace shell displays that organization context as the active workspace context
- **AND** existing organization membership, role, and active organization behavior remain authoritative

#### Acceptance Criteria
- Existing organization flows remain functional.
- Workspace UI can be introduced without database migration in Phase 1.
- Future Workspace records can be backfilled from Organization records.

### Requirement: Workspace shell SHALL preserve current runtime access
The workspace shell SHALL reuse current authentication, organization context, route guards, and permissions.

#### Scenario: Role-aware user enters workspace
- **WHEN** a student, teacher, admin, org admin, or content admin enters a V2 route alias
- **THEN** the user sees only navigation items permitted by existing role and permission logic

#### Acceptance Criteria
- No new auth path is introduced.
- No current role loses access to an existing authorized page.
- No current role gains access to a restricted existing page.

## MODIFIED Requirements

### Requirement: Organization context SHALL support workspace framing
Existing organization context SHALL be presented as workspace context in V2 surfaces while preserving organization data ownership.

#### Scenario: User switches organization
- **WHEN** a user switches their active organization
- **THEN** V2 workspace labels, navigation, and page context update to match the selected organization

#### Acceptance Criteria
- Organization switching remains backed by existing organization APIs.
- Workspace terminology does not require replacing organization records.

