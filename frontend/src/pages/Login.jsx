import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authApi } from '../services/api'

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

export default function Login() {
  const { login, verifyOtp } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [show, setShow]         = useState(false)
  const [error, setError]       = useState('')
  const [busy, setBusy]         = useState(false)

  const [needVerify, setNeedVerify] = useState(false)
  const [code, setCode] = useState('')
  const [info, setInfo] = useState('')

  const submit = async (e) => {
    e.preventDefault(); setError(''); setBusy(true)
    try { await login(email, password); navigate('/') }
    catch (err) {
      if (err?.response?.status === 403 && err.response.data?.needs_verification) {
        try { await authApi.resendOtp(email) } catch { /* ignore */ }
        setInfo(`This account isn't verified yet. We sent a fresh code to ${email}.`)
        setNeedVerify(true)
      } else {
        setError('Invalid email or password.')
      }
    } finally { setBusy(false) }
  }

  const submitOtp = async (e) => {
    e.preventDefault(); setError(''); setBusy(true)
    try { await verifyOtp(email, code.trim()); navigate('/') }
    catch (err) { setError(err?.response?.data?.detail || 'Invalid or expired code.') }
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
          {!needVerify ? (
            <>
              <h1>Sign in</h1>
              <p className="sub">Track fares and get alerted when prices drop.</p>
              {error && <div className="notice err">{error}</div>}
              <form onSubmit={submit}>
                <div className="field">
                  <label>Email</label>
                  <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
                </div>
                <div className="field">
                  <label>Password</label>
                  <div className="input-wrap">
                    <input className="input" type={show ? 'text' : 'password'} required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
                    <button type="button" className="reveal" onClick={() => setShow((s) => !s)} aria-label="Toggle password"><Eye off={show} /></button>
                  </div>
                </div>
                <button className="btn primary block" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
              </form>
              <div className="auth__foot">No account? <Link to="/register">Create one</Link></div>
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
                <button className="btn primary block" disabled={busy || code.length !== 6}>{busy ? 'Verifying…' : 'Verify & sign in'}</button>
              </form>
              <div className="auth__foot">
                <button type="button" className="linklike" onClick={() => { setNeedVerify(false); setError(''); setCode('') }}>← Back to sign in</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
