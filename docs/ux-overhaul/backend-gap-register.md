# Backend Gap Register

Date: 2026-07-13

| Role | User need | Current frontend behavior | API limitation | Privacy/security implication | Blocks current workflow | Future OpenSpec change | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Teacher/instructor | Scoped learner review | Read-only/scoped UI | No complete class-scoped review/feedback persistence | Avoid global learner disclosure | Yes for persistent feedback | Educator review and feedback contract | High |
| Teacher/instructor | Moderate class discussion | Hidden | Thread/post APIs have no auth or class scope | Unscoped destructive access | Yes | Authenticated scoped discussion moderation | Critical |
| Instructor | Use educator analytics consistently | Partial states | Several analytics role lists omit instructor | Role may expose navigation that API rejects | Partial | Instructor authorization alignment | High |
| Admin | Platform-wide organization oversight | Shows current account memberships only | `/api/orgs` is membership-scoped; no member/admin/section summaries | Inferring or bypassing scope risks cross-org disclosure | Yes for requested oversight | Platform organization directory with explicit permission and minimized response | High |
| Admin | Safe role management | Limits roles; blocks self-change | Arbitrary role strings; no final-admin/self-lockout check; full DTO update | Privilege escalation and lockout risk | Partial | Role-specific allowlisted mutation with critical-admin invariant | Critical |
| Admin | Privacy-safe user reads | Typed UI omits sensitive fields; detail deep links work after the UUID route repair | ORM user serialization lacks dedicated minimized summary/detail response schemas | Hashed/internal fields may cross the API boundary even though the UI omits them | No for current UI; yes for API-level minimization | Admin user summary/detail response schemas | High |
| Admin | Disable/restore account | No controls | No status or mutation API | Invented frontend state would be unenforced | Yes | Account access-state lifecycle | Medium |
| Admin | Moderation/report queue | No route/control | No authenticated scope, flags, reports, restore, lock, or audit | Unsafe cross-community disclosure and deletion | Yes | Platform safety and moderation capability | Critical |
| Admin | Audit high-impact actions | Confirmation only | No audit log/event contract | Destructive/privilege changes lack accountability | No, but operational risk | Administrative audit events | High |
| Admin | Badge lifecycle | Create/read only | No edit/archive/delete/criteria relation | Credential meaning cannot be governed | Partial | Badge lifecycle and criteria contract | Medium |
| Admin/super admin | Consistent privilege model | Role-accurate limitation state | Exact checks conflict with presumed super-admin inheritance | Name can cause unsafe assumptions | Partial | Explicit platform permission policy replacing name inference | High |
