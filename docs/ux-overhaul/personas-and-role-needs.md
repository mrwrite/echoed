# Personas and Role Needs

## Student

Status: implemented.

- Responsibilities: sign in, find assigned learning, complete lessons/activities, track progress, view achievements, recover when interrupted.
- Top goals: know what to do next, feel safe and capable, complete a lesson without losing progress.
- Daily workflows: resume learning, finish a lesson, answer assessment questions, view progress and badges.
- Critical workflows: recover stale session, understand unavailable lesson, retry failed submit, ask for support through teacher/community channels when available.
- Technical comfort: mixed; K-5 learners may need low reading burden and clear visual hierarchy.
- Accessibility considerations: large targets, readable type, reduced cognitive load, audio/visual alternatives, clear focus.
- Information priorities: next lesson, why it matters, time/progress, support state, achievements.
- Dashboard priorities: primary "Continue learning", assigned work, progress, achievements, resources.
- Navigation: Learn, Assignments, Courses, Progress, Achievements, Discussions, Profile.
- Notifications: new assignment, feedback, badge earned, lesson unlocked/paused, teacher message.
- Dangerous/confusing actions: enrolling in duplicate courses, leaving lesson before save, assessment submit.
- Cross-role handoffs: teacher assigns/supports; admin/content controls availability; discussion moderation protects learners.

## Teacher / Educator

Status: implemented.

- Responsibilities: orient to class priorities, manage classes/rosters, assign curriculum, monitor completion, provide support and feedback.
- Top goals: know which learners need help, assign the right lesson, see progress quickly.
- Daily workflows: check class dashboard, open class, review learners needing support, assign/resume lessons, review submissions.
- Critical workflows: create class, enroll learner, handle blocked lesson, interpret runtime recommendations, recover from failed assignment.
- Technical comfort: moderate; needs low-friction classroom operations.
- Accessibility considerations: keyboard table navigation, readable dense data, status not color-only.
- Information priorities: active classes, overdue/unstarted work, intervention recommendations, recent submissions.
- Dashboard priorities: today, learners needing support, upcoming lessons, assignment status.
- Navigation: Teach, Classes, Assignments, Curriculum, Progress, Discussions, Settings.
- Notifications: submitted work, learners needing reteach/review/enrichment, discussion flags, roster changes.
- Dangerous/confusing actions: deleting course, assigning wrong cohort, starting unavailable lesson.
- Cross-role handoffs: students complete work; content admins publish/approve curriculum; admins manage users/org.

## Administrator

Status: implemented.

- Responsibilities: manage users, roles, courses, badges, organizations, reports, destructive actions.
- Top goals: maintain platform health, resolve access problems, preserve data integrity.
- Daily workflows: review metrics, manage users, inspect course readiness, resolve access/role issues.
- Critical workflows: delete/deactivate user, manage roles, review content governance, handle moderation.
- Technical comfort: moderate to high.
- Accessibility considerations: dense admin tables, confirmation clarity, keyboard filters/actions.
- Information priorities: system health, pending risks, user/course counts, governance issues.
- Dashboard priorities: alerts, recent activity, users, courses, governance checks.
- Navigation: Admin, Users, Organizations, Curriculum, Reports, Moderation, Assets, Settings.
- Notifications: failed org access, content blocked, user invite issue, flagged content, safe-publish failure.
- Dangerous/confusing actions: delete user/course, revoke access, publish unsafe content.
- Cross-role handoffs: supports teachers/content admins; manages org admins; protects learners.

## Organization Administrator

Status: implemented.

- Responsibilities: invite members, manage organization context, oversee sections/classes, access grants.
- Top goals: keep the organization roster and permissions accurate.
- Daily workflows: manage invites, review sections/cohorts, handle access.
- Critical workflows: revoke/adjust membership, switch org, manage content admin access.
- Navigation: Organization, People, Classes, Access, Settings.

## Content Admin / Curriculum Creator

Status: implemented.

- Responsibilities: author courses/products, manage sources/artifacts, review/publish content.
- Top goals: move content from source to reviewed learner-ready product.
- Daily workflows: open Studio, review queue, inspect products/artifacts, publish approved material.
- Critical workflows: safe publish, review status changes, source provenance, version management.
- Navigation: Studio, Projects, Sources, Artifacts, Review, Products, Analytics.

## Instructor

Status: partially implemented.

- Responsibilities: manage sections/cohorts and support learners.
- Gap: no dedicated instructor-specific dashboard or route labels.

## Parent / Guardian

Status: partially implemented.

- Evidence: backend `OrganizationRole.PARENT`; registration exposes `parent` and family org intent.
- Gap: no parent portal, child linking, progress visibility, or messaging.
- Recommendation: future Family Portal only after backend child relationship/access contracts are defined.

## Super Administrator

Status: partially implemented.

- Evidence: backend super admin bypass and V2 creator role.
- Gap: frontend route constants omit super_admin from creator roles.
- Recommendation: align frontend route access after deciding if super admin should use Admin or internal Ops IA.
