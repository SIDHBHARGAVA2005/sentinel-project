const SEV = [
  { key: 'critical', label: 'Critical', color: '#ff3b5c' },
  { key: 'high',     label: 'High',     color: '#ff8c00' },
  { key: 'medium',   label: 'Medium',   color: '#ffd700' },
  { key: 'low',      label: 'Low',      color: '#00ff88' },
]

export default function SeverityBar({ counts = {} }) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1
  return (
    <div className="space-y-2">
      {SEV.map(({ key, label, color }) => {
        const n = counts[key] || 0
        const pct = Math.round((n / total) * 100)
        return (
          <div key={key} className="flex items-center gap-3 text-xs">
            <span className="w-14 text-sentinel-muted font-mono">{label}</span>
            <div className="flex-1 h-1.5 bg-sentinel-border rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${pct}%`, background: color, boxShadow: `0 0 6px ${color}` }}
              />
            </div>
            <span className="w-6 text-right font-mono" style={{ color }}>{n}</span>
          </div>
        )
      })}
    </div>
  )
}
