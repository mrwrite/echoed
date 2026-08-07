# Organization Isolation Verification

The backend tests create at least two schools with separate administrators/educators/learners, memberships, courses, course versions, sections, enrollments, lessons, sessions, invites, and progress/content records. Direct API identifiers and mismatched parent IDs are exercised rather than relying on Angular navigation.

| Attempt from Organization A against B | Result / evidence |
| --- | --- |
| List B members using A header | 403 path/header mismatch; `test_org_admin_scope.py` |
| Read B sections | only A sections returned; nested B section IDs concealed 404 |
| Invite to B | active membership plus header/path match required; grant role allowlist |
| Enroll non-member into A section | rejected; active same-org membership required |
| Start/end B lesson session | concealed 404; session query joins section organization |
| Combine A section with B lesson | concealed 404 parent mismatch |
| Create A section from B course version | concealed 404 |
| Mutate B unit as A content admin | 403 course-authoring capability denial |
| Read B learner progress by direct ID | learner ownership/teaching-section resolver returns 404 |
| Read B uploads | no organization ownership exists; paths are public by current product contract and recorded as a limitation |
| Mutate B forum content | forum is not organization-scoped; non-owner receives 403 unless platform moderator |
| B administrative reports | scoped section analytics conceals B section; global legacy analytics remains platform/teacher role based and needs future unified reporting scope |

The suite also retains V2 workspace/project/product organization-scope tests. Frontend route guards are not counted as isolation evidence. Remaining limitations arise where the data model itself lacks organization ownership (forum/uploads) and are not described as isolated.
