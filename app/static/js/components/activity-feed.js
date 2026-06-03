export function renderActivityFeed(summary) {
  const items = (summary.recent_activity || [])
    .slice(0, 5)
    .map(
      (item) => `
      <article>
        <strong>${item.project_code}-${item.ticket_id}</strong>
        <p>${item.details}</p>
        <span class="secondary-note">${item.actor_name} · ${item.created_at}</span>
      </article>
    `,
    )
    .join("");

  return `
    <div class="panel-header">
      <h3>Live activity feed</h3>
      <span>Latest 5 events</span>
    </div>
    <div class="mini-feed">${items}</div>
  `;
}
