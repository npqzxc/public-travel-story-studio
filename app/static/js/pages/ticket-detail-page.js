import { renderTimelinePanel } from "../components/timeline-panel.js";
import { qs, setHtml } from "../utils/dom.js";

export async function mountTicketDetailPage({ api, bootstrap }) {
  if (!bootstrap.ticketId) {
    return;
  }
  const ticket = await api.getTicket(bootstrap.ticketId);
  setHtml(qs("#timeline-panel"), renderTimelinePanel(ticket));
}
