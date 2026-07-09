## Context

EchoEd is a full-stack Angular and FastAPI education platform centered on African and African-American history. The repository already contains a working application, deterministic demo runbooks, OpenSpec workflow, CI configuration, and an MIT license, but the public-facing repository is not yet ready for community outreach:

- `README.md` contains stale placeholder GitHub URLs, outdated hosting references, and encoding artifacts.
- Standard community files such as `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ROADMAP.md`, `ARCHITECTURE.md`, and `SECURITY.md` are absent.
- `.github/ISSUE_TEMPLATE/` exists but is empty, and there is no pull request template.
- Demo runbooks exist, but public demo guidance and shared-credential handling need to be separated from internal operator instructions.
- The landing page now speaks to educators and developers, but it still needs aligned public demo instructions, screenshots or walkthrough guidance, and contribution pathways before major outreach.
- The project has no current users, contributors, advisors, stars, or community traction, so first impressions matter.

Phase 1 is a public-readiness phase, not a feature-building phase. The intended stakeholders are educators, African-American studies teachers, homeschool and community learning organizers, Black software developers, HBCU programs, potential advisors, and first-time open-source contributors across the United States, Africa, and the Caribbean.

## Goals / Non-Goals

**Goals:**

- Make the repository understandable within a few minutes for educators and developers.
- Make the project contributor-ready with clear setup, testing, issue, PR, and communication guidance.
- Make the live demo safe and useful for public visitors without exposing confusing internal operations.
- Establish trust practices for historical accuracy, educator review, accessibility, inclusion, recognition, and non-extractive participation.
- Define the minimum viable public-facing checklist that must be complete before broad organic outreach begins.
- Recommend first outreach targets after Phase 1 is complete.

**Non-Goals:**

- No new application runtime features.
- No backend API changes.
- No database, migration, or authentication changes.
- No paid marketing, ads, sponsorships, or paid tooling.
- No formal nonprofit, advisory board, fiscal sponsorship, or governance entity setup.
- No requirement to support production user onboarding beyond the current public demo and contribution flow.

## Decisions

### Decision: Treat Phase 1 as a readiness gate, not outreach itself

Phase 1 will produce documentation, templates, demo guidance, and trust processes. Outreach to educators, HBCUs, developer groups, and community organizers begins only after a minimum viable checklist passes.

Alternatives considered:

- Start outreach immediately and improve docs reactively. Rejected because early visitors would encounter placeholder links, missing contribution guidance, and unclear demo instructions.
- Build more product features first. Rejected because the current blocker is trust and clarity, not feature depth.

### Decision: Separate internal demo operations from public demo guidance

Existing demo runbooks can remain operator-focused. Public-facing README and landing content should present a safe, concise demo path: what the demo shows, who should try it, how credentials are handled, what limitations exist, and how to report feedback.

Alternatives considered:

- Publish all internal runbook details as the primary demo path. Rejected because it overwhelms non-technical visitors and can normalize shared credentials without context.
- Remove demo credentials entirely. Rejected for Phase 1 because the current no-budget outreach plan needs low-friction evaluation.

### Decision: Use GitHub-native community infrastructure first

Phase 1 will use repository files, GitHub issue templates, PR templates, labels, and a recommendation to enable GitHub Discussions. This avoids new infrastructure while the project has no traction and no budget.

Alternatives considered:

- Create a separate Discord, Slack, CRM, or custom community portal now. Rejected because each adds moderation and maintenance overhead before there is a community.
- Use email only. Rejected because developer contributors need transparent issue and discussion history.

### Decision: Define educator participation without extractive framing

Educator review requests must be specific, bounded, credited when desired, and clear about the current no-budget status. The project must not frame open-ended curriculum labor as casual feedback.

Alternatives considered:

- Ask broadly for "educator feedback" without structure. Rejected because it is vague and can feel extractive.
- Delay educator review until funding exists. Rejected because early educator judgment is essential to mission fit; Phase 1 can still define respectful, bounded participation.

### Decision: Create one new OpenSpec capability for community readiness

The requirements cut across docs, GitHub configuration, landing content, and community process. A new `open-source-community-readiness` capability keeps these requirements separate from runtime product specs.

Alternatives considered:

- Modify landing-page or demo-readiness specs only. Rejected because repository trust, contributor onboarding, community review, and outreach readiness are broader than landing/demo behavior.

## Risks / Trade-offs

- [Risk] Shared demo credentials may be misused after public outreach. -> Mitigation: document credential scope, reset expectations, limitations, and owner monitoring; keep credentials demo-only and separate from real user data.
- [Risk] Community docs can overpromise governance or support capacity. -> Mitigation: state the project stage plainly and distinguish current practices from future aspirations.
- [Risk] Educator and historical accuracy review may appear performative without visible process. -> Mitigation: add an explicit review pathway, issue template, recognition option, and advisory circle concept.
- [Risk] First contributors may still struggle with local setup. -> Mitigation: include verified setup commands, env variable guidance, seed data instructions, and testing commands in `CONTRIBUTING.md` and `ARCHITECTURE.md`.
- [Risk] GitHub Discussions and labels require manual repository settings. -> Mitigation: document owner-only setup steps and keep codebase deliverables useful even if settings are enabled later.
- [Risk] The README may become too long for non-technical educators. -> Mitigation: structure README with a concise mission, demo, educator path, developer path, and links to deeper docs.
- [Risk] No paid budget limits reach and response speed. -> Mitigation: prioritize warm, specific, organic outreach targets after readiness is complete.

## Migration Plan

1. Add repository community files and templates without changing application code.
2. Refresh README and supporting docs to point to the real repository, temporary live app, public demo path, and current project status.
3. Add or update landing/demo copy only where needed to align with the public docs.
4. Add issue and PR templates, plus a labels recommendation document because labels may need manual GitHub setup.
5. Run markdown review, link review, OpenSpec validation, and existing build/test smoke checks appropriate for docs-only changes.
6. Enable GitHub Discussions manually after docs are merged, if the repository owner agrees.

Rollback is straightforward: revert the documentation/template changes. No database, API, or runtime migration is involved.

## Open Questions

- What public email address should be used for community inquiries if `support@echoed.com` is not final?
- Should shared demo credentials remain in the README, live landing page, a separate demo guide, or only behind a request flow?
- Which contributor recognition format is preferred: README acknowledgements, release notes, contributor profile page, or all of these?
- Who is the first named maintainer responsible for triage, code review, educator review routing, and security reports?
- Should GitHub Discussions be enabled immediately after Phase 1 or after the first small outreach cohort?
