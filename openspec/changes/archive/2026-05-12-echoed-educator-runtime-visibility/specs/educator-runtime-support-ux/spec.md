## ADDED Requirements

### Requirement: Educator runtime support uses bounded premium UX patterns
Educator runtime support visibility SHALL use existing premium UX primitives and bounded support-state summaries so the experience stays readable and operationally consistent.

#### Scenario: Educator sees support-state summaries
- **WHEN** learner runtime support visibility is shown
- **THEN** the educator surface SHALL present support states through understandable summaries such as cards, badges, or lightweight grouped rows

#### Scenario: Support-state rendering uses canonical failure handling
- **WHEN** educator runtime support data fails to load
- **THEN** the surface SHALL render canonical error and retry treatment using the existing UX state system

#### Scenario: Support language remains culturally affirming and learner-safe
- **WHEN** educator runtime support copy references learner struggle or strong mastery
- **THEN** the language SHALL remain confidence-preserving, culturally affirming, and free of shaming or manipulative framing
