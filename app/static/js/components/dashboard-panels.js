import { titleize } from "../utils/format.js";

export function renderDashboardSpotlights(summary) {
  const cards = (summary.spotlights || [])
    .map(
      (item) => `
      <article class="insight-card">
        <span>${item.label}</span>
        <strong>${item.value}</strong>
      </article>
    `,
    )
    .join("");

  const statusRows = Object.entries(summary.status_counts || {})
    .map(
      ([status, count]) => `
      <div class="stat-row">
        <span>${titleize(status)}</span>
        <strong>${count}</strong>
      </div>
    `,
    )
    .join("");

  return `
    <div class="panel-header">
      <h3>Spotlights</h3>
      <span>${summary.ticket_total} tickets</span>
    </div>
    <div class="stat-list">${cards}</div>
    <div class="panel-header"><h3>Current status mix</h3><span>Live API</span></div>
    <div class="stat-list">${statusRows}</div>
  `;
}
