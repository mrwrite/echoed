# product-catalog Specification

## ADDED Requirements

### Requirement: Product SHALL wrap existing runtime objects
EchoEd SHALL introduce Product as the package-level object above existing education runtime objects.

Supported initial product backing types:

- Course
- Program or Learning Path
- Artifact or Download
- Future membership hub
- Future coaching or review session

#### Scenario: Existing course appears as product
- **WHEN** an existing course is migrated into V2
- **THEN** a course-backed product represents it in the product catalog
- **AND** the original course, units, lessons, activities, and progress records remain unchanged

#### Acceptance Criteria
- Every existing course can be represented by a product.
- Existing `/api/courses` behavior remains intact.
- Product catalog can link to existing course management pages during migration.

### Requirement: Product catalog SHALL become the creator-facing inventory
The V2 product catalog SHALL show products, status, type, backing object, review state, access state, and publishing readiness.

#### Scenario: Creator reviews products
- **WHEN** a creator opens Products
- **THEN** EchoEd shows course-backed products and future product types in one inventory

#### Acceptance Criteria
- Admin Courses can be remapped into Products without deleting the old route.
- Product terminology is introduced before replacing underlying models.

## MODIFIED Requirements

### Requirement: Programs SHALL be repositioned as learning paths
Existing programs SHALL be visible as learning paths or product bundles in V2 while preserving current program behavior.

#### Scenario: Learner views program-backed product
- **WHEN** a learner opens a program-backed product
- **THEN** EchoEd can reuse existing Program, ProgramCourse, progress, assessment, and certification behavior

#### Acceptance Criteria
- Existing program routes remain compatible.
- Program progress remains intact.

