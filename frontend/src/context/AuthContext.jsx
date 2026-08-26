import { createContext, useContext, useState, useEffect } from 'react'
import { getToken, saveToken, clearToken } from '../lib/auth'
import { apiFetch } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // On app load: if a token exists, verify it by fetching the current user.
  useEffect(() => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }
    apiFetch('/api/users/me')
      .then((data) => setUser(data))
      .catch(() => { clearToken(); setUser(null) })  // bad/expired token → sign out
      .finally(() => setLoading(false))
  }, [])

  async function login(token) {
    saveToken(token)
    const userData = await apiFetch('/api/users/me')  // who am I?
    setUser(userData)
  }

  function logout() {
    clearToken()
    setUser(null)
  }

  const value = { user, loading, isAuthenticated: !!user, login, logout }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}