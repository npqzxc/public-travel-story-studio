from __future__ import annotations

from .. import auth
from ..database import authenticate_user, get_user


def current_user_from_environ(environ: dict[str, object]):
    user_id = auth.get_session_user_id(environ.get("HTTP_COOKIE"))
    if user_id is None:
        return None
    return get_user(user_id)


def login_user(username: str, password: str, logout_only: bool = False):
    if logout_only:
        return {"headers": [auth.build_cleared_session_cookie()]}
    user = authenticate_user(username, password)
    if user is None:
        return None
    return {
        "user": user,
        "headers": [auth.build_session_cookie(user["id"])],
    }
