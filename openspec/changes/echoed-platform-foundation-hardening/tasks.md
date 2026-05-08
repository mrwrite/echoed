# Tasks

## 1. Change Setup

- [ ] Review `echoed-global-education-platform-evaluation` artifacts and confirm this change remains a foundation-hardening implementation initiative aligned to the institutional roadmap
- [ ] Confirm the implementation scope stays focused on reliability, consistency, maintainability, UX stability, governance consistency, and operational readiness
- [ ] Avoid introducing parallel auth, onboarding, lesson, progress, governance, or classroom systems while implementing this change

---

## 2. Authentication & Session Reliability

- [ ] Audit login, token persistence, first authenticated load, and role bootstrap behavior across frontend and backend
- [ ] Consolidate post-auth session bootstrap into a deterministic sequence
- [ ] Normalize active organization hydration and permissions refresh after login or refresh
- [ ] Eliminate inconsistent routing outcomes between login, guarded routes, and first-load hydration
- [ ] Validate auth/session behavior for student, teacher, admin, and organization-aware user contexts

---

## 3. Organization & Onboarding Stability

- [ ] Centralize onboarding-required decision logic
- [ ] Normalize personal-org versus institutional-org handling across registration, login, guards, and onboarding
- [ ] Harden onboarding redirect consistency for all non-super-admin user states that require setup
- [ ] Ensure active organization context is stable after onboarding completion and org switching
- [ ] Remove duplicated org-bootstrap logic where equivalent behavior is being reimplemented

---

## 4. Lesson Delivery Reliability

- [ ] Audit lesson visibility behavior across lesson, course, learner, and teacher delivery paths
- [ ] Ensure approved-ready filtering remains deterministic in all learner-facing delivery contexts
- [ ] Normalize governance filtering behavior across nested and direct curriculum responses
- [ ] Harden lesson loading and progress persistence across refresh and transition flows
- [ ] Validate learner-mode and teacher-mode rendering consistency for governed lessons

---

## 5. Shell & Navigation Stability

- [ ] Stabilize sidebar width, layout offsets, and responsive shell behavior
- [ ] Eliminate first-paint shell instability caused by async navigation or permission resolution
- [ ] Normalize route transition loading states across major role-aware surfaces
- [ ] Improve dashboard rendering consistency for student, teacher, and admin experiences
- [ ] Ensure navigation loading states do not obscure or displace primary content unexpectedly

---

## 6. API & Data Consistency

- [ ] Audit DTO and serializer behavior across lesson, course, org, progress, assignment, and analytics APIs
- [ ] Normalize UUID serialization and equivalent domain-shape behavior where drift exists
- [ ] Normalize error response behavior for common auth, org, and governance failures
- [ ] Remove route-level governance duplication where shared enforcement helpers should own the decision
- [ ] Clean inconsistent response-shaping logic that forces frontend compensation behavior

---

## 7. Demo & Seed Reliability

- [ ] Make demo seeding idempotent
- [ ] Verify demo accounts are reliable and role-appropriate
- [ ] Guarantee demo enrollments, sections, and org context are reproducible
- [ ] Ensure learner-facing demo lessons are approved and ready where delivery expects them
- [ ] Validate demo organization and role flows after reseed and fresh startup

---

## 8. Test Infrastructure Hardening

- [ ] Expand backend integration coverage for auth, onboarding, org switching, governance, lessons, assignments, sessions, and progress
- [ ] Expand frontend coverage for shell stability, onboarding flows, role-aware dashboards, and lesson rendering
- [ ] Add governance edge-case coverage around approved-ready behavior and role visibility
- [ ] Add seeded environment verification tests or equivalent validation harnesses
- [ ] Ensure the most fragile foundation flows have regression protection before broader institutional work continues

---

## 9. UX Stability Improvements

- [ ] Normalize loading-state behavior across onboarding, dashboard, lesson, and section surfaces
- [ ] Improve empty-state handling so missing content states remain intentional and readable
- [ ] Fix contrast and accessibility issues that undermine platform trust
- [ ] Improve responsive behavior in the shared shell and other critical role-aware views
- [ ] Clarify learner-mode behavior so student-facing experiences remain focused and calm

---

## 10. Architectural Hardening

- [ ] Remove duplicated onboarding, org-state, and governance decision logic
- [ ] Centralize canonical ownership for auth bootstrap, org context, and lesson visibility decisions
- [ ] Reduce fragile cross-route dependencies where correctness depends on duplicated rule interpretation
- [ ] Improve maintainability by moving repeated logic into shared helpers, serializers, or route-ownership layers
- [ ] Document or codify the canonical foundation decisions that future institutional work must build on

---

## 11. Validation & Readiness

- [ ] Verify this change improves platform reliability without broad rewrites
- [ ] Verify the hardening work keeps EchoEd aligned with:
  - `echoed-global-education-platform-evaluation`
  - `institutional-learning-platform`
  - `premium-global-learning-experience`
  - `assessment-and-reporting-system`
  - `educator-operating-system`
  - `ai-assisted-learning-and-tutoring`
- [ ] Confirm the result leaves EchoEd more maintainable, more deterministic, and more institutionally dependable for the next phases of expansion
