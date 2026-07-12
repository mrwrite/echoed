# Teacher Role Capability Map

Date: 2026-07-12

| Capability | Teacher | Instructor | Org admin in class routes | Notes |
| --- | --- | --- | --- | --- |
| Teach overview | Yes | Yes | No primary nav | Uses existing teacher dashboard component. Instructor compatibility is UI-level; some analytics endpoints still require backend expansion. |
| Classes list | Yes | Yes | Yes | Uses `/api/sections`. |
| Create class | Yes | Yes | Yes | Requires current course version ID contract. |
| Class roster | Yes | Yes | Yes | Uses `/api/sections/{id}/roster`; learner names are matched from `/api/users/students` where available. |
| Create class assignment | Yes | Yes | Yes | Uses `/api/sections/{id}/assignments`; no individual learner targeting in this endpoint. |
| Curriculum browse | Yes | Yes | No | Uses `/api/courses`. |
| Course preview | Yes | Yes | No | Uses `/api/courses/{id}` only; does not create learner progress. |
| Learner detail | Yes, class scoped | Yes, class scoped | Yes, class scoped | Requires `sectionId` and roster membership. |
| Progress monitoring | Partial | Partial | Partial | Section summary and teacher summary are supported; class-scoped learner detail is not fully supported. |
| Assessment/work review | Read-only/limited | Read-only/limited | Read-only/limited | Auto-scored attempts exist; manual grading/feedback persistence is not verified. |
| Discussion moderation | Deferred | Deferred | Deferred | Threads/posts lack verified class scope and moderation permissions. |
| Studio/admin links | No | No | Org admin may have organization/studio permissions separately | Teach nav does not expose Studio/Admin for teacher/instructor roles. |
