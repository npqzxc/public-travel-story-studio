import { titleize } from "../utils/format.js";

export function renderFilterSummary(payload) {
  const filters = payload.filters || {};
  const activeFilters = Object.entries(filters)
    .map(([key, value]) => `<div class="stat-row"><span>${titleize(key)}</span><strong>${value}</strong></div>`)
    .join("");

  const statusCounts = Object.entries(payload.meta?.status_counts || {})
    .map(([key, value]) => `<div class="stat-row"><span>${titleize(key)}</span><strong>${value}</strong></div>`)
    .join("");

  return `
    <div class="panel-header">
      <h3>Active filters</h3>
      <span>${payload.meta?.count || 0} results</span>
    </div>
    <div class="stat-list">
      ${activeFilters || '<p class="filter-note">No filters applied. The queue is showing all tickets.</p>'}
    </div>
    <div class="panel-header">
      <h3>Visible mix</h3>
      <span>Filtered</span>
    </div>
    <div class="stat-list">${statusCounts}</div>
  `;
}
