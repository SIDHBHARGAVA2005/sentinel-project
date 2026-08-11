export const severityColor = (sev) => ({
  critical: '#ff3b5c',
  high:     '#ff8c00',
  medium:   '#ffd700',
  low:      '#00ff88',
}[sev] || '#4a5a7a')

export const severityBadgeClass = (sev) => ({
  critical: 'badge-critical',
  high:     'badge-high',
  medium:   'badge-medium',
  low:      'badge-low',
}[sev] || 'badge-info')

export const riskLabel = (score) => {
  if (score >= 80) return { label: 'CRITICAL', color: '#ff3b5c' }
  if (score >= 60) return { label: 'HIGH',     color: '#ff8c00' }
  if (score >= 40) return { label: 'MEDIUM',   color: '#ffd700' }
  return                   { label: 'LOW',      color: '#00ff88' }
}

export const statusColor = (status) => ({
  completed: '#00ff88',
  running:   '#00d4ff',
  pending:   '#ffd700',
  failed:    '#ff3b5c',
}[status] || '#4a5a7a')

export const fmtDate = (iso) => {
  if (!iso) return '—'
  // SQLite and FastAPI may send UTC times without the 'Z' timezone indicator.
  // We append it to force JS to parse it as UTC, which then accurately converts to local time.
  const utcIso = iso.endsWith('Z') ? iso : `${iso}Z`
  return new Date(utcIso).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}
