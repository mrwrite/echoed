# Admin Moderation Capability Map

Date: 2026-07-13

| Content type | Read API | Action API | Authorization | Reversible/auditable | Admin decision |
| --- | --- | --- | --- | --- | --- |
| Threads | `GET /api/threads*` | Create/update/delete | None | Delete is irreversible; no audit | Not exposed. APIs have no auth, scope, ownership, flag, lock, hide, restore, or moderator contract. |
| Posts | `GET /api/posts*` | Create/update/delete | None | Delete is irreversible; no audit | Not exposed for the same reason. |
| Course discussions | No scoped moderation API | None | None verified | No | Not exposed. |
| Uploaded content | No asset-list API | Upload only | Role-specific upload checks | No delete/audit | No moderation or asset-library UI. Badge upload remains inside badge creation. |
| Flags/reports | No API | None | None | No | No queue, counts, or controls. |

No `/admin/moderation` route is introduced. A platform queue built from unscoped thread/post CRUD would imply authorization, reports, and consequences that do not exist.
