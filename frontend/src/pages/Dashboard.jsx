import { useEffect, useState, useCallback } from 'react'
import { routesApi } from '../services/api'
import RouteCard from '../components/RouteCard'
import StatsBar from '../components/StatsBar'
import AddRouteModal from '../components/AddRouteModal'

export default function Dashboard() {
  const [routes, setRoutes] = useState([])
  const [stats, setStats]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId]   = useState(null)
  const [modal, setModal]     = useState(null)   // null | {route?} — open add/edit modal
  const [notice, setNotice]   = useState('')

  const load = useCallback(async () => {
    const [r, s] = await Promise.all([routesApi.list(), routesApi.stats()])
    setRoutes(r.data); setStats(s.data); setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const flash = (msg) => { setNotice(msg); setTimeout(() => setNotice(''), 4000) }
  const guard = (id, fn) => async () => { setBusyId(id); try { await fn() } finally { setBusyId(null) } }

  const onEdit   = (route) => setModal({ route })
  const onPause  = (route) => guard(route.id, async () => { await routesApi.pause(route.id);  await load() })()
  const onResume = (route) => guard(route.id, async () => { await routesApi.resume(route.id); await load() })()
  const onCheck  = (route) => guard(route.id, async () => {
    await routesApi.checkNow(route.id)
    flash(`Price check queued for ${route.from_code} → ${route.to_code}. Results appear in Alerts.`)
  })()
  const onDelete = (route) => {
    if (!window.confirm(`Stop tracking ${route.from_code} → ${route.to_code}?`)) return
    guard(route.id, async () => { await routesApi.remove(route.id); await load() })()
  }

  return (
    <>
      <div className="head">
        <div>
          <div className="eyebrow">Dashboard</div>
          <h1>Tracked routes</h1>
          <div className="sub">Fares are checked daily — or run an on-demand check any time.</div>
        </div>
        <div className="head__actions">
          <button className="btn primary" onClick={() => setModal({})}>+ Track route</button>
        </div>
      </div>

      <StatsBar stats={stats} />

      {notice && <div className="notice info">{notice}</div>}

      <div className="card">
        <div className="card__head">
          <h2>Routes <span className="count">{routes.length}</span></h2>
        </div>
        {loading ? (
          <div className="empty">Loading…</div>
        ) : routes.length === 0 ? (
          <div className="empty">
            <div className="empty__mark">✈</div>
            No routes yet — add one to start tracking fares.
          </div>
        ) : (
          <table className="tbl">
            <thead>
              <tr>
                <th>Route</th><th>Cabin</th><th className="right">Budget</th>
                <th className="right">Lowest seen</th><th>Status</th><th className="right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((route) => (
                <RouteCard key={route.id} route={route} busy={busyId === route.id}
                  onEdit={onEdit} onPause={onPause} onResume={onResume} onCheck={onCheck} onDelete={onDelete} />
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modal && (
        <AddRouteModal
          route={modal.route}
          onClose={() => setModal(null)}
          onSaved={() => { setModal(null); load() }}
        />
      )}
    </>
  )
}
