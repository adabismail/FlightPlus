import { createContext, useContext, useEffect, useState } from 'react'
import { authApi, tokenStore } from '../services/api'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  // On boot, if we hold a token, resolve the current user.
  useEffect(() => {
    if (!tokenStore.access) { setLoading(false); return }
    authApi
      .me()
      .then((r) => setUser(r.data))
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await authApi.login(email, password)
    tokenStore.set(data.tokens)
    setUser(data.user)
  }

  // Register no longer logs the user in — it triggers an email OTP.
  // The account is activated (and tokens issued) by verifyOtp below.
  const register = async (payload) => {
    const { data } = await authApi.register(payload)
    return data   // { detail, email }
  }

  const verifyOtp = async (email, code) => {
    const { data } = await authApi.verifyOtp(email, code)
    tokenStore.set(data.tokens)
    setUser(data.user)
  }

  const logout = async () => {
    try { await authApi.logout() } catch { /* token may already be invalid */ }
    tokenStore.clear()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, verifyOtp, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
