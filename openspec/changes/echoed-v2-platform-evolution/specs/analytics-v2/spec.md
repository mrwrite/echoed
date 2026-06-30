# analytics-v2 Specification

## ADDED Requirements

### Requirement: Analytics V2 SHALL report on products, sources, artifacts, reviews, and learners
EchoEd SHALL add analytics organized around the V2 platform lifecycle.

Analytics V2 SHALL support:

- product engagement
- learner progress
- source coverage
- artifact generation and review activity
- review cycle time
- product completion
- assessment outcomes
- certificate issuance

#### Scenario: Creator opens product analytics
- **WHEN** a creator opens analytics for a product
- **THEN** EchoEd shows learner progress, completion, review state, source coverage, and related artifact activity where available

#### Acceptance Criteria
- Existing progress, assessment, and certification analytics are reused.
- Missing V2 event data is represented as unavailable rather than fabricated.
- Analytics do not mutate runtime data.

### Requirement: Analytics events SHALL support continuous improvement
EchoEd SHALL track platform events needed to identify stale knowledge, low-completion products, review bottlenecks, and source coverage gaps.

#### Scenario: Source-backed product has weak source coverage
- **WHEN** a product uses generated or source-backed content with incomplete source coverage
- **THEN** Analytics V2 can surface a source coverage warning for creators

#### Acceptance Criteria
- Source coverage signals are advisory unless governance rules require blocking.
- Analytics can reference knowledge sources, artifacts, products, and lessons.

## MODIFIED Requirements

### Requirement: Existing analytics SHALL remain compatible
Existing analytics routes and reporting behavior SHALL remain available while V2 analytics is added.

#### Scenario: Current educator dashboard loads analytics
- **WHEN** an existing dashboard requests current analytics data
- **THEN** EchoEd returns the same supported response shape

#### Acceptance Criteria
- Current analytics tests remain valid.
- V2 analytics is additive.

