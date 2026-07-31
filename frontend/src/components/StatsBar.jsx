const fmt = (n) => Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 })

export default function StatsBar({ stats, currency = 'INR' }) {
  const cells = [
    { k: 'Tracked routes', v: stats?.total_routes ?? '—' },
    { k: 'Active', v: stats?.active_routes ?? '—', mod: 'accent' },
    { k: 'Alerts fired', v: stats?.total_alerts ?? '—' },
    {
      k: 'Lowest seen',
      v: stats?.lowest_seen != null ? <>{fmt(stats.lowest_seen)}<small>{currency}</small></> : '—',
      mod: stats?.lowest_seen != null ? 'good' : undefined,
    },
  ]
  return (
    <div className="tiles">
      {cells.map((c) => (
        <div className={`tile ${c.mod || ''}`} key={c.k}>
          <div className="tile__k">{c.k}</div>
          <div className="tile__v">{c.v}</div>
        </div>
      ))}
    </div>
  )
}
