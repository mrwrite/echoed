# Admin Action Risk Matrix

Date: 2026-07-13

| Action | Classification | Object / backend behavior | Reversible | Confirmation / permission | Recovery and audit gap |
| --- | --- | --- | --- | --- | --- |
| Review user/course/org/badge/report | Informational | GET only | N/A | Guarded route and backend auth | Retryable partial/error states. |
| Create badge | Consequential | Creates badge and optional uploaded image | No delete API | Valid form; `admin` | Failure leaves UI unchanged; uploaded orphan cleanup not supported. |
| Change platform role | Privilege-changing | Rewrites full user DTO including role | Yes by another update | Names user and access impact; `admin`; self-change disabled | Failure retains old role; no audit/final-admin enforcement. |
| Delete user | Destructive | Deletes user plus authored posts/threads, badge awards, and unit links | No | Names user, scope, unaffected objects, irreversibility; `admin`; self-delete disabled in UI | Failure retains record; no restore/audit/final-admin protection. |
| Delete course | Destructive | Deletes course record | No | Names course, learner-access impact, no archive/restore; `admin` | Failure retains record; no restore/audit. |
| Switch organization | Consequential | Reissues token with active organization | Yes | Existing shell interaction | Existing session recovery. Not redesigned here. |

Unsupported disable/restore, invitation resend, organization archive/delete, badge edit/delete, moderation, and platform-setting actions are absent.
