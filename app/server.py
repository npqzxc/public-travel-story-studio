from __future__ import annotations

import mimetypes
from pathlib import Path
from wsgiref.simple_server import make_server

from .config import SETTINGS
from .database import init_db
from .http import (
    extract_filters,
    html_response,
    json_response,
    method_not_allowed,
    not_found,
    parse_form,
    redirect,
)
from .services.auth_service import current_user_from_environ, login_user
from .services.dashboard_service import dashboard_api_payload, dashboard_page_context
from .services.ticket_service import (
    create_ticket_from_form,
    get_projects_payload,
    get_team_payload,
    ticket_api_detail,
    ticket_api_list,
    ticket_detail_context,
    ticket_list_context,
    ticket_new_context,
    update_ticket_comment,
    update_ticket_workflow,
)
from .templates.dashboard_page import render_dashboard_page
from .templates.login_page import render_login_page
from .templates.new_ticket_page import render_new_ticket_page
from .templates.ticket_detail_page import render_ticket_detail_page
from .templates.tickets_page import render_tickets_page

STATIC_DIR = Path(__file__).with_name("static")


def serve_static(start_response, path: str):
    asset_path = (STATIC_DIR / path.removeprefix("/static/")).resolve()
    if not str(asset_path).startswith(str(STATIC_DIR.resolve())) or not asset_path.exists():
        return not_found(start_response)
    data = asset_path.read_bytes()
    start_response(
        "200 OK",
        [
            ("Content-Type", mimetypes.guess_type(str(asset_path))[0] or "application/octet-stream"),
            ("Content-Length", str(len(data))),
        ],
    )
    return [data]


def _ticket_id_from_path(path: str) -> int | None:
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()

    if path.startswith("/static/"):
        return serve_static(start_response, path)

    if path == "/health":
        return json_response(start_response, {"ok": True, "app": "travel-editor"})

    if path == "/login":
        if method == "GET":
            return html_response(start_response, render_login_page())
        if method == "POST":
            form = parse_form(environ)
            authenticated = login_user(form.get("username", "").strip(), form.get("password", ""))
            if authenticated is None:
                return html_response(
                    start_response,
                    render_login_page("Incorrect username or password."),
                    "401 Unauthorized",
                )
            return redirect(start_response, "/", authenticated["headers"])
        return method_not_allowed(start_response)

    user = current_user_from_environ(environ)
    if user is None:
        return redirect(start_response, "/login")

    if path == "/logout":
        if method != "POST":
            return method_not_allowed(start_response)
        return redirect(start_response, "/login", login_user("", "", logout_only=True)["headers"])

    if path == "/":
        if method != "GET":
            return method_not_allowed(start_response)
        return html_response(start_response, render_dashboard_page(**dashboard_page_context(user)))

    if path == "/tickets":
        if method == "GET":
            return html_response(
                start_response,
                render_tickets_page(**ticket_list_context(extract_filters(environ), user)),
            )
        if method == "POST":
            form = parse_form(environ)
            try:
                ticket_id = create_ticket_from_form(form, user["id"])
            except ValueError as exc:
                return html_response(
                    start_response,
                    render_new_ticket_page(**ticket_new_context(user, form, str(exc))),
                    "400 Bad Request",
                )
            return redirect(start_response, f"/tickets/{ticket_id}")
        return method_not_allowed(start_response)

    if path == "/tickets/new":
        if method != "GET":
            return method_not_allowed(start_response)
        return html_response(start_response, render_new_ticket_page(**ticket_new_context(user)))

    if path.startswith("/tickets/") and path.endswith("/comments"):
        if method != "POST":
            return method_not_allowed(start_response)
        ticket_id = _ticket_id_from_path(path)
        if ticket_id is None:
            return not_found(start_response)
        form = parse_form(environ)
        try:
            update_ticket_comment(ticket_id, user["id"], form.get("body", ""))
        except ValueError as exc:
            detail_context = ticket_detail_context(ticket_id, user, error=str(exc))
            if detail_context is None:
                return not_found(start_response)
            return html_response(
                start_response,
                render_ticket_detail_page(**detail_context),
                "400 Bad Request",
            )
        return redirect(start_response, f"/tickets/{ticket_id}")

    if path.startswith("/tickets/") and path.endswith("/status"):
        if method != "POST":
            return method_not_allowed(start_response)
        ticket_id = _ticket_id_from_path(path)
        if ticket_id is None:
            return not_found(start_response)
        form = parse_form(environ)
        try:
            update_ticket_workflow(ticket_id, user["id"], form.get("status", ""))
        except ValueError as exc:
            detail_context = ticket_detail_context(ticket_id, user, error=str(exc))
            if detail_context is None:
                return not_found(start_response)
            return html_response(
                start_response,
                render_ticket_detail_page(**detail_context),
                "400 Bad Request",
            )
        return redirect(start_response, f"/tickets/{ticket_id}")

    if path.startswith("/tickets/"):
        if method != "GET":
            return method_not_allowed(start_response)
        ticket_id = _ticket_id_from_path(path)
        if ticket_id is None:
            return not_found(start_response)
        detail_context = ticket_detail_context(ticket_id, user)
        if detail_context is None:
            return not_found(start_response)
        return html_response(start_response, render_ticket_detail_page(**detail_context))

    if path == "/api/dashboard" and method == "GET":
        return json_response(start_response, dashboard_api_payload())

    if path == "/api/tickets" and method == "GET":
        return json_response(start_response, ticket_api_list(extract_filters(environ)))

    if path.startswith("/api/tickets/") and method == "GET":
        ticket_id = _ticket_id_from_path(path.replace("/api", "", 1))
        if ticket_id is None:
            return not_found(start_response)
        payload = ticket_api_detail(ticket_id)
        if payload is None:
            return not_found(start_response)
        return json_response(start_response, payload)

    if path == "/api/projects" and method == "GET":
        return json_response(start_response, get_projects_payload())

    if path == "/api/team" and method == "GET":
        return json_response(start_response, get_team_payload())

    return not_found(start_response)


def main() -> None:
    SETTINGS.data_dir.mkdir(parents=True, exist_ok=True)
    init_db()
    with make_server(SETTINGS.host, SETTINGS.port, application) as httpd:
        print(f"Travel Editor listening on http://{SETTINGS.host}:{SETTINGS.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
