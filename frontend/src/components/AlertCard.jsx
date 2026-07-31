// A single row in the alert-history table.
const money = (n) => (n == null ? '—' : Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 }))

export default function AlertCard({ alert }) {
  const when = alert.alert_sent_at
    ? new Date(alert.alert_sent_at).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: '2-digit' })
    : '—'

  return (
    <tr>
      <td>
        <div className="pair">
          <span className="code">{alert.from_code}</span>
          <span className="arrow">✈</span>
          <span className="code">{alert.to_code}</span>
        </div>
      </td>
      <td>
        <span className="mono">{alert.flight_number || '—'}</span>
        <span className="dim"> · {alert.airline || alert.airline_code || 'n/a'}</span>
      </td>
      <td className="num">{money(alert.price)} <span className="dim">{alert.currency}</span></td>
      <td className="num">
        {alert.savings_amount != null
          ? <span className="savings">−{money(alert.savings_amount)} · {alert.savings_pct}%</span>
          : '—'}
      </td>
      <td className="mono dim">{alert.stops === 0 ? 'nonstop' : `${alert.stops} stop`}</td>
      <td>{alert.is_delivered ? <span className="tag ok">{alert.channel}</span> : <span className="tag bad">failed</span>}</td>
      <td className="num dim">{when}</td>
    </tr>
  )
}
