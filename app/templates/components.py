from __future__ import annotations

import html
import json
from typing import Any


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def nav_link(href: str, label: str) -> str:
    return f'<a href="{esc(href)}">{esc(label)}</a>'


def status_badge(value: str) -> str:
    return f'<span class="badge badge-{esc(value)}">{esc(value.replace("_", " "))}</span>'


def priority_badge(value: str) -> str:
    return f'<span class="badge priority-{esc(value)}">{esc(value)}</span>'


def render_page_payload(payload: dict[str, Any] | None) -> str:
    if payload is None:
        payload = {}
    return f'<script type="application/json" id="page-bootstrap">{html.escape(json.dumps(payload))}</script>'
