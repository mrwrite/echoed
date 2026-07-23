# Dependency and Code-Quality Review

Date: 2026-07-23

## Frontend

- `package-lock.json` provides reproducible npm resolution; direct Angular ranges were normalized to exact 20.3.25 during the security patch.
- Production dependencies are Angular, CDK, and Zone.js. Stats show no duplicate Angular runtime in the emitted graph and no CommonJS warning.
- Angular CDK drag/drop is genuinely used by the course wizard and is now confined to lazy feature chunks.
- `uuid` was imported from an undeclared transitive dependency. Phase 7 replaced it with `crypto.randomUUID()` and removed the unused `@types/uuid` package, eliminating a fragile implicit runtime dependency.
- `@angular/platform-browser-dynamic` is deprecated upstream but remains required by the current Karma dynamic testing environment. Removal belongs with a test-runner migration, not this patch.
- `@angular/animations` is deprecated in the installed Angular line but remains used by the shared header/home animations. Replacing it would change UI behavior and is deferred.
- CSS/style/Sass loaders are development build tooling and are not emitted in production.
- Angular production optimization/tree shaking and output hashing are active; production source maps are off. Development maps remain on.
- No lint target or script is configured. Type checking occurs through Angular build/test compilation; a dedicated `tsc --noEmit`/lint gate should be evaluated separately.

## Vulnerability results

- Before patch, `npm audit --omit=dev` reported eight production findings: six high and two moderate across Angular 20.3.21.
- Phase 7 upgraded the coordinated runtime/compiler packages to 20.3.25, the fixed version identified by the advisories.
- The full development tree initially reported 37 findings (including two critical); after dependency cleanup/security patch it reported 29 (four low, seven moderate, sixteen high, two critical). These are predominantly build/test transitive packages and require a separate nonbreaking-toolchain review; `npm audit fix --force` was not used.
- Final production-only audit and full regression results are recorded in `phase-7-verification.md`.

## Backend

- `backend/requirements.txt` uses unpinned top-level names and there is no committed resolved lock/constraints file. Builds are not reproducible over time.
- Runtime and test dependencies are mixed in one file (`pytest`, `pytest-cov`, `httpx` ship in the same install set).
- `passlib[bcrypt]` and direct `bcrypt` overlap; code uses direct bcrypt while passlib appears unused. Remove only after an import/test scan in a dedicated dependency cleanup because authentication is high risk.
- Both `python-jose` and bcrypt are security-sensitive; establish advisory tooling and pin/upgrade policy.
- Pydantic v2 emits class-config deprecation warnings across many schemas; a mechanical `ConfigDict` migration should be separate and fully tested.
- SQLAlchemy models use deprecated naive `datetime.utcnow` defaults broadly; timezone migration has persistence and compatibility implications and is not a Phase 7 mechanical fix.
- No committed `pip-audit`, Dependabot/Renovate, SBOM, or vulnerability CI configuration was found.

## Recommended follow-up

Create a bounded dependency/toolchain OpenSpec under operational readiness: split runtime/dev requirements, adopt a lock/constraints workflow, add production and development advisory gates with an exception policy, modernize lint/type-check scripts, and schedule deprecation migrations without combining them with product work.
