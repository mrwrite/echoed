## ADDED Requirements

### Requirement: Forum mutations fail closed
The backend SHALL require authentication for every supported forum mutation, derive ownership from the authenticated user, enforce author-or-moderator changes, and leave unsupported mutation capabilities disabled.

#### Scenario: Anonymous user attempts a forum mutation
- **WHEN** an anonymous actor creates, edits, or deletes a thread or post
- **THEN** the backend returns 401 and does not mutate forum state

#### Scenario: Author edits owned forum content
- **WHEN** an authenticated author updates the mutable content of their own thread or post
- **THEN** the backend preserves ownership and applies the update

#### Scenario: Non-owner attempts a forum mutation
- **WHEN** an authenticated non-moderator edits or deletes another author's content
- **THEN** the backend returns 403 without disclosing or changing protected fields

### Requirement: Privileged user management uses explicit policy
The backend SHALL authorize platform user-management through explicit actor and target role allowlists, organization boundaries, allowed request fields, and deny-by-default behavior.

#### Scenario: Lower administrator targets a higher role
- **WHEN** an admin attempts to modify a super administrator or grant a platform-administrator role
- **THEN** the backend returns 403 and preserves the target account

#### Scenario: Mass assignment is attempted
- **WHEN** a privileged update contains a password, identifier, ownership, organization, or other non-allowlisted field
- **THEN** validation rejects the request and no sensitive field changes

### Requirement: Administrator safety invariants are enforced
The backend SHALL prevent self-escalation, unsafe administrative self-lockout, and removal of the final usable highest-privileged platform administrator.

#### Scenario: Final super administrator is removed
- **WHEN** a mutation would demote or delete the final usable super administrator
- **THEN** the backend rejects the conflict transactionally with an actionable safe error

#### Scenario: Multiple super administrators exist
- **WHEN** an authorized super administrator demotes or deletes another super administrator and at least one usable super administrator remains
- **THEN** the backend permits the otherwise-valid mutation

#### Scenario: Administrator targets self
- **WHEN** an administrator attempts to change their own authority or delete their own account through privileged management
- **THEN** the backend rejects the self-lockout or self-escalation action

### Requirement: Sensitive routes are rate limited
The backend SHALL apply centrally configured fixed-window limits to authentication, uploads, invitations, forum writes, and privileged user mutations and SHALL return 429 with retry metadata when a limit is exceeded.

#### Scenario: Authentication abuse exceeds a limit
- **WHEN** one safe authentication key exceeds the configured attempts in its window
- **THEN** the backend returns a generic 429 response with `Retry-After` without confirming account existence

#### Scenario: Independent actors use a protected route
- **WHEN** distinct authenticated user keys use a limited mutation route within policy
- **THEN** each key receives an independent allowance

#### Scenario: Window expires
- **WHEN** the configured fixed window has elapsed
- **THEN** the actor can make requests under a new allowance

### Requirement: Existing uploads validate actual content
The backend SHALL authenticate upload actors, enforce explicit size and image-format allowlists, validate magic bytes and safe dimensions, generate storage names, and complete writes atomically.

#### Scenario: Claimed image has a mismatched signature
- **WHEN** an upload has an allowed filename and MIME type but invalid or mismatched bytes
- **THEN** the backend rejects it without leaving a stored or partial file

#### Scenario: Traversal filename is supplied
- **WHEN** an authorized actor uploads an otherwise-valid image with path segments in the client filename
- **THEN** the server stores it only under a generated name inside the configured destination

### Requirement: Administrative responses are minimized
Privileged user and organization-administration endpoints SHALL use explicit response schemas that include only fields required by supported consumers and exclude secrets and backend-only relationships.

#### Scenario: Administrator lists users
- **WHEN** an authorized administrator requests the user list
- **THEN** each response contains only the documented user summary fields and never includes password hashes or ORM relationships

#### Scenario: Organization administrator lists invitations
- **WHEN** an organization administrator requests invitations
- **THEN** the response omits invitation bearer tokens and platform-only user information

### Requirement: Object and organization authorization is enforced server-side
Every audited protected object route SHALL verify actor role, organization membership, ownership or parent scope as applicable, and SHALL conceal cross-organization resources consistently.

#### Scenario: Organization A actor requests Organization B object
- **WHEN** an organization-scoped actor supplies a valid identifier belonging to another organization
- **THEN** the backend denies or conceals the object without returning its protected data

#### Scenario: Child object belongs to another parent
- **WHEN** a client combines an authorized parent identifier with a child identifier from another scope
- **THEN** the backend rejects the mismatch and does not mutate either resource

### Requirement: Security failures use consistent safe responses
The API SHALL use 401 for missing or invalid authentication, 403 for known permission denial, 404 for absence or intentional concealment, 409 for security-relevant state conflicts, 422 for validation, and 429 for throttling.

#### Scenario: Protected operation is denied
- **WHEN** a security-sensitive request fails authentication, permission, state, validation, or rate policy
- **THEN** it returns the corresponding non-success status without stack traces, SQL details, tokens, or unnecessary existence disclosure

### Requirement: High-impact actions emit privacy-safe events
The backend SHALL emit structured security events through the existing logging boundary for privileged role/account actions, final-admin failures, rate-limit triggers, authentication failures, upload rejection, forum moderation, and cross-organization denials where the current architecture supports them.

#### Scenario: Privileged mutation succeeds or fails
- **WHEN** a high-impact administrative action is evaluated
- **THEN** logging records correlation, actor, action, target type, result, and a safe reason without passwords, tokens, file contents, or unnecessary personal data

### Requirement: Frontend behavior aligns with hardened APIs
Angular SHALL avoid controls that cannot succeed for the known actor and SHALL present accessible safe states for 401, 403, concealed 404, administrator conflicts, upload rejection, and 429 outcomes while backend enforcement remains authoritative.

#### Scenario: Rate-limited form submission
- **WHEN** the API returns 429 for a supported user action
- **THEN** Angular announces a safe retry message accessibly and preserves entered form content where safe

### Requirement: Security verification preserves supported workflows
The change SHALL preserve or legitimately increase backend, Angular, and Playwright collection baselines and SHALL add direct-request regression coverage for forum, admin safety, rate limits, uploads, object authorization, and cross-organization isolation.

#### Scenario: Phase 8 verification runs
- **WHEN** complete repository verification is executed
- **THEN** supported Student, Teacher, Studio, organization-admin, platform-admin, public, authentication, and onboarding workflows pass without an unexplained test reduction
