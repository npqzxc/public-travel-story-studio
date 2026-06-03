from __future__ import annotations

from collections import Counter

from ..database import (
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
    add_comment,
    create_ticket,
    get_ticket,
    list_projects,
    list_team_members,
    list_tickets,
    update_ticket_status,
)
from ..serializers import (
    serialize_people,
    serialize_projects,
    serialize_ticket_collection,
    serialize_ticket_detail,
)


def ticket_list_context(filters: dict[str, str], current_user: dict) -> dict:
    tickets = list_tickets(filters)
    return {
        "tickets": tickets,
        "filters": filters,
        "members": list_team_members(),
        "current_user": current_user,
        "status_counts": dict(Counter(ticket["status"] for ticket in tickets)),
    }


def ticket_new_context(current_user: dict, values: dict[str, str] | None = None, error: str | None = None) -> dict:
    return {
        "projects": list_projects(),
        "members": list_team_members(),
        "current_user": current_user,
        "values": values or {},
        "error": error,
        "priority_options": PRIORITY_OPTIONS,
    }


def ticket_detail_context(ticket_id: int, current_user: dict, error: str | None = None) -> dict | None:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        return None
    return {
        "ticket": ticket,
        "members": list_team_members(),
        "current_user": current_user,
        "error": error,
        "status_options": STATUS_OPTIONS,
    }


def create_ticket_from_form(form: dict[str, str], reporter_id: int) -> int:
    required = ["project_id", "title", "description", "priority", "assignee_id", "due_date"]
    missing = [field for field in required if not form.get(field, "").strip()]
    if missing:
        raise ValueError("Please provide complete, valid ticket details.")
    if form["priority"] not in PRIORITY_OPTIONS:
        raise ValueError("Please choose a valid priority.")
    return create_ticket(
        project_id=int(form["project_id"]),
        title=form["title"],
        description=form["description"],
        priority=form["priority"],
        assignee_id=int(form["assignee_id"]),
        due_date=form["due_date"],
        reporter_id=reporter_id,
    )


def update_ticket_comment(ticket_id: int, user_id: int, body: str) -> None:
    if not body.strip():
        raise ValueError("Comment text cannot be empty.")
    add_comment(ticket_id, user_id, body)


def update_ticket_workflow(ticket_id: int, user_id: int, status: str) -> None:
    if status not in STATUS_OPTIONS:
        raise ValueError("Please choose a valid status.")
    update_ticket_status(ticket_id, user_id, status)


def ticket_api_list(filters: dict[str, str]) -> dict:
    return serialize_ticket_collection(filters, list_tickets(filters))


def ticket_api_detail(ticket_id: int) -> dict | None:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        return None
    return serialize_ticket_detail(ticket)


def get_team_payload() -> dict:
    return serialize_people(list_team_members())


def get_projects_payload() -> dict:
    return serialize_projects(list_projects())
