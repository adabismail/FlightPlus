import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Plane = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" width="17" height="17"><path d="M21 15.5 14 11V5.2a1.7 1.7 0 0 0-3.4 0V11l-7 4.5v1.9l7-2.1v3.4l-1.8 1.2v1.4l3.5-1 3.5 1v-1.4L14 18.7v-3.4l7 2.1z" /></svg>
)
const Eye = ({ off }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
    {off
      ? <><path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 10 8 10 8a18.5 18.5 0 0 1-2.16 3.19M6.6 6.6A18.6 18.6 0 0 0 2 12s3 8 10 8a9 9 0 0 0 5.4-1.6" /><path d="M1 1l22 22" /></>
      : <><path d="M2 12s3-8 10-8 10 8 10 8-3 8-10 8-10-8-10-8Z" /><circle cx="12" cy="12" r="3" /></>}
  </svg>
)

export default function Register() {
  const { register, verifyOtp } = useAuth()
  const navigate = useNavigate()

  const [step, setStep] = useState('form')      // 'form' | 'otp'
  const [form, setForm] = useState({ name: '', email: '', phone: '', password: '', password2: '' })
  const [show, setShow] = useState(false)
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [info, setInfo]   = useState('')
  const [busy, setBusy]   = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const mismatch = form.password2.length > 0 && form.password !== form.password2

  const submitForm = async (e) => {
    e.preventDefault(); setError('')
    if (form.password !== form.password2) { setError('Passwords do not match.'); return }
    setBusy(true)
    try {
      const data = await register(form)
      setInfo(`We sent a 6-digit code to ${data.email}.`)
      setStep('otp')
    } catch (err) { setError(firstError(err) || 'Could not create account.') }
    finally { setBusy(false) }
  }

  const submitOtp = async (e) => {
    e.preventDefault(); setError(''); setBusy(true)
    try { await verifyOtp(form.email, code.trim()); navigate('/') }
    catch (err) { setError(firstError(err) || 'Invalid or expired code.') }
    finally { setBusy(false) }
  }

  return (
    <div className="auth">
      <div className="auth__card">
        <div className="auth__brand">
          <span className="brand__mark"><Plane /></span>
          <span className="brand__name">Flight<span style={{ color: 'var(--accent)' }}>Pulse</span></span>
        </div>

        <div className="auth__panel">
          {step === 'form' ? (
            <>
              <h1>Create account</h1>
              <p className="sub">Start tracking routes in under a minute.</p>
              {error && <div className="notice err">{error}</div>}
              <form onSubmit={submitForm}>
                <div className="field">
                  <label>Name</label>
                  <input className="input" required value={form.name} onChange={set('name')} placeholder="Ada Lovelace" />
                </div>
                <div className="field">
                  <label>Email</label>
                  <input className="input" type="email" required value={form.email} onChange={set('email')} placeholder="you@example.com" />
                </div>
                <div className="field">
                  <label>Phone <span className="hint">· optional, for SMS alerts</span></label>
                  <input className="input mono" value={form.phone} onChange={set('phone')} placeholder="+91…" />
                </div>
                <div className="field">
                  <label>Password</label>
                  <div className="input-wrap">
                    <input className="input" type={show ? 'text' : 'password'} required minLength={8}
                           value={form.password} onChange={set('password')} placeholder="At least 8 characters" />
                    <button type="button" className="reveal" onClick={() => setShow((s) => !s)} aria-label="Toggle password"><Eye off={show} /></button>
                  </div>
                </div>
                <div className="field">
                  <label>Confirm password</label>
                  <input className={`input ${mismatch ? 'input--err' : ''}`} type={show ? 'text' : 'password'}
                         required value={form.password2} onChange={set('password2')} placeholder="Re-enter password" />
                  {mismatch && <span className="hint" style={{ color: 'var(--bad)' }}>Passwords don't match</span>}
                </div>
                <button className="btn primary block" disabled={busy || mismatch}>{busy ? 'Creating…' : 'Create account'}</button>
              </form>
              <div className="auth__foot">Already have an account? <Link to="/login">Sign in</Link></div>
            </>
          ) : (
            <>
              <h1>Verify your email</h1>
              <p className="sub">{info}</p>
              {error && <div className="notice err">{error}</div>}
              <form onSubmit={submitOtp}>
                <div className="field">
                  <label>6-digit code</label>
                  <input className="input otp" inputMode="numeric" pattern="[0-9]*" maxLength={6} autoFocus
                         value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))} placeholder="000000" />
                  <span className="hint">In development the code is printed in the backend logs.</span>
                </div>
                <button className="btn primary block" disabled={busy || code.length !== 6}>{busy ? 'Verifying…' : 'Verify & continue'}</button>
              </form>
              <div className="auth__foot">
                <button type="button" className="linklike" onClick={() => { setStep('form'); setError(''); setCode('') }}>← Back</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function firstError(err) {
  const d = err?.response?.data
  if (!d) return ''
  if (typeof d === 'string') return d
  if (d.detail) return d.detail
  const v = Object.values(d)[0]
  return Array.isArray(v) ? v[0] : String(v)
}
