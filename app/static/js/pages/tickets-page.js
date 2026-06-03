import { renderFilterSummary } from "../components/filter-summary.js";
import { qs, setHtml } from "../utils/dom.js";

export async function mountTicketsPage({ api }) {
  const payload = await api.getTickets(window.location.search);
  setHtml(qs("#ticket-filter-summary"), renderFilterSummary(payload));
}
