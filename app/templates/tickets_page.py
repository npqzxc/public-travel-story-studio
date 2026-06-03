from __future__ import annotations

from .components import esc, priority_badge, status_badge
from .layout import render_layout


def render_tickets_page(tickets: list[dict], filters: dict, members: list[dict], current_user: dict, status_counts: dict) -> str:
    member_options = '<option value="">Anyone</option>' + "".join(
        f'<option value="{esc(member["username"])}" {"selected" if filters.get("assignee") == member["username"] else ""}>{esc(member["display_name"])}</option>'
        for member in members
    )
    status_options = '<option value="">Any status</option>' + "".join(
        f'<option value="{value}" {"selected" if filters.get("status") == value else ""}>{esc(value.replace("_", " "))}</option>'
        for value in ["todo", "in_progress", "blocked", "review", "done"]
    )
    priority_options = '<option value="">Any priority</option>' + "".join(
        f'<option value="{value}" {"selected" if filters.get("priority") == value else ""}>{esc(value)}</option>'
        for value in ["low", "medium", "high", "urgent"]
    )
    rows = "".join(
        f"""
        <tr>
          <td><a href="/tickets/{ticket["id"]}">{esc(ticket["project_code"])}-{ticket["id"]}</a></td>
          <td><strong>{esc(ticket["title"])}</strong><p class="muted">{esc(ticket["project_name"])}</p></td>
          <td>{status_badge(ticket["status"])}</td>
          <td>{priority_badge(ticket["priority"])}</td>
          <td>{esc(ticket["assignee_name"])}</td>
          <td>{ticket["comment_count"]}</td>
          <td>{esc(ticket["updated_at"])}</td>
        </tr>
        """
        for ticket in tickets
    )
    body = f"""
    <header class="page-header">
      <div>
        <p class="eyebrow">Queue view</p>
        <h2>Tickets</h2>
        <p>Filter open work by status, assignee or keyword.</p>
      </div>
      <a class="primary-link" href="/tickets/new">Create ticket</a>
    </header>
    <section class="tickets-layout">
      <div class="tickets-main">
        <section class="panel filter-panel">
          <form class="filter-grid" method="get" action="/tickets">
            <label>Search<input name="query" value="{esc(filters.get("query", ""))}" placeholder="billing, audit, export" /></label>
            <label>Status<select name="status">{status_options}</select></label>
            <label>Priority<select name="priority">{priority_options}</select></label>
            <label>Assignee<select name="assignee">{member_options}</select></label>
            <button type="submit">Apply filters</button>
          </form>
        </section>
        <section class="panel">
          <table>
            <thead>
              <tr><th>Ticket</th><th>Summary</th><th>Status</th><th>Priority</th><th>Assignee</th><th>Comments</th><th>Updated</th></tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </section>
      </div>
      <aside class="tickets-side">
        <section class="panel" id="ticket-filter-summary"></section>
        <section class="panel">
          <div class="panel-header"><h3>Status mix</h3><span>{len(tickets)} visible</span></div>
          <div class="stat-list">
            {"".join(f'<div class="stat-row"><span>{esc(key.replace("_", " "))}</span><strong>{value}</strong></div>' for key, value in status_counts.items())}
          </div>
        </section>
      </aside>
    </section>
    """
    return render_layout(
        title="Travel Editor Tickets",
        body=body,
        page_id="tickets",
        current_user=current_user,
        payload={"filters": filters, "statusCounts": status_counts},
    )
