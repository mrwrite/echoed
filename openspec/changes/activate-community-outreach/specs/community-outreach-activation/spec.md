## ADDED Requirements

### Requirement: Starter Issue Activation
EchoEd SHALL provide a practical starter-issue package before Phase 2 outreach begins.

#### Scenario: Starter issue drafts exist
- **WHEN** Phase 2 implementation is complete
- **THEN** the repository contains at least 5 starter issue drafts with titles, recommended labels, context, acceptance criteria, and validation steps

#### Scenario: Starter issues cover first engagement paths
- **WHEN** maintainers review starter issue drafts
- **THEN** the drafts include good-first-issue candidates, educator feedback issues, documentation improvement issues, accessibility or UI review issues, and contributor onboarding issues

#### Scenario: Starter issues are manually creatable
- **WHEN** GitHub labels are configured
- **THEN** maintainers can manually create starter issues from the drafts without needing automation or private contact data

### Requirement: Outreach Asset Package
EchoEd SHALL provide copy-ready outreach assets for careful, organic community engagement.

#### Scenario: Outreach templates are available
- **WHEN** maintainers prepare first outreach
- **THEN** they can use copy-ready messages for HBCUs, educators, developer contributors, open-source contributors, Africa or Caribbean contacts, and community organizers

#### Scenario: Launch content is available
- **WHEN** maintainers prepare public launch posts
- **THEN** the repository provides a LinkedIn launch post, GitHub Discussions welcome post, Dev.to article outline, and Reddit-safe discussion post

#### Scenario: Outreach copy is bounded and respectful
- **WHEN** a maintainer uses a Phase 2 outreach template
- **THEN** the message includes a specific ask, current project stage, no-budget transparency where relevant, demo/data safety language where relevant, and no implication of unpaid labor obligation

### Requirement: Contact Tracking Guidance
EchoEd SHALL define a simple outreach tracker structure without storing private contact data in the repository.

#### Scenario: Tracker columns are documented
- **WHEN** maintainers create a private tracker
- **THEN** they can use documented columns for target, contact, region, audience, channel, ask, status, next step, owner, follow-up date, and outcome

#### Scenario: Status lifecycle is defined
- **WHEN** maintainers update outreach status
- **THEN** they can use a lifecycle including identified, drafted, contacted, replied, scheduled, contributed feedback, converted to issue, declined, no response, and closed

#### Scenario: Follow-up cadence is bounded
- **WHEN** a contact does not respond
- **THEN** the tracker guidance limits follow-up cadence and avoids repeated pressure

### Requirement: Community Launch Workflow
EchoEd SHALL define the first manual community launch workflow.

#### Scenario: GitHub Discussions setup is specified
- **WHEN** maintainers are ready to open community discussion
- **THEN** Phase 2 guidance reminds them to enable GitHub Discussions manually and configure categories for announcements, introductions, Q&A, educator feedback, contributor help, roadmap, and show-and-tell

#### Scenario: First welcome discussion is prepared
- **WHEN** GitHub Discussions is enabled
- **THEN** maintainers have copy-ready welcome discussion content that introduces EchoEd, current stage, demo path, contribution paths, and community expectations

#### Scenario: First engagement sessions are planned
- **WHEN** maintainers schedule first community activities
- **THEN** Phase 2 guidance provides a demo walkthrough plan, office hours plan, and educator review session plan

### Requirement: Feedback Collection and Triage
EchoEd SHALL provide feedback prompts and triage rules for early reviewers.

#### Scenario: Feedback questions are available
- **WHEN** educators, developers, or demo reviewers evaluate EchoEd
- **THEN** maintainers can ask role-appropriate feedback questions for educator review, developer onboarding, and demo experience

#### Scenario: Feedback becomes tracked work
- **WHEN** useful feedback is received
- **THEN** maintainers can classify it as bug, documentation, accessibility, curriculum, historical accuracy, onboarding, demo, roadmap, or discussion follow-up

#### Scenario: Feedback triage avoids overclaiming
- **WHEN** feedback suggests classroom or historical readiness concerns
- **THEN** maintainers record the concern without claiming classroom readiness or historical authority until review is complete

### Requirement: Recognition and Trust
EchoEd SHALL define transparent recognition and participation expectations for first community engagement.

#### Scenario: Recognition is opt-in
- **WHEN** contributors, educators, or advisors provide meaningful help
- **THEN** maintainers ask whether and how they want to be credited before public recognition

#### Scenario: Advisor language is accurate
- **WHEN** maintainers discuss advisor or educator participation
- **THEN** they distinguish informal feedback, advisory-circle interest, and any future formal role

#### Scenario: Participation expectations are transparent
- **WHEN** outreach templates or session plans ask for help
- **THEN** they make clear that participation is optional, bounded, unpaid unless otherwise stated, and not an ongoing obligation

### Requirement: Thirty-Day Organic Execution Plan
EchoEd SHALL define a 30-day outreach activation plan appropriate for a zero-traction starting point.

#### Scenario: Week-by-week plan exists
- **WHEN** maintainers begin Phase 2
- **THEN** they can follow a week-by-week plan covering setup, first direct outreach, first feedback sessions, issue conversion, and review of results

#### Scenario: Daily routine is bounded
- **WHEN** maintainers execute outreach on a normal day
- **THEN** the plan defines a minimum daily routine that can be completed without paid tools or high-volume posting

#### Scenario: First target audiences are identified
- **WHEN** maintainers choose first outreach targets
- **THEN** the plan lists 10 target audience types spanning educators, HBCUs, Black developers, Africa and Caribbean contributors, open-source contributors, and community organizers

#### Scenario: Zero-traction metrics are defined
- **WHEN** maintainers evaluate the first 30 days
- **THEN** they measure practical early indicators such as outreach sent, replies, demo reviews, issues created, first contributors, educator feedback quality, and follow-up conversations rather than vanity metrics alone

### Requirement: Manual Setup and Validation
EchoEd SHALL define manual setup reminders and validation steps for Phase 2.

#### Scenario: Manual GitHub setup reminders are present
- **WHEN** maintainers prepare to activate outreach
- **THEN** guidance reminds them to create GitHub labels, enable Discussions, configure discussion categories, and create starter issues manually if no CLI tooling is available

#### Scenario: Phase 2 validation is defined
- **WHEN** Phase 2 artifacts are complete
- **THEN** maintainers can validate OpenSpec, review docs for placeholders and private contact data, verify internal links, and confirm no automation or paid marketing assumptions were introduced
