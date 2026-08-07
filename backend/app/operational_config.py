from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import os
from pathlib import Path
import re
from typing import Mapping
from urllib.parse import urlparse

from dotenv import load_dotenv


class OperationalConfigurationError(RuntimeError):
    """Raised when runtime configuration is unsafe or internally inconsistent."""


_ENVIRONMENTS = {"development", "test", "staging", "production"}
_UNSAFE_SECRETS = {"secret", "testsecret", "changeme", "change-me", "development-secret"}
_UNSAFE_DATABASE_MARKERS = ("your_secure_password", ":postgres@", ":password@")
_HOST_PATTERN = re.compile(r"^(?:\*\.)?[A-Za-z0-9.-]+(?::[0-9]{1,5})?$")


def _boolean(name: str, default: bool, values: Mapping[str, str]) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise OperationalConfigurationError(f"{name}: expected true or false")


def _positive_int(name: str, default: int, values: Mapping[str, str]) -> int:
    raw = values.get(name)
    if raw is None:
        return default
    try:
        result = int(raw)
    except ValueError as exc:
        raise OperationalConfigurationError(f"{name}: expected a positive integer") from exc
    if result <= 0:
        raise OperationalConfigurationError(f"{name}: expected a positive integer")
    return result


def _csv(name: str, raw: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in raw.split(",") if item.strip())
    if not values:
        raise OperationalConfigurationError(f"{name}: at least one value is required")
    return values


def _origin(name: str, raw: str, *, require_https: bool) -> str:
    parsed = urlparse(raw)
    if parsed.scheme not in ({"https"} if require_https else {"http", "https"}):
        raise OperationalConfigurationError(f"{name}: expected an absolute {'HTTPS' if require_https else 'HTTP(S)'} URL")
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise OperationalConfigurationError(f"{name}: expected a credential-free absolute origin")
    if parsed.path not in {"", "/"}:
        raise OperationalConfigurationError(f"{name}: URL paths are not allowed")
    return raw.rstrip("/")


@dataclass(frozen=True)
class OperationalSettings:
    environment: str
    database_url: str
    jwt_secret: str
    allowed_hosts: tuple[str, ...]
    allowed_origins: tuple[str, ...]
    external_base_url: str | None
    trust_proxy_headers: bool
    trusted_proxy_networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]
    storybook_path: Path
    colorings_path: Path
    badges_path: Path
    persistent_storage_acknowledged: bool
    auto_migrate_on_startup: bool
    release_version: str | None
    deployment_id: str | None
    graceful_shutdown_seconds: int


