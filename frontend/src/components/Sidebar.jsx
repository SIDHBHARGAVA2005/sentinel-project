import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Radar, FileText,
  Target, Activity, Settings, ChevronRight
} from 'lucide-react'

const links = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/scans',     icon: Radar,           label: 'Scans' },
  { to: '/assets',    icon: Target,          label: 'Assets' },
  { to: '/reports',   icon: FileText,        label: 'Reports' },
  { to: '/activity',  icon: Activity,        label: 'Activity' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-sentinel-surface border-r border-sentinel-border
                      flex flex-col min-h-screen sticky top-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-sentinel-border">
        <div className="w-9 h-9 rounded-lg bg-sentinel-accent/10 border border-sentinel-accent/30
                        flex items-center justify-center glow-accent">
          <svg viewBox="0 0 24 24" className="w-5 h-5 text-sentinel-accent fill-current">
            <path d="M12 2L3 7v5c0 5.25 3.75 10.15 9 11.35C17.25 22.15 21 17.25 21 12V7L12 2z"/>
          </svg>
        </div>
        <div>
          <div className="text-white font-bold text-sm tracking-widest">SENTINEL</div>
          <div className="text-sentinel-muted text-xs font-mono">v1.0.0</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
               transition-all duration-150 group
               ${isActive
                 ? 'bg-sentinel-accent/10 text-sentinel-accent border border-sentinel-accent/20'
                 : 'text-sentinel-muted hover:text-sentinel-text hover:bg-sentinel-card'}`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={16} className={isActive ? 'text-sentinel-accent' : ''} />
                <span className="flex-1">{label}</span>
                {isActive && <ChevronRight size={12} className="opacity-60" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-sentinel-border">
        <div className="text-xs text-sentinel-muted font-mono leading-relaxed">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-sentinel-green animate-pulse-slow"></span>
            <span>All agents online</span>
          </div>
          <div className="opacity-50">Scout · Analyst · Oracle</div>
        </div>
      </div>
    </aside>
  )
}
