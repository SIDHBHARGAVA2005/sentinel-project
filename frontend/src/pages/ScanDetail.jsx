import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Shield, Target, FileText, RefreshCw,
  ChevronLeft, Globe, Server, Lock, Wifi, Database,
  ExternalLink, CheckCircle, XCircle, Clock, Network
} from 'lucide-react'
import { getScan } from '../utils/api'
import { severityBadgeClass, riskLabel, fmtDate, statusColor } from '../utils/helpers'
import RiskGauge from '../components/ui/RiskGauge'
import SeverityBar from '../components/ui/SeverityBar'
import SeverityChart from '../components/charts/SeverityChart'
import AssetTypeChart from '../components/charts/AssetTypeChart'
import Topbar from '../components/Topbar'

const TAB = { OVERVIEW: 0, ASSETS: 1, IPINFO: 2, REPORT: 3 }

function assetIcon(type) {
  const icons = { domain: Globe, subdomain: Globe, ip: Server, port: Wifi, service: Database }
  const Icon = icons[type] || Target
  return <Icon size={13} />
}

export default function ScanDetail() {
  const { id } = useParams()
  const [scan, setScan] = useState(null)
  const [tab, setTab] = useState(TAB.OVERVIEW)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  const load = () =>
    getScan(id).then(setScan).catch(console.error).finally(() => setLoading(false))

  useEffect(() => {
    load()
    const interval = setInterval(() => {
      if (scan?.status === 'running' || scan?.status === 'pending' || !scan) {
        getScan(id).then(setScan).catch(() => {})
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [id, scan?.status])

  if (loading) return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center space-y-3">
        <div className="w-10 h-10 border-2 border-sentinel-accent border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sentinel-muted font-mono text-sm">Loading scan data…</p>
      </div>
    </div>
  )

  if (!scan) return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <XCircle size={40} className="text-red-400 mx-auto mb-3" />
        <p className="text-sentinel-muted">Scan not found.</p>
        <Link to="/scans" className="btn-primary mt-4 inline-flex">← Back to Scans</Link>
      </div>
    </div>
  )

  const assets = scan.assets || []
  const report = scan.report
  const isRunning = scan.status === 'running' || scan.status === 'pending'

  // Extract unique IPs and open ports from assets
  const ipMap = {}
  assets.forEach(a => {
    if (a.ip_address) {
      if (!ipMap[a.ip_address]) {
        ipMap[a.ip_address] = { ip: a.ip_address, hostnames: new Set(), ports: [] }
      }
      const hostname = a.value?.split(':')[0] || ''
      if (hostname) ipMap[a.ip_address].hostnames.add(hostname)
      if (a.port) {
        ipMap[a.ip_address].ports.push({ port: a.port, service: a.service || 'unknown', protocol: a.protocol || 'TCP' })
      }
    }
  })
  const ipEntries = Object.values(ipMap).map(e => ({ ...e, hostnames: [...e.hostnames] }))

  const tabs = [
    { id: TAB.OVERVIEW, label: 'Overview',       icon: Shield },
    { id: TAB.ASSETS,   label: `Assets (${assets.length})`, icon: Target },
    { id: TAB.IPINFO,   label: `IP Lookup (${ipEntries.length})`, icon: Network },
    { id: TAB.REPORT,   label: 'AI Report',      icon: FileText },
  ]

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title={scan.target} subtitle={`Scan ID: ${scan.id.slice(0, 8)}…`} />

      <div className="p-6 space-y-5 animate-fade-in">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link to="/scans" className="text-sentinel-muted hover:text-sentinel-accent transition-colors">
              <ChevronLeft size={20} />
            </Link>
            <div>
              <h2 className="text-white font-bold text-xl font-mono">{scan.target}</h2>
              <div className="flex items-center gap-3 mt-1">
                <span className="flex items-center gap-1.5 text-xs font-mono"
                      style={{ color: statusColor(scan.status) }}>
                  <span className={`w-2 h-2 rounded-full ${isRunning ? 'animate-ping' : ''}`}
                        style={{ background: statusColor(scan.status) }} />
                  {scan.status.toUpperCase()}
                </span>
                <span className="text-sentinel-muted text-xs font-mono">{fmtDate(scan.created_at)}</span>
              </div>
            </div>
          </div>
          <button onClick={load} className="text-sentinel-muted hover:text-sentinel-accent transition-colors p-2">
            <RefreshCw size={15} className={isRunning ? 'animate-spin' : ''} />
          </button>
        </div>

        {/* Running indicator */}
        {isRunning && (
          <div className="card border-sentinel-accent/30 bg-sentinel-accent/5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-sentinel-accent border-t-transparent animate-spin" />
              <div>
                <div className="text-sentinel-accent font-medium text-sm">Scan in progress…</div>
                <div className="text-sentinel-muted text-xs font-mono">
                  Scout → Analyst → Oracle pipeline running. Results will appear automatically.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-sentinel-border gap-1">
          {tabs.map(({ id: tid, label, icon: Icon }) => (
            <button
              key={tid}
              onClick={() => setTab(tid)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-all
                ${tab === tid
                  ? 'text-sentinel-accent border-b-2 border-sentinel-accent -mb-px'
                  : 'text-sentinel-muted hover:text-sentinel-text'}`}
            >
              <Icon size={13} />
              {label}
            </button>
          ))}
        </div>

        {/* OVERVIEW TAB */}
        {tab === TAB.OVERVIEW && (
          <div className="space-y-5 animate-slide-up">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Risk gauge */}
              <div className="card flex flex-col items-center justify-center gap-3">
                <div className="text-sentinel-muted text-xs uppercase tracking-wider font-medium">Overall Risk</div>
                <RiskGauge score={scan.risk_score} size={140} />
                <div className="mt-2 pt-3 border-t border-sentinel-border grid grid-cols-2 gap-2 text-xs font-mono w-full">
                  <div className="text-sentinel-muted">Assets found</div>
                  <div className="text-white text-right">{assets.length}</div>
                  <div className="text-sentinel-muted">Unique IPs</div>
                  <div className="text-white text-right">{ipEntries.length}</div>
                  <div className="text-sentinel-muted">Open ports</div>
                  <div className="text-white text-right">{ipEntries.reduce((sum, e) => sum + e.ports.length, 0)}</div>
                  <div className="text-sentinel-muted">Scan duration</div>
                  <div className="text-white text-right">
                    {scan.completed_at
                      ? `${Math.round((new Date(scan.completed_at) - new Date(scan.created_at)) / 1000)}s`
                      : isRunning ? 'running…' : '—'}
                  </div>
                </div>
              </div>

              {/* IP Address Summary */}
              <div className="card">
                <div className="text-sentinel-muted text-xs uppercase tracking-wider font-medium mb-4">
                  Resolved IP Addresses
                </div>
                {ipEntries.length === 0 ? (
                  <div className="text-center py-8 text-sentinel-muted text-sm">No IPs resolved yet.</div>
                ) : (
                  <div className="space-y-2 max-h-[280px] overflow-y-auto pr-2">
                    {ipEntries.map(entry => (
                      <div key={entry.ip} className="bg-sentinel-surface rounded-lg p-3 border border-sentinel-border">
                        <div className="flex items-center gap-2 mb-1">
                          <Server size={13} className="text-sentinel-accent" />
                          <span className="font-mono text-sm text-sentinel-accent font-bold">{entry.ip}</span>
                        </div>
                        <div className="text-xs text-sentinel-muted font-mono truncate">
                          {entry.hostnames.join(', ')}
                        </div>
                        {entry.ports.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {entry.ports.map(p => (
                              <span key={p.port} className="bg-sentinel-accent/10 text-sentinel-accent text-xs font-mono px-2 py-0.5 rounded border border-sentinel-accent/20">
                                {p.port}/{p.service}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Asset type chart */}
            <div className="card">
              <div className="text-sentinel-muted text-xs uppercase tracking-wider font-medium mb-3">
                Asset Types Discovered
              </div>
              <AssetTypeChart assets={assets} />
            </div>


          </div>
        )}

        {/* ASSETS TAB */}
        {tab === TAB.ASSETS && (
          <div className="animate-slide-up">
            <div className="card">
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-sentinel-border">
                      {['Type', 'Value', 'IP Address', 'Port/Service', 'Country', 'Risk'].map(h => (
                        <th key={h} className="text-left text-sentinel-muted font-medium uppercase tracking-wider pb-3 pr-4">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-sentinel-border/40">
                    {assets.length === 0
                      ? <tr><td colSpan={6} className="py-10 text-center text-sentinel-muted">No assets discovered yet.</td></tr>
                      : assets.map(a => (
                          <tr key={a.id} className="hover:bg-white/[0.02] transition-colors">
                            <td className="py-2.5 pr-4">
                              <span className="flex items-center gap-1.5 text-sentinel-muted">
                                {assetIcon(a.asset_type)}
                                <span className="font-mono capitalize">{a.asset_type}</span>
                              </span>
                            </td>
                            <td className="py-2.5 pr-4 font-mono text-sentinel-accent max-w-[200px] truncate">{a.value}</td>
                            <td className="py-2.5 pr-4 font-mono text-sentinel-text">{a.ip_address || '—'}</td>
                            <td className="py-2.5 pr-4 font-mono text-sentinel-text">
                              {a.port ? `${a.port}/${a.service || '?'}` : '—'}
                            </td>
                            <td className="py-2.5 pr-4 text-sentinel-muted">{a.country || '—'}</td>
                            <td className="py-2.5">
                              <span className={`badge-${a.risk_level}`}>{a.risk_level?.toUpperCase()}</span>
                            </td>
                          </tr>
                      ))
                    }
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* IP LOOKUP TAB */}
        {tab === TAB.IPINFO && (
          <div className="animate-slide-up">
            <div className="card">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <Network size={16} className="text-sentinel-accent" />
                IP Address Resolution & Open Ports
              </h3>
              {ipEntries.length === 0 ? (
                <div className="text-center py-12 text-sentinel-muted">
                  No IP addresses resolved yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-sentinel-border">
                        {['IP Address', 'Hostname(s)', 'Open Ports', 'Services'].map(h => (
                          <th key={h} className="text-left text-sentinel-muted font-medium uppercase tracking-wider pb-3 pr-4">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-sentinel-border/40">
                      {ipEntries.map(entry => (
                        <tr key={entry.ip} className="hover:bg-white/[0.02] transition-colors">
                          <td className="py-3 pr-4">
                            <span className="font-mono text-sentinel-accent font-bold">{entry.ip}</span>
                          </td>
                          <td className="py-3 pr-4 font-mono text-sentinel-text max-w-[250px]">
                            <div className="space-y-0.5">
                              {entry.hostnames.map(h => (
                                <div key={h} className="truncate">{h}</div>
                              ))}
                            </div>
                          </td>
                          <td className="py-3 pr-4">
                            <div className="flex flex-wrap gap-1">
                              {entry.ports.length > 0 ? entry.ports.map(p => (
                                <span key={p.port} className="bg-sentinel-accent/10 text-sentinel-accent font-mono px-2 py-0.5 rounded border border-sentinel-accent/20">
                                  {p.port}
                                </span>
                              )) : <span className="text-sentinel-muted">—</span>}
                            </div>
                          </td>
                          <td className="py-3">
                            <div className="flex flex-wrap gap-1">
                              {entry.ports.length > 0 ? entry.ports.map(p => (
                                <span key={p.port} className="bg-sentinel-surface text-sentinel-text font-mono px-2 py-0.5 rounded border border-sentinel-border text-xs">
                                  {p.service}
                                </span>
                              )) : <span className="text-sentinel-muted">—</span>}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* REPORT TAB */}
        {tab === TAB.REPORT && (
          <div className="space-y-5 animate-slide-up">
            {!report ? (
              <div className="card text-center py-16">
                <FileText size={40} className="text-sentinel-muted mx-auto mb-3 opacity-40" />
                <p className="text-sentinel-muted">
                  {isRunning ? 'Oracle Agent is generating the report…' : 'No report available.'}
                </p>
              </div>
            ) : (
              <>
                <div className="card">
                  <div className="flex items-center gap-3 mb-1">
                    <Shield size={18} className="text-sentinel-accent" />
                    <h3 className="text-white font-bold text-lg">{report.title}</h3>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-sentinel-muted font-mono mb-5">
                    <span className="flex items-center gap-1"><Clock size={11} /> {fmtDate(report.generated_at)}</span>
                    <span>Risk: <span className="font-bold" style={{ color: riskLabel(report.risk_score).color }}>
                      {report.risk_score}/100 — {riskLabel(report.risk_score).label}
                    </span></span>
                  </div>

                  <div className="space-y-6">
                    <section>
                      <h4 className="text-sentinel-accent font-semibold text-sm uppercase tracking-wider mb-3 flex items-center gap-2">
                        <span className="w-4 h-px bg-sentinel-accent" />
                        Executive Summary
                      </h4>
                      <div className="text-sentinel-text text-sm leading-relaxed whitespace-pre-wrap bg-sentinel-surface
                                      rounded-lg p-4 border border-sentinel-border">
                        {report.executive_summary}
                      </div>
                    </section>

                    <section>
                      <h4 className="text-sentinel-accent font-semibold text-sm uppercase tracking-wider mb-3 flex items-center gap-2">
                        <span className="w-4 h-px bg-sentinel-accent" />
                        Technical Analysis
                      </h4>
                      <div className="text-sentinel-text text-sm leading-relaxed whitespace-pre-wrap bg-sentinel-surface
                                      rounded-lg p-4 border border-sentinel-border font-mono">
                        {report.technical_details}
                      </div>
                    </section>

                    {report.attack_vectors?.length > 0 && (
                      <section>
                        <h4 className="text-red-400 font-semibold text-sm uppercase tracking-wider mb-3">Attack Vectors</h4>
                        <ul className="space-y-2">
                          {report.attack_vectors.map((v, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-sentinel-text">
                              <span className="text-red-400 mt-0.5 shrink-0">▸</span>{v}
                            </li>
                          ))}
                        </ul>
                      </section>
                    )}

                    {report.threat_actors?.length > 0 && (
                      <section>
                        <h4 className="text-orange-400 font-semibold text-sm uppercase tracking-wider mb-3">Threat Actors</h4>
                        <div className="flex flex-wrap gap-2">
                          {report.threat_actors.map((a, i) => (
                            <span key={i} className="badge-high">{a}</span>
                          ))}
                        </div>
                      </section>
                    )}

                    {report.recommendations?.length > 0 && (
                      <section>
                        <h4 className="text-sentinel-green font-semibold text-sm uppercase tracking-wider mb-3">Recommendations</h4>
                        <ul className="space-y-2">
                          {report.recommendations.map((r, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-sentinel-text">
                              <CheckCircle size={14} className="text-sentinel-green mt-0.5 shrink-0" />
                              {r}
                            </li>
                          ))}
                        </ul>
                      </section>
                    )}


                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
