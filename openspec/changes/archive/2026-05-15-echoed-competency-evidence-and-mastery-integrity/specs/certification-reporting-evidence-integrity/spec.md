## ADDED Requirements

### Requirement: Certification meaning SHALL remain anchored to valid historical evidence
The system SHALL preserve the historical competency and assessment evidence context that supported an issued certification, even when later assessment revisions exist.

#### Scenario: Issued certification references superseded assessment evidence
- **WHEN** a learner already holds a certification supported by evidence from an older assessment revision
- **THEN** the certification SHALL remain historically interpretable from that original evidence context
- **AND** the system SHALL not silently rebase the certification onto a successor assessment revision

### Requirement: Reporting summaries SHALL not silently mix incompatible evidence
The system SHALL prevent reporting and mastery summaries from presenting incompatible revision evidence as if it were one continuous equivalent mastery signal.

#### Scenario: Reporting summary spans compatible and incompatible evidence
- **WHEN** a reporting consumer reads evidence across multiple assessment revisions
- **THEN** the system SHALL preserve explainable historical context and compatibility warnings where needed
- **AND** it SHALL not silently merge incompatible evidence into one unqualified mastery interpretation
