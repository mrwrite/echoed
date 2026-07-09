# Open-Source Readiness Audit

This audit records the Phase 1 baseline for `prepare-open-source-community-launch`.

## Confirmed Project Facts

- Live app: https://echoed-theta.vercel.app/
- GitHub repository: https://github.com/mrwrite/echoed
- License: MIT, copyright 2025 Anthony Wright
- Current stage: pre-community-launch, no current public users or contributors
- Demo status: working K-5 demo with shared demo-only credentials
- Budget: no paid outreach budget; outreach will be organic and community-driven
- Community contact used for Phase 1 docs: `support@echoed.com`

## Gaps Found

- README used placeholder GitHub URLs and stale hosting references.
- README contained unreadable encoding artifacts.
- Standard community files were missing: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ROADMAP.md`, `ARCHITECTURE.md`, and `SECURITY.md`.
- `.github/ISSUE_TEMPLATE/` existed but had no templates.
- No pull request template existed.
- Demo credentials were documented in an internal operator runbook, but public demo safety guidance was not separated.
- Contributor onboarding was too thin for a first-time external contributor.
- No documented educator review, historical accuracy review, contributor recognition, or advisory circle concept existed.
- No minimum public-facing checklist existed before outreach.
- GitHub labels and Discussions recommendations were not documented.

## Phase 1 Decisions

- Public demo credentials live in [public-demo.md](public-demo.md), not directly on the landing page.
- README links to the public demo guide and warns against entering real data.
- Internal demo reset and operator details remain in [demo-readiness.md](demo-readiness.md).
- Community contact remains `support@echoed.com` until a final public inbox is chosen.
- GitHub-native surfaces are the first community infrastructure: issues, pull requests, labels, and recommended Discussions categories.
- GitHub labels and Discussions are documented as owner setup steps because they require repository settings.
