export function renderTicketPreview(formState) {
  const title = formState.title || "Draft ticket title";
  const description =
    formState.description ||
    "As you fill out the form, this preview helps the writer see whether the task has enough context.";
  const priority = formState.priority || "medium";
  const dueDate = formState.due_date || "No due date selected";

  return `
    <div class="panel-header">
      <h3>Live preview</h3>
      <span>${priority}</span>
    </div>
    <article class="preview-card">
      <h4>${title}</h4>
      <p>${description}</p>
      <div class="stat-list">
        <div class="stat-row"><span>Priority</span><strong>${priority}</strong></div>
        <div class="stat-row"><span>Due</span><strong>${dueDate}</strong></div>
      </div>
    </article>
  `;
}
