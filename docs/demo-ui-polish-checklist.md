# Demo UI Polish Checklist

This checklist captures the highest-impact visual and UX issues that can undermine a confident live EchoEd demo. It is intentionally bounded to polish planning for the flagship `Introduction to Africa` story and does not propose backend, governance, scoring, auth, or seed-data changes.

## Must Fix Before Demo

| Affected screen/component | Issue | User impact | Recommended fix | Risk / complexity | Suggested test coverage |
| --- | --- | --- | --- | --- | --- |
| `student-view.component.html` | Visible mojibake and encoding artifacts in learner-facing copy, including `Hereâ€™s`, `Kâ€“5 Demo`, and the streak emoji rendering. | Immediately makes the product feel unstable or low-trust during the first student-dashboard impression. | Normalize all affected strings to plain UTF-8 or ASCII-safe copy. Remove any decorative emoji that renders inconsistently. | Low | Update existing student dashboard spec to assert corrected text and absence of malformed copy tokens. |
| `teacher-view.component.html`, `admin-view.component.html` | Staff demo surfaces expose destructive or off-script controls (`Delete`, `+ Add Course`, `Assign Course`, `Start Live Lesson`) adjacent to the flagship read-only story. | Presenter can easily drift into risky actions or trigger off-script states during a live demo. | For demo polish phase, visually de-emphasize or temporarily hide nonessential destructive/action-heavy controls on dashboard surfaces used in the canned demo path. Preserve routes and backend behavior. | Medium | Focused teacher/admin specs asserting demo surfaces keep governance/runtime sections visible and suppress or restyle nonessential actions. |
| `admin-view.component.html` | Demo-breaking stale content in `Announcements` (`Apr 7, 2024`, summit, web development) does not match EchoEd’s current flagship narrative. | Creates immediate credibility drift because the content looks old and unrelated to the flagship course. | Replace with timeless demo-safe institutional copy aligned to the current flagship presentation, or hide the block if no real data source exists. | Low | Simple admin-view spec checking for updated demo-safe announcement copy or absence of the stale block. |
| `teacher-view.component.html` | Two separate intervention-oriented areas (`Runtime intervention recommendations` and `Runtime Support`) present overlapping concepts without clear differentiation. | Presenter has to explain internal distinctions instead of telling a clean teacher story. | Tighten labels and helper copy so one section is clearly course-level recommendation detail and the other is quick flagship support visibility. Keep existing data and layout structure. | Low to medium | Teacher-view spec asserting revised headings/body copy and preserved section rendering. |

## Should Fix Before Demo

| Affected screen/component | Issue | User impact | Recommended fix | Risk / complexity | Suggested test coverage |
| --- | --- | --- | --- | --- | --- |
| `student-view.component.html` | Hero copy is polished but generic (`beautiful overview`) and slightly more promotional than instructional. | Makes the learner experience sound templated rather than grounded in the flagship course story. | Rewrite hero/supporting copy to emphasize governed continuation, progress, and confidence-building. | Low | Student-view spec for revised copy only. |
| `lesson-viewer.component.html` | The lesson page presents strong structure, but activity transitions and completion CTA hierarchy are visually plain compared with the dashboard entry state. | The live demo loses some momentum when moving from dashboard polish into the core lesson experience. | Improve CTA emphasis, activity progress affordances, and spacing consistency without altering lesson behavior. | Medium | Lesson viewer spec for activity navigation button labels and governed completion state still rendering correctly. |
| `assessment-detail.component.html` | Assessment result state is functionally clear, but the page does not strongly guide the presenter or learner to the next step after pass/fail. | The assessment story can feel abrupt at the moment that should reinforce mastery or retry guidance. | Tighten pass/fail copy and add clearer next-step framing using existing result data and navigation. | Low to medium | Assessment detail spec for result copy and action text. |
| `teacher-view.component.html`, `admin-view.component.html` | Governance cards are information-rich but visually dense when several sections expand at once. | Staff demo can feel like reading raw audit output instead of a polished decision surface. | Add bounded spacing, summary emphasis, and stronger visual grouping around status, counts, and issues without changing payloads. | Medium | Component specs for grouped section rendering; optional visual review checklist. |
| `student-view.component.html`, `teacher-view.component.html`, `admin-view.component.html` | Some empty/error states are clear, but adjacent successful sections can make the page feel visually inconsistent when one slice errors. | Partial failures may look rough in a live environment, even if they are recoverable. | Harmonize body copy length and retry affordances so mixed-state pages still look intentional. | Low | Existing loading/error specs extended for copy consistency. |

## Nice To Have

| Affected screen/component | Issue | User impact | Recommended fix | Risk / complexity | Suggested test coverage |
| --- | --- | --- | --- | --- | --- |
| `student-view.component.html` | Dashboard sections such as `What’s next`, certifications, and badges feel useful but slightly crowded in one viewport. | Lowers visual calm on smaller laptop screens. | Reduce visual competition with spacing and slightly clearer section hierarchy. | Low | Manual responsive QA at common laptop widths. |
| `lesson-view.component.html` | The lesson shell is functional, but the transition between dashboard and immersive lesson could feel more theatrical for demos. | Mildly reduces perceived polish. | Add subtle presentation polish in a later phase, such as improved header treatment or transition affordances, without changing lesson semantics. | Medium | Manual visual QA only. |
| `assessment-detail.component.html` | Question cards are readable, but the answer-choice styling is conservative. | Assessment flow feels more utilitarian than premium. | Refine choice-card styling and result badges after must-fix items are done. | Low | Assessment detail visual regression review. |

## Defer

| Affected screen/component | Issue | User impact | Recommended fix | Risk / complexity | Suggested test coverage |
| --- | --- | --- | --- | --- | --- |
| All dashboard surfaces | Broader layout redesign or major information architecture cleanup. | Could improve aesthetics, but not necessary for the current flagship demo. | Defer until after live-demo readiness work. | High | Full component/regression sweep if ever pursued. |
| Governance sections | New governance visualizations or condensed analytics widgets. | Helpful long term, but outside this bounded polish pass. | Defer; keep current read-only sections and focus on clarity, not new features. | High | N/A for this change. |
| Mobile-first redesign | Deeper small-screen reflow beyond current responsive table/card fallbacks. | Mobile basics are already present; this is not the highest-value live-demo investment. | Defer unless mobile becomes a primary presentation target. | Medium to high | Manual mobile smoke later. |

## Phase 5 Plan

Phase 5 should implement only the `Must Fix Before Demo` items above.

1. Fix malformed or mojibake copy in student and staff demo-facing text.
2. Replace or suppress stale/off-script dashboard content that undermines the flagship story, starting with admin announcements.
3. Reduce accidental-demo-risk controls on teacher/admin dashboard entry surfaces by hiding, demoting, or clearly separating destructive/off-script actions.
4. Clarify the teacher runtime story by tightening the labels and helper copy that currently split `Runtime intervention recommendations` and `Runtime Support`.

## Recommended Phase 5 Verification

- Student dashboard specs for corrected hero text and clean learner copy.
- Teacher/admin dashboard specs for preserved governance/runtime rendering with updated labels and safer action presentation.
- Manual desktop checks for:
  - student dashboard first impression
  - lesson launch from student dashboard
  - assessment pass/fail result readability
  - teacher runtime story
  - admin governance story
- Manual responsive spot checks at common laptop and tablet widths.
