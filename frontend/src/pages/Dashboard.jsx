import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Shield, Radar, Target, Globe, TrendingUp, Clock } from 'lucide-react'
import { getStats } from '../utils/api'
import { statusColor, riskLabel, fmtDate } from '../utils/helpers'
import StatCard from '../components/ui/StatCard'
import Topbar from '../components/Topbar'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getStats().then(setStats).catch(console.error).finally(() => setLoading(false))
    const t = setInterval(() => getStats().then(setStats).catch(() => {}), 8000)
    return () => clearInterval(t)
  }, [])

  if (loading) return (
    <div className="flex-1 flex items-center justify-center min-h-screen">
      <div className="text-center space-y-3">
        <div className="w-12 h-12 border-2 border-sentinel-accent border-t-transparent
                        rounded-full animate-spin mx-auto" />
        <p className="text-sentinel-muted font-mono text-sm">Initializing Sentinel…</p>
      </div>
    </div>
  )

  const recent = stats?.recent_scans || []

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Dashboard" subtitle="Attack Surface Overview" />

      <div className="p-6 space-y-6 animate-fade-in">
        {/* Hero banner */}
        <div className="card relative overflow-hidden border-sentinel-accent/20">
          <div className="absolute inset-0 bg-gradient-to-r from-sentinel-accent/5 to-transparent pointer-events-none" />
          <div className="relative flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 rounded-full bg-sentinel-green animate-pulse-slow" />
                <span className="text-sentinel-green text-xs font-mono tracking-widest">SYSTEM OPERATIONAL</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-1">Project Sentinel</h2>
              <p className="text-sentinel-muted text-sm max-w-lg">
                Agentic AI framework for proactive threat intelligence and external attack surface management.
                Three agents — Scout, Analyst, Oracle — working in concert.
              </p>
            </div>
            <div className="hidden md:flex items-center gap-3">
              {['Scout', 'Analyst', 'Oracle'].map((agent, i) => (
                <div key={agent} className="text-center">
                  <div className="w-12 h-12 rounded-full bg-sentinel-accent/10 border border-sentinel-accent/30
                                  flex items-center justify-center mb-1 relative"
                       style={{ animationDelay: `${i * 0.3}s` }}>
                    <span className="text-sentinel-accent text-xs font-bold">{agent[0]}</span>
                    <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full
                                     bg-sentinel-green border-2 border-sentinel-bg" />
                  </div>
                  <span className="text-sentinel-muted text-xs font-mono">{agent}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <StatCard icon={Radar}        label="Total Scans"       value={stats?.total_scans ?? 0}           color="#00d4ff" />
          <StatCard icon={Target}       label="Assets Found"      value={stats?.total_assets ?? 0}          color="#00ff88" />
          <StatCard icon={TrendingUp}   label="Avg Risk Score"    value={`${stats?.average_risk_score ?? 0}/100`} color="#ffd700" />
        </div>

        {/* Recent scans table */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Clock size={16} className="text-sentinel-accent" />
              Recent Scans
            </h3>
            <Link to="/scans" className="text-sentinel-accent text-xs hover:underline font-mono">
              View all →
            </Link>
          </div>

          {recent.length === 0 ? (
            <div className="text-center py-12 space-y-3">
              <Shield size={40} className="text-sentinel-muted mx-auto" />
              <p className="text-sentinel-muted">No scans yet. Start your first scan above.</p>
              <Link to="/scans" className="btn-primary inline-flex items-center gap-2 text-sm">
                <Radar size={14} /> New Scan
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-sentinel-border">
                    {['Target', 'Status', 'Assets', 'Risk', 'Started'].map(h => (
                      <th key={h} className="text-left text-xs text-sentinel-muted font-medium
                                             uppercase tracking-wider pb-3 pr-4">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-sentinel-border/50">
                  {recent.map(s => {
                    const { label, color } = riskLabel(s.risk_score)
                    return (
                      <tr key={s.id} className="hover:bg-sentinel-surface/50 transition-colors">
                        <td className="py-3 pr-4">
                          <Link to={`/scans/${s.id}`}
                            className="text-sentinel-accent hover:underline font-mono text-xs">
                            {s.target}
                          </Link>
                        </td>
                        <td className="py-3 pr-4">
                          <span className="flex items-center gap-1.5 text-xs font-mono"
                                style={{ color: statusColor(s.status) }}>
                            <span className="w-1.5 h-1.5 rounded-full animate-pulse-slow"
                                  style={{ background: statusColor(s.status) }} />
                            {s.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-sentinel-text font-mono text-xs">{s.total_assets}</td>
                        <td className="py-3 pr-4">
                          <span className="font-mono text-xs font-bold" style={{ color }}>{label}</span>
                        </td>
                        <td className="py-3 text-sentinel-muted font-mono text-xs">{fmtDate(s.created_at)}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Agent pipeline diagram */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Shield size={16} className="text-sentinel-accent" />
            Agent Pipeline Architecture
          </h3>
          <div className="flex items-center justify-center gap-2 flex-wrap py-4">
            {[
              { name: 'Scout Agent', desc: 'DNS · Ports · CT Logs · Shodan', color: '#00d4ff' },
              { name: 'Analyst Agent', desc: 'CVE Correlation · Risk Scoring', color: '#00ff88' },
              { name: 'Oracle Agent', desc: 'AI Report Generation', color: '#a78bfa' },
            ].map((agent, i) => (
              <div key={agent.name} className="flex items-center gap-2">
                <div className="text-center px-5 py-4 rounded-xl"
                     style={{ background: agent.color + '0f', border: `1px solid ${agent.color}30` }}>
                  <div className="font-bold text-sm mb-1" style={{ color: agent.color }}>{agent.name}</div>
                  <div className="text-sentinel-muted text-xs font-mono">{agent.desc}</div>
                </div>
                {i < 2 && (
                  <div className="text-sentinel-muted font-mono text-lg">→</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
