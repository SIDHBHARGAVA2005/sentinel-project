import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity, RefreshCw, CheckCircle, XCircle, Clock, Radar } from 'lucide-react'
import { listScans } from '../utils/api'
import { statusColor, riskLabel, fmtDate } from '../utils/helpers'
import Topbar from '../components/Topbar'

function TimelineItem({ scan, isLast }) {
  const { label, color } = riskLabel(scan.risk_score)
  const isRunning = scan.status === 'running' || scan.status === 'pending'
  const icon = scan.status === 'completed'
    ? <CheckCircle size={16} className="text-sentinel-green" />
    : scan.status === 'failed'
      ? <XCircle size={16} className="text-red-400" />
      : <RefreshCw size={16} className="text-sentinel-accent animate-spin" />

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className="w-8 h-8 rounded-full bg-sentinel-card border border-sentinel-border
                        flex items-center justify-center shrink-0">
          {icon}
        </div>
        {!isLast && <div className="w-px flex-1 bg-sentinel-border mt-1" />}
      </div>
      <div className={`pb-6 flex-1 ${isLast ? '' : ''}`}>
        <div className="card hover:border-sentinel-border/80 transition-colors">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs font-medium"
                      style={{ color: statusColor(scan.status) }}>
                  {scan.status.toUpperCase()}
                </span>
                {scan.status === 'completed' && (
                  <span className="font-mono text-xs font-bold" style={{ color }}>
                    {scan.risk_score}/100 — {label}
                  </span>
                )}
              </div>
              <Link to={`/scans/${scan.id}`}
                className="text-sentinel-accent hover:underline font-mono text-sm font-medium">
                {scan.target}
              </Link>
              <div className="flex items-center gap-4 mt-1.5 text-xs text-sentinel-muted font-mono">
                <span className="flex items-center gap-1">
                  <Clock size={10} /> {fmtDate(scan.created_at)}
                </span>
                {scan.status === 'completed' && (
                  <>
                    <span>{scan.total_assets} assets</span>
                    <span>{scan.total_vulns} vulns</span>
                  </>
                )}
              </div>
            </div>
            {isRunning && (
              <div className="flex items-center gap-2 text-xs text-sentinel-accent font-mono
                              bg-sentinel-accent/5 border border-sentinel-accent/20 rounded-lg px-3 py-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-sentinel-accent animate-ping" />
                Scanning…
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ActivityPage() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () =>
    listScans().then(setScans).catch(console.error).finally(() => setLoading(false))

  useEffect(() => {
    load()
    const t = setInterval(load, 6000)
    return () => clearInterval(t)
  }, [])

  const running = scans.filter(s => s.status === 'running' || s.status === 'pending')
  const done    = scans.filter(s => s.status === 'completed')
  const failed  = scans.filter(s => s.status === 'failed')

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Activity" subtitle="Live scan feed" />
      <div className="p-6 space-y-5 animate-fade-in">

        {/* Live stats strip */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Active Scans',    value: running.length, color: '#00d4ff', pulse: running.length > 0 },
            { label: 'Completed Today', value: done.length,    color: '#00ff88' },
            { label: 'Failed',          value: failed.length,  color: '#ff3b5c' },
          ].map(({ label, value, color, pulse }) => (
            <div key={label} className="card flex items-center gap-3"
                 style={{ borderColor: value > 0 ? color + '30' : undefined }}>
              <div className="w-2 h-2 rounded-full shrink-0"
                   style={{ background: color, boxShadow: `0 0 8px ${color}`,
                            animation: pulse ? 'ping 1s cubic-bezier(0,0,0.2,1) infinite' : undefined }} />
              <div>
                <div className="text-xl font-bold font-mono" style={{ color }}>{value}</div>
                <div className="text-sentinel-muted text-xs">{label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Timeline */}
        <div className="card">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Activity size={16} className="text-sentinel-accent" />
              Scan Timeline
            </h3>
            <button onClick={load} className="text-sentinel-muted hover:text-sentinel-accent transition-colors">
              <RefreshCw size={14} />
            </button>
          </div>

          {loading
            ? <div className="flex items-center justify-center py-16 gap-3 text-sentinel-muted">
                <RefreshCw size={16} className="animate-spin" />
                <span className="font-mono text-sm">Loading activity…</span>
              </div>
            : scans.length === 0
              ? <div className="text-center py-16">
                  <Radar size={40} className="text-sentinel-muted mx-auto mb-3 opacity-40" />
                  <p className="text-sentinel-muted text-sm">No activity yet.</p>
                  <Link to="/scans" className="btn-primary inline-flex mt-4 text-sm gap-2">
                    <Radar size={13} /> Start a Scan
                  </Link>
                </div>
              : <div>
                  {scans.map((s, i) => (
                    <TimelineItem key={s.id} scan={s} isLast={i === scans.length - 1} />
                  ))}
                </div>
          }
        </div>
      </div>
    </div>
  )
}
