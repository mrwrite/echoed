# Phase 2 Starter Issue Drafts

Use these drafts to manually create the first GitHub issues after labels are configured. Do not create issues automatically unless maintainers explicitly choose to use GitHub tooling.

## Before Creating Issues

- Create the labels recommended in [github-community-setup.md](github-community-setup.md).
- Keep issue scope small enough for a first contribution.
- Link to relevant docs when possible.
- Do not assign issues to people unless they ask.

## Draft 1: Good First Issue - Verify Windows Setup Instructions

Recommended labels: `good first issue`, `documentation`, `contributor onboarding`, `needs triage`

### Context

EchoEd's docs include Windows-focused setup commands. A new contributor should be able to follow them without private maintainer help.

### Issue Body

Review the setup instructions in `README.md`, `CONTRIBUTING.md`, and `ARCHITECTURE.md` from the perspective of a first-time Windows contributor.

### Acceptance Criteria

- Confirm frontend setup commands are clear.
- Confirm backend setup commands are clear.
- Note any command that fails or needs extra context.
- Suggest doc edits if something is confusing.
- Do not change product code.

### Validation

- Run only the commands you are comfortable running.
- If a command cannot be run, note why in the issue.

## Draft 2: Educator Feedback - Review One Student Demo Flow

Recommended labels: `educator feedback`, `curriculum`, `demo`, `needs educator review`

### Context

EchoEd needs bounded educator feedback before broader outreach. This issue asks for review of one learner flow, not the full platform.

### Issue Body

Use [public-demo.md](public-demo.md) to sign in as `normalstudent` and review one learner path.

### Review Prompts

- What grade band or learner context are you using?
- What felt clear or useful?
- What felt confusing, inaccessible, or culturally off?
- What would an educator need before using this with learners?
- What discussion prompt, activity support, or source would improve the flow?

### Recognition

Please state whether you are comfortable being credited if your feedback leads to a visible change.

### Acceptance Criteria

- Feedback identifies the reviewed route or lesson.
- Feedback includes at least one concrete improvement or concern.
- Feedback avoids entering real learner data.

## Draft 3: Documentation - Improve Public Demo Guide Screenshots or Walkthrough

Recommended labels: `documentation`, `demo`, `good first issue`, `needs maintainer review`

### Context

The public demo guide is text-only. A contributor can improve evaluation by adding a clearer walkthrough outline or screenshot checklist.

### Issue Body

Review [public-demo.md](public-demo.md) and suggest additions that help educators, developers, and organizers understand what to evaluate.

### Acceptance Criteria

- Add or propose a short step-by-step walkthrough for at least one role.
- Include screenshot placeholders or a screenshot checklist if actual screenshots are not added.
- Keep demo credential warnings visible.
- Do not add private data or real student information.

### Validation

- Confirm all links in the guide still resolve.
- Confirm the guide remains readable for non-technical educators.

## Draft 4: Accessibility/UI Review - Landing Page and Demo Entry

Recommended labels: `accessibility`, `frontend`, `demo`, `needs accessibility review`

### Context

Before inviting more visitors, EchoEd needs a lightweight accessibility and UI review of the landing page and demo entry path.

### Issue Body

Review the public landing page and login/demo entry path for keyboard use, readable text, contrast, labels, mobile layout, and clear calls to action.

### Acceptance Criteria

- Note any keyboard navigation issues.
- Note any contrast or readability issues.
- Note any confusing call to action.
- Include browser/device context.
- File follow-up issues for specific fixes if needed.

### Validation

- Manual review is acceptable.
- Screenshots are helpful but not required.

## Draft 5: Contributor Onboarding - Test First PR Flow

Recommended labels: `contributor onboarding`, `documentation`, `good first issue`, `needs maintainer review`

### Context

EchoEd needs to know whether a first-time contributor can understand how to pick an issue, make a small docs change, and open a pull request.

### Issue Body

Follow [CONTRIBUTING.md](../CONTRIBUTING.md) and identify any friction in the first contribution workflow.

### Acceptance Criteria

- Identify one place the contributor workflow is clear.
- Identify one place it could be clearer.
- Suggest a specific doc improvement.
- Do not change application behavior.

### Validation

- A documentation-only pull request or comment with recommended edits is acceptable.

## Draft 6: Historical Accuracy Review - Source and Framing Path

Recommended labels: `historical accuracy`, `curriculum`, `needs historical review`

### Context

EchoEd needs a clear process for historical accuracy and source concerns before scaling educator outreach.

### Issue Body

Review [community-trust.md](community-trust.md) and the historical accuracy issue template. Identify whether the path is clear for reporting source, framing, or accuracy concerns.

### Acceptance Criteria

- Confirm whether the reporting path is understandable.
- Suggest missing context or clarifying language.
- Do not require reviewers to provide unpaid source research.

### Validation

- Documentation review only.

## Draft 7: Good First Issue - Add Five More Starter Issue Candidates

Recommended labels: `good first issue`, `documentation`, `help wanted`

### Context

Phase 2 starts with a small issue set. More starter issues will help match contributors with clear work.

### Issue Body

Add five additional starter issue drafts to this document or propose them in a comment.

### Acceptance Criteria

- Each issue has title, labels, context, acceptance criteria, and validation.
- At least one issue is educator-facing.
- At least one issue is developer-facing.
- At least one issue is accessibility or documentation focused.

### Validation

- Maintainer can manually create the issue from the draft without asking for missing scope.
