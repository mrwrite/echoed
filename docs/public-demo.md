# EchoEd Public Demo Guide

Use this guide to evaluate the public EchoEd demo.

Live app: https://echoed-theta.vercel.app/

## Before You Start

The demo is shared and resettable. Do not enter personal, student, school, or production data.

The demo is useful for:
- Seeing the current K-5 learning experience.
- Reviewing student, teacher, and admin flows.
- Giving educator, curriculum, accessibility, or product feedback.
- Understanding where developers can contribute.

The demo is not:
- A production school environment.
- A private workspace.
- A place to store real learner information.
- A complete statement of historical or classroom readiness.

## Demo Credentials

These accounts are shared, demo-only, and may be reset.

| Role | Username | Password | What to Review |
| --- | --- | --- | --- |
| Student | `normalstudent` | `password` | Learner dashboard, course access, lesson flow |
| Teacher | `teacher` | `password` | Educator dashboard and learner visibility |
| Admin | `orgadmin` | `password` | Organization-level surfaces |
| Content admin | `contentadmin` | `password` | Workspace and content/admin surfaces |

Additional deterministic learner states may exist for internal review:

| Username | Password | Expected State |
| --- | --- | --- |
| `masteredstudent` | `password` | Enrichment |
| `reteachstudent` | `password` | Reteach |
| `reviewstudent` | `password` | Review |
| `monitorstudent` | `password` | Monitor |

## Suggested Educator Walkthrough

1. Open https://echoed-theta.vercel.app/.
2. Select `Try demo`.
3. Sign in as `normalstudent`.
4. Review the student dashboard, course access, lesson entry, activity flow, language, age fit, and clarity.
5. Sign out and sign in as `teacher`.
6. Review whether the teacher view gives enough context to support learners.
7. File feedback using the educator/curriculum feedback issue template.

Useful educator feedback:
- Grade or learner context.
- What felt useful.
- What felt unclear or inaccessible.
- Historical, cultural, or source concerns.
- Suggested discussion prompts or classroom supports.
- What would be required before classroom use.

## Suggested Developer Walkthrough

1. Open the live app and try the student flow.
2. Read [../ARCHITECTURE.md](../ARCHITECTURE.md).
3. Read [../CONTRIBUTING.md](../CONTRIBUTING.md).
4. Run the app locally if you want to contribute.
5. File setup friction, accessibility, docs, frontend, backend, or testing issues.

## Suggested Community Organizer Walkthrough

1. Read the landing page and README.
2. Try the student demo.
3. Review [community-trust.md](community-trust.md).
4. Note what would make the project easier to share with educators, HBCUs, homeschool groups, or developer networks.
5. Use GitHub issues or `support@echoed.com` for introductions or feedback.

## Feedback Paths

- Bugs: GitHub bug report template.
- Educator review: educator/curriculum feedback template.
- Historical accuracy or source concern: historical accuracy issue template.
- Accessibility concern: accessibility issue template.
- Security concern: [../SECURITY.md](../SECURITY.md).
- General contact: `support@echoed.com`.

## Known Limitations

- The project is early and pre-community-launch.
- Demo data is shared and may change.
- The public app is temporarily hosted at `echoed-theta.vercel.app`.
- AI generation, payments, marketplace, subscriptions, and production onboarding are not Phase 1 goals.
- Some internal demo operation details live in [demo-readiness.md](demo-readiness.md) and are intended for maintainers.
