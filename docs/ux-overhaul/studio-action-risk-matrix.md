# Studio Action Risk Matrix

Date: 2026-07-13

| Action | Object | Backend behavior | Risk | Reversible | Confirmation | Permission and recovery |
| --- | --- | --- | --- | --- | --- | --- |
| Create project | Project | Inserts organization-scoped project | Consequential | No delete API | No; explicit submit | Manage visible workspace; preserve form on failure |
| Create learning offering | Product wrapper | Inserts draft wrapper | Consequential | No delete API | No; form explains wrapper-only scope | Manage visible workspace; preserve form on failure |
| Add source record | KnowledgeSource | Inserts project-scoped metadata | Consequential | No edit/delete API | No; explicit submit | Project must belong to workspace; preserve form on failure |
| Create content draft | Artifact | Inserts reviewable wrapper, optionally linked to source/product | Consequential | No delete API | No; explicit submit | Same-project relationships; preserve form on failure |
| Change review state | Artifact or Product | Replaces `status` and `review_state` | Privilege/content-governance changing | Can set another supported state, but no audit | Yes for every state | Manage visible workspace; dialog remains with error after failure |
| Reject draft | Artifact | Sets rejected state; does not delete | Consequential | Another state can be set | Danger confirmation | Explain content and sources remain |
| Archive offering | Product | Sets archived state via review endpoint | Consequential | No dedicated restore semantics | Danger confirmation | Explain audit/restore gap |
| Publish publicly | Product | Sets published/public wrapper state and timestamps | High impact | No unpublish endpoint | Publish confirmation | Explain public visibility and unchanged lesson/access rules |

No V2 project, product, source, or artifact delete endpoint exists. Studio displays no delete buttons and does not imply archive is deletion.
