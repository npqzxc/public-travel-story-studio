from __future__ import annotations

from .components import esc, nav_link, render_page_payload


def render_layout(
    *,
    title: str,
    body: str,
    page_id: str,
    current_user: dict | None = None,
    payload: dict | None = None,
) -> str:
    current_user_html = ""
    if current_user:
        current_user_html = f"""
        <div class="user-chip">
          <div>
            <strong>{esc(current_user["display_name"])}</strong>
            <span>{esc(current_user["role"].replace("_", " "))}</span>
          </div>
          <form method="post" action="/logout">
            <button class="ghost-button" type="submit">Sign out</button>
          </form>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <link rel="stylesheet" href="/static/styles.css" />
  </head>
  <body data-page="{esc(page_id)}">
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark">OD</div>
          <div>
            <h1>Travel Editor</h1>
            <p>Reliability workboard</p>
          </div>
        </div>
        <nav class="nav-links">
          {nav_link("/", "Dashboard")}
          {nav_link("/tickets", "Tickets")}
          {nav_link("/tickets/new", "Create Ticket")}
          {nav_link("/api/dashboard", "Dashboard API")}
          {nav_link("/api/tickets", "Tickets API")}
        </nav>
        {current_user_html}
      </aside>
      <main class="content">{body}</main>
    </div>
    {render_page_payload(payload)}
    <script type="module" src="/static/js/main.js"></script>
  </body>
</html>
"""
