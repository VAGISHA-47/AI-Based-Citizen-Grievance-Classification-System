import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav style={{
      background: '#fff',
      boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '3.5rem',
      }}>
        <Link
          to="/"
          style={{
            fontWeight: 700,
            fontSize: '1.1rem',
            color: '#1e293b',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
          }}
        >
          🏛️ Grievance System
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {user ? (
            <>
              <span style={{ fontSize: '0.875rem', color: '#475569' }}>
                {user.username}
              </span>
              <span className={`badge badge-${user.role === 'admin' ? 'urgent' : 'normal'}`}
                style={{ fontSize: '0.7rem' }}>
                {user.role === 'admin' ? 'Admin' : user.role === 'department_officer' ? 'Officer' : 'Citizen'}
              </span>
              {user.role === 'admin' && (
                <Link to="/admin" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                  Dashboard
                </Link>
              )}
              <Link to="/complaints" style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                Complaints
              </Link>
              <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary btn-sm">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
