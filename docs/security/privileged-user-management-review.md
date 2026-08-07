# Privileged User-Management Review

## Platform routes

| Endpoint | Actor | Target/fields | Invariants | Response |
| --- | --- | --- | --- | --- |
| `GET /users` | `admin`, `super_admin` | all platform users | read-only | explicit platform summaries |
| `GET /users/{id}` | `admin`, `super_admin` | one platform user | 404 absent | explicit platform detail summary |
| `GET /users/students` | `teacher`, `admin`, `super_admin` | students | read-only; no contact data | student summary |
| `PUT /users/{id}` | `admin`, `super_admin` | `role` only | no self action; admins cannot target/grant platform admins; final super admin retained | message only |
| `DELETE /users/{id}` | `admin`, `super_admin` | target account | no self deletion; target hierarchy; final super admin retained | message only |

Unsupported routes for activation/deactivation, credential reset, impersonation, membership mutation/removal, and admin revoke/grant outside role update remain absent (404/405). Phase 8 does not invent them.

## Policy decisions

- `super_admin` is the highest platform role; `admin` is a compatible lower platform-administrator role.
- Admins may manage non-platform roles but cannot grant `admin`/`super_admin`, change another admin, or target a super admin. Super admins may do so except against themselves.
- Public registration may select only supported non-administrative onboarding roles (`student`, `teacher`, `instructor`, `parent`); any other value becomes `student`.
- Organization admins grant only organization roles and cannot grant `super_admin`. Organization invite lists omit bearer tokens; a newly created invitation returns its token once because no mail delivery exists.
- Updates forbid extra fields, so password, IDs, organization scope, names, email, timestamps, and ORM relationships cannot be mass-assigned.
- No active/deactivated column exists; all persisted super admins count as usable. Adding lifecycle state must extend the invariant transactionally.

High-impact successes/final-admin failures emit privacy-safe structured events. Evidence is in `test_admin_users.py`, `test_security_hardening.py`, `test_org_admin_scope.py`, and Angular admin tests.
