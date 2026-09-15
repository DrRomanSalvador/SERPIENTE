"""Producer-side authenticated transport for canonical CeutIA predictions."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import secrets


def canonical_transport_message(payload: dict[str, object], *, timestamp: str, nonce: str) -> bytes:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return f"{timestamp}\n{nonce}\n{canonical}".encode("utf-8")


def sign_prediction_transport(payload: dict[str, object], *, secret: str, timestamp: str | None = None, nonce: str | None = None) -> dict[str, str]:
    if not secret:
        raise ValueError("producer transport secret is required")
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    nonce = nonce or secrets.token_urlsafe(24)
    signature = hmac.new(secret.encode("utf-8"), canonical_transport_message(payload, timestamp=timestamp, nonce=nonce), hashlib.sha256).hexdigest()
    return {"timestamp": timestamp, "nonce": nonce, "signature": signature}


__all__ = ["canonical_transport_message", "sign_prediction_transport"]
