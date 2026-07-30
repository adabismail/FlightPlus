import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const IconRoutes = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="6" cy="18" r="2.4" /><circle cx="18" cy="6" r="2.4" />
    <path d="M8.4 17.2 15.6 7.4" strokeDasharray="1.5 2.4" />
  </svg>
)
const IconAlerts = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8a6 6 0 1 0-12 0c0 7-3 8-3 8h18s-3-1-3-8" /><path d="M13.7 21a2 2 0 0 1-3.4 0" />
  </svg>
)
const IconSettings = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7.7 1.6 1.6 0 0 0-1 1.5V22a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H2a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H8a1.6 1.6 0 0 0 1-1.5V2a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V8a1.6 1.6 0 0 0 1.5 1H22a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z" />
  </svg>
)
const IconPlane = () => (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 15.5 14 11V5.2a1.7 1.7 0 0 0-3.4 0V11l-7 4.5v1.9l7-2.1v3.4l-1.8 1.2v1.4l3.5-1 3.5 1v-1.4L14 18.7v-3.4l7 2.1z" /></svg>
)

const initials = (name = '') =>
  name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]).join('').toUpperCase() || 'U'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = async () => { await logout(); navigate('/login') }

  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand__mark"><IconPlane /></span>
        <span className="brand__name">Flight<span>Pulse</span></span>
      </div>

      <nav className="side-nav">
        <NavLink to="/" end className="navlink"><IconRoutes /><span>Routes</span></NavLink>
        <NavLink to="/alerts" className="navlink"><IconAlerts /><span>Alerts</span></NavLink>
        <NavLink to="/settings" className="navlink"><IconSettings /><span>Settings</span></NavLink>
      </nav>

      <div className="side-foot">
        <div className="side-user">
          <span className="avatar">{initials(user?.name)}</span>
          <div className="side-user__meta">
            <div className="side-user__name">{user?.name}</div>
            <div className="side-user__mail">{user?.email}</div>
          </div>
        </div>
        <button className="btn ghost sm block" onClick={handleLogout}>Sign out</button>
      </div>
    </aside>
  )
}
