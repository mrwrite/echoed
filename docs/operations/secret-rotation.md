# Secret and Configuration Rotation

1. Inventory the credential owner, consumers, expiry, and rollback method without recording values. Prepare a replacement in the target environment's secret manager.
2. Validate a production-equivalent configuration with the replacement using `python -m scripts.validate_operational_config`; do not echo the environment.
3. For database credentials, create/authorize the replacement, deploy dependent instances, verify readiness and representative transactions, then revoke the old credential. For JWT signing, current architecture has one key and no key ring/revocation: rotating invalidates all existing tokens; schedule and communicate reauthentication.
4. For metrics access, update scraper and application in a controlled window; keep the endpoint private/disabled until both sides match.
5. Verify liveness/readiness, authentication, metrics access, logs, and error rates. Revoke the old credential where supported and record only identifier/version/time/result in operational evidence.
6. Emergency rollback restores the prior credential version only if it has not been revoked/compromised; otherwise issue another replacement and contain affected access.

Development, test, staging, and production use distinct credentials, databases, deployment IDs, origins, hosts, and storage. Production never loads dotenv. The drill runner validates two independently supplied synthetic secrets and emits neither. Multi-key JWT overlap and revocation require a future identity/security change and are not implemented here.
