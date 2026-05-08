# governed-learning-state-machine Specification

## Purpose
TBD - created by archiving change echoed-governed-learning-delivery-hardening. Update Purpose after archive.
## Requirements
### Requirement: Governed instructional delivery uses explicit state domains
The system SHALL treat governed instructional delivery as a state model composed of distinct but related domains for lesson governance, learner eligibility, governed availability, progression eligibility, and educator visibility.

#### Scenario: Lesson exists in the curriculum hierarchy
- **WHEN** a lesson exists in the course and unit structure
- **THEN** the system does not assume that the lesson is learner-visible, progression-eligible, or deliverable without evaluating its governed instructional state

#### Scenario: Platform evaluates a learner delivery request
- **WHEN** the platform resolves whether a learner may access or progress through instructional content
- **THEN** it evaluates governed state domains explicitly rather than inferring eligibility from lesson existence alone

### Requirement: Lesson governance state is distinct from learner eligibility
The system SHALL define lesson governance state independently from learner eligibility state so that a lesson may exist for authoring, review, or educator planning without being valid for learner delivery.

#### Scenario: Draft lesson exists
- **WHEN** a lesson is in `draft`
- **THEN** the lesson remains valid for authoring visibility but is not learner-eligible and not progression-eligible

#### Scenario: Reviewed lesson exists
- **WHEN** a lesson is in `reviewed`
- **THEN** the lesson remains valid for reviewer and educator visibility but is not learner-eligible and not progression-eligible unless it later becomes approved and ready

#### Scenario: Approved lesson fails readiness
- **WHEN** a lesson is marked `approved` but fails academic readiness evaluation
- **THEN** the lesson is not learner-eligible and not progression-eligible even though its governance transition history exists

### Requirement: The governed learning state model defines canonical instructional states
The system SHALL recognize the following canonical state dimensions for governed instructional delivery.

#### Scenario: Governance state is evaluated
- **WHEN** the system evaluates a lesson's governance state
- **THEN** it classifies the lesson as one of `draft`, `reviewed`, or `approved`

#### Scenario: Learner eligibility is evaluated
- **WHEN** the system evaluates learner eligibility
- **THEN** it classifies the lesson as either `learner_ineligible` or `learner_eligible`

#### Scenario: Governed availability is evaluated
- **WHEN** the system evaluates whether governed learner delivery can occur
- **THEN** it classifies the delivery state as one of `available`, `pending_review`, `blocked_by_readiness`, `blocked_by_governance`, or `unavailable`

#### Scenario: Progression eligibility is evaluated
- **WHEN** the system evaluates whether progress records may attach to the lesson
- **THEN** it classifies the lesson as either `progression_ineligible` or `progression_eligible`

### Requirement: Learner eligibility is governance-authoritative
The system SHALL determine learner eligibility from governance-authoritative lesson state rather than from curriculum placement, direct route access, historical identifiers, or convenience fallback logic.

#### Scenario: Lesson appears in a unit
- **WHEN** a lesson appears in a unit that otherwise contains learner-visible content
- **THEN** the lesson is not learner-eligible unless it is approved and academically ready according to the governance-authoritative evaluation

#### Scenario: Learner requests a known lesson identifier
- **WHEN** a learner requests a lesson by id
- **THEN** the platform does not infer learner eligibility from the identifier alone and instead resolves the request through governance-authoritative learner eligibility rules

### Requirement: Governed availability is explicit and auditable
The system SHALL surface unavailable governed content through explicit governed availability outcomes rather than silent fallback to draft content, implicit substitution, or ambiguous completion behavior.

#### Scenario: No approved-ready lesson path exists
- **WHEN** no approved-ready governed lesson exists for the learner's requested instructional position
- **THEN** the platform returns an explicit unavailable governed state that can be audited later

#### Scenario: Learner encounters blocked content
- **WHEN** content is blocked by readiness or pending review
- **THEN** the system preserves an explicit governed availability reason rather than reporting the content as complete or silently delivering other content

### Requirement: Instructional identity remains deterministic
The system SHALL preserve deterministic instructional identity for learner delivery so that the lesson attached to a learner-facing instructional event is the same lesson the platform intends to deliver, track, report, and audit.

#### Scenario: Learner requests a draft lesson while an approved sibling exists
- **WHEN** the learner requests a draft lesson in a unit that also contains an approved-ready lesson
- **THEN** the system does not silently substitute instructional identity without an explicit governed contract for the delivered lesson path

#### Scenario: Learner resumes progression
- **WHEN** the learner resumes a governed instructional path
- **THEN** the next instructional identity is resolved deterministically from the canonical governed learner-visible sequence

### Requirement: Progression eligibility is stricter than lesson existence
The system SHALL only allow progression records to attach to governed learner-visible instructional content.

#### Scenario: Segment progress is about to be created
- **WHEN** the platform creates segment, lesson, or equivalent progression records
- **THEN** it attaches those records only to lessons that are both learner-visible and progression-eligible

