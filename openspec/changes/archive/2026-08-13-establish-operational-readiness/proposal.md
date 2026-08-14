## Why

Phase 10 made EchoEd observable, but the repository still lacks a fail-closed production configuration contract and verified procedures for deployment, migration, rollback, shutdown, backup, and recovery. This change turns the existing observability foundation into an evidence-backed operational contract without inventing hosting infrastructure or broadening product scope.

## What Changes

- Add centralized, environment-aware production configuration validation that rejects missing, unsafe, malformed, contradictory, or development-only settings before traffic is served.
- Enforce explicit allowed-host and trusted-proxy boundaries; untrusted forwarded metadata never becomes authoritative.
- Separate database migration execution from application startup and add deterministic pre-deploy, migration, post-deploy, health, rollback, and shutdown procedures.
- Define initial service objectives, alert conditions, operational ownership, escalation, and health-check usage based on Phase 10 signals.
- Add safe, executable backup, integrity-verification, restore, storage-recovery, configuration-rotation, and operational-drill tooling for repository-supported local/test data.
- Document database/application/configuration rollback boundaries, persistent-storage ownership, RPO/RTO assumptions, and infrastructure-dependent limitations.
- Preserve Phase 8 security and Phase 10 observability behavior, existing application workflows, and the separate future durable audit-event change.

## Capabilities

### New Capabilities

- `platform-operational-readiness`: Fail-closed production configuration, trusted network boundaries, deterministic release lifecycle, migration/rollback policy, health and shutdown integration, service objectives and alerts, backup/restore, storage ownership, secret rotation, and verified operational drills.

### Modified Capabilities

- None.

## Impact

- Backend startup/configuration, FastAPI middleware and lifecycle, SQLAlchemy resource shutdown, and Uvicorn/container launch behavior.
- Deployment/container and CI validation, Alembic operational procedures, and repository-provided operator scripts.
- Operations, architecture, security, roadmap, and platform-maturity documentation plus targeted backend tests and drill evidence.
- No database schema migration, commercial dependency, hosting-provider change, distributed state, authentication redesign, or application feature work is introduced.
