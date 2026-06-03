from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from http.cookies import SimpleCookie
from typing import Optional

from .config import SETTINGS


def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return digest


def _sign(payload: bytes) -> str:
    secret = SETTINGS.session_secret.encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def create_session_value(user_id: int, ttl_seconds: int = 60 * 60 * 12) -> str:
    content = {
        "uid": user_id,
        "exp": int(time.time()) + ttl_seconds,
    }
    payload = json.dumps(content, separators=(",", ":")).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).decode("ascii")
    signature = _sign(payload)
    return f"{encoded}.{signature}"


def parse_session_value(value: str) -> Optional[int]:
    try:
        encoded, signature = value.split(".", 1)
        payload = base64.urlsafe_b64decode(encoded.encode("ascii"))
        if not hmac.compare_digest(_sign(payload), signature):
            return None
        content = json.loads(payload.decode("utf-8"))
        if int(content.get("exp", 0)) < int(time.time()):
            return None
        return int(content["uid"])
    except Exception:
        return None


def get_session_user_id(cookie_header: str | None) -> Optional[int]:
    if not cookie_header:
        return None
    jar = SimpleCookie()
    jar.load(cookie_header)
    morsel = jar.get(SETTINGS.cookie_name)
    if morsel is None:
        return None
    return parse_session_value(morsel.value)


def build_session_cookie(user_id: int) -> tuple[str, str]:
    value = create_session_value(user_id)
    cookie = (
        f"{SETTINGS.cookie_name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={60 * 60 * 12}"
    )
    return "Set-Cookie", cookie


def build_cleared_session_cookie() -> tuple[str, str]:
    cookie = f"{SETTINGS.cookie_name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
    return "Set-Cookie", cookie
