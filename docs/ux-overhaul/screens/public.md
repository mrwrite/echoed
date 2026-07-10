# Public Screen Specifications

## Landing Page

- Role: public, contributor, educator, family.
- Goal: understand EchoEd's mission and enter the right path.
- Route/component: `/`, `LandingComponent`.
- Main action: sign in or explore public learning products.
- Layout: first viewport shows EchoEd identity, mission, public product entry, community project signal; no investor language.
- Mobile: brand, mission, primary action, secondary product link.
- States: public product loading may be deferred to product pages.
- API: none required.
- Backend changes: none.
- Analytics: landing CTA click, public products click, login click.

## Public Products

- Route/component: `/products`, `PublicProductsComponent`.
- Goal: browse published learning products.
- Actions: filter/search, open product, sign in/register.
- API: `/api/public/products`.
- Empty: "No public learning products are available yet."
- Error: retry with nontechnical copy.
- Accessibility: product cards need headings and status labels.

## Public Product Detail

- Route/component: `/products/:slug`, `PublicProductDetailComponent`.
- Goal: inspect a public product/course package.
- API: `/api/public/products/{slug}`.
- Layout: title, audience, description, learning outcomes, source/provenance, access action.
- Backend changes: none unless source/provenance fields are missing for desired content depth.

## Login

- Route/component: `/login`, `LoginComponent`.
- Goal: sign in and route to correct role space.
- API: `/api/auth/token`, then session bootstrap `/api/orgs`.
- States: submitting, invalid credentials, bootstrap failure, onboarding required.
- Validation: username/password required.
- Accessibility: show/hide password button has accessible name; errors linked to form.
- Backend changes: none.

## Registration

- Route/component: `/registration`, `RegistrationComponent`.
- Goal: create account and optionally begin organization setup.
- API: `/api/meta/enums`, `/api/auth/register`.
- States: loading roles, enum fallback, password mismatch, registration failed.
- Role treatment: student, teacher, parent, instructor are exposed; parent/instructor support must set expectation.
- Backend changes: none for current registration; parent portal would require future backend contracts.

## Organization Onboarding

- Route/component: `/onboarding/organization`, `OnboardingOrganizationComponent`.
- Goal: create/switch organization after account creation.
- API: `/api/orgs`, `/api/orgs/{id}/switch`.
- States: prefilled pending setup, submit pending, failure preserves input.
- Accessibility: clear required fields, role-specific organization type explanation.

## Error and Not Found

- Current: `AccessDeniedComponent` and wildcard redirect.
- Proposed: add contextual not-found view later.
- Backend changes: none.
