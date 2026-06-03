import { renderActivityFeed } from "../components/activity-feed.js";
import { renderDashboardSpotlights } from "../components/dashboard-panels.js";
import { qs, setHtml } from "../utils/dom.js";

export async function mountDashboardPage({ api, bootstrap }) {
  const summary = await api.getDashboard().catch(() => bootstrap.summary || {});
  setHtml(qs("#dashboard-spotlights"), renderDashboardSpotlights(summary));
  setHtml(qs("#dashboard-activity-feed"), renderActivityFeed(summary));
}
