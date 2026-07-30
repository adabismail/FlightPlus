import axios from 'axios'

// Nginx (prod) and the Vite dev server both proxy /api -> Django.
const API_BASE = '/api'

const api = axios.create({ baseURL: API_BASE })

// --- token storage -------------------------------------------------
export const tokenStore = {
  get access()  { return localStorage.getItem('fp_access') },
  get refresh() { return localStorage.getItem('fp_refresh') },
  set({ access, refresh }) {
    if (access)  localStorage.setItem('fp_access', access)
    if (refresh) localStorage.setItem('fp_refresh', refresh)
  },
  clear() {
    localStorage.removeItem('fp_access')
    localStorage.removeItem('fp_refresh')
  },
}

// --- attach bearer token -------------------------------------------
api.interceptors.request.use((cfg) => {
  const t = tokenStore.access
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

// --- transparent refresh on 401 ------------------------------------
let refreshing = null
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const { response, config } = err
    if (response?.status === 401 && config && !config._retry && tokenStore.refresh) {
      config._retry = true
      try {
        refreshing =
          refreshing ||
          axios.post(`${API_BASE}/auth/refresh/`, { refresh: tokenStore.refresh })
        const { data } = await refreshing
        refreshing = null
        // ROTATE_REFRESH_TOKENS is on, so the response carries a fresh refresh
        // token too and the old one is blacklisted — persist both.
        tokenStore.set({ access: data.access, refresh: data.refresh })
        config.headers.Authorization = `Bearer ${data.access}`
        return api(config)
      } catch (e) {
        refreshing = null
        tokenStore.clear()
        if (window.location.pathname !== '/login') window.location.href = '/login'
        return Promise.reject(e)
      }
    }
    return Promise.reject(err)
  },
)

// --- endpoint helpers ----------------------------------------------
export const authApi = {
  login:     (email, password) => api.post('/auth/login/', { email, password }),
  register:  (payload)         => api.post('/auth/register/', payload),
  verifyOtp: (email, code)     => api.post('/auth/verify-otp/', { email, code }),
  resendOtp: (email)           => api.post('/auth/resend-otp/', { email }),
  me:        ()                => api.get('/auth/me/'),
  updateMe:  (payload)         => api.patch('/auth/me/', payload),
  logout:    ()                => api.post('/auth/logout/', { refresh: tokenStore.refresh }),
}

export const routesApi = {
  list:     ()        => api.get('/routes/'),
  create:   (p)       => api.post('/routes/', p),
  update:   (id, p)   => api.patch(`/routes/${id}/`, p),
  remove:   (id)      => api.delete(`/routes/${id}/`),
  pause:    (id)      => api.post(`/routes/${id}/pause/`),
  resume:   (id)      => api.post(`/routes/${id}/resume/`),
  checkNow: (id)      => api.post(`/routes/${id}/check_now/`),
  stats:    ()        => api.get('/routes/stats/'),
}

export const alertsApi = {
  list: (params) => api.get('/alerts/', { params }),
}

export default api
