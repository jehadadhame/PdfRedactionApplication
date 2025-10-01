# app/services/callback.py
import json, hmac, hashlib, time
import httpx
from typing import Any
from ..core.config import settings
from ..utils.http import http_client

def _to_body_bytes(payload: Any) -> bytes:
    # If it's a Pydantic v2 model, use its JSON serializer
    if hasattr(payload, "model_dump_json"):
        return payload.model_dump_json().encode("utf-8")
    # If it's a dict/list, fall back to json.dumps with default=str (handles UUID, datetime, etc.)
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")


def post_result(callback_url: str, payload, max_attempts: int = 4) -> None:
    body = _to_body_bytes(payload)
    backoff = [0, 1, 2, 4]

    for delay in backoff[:max_attempts]:
        if delay:
            time.sleep(delay)
        try:
            with http_client() as c:
                r = c.post(
                    callback_url,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                    },
                    auth=(settings.accounting_user, settings.accounting_pass.get_secret_value()),
                )
                if 200 <= r.status_code < 300:
                    return
        except Exception:
            pass
    raise RuntimeError("Failed to POST callback")
