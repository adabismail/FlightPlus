import { useState } from 'react'
import { routesApi } from '../services/api'
import { AIRPORTS, AIRPORT_CITY } from '../data/airports'

const BLANK = {
  from_city: '', from_code: '', to_city: '', to_code: '',
  price_limit: '', currency: 'INR', cabin_class: 'ECONOMY',
  trip_type: 'ONE_WAY', adults: 1,
  depart_date: '', return_date: '', flexible_dates: true,
  preferred_airlines: '', weekends_only: false,
}

// Prefill the form when editing an existing route.
function fromRoute(r) {
  if (!r) return BLANK
  return {
    from_city: r.from_city, from_code: r.from_code, to_city: r.to_city, to_code: r.to_code,
    price_limit: r.price_limit, currency: r.currency, cabin_class: r.cabin_class,
    trip_type: r.trip_type, adults: r.adults,
    depart_date: r.depart_date || '', return_date: r.return_date || '',
    flexible_dates: r.flexible_dates,
    preferred_airlines: r.preferred_airlines || '', weekends_only: r.weekends_only,
  }
}

export default function AddRouteModal({ route, onClose, onSaved }) {
  const editing = Boolean(route)
  const [form, setForm]   = useState(() => fromRoute(route))
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const set = (k) => (e) => {
    const v = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((f) => ({ ...f, [k]: v }))
  }

  // Uppercase the IATA code and, if it's a known airport, autofill the city.
  const setCode = (codeKey, cityKey) => (e) => {
    const code = e.target.value.toUpperCase().slice(0, 3)
    setForm((f) => ({ ...f, [codeKey]: code, ...(AIRPORT_CITY[code] ? { [cityKey]: AIRPORT_CITY[code] } : {}) }))
  }

  const submit = async (e) => {
    e.preventDefault()
    setError(''); setSaving(true)
    try {
      const payload = {
        ...form,
        price_limit: Number(form.price_limit),
        adults: Number(form.adults),
        return_date: form.trip_type === 'ROUND_TRIP' ? form.return_date || null : null,
        depart_date: form.depart_date || null,
      }
      const { data } = editing
        ? await routesApi.update(route.id, payload)
        : await routesApi.create(payload)
      onSaved(data)
    } catch (err) {
      setError(firstError(err) || 'Could not save route.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="overlay" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal__head">
          <h2>{editing ? 'Edit route' : 'Track a new route'}</h2>
          <button type="button" className="btn ghost sm" onClick={onClose}>Esc</button>
        </div>
        <form onSubmit={submit}>
          <div className="modal__body">
            {error && <div className="notice err">{error}</div>}

            {/* Shared airport suggestions for both IATA fields */}
            <datalist id="airport-list">
              {AIRPORTS.map((a) => <option key={a.code} value={a.code}>{a.city}</option>)}
            </datalist>

            <div className="row2">
              <div className="field">
                <label>From — city</label>
                <input className="input" required value={form.from_city} onChange={set('from_city')} placeholder="New Delhi" />
              </div>
              <div className="field">
                <label>From — IATA</label>
                <input className="input mono" required maxLength={3} list="airport-list" value={form.from_code}
                       onChange={setCode('from_code', 'from_city')} placeholder="DEL" style={{ textTransform: 'uppercase' }} />
              </div>
            </div>

            <div className="row2">
              <div className="field">
                <label>To — city</label>
                <input className="input" required value={form.to_city} onChange={set('to_city')} placeholder="Dubai" />
              </div>
              <div className="field">
                <label>To — IATA</label>
                <input className="input mono" required maxLength={3} list="airport-list" value={form.to_code}
                       onChange={setCode('to_code', 'to_city')} placeholder="DXB" style={{ textTransform: 'uppercase' }} />
              </div>
            </div>

            <div className="row2">
              <div className="field">
                <label>Max budget</label>
                <input className="input mono" required type="number" min="1" value={form.price_limit} onChange={set('price_limit')} placeholder="15000" />
              </div>
              <div className="field">
                <label>Currency</label>
                <select className="input" value={form.currency} onChange={set('currency')}>
                  <option>INR</option><option>USD</option><option>EUR</option><option>GBP</option><option>AED</option>
                </select>
              </div>
            </div>

            <div className="row2">
              <div className="field">
                <label>Cabin</label>
                <select className="input" value={form.cabin_class} onChange={set('cabin_class')}>
                  <option value="ECONOMY">Economy</option>
                  <option value="PREMIUM_ECONOMY">Premium Economy</option>
                  <option value="BUSINESS">Business</option>
                  <option value="FIRST">First</option>
                </select>
              </div>
              <div className="field">
                <label>Trip type</label>
                <select className="input" value={form.trip_type} onChange={set('trip_type')}>
                  <option value="ONE_WAY">One way</option>
                  <option value="ROUND_TRIP">Round trip</option>
                </select>
              </div>
            </div>

            <div className="row2">
              <div className="field">
                <label>Departure</label>
                <input className="input" type="date" value={form.depart_date} onChange={set('depart_date')} />
              </div>
              <div className="field">
                <label>Return {form.trip_type !== 'ROUND_TRIP' && <span className="hint">(round trip only)</span>}</label>
                <input className="input" type="date" value={form.return_date} onChange={set('return_date')}
                       disabled={form.trip_type !== 'ROUND_TRIP'} />
              </div>
            </div>

            <div className="field">
              <label>Preferred airlines <span className="hint">· optional · comma-separated IATA (EK,AI)</span></label>
              <input className="input mono" value={form.preferred_airlines} onChange={set('preferred_airlines')}
                     placeholder="any airline" style={{ textTransform: 'uppercase' }} />
            </div>

            <label className="toggle" style={{ borderTop: '1px solid var(--line-soft)' }}>
              <span><span className="toggle__label">Flexible dates</span><div className="toggle__desc">Scan ±3 days around departure</div></span>
              <span className="switch"><input type="checkbox" checked={form.flexible_dates} onChange={set('flexible_dates')} /><span /></span>
            </label>
            <label className="toggle">
              <span><span className="toggle__label">Weekends only</span><div className="toggle__desc">Only consider Sat/Sun departures</div></span>
              <span className="switch"><input type="checkbox" checked={form.weekends_only} onChange={set('weekends_only')} /><span /></span>
            </label>
          </div>

          <div className="modal__foot">
            <button type="button" className="btn ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn primary" disabled={saving}>
              {saving ? 'Saving…' : editing ? 'Save changes' : 'Track route'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function firstError(err) {
  const d = err?.response?.data
  if (!d) return ''
  if (typeof d === 'string') return d
  const v = Object.values(d)[0]
  return Array.isArray(v) ? v[0] : String(v)
}
