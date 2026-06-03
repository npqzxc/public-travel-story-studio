from __future__ import annotations

from .components import esc
from .layout import render_layout


def render_new_ticket_page(
    projects: list[dict],
    members: list[dict],
    current_user: dict,
    values: dict | None = None,
    error: str | None = None,
    priority_options: tuple[str, ...] = ("low", "medium", "high", "urgent"),
) -> str:
    values = values or {}
    project_options = "".join(
        f'<option value="{project["id"]}" {"selected" if values.get("project_id") == str(project["id"]) else ""}>{esc(project["code"])} · {esc(project["name"])}</option>'
        for project in projects
    )
    member_options = "".join(
        f'<option value="{member["id"]}" {"selected" if values.get("assignee_id") == str(member["id"]) else ""}>{esc(member["display_name"])}</option>'
        for member in members
    )
    priority_markup = "".join(
        f'<option value="{value}" {"selected" if values.get("priority", "medium") == value else ""}>{esc(value)}</option>'
        for value in priority_options
    )
    error_html = f'<p class="form-error">{esc(error)}</p>' if error else ""
    body = f"""
    <header class="page-header">
      <div>
        <p class="eyebrow">New work item</p>
        <h2>Create ticket</h2>
        <p>Capture enough context so another engineer can continue the work without a handoff meeting.</p>
      </div>
    </header>
    <section class="form-layout">
      <section class="panel form-panel">
        <form class="stack-form" method="post" action="/tickets" id="ticket-create-form">
          <label>Project<select name="project_id">{project_options}</select></label>
          <label>Title<input name="title" value="{esc(values.get("title", ""))}" required /></label>
          <label>Description<textarea name="description" rows="7" required>{esc(values.get("description", ""))}</textarea></label>
          <label>Priority<select name="priority">{priority_markup}</select></label>
          <label>Assignee<select name="assignee_id">{member_options}</select></label>
          <label>Due date<input type="date" name="due_date" value="{esc(values.get("due_date", ""))}" required /></label>
          {error_html}
          <button type="submit">Create ticket</button>
        </form>
      </section>
      <aside class="panel" id="ticket-preview-panel"></aside>
    </section>
    """
    return render_layout(
        title="Create Ticket",
        body=body,
        page_id="new-ticket",
        current_user=current_user,
        payload={"projects": projects, "members": members, "draft": values},
    )
