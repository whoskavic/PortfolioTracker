import { createContext, useContext, useState, useEffect } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      client.get('/users/me')
        .then(res => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (usernameOrEmail, password) => {
    const form = new URLSearchParams()
    form.append('username', usernameOrEmail)
    form.append('password', password)
    const res = await client.post('/token', form)
    localStorage.setItem('token', res.data.access_token)
    const userRes = await client.get('/users/me')
    setUser(userRes.data)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      isAuthenticated: !!localStorage.getItem('token'),
      login,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
