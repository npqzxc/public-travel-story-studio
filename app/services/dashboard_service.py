from __future__ import annotations

from ..database import dashboard_summary
from ..serializers import serialize_dashboard


def dashboard_api_payload() -> dict:
    return serialize_dashboard(dashboard_summary())


def dashboard_page_context(current_user: dict) -> dict:
    summary = dashboard_api_payload()
    return {
        "summary": summary,
        "current_user": current_user,
    }
