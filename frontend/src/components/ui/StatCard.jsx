export default function StatCard({ icon: Icon, label, value, color = '#00d4ff', sub }) {
  return (
    <div className="card flex items-start gap-4 hover:border-sentinel-accent/20 transition-colors">
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
        style={{ background: color + '18', border: `1px solid ${color}30` }}
      >
        <Icon size={18} style={{ color }} />
      </div>
      <div>
        <div className="text-sentinel-muted text-xs font-medium uppercase tracking-wider mb-1">
          {label}
        </div>
        <div className="text-2xl font-bold text-white font-mono">{value ?? '—'}</div>
        {sub && <div className="text-sentinel-muted text-xs mt-0.5">{sub}</div>}
      </div>
    </div>
  )
}
