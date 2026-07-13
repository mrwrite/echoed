# Admin Badge Data Contract

Date: 2026-07-13

| Field/capability | Verified contract | Admin UI behavior |
| --- | --- | --- |
| ID | UUID | Used only for API identity; not displayed. |
| Name | `title`, required | Displayed and searchable. |
| Description | Optional text | Displayed; missing value is stated. |
| Image | Optional `image_url` | Named image alt text; explicit missing-image alternative. |
| Earning criteria | No field/API | Not invented or editable. |
| Course/program relation | No badge relation in response | Not shown. Certifications may reference a badge separately. |
| Active/inactive | No field/API | Not shown. |
| Create | `POST /api/badges`, `admin` | Supported with validation and success/error states. |
| Upload | `POST /api/upload/badge`, `admin` | Optional image upload during creation. |
| Edit | No endpoint | Read-only unavailable. |
| Delete/archive | No endpoint | No control or confirmation shown. |
| Assignment | `POST /api/students/{student_id}/badges/{badge_id}`, `admin` | Verified but not added to broad badge administration because no scoped learner-selection workflow was approved. |

Badge reads require authentication but are not admin-only. `super_admin` therefore receives a read-only catalog; it receives no create/upload control.
