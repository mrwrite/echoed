## ADDED Requirements

### Requirement: Certifications SHALL remain valid across curriculum revision changes
The system SHALL preserve issued certifications and the curriculum context that supported them, even when course, lesson, or assessment revisions later gain successors or become deprecated.

#### Scenario: Certified learner has evidence tied to older course revision
- **WHEN** a learner already holds a certification supported by historical curriculum and assessment evidence
- **THEN** the certification SHALL remain valid and historically interpretable
- **AND** later curriculum revisions SHALL not retroactively corrupt the credential record

### Requirement: Reporting summaries SHALL remain historically interpretable
The system SHALL preserve course, unit, lesson, and assessment titles and metadata needed to interpret historical reporting summaries across revision changes.

#### Scenario: Reporting reads historical completion after course revision changes
- **WHEN** a reporting summary includes completions or evidence tied to superseded curriculum
- **THEN** the reporting output SHALL retain enough historical curriculum context to remain understandable
- **AND** successor context MAY be shown as additive metadata without rewriting the historical result
