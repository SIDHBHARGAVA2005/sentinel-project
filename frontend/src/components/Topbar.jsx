import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Bell, Plus, Zap } from 'lucide-react'
import { createScan } from '../utils/api'

export default function Topbar({ title, subtitle }) {
  const [target, setTarget] = useState('')
  const [scanning, setScanning] = useState(false)
  const navigate = useNavigate()

  const handleQuickScan = async (e) => {
    e.preventDefault()
    if (!target.trim()) return
    setScanning(true)
    try {
      const scan = await createScan(target.trim())
      navigate(`/scans/${scan.id}`)
      setTarget('')
    } catch (err) {
      alert('Failed to start scan. Is the backend running?')
    } finally {
      setScanning(false)
    }
  }

  return (
    <header className="h-16 bg-sentinel-surface border-b border-sentinel-border
                       flex items-center justify-between px-6 gap-4 sticky top-0 z-10">
      <div>
        <h1 className="text-white font-semibold text-base">{title}</h1>
        {subtitle && <p className="text-sentinel-muted text-xs font-mono">{subtitle}</p>}
      </div>

      {/* Quick scan bar */}
      <form onSubmit={handleQuickScan} className="flex items-center gap-2 flex-1 max-w-md">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-sentinel-muted" />
          <input
            value={target}
            onChange={e => setTarget(e.target.value)}
            placeholder="Quick scan: example.com"
            className="input-field pl-9 h-9 text-xs"
          />
        </div>
        <button
          type="submit"
          disabled={scanning || !target.trim()}
          className="btn-primary flex items-center gap-1.5 h-9 text-xs px-3 whitespace-nowrap disabled:opacity-40"
        >
          {scanning
            ? <><span className="w-3 h-3 border border-sentinel-accent border-t-transparent rounded-full animate-spin" /> Scanning…</>
            : <><Zap size={12} /> Scan Now</>
          }
        </button>
      </form>

      <div className="flex items-center gap-2">
        <button className="w-8 h-8 rounded-lg bg-sentinel-card border border-sentinel-border
                           flex items-center justify-center text-sentinel-muted hover:text-sentinel-text
                           hover:border-sentinel-accent/30 transition-all">
          <Bell size={14} />
        </button>
      </div>
    </header>
  )
}
