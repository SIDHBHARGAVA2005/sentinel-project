import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard      from './pages/Dashboard'
import Scans          from './pages/Scans'
import ScanDetail     from './pages/ScanDetail'
import Assets         from './pages/Assets'
import Reports        from './pages/Reports'
import Activity       from './pages/Activity'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-sentinel-bg">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0">
          <Routes>
            <Route path="/"            element={<Dashboard />} />
            <Route path="/scans"       element={<Scans />} />
            <Route path="/scans/:id"   element={<ScanDetail />} />
            <Route path="/assets"      element={<Assets />} />
            <Route path="/reports"     element={<Reports />} />
            <Route path="/activity"    element={<Activity />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
