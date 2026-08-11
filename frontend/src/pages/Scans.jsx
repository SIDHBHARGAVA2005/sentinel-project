import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Radar, Plus, Trash2, RefreshCw, ChevronRight } from 'lucide-react'
import { listScans, createScan, deleteScan } from '../utils/api'
import { statusColor, riskLabel, fmtDate } from '../utils/helpers'
import Topbar from '../components/Topbar'

export default function Scans() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [target, setTarget] = useState('')
  const [creating, setCreating] = useState(false)
  const navigate = useNavigate()

  const load = () => listScans().then(setScans).catch(console.error).finally(() => setLoading(false))

  useEffect(() => {
    load()
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!target.trim()) return
    setCreating(true)
    try {
      const scan = await createScan(target.trim())
      setTarget('')
      navigate(`/scans/${scan.id}`)
    } catch {
      alert('Failed to create scan. Make sure the backend is running.')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id, e) => {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('Delete this scan and all its data?')) return
    await deleteScan(id).catch(console.error)
    setScans(s => s.filter(x => x.id !== id))
  }

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Scans" subtitle="Manage attack surface scans" />

      <div className="p-6 space-y-5 animate-fade-in">
        {/* New scan form */}
        <div className="card border-sentinel-accent/20">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Radar size={16} className="text-sentinel-accent" />
            New Scan
          </h3>
          <form onSubmit={handleCreate} className="flex gap-3">
            <input
              value={target}
              onChange={e => setTarget(e.target.value)}
              placeholder="Enter target domain (e.g. example.com, tesla.com)"
              className="input-field flex-1"
            />
            <button
              type="submit"
              disabled={creating || !target.trim()}
              className="btn-primary flex items-center gap-2 whitespace-nowrap disabled:opacity-40"
            >
              {creating
                ? <><RefreshCw size={14} className="animate-spin" /> Starting…</>
                : <><Plus size={14} /> Launch Scan</>
              }
            </button>
          </form>
          <p className="text-sentinel-muted text-xs mt-2 font-mono">
            ⚡ Scout → Analyst → Oracle pipeline runs automatically in the background.
            Scans typically complete in 30–120 seconds depending on the target.
          </p>
        </div>

        {/* Scans table */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">All Scans ({scans.length})</h3>
            <button onClick={load} className="text-sentinel-muted hover:text-sentinel-accent transition-colors">
              <RefreshCw size={14} />
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16 gap-3 text-sentinel-muted">
              <RefreshCw size={16} className="animate-spin" />
              <span className="font-mono text-sm">Loading scans…</span>
            </div>
          ) : scans.length === 0 ? (
            <div className="text-center py-16">
              <Radar size={48} className="text-sentinel-muted mx-auto mb-3 opacity-40" />
              <p className="text-sentinel-muted">No scans yet. Enter a domain above to get started.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-sentinel-border">
                    {['Target', 'Status', 'Assets', 'Risk Score', 'Started', 'Actions'].map(h => (
                      <th key={h}
                          className="text-left text-xs text-sentinel-muted font-medium uppercase tracking-wider pb-3 pr-4">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-sentinel-border/40">
                  {scans.map(s => {
                    const { label, color } = riskLabel(s.risk_score)
                    const isRunning = s.status === 'running' || s.status === 'pending'
                    return (
                      <tr key={s.id} className="hover:bg-white/[0.02] transition-colors group">
                        <td className="py-3 pr-4">
                          <Link to={`/scans/${s.id}`}
                            className="text-sentinel-accent hover:underline font-mono text-xs flex items-center gap-1">
                            {s.target}
                            <ChevronRight size={10} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                          </Link>
                        </td>
                        <td className="py-3 pr-4">
                          <span className="flex items-center gap-1.5 font-mono text-xs"
                                style={{ color: statusColor(s.status) }}>
                            <span className={`w-1.5 h-1.5 rounded-full ${isRunning ? 'animate-ping' : ''}`}
                                  style={{ background: statusColor(s.status) }} />
                            {s.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-sentinel-text font-mono text-xs">{s.total_assets}</td>
                        <td className="py-3 pr-4">
                          {s.status === 'completed'
                            ? <span className="font-mono text-xs font-bold" style={{ color }}>
                                {s.risk_score}/100 — {label}
                              </span>
                            : <span className="text-sentinel-muted text-xs font-mono">—</span>
                          }
                        </td>
                        <td className="py-3 pr-4 text-sentinel-muted font-mono text-xs">{fmtDate(s.created_at)}</td>
                        <td className="py-3">
                          <button
                            onClick={(e) => handleDelete(s.id, e)}
                            className="text-sentinel-muted hover:text-red-400 transition-colors p-1"
                          >
                            <Trash2 size={13} />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
