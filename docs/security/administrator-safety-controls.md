# Administrator Safety Controls

| Action against self | Decision |
| --- | --- |
| Change/remove own platform role | 409; blocked |
| Grant own additional platform permission | impossible through allowlisted role-only endpoint; blocked |
| Delete own account | 409; blocked |
| Deactivate/reset own security state | endpoint not implemented |
| Remove own organization membership/change org scope | endpoint not implemented |
| Ordinary profile/preferences editing | unchanged |

The protected final administrator is the last persisted `super_admin`, not the last `admin`. Demotion or deletion locks the target and the matching super-admin rows where the database supports `SELECT FOR UPDATE`, counts them inside the mutation transaction, and returns 409 if no super administrator would remain. With two or more, an authorized different super admin may demote/delete one. The current account model has no activation/usable flag, so persisted records are counted; this must change if account lifecycle is added.

EchoEd does not impose a final organization-admin invariant in Phase 8. Personal organizations and existing organization lifecycle do not establish that product requirement, and there is no membership-removal endpoint. Frontend prevention improves clarity but the backend is authoritative. See `test_security_hardening.py` for self, final, and multiple-admin cases.
