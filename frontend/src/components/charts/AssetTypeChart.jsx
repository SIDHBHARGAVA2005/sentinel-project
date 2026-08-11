import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const COLORS = ['#00d4ff', '#00ff88', '#ffd700', '#ff8c00', '#ff3b5c', '#a78bfa']

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div className="bg-sentinel-card border border-sentinel-border rounded-lg px-3 py-2 text-xs font-mono">
        <div className="text-sentinel-accent">{label}</div>
        <div className="text-white">{payload[0].value} assets</div>
      </div>
    )
  }
  return null
}

export default function AssetTypeChart({ assets = [] }) {
  const counts = assets.reduce((acc, a) => {
    const t = a.asset_type || 'unknown'
    acc[t] = (acc[t] || 0) + 1
    return acc
  }, {})

  const data = Object.entries(counts).map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)

  if (!data.length) return (
    <div className="h-48 flex items-center justify-center text-sentinel-muted text-sm">
      No asset data
    </div>
  )

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
        <XAxis dataKey="name" tick={{ fill: '#4a5a7a', fontSize: 11, fontFamily: 'monospace' }}
          axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#4a5a7a', fontSize: 10 }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: '#ffffff08' }} />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]}
              style={{ filter: `drop-shadow(0 0 4px ${COLORS[i % COLORS.length]})` }} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
