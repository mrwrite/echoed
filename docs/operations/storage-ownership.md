# Static and Upload Storage Ownership

| State | Source of truth | Owner / deployment behavior | Loss consequence |
| --- | --- | --- | --- |
| PostgreSQL | Production database | Data operator backs up/restores | Accounts, courses, memberships, and progress lost/inconsistent. |
| Storybook uploads | `STORYBOOK_PATH` | Storage operator provides persistent mount and coordinated backup | Story assets return 404; DB references remain. |
| Coloring uploads | `COLORINGS_PATH` | Same | Coloring assets unavailable. |
| Badge images | `BADGES_PATH` | Same | Badge images unavailable while records remain. |
| Angular/backend code static files | Immutable artifact/source | Release pipeline rebuilds/redeploys | Restore known-good artifact. |
| Configuration/secrets | Versioned templates + external secret manager | Platform/security operator | Startup validation failure or security incident. |

Production validation requires absolute, distinct upload paths and an explicit persistence acknowledgement, but cannot prove the mount is durable. Bind mounts in Compose are development behavior. MinIO exists in Compose but application routes do not use it; it is not a backup or source of truth. External object storage, replication, lifecycle management, and CDN/origin isolation remain deferred infrastructure work.
