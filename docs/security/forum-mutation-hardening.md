# Forum Mutation Hardening

Public thread/post reads remain intentional for the current public Community preview. Every implemented write now fails closed at the backend.

| Endpoint/capability | Before | After |
| --- | --- | --- |
| `POST /api/forum/threads` | anonymous; trusted `user_id` | authenticated; owner is current user; rate-limited |
| `PUT /api/forum/threads/{id}` | anonymous; could replace owner | author or `admin`/`super_admin`; title only; owner immutable |
| `DELETE /api/forum/threads/{id}` | anonymous | author or platform moderator; moderator action logged |
| `POST /api/forum/posts` | anonymous; trusted `user_id` and any parent | authenticated; existing thread required; owner server-derived; rate-limited |
| `PUT /api/forum/posts/{id}` | anonymous; could move parent/owner | author or moderator; content only; parent/owner immutable |
| `DELETE /api/forum/posts/{id}` | anonymous | author or moderator; moderator action logged |
| `GET` thread/post collection/detail | public | public, unchanged |
| reactions/votes/reports | absent | disabled (no route; 404) |
| pin/lock/hide/restore/moderation | absent | disabled except moderator edit/delete on implemented records |
| forum attachments/uploads | absent | disabled; generic content uploads cannot be attached by forum payload |

There is no organization/community field in the current thread/post model, so Phase 8 does not pretend to provide organization-scoped forums. Organization forums, memberships, reporting, reactions, and richer moderator roles require a future community contract. Evidence: `backend/tests/test_forum_endpoints.py` covers 401, allowed author writes, immutable ownership, 403 non-owner denial, moderator deletion, and public reads.
