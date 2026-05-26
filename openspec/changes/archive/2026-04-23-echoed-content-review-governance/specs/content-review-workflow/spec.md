## ADDED Requirements

### Requirement: Lesson review workflow uses constrained status transitions
The system SHALL manage lesson review through the existing `review_status` field using the states `draft`, `reviewed`, and `approved`, with transitions enforced by backend validation.

#### Scenario: Author saves or updates a lesson draft
- **WHEN** an authorized lesson editor creates or updates a lesson without reviewer approval intent
- **THEN** the system permits the lesson to remain in `draft`

#### Scenario: Reviewer advances a lesson through governance states
- **WHEN** an authorized reviewer updates a ready lesson from `draft` to `reviewed` or from `reviewed` to `approved`
- **THEN** the system accepts the transition and persists the new `review_status`

#### Scenario: Reviewer returns a governed lesson to draft
- **WHEN** an authorized reviewer changes a `reviewed` or `approved` lesson back to `draft`
- **THEN** the system accepts the transition so the lesson can be corrected and resubmitted

### Requirement: Reviewer identity is system-controlled
The system SHALL derive `reviewed_by` from the acting reviewer rather than accepting an arbitrary reviewer id from the client.

#### Scenario: Lesson is marked reviewed or approved
- **WHEN** an authorized reviewer transitions a lesson into `reviewed` or `approved`
- **THEN** the system sets `reviewed_by` to the acting user

#### Scenario: Lesson is returned to draft
- **WHEN** an authorized reviewer transitions a lesson back to `draft`
- **THEN** the system clears `reviewed_by`

### Requirement: Only reviewer-capable users can set governed review states
The system SHALL prevent non-reviewer lesson editors from setting `review_status` to `reviewed` or `approved` and from directly changing `reviewed_by`.

#### Scenario: Teacher attempts to mark a lesson reviewed
- **WHEN** a teacher without reviewer privileges submits a lesson update with `review_status` of `reviewed` or `approved`
- **THEN** the system rejects the update as unauthorized

#### Scenario: Client attempts to spoof reviewer identity
- **WHEN** a lesson create or update request includes a `reviewed_by` value that does not match the acting reviewer logic
- **THEN** the system ignores or rejects the supplied reviewer identity and preserves system-controlled reviewer assignment
