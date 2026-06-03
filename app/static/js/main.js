import { createApiClient } from "./api/client.js";
import { mountDashboardPage } from "./pages/dashboard-page.js";
import { mountNewTicketPage } from "./pages/new-ticket-page.js";
import { mountTicketDetailPage } from "./pages/ticket-detail-page.js";
import { mountTicketsPage } from "./pages/tickets-page.js";
import { createStore } from "./utils/state.js";

const page = document.body.dataset.page;
const bootstrapElement = document.getElementById("page-bootstrap");
const bootstrap = bootstrapElement ? JSON.parse(bootstrapElement.textContent || "{}") : {};
const api = createApiClient();
const store = createStore({ page, bootstrap });

const registry = {
  dashboard: mountDashboardPage,
  tickets: mountTicketsPage,
  "ticket-detail": mountTicketDetailPage,
  "new-ticket": mountNewTicketPage,
};

const mount = registry[page];
if (mount) {
  mount({ api, store, bootstrap });
}
