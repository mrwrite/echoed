## 1. Smoke Harness Setup

- [x] 1.1 Add a bounded Playwright smoke test entrypoint for the seeded demo environment
- [x] 1.2 Add shared browser helpers for login, flagship course discovery, and deterministic waiting
- [x] 1.3 Configure clear smoke-oriented failure output and bounded retry behavior

## 2. Student Flagship Smoke

- [x] 2.1 Add student smoke coverage for demo login and dashboard readiness
- [x] 2.2 Add smoke coverage for starting or continuing the flagship course from the dashboard
- [ ] 2.3 Add smoke coverage for lesson view, progression rendering, and assessment loading
- [x] 2.4 Verify the governed learner path remains functional without adding test-only shortcuts

## 3. Staff Flagship Smoke

- [ ] 3.1 Add teacher smoke coverage for dashboard readiness and flagship course visibility
- [ ] 3.2 Add teacher smoke coverage for governance summary, runtime intervention recommendations, and runtime support sections
- [ ] 3.3 Add admin smoke coverage for governance section rendering, publish readiness, safe publish, and competency integrity
- [ ] 3.4 Verify learner and staff auth/session separation remains production-aligned in the smoke flow

## 4. Operational Demo Confidence

- [x] 4.1 Add a demo smoke runbook describing prerequisites, execution, and failure interpretation
- [ ] 4.2 Verify the smoke layer remains bounded, deterministic where practical, and demo-safe in runtime
- [x] 4.3 Document explicit non-goals so the smoke layer does not grow into a full E2E suite
