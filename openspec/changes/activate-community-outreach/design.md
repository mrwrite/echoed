## Context

Phase 1 established EchoEd's public open-source readiness foundation: README, contributor guide, code of conduct, roadmap, architecture overview, security policy, public demo guide, community trust guide, outreach readiness guide, GitHub issue templates, PR template, and the `open-source-community-readiness` spec.

Phase 2 starts from zero traction. EchoEd has no current public users, contributors, stars, advisors, or community routines. The goal is not broad promotion; it is careful activation: create a small set of visible starter issues, prepare respectful outreach assets, enable basic community surfaces, run a first demo/review routine, and turn early feedback into issues or roadmap items.

Important constraints:

- No paid budget.
- No outreach automation.
- No scraping.
- No contacting anyone as part of implementation.
- No private or sensitive contact data committed to the repo.
- No claim that EchoEd is classroom-ready before educator and historical review.
- Manual GitHub owner tasks remain manual: labels, Discussions, categories, and issue creation if API tooling is not used.

## Goals / Non-Goals

**Goals:**

- Provide at least 5 starter issue drafts that are ready to create in GitHub.
- Provide copy-ready outreach templates for educators, HBCUs, developers, open-source contributors, Africa/Caribbean contacts, and community organizers.
- Provide copy-ready launch content for LinkedIn, GitHub Discussions, Dev.to, and Reddit-safe discussion.
- Define a simple contact tracker structure and status lifecycle without storing real contacts.
- Define a first community launch workflow: GitHub Discussions, welcome post, demo walkthrough, office hours, and educator review session.
- Define feedback questions and triage rules that convert feedback into GitHub issues or roadmap items.
- Define recognition and trust practices for the first contributors, educators, and advisors.
- Define a 30-day execution plan with low-volume daily outreach and zero-traction success metrics.

**Non-Goals:**

- No automated emailing, social posting, scraping, or CRM integration.
- No paid marketing, sponsorships, ads, or influencer campaigns.
- No creation of real contact lists in the repository.
- No application feature work.
- No production user onboarding.
- No guarantee of contributor response, educator participation, or public adoption.

## Decisions

### Decision: Use repository docs as reusable outreach assets

Phase 2 will add docs containing copy-ready outreach language, issue drafts, feedback questions, and workflow guidance. This keeps materials visible, reviewable, and easy to revise.

Alternatives considered:

- Keep outreach copy in private notes only. Rejected because the project benefits from transparent messaging and maintainer reuse.
- Add a CRM or contact-management tool. Rejected because the project has no traction, no budget, and no need to store private data in this phase.

### Decision: Draft starter issues rather than create issues automatically

Implementation will provide issue drafts with titles, labels, body copy, and acceptance criteria. Maintainers can create them manually in GitHub after labels are configured.

Alternatives considered:

- Use GitHub CLI or API to create issues automatically. Rejected because `gh` is not installed in the current environment and automation is not necessary for Phase 2.
- Store starter issues only as a list of titles. Rejected because first contributors need enough acceptance criteria to act.

### Decision: Treat GitHub Discussions as a manual launch surface

The change will include welcome discussion copy and category recommendations, but enabling Discussions remains a manual GitHub owner task.

Alternatives considered:

- Use only issues for all community interaction. Rejected because intros, Q&A, and broader educator/developer conversation can overwhelm issue tracking.
- Launch Discord or Slack immediately. Rejected because moderation overhead is too high before there is a community.

### Decision: Use bounded outreach routines

The 30-day plan will favor small daily actions, warm introductions, and concrete asks such as "review one learner flow" or "test setup and file one issue."

Alternatives considered:

- Mass post across many communities. Rejected because the project is zero-traction and culturally specific; trust matters more than volume.
- Wait for contributors organically without outreach. Rejected because early visibility requires deliberate invitations.

### Decision: Keep recognition opt-in and transparent

Recognition guidance will let contributors and educators opt into credit without implying employment, compensation, formal advisor status, or ongoing labor expectations.

Alternatives considered:

- Publicly credit all feedback by default. Rejected because some reviewers may not want visibility.
- Avoid recognition until formal governance exists. Rejected because early contributors deserve visible appreciation when they want it.

## Risks / Trade-offs

- [Risk] Outreach messages may still feel extractive. -> Mitigation: include non-extractive language, bounded asks, no-budget transparency, and opt-in recognition.
- [Risk] Starter issues may attract attention before maintainers are ready. -> Mitigation: include manual readiness checks and label setup before issue creation.
- [Risk] GitHub Discussions may create moderation overhead. -> Mitigation: recommend enabling only when maintainers can respond and start with narrow categories.
- [Risk] Public demo credentials may be misused after outreach. -> Mitigation: repeat demo-only warnings in outreach assets and feedback prompts.
- [Risk] Contact tracking could become sensitive. -> Mitigation: define structure only; do not commit real contacts or private notes.
- [Risk] Success metrics may become vanity metrics. -> Mitigation: focus on replies, feedback quality, issues created, demo review sessions, and first contributor activation rather than follower counts.

## Migration Plan

1. Add Phase 2 outreach activation docs and starter issue drafts.
2. Keep all real outreach execution manual and outside the repository.
3. Validate OpenSpec change with `openspec validate activate-community-outreach --strict`.
4. When implemented, manually configure GitHub labels and Discussions before creating starter issues.
5. Create starter issues manually from the drafts.
6. Run the 30-day plan using an external spreadsheet or private tracker, not committed repo data.

Rollback is documentation-only: revert the Phase 2 docs/change files if they are not useful. No runtime or data migration is involved.

## Open Questions

- Which public contact address should be final for community scheduling if `support@echoed.com` changes?
- Will GitHub Discussions be enabled before the first outreach messages or after the first small review cohort?
- Who will own weekly triage of educator feedback and developer issues during the first 30 days?
- Should the first office hours session be asynchronous in GitHub Discussions or live over video?
