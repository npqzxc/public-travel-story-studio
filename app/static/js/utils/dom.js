export function qs(selector, root = document) {
  return root.querySelector(selector);
}

export function setHtml(target, html) {
  if (target) {
    target.innerHTML = html;
  }
}
