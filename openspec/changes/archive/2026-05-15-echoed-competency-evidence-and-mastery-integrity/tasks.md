## 1. Competency evidence anchoring

- [x] 1.1 Define bounded competency-evidence anchoring semantics for assessment attempts, attempt events, competency alignments, and mastery summaries.
- [x] 1.2 Add additive backend helpers or provenance structures needed to trace mastery interpretation back to authoritative historical evidence.
- [x] 1.3 Ensure historical evidence remains read-only and is never silently reassigned to successor assessment revisions.

## 2. Assessment revision compatibility and mastery safety

- [ ] 2.1 Define compatible, cautionary, and incompatible assessment revision semantics for mastery, certification, and reporting interpretation.
- [x] 2.2 Add read-only mastery-integrity validation for deprecated, archived, superseded, or successor-linked assessment evidence.
- [x] 2.3 Detect ambiguous mastery interpretation when competency alignment, revision metadata, or historical context is insufficient or unsafe.

## 3. Runtime support and staff visibility alignment

- [ ] 3.1 Ensure remediation and enrichment guidance uses only valid and explicitly safe mastery evidence.
- [x] 3.2 Expose competency-evidence integrity and ambiguous mastery warnings to authorized staff/admin surfaces without adding mutation controls.
- [x] 3.3 Preserve learner-facing delivery, continuation guidance determinism, and staff/learner visibility boundaries.

## 4. Certification, reporting, and verification

- [ ] 4.1 Preserve issued certification and historical reporting meaning when evidence spans deprecated, superseded, or incompatible assessment revisions.
- [x] 4.2 Add focused regression coverage for evidence traceability, incompatible revision warnings, runtime support guardrails, staff visibility, and read-only behavior.
- [x] 4.3 Verify that scoring, certification, reporting, and governed progression semantics remain unchanged unless an explicit safe integrity rule applies.

## Follow-Ups

- [ ] Define compatible, cautionary, and incompatible assessment revision semantics
- [ ] Ensure remediation and enrichment guidance uses only explicitly safe mastery evidence
- [ ] Add certification-to-evidence lineage if certification evidence becomes first-class
- [ ] Add richer historical competency alignment snapshots/provenance
- [ ] Add batching/combined governance payload for staff course governance checks
- [ ] Normalize duplicated or overlapping backend issue warnings for staff UI
- [ ] Add route/integration-level learner non-exposure tests
- [ ] Clean up noisy student-view error-path console logs