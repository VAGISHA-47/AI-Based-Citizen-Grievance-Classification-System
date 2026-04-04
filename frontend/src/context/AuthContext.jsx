import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import * as api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const fetchCurrentUser = useCallback(async (tkn) => {
    try {
      const res = await api.getCurrentUser()
      setUser(res.data)
    } catch {
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchCurrentUser(token)
    } else {
      setLoading(false)
    }
  }, [token, fetchCurrentUser])

  const login = async (username, password) => {
    const res = await api.login(username, password)
    const newToken = res.data.access_token
    localStorage.setItem('token', newToken)
    setToken(newToken)
    const userRes = await api.getCurrentUser()
    setUser(userRes.data)
    return userRes.data
  }

  const register = async (username, email, password) => {
    const res = await api.register(username, email, password)
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
