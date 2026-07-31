// A single row in the tracked-routes table.
const STATUS = { ACTIVE: 'active', PAUSED: 'paused', EXPIRED: 'expired' }
const money = (n) => (n == null ? '—' : Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 }))

export default function RouteCard({ route, busy, onEdit, onPause, onResume, onCheck, onDelete }) {
  const seen  = route.lowest_seen != null ? Number(route.lowest_seen) : null
  const limit = Number(route.price_limit)
  const under = seen != null && seen <= limit
  const pct   = seen != null ? Math.max(6, Math.min(100, (seen / limit) * 100)) : 0

  return (
    <tr>
      <td>
        <div className="pair">
          <span className="code">{route.from_code}</span>
          <span className="arrow">✈</span>
          <span className="code">{route.to_code}</span>
          <span className="sub">{route.from_city} – {route.to_city}</span>
        </div>
      </td>
      <td className="muted" style={{ textTransform: 'capitalize' }}>
        {route.cabin_class.replace('_', ' ').toLowerCase()}
        {route.weekends_only && <span className="tag" style={{ marginLeft: 8 }}>wknd</span>}
      </td>
      <td className="num">{money(route.price_limit)} <span className="dim">{route.currency}</span></td>
      <td>
        {seen != null ? (
          <div className="gauge">
            <span className={`gauge__val ${under ? 'savings' : ''}`}>{money(seen)}</span>
            <span className="gauge__track"><span className={`gauge__fill ${under ? 'under' : ''}`} style={{ width: `${pct}%` }} /></span>
          </div>
        ) : <span className="dim mono">no data</span>}
      </td>
      <td><span className={`chip ${STATUS[route.status] || 'expired'}`}>{route.status}</span></td>
      <td className="actions">
        <button className="btn sm" disabled={busy} onClick={() => onCheck(route)}>Check</button>
        <button className="btn sm ghost" disabled={busy} onClick={() => onEdit(route)}>Edit</button>
        {route.status === 'ACTIVE'
          ? <button className="btn sm ghost" disabled={busy} onClick={() => onPause(route)}>Pause</button>
          : <button className="btn sm ghost" disabled={busy} onClick={() => onResume(route)}>Resume</button>}
        <button className="btn sm danger" disabled={busy} onClick={() => onDelete(route)}>Delete</button>
      </td>
    </tr>
  )
}
