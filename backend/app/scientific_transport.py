from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import hashlib
import hmac
import json
import secrets
from typing import Any


TRANSPORT_VERSION = "1"


def canonical_transport_message(
    payload: dict[str, Any], *, timestamp: str, nonce: str
) -> bytes:
    if not timestamp or not nonce:
        raise ValueError("transport timestamp and nonce are required")
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return f"{timestamp}\n{nonce}\n{canonical}".encode("utf-8")


def sign_prediction(
    payload: dict[str, Any], *, secret: str, timestamp: str, nonce: str
) -> str:
    if not secret:
        raise ValueError("transport secret is required")
    return hmac.new(
        secret.encode("utf-8"),
        canonical_transport_message(payload, timestamp=timestamp, nonce=nonce),
        hashlib.sha256,
    ).hexdigest()


def build_authenticated_prediction(
    payload: dict[str, Any],
    *,
    secret: str,
    timestamp: str | None = None,
    nonce: str | None = None,
) -> dict[str, Any]:
    """Wrap one canonical scientific prediction in an authenticated transport envelope."""
    if not secret:
        raise ValueError("producer transport secret is required")
    transport_timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    transport_nonce = nonce or secrets.token_urlsafe(24)
    scientific_payload = dict(payload)
    envelope = {
        "timestamp": transport_timestamp,
        "nonce": transport_nonce,
        "signature": sign_prediction(
            scientific_payload,
            secret=secret,
            timestamp=transport_timestamp,
            nonce=transport_nonce,
        ),
        "transport_version": TRANSPORT_VERSION,
    }
    # CeutIA v1.1 currently authenticates the three transport fields only.
    # Keep the version outside the signed envelope until the canonical transport
    # contract explicitly incorporates it; do not create a second contract here.
    envelope.pop("transport_version")
    return {**scientific_payload, "_transport": envelope}


__all__ = [
    "TRANSPORT_VERSION",
    "build_authenticated_prediction",
    "canonical_transport_message",
    "sign_prediction",
]
