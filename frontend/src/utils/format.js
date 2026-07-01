// Small display helpers shared across pages.

export function formatDuration(seconds) {
  const s = Math.round(seconds || 0);
  const m = Math.floor(s / 60);
  const rem = s % 60;
  if (m === 0) return `${rem}s`;
  return `${m}m ${rem}s`;
}

export function formatMinutes(seconds) {
  return `${((seconds || 0) / 60).toFixed(1)} min`;
}

export function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function formatNumber(n) {
  return Math.round(n || 0).toLocaleString();
}
