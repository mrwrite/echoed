## ADDED Requirements

### Requirement: Curriculum governance remains technically additive
The implementation SHALL preserve the existing content model, lesson governance authority where appropriate, assessment/mastery architecture, governed delivery, auth/session authority, and premium UX primitives.

#### Scenario: No parallel curriculum or learner-state engine is introduced
- **WHEN** curriculum governance evolves
- **THEN** the system MUST NOT introduce a separate curriculum database, parallel authoring engine, or new learner progression system

#### Scenario: Existing authority boundaries remain in force
- **WHEN** staff accesses curriculum authoring or governance behavior
- **THEN** current auth/session authority and educator/content-admin boundary rules SHALL remain the source of access control

#### Scenario: AI content generation stays out of scope
- **WHEN** curriculum governance is implemented
- **THEN** the system MUST NOT depend on AI-generated content workflows to satisfy governance requirements
