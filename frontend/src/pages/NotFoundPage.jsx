import React from 'react'
import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div style={{
      minHeight: 'calc(100vh - 3.5rem)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: '5rem', marginBottom: '1rem' }}>🔍</div>
      <h1 style={{ fontSize: '3rem', fontWeight: 800, color: '#1e293b', marginBottom: '0.5rem' }}>404</h1>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#475569', marginBottom: '0.75rem' }}>
        Page Not Found
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '1.5rem', maxWidth: '360px' }}>
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/" className="btn btn-primary">
        ← Back to Home
      </Link>
    </div>
  )
}
