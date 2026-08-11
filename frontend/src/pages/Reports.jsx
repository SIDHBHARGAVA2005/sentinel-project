import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, RefreshCw, Shield, ChevronRight } from 'lucide-react'
import { listScans, getScan } from '../utils/api'
import { riskLabel, fmtDate } from '../utils/helpers'
import RiskGauge from '../components/ui/RiskGauge'
import Topbar from '../components/Topbar'

export default function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const scans = await listScans()
        const completed = scans.filter(s => s.status === 'completed')
        const all = []
        for (const s of completed.slice(0, 15)) {
          const detail = await getScan(s.id)
          if (detail.report) all.push({ ...detail.report, scan_target: s.target, scan_id: s.id, scan: detail })
        }
        setReports(all)
        if (all.length > 0) setSelected(all[0])
      } catch (e) { console.error(e) }
      finally { setLoading(false) }
    }
    load()
  }, [])

  return (
    <div className="flex-1 flex flex-col">
      <Topbar title="Reports" subtitle="AI-generated security assessments" />
      <div className="p-6 animate-fade-in">
        {loading
          ? <div className="flex items-center justify-center py-16 gap-3 text-sentinel-muted">
              <RefreshCw size={16} className="animate-spin" />
              <span className="font-mono text-sm">Loading reports…</span>
            </div>
          : reports.length === 0
            ? <div className="card text-center py-20">
                <FileText size={48} className="text-sentinel-muted mx-auto mb-4 opacity-30" />
                <p className="text-sentinel-muted mb-4">No reports yet. Complete a scan to generate a report.</p>
                <Link to="/scans" className="btn-primary inline-flex items-center gap-2">
                  Start a scan →
                </Link>
              </div>
            : <div className="grid grid-cols-12 gap-5">
                {/* Report list */}
                <div className="col-span-4 space-y-2">
                  {reports.map(r => (
                    <div key={r.id}
                      onClick={() => setSelected(r)}
                      className={`card cursor-pointer transition-all hover:border-sentinel-accent/30
                        ${selected?.id === r.id ? 'border-sentinel-accent/50 bg-sentinel-accent/5' : ''}`}>
                      <div className="flex items-center justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="font-mono text-sentinel-accent text-sm truncate">{r.scan_target}</div>
                          <div className="text-sentinel-muted text-xs font-mono mt-0.5">{fmtDate(r.generated_at)}</div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="font-mono text-xs font-bold"
                                style={{ color: riskLabel(r.risk_score).color }}>
                            {r.risk_score}
                          </span>
                          <ChevronRight size={12} className="text-sentinel-muted" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Report viewer */}
                {selected && (
                  <div className="col-span-8 card space-y-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-white font-bold text-lg">{selected.title}</h3>
                        <div className="text-sentinel-muted text-xs font-mono mt-1">{fmtDate(selected.generated_at)}</div>
                      </div>
                      <RiskGauge score={selected.risk_score} size={90} />
                    </div>

                    <div className="border-t border-sentinel-border pt-4 space-y-5">
                      {[
                        { heading: 'Executive Summary', content: selected.executive_summary, color: 'text-sentinel-accent' },
                        { heading: 'Technical Analysis', content: selected.technical_details, color: 'text-sentinel-green', mono: true },
                      ].map(({ heading, content, color, mono }) => (
                        <div key={heading}>
                          <h4 className={`font-semibold text-xs uppercase tracking-wider mb-2 ${color}`}>{heading}</h4>
                          <div className={`text-sentinel-text text-sm leading-relaxed whitespace-pre-wrap bg-sentinel-surface
                                          rounded-lg p-4 border border-sentinel-border ${mono ? 'font-mono text-xs' : ''}`}>
                            {content || 'Not available.'}
                          </div>
                        </div>
                      ))}

                      {selected.recommendations?.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-xs uppercase tracking-wider mb-2 text-sentinel-green">
                            Recommendations
                          </h4>
                          <ul className="space-y-1.5">
                            {selected.recommendations.map((r, i) => (
                              <li key={i} className="flex items-start gap-2 text-xs text-sentinel-text">
                                <Shield size={11} className="text-sentinel-green mt-0.5 shrink-0" />
                                {r}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="pt-2">
                        <Link to={`/scans/${selected.scan_id}`} className="btn-primary text-xs inline-flex items-center gap-2">
                          View Full Scan Details →
                        </Link>
                      </div>
                    </div>
                  </div>
                )}
              </div>
        }
      </div>
    </div>
  )
}
