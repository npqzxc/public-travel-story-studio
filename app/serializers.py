from __future__ import annotations

from collections import Counter
from typing import Any


def serialize_ticket_summary(ticket: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": ticket["id"],
        "project_id": ticket["project_id"],
        "project_code": ticket["project_code"],
        "project_name": ticket["project_name"],
        "title": ticket["title"],
        "status": ticket["status"],
        "priority": ticket["priority"],
        "due_date": ticket["due_date"],
        "updated_at": ticket["updated_at"],
        "assignee_name": ticket["assignee_name"],
        "assignee_username": ticket["assignee_username"],
        "comment_count": ticket.get("comment_count", len(ticket.get("comments", []))),
    }


def serialize_ticket_detail(ticket: dict[str, Any]) -> dict[str, Any]:
    return {
        **serialize_ticket_summary(ticket),
        "description": ticket["description"],
        "reporter_name": ticket["reporter_name"],
        "comments": ticket["comments"],
        "events": ticket["events"],
    }


def serialize_dashboard(summary: dict[str, Any]) -> dict[str, Any]:
    status_counts = summary["status_counts"]
    priority_counts = summary["priority_counts"]
    top_status = ""
    if status_counts:
        top_status = max(status_counts.items(), key=lambda item: item[1])[0]
    return {
        **summary,
        "spotlights": [
            {"label": "Most common state", "value": top_status.replace("_", " ") if top_status else "n/a"},
            {"label": "Urgent tickets", "value": priority_counts.get("urgent", 0)},
            {"label": "Due soon", "value": summary["tickets_due_soon"]},
        ],
    }


def serialize_ticket_collection(filters: dict[str, str], tickets: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(ticket["status"] for ticket in tickets)
    return {
        "filters": filters,
        "items": [serialize_ticket_summary(ticket) for ticket in tickets],
        "meta": {
            "count": len(tickets),
            "status_counts": dict(status_counts),
        },
    }


def serialize_people(people: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": people}


def serialize_projects(projects: list[dict[str, Any]]) -> dict[str, Any]:
    return {"items": projects}
