from __future__ import annotations

import json
from urllib.parse import parse_qs


def parse_form(environ: dict[str, object]) -> dict[str, str]:
    length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(length).decode("utf-8") if length else ""
    parsed = parse_qs(raw)
    return {key: values[0] for key, values in parsed.items()}


def extract_filters(environ: dict[str, object]) -> dict[str, str]:
    query = parse_qs(environ.get("QUERY_STRING", ""))
    return {key: value[0] for key, value in query.items() if value and value[0].strip()}


def redirect(start_response, location: str, headers: list[tuple[str, str]] | None = None):
    response_headers = [("Location", location)]
    if headers:
        response_headers.extend(headers)
    start_response("302 Found", response_headers)
    return [b""]


def html_response(start_response, body: str, status: str = "200 OK", headers: list[tuple[str, str]] | None = None):
    encoded = body.encode("utf-8")
    response_headers = [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(encoded)))]
    if headers:
        response_headers.extend(headers)
    start_response(status, response_headers)
    return [encoded]


def json_response(start_response, payload: object, status: str = "200 OK"):
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    start_response(
        status,
        [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(encoded)))],
    )
    return [encoded]


def not_found(start_response):
    return html_response(start_response, "<h1>Not found</h1>", "404 Not Found")


def method_not_allowed(start_response):
    return html_response(start_response, "<h1>Method not allowed</h1>", "405 Method Not Allowed")
