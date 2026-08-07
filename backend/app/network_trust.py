from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import re

from fastapi import Request

from app.operational_config import OperationalSettings


_FORWARDED_HOST = re.compile(r"^[A-Za-z0-9.-]+(?::[0-9]{1,5})?$")


@dataclass(frozen=True)
class NetworkContext:
    client_ip: str
    scheme: str
    host: str
    proxy_trusted: bool


def _peer_is_trusted(peer: str, settings: OperationalSettings) -> bool:
    try:
        address = ipaddress.ip_address(peer)
    except ValueError:
        return False
    return any(address in network for network in settings.trusted_proxy_networks)


def resolve_network_context(request: Request, settings: OperationalSettings) -> NetworkContext:
    peer = request.client.host if request.client else "unknown"
    direct_host = request.headers.get("host", "unknown")[:255]
    if not settings.trust_proxy_headers or not _peer_is_trusted(peer, settings):
        return NetworkContext(peer, request.url.scheme, direct_host, False)

    forwarded_for = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    try:
        client_ip = str(ipaddress.ip_address(forwarded_for))
    except ValueError:
        client_ip = peer
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    scheme = forwarded_proto if forwarded_proto in {"http", "https"} else request.url.scheme
    forwarded_host = request.headers.get("x-forwarded-host", "").split(",", 1)[0].strip()
    host = forwarded_host if _FORWARDED_HOST.fullmatch(forwarded_host) else direct_host
    return NetworkContext(client_ip, scheme, host, True)
