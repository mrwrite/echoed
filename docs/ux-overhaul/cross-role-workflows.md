# Cross-Role Workflows

## Course to Classroom

```mermaid
flowchart LR
  A[Content admin authors course] --> B[Review center approves]
  B --> C[Product/course published]
  C --> D[Teacher previews curriculum]
  D --> E[Teacher assigns to class]
  E --> F[Student completes lesson]
  F --> G[Teacher monitors progress]
  G --> H[Runtime support recommends reteach/review/enrichment]
```

Backend compatibility: supported by existing course/version/review/product, assignment, progress, and analytics APIs.

## Organization Onboarding

```mermaid
flowchart LR
  A[User registers] --> B[Optional pending org setup]
  B --> C[Login]
  C --> D[Onboarding guard checks orgs]
  D --> E[Create organization]
  E --> F[Switch active org]
  F --> G[Role-aware home]
```

Backend compatibility: supported by `auth`, `orgs`, `PermissionsService`, and onboarding helpers.

## Discussion and Moderation

```mermaid
flowchart LR
  A[Student posts question] --> B[Thread API]
  B --> C[Teacher monitors class discussion]
  C --> D[Admin/content moderator reviews flagged content]
  D --> E[Resolution and learner-safe feedback]
```

Gap: backend `posts.py` and `threads.py` exist, but full UI and moderation workflow are not clearly implemented.

## Access Grants

```mermaid
flowchart LR
  A[Org admin/content admin grants access] --> B[Access grant API]
  B --> C[Learner portal product visible]
  C --> D[Student starts learning]
  D --> E[Teacher/admin sees progress]
```

Design warning: avoid commercial/marketplace framing in community project UI.
