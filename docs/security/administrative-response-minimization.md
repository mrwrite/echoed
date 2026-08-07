# Administrative Response Minimization

| Endpoint | Previous exposure | New fields | Removed / compatibility |
| --- | --- | --- | --- |
| `GET /users` | raw ORM `User`, including `hashed_password`, update timestamp, and future relationships | `id`, `firstname`, `lastname`, `username`, `email`, `role`, `created_at` | password hash, `updated_at`, relationships, future model fields; Angular Admin uses retained fields |
| `GET /users/{id}` | raw ORM `User` | same explicit detail summary | same removals; Admin detail compatible |
| `GET /users/students` | raw ORM users and contact/security fields | `id`, names, `username`, `role` | email, hash, timestamps, relationships; teacher selectors use identity fields only |
| `POST /orgs/{id}/invites` | full invite including bearer token | invite metadata plus token once for current no-email distribution workflow | no unrelated organization/user graph |
| `GET /orgs/{id}/invites` | bearer token on every list read | id, org id, email, role, expiry, acceptance timestamp, inviter id | `token`; Angular status views remain compatible |
| `GET /orgs/{id}/members` | already minimal | membership id, user id, display name, username, org role/status/joined date | email, global platform role, hash, relationships remain absent |

All changed response models are explicit Pydantic schemas and prevent future ORM fields from serializing accidentally. Platform-global user summaries and organization-member summaries remain distinct. Backend schema tests and Angular consumer tests provide evidence.
