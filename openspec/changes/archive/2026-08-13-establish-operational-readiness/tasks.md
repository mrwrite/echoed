## 1. Baseline and operational contract

- [x] 1.1 Record branch, commit, dirty-tree boundaries, OpenSpec states, Phase 10 dependency, actual test baselines, deployment/configuration/database/storage/CI/startup findings, and preserve unrelated work
- [x] 1.2 Create strictly valid proposal, design, capability specification, and concrete task artifacts with explicit non-goals and durable-audit boundary
- [x] 1.3 Document the canonical production configuration contract and environment-separation rules without secret values

## 2. Configuration and network trust

- [x] 2.1 Implement centralized environment-aware operational settings and fail-closed production validation before application initialization
- [x] 2.2 Add a validation-only operator command and tests for valid, missing, unsafe, malformed, contradictory, development, test, and production configurations
- [x] 2.3 Enforce allowed hosts and explicit peer IP/CIDR proxy trust while ignoring spoofed forwarding metadata
- [x] 2.4 Add trusted-host/proxy tests for allowed, rejected, trusted, malformed, and untrusted requests

## 3. Release, migration, health, and shutdown lifecycle

- [x] 3.1 Remove automatic production migrations from normal startup and provide explicit migration/head-verification and preflight commands
- [x] 3.2 Implement deterministic deployment and post-deployment verification automation using liveness, readiness, and safe smoke gates
- [x] 3.3 Add bounded graceful-shutdown lifecycle events, database resource cleanup, and server shutdown configuration
- [x] 3.4 Add tests/drills for migration failure/gating, startup, health dependency failure, failed post-deploy checks, lifecycle shutdown, and resource cleanup
- [x] 3.5 Document deployment, migration compatibility/irreversibility, application/configuration/database rollback, health integration, and shutdown procedures

## 4. Backup, restore, storage, and rotation

- [x] 4.1 Implement safe disposable SQLite/upload backup bundles with versioned manifests, checksums, integrity verification, isolated restore, and production-data refusal boundaries
- [x] 4.2 Add tests for backup creation, manifest integrity, corrupted-backup rejection, database restore usability, asset restore, and target safety
- [x] 4.3 Document production database/upload backup scope, scheduling/retention/encryption/separation, restore ownership, static/upload sources of truth, and loss behavior
- [x] 4.4 Establish defensible conditional RPO/RTO targets and document production-native PostgreSQL restore validation requirements
- [x] 4.5 Document and safely simulate environment-specific secret/configuration rotation, verification, invalidation, emergency rollback, and storage recovery

## 5. SLOs, alerts, drills, and operational guidance

- [x] 5.1 Define pragmatic availability, success/error, latency, readiness, authentication, and rate-limit indicators/targets/windows with process-local limitations
- [x] 5.2 Define alert signals, conditions, severities, owner roles, escalation paths, responses, and related runbooks without claiming external delivery
- [x] 5.3 Implement a repeatable isolated operational drill runner covering invalid production configuration, database/readiness failure, startup/shutdown, health, deployment failure, backup/restore, rollback, rotation, and storage recovery
- [x] 5.4 Execute drills, capture prerequisites/expected/observed/pass-fail evidence, measure backup/restore timings, and remove disposable artifacts
- [x] 5.5 Update operations, incident, architecture, security, README, roadmap, and platform-maturity documents with cross-references and explicit deferred infrastructure/audit work

## 6. Verification and completion evidence

- [x] 6.1 Run targeted operational tests plus the complete backend suite and repository-supported backend compile/static/lint/format checks without baseline regression
- [x] 6.2 Run the complete Angular suite, production build, configured frontend lint/format checks, and production dependency audit without baseline regression
- [x] 6.3 Run the complete Playwright suite and verify Phase 8/10 health, privacy, authorization, rate-limit, upload, metrics, and logging boundaries remain intact
- [x] 6.4 Run strict OpenSpec validation, `git diff --check`, secret/temp-artifact checks, and remove temporary servers, databases, backups, logs, and generated drill data
- [x] 6.5 Publish exact Phase 11 verification evidence, known limitations, deferred work, recommended next change, and mark tasks complete only where implementation/evidence exists
