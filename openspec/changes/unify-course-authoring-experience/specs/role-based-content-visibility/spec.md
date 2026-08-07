## ADDED Requirements

### Requirement: Course-authoring actions are capability-based and organization-scoped
The platform SHALL derive course-authoring actions from the authenticated user's platform role, active organization membership, course relationship, and organization policy, and SHALL enforce those actions on the backend for every mutation.

#### Scenario: Content administrator authors organization curriculum
- **WHEN** an active content administrator creates or edits a course within an authorized organization
- **THEN** the platform permits authoring and review submission while withholding review or publication actions not granted by policy

#### Scenario: Organization administrator manages a course
- **WHEN** an active organization administrator acts on a course within the administered organization
- **THEN** the platform exposes only the authoring, assignment, review, or publication actions allowed by organization policy

#### Scenario: Teacher adapts curriculum
- **WHEN** a teacher or instructor is permitted to adapt an assigned or approved course
- **THEN** the platform applies the configured derivative-copy or version workflow without implicitly granting canonical publication authority

#### Scenario: Reviewer evaluates submitted content
- **WHEN** a reviewer opens a course submitted within the reviewer's authorized scope
- **THEN** the platform permits the configured review decision and feedback actions without implicitly granting authoring ownership

#### Scenario: Frontend capability state is stale or manipulated
- **WHEN** a client sends an authoring, review, or publication mutation that the backend capability decision does not allow
- **THEN** the backend rejects the mutation without changing canonical content or lifecycle state

### Requirement: Authoring capability discovery is consistent across navigation and APIs
The platform SHALL provide a bounded capability representation that lets authorized clients render course actions consistently without treating client-side route guards as authorization.

#### Scenario: User opens a course collection
- **WHEN** the course collection or course detail loads for authenticated staff
- **THEN** the response or associated capability contract identifies permitted create, edit, duplicate, submit, review, preview, and publish actions for the relevant scope

#### Scenario: User follows a deep link
- **WHEN** a user follows an authoring deep link
- **THEN** route access, rendered controls, and backend mutation decisions resolve from the same canonical capability rules

