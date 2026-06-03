import { renderTicketPreview } from "../components/ticket-preview.js";
import { qs, setHtml } from "../utils/dom.js";

function formStateFrom(form) {
  return Object.fromEntries(new FormData(form).entries());
}

export async function mountNewTicketPage({ api, bootstrap }) {
  const form = qs("#ticket-create-form");
  const preview = qs("#ticket-preview-panel");
  if (!form || !preview) {
    return;
  }

  const hydrated = await api.getProjects().catch(() => bootstrap.projects || []);
  if (hydrated.items && !bootstrap.projects) {
    bootstrap.projects = hydrated.items;
  }

  const update = () => {
    setHtml(preview, renderTicketPreview(formStateFrom(form)));
  };

  form.addEventListener("input", update);
  form.addEventListener("change", update);
  update();
}
