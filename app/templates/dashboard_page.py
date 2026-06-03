from __future__ import annotations

from .components import esc
from .layout import render_layout


def render_dashboard_page(summary: dict, current_user: dict) -> str:
    metric_cards = f"""
      <section class="metric-grid">
        <article class="metric-card"><span>Total tickets</span><strong>{summary["ticket_total"]}</strong></article>
        <article class="metric-card"><span>In progress</span><strong>{summary["status_counts"].get("in_progress", 0)}</strong></article>
        <article class="metric-card"><span>Blocked</span><strong>{summary["status_counts"].get("blocked", 0)}</strong></article>
        <article class="metric-card"><span>Urgent</span><strong>{summary["priority_counts"].get("urgent", 0)}</strong></article>
      </section>
    """
    project_cards = "".join(
        f"""
        <article class="project-card">
          <div class="project-header">
            <span>{esc(project["code"])}</span>
            <strong>{esc(project["name"])}</strong>
          </div>
          <p>{esc(project["summary"])}</p>
          <div class="project-footer">
            <span>{project["ticket_count"]} active items</span>
            <span>{esc(project["status"])}</span>
          </div>
        </article>
        """
        for project in summary["project_cards"]
    )
    activity_rows = "".join(
        f"""
        <tr>
          <td>{esc(item["created_at"])}</td>
          <td>{esc(item["project_code"])}-{item["ticket_id"]}</td>
          <td>{esc(item["actor_name"])}</td>
          <td>{esc(item["details"])}</td>
        </tr>
        """
        for item in summary["recent_activity"]
    )
    body = f"""
    <header class="page-header">
      <div>
        <p class="eyebrow">Workspace summary</p>
        <h2>Dashboard</h2>
        <p>Current workload across operations, support and yukilytics teams.</p>
      </div>
    </header>
    {metric_cards}
    <section class="dashboard-layout">
      <div class="dashboard-primary">
        <section class="card-grid">{project_cards}</section>
        <section class="panel">
          <div class="panel-header">
            <h3>Recent activity</h3>
            <a href="/tickets">Open full queue</a>
          </div>
          <table>
            <thead>
              <tr><th>When</th><th>Ticket</th><th>Actor</th><th>Update</th></tr>
            </thead>
            <tbody>{activity_rows}</tbody>
          </table>
        </section>
      </div>
      <aside class="dashboard-secondary">
        <section class="panel" id="dashboard-spotlights"></section>
        <section class="panel" id="dashboard-activity-feed"></section>
      </aside>
    </section>
    """
    return render_layout(
        title="Travel Editor Dashboard",
        body=body,
        page_id="dashboard",
        current_user=current_user,
        payload={"summary": summary},
    )
