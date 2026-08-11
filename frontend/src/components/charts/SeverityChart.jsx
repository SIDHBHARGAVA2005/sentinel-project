import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS = {
  critical: '#ff3b5c',
  high:     '#ff8c00',
  medium:   '#ffd700',
  low:      '#00ff88',
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload?.length) {
    const { name, value } = payload[0]
    return (
      <div className="bg-sentinel-card border border-sentinel-border rounded-lg px-3 py-2 text-xs font-mono">
        <span style={{ color: COLORS[name] }}>{name.toUpperCase()}</span>
        <span className="text-white ml-2">{value}</span>
      </div>
    )
  }
  return null
}

export default function SeverityChart({ counts = {} }) {
  const data = Object.entries(counts)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }))

  if (!data.length) return (
    <div className="h-48 flex items-center justify-center text-sentinel-muted text-sm">
      No vulnerability data
    </div>
  )

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
          paddingAngle={3} dataKey="value">
          {data.map(({ name }) => (
            <Cell key={name} fill={COLORS[name]} stroke="transparent"
              style={{ filter: `drop-shadow(0 0 6px ${COLORS[name]})` }} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend formatter={(v) => (
          <span style={{ color: COLORS[v], fontSize: 11, fontFamily: 'monospace' }}>
            {v.toUpperCase()}
          </span>
        )} />
      </PieChart>
    </ResponsiveContainer>
  )
}