#### Scenario: Unit contains mixed governance states
- **WHEN** a unit contains approved-ready and non-governed lessons
- **THEN** the system only creates progression records for the approved-ready learner-visible instructional path

### Requirement: Instructional lifecycle transitions are governed and explicit
The system SHALL define lifecycle transitions that move lessons between authoring, review, governed availability, and progression eligibility states in predictable ways.

#### Scenario: Draft becomes reviewed
- **WHEN** an authorized reviewer transitions a lesson from `draft` to `reviewed`
- **THEN** the lesson remains educator-visible but learner-ineligible and progression-ineligible

#### Scenario: Reviewed becomes approved and ready
- **WHEN** an authorized reviewer transitions a lesson into `approved` and the lesson satisfies readiness requirements
- **THEN** the lesson becomes learner-eligible, governed-available, and progression-eligible

#### Scenario: Approved lesson loses readiness or returns to draft
- **WHEN** a previously approved lesson is edited so that it fails readiness or is explicitly returned to `draft`
- **THEN** the lesson becomes learner-ineligible, governed-unavailable, and progression-ineligible for new governed delivery

### Requirement: Educator visibility is broader than learner visibility
The system SHALL preserve educator, reviewer, and author access to in-progress instructional content while maintaining strict learner visibility boundaries.

#### Scenario: Educator views a draft or reviewed lesson
- **WHEN** an educator with appropriate visibility views a draft or reviewed lesson
- **THEN** the system may expose governance metadata, instructional notes, and remediation context needed for authoring or review

#### Scenario: Learner views the same lesson state
- **WHEN** a learner attempts to view a draft or reviewed lesson
- **THEN** the lesson is not delivered as learner-visible instructional content

### Requirement: Learner visibility excludes governance ambiguity
The system SHALL ensure learner-facing instructional delivery does not expose ambiguous governance state, draft-state leakage, or unclear readiness semantics as part of normal learner instruction.

#### Scenario: Learner receives governed lesson payload
- **WHEN** a learner receives a lesson payload for normal instruction
- **THEN** the payload represents learner-visible governed content rather than governance-workflow ambiguity

#### Scenario: Learner encounters blocked instruction
- **WHEN** learner delivery is unavailable
- **THEN** the learner experience reflects explicit availability status without exposing educator-only governance details unless the institutional contract explicitly allows it

### Requirement: Progression invalidation is explicit and integrity-preserving
The system SHALL define how governed instructional changes affect existing or future progression records without silently corrupting learner history.

#### Scenario: Previously progression-eligible lesson becomes ineligible before new progress starts
- **WHEN** a lesson loses governed progression eligibility before a learner begins that lesson
- **THEN** no new progression records may attach to that lesson

#### Scenario: Previously progression-eligible lesson becomes ineligible after progress exists
- **WHEN** a learner already has progression records attached to a lesson that later becomes governance-ineligible
- **THEN** the platform preserves historical auditability while preventing the lesson from serving as a normal future governed progression target without an explicit remediation rule

### Requirement: Governance transition expectations are auditable
The system SHALL preserve governance transition expectations so institutions can reconstruct why a lesson was or was not learner-eligible at a given point in time.

#### Scenario: Institution audits a delivery decision
- **WHEN** an institution audits why a learner could or could not access a lesson
- **THEN** the platform can explain the relationship between governance state, readiness, availability state, and progression eligibility

#### Scenario: Reviewer approves a lesson
- **WHEN** a reviewer transitions a lesson into an approved-ready governed state
- **THEN** the resulting learner-eligibility and progression-eligibility implications are deterministic and reviewable

### Requirement: Edge-case behavior is defined by governed state, not convenience fallback
The system SHALL resolve edge cases by governed state evaluation rather than route-local convenience behavior.

#### Scenario: Unit contains no governed learner-visible lessons
- **WHEN** a learner starts or resumes a unit with no progression-eligible lessons
- **THEN** the platform returns an explicit governed unavailable state rather than constructing empty progress or silently marking the path complete

#### Scenario: Lesson exists but unit ordering changes
- **WHEN** lesson ordering or unit composition changes
- **THEN** learner instructional identity and progression eligibility are re-evaluated through the canonical governed sequence rather than by unstable incidental ordering alone

#### Scenario: Multiple approved lessons exist in the same instructional position
- **WHEN** the platform must resolve among multiple candidate learner-visible lessons
- **THEN** it uses a deterministic canonical ordering rule that can be documented and audited

### Requirement: Progression integrity supports institutional reporting
The system SHALL maintain governed progression integrity so downstream analytics, mastery systems, reporting, certification, and transcript-ready records can trust learner instructional history.

#### Scenario: Analytics consume progression data
- **WHEN** analytics or mastery systems summarize learner performance
- **THEN** they may rely on progression records as evidence of governed learner-visible instruction rather than draft instructional artifacts

#### Scenario: Institution exports learner records
- **WHEN** institutional reporting, certification, or future transcript systems consume learner progression data
- **THEN** the records reflect governed instructional participation that is explicit, auditable, and deterministic

