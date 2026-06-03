export function renderTimelinePanel(ticket) {
  const events = (ticket.events || [])
    .slice(0, 6)
    .map(
      (event) => `
      <li>
        <strong>${event.actor_name}</strong>
        <span>${event.details}</span>
        <em>${event.created_at}</em>
      </li>
    `,
    )
    .join("");

  return `
    <div class="panel-header">
      <h3>Live timeline</h3>
      <span>${ticket.events?.length || 0} events</span>
    </div>
    <ul class="timeline">${events}</ul>
  `;
}
