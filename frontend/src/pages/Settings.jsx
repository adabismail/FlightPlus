import { useState } from 'react'
import { authApi } from '../services/api'
import { useAuth } from '../contexts/AuthContext'

export default function Settings() {
  const { user, setUser } = useAuth()
  const [form, setForm] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    currency: user?.currency || 'INR',
    notify_email: user?.notify_email ?? true,
    notify_sms: user?.notify_sms ?? false,
  })
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy]   = useState(false)

  const set = (k, v) => { setForm((f) => ({ ...f, [k]: v })); setSaved(false) }

  const save = async (e) => {
    e.preventDefault()
    setError(''); setSaved(false); setBusy(true)
    try {
      const { data } = await authApi.updateMe(form)
      setUser(data); setSaved(true)
    } catch { setError('Could not save changes.') } finally { setBusy(false) }
  }

  return (
    <>
      <div className="head">
        <div>
          <div className="eyebrow">Account</div>
          <h1>Settings</h1>
          <div className="sub">Profile and notification preferences.</div>
        </div>
      </div>

      <form onSubmit={save} style={{ maxWidth: 620 }}>
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card__head"><h2>Profile</h2></div>
          <div style={{ padding: 18 }}>
            {error && <div className="notice err">{error}</div>}
            <div className="field">
              <label>Email</label>
              <input className="input" value={user?.email || ''} disabled />
              <span className="hint">Email is your login and can't be changed here.</span>
            </div>
            <div className="row2">
              <div className="field">
                <label>Name</label>
                <input className="input" value={form.name} onChange={(e) => set('name', e.target.value)} />
              </div>
              <div className="field">
                <label>Phone</label>
                <input className="input mono" value={form.phone || ''} onChange={(e) => set('phone', e.target.value)} placeholder="+91…" />
              </div>
            </div>
            <div className="field" style={{ maxWidth: 180, marginBottom: 0 }}>
              <label>Default currency</label>
              <select className="input" value={form.currency} onChange={(e) => set('currency', e.target.value)}>
                <option>INR</option><option>USD</option><option>EUR</option><option>GBP</option><option>AED</option>
              </select>
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card__head"><h2>Notifications</h2></div>
          <div style={{ padding: '4px 18px' }}>
            <label className="toggle">
              <span><span className="toggle__label">Email alerts</span><div className="toggle__desc">Deal alerts sent to {user?.email}</div></span>
              <span className="switch"><input type="checkbox" checked={form.notify_email} onChange={(e) => set('notify_email', e.target.checked)} /><span /></span>
            </label>
            <label className="toggle">
              <span><span className="toggle__label">SMS alerts</span><div className="toggle__desc">Requires a phone number on file</div></span>
              <span className="switch"><input type="checkbox" checked={form.notify_sms} onChange={(e) => set('notify_sms', e.target.checked)} /><span /></span>
            </label>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <button className="btn primary" disabled={busy}>{busy ? 'Saving…' : 'Save changes'}</button>
          {saved && <span className="saved-tick">✓ Saved</span>}
        </div>
      </form>
    </>
  )
}
