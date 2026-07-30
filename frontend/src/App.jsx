import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-loading">LOADING</div>
  return user ? children : <Navigate to="/login" replace />
}

function Shell({ children }) {
  return (
    <div className="app">
      <Navbar />
      <main className="main">
        <div className="content">{children}</div>
      </main>
    </div>
  )
}

export default function App() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login"    element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/" replace /> : <Register />} />
      <Route path="/"         element={<Protected><Shell><Dashboard /></Shell></Protected>} />
      <Route path="/alerts"   element={<Protected><Shell><Alerts /></Shell></Protected>} />
      <Route path="/settings" element={<Protected><Shell><Settings /></Shell></Protected>} />
      <Route path="*"         element={<Navigate to="/" replace />} />
    </Routes>
  )
}
