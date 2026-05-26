## ADDED Requirements

### Requirement: Learner authenticated entry preserves continuity
The platform SHALL preserve learner continuity across dashboard entry, continue-learning, and return-to-session flows using authoritative session and governed learning state.

#### Scenario: Learner returns to the platform
- **WHEN** a learner opens the authenticated experience after a prior session
- **THEN** the dashboard and continue-learning entry reflect the authoritative current learning state without contradictory or stale route-local cues

#### Scenario: Learner resumes governed delivery on mobile
- **WHEN** a learner continues learning from a mobile device
- **THEN** the platform preserves continuity and does not force a desktop-only navigation pattern

### Requirement: Lesson and assessment delivery minimize cognitive overhead
The platform SHALL present lesson and assessment experiences with clear pacing, focus, and progression cues that reduce cognitive overload while preserving governed delivery and assessment integrity.

#### Scenario: Learner enters a lesson
- **WHEN** a learner opens a governed lesson
- **THEN** the view emphasizes active learning context, progression clarity, and accessible navigation rather than competing operational chrome

#### Scenario: Learner enters an assessment
- **WHEN** a learner opens an available assessment
- **THEN** the assessment experience preserves immersion, feedback clarity, and attempt-state awareness without exposing unrelated operational distractions

### Requirement: Learner-facing responsive and accessibility behavior is first-class
The platform SHALL preserve learner usability across mobile, tablet, keyboard, and assistive-technology contexts.

#### Scenario: Learner navigates without a pointer device
- **WHEN** a learner uses keyboard or assistive navigation
- **THEN** the authenticated learner flow remains operable and comprehensible

#### Scenario: Learner uses a small-screen device
- **WHEN** learner-facing content is viewed on a narrow viewport
- **THEN** the layout preserves readability, primary actions, and progression clarity without horizontal overflow or hidden critical controls
