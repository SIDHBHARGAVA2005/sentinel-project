import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ShieldAlert, RefreshCw, ExternalLink, CheckCircle } from 'lucide-react'
import { listScans, getScan } from '../utils/api'
import { severityBadgeClass } from '../utils/helpers'
import Topbar from '../components/Topbar'

export default function Vulnerabilities() {
  const [vulns, setVulns] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const scans = await listScans()
        const completed = scans.filter(s => s.status === 'completed')
        const all = []
        for (const s of completed.slice(0, 10)) {
          const detail = await getScan(s.id)
          detail.vulnerabilities?.forEach(v => all.push({ ...v, scan_target: s.target, scan_id: s.id }))
        }
        // Sort by severity
        const order = { critical: 0, high: 1, medium: 2, low: 3 }
        all.sort((a, b) => (order[a.severity] ?? 4) - (order[b.severity] ?? 4))
        setVulns(all)
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  const filtered = vulns.filter(v =>
    (filter === 'all' || v.severity === filter) &&
    (!search || v.title?.toLowerCase().includes(search.toLowerCase()) ||
                v.cve_id?.toLowerCase().includes(search.toLowerCase()))
  )

  const counts = vulns.reduce((a, v) => ({ ...a, [v.severity]: (a[v.severity] || 0) + 1 }), {})

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Vulnerabilities" subtitle={`${vulns.length} total findings`} />
      <div className="p-6 space-y-5 animate-fade-in">

        {/* Summary cards */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { sev: 'critical', color: '#ff3b5c', label: 'Critical' },
            { sev: 'high',     color: '#ff8c00', label: 'High' },
            { sev: 'medium',   color: '#ffd700', label: 'Medium' },
            { sev: 'low',      color: '#00ff88', label: 'Low' },
          ].map(({ sev, color, label }) => (
            <div key={sev}
              onClick={() => setFilter(filter === sev ? 'all' : sev)}
              className="card cursor-pointer hover:scale-[1.02] transition-all"
              style={{ borderColor: filter === sev ? color + '60' : undefined,
                       background: filter === sev ? color + '08' : undefined }}>
              <div className="text-2xl font-bold font-mono" style={{ color }}>
                {counts[sev] || 0}
              </div>
              <div className="text-sentinel-muted text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>

        {/* Search + filter */}
        <div className="flex gap-3 flex-wrap">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by title or CVE ID…"
            className="input-field max-w-sm"
          />
          <div className="flex gap-1">
            {['all', 'critical', 'high', 'medium', 'low'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all
                  ${filter === f
                    ? 'bg-sentinel-accent/20 text-sentinel-accent border border-sentinel-accent/40'
                    : 'bg-sentinel-card text-sentinel-muted border border-sentinel-border'}`}>
                {f.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Vuln list */}
        {loading
          ? <div className="flex items-center justify-center py-16 gap-3 text-sentinel-muted">
              <RefreshCw size={16} className="animate-spin" />
              <span className="font-mono text-sm">Loading vulnerabilities…</span>
            </div>
          : filtered.length === 0
            ? <div className="card text-center py-16 text-sentinel-muted">No vulnerabilities match your filters.</div>
            : <div className="space-y-3">
                {filtered.map(v => (
                  <div key={v.id} className="card hover:border-sentinel-border/80 transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                          <span className={severityBadgeClass(v.severity)}>{v.severity?.toUpperCase()}</span>
                          {v.cve_id && (
                            <a href={`https://nvd.nist.gov/vuln/detail/${v.cve_id}`}
                               target="_blank" rel="noreferrer"
                               className="badge-info flex items-center gap-1 hover:text-blue-300 transition-colors">
                              {v.cve_id} <ExternalLink size={9} />
                            </a>
                          )}
                          {v.cvss_score && (
                            <span className="text-xs font-mono text-sentinel-muted">CVSS {v.cvss_score}</span>
                          )}
                          <Link to={`/scans/${v.scan_id}`}
                            className="text-xs font-mono text-sentinel-muted hover:text-sentinel-accent ml-auto">
                            ↗ {v.scan_target}
                          </Link>
                        </div>
                        <h4 className="text-white font-semibold text-sm mb-1">{v.title}</h4>
                        <p className="text-sentinel-muted text-xs leading-relaxed">{v.description}</p>

                      </div>
                    </div>
                  </div>
                ))}
              </div>
        }
      </div>
    </div>
  )
}
