## 1. Baseline Audit and Decisions

- [x] 1.1 Record the current repository readiness gaps: stale README links, missing community files, empty issue template folder, missing PR template, demo credential exposure, and missing contributor onboarding.
- [x] 1.2 Confirm the public project facts to publish: live app URL, GitHub URL, temporary hosting status, project stage, current maintainer contact, and current demo availability.
- [x] 1.3 Decide where public demo credentials will live: README, dedicated demo guide, landing page, or request-only flow.
- [x] 1.4 Decide the initial community contact path and replace any placeholder contact or social links.

## 2. Repository Readiness

- [x] 2.1 Rewrite `README.md` with mission, current status, live app, demo path, educator path, developer path, community path, project structure, setup summary, testing summary, license, and contact information.
- [x] 2.2 Remove placeholder GitHub URLs, stale hosting references, and mojibake/encoding artifacts from the README.
- [x] 2.3 Verify `LICENSE` is MIT and referenced accurately from README and contribution docs.
- [x] 2.4 Add `ROADMAP.md` with practical near-term milestones, including Phase 1 readiness, early educator review, contributor onboarding, and later product/runtime priorities.
- [x] 2.5 Add `ARCHITECTURE.md` summarizing frontend, backend, database, migrations, demo seed, OpenSpec workflow, and key code ownership boundaries.
- [x] 2.6 Add `SECURITY.md` with vulnerability reporting, supported scope, demo credential cautions, and sensitive-data handling expectations.

## 3. Contributor Onboarding

- [x] 3.1 Add `CONTRIBUTING.md` with first contribution workflow, local frontend setup, local backend setup, environment variables, migrations, seed/demo data, testing commands, and PR expectations.
- [x] 3.2 Document how contributors should report tests they could not run.
- [x] 3.3 Add first-contribution guidance for documentation, educator review, frontend, backend, tests, accessibility, and curriculum tooling.
- [x] 3.4 Add communication guidelines covering respectful discussion, review expectations, maintainer response limitations, and no-budget project stage.
- [x] 3.5 Add good-first-issue guidance with example issue shapes and acceptance criteria for small starter tasks.

## 4. GitHub Community Surfaces

- [x] 4.1 Add issue templates for bug report, feature request, educator/curriculum feedback, historical accuracy or source concern, accessibility issue, and good-first-issue proposal.
- [x] 4.2 Add `.github/pull_request_template.md` with summary, motivation, test plan, screenshots when relevant, accessibility check, and community/curriculum impact check.
- [x] 4.3 Add a labels recommendation document covering `good first issue`, `help wanted`, `educator feedback`, `historical accuracy`, `accessibility`, `documentation`, `frontend`, `backend`, `testing`, `demo`, `curriculum`, `question`, `blocked`, and priority labels.
- [x] 4.4 Add a GitHub Discussions recommendation with suggested categories for introductions, Q&A, educator feedback, contributor help, roadmap, and show-and-tell.

## 5. Landing and Demo Readiness

- [x] 5.1 Review the landing page against the Phase 1 mission and ensure it clearly routes visitors to educator, developer, demo, and community contribution paths.
- [x] 5.2 Add public demo instructions that explain demo roles, access steps, safe use, reset expectations, limitations, and feedback paths.
- [x] 5.3 Ensure demo credential handling is clearly marked as demo-only and excludes personal, student, school, or production data.
- [x] 5.4 Add screenshot or walkthrough guidance for educators, developers, and community organizers evaluating the K-5 demo.
- [x] 5.5 Link the README, landing page, demo guidance, and GitHub contribution paths consistently.

## 6. Community Trust Process

- [x] 6.1 Add `CODE_OF_CONDUCT.md` with inclusive, respectful participation expectations and enforcement contact guidance.
- [x] 6.2 Add non-extractive language guidance for educator asks, including bounded review requests and transparency about the no-budget stage.
- [x] 6.3 Document the educator review process, including what to review, how to submit feedback, how feedback is triaged, and how reviewers can be recognized.
- [x] 6.4 Document the historical accuracy review process for source concerns, framing concerns, curriculum corrections, and resolution tracking.
- [x] 6.5 Document contributor recognition options and the advisory circle concept without implying a formal board already exists.
- [x] 6.6 Document accessibility and inclusion expectations for docs, UI, demo flows, and learning content.

## 7. Outreach Readiness

- [x] 7.1 Create a minimum viable public-facing checklist that must pass before outreach begins.
- [x] 7.2 Define what must be complete before contacting educators, HBCUs, developer groups, homeschool groups, and community organizers.
- [x] 7.3 Add recommended first outreach targets after Phase 1, grouped by Black educator networks, African-American studies educators, HBCU education and CS programs, Black software developer communities, homeschool/community learning groups, and Africa or Caribbean education technology contacts.
- [x] 7.4 Add a simple outreach tracking structure with fields for person or organization, contact, region, audience, channel, status, next step, owner, and outcome.

## 8. Validation

- [x] 8.1 Run `openspec validate prepare-open-source-community-launch --strict`.
- [x] 8.2 Review all new Markdown files for broken relative links, placeholder links, stale project facts, and unreadable encoding artifacts.
- [x] 8.3 Run the frontend build if landing copy or routing changes are made.
- [x] 8.4 Run targeted demo smoke or manual demo walkthrough checks if public demo instructions change.
- [x] 8.5 Confirm no application runtime, API, database, authentication, or migration behavior changed as part of Phase 1.
