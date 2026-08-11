import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Target, RefreshCw, Globe, Server, Wifi, Database } from 'lucide-react'
import { listScans, getScan } from '../utils/api'
import Topbar from '../components/Topbar'

function assetIcon(type) {
  const m = { domain: Globe, subdomain: Globe, ip: Server, port: Wifi, service: Database }
  const I = m[type] || Target
  return <I size={13} />
}

export default function Assets() {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState('all')
  const [filterRisk, setFilterRisk] = useState('all')

  useEffect(() => {
    async function load() {
      try {
        const scans = await listScans()
        const completed = scans.filter(s => s.status === 'completed')
        const all = []
        for (const s of completed.slice(0, 10)) {
          const detail = await getScan(s.id)
          detail.assets?.forEach(a => all.push({ ...a, scan_target: s.target, scan_id: s.id }))
        }
        setAssets(all)
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  const types = ['all', ...new Set(assets.map(a => a.asset_type))]
  const filtered = assets.filter(a =>
    (filterType === 'all' || a.asset_type === filterType) &&
    (filterRisk === 'all' || a.risk_level === filterRisk)
  )

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Assets" subtitle={`${assets.length} total assets discovered`} />
      <div className="p-6 space-y-5 animate-fade-in">
        <div className="flex gap-3 flex-wrap">
          <div className="flex gap-1">
            {types.slice(0, 6).map(t => (
              <button key={t} onClick={() => setFilterType(t)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all
                  ${filterType === t
                    ? 'bg-sentinel-accent/20 text-sentinel-accent border border-sentinel-accent/40'
                    : 'bg-sentinel-card text-sentinel-muted border border-sentinel-border hover:border-sentinel-accent/20'}`}>
                {t.toUpperCase()}
              </button>
            ))}
          </div>
          <div className="flex gap-1">
            {['all', 'critical', 'high', 'medium', 'low'].map(r => (
              <button key={r} onClick={() => setFilterRisk(r)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all
                  ${filterRisk === r
                    ? 'bg-sentinel-accent/20 text-sentinel-accent border border-sentinel-accent/40'
                    : 'bg-sentinel-card text-sentinel-muted border border-sentinel-border hover:border-sentinel-accent/20'}`}>
                {r === 'all' ? 'All Risk' : r.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          {loading
            ? <div className="flex items-center justify-center py-16 gap-3 text-sentinel-muted">
                <RefreshCw size={16} className="animate-spin" />
                <span className="font-mono text-sm">Loading assets…</span>
              </div>
            : filtered.length === 0
              ? <div className="text-center py-16 text-sentinel-muted">No assets match your filters.</div>
              : <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-sentinel-border">
                        {['Type', 'Value', 'IP', 'Port/Service', 'Risk', 'Scan'].map(h => (
                          <th key={h} className="text-left text-sentinel-muted font-medium uppercase tracking-wider pb-3 pr-4">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-sentinel-border/40">
                      {filtered.map(a => (
                        <tr key={a.id} className="hover:bg-white/[0.02]">
                          <td className="py-2.5 pr-4">
                            <span className="flex items-center gap-1.5 text-sentinel-muted">
                              {assetIcon(a.asset_type)}
                              <span className="capitalize">{a.asset_type}</span>
                            </span>
                          </td>
                          <td className="py-2.5 pr-4 font-mono text-sentinel-accent max-w-[200px] truncate">{a.value}</td>
                          <td className="py-2.5 pr-4 font-mono text-sentinel-text">{a.ip_address || '—'}</td>
                          <td className="py-2.5 pr-4 font-mono text-sentinel-text">{a.port ? `${a.port}/${a.service || '?'}` : '—'}</td>
                          <td className="py-2.5 pr-4">
                            <span className={`badge-${a.risk_level}`}>{a.risk_level?.toUpperCase()}</span>
                          </td>
                          <td className="py-2.5">
                            <Link to={`/scans/${a.scan_id}`} className="text-sentinel-accent hover:underline font-mono">
                              {a.scan_target}
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
          }
        </div>
      </div>
    </div>
  )
}
