from __future__ import annotations

from .components import esc, priority_badge, status_badge
from .layout import render_layout


def render_ticket_detail_page(
    ticket: dict,
    members: list[dict],
    current_user: dict,
    error: str | None = None,
    status_options: tuple[str, ...] = ("todo", "in_progress", "blocked", "review", "done"),
) -> str:
    comments_html = "".join(
        f"""
        <article class="comment-card">
          <div class="comment-meta">
            <strong>{esc(comment["author_name"])}</strong>
            <span>{esc(comment["created_at"])}</span>
          </div>
          <p>{esc(comment["body"])}</p>
        </article>
        """
        for comment in ticket["comments"]
    )
    events_html = "".join(
        f"""
        <li>
          <strong>{esc(event["actor_name"])}</strong>
          <span>{esc(event["details"])}</span>
          <em>{esc(event["created_at"])}</em>
        </li>
        """
        for event in ticket["events"]
    )
    status_markup = "".join(
        f'<option value="{value}" {"selected" if ticket["status"] == value else ""}>{esc(value.replace("_", " "))}</option>'
        for value in status_options
    )
    error_html = f'<p class="form-error">{esc(error)}</p>' if error else ""
    body = f"""
    <header class="page-header">
      <div>
        <p class="eyebrow">{esc(ticket["project_code"])}-{ticket["id"]}</p>
        <h2>{esc(ticket["title"])}</h2>
        <p>{esc(ticket["project_name"])} · reported by {esc(ticket["reporter_name"])}</p>
      </div>
      <a class="ghost-link" href="/tickets">Back to queue</a>
    </header>
    <section class="detail-grid">
      <article class="panel">
        <div class="ticket-meta">
          {status_badge(ticket["status"])}
          {priority_badge(ticket["priority"])}
          <span>Assignee: {esc(ticket["assignee_name"])}</span>
          <span>Due: {esc(ticket["due_date"])}</span>
        </div>
        <p class="ticket-body">{esc(ticket["description"])}</p>
      </article>
      <aside class="panel">
        <h3>Workflow</h3>
        <form class="stack-form compact-form" method="post" action="/tickets/{ticket["id"]}/status">
          <label>Status<select name="status">{status_markup}</select></label>
          <button type="submit">Update status</button>
        </form>
        <section id="timeline-panel" class="timeline-shell"></section>
      </aside>
    </section>
    <section class="detail-grid">
      <article class="panel">
        <div class="panel-header">
          <h3>Discussion</h3>
          <span>{len(ticket["comments"])} comments</span>
        </div>
        {comments_html}
      </article>
      <aside class="panel">
        <h3>Add comment</h3>
        <form class="stack-form compact-form" method="post" action="/tickets/{ticket["id"]}/comments">
          <label>Update<textarea name="body" rows="6" required></textarea></label>
          {error_html}
          <button type="submit">Post comment</button>
        </form>
        <ul class="timeline timeline-fallback">{events_html}</ul>
      </aside>
    </section>
    """
    return render_layout(
        title=f"Ticket {ticket['id']}",
        body=body,
        page_id="ticket-detail",
        current_user=current_user,
        payload={"ticketId": ticket["id"], "memberCount": len(members)},
    )
