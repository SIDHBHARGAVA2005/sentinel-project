import { riskLabel } from '../../utils/helpers'

export default function RiskGauge({ score = 0, size = 120 }) {
  const { label, color } = riskLabel(score)
  const r = 45
  const circ = 2 * Math.PI * r
  const progress = (score / 100) * circ
  const cx = size / 2
  const cy = size / 2

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="risk-ring" style={{ color }}>
        {/* Background circle */}
        <circle cx={cx} cy={cy} r={r}
          fill="none" stroke="#1e2d4a" strokeWidth="8" />
        {/* Progress arc */}
        <circle cx={cx} cy={cy} r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${progress} ${circ}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${cx} ${cy})`}
          style={{ filter: `drop-shadow(0 0 6px ${color})` }}
        />
        {/* Score text */}
        <text x={cx} y={cy - 4} textAnchor="middle"
          fill="white" fontSize="20" fontWeight="700" fontFamily="JetBrains Mono">
          {score}
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle"
          fill="#4a5a7a" fontSize="8" fontFamily="Inter">
          / 100
        </text>
      </svg>
      <span className="text-xs font-mono font-bold tracking-widest" style={{ color }}>
        {label}
      </span>
    </div>
  )
}