def load_operational_settings(environ: Mapping[str, str] | None = None) -> OperationalSettings:
    if environ is None:
        environment_hint = os.environ.get("APP_ENV", "development").strip().lower() or "development"
        if environment_hint != "production":
            load_dotenv(override=False)
        values: Mapping[str, str] = os.environ
    else:
        values = environ

    environment = values.get("APP_ENV", "development").strip().lower() or "development"
    if environment not in _ENVIRONMENTS:
        raise OperationalConfigurationError("APP_ENV: expected development, test, staging, or production")
    production = environment == "production"

    database_url = values.get("DATABASE_URL", "").strip()
    if not database_url:
        if production:
            raise OperationalConfigurationError("DATABASE_URL: required in production")
        database_url = "sqlite:///./echoed.db"
    parsed_database = urlparse(database_url)
    if not parsed_database.scheme:
        raise OperationalConfigurationError("DATABASE_URL: expected a valid database URL")
    if production:
        if parsed_database.scheme not in {"postgresql", "postgresql+psycopg2"}:
            raise OperationalConfigurationError("DATABASE_URL: production requires PostgreSQL")
        if any(marker in database_url.lower() for marker in _UNSAFE_DATABASE_MARKERS):
            raise OperationalConfigurationError("DATABASE_URL: development/default credentials are forbidden")

    jwt_secret = values.get("JWT_SECRET", "").strip()
    if not jwt_secret:
        raise OperationalConfigurationError("JWT_SECRET: required")
    if production and (len(jwt_secret) < 32 or jwt_secret.lower() in _UNSAFE_SECRETS):
        raise OperationalConfigurationError("JWT_SECRET: production secret does not meet the safety policy")

    raw_hosts = values.get("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
    allowed_hosts = _csv("ALLOWED_HOSTS", raw_hosts)
    for host in allowed_hosts:
        if host == "*" or not _HOST_PATTERN.fullmatch(host):
            raise OperationalConfigurationError("ALLOWED_HOSTS: contains an unsafe or malformed host")
    if production and any(host.split(":", 1)[0] in {"localhost", "127.0.0.1"} for host in allowed_hosts):
        raise OperationalConfigurationError("ALLOWED_HOSTS: local development hosts are forbidden in production")

    raw_origins = values.get("FRONTEND_URL", "http://localhost:4200,http://127.0.0.1:4200")
    allowed_origins = tuple(
        _origin("FRONTEND_URL", origin, require_https=production)
        for origin in _csv("FRONTEND_URL", raw_origins)
    )
    external_raw = values.get("EXTERNAL_BASE_URL", "").strip()
    external_base_url = _origin("EXTERNAL_BASE_URL", external_raw, require_https=production) if external_raw else None
    if production and not external_base_url:
        raise OperationalConfigurationError("EXTERNAL_BASE_URL: required in production")

    trust_proxy_headers = _boolean("TRUST_PROXY_HEADERS", False, values)
    proxy_entries = tuple(item.strip() for item in values.get("TRUSTED_PROXY_IPS", "").split(",") if item.strip())
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for entry in proxy_entries:
        try:
            networks.append(ipaddress.ip_network(entry, strict=False))
        except ValueError as exc:
            raise OperationalConfigurationError("TRUSTED_PROXY_IPS: contains an invalid IP address or CIDR") from exc
    if trust_proxy_headers and not networks:
        raise OperationalConfigurationError("TRUSTED_PROXY_IPS: required when proxy headers are trusted")
    if production and proxy_entries and not trust_proxy_headers:
        raise OperationalConfigurationError("TRUST_PROXY_HEADERS: must explicitly enable configured proxy trust")

    paths = {
        "STORYBOOK_PATH": Path(values.get("STORYBOOK_PATH", "./storybook")),
        "COLORINGS_PATH": Path(values.get("COLORINGS_PATH", "./colorings")),
        "BADGES_PATH": Path(values.get("BADGES_PATH", "./badges")),
    }
    persistent_ack = _boolean("PERSISTENT_STORAGE_ACKNOWLEDGED", False, values)
    if production:
        if not persistent_ack:
            raise OperationalConfigurationError("PERSISTENT_STORAGE_ACKNOWLEDGED: required in production")
        if any(not path.is_absolute() for path in paths.values()):
            raise OperationalConfigurationError("UPLOAD_STORAGE: production paths must be absolute")
        if len({str(path.resolve()) for path in paths.values()}) != len(paths):
            raise OperationalConfigurationError("UPLOAD_STORAGE: storage paths must be distinct")

    auto_migrate = _boolean("AUTO_MIGRATE_ON_STARTUP", False, values)
    if production and auto_migrate:
        raise OperationalConfigurationError("AUTO_MIGRATE_ON_STARTUP: forbidden in production")
    release_version = values.get("RELEASE_VERSION", "").strip() or None
    deployment_id = values.get("DEPLOYMENT_ID", "").strip() or None
    if production and (not release_version or not deployment_id):
        raise OperationalConfigurationError("RELEASE_IDENTITY: RELEASE_VERSION and DEPLOYMENT_ID are required")

    if production:
        if values.get("LOG_FORMAT", "").strip().lower() != "json":
            raise OperationalConfigurationError("LOG_FORMAT: production requires json")
        if not _boolean("METRICS_ENABLED", True, values):
            raise OperationalConfigurationError("METRICS_ENABLED: production operational metrics must be enabled")
        if not _boolean("REQUEST_LOGGING_ENABLED", True, values):
            raise OperationalConfigurationError("REQUEST_LOGGING_ENABLED: production request diagnostics must be enabled")
        if _boolean("METRICS_ENDPOINT_ENABLED", False, values) and not values.get("METRICS_ACCESS_TOKEN", "").strip():
            raise OperationalConfigurationError("METRICS_ACCESS_TOKEN: required when metrics export is enabled")

    return OperationalSettings(
        environment=environment,
        database_url=database_url,
        jwt_secret=jwt_secret,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
        external_base_url=external_base_url,
        trust_proxy_headers=trust_proxy_headers,
        trusted_proxy_networks=tuple(networks),
        storybook_path=paths["STORYBOOK_PATH"],
        colorings_path=paths["COLORINGS_PATH"],
        badges_path=paths["BADGES_PATH"],
        persistent_storage_acknowledged=persistent_ack,
        auto_migrate_on_startup=auto_migrate,
        release_version=release_version,
        deployment_id=deployment_id,
        graceful_shutdown_seconds=_positive_int("GRACEFUL_SHUTDOWN_SECONDS", 30, values),
    )
