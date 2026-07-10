# Proposed User Journeys

## Student: Resume Learning

```mermaid
flowchart TD
  A[Sign in] --> B[Resolve role and active org]
  B --> C[/learn]
  C --> D[Next learning card]
  D --> E{Assigned or self-selected?}
  E -->|assigned| F[Open assignment context]
  E -->|self-selected| G[Open course overview]
  F --> H[Start/resume lesson]
  G --> H
  H --> I[Lesson player]
  I --> J[Activity/assessment]
  J --> K[Completion feedback]
  K --> L[Progress and next recommendation]
```

Design requirements: next action first, lesson status visible, safe exit sticky on mobile, live progress feedback.

## Student: Recover Interrupted Session

```mermaid
flowchart TD
  A[Open lesson route] --> B[Show restoring lesson status]
  B --> C[Try segment restore]
  C -->|success| D[Return to exact lesson]
  C -->|stale| E[Find active learner course]
  E -->|found| F[Explain recovery and continue]
  E -->|not found| G[Return to Learn with retry]
```

Design requirements: do not show raw IDs, explain recovery in student-safe copy.

## Teacher: Start Day

```mermaid
flowchart TD
  A[Sign in] --> B[/teach]
  B --> C[Today's priorities]
  C --> D[Learners needing support]
  C --> E[Recent submissions]
  C --> F[Upcoming assignments]
  D --> G[Open class detail]
  E --> H[Review work]
  F --> I[Edit or assign learning]
```

Design requirements: class context visible; intervention recommendations linked to evidence and next teacher action.

## Teacher: Assign Learning

```mermaid
flowchart TD
  A[Classes] --> B[Select class]
  B --> C[Assignments tab]
  C --> D[Create assignment]
  D --> E[Choose curriculum item]
  E --> F[Choose target learners]
  F --> G[Set due/status]
  G --> H[Review summary]
  H --> I[Confirm assignment]
```

Design requirements: reuse existing sections/assignments APIs; no new backend contract required for initial guided UI.

## Content Admin: Publish Content

```mermaid
flowchart TD
  A[Studio] --> B[Projects]
  B --> C[Product detail]
  C --> D[Review readiness]
  D --> E{Safe to publish?}
  E -->|yes| F[Publish confirmation]
  E -->|no| G[Issue list with owners]
  F --> H[Published product]
```

Design requirements: source provenance, review status, safe-publish issues, learner impact warnings.

## Admin: Resolve Access Issue

```mermaid
flowchart TD
  A[Admin dashboard] --> B[Access alert]
  B --> C[User detail]
  C --> D[Org memberships]
  D --> E[Adjust role or invite]
  E --> F[Confirmation]
  F --> G[Audit-friendly success]
```

Design requirements: destructive/privileged actions require confirmation and clear role definitions.
