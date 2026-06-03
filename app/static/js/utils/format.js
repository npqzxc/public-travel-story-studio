export function titleize(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}
