import { useEffect, useState, useCallback } from 'react'
import { alertsApi, routesApi } from '../services/api'
import AlertCard from '../components/AlertCard'

export default function Alerts() {
  const [alerts, setAlerts]   = useState([])
  const [routes, setRoutes]   = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ route: '', channel: '', is_delivered: '' })

  useEffect(() => { routesApi.list().then((r) => setRoutes(r.data)).catch(() => {}) }, [])

  const load = useCallback(async () => {
    setLoading(true)
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ''))
    const { data } = await alertsApi.list(params)
    setAlerts(data); setLoading(false)
  }, [filters])

  useEffect(() => { load() }, [load])
  const set = (k) => (e) => setFilters((f) => ({ ...f, [k]: e.target.value }))

  return (
    <>
      <div className="head">
        <div>
          <div className="eyebrow">History</div>
          <h1>Alerts</h1>
          <div className="sub">Every deal that beat one of your thresholds.</div>
        </div>
      </div>

      <div className="card">
        <div className="card__head">
          <h2>Alerts <span className="count">{alerts.length}</span></h2>
          <div className="filters">
            <select className="input" value={filters.route} onChange={set('route')}>
              <option value="">All routes</option>
              {routes.map((r) => <option key={r.id} value={r.id}>{r.from_code} → {r.to_code}</option>)}
            </select>
            <select className="input" value={filters.channel} onChange={set('channel')}>
              <option value="">Any channel</option><option value="EMAIL">Email</option>
              <option value="SMS">SMS</option><option value="BOTH">Both</option>
            </select>
            <select className="input" value={filters.is_delivered} onChange={set('is_delivered')}>
              <option value="">Any status</option><option value="true">Delivered</option><option value="false">Failed</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="empty">Loading…</div>
        ) : alerts.length === 0 ? (
          <div className="empty">
            <div className="empty__mark">◎</div>
            No alerts yet — they appear here once a fare drops below your budget.
          </div>
        ) : (
          <table className="tbl">
            <thead>
              <tr>
                <th>Route</th><th>Flight</th><th className="right">Price</th>
                <th className="right">Saved</th><th>Stops</th><th>Delivery</th><th className="right">Date</th>
              </tr>
            </thead>
            <tbody>{alerts.map((a) => <AlertCard key={a.id} alert={a} />)}</tbody>
          </table>
        )}
      </div>
    </>
  )
}
